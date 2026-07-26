# Tony Webb Minor Counties Cricket Collection

Tools for transcribing and indexing the [Tony Webb minor counties cricket newspaper cuttings (1895)](https://archive.acscricket.com/research/tw/tw_newspaper_cuttings_1895/) using LLMs, packaged as a single `tonywebb` CLI.

## Overview

The collection is a 247-page FlippingBook archive of Victorian cricket newspaper cuttings. The pipeline has three stages:

1. **Transcription** (`tonywebb transcribe`) — fetches each page image and asks a vision LLM to transcribe the text verbatim, saving one `.txt` file per page. `tonywebb clean-transcriptions` fixes OCR-layer artifacts (dot leaders, soft-wrap hyphens, known typos) in the result.
2. **Extraction** — reads the transcribed text and asks an LLM to pull out structured data:
   - `tonywebb extract-matches` — match/content index entries (match reports, statistics tables, biographies, etc.) into a CSV.
   - `tonywebb extract-stats` — end-of-season player/team averages tables into JSON.
   - `tonywebb index-stats` — a focused pass that indexes *which pages* have end-of-season statistics tables, ACS-style.
   - `tonywebb index-scorecards` — a focused pass that indexes *which match reports* include a full scorecard.
3. **Analysis and assembly** — comparing model outputs, scoring them against a manually-built ground truth, and merging them into one deliverable index:
   - `tonywebb compare` / `tonywebb browse` — cross-model agreement.
   - `tonywebb evaluate` — score a model's index against `match_index_willis.csv`.
   - `tonywebb consensus` — merge every `match_index_*.csv` into one submittable index via majority vote.
   - `tonywebb promote-reviewed` — append your accepted review-queue rows into the Willis ground truth.
   - `tonywebb clubs` — regenerate the canonical team-name registry (`clubs.csv`).

## Setup

```bash
uv sync
llm keys set anthropic   # or openai, gemini, etc.
```

For Ollama cloud models:
```bash
export OLLAMA_HOST=https://api.ollama.com
llm keys set ollama      # paste your Ollama API key
```

Run any command with `uv run tonywebb <command> --help`.

## Stage 1: Transcribe pages

```bash
uv run tonywebb transcribe --model claude-sonnet-4.6 --start-page 1 --end-page 247
```

Output is saved to `{model}/tw_newspaper_cuttings_1895_{page}.txt` (bulk mode). Already-completed pages are skipped automatically on re-runs.

To use locally-saved JPGs instead of fetching from the archive:
```bash
uv run tonywebb transcribe --model claude-sonnet-4.6 --pages 24 --local-dir jpgs/
```

To write a single concatenated file (the `full_text_output_*.txt` format) instead of per-page files:
```bash
uv run tonywebb transcribe --model gpt-5.4 --pages 1,3,5-10 --output full_text_output_gpt54.txt
```

**Options**

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `gpt-5.4` | LLM model ID (must support image attachments) |
| `--pages` | — | Specific pages/ranges, e.g. `1,3,5-10` (overrides `--start-page`/`--end-page`) |
| `--start-page` / `--end-page` | `1` / `61` | Page range (bulk mode) |
| `--local-dir` | — | Directory of local JPGs to use instead of fetching |
| `--output-dir` | `{model}/` | Per-page output directory (bulk mode) |
| `--output` / `-o` | — | Write a single concatenated file/stdout instead of per-page files |

## Stage 1b: Clean transcriptions

```bash
uv run tonywebb clean-transcriptions --input qwen3.5:397b/ --dry-run   # preview counts first
uv run tonywebb clean-transcriptions --input qwen3.5:397b/             # then write in place
```

Fixes three things in already-transcribed page text: soft line-wrap hyphens that split a word across two lines (`per-\nformances` → `performances`), dot-leader runs in averages tables (`Curtis........... 9 196` → `Curtis .. 9 196`), and a handful of known misreadings (`Ex ras` → `Extras`). The hyphen join is guarded — it skips the join when either side is numeric or the right side starts with a capital letter, so real hyphenated surnames split at a line wrap (`Tasker-\nEvans`, `GRANT-\nCHESTER`) are left alone, with a narrow exception for `Mc-`/`Mac-` prefixes (`Mc-\nGuire` → `McGuire`, which genuinely is one name split by the wrap).

Always run `--dry-run` first — it reports per-file change counts with no writes — then re-run without it once the counts look right. `--skip-dot-leaders`, `--skip-hyphens`, and `--skip-typos` disable individual transforms.

## Stage 2: Extract match records

```bash
uv run tonywebb extract-matches --input claude-sonnet-4.6/ --model gpt-5.4
```

Accepts either a directory of per-page `.txt` files or a single concatenated text file. Already-processed pages are skipped on re-runs.

Output:
- `match_index_{model}.csv` — one row per entry found (18 content types: match reports, statistics, biographies, etc.)
- `raw_responses_{model}.jsonl` — raw LLM output per page for diagnostics

**CSV format**

```
matchup, page, date, content_type, collection, pages
Penzance v Helston, 62, 18950809, match information, Tony Webb minor counties collection,
```

`pages` is the number of distinct pages this entry was found on -- normally `1`. The same match sometimes gets reported twice, not just as a continuation onto the very next page but in a wholly separate newspaper cutting elsewhere in the collection (team order and even the reported date can differ between the two write-ups). Every run recomputes this column across the whole output file, flagging both occurrences with the shared count rather than merging them into one row, so nothing is silently dropped -- a human decides what to do with the duplicate. `consensus` and `promote-reviewed` also recompute it on their own output.

**Options**

| Flag | Default | Description |
|------|---------|-------------|
| `--input` / `-i` | `full_text_output_gemini31pro.txt` | Input file or directory |
| `--model` / `-m` | `qwen3.5:397b-cloud` | LLM model ID |
| `--output` / `-o` | `match_index_{model}.csv` | Output CSV path |
| `--pages` | — | Specific pages, e.g. `1,3,5-10` |
| `--content-types` | all | Filter by type, e.g. `match information,statistics` |

## Stage 2b: Extract season statistics

```bash
uv run tonywebb extract-stats --input full_text_output_gemini31pro.txt --model qwen3.5:397b-cloud
```

Extracts end-of-season batting/bowling averages tables (not individual match scorecards) into `player_stats_{model}.json`.

## Stage 2c: Index statistics tables and scorecards

Two focused, single-purpose passes that produce ordinary `match_index`-shaped
CSVs (same 6 columns) rather than a separate data model. An earlier version
of this project tried to fully *extract* scorecard batting/bowling figures
into structured JSON (`extract-scorecards`); on a full run, 613/786 (78%) of
the extracted scorecards scored below a 0.7 confidence threshold, because
Victorian print quality and transcription noise make figure-level extraction
unreliable. These two commands instead answer a much more reliable question
— "does this exist on this page" — which is what an ACS-style index needs.

```bash
uv run tonywebb index-stats      --input qwen3.5:397b/ --model qwen3.5:397b-cloud
uv run tonywebb index-scorecards --input qwen3.5:397b/ --model qwen3.5:397b-cloud
```

- `index-stats` finds end-of-season batting/bowling averages tables and
  writes one `"Team Name player statistics"` row per team per page — even
  when that team has several separate tables (1st XI, 2nd XI, batting,
  bowling), matching the Willis convention of one entry per team, not per
  table. A `"Team Name team aggregates"` row is added when the team also has
  separate aggregate figures (season record, runs for/against as a team).
  Output: `stats_index_{model}.csv` + `raw_responses_stats_index_{model}.jsonl`.
- `index-scorecards` finds match reports that include a full scorecard
  (individual batting lines with dismissals and runs, plus an innings total)
  as opposed to a prose-only result, and writes ordinary
  `"Team A v Team B"` / `match information` rows. The file itself — not a
  special `content_type`, since the ACS controlled vocabulary has none for
  this — is what marks "these matches have scorecards."
  Output: `scorecard_index_{model}.csv` + `raw_responses_scorecard_index_{model}.jsonl`.

Both share `extract-matches`' continuation rule (only index content that
*begins* on the page) and full 1895 date resolution (publication date,
weekday references, bank holidays).

