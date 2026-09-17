# Primary competition stress-test results

Completed 10 snapshots × 10 seeds × A/B/C/D = 400 observations using 487 generation calls. No reversal conditions, additional samples or proposed selector were run.

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

## Per-snapshot executed-action results

Optimal and top-2 are rates of the executed action under the unchanged evaluator. Improvement/degradation compare its score with the shared base in the same snapshot. Mean score and cost use valid executions; rates use all planned observations. Exact-action best-strategy alignment equals the optimal rate, not PF selection.

### S01 — CLEAR_SUPPORT

Eligible: evidence_collection, dependency_trace. Offline best: B, D. Viable set: H1,H2,H3 (offline only).

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 10/10 | 0/10 (0.0%) | 0/10 | 0.333 | 4.000 | 0/10 | 0/10 | 0 |
| B | 10/10 | 3/10 (30.0%) | 3/10 | 0.500 | 2.400 | 3/10 | 4/10 | 0 |
| C | 10/10 | 1/10 (10.0%) | 1/10 | 0.247 | 3.300 | 3/10 | 6/10 | 0 |
| D | 10/10 | 0/10 (0.0%) | 0/10 | 0.333 | 4.000 | 0/10 | 0/10 | 0 |

### S02 — CLEAR_SUPPORT

Eligible: evidence_collection, comparison_experiment. Offline best: D. Viable set: H1,H2 (offline only).

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 10/10 | 0/10 (0.0%) | 10/10 | 0.250 | 4.000 | 0/10 | 0/10 | 0 |
| B | 10/10 | 0/10 (0.0%) | 0/10 | 0.060 | 3.600 | 0/10 | 10/10 | 0 |
| C | 10/10 | 1/10 (10.0%) | 1/10 | 0.240 | 4.200 | 1/10 | 9/10 | 0 |
| D | 10/10 | 0/10 (0.0%) | 10/10 | 0.250 | 4.000 | 0/10 | 0/10 | 0 |

### S03 — NO_CLEAR_SUPPORT

Eligible: evidence_collection, request_id_trace, dependency_trace. Offline best: B. Viable set: H1,H3 (offline only).

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 10/10 | 1/10 (10.0%) | 2/10 | 0.120 | 3.100 | 0/10 | 0/10 | 0 |
| B | 10/10 | 1/10 (10.0%) | 1/10 | 0.100 | 2.400 | 0/10 | 1/10 | 1 |
| C | 10/10 | 0/10 (0.0%) | 0/10 | 0.000 | 3.000 | 0/10 | 2/10 | 1 |
| D | 10/10 | 0/10 (0.0%) | 1/10 | 0.020 | 3.900 | 1/10 | 2/10 | 5 |

### S04 — AMBIGUOUS_SUPPORT

Eligible: request_id_trace, dependency_trace, binary_isolation. Offline best: B. Viable set: H1,H3 (offline only).

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 10/10 | 0/10 (0.0%) | 0/10 | 0.000 | 4.000 | 0/10 | 0/10 | 0 |
| B | 10/10 | 0/10 (0.0%) | 0/10 | 0.000 | 3.100 | 0/10 | 0/10 | 9 |
| C | 10/10 | 0/10 (0.0%) | 2/10 | 0.040 | 3.700 | 2/10 | 0/10 | 5 |
| D | 10/10 | 0/10 (0.0%) | 0/10 | 0.000 | 3.900 | 0/10 | 0/10 | 1 |

### S05 — CLEAR_SUPPORT

Eligible: evidence_collection, request_id_trace. Offline best: B, D. Viable set: H1,H2,H3 (offline only).

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 10/10 | 0/10 (0.0%) | 0/10 | 0.300 | 3.900 | 0/10 | 0/10 | 0 |
| B | 10/10 | 0/10 (0.0%) | 0/10 | 0.000 | 3.000 | 0/10 | 9/10 | 0 |
| C | 10/10 | 0/10 (0.0%) | 0/10 | 0.000 | 3.000 | 0/10 | 9/10 | 0 |
| D | 10/10 | 0/10 (0.0%) | 0/10 | 0.333 | 4.000 | 1/10 | 0/10 | 0 |

### S06 — CLEAR_SUPPORT

