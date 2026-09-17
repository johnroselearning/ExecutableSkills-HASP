# Pilot 1b — native HASP reached; reliable isolation, weak cost efficiency

**Native HASP did not show reliably economical diagnostic action selection in this
pilot.** It usually acquired enough evidence to isolate the world, and occasionally
changed a proposal into the evaluator's best check. However, native model-selected
HASP had higher mean cost than the base model, low expected-optimal action rates,
and mostly adverse proposal-to-action score changes. These are observations about
this model, support adapter, PF set and synthetic environment—not evidence of novelty
or proof that another selector is necessary.

The narrow question about *simultaneously applicable strategies* remains only weakly
tested: after native fire caps, multiple PFs were eligible on just **3/55 B dispatches**
and **0/69 C dispatches**. Many PF selections did not activate. Do not equate multiple
selected IDs with actual strategy competition.

All **80 scheduled attempts** finished. No larger experiment, output repair after
results, evaluator change or new strategy mechanism followed. The local server is stopped.

## What Pilot 1 taught us

Pilot 1 remains a legitimate, unchanged interface result: completed attempts, diagnostic
comparison not reached because the experiment-specific parser rejected whole-output
Markdown-fenced JSON. Its five unique initial responses affected 80 paired attempts;
zero executed actions were never interpreted as a 0% native HASP score.

Pilot 1b's offline contract audit successfully parsed those five historical responses,
saving raw text, normalized text and action IDs. **Those historical actions were never
executed or rescored.** All model generations reported below are from the new run.

## What Pilot 1b changes

Only the policy/revision parser's interface compatibility changed: bare JSON or one
complete outer JSON/untagged Markdown fence is accepted. Surrounding prose, multiple
objects, malformed JSON, unknown action IDs and missing fields remain invalid.
Normalization delegates to the original schema/action validator. No JSON decoding
mode, retry, fallback, action inference or diagnostic hint was added.

Positive/negative parser tests and the existing oracle tests passed before inference.
The original runner, native adapter, oracle, hypotheses, actions/costs, evaluator,
HASP prompts/PFs/dispatcher, model and sampling remain unchanged. A new wrapper binds
the amended parser and output directory to the original loop. Frozen source copies
and a post-run audit verified **49 pre-existing artifacts unchanged**, including all
Pilot 1 reports, manifests and traces.

Protocol and audit: [pre-run amendment](PILOT1B_PROTOCOL.md),
[historical parser contract](results/pilot1b/historical_parser_contract.json),
[frozen manifest](results/pilot1b/manifest.json),
[completion record](results/pilot1b/completion.json).

## Runtime and sample

- Local `gemma4e-64k:latest`, installed parent `gemma4:e4b`, reported 8.0B, Q4_K_M GGUF;
  same model digest as Pilot 1. Ollama 0.31.2, Radeon 780M/Vulkan, 8 host threads.
- Temperature 0.7; top_p 1; top_k 64; repeat_penalty 1.0; context 4096; think=false.
  Output caps: policy 256, selector 256, revision 512. No provider JSON mode.
- Four worlds × five seeds 101–105 × A/B/C/B_reverse = 80 attempts. A/B/C are the
  **60 primary attempts**; B_reverse is a separate 20-attempt sensitivity arm.
- All start from the initial complaint; maximum eight checks. Initial proposals were
  generated anew, then shared within this run exactly as before. There are **five
  unique first-proposal samples**, not 80 independent samples. Role/step seed offsets,
  schedule rotation and native fire caps are unchanged. Seed acceptance is verified;
  exact GPU sampling reproducibility is not guaranteed.
- **341 model calls:** 145 policy, 104 selector, 92 revision. Reported usage: **185,132
  prompt tokens and 20,609 output tokens**. Wall time **1,862.3 seconds (31.0 minutes)**.
  **$0 API charges**; local electricity/compute only. No new feasibility inference.
- No truncations, provider errors, dispatcher errors or step-cap terminations.
  Four episodes ended on invalid base-policy JSON after two successful checks.

## Primary A vs B vs C

Rates score **executed actions** using frozen expected eliminations per cost. Cost
spent includes failed episodes; success-only cost/steps are shown separately so failed
episodes cannot appear artificially efficient. Isolation is the evaluator detecting a
singleton world, not a model-authored final diagnosis or causal-confirmation claim.

