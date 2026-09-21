# Lab 01 — The price of one request
**Report**
**Student:** Inamkhodzhayeva Karina 
**Course:** LLMs, Agentic AI and Reinforcement Learning / Narxoz University 
**Date:** 20.09.2026

 
---
 
> **Data note.** Parts 0, 1 and 3 were run locally. Part 2 was run with OpenAI models (`gpt-5.6-luna` and `gpt-5.6-terra`) using my own script `part2_openai.py`, because I had no Anthropic API key. The Claude cost figures in Part 3 therefore come from the reference run shipped with the lab (`measurements.example.json`, dated 2026-09-12), while the OpenAI figures are my own measurements. The two sets are **not directly comparable**: different models, tokenizers, prices and answer lengths.
 
---
 
## 1. Part 1: Prediction vs. Measured Value
 
### Prediction (written before any token count)
 
*   RU / EN expected token ratio: **1.80x–2.00x**
*   KK / EN expected token ratio: **2.00x–2.50x**
*   Basis: UTF-8 byte size. Cyrillic letters take 2 bytes, English (ASCII) takes 1 byte, and the translations have roughly the same number of words, so I expected token cost to scale with bytes.
### Prediction vs. measured (COMPLAINT text)
 
| Ratio vs. EN | My prediction | Bytes (Part 1) | o200k_base | cl100k_base | Claude request* | gpt-5.6 request** |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| RU / EN | 1.80x–2.00x | 1.92x | 1.36x | 2.47x | 1.44x | 1.28x |
| KK / EN | 2.00x–2.50x | 2.13x | 2.00x | 4.49x | 2.19x | 1.79x |
 
\*Claude request = system prompt + complaint counted together on claude-opus-5 (reference run: EN 145, RU 209, KK 317 tokens).
\*\*gpt-5.6 request = system prompt + complaint, as billed by the API in my own Part 2 run (EN 109, RU 139, KK 195 input tokens). Each request includes 10 fixed framing tokens (the plain texts count 99 / 129 / 185), which pulls the ratios toward 1.
 
**Reading the result.** The Kazakh prediction was correct for bytes (2.13x), o200k_base (2.00x, lower edge of my range) and Claude (2.19x), but too low for the legacy cl100k_base (4.49x). On the gpt-5.6 request the Kazakh ratio (1.79x) is below my range, because a request contains the system prompt (whose KK ratio is only 1.68x) and a fixed framing overhead that is the same in every language. The Russian prediction was too high for all modern tokenizers (1.28x–1.44x): they compress Cyrillic far better than raw bytes suggest. Only cl100k_base (2.47x) exceeds my range.
 
### Measured offline metrics (part1_offline.py)
 
| Item | EN bytes | RU bytes (÷EN) | KK bytes (÷EN) | Bytes/char EN / RU / KK |
| :--- | :---: | :---: | :---: | :---: |
| SENTENCE | 69 | 139 (2.01x) | 135 (1.96x) | 1.00 / 1.85 / 1.88 |
| COMPLAINT | 300 | 576 (1.92x) | 640 (2.13x) | 1.00 / 1.83 / 1.86 |
| SYSTEM_PROMPT | 175 | 331 (1.89x) | 380 (2.17x) | 1.00 / 1.83 / 1.84 |
| MY_ITEM | 251 | 443 (1.76x) | 420 (1.67x) | 1.00 / 1.86 / 1.84 |
 
### Measured tokens (part0_tokenizers.py)
 
| Item | Tokenizer | EN | RU (÷EN) | KK (÷EN) |
| :--- | :--- | :---: | :---: | :---: |
| SENTENCE | o200k_base | 12 | 18 (1.50x) | 21 (1.75x) |
| SENTENCE | cl100k_base | 12 | 35 (2.92x) | 58 (4.83x) |
| COMPLAINT | o200k_base | 59 | 80 (1.36x) | 118 (2.00x) |
| COMPLAINT | cl100k_base | 59 | 146 (2.47x) | 265 (4.49x) |
| SYSTEM_PROMPT | o200k_base | 40 | 49 (1.23x) | 67 (1.68x) |
| SYSTEM_PROMPT | cl100k_base | 40 | 77 (1.93x) | 157 (3.92x) |
 
**Conclusion.** Token cost does not follow byte size. On the modern tokenizer Russian costs only 1.2x–1.5x English, less than its 1.8x–2.0x byte footprint. On the legacy tokenizer Kazakh costs 3.9x–4.8x English, roughly double its byte ratio (1.96x–2.17x). The Kazakh premium lives in the tokenizer's merge table, not in the amount of data.
 
---
 
## 2. Annual Cost Table
 
**Volume:** 2,000 requests/day (730,000 requests/year), a plausible load for the support queue of a mid-sized regional bank or e-commerce company in Kazakhstan.
 
