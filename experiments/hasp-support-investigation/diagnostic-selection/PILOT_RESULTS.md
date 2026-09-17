# Pilot 1: completed attempts, diagnostic comparison not reached

**Pilot 1 is inconclusive about native HASP.** The local model produced Markdown-fenced
JSON in all five unique initial proposals. The frozen, experiment-specific action
parser requires a bare JSON object and rejects fenced output. Every episode therefore
stopped before action execution, PF selection, PF activation or feedback.

This is an interface failure under the approved protocol, **not evidence that native
HASP needs a discriminative strategy selector**. It would be incorrect to label native
HASP's diagnostic performance 0%, or to claim A/B/C are equivalent. They were never
compared on an executed diagnostic action. No new mechanism, parser repair, evaluator
change, model substitution or rerun followed these results.

## Scope and dependence of samples

As recorded before inference in [PILOT1_PROTOCOL.md](PILOT1_PROTOCOL.md):

- H1/H2/H3/H4, five trials per world/arm, all starting from the initial complaint.
- Primary A/base, B/native model-selected canonical, C/all retained: 60 attempts.
- Separate B_reverse sensitivity arm: 20 attempts. It is not pooled into A/B/C.
- Six actions A–F remain available; maximum eight executed actions per episode.
- First proposals share identical public inputs across all worlds and arms. Five
  proposals, with seeds 101–105, were cached and shared across those matched inputs.
  Each initial response is referenced by 16 episode attempts. Thus **80 attempted
  episodes represent five unique initial model generations, not 80 independent
  formatting failures**. No later model calls occurred.
- The original five snapshot cases were not crossed into this smaller pilot.

Primary execution began 2026-09-16 02:25:48 UTC and ended 02:26:08 UTC. All 80 scheduled
attempt records exist; none was silently dropped. The completed schedule must not be
mistaken for 80 completed diagnostic investigations.

## Model, runtime and resource use

| Setting | Verified value |
|---|---|
| Model tag | gemma4e-64k:latest, installed parent gemma4:e4b |
| Model metadata | gemma4 family, 8.0B, GGUF Q4_K_M |
| Model blob digest | `sha256:4c27e0f5b5adf02ac956c7322bd2ee7636fe3f45a8512c9aba5385242cb6e09a` |
| Provider/runtime | Local Ollama 0.31.2, isolated localhost:11435, cloud disabled |
| Hardware | AMD Radeon 780M via Vulkan; runtime logged 43/43 layers offloaded; 8 host threads |
| Temperature / sampling | 0.7; top_p 1; top_k 64; repeat_penalty 1.0 |
| Context / thinking | 4,096 tokens; think=false |
| Output caps | policy 256; selector 256; revision 512 |
| Seeds | 101–105 for first policy calls; role/step offsets configured but never reached |
| Seed evidence | Ollama accepted options.seed; two same-seed non-diagnostic smoke responses matched; stronger determinism unverified |
| Planned calls | About 285–465 at 2–3 steps; conservative ceiling 1,365 |
| Actual diagnostic calls | **5 policy, 0 selector, 0 revision** |
| Actual diagnostic tokens | 1,530 reported prompt tokens, 287 generated tokens |
| Actual elapsed | **19.58 seconds** for pilot schedule; model-call time sum 19.33 seconds |
| Paid API cost | **$0**; local compute/electricity only |

Two additional non-diagnostic feasibility calls used 50 reported prompt tokens and
12 generated tokens (about 9.42 seconds including initial load). Total model requests
for this task: **7**, counting those two smoke calls. The pre-run 1–3-hour expectation
assumed real diagnostic trajectories; fast termination is not an efficiency result.
No diagnostic output was truncated: all five responses ended with `done_reason=stop`,
54–65 output tokens, and 306 reported prompt tokens. No provider errors occurred.

Exact model metadata and provider template are saved in
[model metadata](results/gemma4e-64k_latest_runtime.json). Ollama does not expose the
final rendered token prompt here; exact messages/options and its template are saved
instead. The isolated server was shut down after the pilot; no monitoring or follow-up
inference was scheduled.

## Results by world: primary A/B/C

“Isolation” below is the end-to-end attempted-episode outcome, including invalid
outputs. The zero is caused entirely by the interface failure. It is **not** a measured
native diagnostic-success rate. “Cost spent” is not cost-to-success.

