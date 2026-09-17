# HASP Strategy Experiment: Findings

## Scope and Reproducibility

Five independent support PFs are implemented in
`skills/executable/support/skills.py`, with matching native `SKILL.md` cards:
`evidence_collection`, `request_id_trace`, `comparison_experiment`,
`dependency_trace`, and `binary_isolation`. They use HASP's existing
`@pf_skill`, `Anchor`, `should_activate` and `inject` conventions. Their cards
have equal priority. The previous insufficient-evidence PF is excluded from
the five-item experimental menu.

`support_strategy_trials.py` imports the actual HASP menu builder, unchanged
selection instruction, tag parser and dispatcher. The model sees only the
five relevant support cards, giving these strategies a favorable menu with no
unrelated distractors. Neither ranking nor a new strategy selector is added.
Structured observed facts are supplied by the synthetic fixture; extracting
those facts automatically from incident evidence is not tested.

The first model condition uses fixed base proposals. E2 onward deliberately
retains tracing as the proposed direction, testing repair of an earlier plan.
A second condition generates a base proposal before revealing the PF menu,
at E2, E4 and the invalidation control. These are two different conditions,
not exchangeable samples.

E0-E4 are cumulative: E2 retains E1's endpoint and request ID. A separate
`E2_standalone` excludes that ID. At E3 the fixture names two differing headers;
this supplies a finite input set for binary isolation, but does not assert
that either header causes the failure. E5 adds exhausted trace evidence and
verified successful downstream calls. No actual support incident, trace lookup,
replay, deployment change or causal outcome is executed.

Model inference uses local Ollama with native HASP selection messages. This
adapts the final-answer evaluation protocol to support investigative steps;
it does not run the optional `HASP_STEP_DISPATCH` consent channel or reproduce
the authors' vLLM benchmark. Full selections and responses are retained, with
provider termination metadata. A response ending at the token limit must not
be treated as a complete plan. Selection is invoked afresh per fixture by the
experiment; that is not evidence of an automatic reconsideration hook.

## Mechanical Results

All 32 subsets of the five PFs are exercised at seven states, plus reversed
order and two retained-selection trajectories: 243 dispatch records total.
Every supplied selected PF reached its gate without an exception.

With all five selected and fresh fire counts:

| State | Activating PFs |
| --- | --- |
| E0 | evidence_collection |
| E1 | evidence_collection, request_id_trace, dependency_trace |
| E2 | evidence_collection, request_id_trace, comparison_experiment, dependency_trace |
| E3 | request_id_trace, comparison_experiment, dependency_trace, binary_isolation |
| E4 | request_id_trace, comparison_experiment, dependency_trace, binary_isolation |
| E5 invalidation | comparison_experiment, binary_isolation |
| E2 standalone | evidence_collection, comparison_experiment |

Reversing selection reverses injection order; it does not choose a winner.
Because all five PFs inject context, the dispatcher leaves the proposed action
unchanged. A subsequent model revision is necessary to observe the final
proposed investigative action. Mechanical runs explicitly leave that revision
unobserved rather than equating an injection with a changed policy decision.

With all five selected once and fire counts retained, the observed progression
is collection at E0, tracing/dependencies at E1, comparison at E2, isolation at
E3, and no further injections at E4/E5. That progression follows independent
prerequisite gates and default one-fire limits. It is a direct counterexample
to claiming that HASP cannot change the visible investigative direction unless
it has a new intra-skill selection mechanism. With only request tracing selected
at episode start, no comparison PF is later added.

## Questions A-G

**A. Competing plausible PFs.** In the evaluated path, the policy model receives
the problem/evidence, its candidate answer, and an alphabetically ordered menu
of ID/summary pairs. The native instruction asks for the most relevant PFs and
allows any number. It does not require choosing between tracing and comparison.
The tag parser preserves the model's order and removes duplicate/unknown IDs;
the dispatcher checks every selected PF independently. There is no arbitration
between the two strategies in this path.