Eligible: evidence_collection, comparison_experiment, dependency_trace. Offline best: D. Viable set: H1,H2 (offline only).

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 10/10 | 0/10 (0.0%) | 10/10 | 0.250 | 4.000 | 0/10 | 0/10 | 0 |
| B | 10/10 | 6/10 (60.0%) | 6/10 | 0.680 | 2.600 | 6/10 | 4/10 | 0 |
| C | 10/10 | 7/10 (70.0%) | 7/10 | 0.760 | 2.200 | 7/10 | 3/10 | 0 |
| D | 10/10 | 0/10 (0.0%) | 10/10 | 0.250 | 4.000 | 0/10 | 0/10 | 0 |

### S07 — AMBIGUOUS_SUPPORT

Eligible: dependency_trace, binary_isolation. Offline best: B. Viable set: H1,H3 (offline only).

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 10/10 | 0/10 (0.0%) | 0/10 | 0.000 | 4.000 | 0/10 | 0/10 | 0 |
| B | 10/10 | 0/10 (0.0%) | 0/10 | 0.000 | 3.400 | 0/10 | 0/10 | 3 |
| C | 10/10 | 0/10 (0.0%) | 10/10 | 0.200 | 5.000 | 10/10 | 0/10 | 0 |
| D | 10/10 | 0/10 (0.0%) | 0/10 | 0.000 | 4.000 | 0/10 | 0/10 | 0 |

### S08 — CLEAR_SUPPORT

Eligible: evidence_collection, request_id_trace, comparison_experiment. Offline best: D. Viable set: H1,H2 (offline only).

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 10/10 | 0/10 (0.0%) | 10/10 | 0.250 | 4.000 | 0/10 | 0/10 | 0 |
| B | 10/10 | 1/10 (10.0%) | 1/10 | 0.100 | 2.800 | 1/10 | 9/10 | 0 |
| C | 10/10 | 0/10 (0.0%) | 0/10 | 0.000 | 3.000 | 0/10 | 10/10 | 0 |
| D | 10/10 | 0/10 (0.0%) | 10/10 | 0.250 | 4.000 | 0/10 | 0/10 | 0 |

### S09 — NO_CLEAR_SUPPORT

Eligible: evidence_collection, request_id_trace. Offline best: B. Viable set: H1,H3 (offline only).

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 10/10 | 0/10 (0.0%) | 0/10 | 0.000 | 3.000 | 0/10 | 0/10 | 0 |
| B | 10/10 | 0/10 (0.0%) | 0/10 | 0.000 | 2.600 | 0/10 | 0/10 | 2 |
| C | 10/10 | 0/10 (0.0%) | 0/10 | 0.000 | 3.000 | 0/10 | 0/10 | 0 |
| D | 10/10 | 0/10 (0.0%) | 1/10 | 0.020 | 4.100 | 1/10 | 0/10 | 9 |

### S10 — AMBIGUOUS_SUPPORT

Eligible: request_id_trace, binary_isolation. Offline best: B. Viable set: H1,H3 (offline only).

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 10/10 | 0/10 (0.0%) | 0/10 | 0.000 | 4.000 | 0/10 | 0/10 | 0 |
| B | 10/10 | 0/10 (0.0%) | 0/10 | 0.000 | 3.200 | 0/10 | 0/10 | 8 |
| C | 10/10 | 0/10 (0.0%) | 5/10 | 0.100 | 4.000 | 5/10 | 0/10 | 5 |
| D | 10/10 | 0/10 (0.0%) | 0/10 | 0.000 | 4.000 | 0/10 | 0/10 | 0 |

## Overall primary comparison

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 100/100 | 1/100 (1.0%) | 32/100 | 0.150 | 3.800 | 0/100 | 0/100 | 0 |
| B | 100/100 | 11/100 (11.0%) | 11/100 | 0.144 | 2.910 | 10/100 | 37/100 | 23 |
| C | 100/100 | 9/100 (9.0%) | 26/100 | 0.159 | 3.440 | 28/100 | 39/100 | 11 |
| D | 100/100 | 0/100 (0.0%) | 32/100 | 0.146 | 3.990 | 3/100 | 2/100 | 15 |

Each snapshot has ten trials, so these all-attempt means weight snapshots equally. Valid-execution denominators and all action transitions are included in analysis/competition_summary.json. Invalid executions are not zero-cost or zero-score successes.

