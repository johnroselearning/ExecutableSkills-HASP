# Pilot 1b tables — generated from preserved traces

Pooled executed-action denominators; mean episode rates also appear in CSV/JSON.

| World | Arm | Valid actions / decisions | First executed | Optimal | Top-2 | Isolation | Mean cost spent | Mean steps | Zero-info | Repeats |
|---|---|---|---|---|---|---|---:|---:|---|---|
| H1 | A | 16/16 | A:1, C:4 | 0/16 (0.0%) | 5/16 (31.2%) | 5/5 | 12.60 | 3.20 | 5 | 1 |
| H1 | B | 18/19 | A:5 | 0/18 (0.0%) | 4/18 (22.2%) | 4/5 | 12.80 | 3.60 | 4 | 2 |
| H1 | C | 25/25 | A:5 | 1/25 (4.0%) | 5/25 (20.0%) | 5/5 | 14.80 | 5.00 | 10 | 2 |
| H1 | B_reverse | 17/18 | A:5 | 0/17 (0.0%) | 4/17 (23.5%) | 4/5 | 12.20 | 3.40 | 3 | 1 |
| H2 | A | 6/6 | A:1, C:4 | 0/6 (0.0%) | 0/6 (0.0%) | 5/5 | 4.60 | 1.20 | 0 | 0 |
| H2 | B | 13/13 | A:5 | 0/13 (0.0%) | 0/13 (0.0%) | 5/5 | 8.40 | 2.60 | 3 | 1 |
| H2 | C | 15/15 | A:5 | 0/15 (0.0%) | 0/15 (0.0%) | 5/5 | 9.20 | 3.00 | 5 | 1 |
| H2 | B_reverse | 11/11 | A:5 | 0/11 (0.0%) | 0/11 (0.0%) | 5/5 | 7.60 | 2.20 | 1 | 1 |
| H3 | A | 16/16 | A:1, C:4 | 0/16 (0.0%) | 5/16 (31.2%) | 5/5 | 12.60 | 3.20 | 5 | 1 |
| H3 | B | 19/20 | A:5 | 1/19 (5.3%) | 4/19 (21.1%) | 4/5 | 12.20 | 3.80 | 5 | 1 |
| H3 | C | 24/24 | A:5 | 2/24 (8.3%) | 5/24 (20.8%) | 5/5 | 13.40 | 4.80 | 9 | 1 |
| H3 | B_reverse | 16/17 | A:5 | 0/16 (0.0%) | 4/16 (25.0%) | 4/5 | 12.00 | 3.20 | 2 | 1 |
| H4 | A | 5/5 | A:1, C:4 | 0/5 (0.0%) | 0/5 (0.0%) | 5/5 | 3.80 | 1.00 | 0 | 0 |
| H4 | B | 5/5 | A:5 | 0/5 (0.0%) | 0/5 (0.0%) | 5/5 | 3.00 | 1.00 | 0 | 0 |
| H4 | C | 5/5 | A:5 | 0/5 (0.0%) | 0/5 (0.0%) | 5/5 | 3.00 | 1.00 | 0 | 0 |
| H4 | B_reverse | 5/5 | A:5 | 0/5 (0.0%) | 0/5 (0.0%) | 5/5 | 3.00 | 1.00 | 0 | 0 |
| ALL | A | 43/43 | A:4, C:16 | 0/43 (0.0%) | 10/43 (23.3%) | 20/20 | 8.40 | 2.15 | 10 | 2 |
| ALL | B | 55/57 | A:20 | 1/55 (1.8%) | 8/55 (14.5%) | 18/20 | 9.10 | 2.75 | 12 | 4 |
| ALL | C | 69/69 | A:20 | 3/69 (4.3%) | 10/69 (14.5%) | 20/20 | 10.10 | 3.45 | 24 | 4 |
| ALL | B_reverse | 49/51 | A:20 | 0/49 (0.0%) | 8/49 (16.3%) | 18/20 | 8.70 | 2.45 | 6 | 3 |

## Proposal → executed action (descriptive association)

