"""Summarize recorded observations; never chooses or ranks a PF."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path


def summarize(path):
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    groups = defaultdict(list)
    for row in rows:
        if row.get("kind") == "model_trial":
            groups[row["state"]].append(row)
    states = {}
    for state, trials in groups.items():
        states[state] = dict(
            n=len(trials),
            selected=dict(Counter(sid for t in trials for sid in t["selected_pfs"])),
            activated=dict(Counter(sid for t in trials for sid, active in t["should_activate"].items() if active)),
            selection_sequences=dict(Counter(", ".join(t["selected_pfs"]) or "(none)" for t in trials)),
            trace_and_comparison=sum({"request_id_trace", "comparison_experiment"} <= set(t["selected_pfs"]) for t in trials),
            truncated_selections=sum(t["selection_raw"].get("done_reason") == "length" for t in trials),
            truncated_revisions=sum((t.get("revision_raw") or {}).get("done_reason") == "length" for t in trials),
        )
    return dict(file=str(path), metadata=rows[0], states=states)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("files", type=Path, nargs="+")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps([summarize(path) for path in args.files], indent=2) + "\n"
    if args.output:
        args.output.write_text(result)
    else:
        print(result)
