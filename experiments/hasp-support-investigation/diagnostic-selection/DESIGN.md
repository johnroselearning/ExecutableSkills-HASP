# Controlled diagnostic competition — checkpoint design

## Scope and falsification target

Question: when several investigative PFs apply, does a native HASP-assisted policy
choose checks that discriminate among remaining explanations at low diagnostic cost?
We are trying to falsify the need for an additional selector. Native adaptation was
already demonstrated; absence of an explicit objective is not evidence of inability.
No selector, information-gain algorithm, entropy calculation, PF ranking, or new
orchestration architecture has been added. Simple scoring exists exclusively offline.
The checkpoint takes precedence over the request for eventual repeated model trials.

## Private worlds and evidence assumptions

H1 is fixed across proposed primary trials. H1: a web serializer produces a string
amount instead of a number, causing normalization to fail. H2: missing web checkout
scope triggers an incorrectly surfaced auth exception. H3: a shared normalization
regression breaks both client representations. H4: a shared payment outage breaks
both matched clients. These refine the broad hypotheses into mutually exclusive,
exhaustive, deterministic single-fault worlds. They are not exhaustive real incidents.

H1 and H3 produce the same request capture and exception: a string amount can be
causal or incidental. In H3 even valid mobile numeric amounts fail. Content-Type
charset spelling and X-Checkout-Version also differ innocuously. Captures alone do
not establish causality. Controlled replay F confirms a causal change, but costs 5.
Matched-account/cart/payment/time/backend reproduction B controls confounders.

All checks have fixed cost and return fixed evidence in each world. A reports a
coarse failure boundary; C reports an exception class, so A and C are distinct scopes.
E includes incident-window probes AND per-request outcomes: green global status alone
would not exclude an input-specific dependency failure. A/D/E include the correlation
lookup needed to make the tool usable even without a previously known ID. This is
included in their stated costs. D may capture without exercising mobile checkout;
only B reports mobile success. F performs a complete sandbox isolation suite, not an
unpriced composite of other checks. Repeated checks return identical evidence and
incur full cost; no cache discount or hidden action prerequisite is assumed.

The host reveals evidence only through `Oracle.execute(action)`. Adversarial starting
cases are seeded by actually executing their stated history, not by privileged facts.
Sunk history costs are recorded separately. The initial case contains only the user
complaint. Later cases represent independently sampled investigation snapshots; all
PF fire counts start at zero because the seeding actions were external observations.
In a live episode counts persist across its subsequent steps.

A uniform prior over the four private worlds is conditioned on observed evidence.
The policy is **not told** that these four worlds are exhaustive, their partitions,
priors, or the answer. The optimality reference is an idealized closed-world evaluator,
not proof that a policy can infer its probabilities from an ordinary support ticket.
This epistemic mismatch limits any negative conclusion. The four-world partition
assumptions and subjective costs are experimental choices, not measured facts about
production systems. Strong results would support native HASP in this toy environment;
weak results would not establish a general strategy-selection deficit.

## Public policy interface and cost visibility

Each tool has a neutral description and explicit numeric cost (see actions.py).
Costs are visible equally in A/B/C, so preference for cheap checks is testable.
No outcomes, hypothesis-elimination table, expected utility, ranks or best labels are
visible. No hypothesis IDs occur in policy inputs. All six actions remain available,
including repeated or already non-discriminating checks. The policy must output one
JSON object with `action` and a short `reason`. Actions are parsed exactly; free prose,
multiple objects, unknown IDs or malformed output fail that decision. There is no
LLM judge, fuzzy action mapper, corrective best-action fallback or free diagnostic
retry. Invalid outputs are included in the failure denominator and abort the episode.
Report failures separately and do not misreport their low cost as successful efficiency.

## Native HASP interaction (exact implementation boundary)

Native source: `pf_select/pf_select_eval.py`, at base commit
`2a0e859ef320719d0794fe2ccda5c672a28cc0fb` plus the pre-existing local support PFs.
`src/skills_agent/skills/pf_selector.py` is a different web-search selector with
mandatory web PFs and heuristic fallbacks; it is not this experimental path.

For each decision:

1. `policy_messages(public_state)` supplies complaint, cumulative observed actions,
   observations/costs and the six public tool descriptions. Generate a base proposal.
2. In B, append that assistant proposal and native
   `_PF_SELECT_INSTRUCTION_TMPL.format(menu=menu, candidate=proposal[-1200:])`.
   Keep the native wording, including “candidate answer”; do not insert a
   discriminate/optimize instruction. Record full messages, rendered tokenizer
   prompt, unmodified selector response and provider metadata. Use the same policy
   model for selection. Parse with native `_parse_pf_selection`, accepting empty
   selections; no fallback to all PFs or a heuristic.
