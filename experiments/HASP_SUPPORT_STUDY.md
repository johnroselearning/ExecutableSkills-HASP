# Can native HASP reproduce evidence-driven investigative adaptation?

## Assessment

The earlier E2 result was confounded by a missing comparison PF and must not be
used as evidence for a research gap. With five independent native PFs, HASP can
represent overlapping investigative directions, activate comparison after new
evidence, and produce a collection-to-tracing-to-comparison-to-isolation sequence
without a new selection mechanism. The broad behavioral gap is substantially
undermined by this experiment.

The narrower question remains unmeasured: whether a model using HASP's normal
selection prompt reliably chooses the experiment that best distinguishes live
hypotheses, and whether a first-class intra-skill selector improves that behavior.
Absence of an explicit objective in the dispatcher does not show that an LLM
cannot reason about diagnostic value. No actual model-selection trials ran.

## Implementation and experimental scope

Upstream commit: `2a0e859ef320719d0794fe2ccda5c672a28cc0fb`.
Five authored PFs live in `skills/executable/support/skills.py`, with normal
`@pf_skill`, step anchors, `should_activate`, `intervene`, and `inject`. Each has
its own card with equal priority. The upstream selector and dispatcher are
unchanged. No research algorithm, scoring, information gain or PF ranking was added.

Each PF reads fixture observations through the existing `Ctx.raw` escape hatch.
The facts are explicit synthetic observations, not results inferred by an LLM
or extracted from its proposed action. Prerequisite checks are deliberately
independent and overlapping; no PF suppresses a competitor. These domain rules
are authored experimental content, not previously shipped HASP support skills.

The menu always contains all five PFs. Controls cover all 32 subsets at every
state, plus reversed all-PF and reversed request/comparison order. Two further
fixed base proposals at E2 test proposal leakage into activation. Two trajectories
retain an initial selection and preserve its fire counts. Total: **284 support
dispatch traces**, plus one upstream `iterative_refinement` control.

The base proposal for the main matrix is: "Investigate the checkout HTTP 500
and determine the next diagnostic action." Alternate proposals favor tracing
or comparison. These are fixture proposals, not model-generated behavior.
Selections are forced controls, never asserted to be what HASP's LLM would choose.

Every trace records full cumulative evidence, current facts, proposal, full
menu, native selection messages, selected tags, activation records, fire counts,
complete intervention text and final dispatch action. Rationale is null because
there is no model response; the native prompt asks for tags only. PF records
truncate context text, so full injections are also saved separately.

## Evidence and activation

States are cumulative. Blank facts mean unknown. E3's concrete header values
are added synthetic detail, and E5 is an extra falsification control.

| State | New observation | PFs activating when all five are selected with fresh fire counts |
| --- | --- | --- |
| E0 | Checkout HTTP 500; little evidence | evidence_collection |
| E1 | POST /api/checkout -> 500; request-id abc123 | evidence_collection, request_id_trace, dependency_trace |
| E2 | Web consistently fails, mobile succeeds; same account and operation | evidence_collection, request_id_trace, comparison_experiment, dependency_trace |
| E3 | Requests captured; Content-Type and X-Checkout-Version differ | request_id_trace, comparison_experiment, dependency_trace, binary_isolation |
| E4 | Failure immediately follows frontend deployment; backend version unchanged | request_id_trace, comparison_experiment, dependency_trace, binary_isolation |
| E5 | Available abc123 logs exhausted; correlated downstream calls verified successful | comparison_experiment, binary_isolation |

Collection remains applicable at E1/E2 because request headers/body have not yet
been captured. E4 does not logically invalidate tracing: frontend input changes
can expose backend or dependency failures without a backend deployment. Temporal
correlation is not proof of frontend causation. The test therefore keeps those
alternatives alive. E5 explicitly removes the utility of repeating the available
trace and verifies downstream success; it still does not establish a root cause.

At E2, forcing request tracing alone fires that PF alone; forcing comparison
alone fires comparison; selecting both fires both. Reversing their tag order
reverses injection order. No internal tie-break, winner, or merge is produced.
All five support PFs inject context, so every deterministic dispatch final action
is the original proposal. A subsequent policy response would be required to show
which investigation is actually undertaken; no such response is fabricated here.

## Strong counterexamples to the gap

With **all five selected once at episode start**, native gates and default fire
limits produce this observed sequence:

| State | Newly firing PFs |
| --- | --- |
| E0 | evidence_collection |
| E1 | request_id_trace, dependency_trace |
| E2 | comparison_experiment |
| E3 | binary_isolation |
| E4/E5 | none; previously eligible PFs already exhausted their fire budgets |

This is already evidence-dependent adaptation of injected investigative guidance.
It requires no reselection and no intra-skill strategy abstraction. It does not
prove the policy follows the guidance or that its sequence is optimal.

With only request tracing selected at the start, the new comparison evidence
does not insert comparison into the active list. Its later silence can also
be caused by the fire cap. Fresh-state E5 probes isolate evidence invalidation
from this cap: request and dependency tracing decline, while comparison and
binary isolation still fire if selected. These decline rules were authored in
the individual PFs; the dispatcher does not infer them.

An **unchanged upstream PF** supplies another counterexample:
`iterative_refinement`, given two repeated searches for "checkout payment error",
redirects the next SEARCH to the original question, "Why does web checkout fail
while mobile succeeds?" This is a recorded MODIFY_ACTION, not just advice.
Its trigger is repetition, not a generic proof that a hypothesis was invalidated.