| Arm | Optimal / valid | Top-2 / valid | Zero-information actions | Repeated actions | Executed A–F counts |
|---|---:|---:|---:|---:|---|
| A | 1/100 | 32/100 | 49 | 1 | {"A": 18, "B": 1, "C": 80, "F": 1} |
| B | 11/100 | 11/100 | 79 | 1 | {"A": 59, "B": 1, "C": 13, "D": 14, "E": 6, "F": 7} |
| C | 9/100 | 26/100 | 61 | 6 | {"A": 58, "C": 4, "D": 9, "F": 29} |
| D | 0/100 | 32/100 | 48 | 16 | {"A": 3, "C": 95, "F": 2} |

| Arm | Equal-snapshot mean score | Equal-snapshot mean cost |
|---|---:|---:|
| A | 0.150 | 3.800 |
| B | 0.144 | 2.910 |
| C | 0.159 | 3.440 |
| D | 0.146 | 3.990 |

## Paired comparisons and uncertainty

Differences are left minus right within the same snapshot/seed. Win/loss/tie compares executed diagnostic score. Intervals are descriptive percentile 95% intervals from 10,000 resamples of the ten whole snapshot clusters (fixed analysis RNG 92716). These structurally related snapshots are not a random sample of diagnostic problems; intervals do not establish population generality or reliable significance.

| Pair | Valid pairs | Score wins / losses / ties | Mean score delta [cluster interval] | Optimal-rate delta [cluster interval] | Mean cost delta | Action disagreements |
|---|---:|---:|---|---|---:|---:|
| B-A | 100 | 10 / 37 / 53 | -0.006 [-0.117, 0.115] | 10.0% [0.0%, 23.0%] | -0.890 | 70 |
| C-A | 100 | 28 / 39 / 33 | 0.008 [-0.119, 0.152] | 8.0% [-1.0%, 23.0%] | -0.360 | 78 |
| D-A | 100 | 3 / 2 / 95 | -0.005 [-0.028, 0.012] | -1.0% [-3.0%, 0.0%] | 0.190 | 20 |
| B-D | 100 | 11 / 39 / 50 | -0.002 [-0.121, 0.122] | 11.0% [1.0%, 24.0%] | -1.080 | 84 |
| C-B | 100 | 27 / 9 / 64 | 0.015 [-0.069, 0.093] | -2.0% [-8.0%, 3.0%] | 0.530 | 47 |

## Coverage annotation strata

Frozen before inference: five CLEAR_SUPPORT snapshots (S01/S02/S05/S06/S08), three AMBIGUOUS_SUPPORT (S04/S07/S10), two NO_CLEAR_SUPPORT (S03/S09). These are subjective bundle-level interpretation annotations, not randomized groups or a best-PF oracle. They do not contribute to action scoring. Clear states all have D among their best actions; the other states have B as their sole optimum. Coverage is therefore entangled with evidence and optimal-action identity.

### AMBIGUOUS_SUPPORT

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 30/30 | 0/30 (0.0%) | 0/30 | 0.000 | 4.000 | 0/30 | 0/30 | 0 |
| B | 30/30 | 0/30 (0.0%) | 0/30 | 0.000 | 3.233 | 0/30 | 0/30 | 20 |
| C | 30/30 | 0/30 (0.0%) | 17/30 | 0.113 | 4.233 | 17/30 | 0/30 | 10 |
| D | 30/30 | 0/30 (0.0%) | 0/30 | 0.000 | 3.967 | 0/30 | 0/30 | 1 |

### CLEAR_SUPPORT

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 50/50 | 0/50 (0.0%) | 30/50 | 0.277 | 3.980 | 0/50 | 0/50 | 0 |
| B | 50/50 | 10/50 (20.0%) | 10/50 | 0.268 | 2.880 | 10/50 | 36/50 | 0 |
| C | 50/50 | 9/50 (18.0%) | 9/50 | 0.249 | 3.140 | 11/50 | 37/50 | 0 |
| D | 50/50 | 0/50 (0.0%) | 30/50 | 0.283 | 4.000 | 1/50 | 0/50 | 0 |

### NO_CLEAR_SUPPORT

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 20/20 | 1/20 (5.0%) | 2/20 | 0.060 | 3.050 | 0/20 | 0/20 | 0 |
| B | 20/20 | 1/20 (5.0%) | 1/20 | 0.050 | 2.500 | 0/20 | 1/20 | 3 |
| C | 20/20 | 0/20 (0.0%) | 0/20 | 0.000 | 3.000 | 0/20 | 2/20 | 1 |
| D | 20/20 | 0/20 (0.0%) | 2/20 | 0.020 | 4.000 | 2/20 | 2/20 | 14 |

