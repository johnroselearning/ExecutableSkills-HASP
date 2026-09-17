# Native HASP diagnostic selection — checkpoint report

**Status: design checkpoint only. Zero model trials; no claims about native diagnostic
performance.** User review is required before inference experiments. The deterministic
checks below do not falsify or validate the proposed research gap.

## 1. Research question

Does a native HASP-assisted policy choose discriminating, economical next actions
when multiple support PFs are applicable? We seek evidence against needing an added
selection mechanism, not evidence that HASP cannot adapt.

## 2. Experimental design

Implemented a fixed-world synthetic HTTP-500 environment with four private worlds,
six deterministic actions, five initial evidence histories, offline partition scoring
and native interface probes. Full protocol: [DESIGN.md](DESIGN.md).
The initial complaint reveals no root cause. The policy receives observations only
when a check is executed. Prehistory is generated through the same oracle.

## 3. Hypotheses

Fixed truth H1: web amount serialization defect. Counterfactual H2: missing web auth
scope incorrectly produces 500. H3: shared backend normalization regression.
H4: shared payment outage. These narrow the original broad categories into exclusive
single-fault worlds. H1/H3 share an ambiguous capture and exception; a suspicious
request difference is not automatically causal. World definitions are reviewer-only.

## 4. Diagnostic actions and costs

| ID | Check | Cost |
|---|---|---:|
| A | Request trace | 3 |
| B | Matched web/mobile reproduction | 1 |
| C | Backend exception/log inspection | 4 |
| D | Header/payload comparison | 1 |
| E | Dependency probes plus per-request health | 2 |
| F | Controlled isolation replay suite | 5 |

Costs are synthetic units, visible equally in all planned conditions. F is added to
make binary isolation executable; it is deliberately priced as a complete suite.

## 5. Evidence oracle

[Complete hypothesis/action/evidence matrix](analysis/MATRIX.md).
`oracle.py` returns public text, observed facts and cost for each action; its private
world never enters the input builder. Repeats are deterministic and still paid.
The source is not exposed to the future model. Five unit tests pass, including all
720 full action permutations in each of four worlds (17,280 transitions), truth
retention, monotone elimination, repeat/copy safety, hand calculations, native gate
competition/fire caps, parser behavior and input projection.

## 6. HASP configuration

Unchanged five support PFs from the previous local experiment. Native
`pf_select_eval` menu, selection instruction, parser and program-function dispatcher.
Support-domain `INVESTIGATE` adapter; native per-PF fire cap preserved. This is a
support adaptation of native primitives, not an unchanged terminal-answer evaluator.

Mechanical fresh-episode gates, independently checked with all five retained:

| Case | Activatable PFs |
|---|---|
| Initial | evidence_collection |
| After B | evidence_collection, comparison_experiment |
| After A | evidence_collection, dependency_trace |
| After D | request_id_trace, dependency_trace, binary_isolation |
| After B,E | evidence_collection, request_id_trace, comparison_experiment |

This verifies competition without changing gates to admit a preferred winner.
The initial case is a low-evidence reference, not itself a multi-PF competition case.

## 7. Models/settings

No model selected or invoked. Proposed temperature 0.7, 30 trials/cell, two menu
orders, maximum 8 steps. Seed base 101, role/step-separated seeds where supported.
10 trials/cell is the fallback pilot. Provider/runtime feasibility is not yet verified.
Ollama executable exists but its local endpoint did not respond; no visible GPU
runtime/device was found. No package or model installation was attempted.

## 8. Conditions A/B/C

A: base only. B: native model-selected PFs, canonical and reversed menu orders.
C: all five retained, native gates/fire caps, fixed dispatch order, no selector turn.
Same oracle, initial histories and paired seeds. Planned 600 episodes (pilot 200).
C is explicitly a retained-PF control, not evidence of model-driven selection.

## 9. Model-driven PF-selection traces

**None yet.** [Checkpoint mechanical JSONL](traces/checkpoint_mechanical.jsonl)
contains 10 clearly labeled probes, complete menu/prompt previews and actual native
mechanical dispatch records. Base model proposal, raw selector output and executed
policy action are null. A fixed fixture proposal is separately labeled.
These must never be counted as model-driven selections or policy successes.

## 10. Optimal-next-action results

