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