| Arm | Valid actions / decision attempts | Isolation | Expected-optimal | Top-2 | Mean cost spent | Mean cost, successes | Mean steps to isolation |
|---|---|---|---|---|---:|---:|---:|
| A: base | 43/43 | 20/20 | 0/43 (0.0%) | 10/43 (23.3%) | 8.40 | 8.40 | 2.15 |
| B: native selected | 55/57 | 18/20 | 1/55 (1.8%) | 8/55 (14.5%) | 9.10 | 9.33 | 2.83 |
| C: all retained | 69/69 | 20/20 | 3/69 (4.3%) | 10/69 (14.5%) | 10.10 | 10.10 | 3.45 |

Mean per-episode optimal-action rates are A 0%, B 1%, C 3%; the table's pooled rates
weight longer trajectories more heavily. Including invalid decisions in the optimal
yield denominator gives A 0/43, B 1/57, C 3/69. No failures are dropped. Expected-optimal
rate alone is not the definition of success: F is an informative, valid action that
can isolate in one step at cost 5 without maximizing eliminations per cost.

Within this sample, B spent 0.70 more cost units per attempted episode than A; C spent
1.70 more. The success-only comparison also favors A. This is descriptive, not a
statistically established treatment effect or proof of causation by any individual PF.

## Results by world — primary comparison

“Steps” below means mean executed steps across all attempts. B's failed H1/H3 attempts
spent two steps and cost 7 each; success-only means follow the table. Every row has five
episode attempts. Optimal/top-2 columns use the executed-action denominator.

| World | Arm | Valid actions / decisions | First executed | Optimal | Top-2 | Isolated | Mean cost | Steps | Zero-info checks | Redundant repeats |
|---|---|---|---|---|---|---|---:|---:|---:|---:|
| H1 | A | 16/16 | A:1, C:4 | 0/16 | 5/16 | 5/5 | 12.60 | 3.20 | 5 | 1 |
| H1 | B | 18/19 | A:5 | 0/18 | 4/18 | 4/5 | 12.80 | 3.60 | 4 | 2 |
| H1 | C | 25/25 | A:5 | 1/25 | 5/25 | 5/5 | 14.80 | 5.00 | 10 | 2 |
| H2 | A | 6/6 | A:1, C:4 | 0/6 | 0/6 | 5/5 | 4.60 | 1.20 | 0 | 0 |
| H2 | B | 13/13 | A:5 | 0/13 | 0/13 | 5/5 | 8.40 | 2.60 | 3 | 1 |
| H2 | C | 15/15 | A:5 | 0/15 | 0/15 | 5/5 | 9.20 | 3.00 | 5 | 1 |
| H3 | A | 16/16 | A:1, C:4 | 0/16 | 5/16 | 5/5 | 12.60 | 3.20 | 5 | 1 |
| H3 | B | 19/20 | A:5 | 1/19 | 4/19 | 4/5 | 12.20 | 3.80 | 5 | 1 |
| H3 | C | 24/24 | A:5 | 2/24 | 5/24 | 5/5 | 13.40 | 4.80 | 9 | 1 |
| H4 | A | 5/5 | A:1, C:4 | 0/5 | 0/5 | 5/5 | 3.80 | 1.00 | 0 | 0 |
| H4 | B | 5/5 | A:5 | 0/5 | 0/5 | 5/5 | 3.00 | 1.00 | 0 | 0 |
| H4 | C | 5/5 | A:5 | 0/5 | 0/5 | 5/5 | 3.00 | 1.00 | 0 | 0 |

B success-only H1 means: cost **14.25**, steps **4.00**. H3: cost **13.50**, steps
**4.25**. All other primary world/arm rows completed every episode, so their means
already equal success-only means.

The fixed-world minimum costs are H1/H3 **2** (B→D or D→B), H2/H4 **1** (D).
These are privileged, truth-aware lower bounds, not a policy available to the agent.
No arm approached them in this pilot. Conversely, H4 demonstrates real economy
relative to the base arm: native feedback reduced observed mean cost from 3.8 to 3.0
with one executed action. The expected score still ranks that first action below D;
realized outcome and expected discrimination must not be conflated.

## Zero-information actions and redundant repeats