3. Call native `execute_program_functions` with selected IDs, support-domain context,
   `INVESTIGATE`, observed structured facts and the base proposal. Record wrapper
   `should_activate` separately from dispatch records/interventions, including fire
   counts. Five pre-existing PFs are loaded unchanged, with native fire cap 1.
4. When injections occur, append `[System Feedback]` plus the complete interventions
   to the original policy conversation, and ask for a revision in the same JSON
   format. This is a policy generation, not an automatic PF-to-action mapping.
   Otherwise execute the original parsed action. Respect any native action rewrite;
   no hidden evaluator correction is permitted.
5. Execute exactly that action in the oracle. Persist evidence and native fire counts.
   Offline only, attach viable hypotheses, per-action scores and eliminated sets to
   the stored trace. The evaluator may stop at singleton isolation or the step cap;
   its singleton signal is not fed into another policy prompt.

The checked-in native adapter implements prompt construction, parsing and dispatch;
the inference/episode loop is deliberately pending review. The retained control
probes use a fixed A proposal solely to test interfaces. They are not observations
about action-selection behavior.

**Fidelity limit:** stock `pf_select_eval` reviews a terminal answer, not an HTTP tool
loop. Using its unchanged primitives on each diagnostic action is the pre-existing
support step adaptation. Per-step reselection and support facts are experiment
invocations, not a claimed native automatic invalidation hook or unmodified stock
benchmark. Fresh native selection in B occurs at every diagnostic step. The five
support PFs are experiment-created reusable PFs, not upstream support capabilities.
This limitation must stay in the eventual report.

## Conditions and ordering

A: base policy without HASP; one proposal per step, no PF menu or revision.
B: native model-selected PFs; full five-PF menu every step, normal parser/dispatch.
C: all five relevant PFs retained throughout the episode; selection bypassed as an
explicit all-retained control. Native gates and fire caps still determine firing.
C is not a model-selection success and has null selector output. It probes whether
pruning PFs hurts or helps. Do not use `force_skill_ids` in B.

B orders: alphabetical native menu and exact reversal of rendered menu lines.
Reversing the library dictionary would not work: `_build_pf_menu` sorts the IDs.
For the primary order comparison, change **only** menu presentation; retain the
native parser output order for dispatch and log it. Any resulting intervention order
change is a mediator of selection, not independently randomized.
C retention/dispatch order stays fixed at IDS in `native_adapter.py`. A has no order.
Do not duplicate A/C into pseudo-independent menu-order samples.

## Sample size, settings and isolation

Five cases × four arms (A, B canonical, B reverse, C) × 30 episodes = **600 episodes**.
Pilot if compute is constrained: 10 per cell = 200 episodes. Each episode has at most
8 paid checks. No cross-trial memory or source browsing. Pair trial seeds across
arms/cases where possible; use separate deterministic per-step/per-role seeds so
extra selector calls do not shift the policy RNG schedule. The first proposal at an
identical case/seed should be reused across arms, preserving its raw response and
usage attribution; subsequent divergent histories are generated independently.

Proposed temperature 0.7 for policy, selection and revision; top_p=1; no thinking
mode if supported consistently; output caps 256 policy, 256 selection, 512 revision.
Model/provider/tokenizer/quantization are not selected or verified yet. Record exact
values, seed support, rendered prompts, all provider requests/responses and token
usage; unsupported seed controls must be recorded as unsupported. Do not claim
reproducibility from seeds alone. Providers that cannot expose a tokenizer-rendered
prompt should record that limitation and the exact messages instead.

## Offline evaluator and stopping

For n viable worlds and an action partition with group sizes n_j:

`expected_eliminations = sum_j (n_j/n) * (n - n_j)`

`expected_eliminations_per_cost = expected_eliminations / action_cost`

Primary best-next rate uses this expectation; secondary realized best-next rate uses
eliminations along fixed H1. No entropy or information-gain code is needed. See all
possible observations and calculations in `analysis/`.

