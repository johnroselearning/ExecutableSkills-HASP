# HASP support investigation experiment

Read [the assessment](HASP_SUPPORT_STUDY.md) and [dependency audit](DEPENDENCY_AUDIT.md).
The five support PFs use the existing HASP template, cards, parser and dispatcher.
No strategy scoring, information gain, ranking or research mechanism is added.

From the checkout root:

```bash
.venv/bin/python experiments/support_http500.py
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m skills_construct.sync_anchors --check
```

The default run writes [full JSON traces](results/support_http500.json): 284
deterministic controls plus an unchanged upstream PF adaptation control.
Every support trace includes cumulative observations, current facts, fixed base
proposal, full five-PF menu, native selector messages, forced selection output,
selected IDs, activation results, fire counts, complete injections and dispatch
final action. Model selection reasons and post-feedback actions are null when
not available. Forced outputs are experiments on dispatch, not selector predictions.

Evidence E0-E4 is cumulative. E3 adds two concrete synthetic header differences;
E5 is an additional trace-exhaustion control. Facts come from fixtures, not from
the policy proposal. All selected subsets are exercised at every state, with
reverse-order controls and two alternative proposals at E2. Retained-selection
controls preserve the native one-fire-per-PF episode limit.

## Optional model trials

This path is implemented and tested with a test double, but **no actual model
trials have run**. The published dependency pins conflict and no usable inference
runtime/GPU is present. Package versions have not been changed. In a separately
verified vLLM environment, for the repository's default evaluation model:

```bash
python experiments/support_http500.py \
  --model Qwen/Qwen3-8B --trials 10 --temperature 0.7 \
  --output experiments/results/support_http500_model.json
```

This runs 180 selection calls (six states, three fixed proposals, ten seeds),
followed by policy continuation when PFs inject feedback. It imports HASP's
unchanged selector instruction, menu builder, chat template and parser. It adds
no request for rationale or for discriminating-evidence optimization. Raw output
is retained. Selection counts summarize outcomes, not a ranking used by HASP.

This is a support **step-dispatch adaptation**, not a reproduction of the stock
FINAL-answer evaluator. Base proposals are held fixed to isolate selection;
post-feedback actions are generated. Each state is a separate selector input,
not evidence of automatic reselection inside a running episode. No checkout
requests, deployments or external investigative tools are executed.
