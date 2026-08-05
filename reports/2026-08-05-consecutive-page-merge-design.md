# Design: auto-merge consecutive-page continuation entries

## Problem

`extract-matches`/`index-stats`/`index-scorecards` are already instructed (via
the extraction prompt, `tonywebb/extract_matches.py:146-148`) not to create a
new entry for a match report that continues from the previous page — only for
content that *begins* on the current page. Models don't always comply: the
`willis-compare` browser surfaced real cases (e.g. `glm52_cleaned`) where the
same match got indexed on both page 9 and page 10.

Today's safety net, `track_cross_page()` / `recompute_pages_column()` in
`tonywebb/indexing.py`, deliberately never merges or drops anything — any
repeat of the same `(matchup, date, content_type)` key anywhere in the file
just gets flagged (both rows kept, `pages` count updated to the total distinct
occurrences), because the same pattern can also mean a genuinely separate
write-up of the same match elsewhere in the collection, which must not be
silently dropped.

## Goal

When the duplicate is on the *immediately next* page — overwhelmingly a
continuation, not a separate write-up — collapse it automatically: keep the
first-page row, set `pages` to the span length, drop the rest. Duplicates on
non-adjacent pages keep today's flag-only behavior unchanged.

## Algorithm

Replace `recompute_pages_column(csv_path)` with a function that, for each
`(matchup, date, content_type)` key:

1. Collect the sorted list of pages that key appears on across the whole file.
2. Split that list into maximal runs of consecutive page numbers.
3. For each run of length ≥ 2: keep only the row on the run's first page, set
   its `pages` to the run's length, and drop every other row in the run.
4. Runs of length 1 are left as-is. If a key still has more than one
   surviving run after step 3 (e.g. occurrences at pages {9, 10} and {20} —
   the first run merges to one row at page 9 with `pages=2`, page 20 stays
   its own row with `pages=1`), that's the genuine-separate-write-up case:
   unchanged from today, both surviving rows kept and flagged for human
   review.

This generalizes runs of any length (three consecutive pages of the same
report collapse to one row with `pages=3`) and handles mixed cases (one
consecutive run plus one isolated far-away occurrence of the same key)
correctly by treating each run independently.

## Audit trail

Every row dropped by step 3 is appended to a JSONL log next to the CSV
(derived from the output path, e.g. `match_index_glm52_cleaned.merges.jsonl`),
recording the dropped row's page/matchup/date/content_type and which page it
merged into — append-only, same pattern as `reconcile_conflicts.jsonl`. A
wrong merge (e.g. a rare same-day rematch between the same two teams landing
on consecutive pages) is always recoverable from this log, never silently
lost — it's just no longer in the primary deliverable CSV.

## Scope

`recompute_pages_column()` is shared by `extract-matches`, `index-stats`, and
`index-scorecards` (`tonywebb/indexing.py`'s `run_index_extraction()`), across
every content type — fixing it once in the shared function covers all three
commands and all content types, not just "match information".

## Console output changes

`run_index_extraction()`'s end-of-run summary currently prints one undifferentiated
list ("N entry(ies) also appear on an earlier page (kept; review manually)").
This changes to two separate messages:
- Merged-and-dropped continuations (with a pointer to the merge log).
- Still-flagged non-adjacent duplicates (unchanged wording/intent from today).

## Not in scope

No new CLI flag to disable the auto-merge — it becomes the new default
behavior for these three commands, not an opt-in. If an escape hatch turns
out to be wanted later, that's a small follow-up, not part of this change.

## Testing

`tests/test_indexing.py` (if it exists) or a new test module covering the
shared `indexing.py` function: exact-run merge (2 and 3+ consecutive pages),
mixed run + isolated-occurrence case, non-adjacent duplicates unchanged,
audit log content and format, and an integration check that
`run_index_extraction()`'s console output correctly separates the two
message categories.
