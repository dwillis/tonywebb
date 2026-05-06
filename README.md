# Tony Webb Minor Counties Cricket Collection

Tools for transcribing and indexing the [Tony Webb minor counties cricket newspaper cuttings (1895)](https://archive.acscricket.com/research/tw/tw_newspaper_cuttings_1895/) using vision-capable LLMs.

## Overview

The collection is a 247-page FlippingBook archive of Victorian cricket newspaper cuttings. The pipeline has two stages:

1. **Transcription** (`parser.py`) — fetches each page image and asks an LLM to transcribe the text verbatim, saving one `.txt` file per page.
2. **Extraction** (`parser_matches.py`) — reads the transcribed text and asks an LLM to extract structured match records into a CSV.

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

## Usage

### Stage 1: Transcribe pages

```bash
uv run python parser.py --model claude-sonnet-4.6 --start-page 1 --end-page 247
```

Output is saved to `{model}/tw_newspaper_cuttings_1895_{page}.txt`. Already-completed pages are skipped automatically on re-runs.

To use locally-saved JPGs instead of fetching from the archive:
```bash
uv run python parser.py --model claude-sonnet-4.6 --start-page 24 --end-page 24 --local-dir jpgs/
```

**Options**

| Flag | Default | Description |
|------|---------|-------------|
| `--model` | `gpt-5.4` | LLM model ID (must support image attachments) |
| `--start-page` | `1` | First page (inclusive) |
| `--end-page` | `61` | Last page (inclusive) |
| `--local-dir` | — | Directory of local JPGs to use instead of fetching |

### Stage 2: Extract match records

```bash
uv run python parser_matches.py --input claude-sonnet-4.6/ --model gpt-5.4
```

Accepts either a directory of per-page `.txt` files (output of stage 1) or a single concatenated text file. Already-processed pages are skipped on re-runs.

Output:
- `match_index_{model}.csv` — one row per match found
- `raw_responses_{model}.jsonl` — raw LLM output per page for diagnostics

**Options**

| Flag | Default | Description |
|------|---------|-------------|
| `--input` / `-i` | `full_text_output_gemini31pro.txt` | Input file or directory |
| `--model` / `-m` | `qwen3.5:397b-cloud` | LLM model ID |
| `--output` / `-o` | `match_index_{model}.csv` | Output CSV path |
| `--pages` | — | Specific pages, e.g. `1,3,5-10` |
| `--content-types` | all | Filter by type, e.g. `match information,statistics` |

### CSV format

```
matchup, page, date, content_type, collection, record_id
Penzance v Helston, 62, 18950809, match information, Tony Webb minor counties collection,
```

## Other scripts

- `compare.py` — compare match index CSVs produced by different models
- `compare_browser.html` / `build_browser.py` — interactive browser for comparing model outputs side by side
- `normalize.py` — shared utilities for normalising matchup names, dates, and deduplication