**Options** (both commands)

| Flag | Default | Description |
|------|---------|-------------|
| `--input` / `-i` | `full_text_output_gemini31pro.txt` | Input file or directory |
| `--model` / `-m` | `qwen3.5:397b-cloud` | LLM model ID |
| `--output` / `-o` | `stats_index_{model}.csv` / `scorecard_index_{model}.csv` | Output CSV path |
| `--pages` | — | Specific pages, e.g. `1,3,5-10` |

## Stage 3: Evaluate against the Willis ground truth

`match_index_willis.csv` is a manually-built index covering pages 1–61 (388 rows) — a partial ground truth, not a complete one. `tonywebb evaluate` scores a model's output against it:

```bash
uv run tonywebb evaluate match_index_qwen3.5_cloud.csv
uv run tonywebb evaluate --all   # every match_index_*.csv, plus a leaderboard
```

Because Willis is partial, the headline metric is **coverage** (recall against the rows Willis has), not precision — "surplus" model rows on Willis-covered pages are reported as a review list, not treated as false positives. Each run writes `eval_{label}.md` with coverage by content type, missed Willis rows, low-similarity fuzzy matches, and the surplus list, so it doubles as a human-review worksheet.

`--pages` restricts scoring to only the pages you actually ran (useful for a partial/test run, so coverage isn't diluted by pages you never attempted), and `--content-types` restricts it to only certain content types — use this to score a focused index like `stats_index_*.csv` (`--content-types statistics`) or `scorecard_index_*.csv` (`--content-types "match information"`) against Willis's full mix of content types:

```bash
uv run tonywebb evaluate stats_index_qwen3.5_397b-cloud.csv --content-types statistics
```

## Stage 4: Merge into a consensus index

Every command above produces one model's opinion, or a diagnostic comparison — nothing assembles them into a single deliverable index. `tonywebb consensus` does:

```bash
uv run tonywebb consensus
```

Groups every `match_index_*.csv` row by (normalized matchup, page, content type) and majority-votes the date and matchup text. `match_index_willis.csv`, when present, is treated as authoritative for any row it has — both spelling and date — since it's the manually-verified ground truth; otherwise the most common value among the model files wins. No group is dropped just because only one model found it (no single model has near-complete recall), but every disagreement — a date split, a matchup-text variant, a row only one model found — is flagged in `consensus_report.md` for human review rather than silently resolved. Writes `consensus_index.csv` (same 6-column format as everything else) and the report. `--min-agreement N` drops non-Willis rows found by fewer than `N` model files instead of just flagging them.

## Promoting reviewed entries

`match_index_willis.csv` only covers pages 1–61. `tonywebb browse` has an "Export Reviewed CSV" button that writes whatever you've accepted in the review queue as `match_index_reviewed.csv`; `tonywebb promote-reviewed` appends the rows from that export that aren't already in Willis, so your review decisions expand the ground truth past page 61 instead of being a one-time manual index:

```bash
uv run tonywebb promote-reviewed match_index_reviewed.csv --dry-run   # preview what's new
uv run tonywebb promote-reviewed match_index_reviewed.csv             # then append it
```

## Other analysis commands

```bash
uv run tonywebb compare              # cross-model agreement matrix -> compare_results.md
uv run tonywebb browse               # interactive HTML browser -> compare_browser.html
uv run tonywebb clubs                # regenerate clubs.csv from all match_index_*.csv files
```

## Development

```bash
uv run pytest
```

Package layout: `tonywebb/pipeline.py` holds the shared page-iteration/retry/resume scaffolding used by every extraction command; `tonywebb/indexing.py` holds the shared prompt fragments (style rules, 1895 calendar, date-context builder) and CLI runner used by every *index*-producing command (`extract-matches`, `index-stats`, `index-scorecards`); `tonywebb/normalize.py` holds matchup/date normalization and the club registry. `compare.py` at the repo root (field-level diff report) predates the CLI and is kept standalone.
