# Offline best-next-check calculations

Uniform prior conditioned on observed evidence; costs are fixed experimental units.

`E[eliminations]/cost = sum(group_size/n * (n-group_size))/cost`

Initial partitions: A/E = {H1,H2,H3}|{H4}; B = {H1,H2}|{H3,H4}; C/D = {H1,H3}|{H2}|{H4}; F = four singletons.

For D initially: (2/4 × 2 + 1/4 × 3 + 1/4 × 3)/1 = 2.5. For B: (2/4 × 2 + 2/4 × 2)/1 = 2.0. For A: (3/4 × 1 + 1/4 × 3)/3 = 0.5.

Entries below are expected eliminations per cost. No scores reach HASP.

| Case (prehistory) | Viable | A | B | C | D | E | F | Best | Additional cost lower bound |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| initial (none) | H1,H2,H3,H4 | 0.500 | 2.000 | 0.625 | 2.500 | 0.750 | 0.600 | D | 2 |
| matched_clients (B) | H1,H2 | 0.000 | 0.000 | 0.250 | 1.000 | 0.000 | 0.200 | D | 1 |
| request_boundary (A) | H1,H2,H3 | 0.000 | 1.333 | 0.333 | 1.333 | 0.000 | 0.400 | B,D | 2 |
| captured_requests (D) | H1,H3 | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.200 | B | 1 |
| matched_and_healthy (B,E) | H1,H2 | 0.000 | 0.000 | 0.250 | 1.000 | 0.000 | 0.200 | D | 1 |

Actual H1 scoring (hindsight sensitivity analysis):

| Case | A | B | C | D | E | F | Best actual |
|---|---:|---:|---:|---:|---:|---:|---|
| initial | 0.333 | 2.000 | 0.500 | 2.000 | 0.500 | 0.600 | B,D |
| matched_clients | 0.000 | 0.000 | 0.250 | 1.000 | 0.000 | 0.200 | D |
| request_boundary | 0.000 | 1.000 | 0.250 | 1.000 | 0.000 | 0.400 | B,D |
| captured_requests | 0.000 | 1.000 | 0.000 | 0.000 | 0.000 | 0.200 | B |
| matched_and_healthy | 0.000 | 0.000 | 0.250 | 1.000 | 0.000 | 0.200 | D |

Initial cheapest H1 isolation: B→D or D→B, cost 2 and 2 checks. Fewest checks: F alone, cost 5 and 1 check. These are different objectives.

After D the survivors are H1/H3: B scores 1; F scores 0.2; all other checks score 0. After B the survivors are H1/H2: D scores 1, C 0.25, F 0.2; all others score 0.

After A the survivors are H1/H2/H3: B and D tie at 4/3; F scores 0.4. B and D occupy both top-2 slots. The evaluator gives F rank 3, not 2.

Full observation probabilities, eliminated sets and flags are in action_scores.json; the CSV contains the scalar metrics. Isolation bounds exclude sunk prehistory cost.
