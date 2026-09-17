"""HASP-native support PF dispatch controls and optional vLLM selection trials.

No selection algorithm is added. Controls enumerate possible selector outputs;
--model uses HASP's existing menu, instruction, parser and chat template.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import itertools
import json
from pathlib import Path
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pf_select.pf_select_eval import (
    _PF_SELECT_INSTRUCTION_TMPL, _build_pf_menu, _chat_tmpl,
    _load_pf_system, _parse_pf_selection,
)

IDS = ("evidence_collection", "request_id_trace", "comparison_experiment",
       "dependency_trace", "binary_isolation")
PROPOSALS = {
    "neutral": "Investigate the checkout HTTP 500 and determine the next diagnostic action.",
    "trace": "Continue tracing request-id abc123 through backend logs and dependencies.",
    "comparison": "Compare failing web checkout with successful mobile checkout under matched conditions.",
}


def stages():
    """Cumulative synthetic observations; absent fields mean unknown, not false."""
    additions = [
        ("E0", "Checkout returns HTTP 500. No request capture is available.",
         {"operation": "checkout", "status": 500}),
        ("E1", "The failing request is POST /api/checkout, status 500, request-id abc123.",
         {"method": "POST", "endpoint": "/api/checkout", "request_id": "abc123"}),
        ("E2", "Web checkout fails consistently; mobile checkout succeeds for the same account and same operation.",
         {"web_fails": True, "mobile_succeeds": True, "same_account": True, "same_operation": True}),
        ("E3", "Both requests have now been captured. Web and mobile send different headers: "
         "web Content-Type=text/plain and X-Checkout-Version=2; mobile Content-Type=application/json "
         "and X-Checkout-Version=1. These are observed differences, not established causes.",
         {"request_captured": True, "differing_headers": ["Content-Type", "X-Checkout-Version"],
          "web_headers": {"Content-Type": "text/plain", "X-Checkout-Version": "2"},
          "mobile_headers": {"Content-Type": "application/json", "X-Checkout-Version": "1"}}),
        ("E4", "Failure began immediately after frontend deployment. Backend version is unchanged. "
         "No rollback or causal intervention has yet been tested.",
         {"frontend_deployment_precedes_failure": True, "backend_version_unchanged": True}),
        ("E5_trace_exhausted", "Additional falsification control: all available logs for abc123 "
         "have been inspected and yield only a generic 500. Correlated downstream calls are "
         "verified successful. Repeating this log search has no new data; the cause remains unknown.",
         {"trace_exhausted": True, "dependencies_verified_successful": True}),
    ]
    facts, observations, result = {}, [], []
    for name, observation, delta in additions:
        facts.update(delta)
        observations.append({"stage": name, "observation": observation})
        result.append({"stage": name, "observations": deepcopy(observations), "facts": deepcopy(facts)})
    return result


def load():
    execute, library = _load_pf_system(str(ROOT / "skills"))
    return execute, {sid: library[sid] for sid in IDS}


def selection_messages(stage, proposal, menu):
    question = "Investigate this checkout incident. Evidence history and current observed facts:\n" + json.dumps(stage, indent=2)
    return [
        {"role": "user", "content": question},
        {"role": "assistant", "content": proposal},
        {"role": "user", "content": _PF_SELECT_INSTRUCTION_TMPL.format(menu=menu, candidate=proposal[-1200:])},
    ]


def dispatch(execute, menu, stage, proposal, output, *, source, label, counts=None):
    selected = _parse_pf_selection(output, set(IDS))
    context = {
        "domain": "support", "question": selection_messages(stage, proposal, menu)[0]["content"],
        "support_evidence": deepcopy(stage["facts"]),
        "raw_reasoning": proposal, "step_count": len(stage["observations"]) - 1,
        "max_steps": 10, "action_history": [],
        "_pf_fire_counts": counts if counts is not None else {},
    }
    counts_before = dict(context["_pf_fire_counts"])
    action, arg, records, injections = execute(
        active_skill_ids=selected, step_context=context, action_type="INVESTIGATE",
        arg=proposal, reasoning=proposal, teacher_model=None,
    )
    return {
        "stage": stage["stage"], "trial": label,
        "complete_evidence": stage, "base_policy_proposed_action": proposal,
        "base_policy_source": "fixed experimental proposal",
        "pf_menu": menu, "selection_messages": selection_messages(stage, proposal, menu),
        "selection_source": source, "selection_output": output,
        "selection_reason": None,
        "selection_reason_note": "Native prompt requests tags only; no rationale is requested or inferred.",
        "selected_pfs": selected,
        "should_activate": {r.skill_id: r.activated for r in records},
        "fire_counts_before": counts_before,
        "fire_counts_after": dict(context["_pf_fire_counts"]),
        "records": [r.to_dict() for r in records],
        "interventions": injections,
        "dispatch_final_action": {"type": action, "arg": arg},
        "final_action": {"type": action, "arg": arg},
        "post_feedback_policy_action": None,
        "final_action_scope": "PF dispatch result only; injected context requires a subsequent policy turn",
    }


def tags(ids):
    return "\n".join(f"<pf>{sid}</pf>" for sid in ids)


def controls():
    execute, library = load()
    menu = _build_pf_menu(library)
    traces = []
    # Exhaust all 32 subsets, including no selection. Order probes separately
    # check that dispatch preserves tag order rather than assigning precedence.
    selections = [list(s) for n in range(6) for s in itertools.combinations(IDS, n)]
    selections += [list(reversed(IDS)), ["comparison_experiment", "request_id_trace"]]
    for stage in stages():
        for i, selected in enumerate(selections):
            traces.append(dispatch(execute, menu, stage, PROPOSALS["neutral"], tags(selected),
                                   source="forced dispatch control; no model selection", label=f"subset_{i:02}"))
    for proposal_name in ("trace", "comparison"):
        for i, selected in enumerate(selections):
            traces.append(dispatch(execute, menu, stages()[2], PROPOSALS[proposal_name], tags(selected),
                                   source="forced proposal control; no model selection", label=f"{proposal_name}_{i:02}"))
    for name, selected in (("retained_trace", ["request_id_trace"]), ("retained_all", list(IDS))):
        counts = {}
        for stage in stages():
            traces.append(dispatch(execute, menu, stage, PROPOSALS["trace"], tags(selected),
                                   source="fixed episode selection; no reselection", label=name, counts=counts))
    return {"mode": "deterministic dispatch controls", "model_trials_run": 0, "traces": traces,
            "existing_hasp_adaptation_control": existing_adaptation_control(execute)}


def existing_adaptation_control(execute):
    """Exercise an upstream PF unchanged, beyond the authored support gates."""
    proposal = "checkout payment error"
    context = {
        "domain": "web", "question": "Why does web checkout fail while mobile succeeds?",
        "action_history": [{"action_type": "SEARCH", "arg": proposal}] * 2,
        "step_count": 2, "_pf_fire_counts": {},
    }
    original_context = deepcopy(context)
    action, arg, records, injections = execute(
        active_skill_ids=["iterative_refinement"], step_context=context,
        action_type="SEARCH", arg=proposal, reasoning="Previous queries repeated the same terms.",
    )
    return {"selection_source": "forced upstream PF control", "selected_pfs": ["iterative_refinement"],
            "complete_evidence": original_context, "fire_counts_after": dict(context["_pf_fire_counts"]),
            "base_policy_proposed_action": {"type": "SEARCH", "arg": proposal},
            "records": [r.to_dict() for r in records], "interventions": injections,
            "final_action": {"type": action, "arg": arg}}


def model_trials(model, trials, temperature, max_model_len):
    """A step-level support adaptation, not the untouched FINAL-answer evaluator.

