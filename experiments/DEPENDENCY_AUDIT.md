# Dependency audit

Checked 2026-09-15 against upstream commit
`2a0e859ef320719d0794fe2ccda5c672a28cc0fb`. No package pins were changed.

## Evidence

| Source | Finding |
| --- | --- |
| `requirements.txt:10` | Pins `vllm==0.15.1` and `transformers==5.5.3` together. |
| Complete local git history | Not shallow. Three commits total; requirements introduced once in `081a469db18d6d813c9b95a045b0b2a895ac8fad`, with the same conflict. No alternative historical pin set. |
| `README.md:65` | Recommends Python 3.11. |
| `README.md:69` | Explicitly retains vLLM 0.15.1 and lets it resolve torch 2.9.1; advises against an independently pinned torch/CUDA build. |
| `README.md:73` | Places Qwen3.5 models requiring vLLM 0.20 in a separate environment; argues against silently upgrading the default stack. |
| Tracked file inventory | No lock file, pyproject, environment export or CI environment defining a working alternative. |
| `scripts/slurm/env.sh:33` | Optional uncommitted site configuration and a `hasp` conda environment; no exact package set. Local `~/.hasp_site` is absent. |
| `configs/protocol.yaml:16`, SLURM configs | Qwen3-4B/8B and Qwen2.5-7B defaults. These do not establish an exact Transformers pin. |
| Public GitHub API | `issues?state=all&per_page=100` returned `[]`; branches returned only `main`, at the checkout SHA. Local tag list is empty. |
| Published vLLM 0.15.1 metadata | Requires `transformers<5,>=4.56.0`, `torch==2.9.1`, `torchaudio==2.9.1`, `torchvision==0.24.1`. |

Public metadata was fetched directly as JSON, after a sandbox DNS failure:
[vLLM package metadata](https://pypi.org/pypi/vllm/0.15.1/json),
[repository issues](https://api.github.com/repos/HolaYan/ExecutableSkills-HASP/issues?state=all&per_page=100),
[repository branches](https://api.github.com/repos/HolaYan/ExecutableSkills-HASP/branches).

Reproduce the history checks with:

```bash
git rev-parse --is-shallow-repository
git log --all -p -- requirements.txt
git log --all --oneline -- README.md requirements.txt scripts/slurm/env.sh configs/protocol.yaml
git tag --list
```

## Conclusion

The published requirements cannot resolve as written. The strongest documented
intent is Python 3.11 plus vLLM 0.15.1 and its torch dependencies. Retaining that
vLLM version requires Transformers in `[4.56.0, 5)`, but this is a necessary
compatibility constraint, **not an author-confirmed replacement pin or proof that
the entire unbounded training dependency set will resolve**. No source found
establishes the exact environment used by the author. A silent upgrade or a
guessed Transformers downgrade would not be a faithful reproduction.

## Model availability

The project venv supports the CPU checks; the earlier full installation attempt
failed on the conflict. The available system Python is 3.12.3; Python 3.11 and
conda were unavailable in the initial reproduction. System Python has no torch,
Transformers or vLLM. `nvidia-smi` is unavailable and `/dev/nvidia0`, `/dev/kfd`
and `/dev/dri` are absent. No HASP/model/provider environment variables were
configured. A Hugging Face cache contains model directory names, which alone
does not supply a runnable model environment. No new inference packages were
installed during this extension, and no stochastic model trials are reported.
