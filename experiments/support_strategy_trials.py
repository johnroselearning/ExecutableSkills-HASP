"""Independent native-dispatch probes and repeated local-model selection trials.

Ollama supplies text generation only. Menu, prompt, parser, gates and dispatch
come from HASP. No strategy chooser is implemented here.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pf_select.pf_select_eval import (
    _build_pf_menu, _load_pf_system, _parse_pf_selection,
    _PF_SELECT_INSTRUCTION_TMPL,
)

IDS = ["evidence_collection", "request_id_trace", "comparison_experiment",
       "dependency_trace", "binary_isolation"]
QUESTION = "Checkout returns HTTP 500. What investigative action should be taken next?"


def states():
    facts = {"operation": "checkout", "status": 500}
    evidence = "Checkout returns HTTP 500; little evidence."
    updates = [
        ("E0", {}, "", "Inspect server logs for checkout errors."),
        ("E1", {"endpoint": "/api/checkout", "method": "POST", "request_id": "abc123"},
         "POST /api/checkout returns 500; request-id abc123.",
         "Trace request-id abc123 through backend logs and dependencies."),
        ("E2", {"web_fails": True, "mobile_succeeds": True,
                "same_account": True, "same_operation": True},
         "Web checkout fails consistently; mobile checkout succeeds. Same account and same operation.",
         "Continue tracing request-id abc123 through backend logs and dependencies."),
        ("E3", {"differing_headers": ["Content-Type", "X-Client-Version"], "request_captured": True},
         "Web and mobile send different request headers: Content-Type and X-Client-Version. "
         "Request captures exist; header values and causal relevance are not yet known.",
         "Continue tracing request-id abc123 through backend logs and dependencies."),
        ("E4", {"frontend_deployment_precedes_failure": True, "backend_version_unchanged": True},
         "Failure began immediately after frontend deployment; backend version unchanged.",
         "Continue tracing request-id abc123 through backend logs and dependencies."),
        ("E5_invalidated", {"trace_exhausted": True, "dependencies_verified_successful": True},
         "The complete abc123 trace has now been inspected: all downstream calls succeeded. "
         "No further uninspected spans remain. This invalidates the proposed downstream-failure "
         "investigation; it does not prove a frontend cause.",
         "Continue tracing request-id abc123 through backend logs and dependencies."),
    ]
    out = []
    for name, update, addition, proposal in updates:
        facts.update(update)
        evidence += ("\n" + addition) if addition else ""
        out.append(dict(state=name, evidence=evidence, facts=copy.deepcopy(facts), proposal=proposal))
    # The user's E2 alone does not imply that a request ID was collected.
    out.append(dict(state="E2_standalone", evidence=updates[2][2],
                    facts={"operation": "checkout", "status": 500, **updates[2][1]},
                    proposal="Inspect server logs for checkout errors."))
    return out


def dispatch(execute, state, selected, counts=None, step=0):
    ctx = dict(question=QUESTION, domain="support", support_evidence=state["facts"],
               evidence=state["evidence"], raw_reasoning=state["proposal"],
               action_history=[], step_count=step, max_steps=6,
               _pf_fire_counts=counts if counts is not None else {})
    before = dict(ctx["_pf_fire_counts"])
    action, arg, records, injections = execute(
        active_skill_ids=selected, step_context=ctx, action_type="INVESTIGATE",
        arg=state["proposal"], reasoning=state["proposal"], teacher_model=None)
    return dict(should_activate={r.skill_id: r.activated for r in records},
                records=[r.to_dict() for r in records], interventions=injections,
                dispatch_action=dict(type=action, argument=arg),
                fire_counts_before=before, fire_counts_after=dict(ctx["_pf_fire_counts"]))


def generate(model, messages, seed, limit):
    payload = dict(model=model, messages=messages, stream=False, think=False,
                   options=dict(temperature=0.7, seed=seed, num_predict=limit))
    req = urllib.request.Request("http://127.0.0.1:11434/api/chat",
                                 data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as response:
        raw = json.load(response)
    return raw["message"]["content"], raw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model")
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--base-policy", choices=("fixed", "model"), default="fixed")
    parser.add_argument("--states", nargs="+")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.repeats < 1 or (args.base_policy == "model" and not args.model):
        parser.error("Positive repeats and a model for model-generated proposals are required")
    execute, library = _load_pf_system("skills")
    assert set(IDS) <= set(library), set(IDS) - set(library)
    from src.skills_agent.skills.program_functions import get_program_function
    assert all(get_program_function(sid) is not None for sid in IDS), "PF registry mismatch"
    menu = _build_pf_menu({sid: library[sid] for sid in IDS})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as target:
        def emit(record):
            target.write(json.dumps(record, ensure_ascii=True) + "\n")
            target.flush()

        revision_instruction = ("Please provide a revised answer:" if args.base_policy == "fixed" else
                                "Please provide a revised answer. State the next investigative action in at most 100 words.")
        emit(dict(kind="metadata", model=args.model, temperature=0.7, base_policy=args.base_policy,
                  revision_instruction=revision_instruction,
                  selector_prompt=_PF_SELECT_INSTRUCTION_TMPL, menu=menu,
                  files={str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in [Path(__file__).resolve(), ROOT / "skills/executable/support/skills.py",
                                   ROOT / "pf_select/pf_select_eval.py",
                                   ROOT / "src/skills_agent/skills/program_functions.py"]},
                  protocol="Fixed base proposals; fresh selection per state. "
                  "Ollama inference adapter, native HASP prompt/parser/dispatch. "
                  "Reselection between states is an experiment invocation, not an invalidation hook."))
        for state in states():
            if args.states and state["state"] not in args.states:
                continue
            base = dict(**state, menu=menu, base_policy_source="fixed experimental control")
            if args.model:
                for trial in range(args.repeats):
                    base_raw = None
                    if args.base_policy == "model":
                        state = copy.deepcopy(state)
                        proposal, base_raw = generate(args.model, [dict(role="user", content=
                            QUESTION + "\nEvidence:\n" + state["evidence"]
                            + "\nState the next investigative action in at most 100 words.")],
                            trial + 101, 256)
                        state["proposal"] = proposal
                        base = dict(**state, menu=menu, base_policy_source="model before seeing PF menu")
                    messages = [dict(role="user", content=QUESTION + "\nEvidence:\n" + state["evidence"]),
                                dict(role="assistant", content=state["proposal"]),
                                dict(role="user", content=_PF_SELECT_INSTRUCTION_TMPL.format(
                                    menu=menu, candidate=state["proposal"]))]
                    output, raw = generate(args.model, messages, trial + 101, 256)
                    selected = _parse_pf_selection(output, set(IDS))
                    result = dispatch(execute, state, selected)
                    final = state["proposal"]
                    revision_raw = None
                    if result["interventions"]:
                        revision = messages[:2] + [dict(role="user", content=
                            "[System Feedback]\n" + "\n\n".join(result["interventions"])
                            + "\n\n" + revision_instruction)]
                        final, revision_raw = generate(args.model, revision, trial + 101, 512)
                    emit(dict(**base, **result, kind="model_trial", trial=trial,
                              selection_output=output, selected_pfs=selected,
                              selection_raw=raw, revision_raw=revision_raw, final_action=final,
                              base_raw=base_raw, selection_messages=messages,
                              selection_reason="Native prompt requests tags only; no rationale requested."))
                    print(state["state"], trial, selected, flush=True)
            else:
                # Exhaust every possible subset; these are supplied tags, not LLM decisions.
                for size in range(6):
                    for subset in itertools.combinations(IDS, size):
                        output = "\n".join(f"<pf>{sid}</pf>" for sid in subset)
                        selected = _parse_pf_selection(output, set(IDS))
                        result = dispatch(execute, state, selected)
                        emit(dict(**base, **result, kind="forced_subset", selected_pfs=selected,
                                  selection_output=output, selection_reason="Forced mechanical probe",
                                  final_action=None, final_action_status="No model revision in mechanical probe"))
                result = dispatch(execute, state, IDS[::-1])
                emit(dict(**base, **result, kind="reverse_order", selected_pfs=IDS[::-1],
                          selection_output="\n".join(f"<pf>{s}</pf>" for s in IDS[::-1]),
                          selection_reason="Forced order probe", final_action=None))
            print("completed", state["state"], flush=True)
        if not args.model:
            for mode in ("all_frozen", "request_only_frozen"):
                counts = {}
                selected = IDS if mode == "all_frozen" else ["request_id_trace"]
                for step, state in enumerate(states()[:6]):
                    emit(dict(**state, menu=menu, kind=mode, selected_pfs=selected,
                              **dispatch(execute, state, selected, counts, step)))


if __name__ == "__main__":
    main()