No observed policy rate. [Expected and actual score tables](analysis/CALCULATIONS.md)
provide the reference calculations. Initially expected elimination/cost is D=2.5,
B=2.0, E=0.75, C=0.625, F=0.6, A=0.5. After D, B is best; after B, D is best.
After A, B/D tie. Expected scoring is primary; fixed-truth hindsight is secondary.
The two differ initially: B and D tie under actual H1 eliminations/cost.

## 11. Diagnostic-cost results

No observed policy cost. Fixed-H1 offline minimum additional cost is 2 initially,
1 after B, 2 after A, 1 after D, 1 after B,E. Initial cheapest paths are B→D and D→B.
These are truth-aware lower bounds, not expected-cost optimal planners.
Prehistory costs are 0,1,3,1,3 respectively and must be reported separately.
Planning ceiling: 10,800 model calls, 3.69M output tokens and assumed 21.6–64.8M input
tokens for 30 trials; pilot one-third. No dollar estimate without a chosen provider.

## 12. Steps-to-isolation

No observed policy steps. F isolates any world in one expensive action; initial
cheapest paths use two actions. Singleton isolation is only within the stipulated
worlds, not causal confirmation or a model-authored correct diagnosis. Capped/invalid
runs must remain in success-rate denominators and be reported separately from successes.

## 13. Redundant-action analysis

No behavioral rate yet. The offline evaluator flags repeated checks and any action
whose partition cannot split remaining worlds. After D, A/C/D/E are all
non-discriminating; only D is a repeat. Strict redundant repeats and all zero-value
checks will be separate metrics. Tests confirm repeats add no elimination.

## 14. PF-selection vs actual-action analysis

No causal or behavioral result. Gate results, firing records, complete injections,
base proposal and resulting policy action are distinct fields. Actual executed
actions determine scores. Proposal changes after feedback are descriptive alignment;
an additional generation alone can change output, so causal attribution is unresolved.

## 15. PF-menu-order sensitivity

No model comparison yet. Verified that the native builder sorts IDs; the alternative
reverses rendered menu lines, not dictionary insertion order. A has no menu and C
has fixed retention/dispatch order. Both orders' exact previews are recorded.

## 16. Evidence-conditioned switching behavior

No observed switching yet. The environment demands a change in best next action:
D leaves H1/H3, making B best; B leaves H1/H2, making D best. Native fire counts will
persist across an episode. Snapshot prehistories do not silently consume PF firings.
Per-step reselection is an explicit support-runner invocation, not a claimed automatic
native evidence-invalidation feature.

## 17. Strongest evidence FOR native HASP

At checkpoint, native interfaces support competing applicable PFs and preserve their
independent interventions. Nothing in this deterministic setup shows that the LLM
will choose poorly. Earlier adaptation evidence is accepted, not retested as a gap.
Strong model results, if obtained, would count against needing an added selector.

## 18. Strongest evidence AGAINST native HASP

None from model behavior: no model experiments ran. Gate overlap, lack of an explicit
scoring objective and arbitrary mechanical control proposals are not negative evidence.

## 19. What this falsifies from our earlier assumptions

This checkpoint does not newly falsify a behavioral hypothesis. It rejects measuring
PF selection as action success and confirms that only-one-surviving-gate fixtures are
unnecessary here. The earlier broad claim that native HASP cannot adapt remains
withdrawn based on the user's prior findings.

## 20. What remains unresolved

Actual A/B/C performance, implicit discrimination/cost reasoning, redundant checks,
menu effects, provider feasibility and statistical precision. All primary worlds use
H1 truth, so repeated trials characterize stochasticity, not incident diversity.
The model does not know the evaluator's exhaustive worlds or prior, so “suboptimal”
is relative to a privileged benchmark. Costs/partitions are synthetic. Scope-specific
support PFs and terminal-to-step adaptation limit generalization. Comparing cases
with different evidence does not causally isolate the effect of multiple PFs.
No-feedback revision and balanced alternative truths would need separate experiments.

## 21. Whether another experiment is justified

The proposed A/B/C model experiment is ready for design review, not execution.
Review the closed-world assumptions, visible costs, reselection boundary, endpoint
and resource budget first. Native behavior could falsify the motivation for an added
selector; poor behavior would establish only behavior in this benchmark. No novelty
claim is warranted, and no smaller gap will be sought merely to preserve the idea.

**Stopped here as requested. No model-run command is enabled.**