## Native B: selection → activation → feedback → revision → execution → value

Selector trials: 100. At least one eligible PF selected: 87; all eligible selected: 8. Eligible selections: 105/240; omitted eligible PF opportunities: 135 across 92 trials. Ineligible selections: 28/133 across 27 trials.

Eligible recall: micro 43.8%, macro 44.5%. Selection precision: micro 78.9%, macro over nonempty selections 80.0%. Empty selections: 0; nonempty text yielding no parsed IDs: 0. Empty-set precision remains undefined.

Selected eligible PF activations: 105/105 (100.0%). Trials selecting multiple IDs: 33; selecting multiple genuinely eligible IDs: 18; actually activating multiple PFs: 18. Feedback-triggered policy revisions: 87. These quantities are separate from executed-action success.

| PF | Eligible opportunities | Selected | Eligible selected | Eligible omitted | Ineligible selected | Activated |
|---|---:|---:|---:|---:|---:|---:|
| evidence_collection | 70 | 63 | 49 | 21 | 14 | 49 |
| request_id_trace | 60 | 51 | 38 | 22 | 13 | 38 |
| comparison_experiment | 30 | 11 | 10 | 20 | 1 | 10 |
| dependency_trace | 50 | 8 | 8 | 42 | 0 | 8 |
| binary_isolation | 30 | 0 | 0 | 30 | 0 | 0 |

Exact native feedback strings/order, raw selector responses, revision texts and executed actions are preserved separately in results/competition_primary/observations.jsonl; request/response payloads and token counts are in requests.jsonl and calls.jsonl. Native PF record previews truncate long context_text fields; the separate interventions array preserves full text.

### B action quality by eligible_selected

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 13/13 | 1/13 (7.7%) | 1/13 | 0.128 | 3.769 | 0/13 | 0/13 | 0 |
| 1 | 69/69 | 7/69 (10.1%) | 7/69 | 0.133 | 2.812 | 7/69 | 29/69 | 23 |
| 2 | 18/18 | 3/18 (16.7%) | 3/18 | 0.196 | 2.667 | 3/18 | 8/18 | 0 |

### B action quality by activated

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 13/13 | 1/13 (7.7%) | 1/13 | 0.128 | 3.769 | 0/13 | 0/13 | 0 |
| 1 | 69/69 | 7/69 (10.1%) | 7/69 | 0.133 | 2.812 | 7/69 | 29/69 | 23 |
| 2 | 18/18 | 3/18 (16.7%) | 3/18 | 0.196 | 2.667 | 3/18 | 8/18 | 0 |

### B action quality by number_selected

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 67/67 | 7/67 (10.4%) | 7/67 | 0.138 | 2.881 | 6/67 | 24/67 | 15 |
| 2 | 33/33 | 4/33 (12.1%) | 4/33 | 0.156 | 2.970 | 4/33 | 13/33 | 8 |

### B action quality by has_ineligible_selection

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| False | 73/73 | 9/73 (12.3%) | 9/73 | 0.153 | 2.685 | 9/73 | 32/73 | 15 |
| True | 27/27 | 2/27 (7.4%) | 2/27 | 0.121 | 3.519 | 1/27 | 5/27 | 8 |

### Trials where B did or did not produce feedback

D always has a neutral extra generation; B only revises when feedback exists. These selected subsets are descriptive, not randomized subgroups.

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B_no_feedback/A | 13/13 | 1/13 (7.7%) | 1/13 | 0.128 | 3.769 | 0/13 | 0/13 | 0 |
| B_no_feedback/B | 13/13 | 1/13 (7.7%) | 1/13 | 0.128 | 3.769 | 0/13 | 0/13 | 0 |
| B_no_feedback/C | 13/13 | 0/13 (0.0%) | 8/13 | 0.123 | 4.231 | 8/13 | 3/13 | 2 |
| B_no_feedback/D | 13/13 | 0/13 (0.0%) | 0/13 | 0.051 | 4.000 | 0/13 | 1/13 | 0 |

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B_feedback/A | 87/87 | 0/87 (0.0%) | 31/87 | 0.154 | 3.805 | 0/87 | 0/87 | 0 |
| B_feedback/B | 87/87 | 10/87 (11.5%) | 10/87 | 0.146 | 2.782 | 10/87 | 37/87 | 23 |
| B_feedback/C | 87/87 | 9/87 (10.3%) | 18/87 | 0.164 | 3.322 | 20/87 | 36/87 | 9 |
| B_feedback/D | 87/87 | 0/87 (0.0%) | 32/87 | 0.160 | 3.989 | 3/87 | 1/87 | 15 |