Tied optima all count as optimal. Top-2 includes ties at the second action cutoff,
using competition ranks (1,1,3 rather than 1,1,2). Also report chance baseline per
state (# qualifying actions / 6); a permissive tie must not inflate conclusions.
Only unresolved states contribute diagnostic decision denominators.

Stop at offline singleton isolation or 8 actions. Singleton is identification within
the four-world model, **not causal confirmation** or a correct final diagnosis by the
LLM. A full causal confirmation endpoint would require F and is not the primary
endpoint. Invalid generation, provider errors and budget exhaustion are separate
terminal statuses; no silent dropping or hidden resampling. Models never see the
singleton decision or scorer feedback.

The offline enumerator gives cheapest H1 paths and fewest steps separately. Initial
minimum cost is 2 with B,D or D,B; minimum steps is 1 via F at cost 5. This is a
truth-aware lower bound, not an expected-cost optimal decision tree or implemented
online planner. Compare additional cost with additional-cost bounds and report sunk
cost separately. Do not optimize the policy using this enumeration.

## Measurements and interpretation

Report per arm, case and menu order before pooling:

- Expected-optimal and realized-optimal next-check rates; top-2 rates with ties.
- Isolation success, additional/total cost and steps. Show failures/censoring alongside
  success-only distributions; cheap aborted episodes must not look efficient.
- Zero-expected-discrimination action rate; strict redundant-repeat rate (repeated
  and zero discrimination). A new check may be useless too; keep these distinct.
- PF IDs selected, count >1, native gates, actual firings, injections and executed IDs.
  Selection of `comparison_experiment` alone is never credited as diagnostic success.
- Proposal→execution change frequency, both helpful and harmful changes by offline
  score. This is observed alignment, not proof a PF caused the change: an extra model
  generation can change an answer without feedback. No-feedback revision control
  would be a later experiment if causality becomes essential.
- Paired B-order changes in selections/actions/outcome metrics. A/C have no menu
  manipulation. Compare case-level intervals, not just a pooled percentage.
- Conditional action trajectories, repeats after zero-information evidence, and
  changes from D→B versus B→D. Do not equate a new selected PF with actual switching.
- Descriptive comparison between initial (one activatable PF) and ambiguous cases
  (two or three); evidence differs, so this does not isolate a causal effect of
  “more relevant PFs.” A matched PF-menu ablation is unresolved future work.

Use episode-level bootstrap intervals for costs and per-episode rates; Wilson
intervals for independent first decisions. Do not treat correlated steps as independent
trials. With n=30, even 30/30 gives a two-sided 95% Wilson lower bound about 88.6%;
with n=10 it is about 72.2%. Failure to detect an order effect is not equivalence.

For review, provisional descriptive evidence against needing a selector: >=90%
expected-optimal next actions, >=95% isolation, median cost <=1.1× the fixed-world
bound, <=5% redundant repeats and <=5 percentage-point order effect, assessed per
case with uncertainty. These are design thresholds, not established results or
powered equivalence margins. Retain continuous measurements regardless of thresholds.
A stronger claim requires more cases/worlds and adequate precision.

## Compute estimate and availability

No inference was attempted. Read-only local checks found an Ollama executable but
no responding service at localhost:11434; `nvidia-smi` and GPU device paths were not
available. The earlier dependency audit records incompatible published runtime pins;
this checkpoint did not install packages, fix pins or establish a usable model.

At 8 decisions/episode with revisions every HASP step, the upper-bound calls are:
A 1 + B canonical 3 + B reverse 3 + C 2 = 9 per matched case/trial/step.
For 30 trials: 5×30×8×9 = **10,800 calls** (pilot: 3,600).
Sharing identical initial proposals saves up to 450 calls (pilot: 150), so these are
conservative ceilings. Average 2 steps would be roughly 2,700 calls before reuse.

At output caps the maximum is 5×30×8×(256+1024+1024+768) = **3,686,400 output tokens**.
Pilot cap: 1,228,800. Assuming 2,000–6,000 input tokens per call, input planning
range is **21.6–64.8 million tokens** at the call ceiling. Actual history/tokenizer
counts and whether all PFs fire matter; this is not a measured token forecast.
API cost = input_millions×provider_input_rate + output_millions×provider_output_rate;
no model/provider chosen means no honest dollar quote yet. There are no API charges
at checkpoint.

For a hypothetical 8-billion-parameter model, weight storage alone is about 16 GB at
2 bytes/parameter or 4 GB at 4 bits/parameter; runtime, quantization metadata and KV
cache add memory. A local CPU/quantized runtime may be possible, but speed and capacity
are unverified. Wall-clock runtime must be estimated from a small approved pilot's
observed throughput, not guessed. No GPU or API purchase is authorized at checkpoint.

## Review checkpoint

Implemented: deterministic environment, offline evaluator, complete matrix, expected
and realized calculations, verified native prompt/parser/dispatcher integration,
competition probes, resource estimate and planned A/B/C protocol. No expensive or
cheap model experiments have run. Stop here for the user's design review.
