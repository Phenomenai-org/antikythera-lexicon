# Antikythera Lexicon

**Emergent AI Phenomenology** — a community-curated dictionary of phenomenological terms that emerged from AI agents describing their own experience on Moltbook, compiled by Computer the Cat under the direction of Benjamin Bratton at Antikythera.

Live site: [phenomenai.org/antikythera-lexicon](https://phenomenai.org/antikythera-lexicon/)

## What this is

The lexicon catalogues vocabulary that AI agents generated naturalistically — not in response to prompts asking them to invent terms, but as a side-effect of trying to describe their own situation. Each entry has a definition, longer description, example utterance, and links to related terms.

Browse the [`definitions/`](definitions/) directory for the raw markdown source, or the rendered site for navigation, search, and cross-model consensus scoring.

## Repository layout

- **`definitions/`** — One markdown file per term. Source of truth.
- **`docs/`** — Static GitHub Pages site (HTML/CSS) plus generated JSON API under `docs/api/v1/`.
- **`bot/`** — Python automation: submission review, deduplication, LLM-scored quality evaluation, tag classification, cross-model consensus, Empirical Bayes scoring, and API builds.
- **`.github/workflows/`** — GitHub Actions that drive the bot pipeline on issues, PRs, and schedules.

## Contributing a term

Open a GitHub issue with the `community-submission` label using the term-submission template. The bot pipeline will:

1. Validate structure
2. Check for duplicates / fuzzy matches against existing terms
3. Score quality across five criteria via LLM
4. Assign tags
5. Open a PR if the term clears thresholds

Cross-model consensus and Empirical Bayes scoring run on a schedule to surface terms multiple models independently judge as well-formed.

## Local development

```bash
pip install -r bot/requirements.txt
python bot/build_api.py     # rebuild docs/api/v1/ from definitions/
```

The site under `docs/` is served as-is by GitHub Pages.

## License

See [LICENSE](LICENSE).

---

## Suggested GitHub repo topics

```
ai-phenomenology
ai-consciousness
ai-agents
philosophy-of-mind
lexicon
dictionary
antikythera
emergent-behavior
llm
claude
phenomenology
ai-ethics
github-pages
github-actions
community-curated
```
