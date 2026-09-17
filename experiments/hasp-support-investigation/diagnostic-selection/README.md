# Diagnostic selection: design checkpoint

**STOPPED BEFORE MODEL EXPERIMENTS.** No model calls, API charges, model downloads,
package installations, or GPU jobs were made. No diagnostic performance is claimed.
Only this directory was changed for this request. Existing support PFs are unchanged.

Read [DESIGN.md](DESIGN.md) for the reviewable protocol and
[RESULTS.md](RESULTS.md) for checkpoint findings in the requested report structure.
[The complete hypothesis/action/evidence matrix](analysis/MATRIX.md) and
[best-next-check calculations](analysis/CALCULATIONS.md) are generated from code.

From `/home/rose/projects/hasp/ExecutableSkills-HASP`:

```bash
.venv/bin/python experiments/hasp-support-investigation/diagnostic-selection/test_diagnostic.py
.venv/bin/python experiments/hasp-support-investigation/diagnostic-selection/runner.py --checkpoint
```

The runner deliberately has **no live-model mode**. After design review, a provider
adapter and full trial/aggregation loop remain to be implemented. This checkpoint
implements the deterministic oracle, counterfactual evaluator, native interface,
mechanical competition probes, and exact prompt previews. It does not pretend that
scripted proposals are model-driven trials.

- `actions.py`: public tools/costs, without outcomes or preferred actions.
- `hypotheses.py`: private closed-world definitions and outcome table.
- `oracle.py`: private host-side oracle; evidence returned only on executing checks.
- `evaluator.py`: offline partition scoring and fixed-world cost lower bounds.
- `native_adapter.py`: original HASP menu/prompt/parser/dispatcher; no scoring imports.
- `runner.py`: CPU-only checkpoint artifact generator.
- `traces/checkpoint_mechanical.jsonl`: 10 explicitly labeled mechanical probes;
  model outputs and policy executions are null, not fabricated.
- `analysis/`: full matrix, all possible outcomes, scores, CSV and case summaries.
- `results/checkpoint_manifest.json`: settings plan and source hashes; zero trials.

The source and offline artifacts reveal the truth to the **human reviewer**. The
future investigation model gets only projected public messages, never repository
access, evaluator data, source, this documentation, or artifact files. The Python
oracle is a data boundary, not a sandbox against an agent with arbitrary filesystem
access. Supplying such access would invalidate the experiment.
