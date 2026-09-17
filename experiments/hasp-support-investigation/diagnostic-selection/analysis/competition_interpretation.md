Arm labels A/B/C/D mean base / native HASP / all eligible / neutral revision. Diagnostic action IDs A–F mean request trace / matched-client comparison / exception logs / request comparison / dependency health / isolation replay.

## Main finding

Native HASP did not reliably choose high-value next actions in these forced-competition states. It produced more evaluator-optimal actions than base or neutral revision—11/100 versus 1/100 and 0/100—but did not improve mean diagnostic score over either control. Native B improved the shared base on 10 trials, degraded it on 37, and produced zero-information actions on 79. All-eligible C did not solve the problem either.

There is a real positive result: all ten B improvements reached an optimum, all occurred in CLEAR_SUPPORT snapshots, and neutral revision produced no optimum. In S06 specifically, B reached the optimum on 6/10 trials versus 0/10 for both controls. This supports a localized benefit from native feedback. It does not satisfy the proposed falsification criterion of reliable high-value execution across genuine competition states with a clear advantage over both controls.

All 400 observations were valid; there were no parser failures, retries, repaired outputs or fallback actions. The fixed primary run used 100 shared base calls, 100 native selectors, 87 native-B revisions, 100 all-eligible-C revisions and 100 neutral-D revisions: 487 generations. One earlier load-only request generated no tokens and is logged separately. No reversal, sample expansion or new selector was run.

## Direct answers about native B

| Question | Observed result |
|---|---|
| Did it select genuinely eligible PFs? | At least one on 87/100 trials. It selected 105 of 240 eligible PF opportunities: 43.75% micro recall. |
| How many eligible PFs were omitted? | 135/240 opportunities, across 92/100 trials. All eligible PFs were selected on only 8 trials. |
| How many ineligible PFs were selected? | 28/133 selected IDs, across 27 trials. Selection precision was 78.95%. Thirteen trials selected only ineligible PFs and therefore received no feedback. |
| Did selected eligible PFs activate? | Yes: 105/105. Every selected ineligible PF was correctly gated out. No gate/dispatcher failure was observed. |
| One or several PFs? | One ID on 67 trials; two IDs on 33; never three. Only 18 trials selected and activated two genuinely eligible PFs. |
| Did executed actions improve or degrade the shared base? | Improved 10%, degraded 37%, tied in score 53%. Actions changed on 70%; 23% changed action without changing score. |
| How did B compare with neutral D? | Optimal: 11% versus 0%; mean score: 0.1440 versus 0.1457; top-2: 11% versus 32%; cost: 2.91 versus 3.99. Paired B–D score wins/losses/ties: 11/39/50. D itself improved the base on 3% and degraded it on 2%. |
| How did B compare with all-eligible C? | C had higher mean score (0.1587 versus 0.1440) and top-2 rate (26% versus 11%), but lower optimal rate (9% versus 11%) and higher cost (3.44 versus 2.91). Paired C–B score wins/losses/ties: 27/9/64. C does not uniformly dominate B. |
| Did quality change with eligible count? | B optimal rate was 3/60 (5%) with two eligible PFs and 8/40 (20%) with three; mean scores were 0.0933 and 0.2200. Six of the eight three-eligible optima came from S06. These are different evidence states, not randomized PF-count treatments. |
| Was performance better with clear bundle support? | B reached 10/50 optima (20%) in CLEAR_SUPPORT, 0/30 in AMBIGUOUS_SUPPORT, and 1/20 (5%) in NO_CLEAR_SUPPORT. The last was an already-optimal base preserved without feedback, not a feedback improvement. Clear-support B still degraded 36/50 bases and had a lower mean score than its base and neutral controls. |

The 13 no-feedback B trials are separately reported below: B simply preserved their shared base. Among the 87 feedback trials, B reached 10 optima, improved 10 bases and degraded 37; its mean score was 0.1464 versus 0.1598 for matched neutral D. The one optimum outside CLEAR_SUPPORT came from S03-t03, where native selection chose an ineligible comparison PF and the gate prevented a revision. That preservation must not be credited to successful intervention guidance.

The exact-action optimum improvement is distinct from the mean-score result. A few large gains coexist with many smaller losses. The descriptive snapshot-cluster interval for B–D optimal-rate difference is +1 to +24 percentage points; the mean-score interval spans −0.1213 to +0.1220. Ten structurally related snapshots do not support broad significance or reliability claims.

## Interpreting where weakness appears

