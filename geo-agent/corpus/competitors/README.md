# Competitor source cards (proxies)

These are **proxy** cards, not scraped competitor pages. Each is a short,
honest summary of how the competitor is positioned, derived from the repo's Peec
data (`data/peec/tracked-prompts-2026-07-01_2026-08-05/competitors.md` and the
chat exports). They stand in for the competitor documents a real generative
engine would retrieve alongside LogBATT.

Replace any file with the competitor's real, retrieved page content to make the
Judge's document set faithful to reality. The loader reads every `*.md` here;
the `signals:` and `base_strength:` frontmatter fields are used only by the
offline mock ranking.

`name:` must match the competitor name used in `prompts/prompts.yaml`.