**B. Semantic matching.** Relevance from natural-language descriptions is the
explicit selection interface. It is not justified to conclude the LLM *merely*
performs surface matching: the prompt includes incident context and the proposal,
so the model can reason about them. Native selection requests tags only, giving
no direct explanation of why one PF was selected. PF activation adds executable
prerequisite checks after model selection.

**C. Greatest discriminating evidence.** No inspected native selection objective
compares predicted observations, hypothesis partitions, uncertainty reduction or
expected experimental benefit. That is a code-level finding, not a claim about
what an LLM can infer internally. A model can propose a controlled comparison
or prioritize a useful experiment in free text without a dedicated data object
or optimizer. Final-policy explanations are not selector explanations, and
mentioning a one-factor replay does not establish that it maximizes evidence.

**D. Simultaneous selection.** Yes. The native instruction explicitly allows any
number and the parser returns a list. The forced-subset tests establish joint
activation; model trials test whether it actually occurs without forcing.

**E. Execution and prioritization.** `execute_program_functions` loops over
`active_skill_ids` in order. Injections accumulate. If a PF rewrites an action,
later PFs see that rewritten action, so order can affect results in general.
There is no strategy-utility ranking in this dispatcher. However, other HASP
paths do have selection priorities: `SkillSelector.select` scores mode and
trigger matches; phase instructions sort by `priority_boost`; the older
`PFSelector` uses top-k, mandatory PFs and a heuristic fallback. The optional
step-consent channel requires a named error and orders/caps repairs by step.
Those facts rule out a blanket claim that HASP never prioritizes anything.

**F. Invalidated direction.** Supplied invalidation facts cause the relevant
local PF gates to decline in a fresh dispatch. The dispatcher does not respond
by retrieving a replacement PF. The older agent runner selects its active PF
list at episode start; this experiment's fresh-per-state model calls are a
harness choice. Already-selected alternatives can become applicable as evidence
changes. HASP also has existing repeated-search and contradictory-evidence
corrections, so it is false to say HASP cannot prompt any reconsideration.
The narrower missing mechanism is a general explicit invalidation event that
reopens and compares an investigation's strategy alternatives. One-fire limits
must be separated from evidence-based invalidation when interpreting silence.

**G. First-class representation.** HASP has first-class PFs, selectors, anchors,
findings, phase instructions and intervention records. `Skill` also stores
`avoidance_strategies: List[str]`; reminder fallback takes the first string.
In this experiment the investigative strategies are independent PFs. I found
no explicit object for an intra-skill investigative strategy decision containing
alternatives, expected observations, a selection criterion and reconsideration
conditions. This narrower statement preserves HASP's existing representations.

## Source Locations

- `pf_select/pf_select_eval.py:76`: menu; `:123`: parser; `:172`: instruction;
  `:323`: model selection; `:445`: post-feedback revision.
- `src/skills_agent/skills/program_functions.py:156`: dispatcher; `:194`:
  execution order; `:252`: action mutation; `:265`: injection accumulation.
- `skills/pf_template.py:640`: domain, fire-count and activation gates.
- `src/skills_agent/agent/skill_agent_runner.py:441`: episode-level PF selection.
- `src/skills_agent/skills/selector.py:32`: mode/keyword selection;
  `:73`: contextual reminders; `:125`: phase instruction priorities.
- `src/skills_agent/skills/pf_selector.py:88`: older top-k model selector.
- `src/skills_agent/skills/skill.py:68`: Skill data model.
- `src/skills_agent/skills/prompts.py:163`: reminder selection and fallback.
- `skills/executable/web/skills.py:726`: existing repeated-search correction.
- `pf_select/step_dispatch.py:1`: optional consent channel and its limits.

## Research Implication

The original two-PF experiment cannot support a behavioral research gap. Native
independent PFs with suitable prerequisites can reproduce an evolving strategy
sequence, and a model can select multiple useful approaches. A defensible
remaining question is whether an explicit intra-skill decision representation
improves effectiveness, cost or reliability over this stronger native baseline.
Absence of a dedicated representation alone does not establish a behavioral
advantage. That advantage requires comparative outcome experiments.

Dependency provenance and backend details are in `strategy_dependency_audit.md`.
