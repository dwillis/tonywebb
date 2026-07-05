# Tony Webb Minor Counties Cricket Collection

Tools for transcribing and indexing the [Tony Webb minor counties cricket newspaper cuttings (1895)](https://archive.acscricket.com/research/tw/tw_newspaper_cuttings_1895/) using LLMs, packaged as a single `tonywebb` CLI.

## Overview

The collection is a 247-page FlippingBook archive of Victorian cricket newspaper cuttings. The pipeline has three stages:

1. **Transcription** (`tonywebb transcribe`) — fetches each page image and asks a vision LLM to transcribe the text verbatim, saving one `.txt` file per page.
2. **Extraction** — reads the transcribed text and asks an LLM to pull out structured data:
   - `tonywebb extract-matches` — match/content index entries (match reports, statistics tables, biographies, etc.) into a CSV.
   - `tonywebb extract-stats` — end-of-season player/team averages tables into JSON.
   - `tonywebb extract-scorecards` — per-match batting/bowling scorecards into JSON, linked back to the match index.
3. **Analysis** — comparing model outputs and scoring them against a manually-built ground truth:
   - `tonywebb compare` / `tonywebb browse` — cross-model agreement.
   - `tonywebb evaluate` — score a model's index against `match_index_willis.csv`.
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
matchup, page, date, content_type, collection, record_id
Penzance v Helston, 62, 18950809, match information, Tony Webb minor counties collection,
```

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

## Stage 2c: Extract match scorecards

```bash
uv run tonywebb extract-scorecards --input qwen3.5:397b/ --model qwen3.5:397b-cloud --index match_index_qwen3.5_cloud.csv
```

Extracts the full batting/bowling scorecard for every match report, as opposed to just the match's existence (which is all `extract-matches` records). Output is `scorecards_{model}.json`: one entry per match with per-innings batting lines (batter, dismissal, bowler, fielder, runs, `raw` verbatim source line), bowling figures (including figures given only in prose, e.g. "Tilley took five wickets for 12 runs"), extras, and totals.

Every scorecard is validated on write: batting runs + extras are checked against the stated total, bowler figures are cross-checked against credited dismissals, names are sanity-checked, and the scorecard is linked back to its `match_index` row (exact, then fuzzy match). This produces a `confidence` score and a list of `flags` (e.g. `total_mismatch`, `not_in_index`) — useful for triaging which scorecards need a human look, since Victorian print runs and low-resolution scans reliably scramble numeric columns.

Scorecards below the confidence threshold (default `0.7`) can be re-verified against the actual page image with a vision model:

```bash
uv run tonywebb extract-scorecards --recheck --vision-model gemini-3.1-pro-preview --local-dir jpgs/
```

This re-sends only the flagged pages, and replaces a scorecard only if the recheck's confidence is higher than the original.

**Options**

| Flag | Default | Description |
|------|---------|-------------|
| `--input` / `-i` | `full_text_output_gemini31pro.txt` | Input file or directory |
| `--model` / `-m` | `qwen3.5:397b-cloud` | LLM model ID |
| `--index` | — | `match_index_<model>.csv` to link scorecards against |
| `--sum-tolerance` | `0` | Allowed discrepancy between computed and stated innings totals |
| `--recheck` | off | Re-verify low-confidence scorecards against page images |
| `--vision-model` | `gpt-5.4` | Model used for `--recheck` |
| `--recheck-threshold` | `0.7` | Confidence cutoff for `--recheck` |
| `--limit` | — | Max scorecards to recheck in one run |

## Stage 3: Evaluate against the Willis ground truth

`match_index_willis.csv` is a manually-built index covering pages 1–61 (388 rows) — a partial ground truth, not a complete one. `tonywebb evaluate` scores a model's output against it:

```bash
uv run tonywebb evaluate match_index_qwen3.5_cloud.csv
uv run tonywebb evaluate --all   # every match_index_*.csv, plus a leaderboard
```

Because Willis is partial, the headline metric is **coverage** (recall against the rows Willis has), not precision — "surplus" model rows on Willis-covered pages are reported as a review list, not treated as false positives. Each run writes `eval_{label}.md` with coverage by content type, missed Willis rows, low-similarity fuzzy matches, and the surplus list, so it doubles as a human-review worksheet.

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

Package layout: `tonywebb/pipeline.py` holds the shared page-iteration/retry/resume scaffolding used by every extraction command; `tonywebb/normalize.py` holds matchup/date normalization and the club registry; `tonywebb/scorecards/` holds the scorecard schema, validation, and prompts. `compare.py` at the repo root (field-level diff report) predates the CLI and is kept standalone.