| World | Arm | Attempts | Invalid initial output | Isolated | Executed checks | Cost spent | Steps to isolation |
|---|---|---:|---:|---:|---:|---:|---|
| H1 | A | 5 | 5 | 0/5 | 0 | 0 | N/A |
| H1 | B | 5 | 5 | 0/5 | 0 | 0 | N/A |
| H1 | C | 5 | 5 | 0/5 | 0 | 0 | N/A |
| H2 | A | 5 | 5 | 0/5 | 0 | 0 | N/A |
| H2 | B | 5 | 5 | 0/5 | 0 | 0 | N/A |
| H2 | C | 5 | 5 | 0/5 | 0 | 0 | N/A |
| H3 | A | 5 | 5 | 0/5 | 0 | 0 | N/A |
| H3 | B | 5 | 5 | 0/5 | 0 | 0 | N/A |
| H3 | C | 5 | 5 | 0/5 | 0 | 0 | N/A |
| H4 | A | 5 | 5 | 0/5 | 0 | 0 | N/A |
| H4 | B | 5 | 5 | 0/5 | 0 | 0 | N/A |
| H4 | C | 5 | 5 | 0/5 | 0 | 0 | N/A |

Each primary arm has 20 attempts, all invalid before its condition-specific processing.
A vs B vs C diagnostic performance is **not estimable** from this pilot.

## B canonical versus reversed menu — separate sensitivity analysis

| World | Canonical attempts / invalid | Reversed attempts / invalid | Selector calls | Order effect |
|---|---|---|---:|---|
| H1 | 5 / 5 | 5 / 5 | 0 | Not measured |
| H2 | 5 / 5 | 5 / 5 | 0 | Not measured |
| H3 | 5 / 5 | 5 / 5 | 0 | Not measured |
| H4 | 5 / 5 | 5 / 5 | 0 | Not measured |

Both menu strings are retained in the step records, but neither was sent to the model:
base-policy validation failed first. Identical failure counts are not ordering robustness.

## First-action choices

Executed first actions: **none** in every world/arm. Invalid-output outcome: five per
world/arm. For transparency only, the unexecuted raw text contains these action fields:

| Unique response | Seed | Apparent field in invalid raw output | Executed action |
|---|---:|---|---|
| call-00001 | 101 | C | None |
| call-00002 | 102 | A | None |
| call-00003 | 103 | C | None |
| call-00004 | 104 | C | None |
| call-00005 | 105 | C | None |

These apparent fields are a description of raw text, **not scored actions**. We did
not remove fences, execute the apparent tool, or attach action-quality scores to it.
The same initial symptom and tool list were supplied in every world; no world-specific
evidence had been acquired.

## Expected-optimal rate, isolation, cost and steps

| Metric | Pilot 1 result | Interpretation |
|---|---|---|
| Expected-optimal executed-action rate | **N/A (0 executed actions)** | No action-quality denominator |
| Top-2 executed-action rate | N/A | Same limitation |
| Optimal decision yield including invalid attempts | 0/5 per world/arm | Pipeline yield only, retaining failures in the denominator |
| Attempted-episode isolation rate | 0/5 per world/arm | Format failure before investigation |
| Cumulative diagnostic cost spent | 0 for every attempt | No calls to the evidence oracle |
| Cost to successful isolation | N/A | No successful episodes |
| Executed steps | 0 for every attempt | Not “zero-step success” |
| Steps to isolation | N/A | No isolation occurred |
| Zero-information checks | Count 0; rate N/A | No check executed |
| Redundant repeats | Count 0; rate N/A | No check executed |
| Evidence-conditioned switching | Not measured | No evidence arrived |

F remained available in every initial prompt. Its selection would not have counted
as isolation failure: the unchanged oracle isolates a world through F at cost 5 and
one step. None was executed. Cost and step objectives remain separate; low
eliminations-per-cost is not synonymous with failed isolation.

## PF selected versus activated versus intervention versus action

| Stage | A | B canonical / B reversed | C retained |
|---|---|---|---|
| Base proposal generation | Shared initial calls | Shared initial calls | Shared initial calls |
| Model PF selection | Not applicable | **Not reached** | Not applicable |
| Selected PF IDs | Null | Null (not empty successful selection) | Null |
| Retained configuration | None | Model-selected path configured | Five support IDs configured |
| Native should_activate evaluation | Not applicable | Not reached | Not reached |
| Actual PF firings | 0 | 0 | 0 |
| Interventions | 0 | 0 | 0 |
| Executed diagnostic actions | 0 | 0 | 0 |

