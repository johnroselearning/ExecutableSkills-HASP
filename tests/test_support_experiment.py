"""Guard experimental validity: selection provenance, overlapping PFs and limits."""
from copy import deepcopy
import json
from types import SimpleNamespace

import pytest

from experiments import support_http500 as exp


@pytest.fixture(scope="module")
def results():
    return exp.controls()


def find(results, stage, selected, trial_prefix="subset_"):
    return next(t for t in results["traces"] if t["stage"] == stage
                and t["selected_pfs"] == selected and t["trial"].startswith(trial_prefix))


def test_every_subset_is_exercised_without_claiming_model_selection(results):
    assert len(results["traces"]) == 284
    assert results["model_trials_run"] == 0
    for stage in exp.stages():
        ts = [t for t in results["traces"] if t["stage"] == stage["stage"]
              and t["trial"].startswith("subset_")]
        assert len({frozenset(t["selected_pfs"]) for t in ts}) == 32
        for t in ts:
            assert set(t["should_activate"]) == set(t["selected_pfs"])
            assert all(f"- {sid}:" in t["pf_menu"] for sid in exp.IDS)
            assert t["selection_reason"] is None
            assert not any(r.get("reason", "").startswith("error:") for r in t["records"])


def test_overlapping_pfs_are_not_arbitrated_and_order_is_preserved(results):
    ids = ["request_id_trace", "comparison_experiment"]
    a = find(results, "E2", ids)
    b = find(results, "E2", ids[::-1])
    assert all(a["should_activate"].values())
    assert a["interventions"] == b["interventions"][::-1]
    assert a["final_action"] == b["final_action"]
    assert len(find(results, "E4", list(exp.IDS))["interventions"]) == 4


def test_unselected_comparison_cannot_activate(results):
    t = find(results, "E2", ["request_id_trace"])
    assert t["should_activate"] == {"request_id_trace": True}
    assert len(t["interventions"]) == 1
    empty = find(results, "E2", [])
    assert empty["records"] == [] and empty["interventions"] == []


def test_proposed_action_does_not_become_observed_evidence():
    execute, library = exp.load()
    t = exp.dispatch(execute, exp._build_pf_menu(library), exp.stages()[0],
                     "POST /api/checkout request-id abc123; web fails, mobile succeeds, compare headers",
                     exp.tags(exp.IDS), source="test", label="proposal_leakage")
    assert [sid for sid, active in t["should_activate"].items() if active] == ["evidence_collection"]


def test_matched_account_is_a_real_comparison_prerequisite():
    execute, library = exp.load()
    stage = deepcopy(exp.stages()[2])
    stage["facts"]["same_account"] = False
    t = exp.dispatch(execute, exp._build_pf_menu(library), stage, exp.PROPOSALS["neutral"],
                     exp.tags(["comparison_experiment"]), source="test", label="unmatched")
    assert t["should_activate"] == {"comparison_experiment": False}


def test_invalidation_and_fire_cap_are_distinguished(results):
    fresh = find(results, "E5_trace_exhausted", list(exp.IDS))
    assert fresh["fire_counts_before"] == {}
    assert fresh["should_activate"]["request_id_trace"] is False
    assert fresh["should_activate"]["dependency_trace"] is False
    assert fresh["should_activate"]["comparison_experiment"] is True
    retained = next(t for t in results["traces"] if t["stage"] == "E2" and t["trial"] == "retained_all")
    assert retained["fire_counts_before"]["request_id_trace"] == 1
    assert retained["should_activate"]["request_id_trace"] is False
    assert retained["should_activate"]["comparison_experiment"] is True


def test_upstream_pf_can_redirect_a_stalled_search(results):
    t = results["existing_hasp_adaptation_control"]
    assert t["records"][0]["activated"] is True
    assert t["records"][0]["intervention_type"] == "modify_action"
    assert t["final_action"]["arg"] == t["complete_evidence"]["question"]


def test_optional_model_path_preserves_native_prompt_and_records_revisions(monkeypatch):
    calls = []

    class FakeLLM:
        def __init__(self, **kwargs):
            pass

        def get_tokenizer(self):
            return SimpleNamespace(apply_chat_template=lambda msgs, **kw: json.dumps(msgs))

        def generate(self, prompts, params, **kwargs):
            calls.append((prompts, params))
            selection = params.max_tokens == 256
            text = exp.tags(["request_id_trace", "comparison_experiment"]) if selection else "Compare captured requests."
            return [SimpleNamespace(outputs=[SimpleNamespace(text=text)]) for _ in prompts]

    monkeypatch.setitem(exp.sys.modules, "vllm", SimpleNamespace(LLM=FakeLLM, SamplingParams=SimpleNamespace))
    result = exp.model_trials("test-double", 2, 0.7, 4096)
    assert result["model_trials_run"] == 36
    assert {t["seed"] for t in result["traces"]} == {0, 1}
    first_messages = json.loads(calls[0][0][0])
    assert first_messages[-1]["content"] == exp._PF_SELECT_INSTRUCTION_TMPL.format(
        menu=result["traces"][0]["pf_menu"], candidate=exp.PROPOSALS["neutral"])
    e2 = next(t for t in result["traces"] if t["stage"] == "E2")
    assert len(e2["interventions"]) == 2
    assert e2["final_action"]["arg"] == "Compare captured requests."
    assert e2["dispatch_final_action"]["arg"] == exp.PROPOSALS["neutral"]