**Price sources.**
*   Claude: the list prices recorded in `prices.py` (Anthropic's public model documentation, `platform.claude.com/docs/en/about-claude/models/overview`), checked 2026-09-12. The script only prints this source as a citation; it does not fetch anything from the internet.
*   OpenAI: the Standard, short-context prices on `developers.openai.com/api/docs/pricing`, checked 21.09.2026. gpt-5.6-luna: \$0.20 input / \$1.20 output per 1M tokens; gpt-5.6-terra: \$2.00 input / \$12.00 output per 1M tokens.
### 2a. Claude models (reference run, `--requests-per-day 2000`), USD / year
 
| Model | English (EN) | Russian (RU) | Kazakh (KK) |
| :--- | :---: | :---: | :---: |
| haiku-4.5 | \$3,592 | \$4,627 | \$5,111 |
| sonnet-5 | \$7,183 | \$9,255 | \$10,223 |
| opus-5 | \$17,958 | \$23,137 | \$25,557 |
| fable-5.1 | \$35,916 | \$46,275 | \$51,115 |
 
### 2b. OpenAI models (my own Part 2 measurements), USD / year
 
| Model | English (EN) | Russian (RU) | Kazakh (KK) |
| :--- | :---: | :---: | :---: |
| gpt-5.6-luna | \$121 | \$136 | \$232 |
| gpt-5.6-terra | \$1,044 | \$1,070 | \$1,826 |
 
### Two ratios that are not the same number
 
| Metric | Model | EN | RU | KK | Meaning |
| :--- | :--- | :---: | :---: | :---: | :--- |
| Input tokens only | opus-5 (reference) | 1.00x | 1.44x | 2.19x | Property of the tokenizer |
| Total bill | opus-5 (reference) | 1.00x | 1.29x | 1.42x | What is actually invoiced |
| Input tokens only | gpt-5.6 (measured) | 1.00x | 1.28x | 1.79x | Property of the tokenizer |
| Total bill | gpt-5.6-luna (measured) | 1.00x | 1.12x | 1.91x | What is actually invoiced |
| Total bill | gpt-5.6-terra (measured) | 1.00x | 1.03x | 1.75x | What is actually invoiced |
 
**Why they differ.** Output tokens are priced several times higher than input tokens and there are more of them, so output dominates the bill: about 95–97% on opus-5 (reference run: 955 / 1,226 / 1,337 output tokens for EN / RU / KK) and about 85–88% in my OpenAI runs. The input premium is therefore diluted, and the *length of the answer* decides the total-bill ratio. On opus-5 the Kazakh answer was 1.40x the English one and this longer output, not the input, causes about 92% of the extra cost per KK request; running the Kazakh queue instead of English costs \$7,599/year more (1.42x). In my OpenAI runs the Kazakh answer was 1.93x (luna: 232 vs. 120 tokens) and 1.74x (terra: 176 vs. 101 tokens) as long as the English one, so the KK total-bill ratio (1.91x and 1.75x) is above the input ratio (1.79x) on luna and just below it on terra. For Russian the answers were about as long as the English ones, so the RU bill barely moves (1.12x and 1.03x) despite a 1.28x input premium. Output tokens also include hidden reasoning tokens (19–51 per answer in my runs), which are billed but never shown. *Caveat:* each language was measured once, and the Kazakh answers also contain extra sentences, so answer length is noisy; I read it as an observation, not as a law.
 
---
 
## 3. Production Model for a Kazakh-language Support Queue
 
**Recommendation: gpt-5.6-luna among the models I measured; for the Claude models priced in this lab, haiku-4.5 would be the analogous first candidate (its quality was not measured).**
 
**Cost.** For Kazakh at 2,000 requests/day, luna costs \$232/year and terra \$1,826/year, so terra is about 7.9x more expensive (10x the price per token, partly offset by its shorter answers).
 
**Quality.** I read all six answers (2 models x 3 languages) against four simple criteria: the answer must decline to explain the rate change instead of inventing a cause (the complaint claims attachments, but nothing is attached), invent no numbers that are not in the complaint, stay entirely in the customer's language, and name a concrete next step. Both models met all four criteria in all three languages: each noticed that no documents were attached, refused to judge the rate change and asked the customer to send the contract and statement again. The only difference is that the luna Kazakh answer adds a promise that the application will be handled "in the established order", which the provided information does not support; terra stayed strictly within the documents. So on this test the more expensive model bought no measurable quality, and the cheaper model is the rational default. It should be replaced by terra only if a larger test set shows failures.
 
**Claude family.** The Part 3 bills for Claude models are priced, but their quality was not measured, so I make no claim about it. luna's Kazakh bill (\$232/year) is far below even haiku-4.5's reference-run bill (\$5,111/year), but those numbers come from different runs, tokenizers and answer lengths and are not a like-for-like comparison.
 
**Limits of the evidence.** Six answers, one complaint, one run per language. The test checks constraint-following (declining when the attachment is missing), not general Kazakh fluency or multi-turn dialogue. The Kazakh answers were not reviewed by a native speaker.
 
---
 
## 4. A Cost Lever This Lab Did Not Use
 
**Prompt caching of the system prompt**, which is identical in every request and is read from cache at about 10% of the normal input price. A back-of-envelope estimate (Kazakh system prompt = 124 of 317 input tokens, opus-5) gives only about \$407/year saved (1.6% of \$25,557), because about 95% of the bill is output. Shortening the answers is therefore the larger lever. The estimate ignores the one-time cache-write cost and any minimum cacheable prompt length, which I did not verify; since my requests are only about 110–320 tokens long, caching may not even apply to them.
 
---
 
## Appendix A: Core Task Extensions
 
### Task 1: Custom corpus item (`my_item`)
 
A three-sentence contract clause (validity period, rate-change notice, early termination), written in parallel in EN / RU / KK.
 
| Tokenizer | EN tokens | RU tokens / ratio | KK tokens / ratio |
| :--- | :---: | :---: | :---: |
| o200k_base | 45 | 54 / 1.20x | 65 / 1.44x |
| cl100k_base | 45 | 101 / 2.24x | 162 / 3.60x |
 
The Kazakh ratios fall inside the lab's expected bands (o200k ≈1.4x–2.0x, cl100k ≈2.5x–4.5x). The Russian ratios are slightly below them, consistent with Cyrillic being compressed well by both tokenizers.
 
### Task 2: Locating the Kazakh premium (`kk_common` vs. `kk_special`)
 
Two Kazakh sentences of six words each. `kk_common` uses only letters shared with Russian ("Мен мектепке барамын, ол да барады."). `kk_special` is dense with Kazakh-only letters ("Ұлы даладағы әдемі қала көңілді қуантты.").
 
| Entry | Chars | Bytes | Bytes/char | o200k tokens | cl100k tokens |
| :--- | :---: | :---: | :---: | :---: | :---: |
| kk_common | 35 | 63 | 1.80 | 11 | 20 |
| kk_special | 40 | 74 | 1.85 | 14 | 38 |
 
Bytes per character are nearly identical (1.80 vs. 1.85), yet on cl100k_base the token count almost doubles (+90%), while on o200k_base it grows only +27%. The Kazakh-specific letters are what the legacy merge table handles badly. Bytes per character cannot see this at all. *Caveat:* the two sentences differ slightly in length (35 vs. 40 characters), so I compare tokens per word, not only totals.
 
### Task 3: Prose vs. JSON
 
The `complaint` text was re-expressed as a JSON object with the same five sentences split across fields (`greeting`, `history`, `issue`, `attachments`, `request`). Field names stay in English for all languages.
 
| Tokenizer | Language | Prose tokens | JSON tokens | Increase (tokens) | Increase (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| o200k_base | EN | 59 | 81 | +22 | +37.3% |
| o200k_base | RU | 80 | 102 | +22 | +27.5% |
| o200k_base | KK | 118 | 140 | +22 | +18.6% |
| cl100k_base | EN | 59 | 81 | +22 | +37.3% |
| cl100k_base | RU | 146 | 167 | +21 | +14.4% |
| cl100k_base | KK | 265 | 287 | +22 | +8.3% |
 
Prediction: not recorded before the run; the lab's expected direction is that JSON costs more in every language.
 
Part 1 confirms this at the byte level: the JSON version is exactly 74 bytes longer than the prose in every language (EN 300 → 374, RU 576 → 650, KK 640 → 714), all of it ASCII braces, quotes, colons and field names.
 
**Result.** JSON costs more in every language and on both tokenizers, so the direction was as expected. The absolute overhead is almost constant: +22 tokens everywhere (+21 for RU on cl100k_base). The braces, quotes and English field names stay ASCII no matter what language the values are in, so their token cost does not depend on the language. The percentage increase is largest for English (+37.3%) and smallest for Kazakh (+8.3% on cl100k_base) only because English starts from the smallest base: 22 tokens on top of 59 is proportionally much more than 22 on top of 265. A "smaller relative increase" for Kazakh is therefore a division artifact, not a cheaper format. Percentages are compared only after checking the absolute counts.
 
---
 
## Appendix B: Part 2 Measurements with OpenAI Models
 
Script: `part2_openai.py` (same structure as the lab's `part2_measure.py`). It sends one real request per language (system prompt + complaint) and records the usage that the API bills. Output files: `measurements-openai-gpt-5.6-luna.json` and `measurements-openai-gpt-5.6-terra.json`.
 
| Model | Lang | Input tokens | Output tokens | of which hidden reasoning | finish_reason | Cost per request (USD) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| gpt-5.6-luna | EN | 109 | 120 | 29 | stop | 0.00017 |
| gpt-5.6-luna | RU | 139 | 132 | 30 | stop | 0.00019 |
| gpt-5.6-luna | KK | 195 | 232 | 51 | stop | 0.00032 |
| gpt-5.6-terra | EN | 109 | 101 | 27 | stop | 0.00143 |
| gpt-5.6-terra | RU | 139 | 99 | 19 | stop | 0.00147 |
| gpt-5.6-terra | KK | 195 | 176 | 35 | stop | 0.00250 |
 
All six answers ended with `finish_reason: stop`, so none was cut off. The billed input of each request equals the offline count of system prompt + complaint plus exactly 10 tokens (99 → 109, 129 → 139, 185 → 195), which is the per-request message framing and confirms that summing standalone counts would double-count it.
 