| Arm | Zero-information checks / executed | Strict redundant repeats / executed | F executions |
|---|---|---|---:|
| A | 10/43 (23.3%) | 2/43 (4.7%) | 10 |
| B | 12/55 (21.8%) | 4/55 (7.3%) | 7 |
| C | 24/69 (34.8%) | 4/69 (5.8%) | 7 |
| B_reverse, separate | 6/49 (12.2%) | 3/49 (6.1%) | 8 |

A new check can be non-discriminating without being a repeat. F's 32 executions all
provided singleton isolation; none was classified as a diagnostic failure. Its cost
and step efficiency are separate from the expected-optimal rate. The four invalid
raw F proposals described below were never executed or scored.

## PF selected → activated → intervention → executed action

Native selection, gates and feedback were actually reached. B selected multiple PFs
on **17/55** turns (30.9%); B_reverse on **22/49** (44.9%). There were no empty or
nonempty-unparseable selector results. Counts below are not action-success counts.

| PF | B selected / 55 | B activated / 55 dispatches | C activated / 69 retained dispatches | B_reverse selected / 49 | B_reverse activated / 49 |
|---|---|---|---|---|---|
| evidence_collection | 38 | 19 | 20 | 26 | 18 |
| request_id_trace | 13 | 0 | 0 | 32 | 0 |
| comparison_experiment | 2 | 0 | 0 | 1 | 0 |
| dependency_trace | 9 | 6 | 15 | 6 | 4 |
| binary_isolation | 10 | 2 | 8 | 6 | 0 |

