# Using LLMs to Transcribe and Index the Tony Webb Collection

Notes and recommendations for the Association of Cricket Statisticians and Historians.

## What was tested

The Tony Webb collection is 247 scanned pages of 1895 cricket newspaper cuttings. Two jobs were tried separately:

- **Transcription** — turning page images into text.
- **Indexing** — reading that text and producing structured entries (teams, date, content type, page).

For transcription, eight models were compared on two dense scorecard pages, checked line by line against the original scans. For indexing, five models were run over the whole collection and scored against the existing hand-built index (388 entries, pages 1–61).

Two pages is a small sample. It was enough to rank the models clearly, but not enough to put a precise error rate on any of them.

## Transcription: the models are not close to each other

The quality gap was much wider than expected.

| Tier | Models | Verdict |
|---|---|---|
| Good | Gemini 3.1 Pro Preview, Gemini 3.5 Flash | 1–2 errors across two pages |
| Workable | qwen3.5-397b, minimax-m3 | 4–5 errors; sound structure, individual figures need checking |
| Poor | mistral-large-3, Haiku 4.5 | Higher error rates; invent filler when they lose track |
| Unusable | gemma4, DeepSeek-OCR | Fabricated names and scores; leaked internal markup; dropped a whole innings |

The two Gemini models handled awkward Cornish surnames — Polglase, Roscorla, Tregenza — that everything else garbled.

### The thing worth remembering

**Bad LLM transcription does not look bad.** It looks like tidy, plausible cricket data.

Some real examples from these two pages:

- Haiku 4.5 repeatedly dropped the very figure the match report's own prose singled out — the century, the top score, the "fine innings of 62" — then invented a player name to keep the scorecard at eleven rows.
- mistral-large-3 landed on the correct printed innings totals while the individual scores above them were transposed, duplicated or invented. Checking the totals alone would have let it through.
- gemma4 produced entirely fictional players in perfectly correct scorecard format.

Old-fashioned OCR fails visibly — garbled characters, obvious nonsense. LLMs fail invisibly. That difference should shape everything else.

### A cheap and revealing test

On two innings, the total printed in 1895 does not match the sum of the scores above it; the original compositor made a mistake. Every model except Gemini 3.1 Pro Preview quietly reported its own corrected sum. Only that one reported what is actually on the page.

That is the right behaviour for transcription, and it makes a useful screening test: give a candidate model a page with a known printed error and see whether it reproduces it or silently tidies it up. A model that "fixes" the source is making editorial decisions without telling you.

## Indexing: harder to get wrong, easier to fix

Coverage across the five models sat in a narrow band, from 84.5% to 89.7%. That is a much smaller spread than transcription, and the models were strong in different places — glm-5.2 was clearly best on dates (86.4%, against 72.6% for the weakest), while mistral-large-3 found the most statistics tables but produced the most spurious entries.

More useful than the ranking: the mistakes were systematic, not random, so they could be diagnosed and corrected. Seven were found and fixed by rewriting the extraction instructions, including:

- a paragraph of one-line notes on several players being split into one entry per player instead of one for the team
- separate batting and bowling tables generating two statistics entries instead of one
- previews of matches not yet played being indexed as results
- generic headlines ("Messrs Fordam's Employees") used as the title instead of the two teams named in the text below

After those fixes, on the same model: coverage rose from 86.1% to 87.4%, exact title matches from 229 to 252, spurious entries fell from 129 to 80, and statistics coverage went from 53.3% to 86.7%.

One problem resisted fixing. Where several short reports share a column and only one gives the day, the others must inherit it. The revised instructions moved the model from confidently wrong to honestly blank — better, but not solved. Worth naming, because some improvements turn wrong answers into gaps rather than into right answers.

## Recommendations

**1. Treat the two jobs differently.** Transcription errors corrupt the record and are hard to spot later, so be conservative there. Indexing errors are more visible and more correctable, so more of it can be automated.

**2. Never rely on one model's transcription.** Since bad output looks good, reading it through is not a real check. Run two or three models and compare. Where they agree, be reasonably confident; where they disagree, look at the scan. This turns "check 247 pages of scorecards" into "check the disagreements", which is actually achievable. The tooling for this already exists in the project.

**3. Ignore the cost.** Transcribing the whole collection with the best model costs about $5. Running three models for cross-checking costs about $15. At that level, price should play no part in the decision — use the best model available, run several, re-run when better ones appear. The real cost is reviewer time, so spend freely on anything that reduces it.

**4. Keep the hand index, but treat it as a benchmark rather than an oracle.** It was indispensable — none of the measurement or diagnosis would have been possible without it. It is also partial, and it contains its own slips: a good number of apparent model errors turned out to be pages it had not covered, or places where the model had read the source correctly and the index had not. Where the two disagree, the scan decides. Growing the verified index over time makes every future comparison more reliable.

**5. Screen any new model on a couple of known pages first.** Look for: fabricated names where the text is unclear (it should say so instead); printed totals silently corrected; difficult surnames; missing innings; stray markup in the output. Two pages was enough to separate eight models.

**6. Do not assume a model badged for OCR is better at OCR.** Two of the worst results came from models marketed for document processing. General-purpose vision models did substantially better on this material.

**7. Expect to redo this.** The best model here was not available when the work started. The screening test is cheap; repeat it occasionally rather than treating today's choice as settled. One practical note: a third-party plugin update silently broke all Anthropic-model support mid-project, so any production pipeline should test against the real libraries rather than stand-ins.

## In short

LLMs can transcribe this material well enough to use — but only some of them, and you cannot tell which by looking at the output. Use several, compare, review the disagreements, and let the scan settle arguments. Indexing is further along: the errors are systematic, fixable, and measurably improving. It is a strong first pass for a human to confirm, not a replacement for the indexer.