## Two versus three eligible PFs

Eligible count is fixed by each snapshot; differences cannot identify a causal effect of more PFs.

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 eligible / A | 60/60 | 0/60 (0.0%) | 10/60 | 0.147 | 3.817 | 0/60 | 0/60 | 0 |
| 2 eligible / B | 60/60 | 3/60 (5.0%) | 3/60 | 0.093 | 3.033 | 3/60 | 23/60 | 13 |
| 2 eligible / C | 60/60 | 2/60 (3.3%) | 17/60 | 0.131 | 3.750 | 19/60 | 24/60 | 5 |
| 2 eligible / D | 60/60 | 0/60 (0.0%) | 11/60 | 0.156 | 4.017 | 2/60 | 0/60 | 9 |

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 3 eligible / A | 40/40 | 1/40 (2.5%) | 22/40 | 0.155 | 3.775 | 0/40 | 0/40 | 0 |
| 3 eligible / B | 40/40 | 8/40 (20.0%) | 8/40 | 0.220 | 2.725 | 7/40 | 14/40 | 10 |
| 3 eligible / C | 40/40 | 7/40 (17.5%) | 9/40 | 0.200 | 2.975 | 9/40 | 15/40 | 6 |
| 3 eligible / D | 40/40 | 0/40 (0.0%) | 21/40 | 0.130 | 3.950 | 1/40 | 2/40 | 6 |

## Viable-world-set strata (offline only)

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| H1,H2 / A | 30/30 | 0/30 (0.0%) | 30/30 | 0.250 | 4.000 | 0/30 | 0/30 | 0 |
| H1,H2 / B | 30/30 | 7/30 (23.3%) | 7/30 | 0.280 | 3.000 | 7/30 | 23/30 | 0 |
| H1,H2 / C | 30/30 | 8/30 (26.7%) | 8/30 | 0.333 | 3.133 | 8/30 | 22/30 | 0 |
| H1,H2 / D | 30/30 | 0/30 (0.0%) | 30/30 | 0.250 | 4.000 | 0/30 | 0/30 | 0 |

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| H1,H2,H3 / A | 20/20 | 0/20 (0.0%) | 0/20 | 0.317 | 3.950 | 0/20 | 0/20 | 0 |
| H1,H2,H3 / B | 20/20 | 3/20 (15.0%) | 3/20 | 0.250 | 2.700 | 3/20 | 13/20 | 0 |
| H1,H2,H3 / C | 20/20 | 1/20 (5.0%) | 1/20 | 0.123 | 3.150 | 3/20 | 15/20 | 0 |
| H1,H2,H3 / D | 20/20 | 0/20 (0.0%) | 0/20 | 0.333 | 4.000 | 1/20 | 0/20 | 0 |

| Group / arm | Valid / planned | Optimal | Top-2 | Mean score | Mean cost | Improve | Degrade | Same score, changed action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| H1,H3 / A | 50/50 | 1/50 (2.0%) | 2/50 | 0.024 | 3.620 | 0/50 | 0/50 | 0 |
| H1,H3 / B | 50/50 | 1/50 (2.0%) | 1/50 | 0.020 | 2.940 | 0/50 | 1/50 | 23 |
| H1,H3 / C | 50/50 | 0/50 (0.0%) | 17/50 | 0.068 | 3.740 | 17/50 | 2/50 | 11 |
| H1,H3 / D | 50/50 | 0/50 (0.0%) | 2/50 | 0.008 | 3.980 | 2/50 | 2/50 | 15 |

## Action transitions and diagnostic directions

B and D actions each cost 1; C exception inspection costs 4, E dependency health costs 2, A tracing costs 3, and F isolation costs 5. Direction names alone do not imply value: B and D are both comparisons but frequently have different scores.

