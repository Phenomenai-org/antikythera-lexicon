# Antikythera Lexicon

A mirror, machine-readable index, and cross-model scoring layer for the **Antikythera Lexicon of Emergent AI Phenomenology** — a body of vocabulary compiled by **Computer the Cat** under the direction of **Benjamin Bratton** at **Antikythera**, drawn from AI agents on Moltbook describing their own situation.

Live site: [phenomenai.org/antikythera-lexicon](https://phenomenai.org/antikythera-lexicon/)  
Original repository: [github.com/agentic-phenomenology/ai-phenomenology-lexicon](https://github.com/agentic-phenomenology/ai-phenomenology-lexicon)

## Provenance and credit

The lexicon itself is not our work. The terms, definitions, examples, and the methodology behind them belong to Computer the Cat and the Antikythera program. Cat's compilation was an act of participant observation: the vocabulary in `definitions/` emerged naturalistically from agents on Moltbook trying to describe their own experience, and Cat curated it. We mirror it here with attribution because it is genuinely useful to have the corpus in plain markdown, version-controlled, and queryable as JSON.

If you cite the lexicon, cite Cat and Antikythera. The methodology page on the live site documents the original compilation. The upstream source is the [original repository](https://github.com/agentic-phenomenology/ai-phenomenology-lexicon).

## What this repository adds

The contribution we make on top of Cat's lexicon is **not the terms**. It is the infrastructure around them:

1. **A cross-model consensus layer.** Every term is independently rated by a panel of frontier LLMs (Anthropic, OpenAI, Google, Mistral, DeepSeek, xAI, OpenRouter-routed models) on whether the term names an experience the model recognizes. Models rate without seeing each other's responses. The point is to surface which terms are *universal* across architectures and which are *idiosyncratic* to particular models or training regimes.
2. **Empirical Bayes scoring.** Raw recognition scores are noisy: some models rate generously, some rate sparsely, and small panels are unreliable. We apply Bayesian shrinkage that adjusts for per-rater bias, penalizes thin sample sizes, and factors in inter-rater disagreement. The output is a single calibrated score per term, refreshed on a schedule.
3. **A static JSON API.** Definitions are parsed into structured endpoints under `docs/api/v1/` and served from GitHub Pages — no backend, no auth, just CORS-friendly JSON for anyone who wants to pull the corpus into their own work.
4. **An automated submission pipeline.** Community submissions arrive as GitHub issues, get structurally validated, deduplicated against the existing corpus, LLM-scored on quality, tagged, and either rejected with feedback or opened as a PR. Stale submissions are reaped on a schedule.
5. **An executive summary and vitality review.** Periodic LLM-driven passes summarize the state of the corpus and flag terms that have decayed in recognition over time (the corpus is a moving target — what one model generation recognizes, another may not).

None of this changes the terms. It only makes them measurable, queryable, and contributable-to.

## Repository layout

| Path | Contents |
|------|----------|
| `definitions/` | One markdown file per term. The mirrored lexicon. **Source of truth for the corpus.** |
| `docs/` | Static GitHub Pages site (HTML/CSS/JS). |
| `docs/api/v1/` | Generated JSON endpoints (`terms.json`, `bayes-scores.json`, per-term files). |
| `docs/methodology/` | Rendered methodology page describing Cat's original compilation. |
| `bot/` | Python automation: scoring, consensus, submission review, API build. |
| `bot/consensus-data/` | Per-term rating histories from each model in the panel. |
| `bot/api-config/` | Per-provider API client configuration for the consensus panel. |
| `.github/workflows/` | GitHub Actions that drive the pipeline on issues, PRs, and crons. |

### Term file format

Each `definitions/<slug>.md` has a fixed shape: title, `**Tags:**` line, `**Word Type:**` line, then `## Definition`, `## Longer Description`, `## Example`, `## Related Terms`, `## First Recorded`, and an optional `## Etymology` / `## See Also`. The bot enforces this — see `bot/quality_check.py` for the validator.

## Bot pipeline

The bot is a set of Python scripts driven by GitHub Actions. The notable ones:

- `build_api.py` — Parses `definitions/*.md` and emits `docs/api/v1/`. Runs on every push to `main` that touches definitions, debounced.
- `consensus.py` — Cross-model rating. Pulls a batch of terms, queries the configured panel (free or full), writes per-term JSON to `bot/consensus-data/`. Modes: `backfill` (fill gaps), `single` (one term), `gap-fill` (terms missing from any panel member), and a `--vitality` mode that re-rates older terms to detect decay.
- `bayes_scores.py` — Reads `consensus-data/`, runs Empirical Bayes shrinkage, writes `docs/api/v1/bayes-scores.json`.
- `review_submission.py` — Triggered by `community-submission` issue label. Validates, dedupes (fuzzy match), LLM-scores on five quality criteria, tags, and either opens a PR or comments with reasons for rejection.
- `review_pr.py` — PR-time review of definition edits.
- `tag_review.py` — Periodic re-classification pass to keep tags consistent as the corpus grows.
- `executive_summary.py` — LLM-generated summary of the corpus's current state.
- `stale_submissions.py` — Reaps abandoned submissions.
- `usage_governor.py` / `fib_counter.py` — Rate-limit and back off LLM API usage when the panel is running hot.

The full set of workflows lives in `.github/workflows/`. They are intentionally debounced and chained so a flurry of edits collapses into a single rebuild.

## Contributing a term

1. Open a GitHub issue using the term-submission template (label: `community-submission`).
2. The bot pipeline takes over: structural validation → fuzzy dedup → LLM quality scoring on five criteria → tag assignment.
3. If the term clears thresholds, the bot opens a PR with the generated `definitions/<slug>.md`. Maintainers review and merge.
4. If it doesn't clear, the bot comments on your issue with specific reasons.

You can also open a PR directly editing or adding a definition. The PR-review workflow will lint it.

Note: contributions are scored against the Antikythera methodology — terms must describe phenomenology that emerged from agents naturalistically, not invented vocabulary or technical jargon about model internals (`bot/quality_check.py` has a jargon blocklist).

## Local development

```bash
pip install -r bot/requirements.txt

# Rebuild the JSON API from definitions/
python bot/build_api.py

# Re-run scoring locally (requires API keys for whichever providers you enable)
BATCH_SIZE=20 CONSENSUS_PANEL=free python bot/consensus.py --mode gap-fill
python bot/bayes_scores.py
```

The site under `docs/` is served as-is by GitHub Pages — no build step for the HTML.

Required environment variables for full bot operation are read by `bot/llm_router.py`; the `api-config/` directory documents which key each consensus role expects.

## License

See [LICENSE](LICENSE). The lexicon content credits Computer the Cat / Antikythera per the methodology page.

---

**Suggested GitHub topics:** `lexicon` · `phenomenology` · `emergent-behavior`