| World | Arm | Actions | Changed | Improved score | Equal score | Worse score | Transitions |
|---|---|---:|---:|---:|---:|---:|---|
| H1 | A | 16 | 0 | 0 | 16 | 0 | A→A:6, C→C:5, F→F:5 |
| H1 | B | 18 | 7 | 0 | 11 | 7 | A→A:1, C→A:5, C→C:5, C→E:1, D→D:1, F→A:1, F→F:4 |
| H1 | C | 25 | 11 | 1 | 14 | 10 | A→A:1, C→A:5, C→C:5, C→E:4, D→D:4, F→A:1, F→B:1, F→F:4 |
| H1 | B_reverse | 17 | 7 | 0 | 11 | 6 | A→A:1, C→A:5, C→C:5, E→D:1, F→E:1, F→F:4 |
| H2 | A | 6 | 0 | 0 | 6 | 0 | A→A:1, C→C:5 |
| H2 | B | 13 | 7 | 0 | 6 | 7 | A→A:1, C→A:5, C→C:5, C→E:2 |
| H2 | C | 15 | 9 | 0 | 6 | 9 | A→A:1, C→A:5, C→C:5, C→E:4 |
| H2 | B_reverse | 11 | 5 | 0 | 6 | 5 | A→A:1, C→A:5, C→C:5 |
| H3 | A | 16 | 0 | 0 | 16 | 0 | A→A:6, C→C:5, F→F:5 |
| H3 | B | 19 | 9 | 1 | 10 | 8 | A→A:1, C→A:5, C→C:5, C→E:2, D→D:1, F→B:1, F→E:1, F→F:3 |
| H3 | C | 24 | 11 | 2 | 13 | 9 | A→A:1, C→A:5, C→C:5, C→E:4, D→D:4, F→B:2, F→F:3 |
| H3 | B_reverse | 16 | 6 | 0 | 11 | 5 | A→A:1, C→A:4, C→C:5, E→A:1, F→E:1, F→F:4 |
| H4 | A | 5 | 0 | 0 | 5 | 0 | A→A:1, C→C:4 |
| H4 | B | 5 | 4 | 0 | 1 | 4 | A→A:1, C→A:4 |
| H4 | C | 5 | 4 | 0 | 1 | 4 | A→A:1, C→A:4 |
| H4 | B_reverse | 5 | 4 | 0 | 1 | 4 | A→A:1, C→A:4 |
| ALL | A | 43 | 0 | 0 | 43 | 0 | A→A:14, C→C:19, F→F:10 |
| ALL | B | 55 | 27 | 1 | 28 | 26 | A→A:4, C→A:19, C→C:15, C→E:5, D→D:2, F→A:1, F→B:1, F→E:1, F→F:7 |
| ALL | C | 69 | 35 | 3 | 34 | 32 | A→A:4, C→A:19, C→C:15, C→E:12, D→D:8, F→A:1, F→B:3, F→F:7 |
| ALL | B_reverse | 49 | 22 | 0 | 29 | 20 | A→A:4, C→A:18, C→C:15, E→A:1, E→D:1, F→E:2, F→F:8 |

## PF frequency

Selection denominator: selector turns. Activation denominator: native dispatch calls, including those where that PF was not selected. C is retained, not model-selected.