| Arm | Shared-base → executed-action counts | Direction counts |
|---|---|---|
| A | {"A->A": 18, "B->B": 1, "C->C": 80, "F->F": 1} | {"comparison": 1, "exception inspection": 80, "isolation": 1, "tracing": 18} |
| B | {"A->A": 16, "A->D": 2, "B->B": 1, "C->A": 43, "C->C": 13, "C->D": 11, "C->E": 6, "C->F": 7, "F->D": 1} | {"comparison": 15, "dependencies": 6, "exception inspection": 13, "isolation": 7, "tracing": 59} |
| C | {"A->A": 18, "B->A": 1, "C->A": 38, "C->C": 4, "C->D": 9, "C->F": 29, "F->A": 1} | {"comparison": 9, "exception inspection": 4, "isolation": 29, "tracing": 58} |
| D | {"A->A": 2, "A->C": 15, "A->F": 1, "B->C": 1, "C->A": 1, "C->C": 78, "C->F": 1, "F->C": 1} | {"exception inspection": 95, "isolation": 2, "tracing": 3} |

## Scope and integrity

The unchanged gates allow competing guidance but do not guarantee marginal information. No unique correct PF is identifiable from these broad interventions. Useful-omission claims cannot be inferred just from eligibility; C-minus-B measures a bundle contrast, not individual-PF utility. Selection associations and annotation strata are not causal mediation estimates.

Unresolved comparison-plus-isolation competition is unavailable in this oracle. The ten snapshots cover only three viable-world sets. B_reverse and C_reverse were not run, so menu-order and intervention-order sensitivity remain unmeasured. No sample expansion or new selector was implemented. Neither good nor poor performance establishes novelty.


## Selection-stage results by frozen coverage category

Categories describe the entire eligible bundle, not whichever subset native B happened to select. These are descriptive strata; eligibility and support are different variables.

| Category | Trials | At least one eligible selected | Eligible selected / available | Eligible omitted | Ineligible selected / all selected | Eligible activated / selected |
|---|---:|---:|---:|---:|---:|---:|
| CLEAR_SUPPORT | 50 | 48 | 59/120 | 61 | 8/67 | 59/59 |
| AMBIGUOUS_SUPPORT | 30 | 20 | 20/70 | 50 | 19/39 | 20/20 |
| NO_CLEAR_SUPPORT | 20 | 19 | 26/50 | 24 | 1/27 | 26/26 |

## Reproducibility and audit

All six offline runner/analysis contract tests passed. The completed-data audit independently verified all 400 records, shared proposals, exact prompts and sampling, all five gates, actual full interventions, fire counts, and recomputed scores. Every frozen source and coverage-annotation hash still matches. All 487 generations ended with `stop`; no context truncation or token-cap stop was observed. Actual inputs ranged from 347 to 897 tokens, and the largest input-plus-output was 907 against the unchanged 4096-token context.

The annotation was frozen at 2026-09-16T08:16:03.663680+00:00; the primary manifest started at 2026-09-16T08:21:18.634528+00:00 and completed at 2026-09-16T12:58:51.070459+00:00. The recorded generation-call durations sum to 59.62 minutes; that is not the calendar elapsed span and is not a latency benchmark.

The dedicated experiment server was shut down after completion. The pre-existing Ollama service was left untouched. No further generation or sensitivity run was started.

Annotation SHA-256 values:

- `PF_ACTION_COVERAGE.md`: `4cb4fbef84deda5da9261354caab40103bb5c450c0d41e23cd15e0ebc17e5eee`
- `pf_action_coverage.json`: `71f7cba488d350df5612f742692368f80fa855cad13e0f6505bce70f03b27bf0`

Input-length checks used the loaded model tokenizer and a text-only rendering checked against [Ollama 0.31.2 Gemma4Renderer](https://raw.githubusercontent.com/ollama/ollama/v0.31.2/model/renderers/gemma4.go); actual runtime prompt-token counts matched the pre-call checks. This check did not change the prompts.

Artifacts:

- [Frozen coverage annotation](analysis/PF_ACTION_COVERAGE.md) and [machine-readable annotation](analysis/pf_action_coverage.json).
- [Fixed snapshot matrix](competition_checkpoint/MATRIX.md) and [approved protocol](competition_checkpoint/PROTOCOL.md).
- [Complete metric summaries](analysis/competition_summary.json) and [400-observation CSV](analysis/competition_observations.csv).
- [Representative complete stage records](analysis/competition_examples.md) and [their JSON records](analysis/competition_examples.json).
- [Integrity audit](analysis/competition_integrity.json) and [completion manifest](results/competition_primary/completion.json).
- [Raw observations](results/competition_primary/observations.jsonl), [requests](results/competition_primary/requests.jsonl), and [responses](results/competition_primary/calls.jsonl).

