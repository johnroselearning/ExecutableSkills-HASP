# Dependency Audit

Inspected 2026-09-15. No package versions were changed for these trials.

## Evidence

- Checkout HEAD: `2a0e859`; preceding implementation commit:
  `081a469db18d6d813c9b95a045b0b2a895ac8fad`.
- `git log -p -- requirements.txt` shows one introduction of the dependency
  file, in `081a469`, with both `vllm==0.15.1` and `transformers==5.5.3`.
  There is no later correction in the available history.
- README Setup explicitly recommends Python 3.11, vLLM 0.15.1 and allowing
  vLLM to resolve Torch 2.9.1. It says to keep Qwen3.5/vLLM 0.20 in a separate
  environment rather than upgrading the default. Flash Attention is optional
  and intentionally absent from requirements.
- `git ls-files '*lock*' '*requirements*' '*environment*' '*conda*'` returns
  only `requirements.txt`. There is no committed lock or conda environment
  specification resolving the contradictory pins.
- `scripts/slurm/env.sh` selects `HASP_CONDA_ENV`, default `hasp`, optionally
  from `~/.hasp_site`. It supplies no independent dependency versions. No
  local `~/.hasp_site` override was found by the site-file check.
- The public [GitHub issue API](https://api.github.com/repos/HolaYan/ExecutableSkills-HASP/issues?state=all&per_page=100)
  returned `[]` for all states, so it provided no author clarification. The
  browser fetch of the issue webpage failed; the API check succeeded.
- The [published vLLM 0.15.1 metadata](https://pypi.org/pypi/vllm/0.15.1/json)
  declares `transformers<5,>=4.56.0`, `torch==2.9.1`,
  `torchaudio==2.9.1`, `torchvision==0.24.1`, and `tokenizers>=0.21.1`.
  Therefore its Transformers requirement cannot intersect the repository's
  `transformers==5.5.3` pin.

## Interpretation

The author's stated default is the vLLM 0.15.1/Torch 2.9.1 stack. An exact
intended, compatible Transformers version cannot be recovered from these
sources. A 4.x version satisfying vLLM would resolve this particular conflict,
but choosing one would be our repair, not a recovered author lock. It would
also require resolving and checking the rest of the training dependency set.

The existing local `.venv` is Python 3.12 with SymPy 1.14.0 and pytest 9.1.1;
it has no Torch, Transformers or vLLM. No API-key environment variables were
present. A local Ollama service has two models, so repeated inference is
available without repairing or installing the pinned training stack.

## Trial Backend

The model used is `gemma4e-64k:latest`, local digest prefix `8f3c23b2ff2b`.
`ollama show` reports architecture gemma4, 8.0B parameters, Q4_K_M quantization,
configured context 64000, top-k 64, top-p 0.95. The harness sets temperature
0.7, seeds 101 onward and `think=false`. It uses the same native HASP menu,
selection instruction, tag parser and executable PF dispatcher. Ollama's chat
rendering replaces vLLM's inference backend. This is a support-domain adaptation,
not a reproduction of the paper's model/backend benchmark.

The local model is a useful behavioral counterexample test, but does not
establish what the authors' reported models would do. Model identity, full
responses, token-limit termination reasons, inputs and code hashes are retained
in the JSONL records.

## Separate Import-Path Issue

The focused `python -m pytest tests -q` run passed, and the native anchor
consistency check reported 77 matching skills/cards. Repository-wide pytest
collection also imports `training/tests/smoke_test.py`, which prepends `src`
to `sys.path`. The initial broad run had 80 passes and three registry/helper
failures. A separate probe confirmed that `skills_agent.skills.program_functions`
and `src.skills_agent.skills.program_functions` can be distinct modules with
distinct registries (77 versus 37 entries in that probe). This is an import
identity issue, not evidence that changing Transformers repairs the tests.

The trial harness runs from the repository root without adding `src` to its
import path. Its recorded mechanical probes confirmed a record for every
selected support PF, and its startup now checks that all five are registered
in the dispatcher's registry. Core loader behavior was left unchanged.