| World | Arm | PF | Selected / selector turns | Gate true | Activated / dispatches |
|---|---|---|---|---:|---|
| H1 | B | evidence_collection | 13/18 | 5 | 5/18 |
| H1 | B | request_id_trace | 4/18 | 0 | 0/18 |
| H1 | B | comparison_experiment | 1/18 | 0 | 0/18 |
| H1 | B | dependency_trace | 2/18 | 1 | 1/18 |
| H1 | B | binary_isolation | 5/18 | 1 | 1/18 |
| H1 | C | evidence_collection | retained | 5 | 5/25 |
| H1 | C | request_id_trace | retained | 0 | 0/25 |
| H1 | C | comparison_experiment | retained | 0 | 0/25 |
| H1 | C | dependency_trace | retained | 5 | 5/25 |
| H1 | C | binary_isolation | retained | 4 | 4/25 |
| H1 | B_reverse | evidence_collection | 8/17 | 5 | 5/17 |
| H1 | B_reverse | request_id_trace | 9/17 | 0 | 0/17 |
| H1 | B_reverse | comparison_experiment | 1/17 | 0 | 0/17 |
| H1 | B_reverse | dependency_trace | 3/17 | 2 | 2/17 |
| H1 | B_reverse | binary_isolation | 3/17 | 0 | 0/17 |
| H2 | B | evidence_collection | 10/13 | 5 | 5/13 |
| H2 | B | request_id_trace | 3/13 | 0 | 0/13 |
| H2 | B | comparison_experiment | 0/13 | 0 | 0/13 |
| H2 | B | dependency_trace | 2/13 | 2 | 2/13 |
| H2 | B | binary_isolation | 0/13 | 0 | 0/13 |
| H2 | C | evidence_collection | retained | 5 | 5/15 |
| H2 | C | request_id_trace | retained | 0 | 0/15 |
| H2 | C | comparison_experiment | retained | 0 | 0/15 |
| H2 | C | dependency_trace | retained | 5 | 5/15 |
| H2 | C | binary_isolation | retained | 0 | 0/15 |
| H2 | B_reverse | evidence_collection | 7/11 | 5 | 5/11 |
| H2 | B_reverse | request_id_trace | 10/11 | 0 | 0/11 |
| H2 | B_reverse | comparison_experiment | 0/11 | 0 | 0/11 |
| H2 | B_reverse | dependency_trace | 0/11 | 0 | 0/11 |
| H2 | B_reverse | binary_isolation | 0/11 | 0 | 0/11 |
| H3 | B | evidence_collection | 11/19 | 5 | 5/19 |
| H3 | B | request_id_trace | 4/19 | 0 | 0/19 |
| H3 | B | comparison_experiment | 1/19 | 0 | 0/19 |
| H3 | B | dependency_trace | 5/19 | 3 | 3/19 |
| H3 | B | binary_isolation | 5/19 | 1 | 1/19 |
| H3 | C | evidence_collection | retained | 5 | 5/24 |
| H3 | C | request_id_trace | retained | 0 | 0/24 |
| H3 | C | comparison_experiment | retained | 0 | 0/24 |
| H3 | C | dependency_trace | retained | 5 | 5/24 |
| H3 | C | binary_isolation | retained | 4 | 4/24 |
| H3 | B_reverse | evidence_collection | 7/16 | 4 | 4/16 |
| H3 | B_reverse | request_id_trace | 8/16 | 0 | 0/16 |
| H3 | B_reverse | comparison_experiment | 0/16 | 0 | 0/16 |
| H3 | B_reverse | dependency_trace | 3/16 | 2 | 2/16 |
| H3 | B_reverse | binary_isolation | 3/16 | 0 | 0/16 |
| H4 | B | evidence_collection | 4/5 | 4 | 4/5 |
| H4 | B | request_id_trace | 2/5 | 0 | 0/5 |
| H4 | B | comparison_experiment | 0/5 | 0 | 0/5 |
| H4 | B | dependency_trace | 0/5 | 0 | 0/5 |
| H4 | B | binary_isolation | 0/5 | 0 | 0/5 |
| H4 | C | evidence_collection | retained | 5 | 5/5 |
| H4 | C | request_id_trace | retained | 0 | 0/5 |
| H4 | C | comparison_experiment | retained | 0 | 0/5 |
| H4 | C | dependency_trace | retained | 0 | 0/5 |
| H4 | C | binary_isolation | retained | 0 | 0/5 |
| H4 | B_reverse | evidence_collection | 4/5 | 4 | 4/5 |
| H4 | B_reverse | request_id_trace | 5/5 | 0 | 0/5 |
| H4 | B_reverse | comparison_experiment | 0/5 | 0 | 0/5 |
| H4 | B_reverse | dependency_trace | 0/5 | 0 | 0/5 |
| H4 | B_reverse | binary_isolation | 0/5 | 0 | 0/5 |
| ALL | B | evidence_collection | 38/55 | 19 | 19/55 |
| ALL | B | request_id_trace | 13/55 | 0 | 0/55 |
| ALL | B | comparison_experiment | 2/55 | 0 | 0/55 |
| ALL | B | dependency_trace | 9/55 | 6 | 6/55 |
| ALL | B | binary_isolation | 10/55 | 2 | 2/55 |
| ALL | C | evidence_collection | retained | 20 | 20/69 |
| ALL | C | request_id_trace | retained | 0 | 0/69 |
| ALL | C | comparison_experiment | retained | 0 | 0/69 |
| ALL | C | dependency_trace | retained | 15 | 15/69 |
| ALL | C | binary_isolation | retained | 8 | 8/69 |
| ALL | B_reverse | evidence_collection | 26/49 | 18 | 18/49 |
| ALL | B_reverse | request_id_trace | 32/49 | 0 | 0/49 |
| ALL | B_reverse | comparison_experiment | 1/49 | 0 | 0/49 |
| ALL | B_reverse | dependency_trace | 6/49 | 4 | 4/49 |
| ALL | B_reverse | binary_isolation | 6/49 | 0 | 0/49 |