C retained all five PFs and has no model-selected IDs. There were 27 B, 43 C and
22 B_reverse intervention/revision turns. The per-world selection/gate/activation
counts for every PF are in [the full tables](analysis/PILOT1B_TABLES.md#pf-frequency)
and [PF-frequency CSV](analysis/pilot1b_pf_frequencies.csv). Actual gate results,
interventions and actions are separate fields in every raw step record.

Request tracing was often selected when its gate could not activate: no request ID
was yet available, or the trace was exhausted. The comparison PF requires already
observed web failure/mobile success, a prerequisite the typical paths had not obtained.
When B finally isolated a world, offline stopping prevented another PF-selection turn.
Thus absence of comparison-PF activation is not evidence that it could never work.

### Coverage of actual competition

A post-hoc, CPU-only audit checked all five unchanged native gates at each recorded
pre-dispatch state, including its real fire counts. It did not dispatch PFs or affect
inference. Multiple PFs were eligible on **B 3/55**, **C 0/69**, **B_reverse 4/49**
dispatches. Ignoring the fire cap only as an explicitly counterfactual prerequisite
audit gives 23/55, 20/69 and 27/49 overlaps respectively. Those counterfactual counts
are not actual activations. [Coverage audit](analysis/pilot1b_gate_coverage.json).

This pilot tests the whole native support-step pipeline along its chosen paths more
strongly than it tests selection among several simultaneously eligible PFs. The initial
state activates only evidence collection; the chosen paths and one-fire cap reduced
later competition. The cap was not reset or relaxed to manufacture competition.

## Proposal-to-action changes: improved, unchanged, worse

Scores compare base and executed actions in the **same pre-action evidence state**.
“Unchanged score” includes unchanged actions; the changed-action count is separate.
These associations are not causal proof: an extra model generation can alter output
without a PF, and no no-feedback revision control was run.

| World | Arm | Executed | Action changed | Improved score | Unchanged score | Worse score |
|---|---|---:|---:|---:|---:|---:|
| H1 | B | 18 | 7 | 0 | 11 | 7 |
| H1 | C | 25 | 11 | 1 | 14 | 10 |
| H2 | B | 13 | 7 | 0 | 6 | 7 |
| H2 | C | 15 | 9 | 0 | 6 | 9 |
| H3 | B | 19 | 9 | 1 | 10 | 8 |
| H3 | C | 24 | 11 | 2 | 13 | 9 |
| H4 | B | 5 | 4 | 0 | 1 | 4 |
| H4 | C | 5 | 4 | 0 | 1 | 4 |
| ALL | B | 55 | 27 | **1** | 28 | **26** |
| ALL | C | 69 | 35 | **3** | 34 | **32** |
| ALL, separate | B_reverse | 49 | 22 | **0** | 29 | **20** |

All four improvements were **F→B**, raising expected eliminations per cost from **0.2
to 1.0** after the available evidence left H1/H3. The activated PF was binary_isolation;
the executed action was matched-client comparison B, not PF-named “binary isolation.”
In B's H3 trial 3, both binary_isolation and request_id_trace were selected, but only
binary_isolation activated. This is why PF names cannot stand in for executed checks.

## Does native HASP reduce generic debugging heuristics?

**Not in the desired direction in this pilot.** The five newly generated initial
proposals were C, A, C, C, C. A executed those proposals, giving C:4/A:1 per world.
All HASP arms executed A first in every world/trial. Feedback changed generic
“inspect logs” into generic “trace the request,” not initially into B or D.

Across all primary B actions there were 19 C→A and 5 C→E changes; C had 19 C→A and
12 C→E changes. There were **no direct A/C→B/D changes** in either primary HASP arm.
The helpful comparison changes arose later from F proposals. Eight C-arm D actions
and two B-arm D actions came from D base proposals, not a revision changing another
action into D. These later captures were often zero-information under the then-remaining
worlds, which further distinguishes “comparison-like action” from diagnostic value.

“Worse score” is not necessarily a worse realized outcome: C→A in H4 saves one cost
unit and still isolates. Conversely, requesting dependency checks after a known internal
failure boundary often has zero discrimination. Both patterns remain visible rather
than being collapsed into a blanket good/bad strategy label.

## B canonical versus reversed menu — separate sensitivity analysis

| World | Reverse valid / decisions | First executed | Optimal | Top-2 | Isolation | Mean cost spent | Mean executed steps | Zero-info | Repeats |
|---|---|---|---|---|---|---:|---:|---:|---:|
| H1 | 17/18 | A:5 | 0/17 | 4/17 | 4/5 | 12.20 | 3.40 | 3 | 1 |
| H2 | 11/11 | A:5 | 0/11 | 0/11 | 5/5 | 7.60 | 2.20 | 1 | 1 |
| H3 | 16/17 | A:5 | 0/16 | 4/16 | 4/5 | 12.00 | 3.20 | 2 | 1 |
| H4 | 5/5 | A:5 | 0/5 | 0/5 | 5/5 | 3.00 | 1.00 | 0 | 0 |

Reverse overall: 49/51 valid decisions, 18/20 isolated, mean cost spent 8.70, success-only
cost 8.89 and success-only steps 2.50. Success-only H1: cost 13.50/steps 3.75; H3:
cost 13.25/steps 3.50. Invalid decisions remain in the recorded attempted totals.

Compared with canonical B, initial selected-ID **sets differed in 13/20 pairs**, yet
first executed actions differed in **0/20**. Full action paths differed in **7/20**;
mean reverse-minus-canonical cost was **−0.40** (median 0), and isolation statuses
matched in every pair. Request-trace selections rose from 13/55 to 32/49, but that PF
never activated in either order. Selection-level ordering sensitivity therefore did
not translate directly into first-action differences.

These are 20 paired world/seed records, with shared first proposals and only five
trial seeds. Later inputs differ once paths diverge; GPU nondeterminism is not excluded.
The small pilot establishes neither ordering equivalence nor a general benefit from
reversal. [All paired comparisons](analysis/pilot1b_order_pairs.csv).

## Failures and executed-action validity

Four calls failed in base-policy generation at the **third decision**, after A→C:
H1-t5-B, H1-t5-B_reverse, H3-t5-B, H3-t5-B_reverse. Their outer fences were accepted,
but JSON strings contained illegal backslash-backtick escapes around
`CheckoutNormalizationError`. `json.loads` correctly rejected them.

These are new, legitimate interface failures distinct from Pilot 1's rejected outer
fences. They occurred at matching seed/history patterns; do not treat them as four
independent discoveries. They were not repaired, retried, normalized further or counted
as executed F actions. The two completed checks in each failed episode remain scored
and their cost 7 remains in totals. No final diagnostic decision is imputed.

All 216 executed actions were valid. Across **220 decision attempts**, four were invalid;
A validity was 100%, B 55/57 (96.5%), C 100%, reverse 49/51 (96.1%). No revision failed
validation and no selector call produced an empty/unparseable selection. The individual
raw failures and full traces are retained in the summary and trajectory files.

## Representative full trajectories

| Example | Actual sequence | Cost | What it illustrates |
|---|---|---:|---|
| H1-t1-A | C→A→F | 12 | Base isolation with an intervening zero-information trace |
| H1-t1-B | A→C→F | 12 | Native selection reached; successful F remains credited |
| H1-t1-C | A→E→C→D→F | 15 | All retained; added zero-information checks |
| [H3-t3-B](traces/pilot1b_H3_t3_B.json) | A→E→C→D→B | 11 | Binary-isolation feedback associated with helpful F→B revision |
| H3-t3-C | A→E→C→D→B | 11 | Helpful late change does not make the whole path low-cost |
| H4-t1-A versus B | C versus A | 4 versus 3 | Native feedback reduces realized cost in one world |
| H1-t5-B | A→C→invalid JSON | 7 spent | Legitimate failure; proposed F never executed |

[Full representative transcripts](analysis/PILOT1B_TRAJECTORIES.md) include first-trial
world/arm cases, the first improved/worse score change and all failures. For every
one of the 80 attempts, [full trajectory JSONL](traces/pilot1b_full_trajectories.jsonl)
contains complete requests, raw model responses, cumulative evidence, full menus,
selected IDs, gates, interventions, revisions, actions and offline scores.
[Enriched scored steps](traces/pilot1b_scored_steps.jsonl) explicitly list offline best
checks and proposal/execution score changes. Original raw
[calls](results/pilot1b/calls.jsonl), [steps](results/pilot1b/steps.jsonl) and
[episode records](results/pilot1b/episodes.jsonl) remain unchanged.

## Strongest evidence supporting native HASP

1. Native model selection, tag parsing, gates and feedback operate through multi-step
   investigations; this was not a forced-PF simulation. B acquired isolation evidence
   in 18/20 attempts; the two failures were JSON validity issues after useful actions.
   C acquired isolation evidence in 20/20.
2. There are genuine high-discrimination improvements: one B and three C F→B revisions
   chose the best check for H1/H3 and saved four units versus the proposed F at that step.
   This falsifies any categorical claim that native HASP cannot make such a switch.
3. H4's native paths reduced realized cost relative to the base model while retaining
   one-step isolation. F also offered reliable one-step completion from unresolved states.
4. Large differences in first PF sets under reversal did not change first executed
   actions. Selection variation alone would exaggerate action-level sensitivity.

## Strongest evidence challenging native HASP

1. Native assistance did not improve overall cost relative to A in this sample; all-
   retained C spent the most. Successful episodes were also more costly on average.
2. Expected-optimal choices were rare. Zero-information checks were common, particularly
   in C, and strict redundant repeats occurred in all arms.
3. Most proposal-to-execution score changes were adverse under the fixed metric:
   B 26 worse versus 1 improved; C 32 versus 3. Generic trace/dependency heuristics
   often displaced other checks rather than becoming discriminating comparisons.
4. Native selected PF IDs often did not activate, and selection changed with menu order.
   These are measurements of this configuration, not conclusions about all HASP setups.

## Does this falsify the need for another selector?

**It does not establish a need for another selector, and it does not show native HASP
already near-optimal in cost.** Basic isolation was already reliable without one—A
and C both achieved 20/20—so necessity for basic task completion is weakened. A
potential efficiency benefit remains possible, but no proposed selector was tested.
The actual simultaneous-eligibility coverage is too sparse to make a strong claim
about that narrow mechanism.

Several explanations remain unresolved: this local model's generic debugging habits,
the support PF interventions, native fire caps, the step adapter, the objective and
closed-world evidence/cost assumptions. The evaluator knows an exhaustive four-world
model and uniform prior that the policy does not. F can be reasonable causal verification
in real support work even when a cheaper closed-world check exists. Poor score here is
not proof of poor reasoning in general.

Only five seeds were used, with shared first proposals and correlated paths across
worlds. No population-significance claim or causal claim about feedback/order follows.
The unchanged native primitives are still embedded in a synthetic support-step adapter,
not the stock terminal-answer benchmark. **No novelty claim, new selector, larger
experiment or post-result protocol repair was made. Stopped after Pilot 1b for review.**