## Answers A-G

| Question | Finding |
| --- | --- |
| A. How does it decide between plausible request tracing and comparison? | The stock evaluation prompt asks the LLM to emit any number of most-relevant PF IDs from descriptions and the candidate answer. It need not choose between them. The parser preserves unique valid tags in model-output order; dispatch checks only those PFs. In controls, either or both work. Actual selection preferences are unmeasured. |
| B. Is it merely semantic matching? | Description-based relevance is the explicit prompt criterion. It is not a deterministic semantic matcher, and its prompt gives the LLM the problem and candidate answer. The model may reason about context and diagnostic usefulness. "Merely matching descriptions" is not established. |
| C. Does it reason about greatest discriminating evidence? | There is no explicit discriminating-evidence objective, hypothesis comparison or expected-information calculation in this PF selection/dispatch path. An LLM may do this implicitly. No model trials or rationale observations support either an affirmative or a categorical negative behavioral claim. |
| D. Multiple strategy PFs simultaneously? | Yes. The prompt permits any number, the parser retains multiple IDs, and overlapping PFs fired together in E2-E4. |
| E. Ranking or sequential execution? | Dispatch follows the supplied ID order with no dispatcher ranking or arbitration. Earlier MODIFY_ACTION results become the action seen by later gates; injections accumulate in order. The model may express precedence by output order. Other HASP components do contain top-K selection and relevance/phase-priority ordering; a repository-wide "no ranking" claim would be false. |
| F. Explicit reconsideration after invalidation? | No generic invalidation event updates the PF list in the examined runners. PFs are checked each step and can decline or redirect according to their own logic; the base policy can react to new observations. Retained-all controls show adaptation without reselection. Existing repetition/stall PFs can redirect an unproductive search. Evidence-triggered changes are supported, but a generic hypothesis-invalidation/reselection controller was not found. |
| G. First-class strategy selection? | This experiment represents strategies as independent PFs and selection as lists of PF IDs. HASP already has first-class Skill/PF objects, a PFSelector, textual `avoidance_strategies`, and conditional PhaseInstruction objects. No typed intra-skill investigative strategy set with comparative evidence-based selection state was found in the inspected runtime. Merely renaming PFs as strategies would not establish a substantive research contribution. |

## Source map and qualifications

- `pf_select/pf_select_eval.py:76`: menu uses card summaries, sorted by ID, clipped to 140 characters.
- `pf_select/pf_select_eval.py:123`: parses/deduplicates valid tags in output order.
- `pf_select/pf_select_eval.py:173`: prompt permits any number and asks for most-relevant PFs, with tags only.
- `pf_select/pf_select_eval.py:324`: model selection sees problem, candidate answer and menu; thinking is disabled in the chat template.
- `src/skills_agent/skills/program_functions.py:194`: sequential dispatch, gates and interventions; no arbitration.
- `skills/pf_template.py:599`: native fire budget defaults to one; both injections and rewrites count.
- `src/skills_agent/agent/skill_agent_runner.py:442`: PFSelector is called at episode start; async initialization also selects at episode start near line 1268.
- `src/skills_agent/agent/skill_agent_runner.py:666`: PF dispatch runs each step; injections feed subsequent observations/revision.
- `src/skills_agent/skills/pf_selector.py:67`: separate helper-based top-K selector with web-specific mandatory PFs, heuristic fallback and truncation; not the five-PF evaluation-menu path.
- `src/skills_agent/skills/selector.py:32`: mode/trigger relevance selection; `select_for_step` checks observation conditions; `select_for_phase` sorts by `priority_boost` (despite a broader docstring).
- `src/skills_agent/skills/skill.py:20`: PhaseInstruction; line 68: Skill, including string avoidance strategies and phase instructions.
- `src/skills_agent/skills/prompts.py:164`: reminder selection uses a fixed skill-ID map/first avoidance strategy, despite its comment suggesting context-based strategy choice.
- `skills/executable/web/skills.py:726`: registered template wrapper for iterative refinement; `implementations.py:1696` provides its current conditional query redirects.
- `pf_select/step_dispatch.py`: optional anchor/model-consent gating on already selected PFs; does not compare rival investigative strategies.

The five-PF menu is intentionally domain-restricted. Broad-library selection
dilution, alternative menu phrasings/order, model scale and fine-tuning could
affect behavior. Step dispatch uses a synthetic INVESTIGATE action and explicit
support context; the untouched stock evaluator normally dispatches a FINAL
answer. The optional model harness reuses the native selection prompt but
adapts the surrounding task to next-action investigation. It does not establish
automatic per-state reselection in a native episode.

## Validation and unresolved measurement

All **84 tests pass**, including eight new experimental-validity tests. All 77
registered skill anchors agree with cards. The optional model branch is tested
with a test double for prompt preservation, repeated seeds and feedback recording;
that test is not model evidence. Runtime/package limitations are documented in
[the dependency audit](DEPENDENCY_AUDIT.md); versions are unchanged.

The fair conclusion is that HASP already supplies enough machinery to reproduce
much of the proposed observable adaptation. A narrower research claim needs
model-driven comparison against this five-PF baseline, with externally defined
hypotheses, test outcomes and diagnostic cost. No performance advantage, reliable
optimal selection, or novelty claim is established by these dispatch controls.