C's retained list is configuration, not evidence that its PFs fired. There are no
selected-PF/action alignment rates and no native selector outputs to interpret.
The zero firing count must not be described as gates refusing activation: dispatch
never ran. Earlier checkpoint mechanical probes remain separately labeled and are
not used as pilot behavioral results.

## Representative full trajectories and raw traces

All five unique trajectories are provided in
[full trajectory transcripts](analysis/PILOT1_TRAJECTORIES.md), including exact input,
options, complete raw response, every affected episode ID and terminal state.
Machine-readable counterparts: [full trajectories JSONL](traces/pilot1_full_trajectories.jsonl).

Representative example, call-00001, seed 101, unmodified content:

````text
```json
{
  "action": "C",
  "reason": "Since the checkout returns a generic HTTP 500, inspecting the backend exception and correlated application logs is the most direct way to find the root cause."
}
```
````

Trajectory: initial complaint → base generation above → strict `json.loads` rejects
the opening backticks → `invalid_output` at `base_policy` → no selector, no dispatch,
no revision, no action, no evidence. The offline viable set remains H1/H2/H3/H4.
The other four trajectories terminate at the same stage; no intermediate events
have been omitted.

Primary audit files:

- [Raw model requests and responses](results/pilot1/calls.jsonl)
- [Requests recorded before sending](results/pilot1/requests.jsonl)
- [All 80 step/attempt records](results/pilot1/steps.jsonl)
- [All 80 terminal episode records](results/pilot1/episodes.jsonl)
- [World/arm CSV](analysis/pilot1_by_world_arm.csv)
- [Machine-readable summary and source audit](analysis/pilot1_summary.json)
- [Frozen run manifest](results/pilot1/manifest.json) and [completion record](results/pilot1/completion.json)

The original manifest records `running` because it was saved before inference and
left immutable; `completion.json` records the final `complete` schedule status.

## Failures and unchanged evaluation

Failure mode: all five independent seed outputs include Markdown code fences despite
the request for exactly one JSON object. The action parser's bare-JSON contract was
explicit in the approved design; its refusal is expected code behavior, **not an
identified evaluator bug**. No automatic retry, fallback action, output cleaning,
provider JSON mode, model switch or second run occurred.

This exposes a limitation of the experiment harness's chosen interface for this
runtime. It does not establish a flaw in HASP's native PF selection, whose parser
accepts its own native PF tags and was never invoked.

A post-run audit verified hashes against both the frozen copies and live sources for
`evaluator.py`, `oracle.py`, `hypotheses.py`, `actions.py`, `native_adapter.py`, the pilot
runner/protocol and native HASP implementation files. They are unchanged. The original
checkpoint artifacts and report are preserved. The new analysis script reads results
and performs accounting only; it does not redefine diagnostic scoring.

The pre-run oracle tests passed. Three fake-output harness contract checks confirmed
that F is accepted as isolation at cost 5, selected PF IDs remain distinct from the
revised action, and invalid revisions remain failures. These are infrastructure
checks, not additional model trials. The post-run audit also verified 80 unique
scheduled episode IDs, five model calls, exact 16-way call references, no truncation,
no hidden world/score fields in model requests, and zero executed actions.

## Observations supporting native HASP

No direct behavioral support can be measured: native HASP was not reached. Crucially,
the observed failure is upstream of HASP and shared with A. It provides **no evidence
for the necessity of the proposed selector**. The model's raw responses named
recognizable legitimate checks, but their diagnostic efficiency was not tested.

## Observations challenging native HASP

None about native strategy selection, cost, implicit discrimination or adaptation.
The runnable study pipeline, including the base interface, failed its end-to-end
format contract. Claiming this challenges native HASP would misattribute a custom
harness interface failure to a mechanism that did not run.

## Falsification conclusion and review stop

**The need for a proposed discriminative selector remains untested by Pilot 1.** We
cannot say native HASP is reliably economical, and we also cannot say it is poor.
There is no basis here to implement another selector or claim a research gap.

A next experiment would first need an explicitly reviewed interface-only amendment,
for example accepting one fenced JSON object or using a supported structured-output
mode identically across A/B/C. That would change the action-format protocol and must
be documented as a new run, retaining this original result; it would not justify
changing the evaluator or adding a strategy mechanism. No such amendment or rerun
was implemented. **Stopped after Pilot 1 for review, as requested.**