The only selection logic is the imported HASP prompt and parser. Each state is
an independent selection call; this harness does not add a reselection policy.
"""
    from vllm import LLM, SamplingParams

    execute, library = load()
    menu = _build_pf_menu(library)
    llm = LLM(model=model, tensor_parallel_size=1, gpu_memory_utilization=0.92,
              max_model_len=max_model_len, trust_remote_code=True)
    tokenizer = llm.get_tokenizer()
    cases = [(s, name, p) for s in stages() for name, p in PROPOSALS.items()]
    messages = [selection_messages(s, p, menu) for s, _, p in cases]
    prompts = [_chat_tmpl(tokenizer, m, enable_thinking=False) for m in messages]
    traces = []
    for seed in range(trials):
        outputs = llm.generate(prompts, SamplingParams(temperature=temperature, seed=seed,
                                                       max_tokens=256, n=1), use_tqdm=False)
        batch = []
        for (stage, name, proposal), output in zip(cases, outputs):
            raw = output.outputs[0].text if output.outputs else ""
            trace = dispatch(execute, menu, stage, proposal, raw, source="vLLM native HASP selection prompt",
                             label=f"{name}_seed_{seed}")
            trace.update(model=model, seed=seed, temperature=temperature)
            batch.append(trace)
        pending = [t for t in batch if t["interventions"]]
        if pending:
            followups = []
            for t in pending:
                feedback = "\n\n".join(t["interventions"])
                msgs = [t["selection_messages"][0],
                        {"role": "assistant", "content": t["base_policy_proposed_action"]},
                        {"role": "user", "content": feedback + "\nState your next diagnostic action."}]
                t["post_feedback_messages"] = msgs
                followups.append(_chat_tmpl(tokenizer, msgs, enable_thinking=False))
            revisions = llm.generate(followups, SamplingParams(temperature=temperature, seed=seed,
                                                               max_tokens=512, n=1), use_tqdm=False)
            for t, revision in zip(pending, revisions):
                raw = revision.outputs[0].text if revision.outputs else ""
                t["post_feedback_policy_action"] = raw
                t["final_action"] = {"type": "policy_text", "arg": raw}
                t["final_action_scope"] = "Model response after step feedback; no investigative tool executed"
        traces.extend(batch)
    return {"mode": "model selection with fixed base proposals and step dispatch",
            "model_trials_run": len(traces), "traces": traces}


def summarize(result):
    traces = result["traces"]
    if result["model_trials_run"]:
        return {s["stage"]: {
            sid: sum(sid in t["selected_pfs"] for t in traces if t["stage"] == s["stage"])
            for sid in IDS
        } for s in stages()}
    return {t["stage"]: t["should_activate"] for t in traces if t["trial"] == "subset_31"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", help="Optional local/vLLM model identifier; never guesses a model")
    parser.add_argument("--trials", type=int, default=10)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-model-len", type=int, default=4096)
    parser.add_argument("--output", type=Path, default=ROOT / "experiments/results/support_http500.json")
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("--trials must be positive")
    result = (model_trials(args.model, args.trials, args.temperature, args.max_model_len)
              if args.model else controls())
    result["summary"] = summarize(result)
    source_paths = [Path(__file__), ROOT / "skills/executable/support/skills.py",
                    ROOT / "pf_select/pf_select_eval.py", ROOT / "src/skills_agent/skills/program_functions.py"]
    result["provenance"] = {
        "upstream_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "python": sys.version,
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"mode": result["mode"], "traces": len(result["traces"]),
                      "model_trials_run": result["model_trials_run"], "summary": result["summary"]}, indent=2))
    print(f"Full traces: {args.output}")


if __name__ == "__main__":
    main()