| Stage | Evidence | What this supports—and its limit |
|---|---|---|
| PF selection | Recall 43.75%; 135 eligible omissions; 28 false-gate selections. Binary isolation was never selected despite 30 eligible opportunities; comparison was selected on 10/30 eligible opportunities. | Selection was incomplete and sometimes inconsistent with prerequisites. Eligibility is not utility; these counts alone do not prove the omitted PF would improve an action. |
| Gate/activation | All 105 selected eligible PFs activated; all 28 selected ineligible IDs were filtered. | No observed activation defect. Gate eligibility correctly implemented the existing prerequisites, but it did not certify positive marginal diagnostic information. |
| Intervention content | The same frozen guidance was delivered verbatim. Some bundles combine request capture, tracing and comparison, with no instruction for comparing their information-per-cost value. | Content can point in different directions. This experiment did not randomize wording, so it cannot isolate a content defect or prove interference. |
| Policy execution after feedback | B changed C→A (exception inspection to tracing) on 43 trials. In S08 all-eligible C delivered explicit comparison guidance, yet executed tracing on all ten trials, scoring zero each time. | Clear support in an available or delivered bundle does not ensure execution of the evaluator-best action. Selection alone cannot explain the all-eligible failures. |
| PF-library coverage | In NO_CLEAR_SUPPORT, B made no improvement; C scored zero on all 20 trials. In AMBIGUOUS_SUPPORT, B scored zero on all 30; C gained information on 17 but reached no optimum. | The library lacks direct matched-client guidance in these evidence states under its unchanged gates. A selector over these PFs cannot be assumed sufficient to supply that missing representation. |
| Offline-objective mismatch | The evaluator rewards expected eliminations per cost in a uniform closed-world hypothesis set. The model is not given that set or its outcome table, and the prompts ask for a next diagnostic check. In S07, full feedback led to comprehensive replay F (cost 5, score 0.2), while the offline optimum was client comparison B (cost 1, score 1). | A reasonable comprehensive investigation direction can be suboptimal for this narrow evaluator. This does not establish that real-world tracing/replay is generally poor or that the model can infer the hidden objective perfectly. |

All-eligible C's modest aggregate gain over B was concentrated outside CLEAR_SUPPORT: mean-score C–B was −0.0187 in CLEAR_SUPPORT, +0.1133 in AMBIGUOUS_SUPPORT, and −0.0500 in NO_CLEAR_SUPPORT. The ambiguous group's gains came from 17 isolation replays. That is evidence that the all-eligible bundle can recover useful information omitted by native B, but not that a particular omitted PF is a uniquely correct selection or that the recovered action is optimal.

## Multiple guidance, cheap checks and order limits

With two genuinely eligible PFs activated in B (18 trials), there were 3 improvements, 8 degradations and 7 score ties; 14 final actions supplied zero information. The optimum rate was 3/18 (16.7%), versus 7/69 (10.1%) when one PF activated. These endogenous groups differ in evidence, selected guidance and base proposal, so this is neither proof that multiple guidance helps nor proof that it confuses the policy.

B reduced average action cost from 3.80 to 2.91, but much of the shift was from exception inspection (cost 4) to tracing (cost 3), not to the best cost-1 check. B executed 15 cost-1 comparisons: ten were newly optimal request comparisons, one preserved the base's optimal client comparison, and four request comparisons supplied no information in their states. It executed tracing 59 times, all zero-information under this evaluator. C executed 29 expensive isolation suites, including the 17 informative but suboptimal ambiguous-support cases. Lower action cost alone was not diagnostic success.

Intervention order and menu order were not tested. The observed S08 preference for tracing despite explicit comparison guidance is compatible with several explanations, including content priority and policy choice; it cannot establish an order effect. Those sensitivities remain unmeasured by instruction.

## Falsification interpretation

The broad falsification outcome—native HASP reliably choosing high-value actions and clearly exceeding both controls—was not observed. Native feedback did produce ten optimum-reaching improvements beyond anything neutral revision produced, so it would be wrong to call it ineffective. Those gains were localized, accompanied by frequent score degradation, and insufficient for a mean-score advantage.

Poor aggregate performance does not isolate a missing strategy selector as the cause. Selection omissions matter descriptively, gates work as implemented, full eligible feedback remains weak, the library's coverage is limited, and the closed-world value objective differs from much of the natural investigative guidance. These results can motivate further investigation of representation and post-feedback decision-making, but they establish neither the necessity or sufficiency of an additional selector nor novelty.
