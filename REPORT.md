# Lab 01 — The price of one request
**Report**
**Student:** Inamkhodzhayeva Karina 
**Course:** LLMs, Agentic AI and Reinforcement Learning / Narxoz University 
**Date:** 20.09.2026


---
> **Data note.** Parts 0, 1 and 3 were run locally. Part 2 (live Claude API calls) was **not** run because no Anthropic API key was available. All Part 3 cost figures therefore use the reference run shipped with the lab (`measurements.example.json`, dated 2026-09-12), not my own measurements.
 
---
 
## 1. Part 1: Prediction vs. Measured Value
 
### Prediction (written before any token count)
 
*   RU / EN expected token ratio: **1.80x–2.00x**
*   KK / EN expected token ratio: **2.00x–2.50x**
*   Basis: UTF-8 byte size. Cyrillic letters take 2 bytes, English (ASCII) takes 1 byte, and the translations have roughly the same number of words, so I expected token cost to scale with bytes.
### Prediction vs. measured (COMPLAINT text)
 
| Ratio vs. EN | My prediction | Bytes (Part 1) | o200k_base | cl100k_base | Claude request* |
| :--- | :---: | :---: | :---: | :---: | :---: |
| RU / EN | 1.80x–2.00x | 1.92x | 1.36x | 2.47x | 1.44x |
| KK / EN | 2.00x–2.50x | 2.13x | 2.00x | 4.49x | 2.19x |
 
\*Claude request = system prompt + complaint counted together on claude-opus-5 (reference run: EN 145, RU 209, KK 317 tokens).
 
**Reading the result.** The Kazakh prediction was correct for bytes (2.13x), o200k_base (2.00x, lower edge of my range) and Claude (2.19x), but too low for the legacy cl100k_base (4.49x). The Russian prediction was too high for modern tokenizers (1.36x–1.44x): they compress Cyrillic far better than raw bytes suggest. Only cl100k_base (2.47x) exceeds my range.
 
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
 
**Price source.** List prices are the ones recorded in `prices.py`: Anthropic's public model documentation (`platform.claude.com/docs/en/about-claude/models/overview`), checked 2026-09-12. The script only prints this source as a citation; it does not fetch anything from the internet.
 
### Annual bill (USD / year, reference run, `--requests-per-day 2000`)
 
| Model | English (EN) | Russian (RU) | Kazakh (KK) |
| :--- | :---: | :---: | :---: |
| haiku-4.5 | \$3,592 | \$4,627 | \$5,111 |
| sonnet-5 | \$7,183 | \$9,255 | \$10,223 |
| opus-5 | \$17,958 | \$23,137 | \$25,557 |
| fable-5.1 | \$35,916 | \$46,275 | \$51,115 |
 
### Two ratios that are not the same number (opus-5)
 
| Metric | EN | RU | KK | Meaning |
| :--- | :---: | :---: | :---: | :--- |
| Input tokens only | 1.00x | 1.44x | 2.19x | Property of the tokenizer |
| Total bill | 1.00x | 1.29x | 1.42x | What is actually invoiced |
 
**Why they differ.** Output tokens are priced 5x higher than input tokens and there are far more of them (reference run: 955 / 1,226 / 1,337 output tokens for EN / RU / KK), so output makes up about 95–97% of every bill. The large input premium is therefore diluted. The answers themselves are also longer in Kazakh (1.40x the English answer), and this longer output, not the input, causes about 92% of the extra cost per KK request. Running the Kazakh queue instead of English costs **\$7,599/year more** on opus-5 (1.42x). Output tokens include hidden thinking tokens, which are billed but never shown.
 
---
 
## 3. Production Model for a Kazakh-language Support Queue
 
**Recommendation: sonnet-5 as the default, with haiku-4.5 as the candidate to switch to after a quality test.**
 
*   **Cost.** For Kazakh, sonnet-5 costs \$10,223/year, which is \$15,334 less than opus-5 (\$25,557). haiku-4.5 costs \$5,111, another \$5,112 less than sonnet-5. haiku-4.5's list price is exactly 1/5 of opus-5's.
*   **Quality: not measured in this lab.** Without an API key I could not collect real answers, so I make no claim about which model writes better Kazakh. The corpus, however, contains a built-in trap: the complaint says the contract is attached, but nothing is attached, and the system prompt says to answer only from provided documents. This tests whether the model follows a simple constraint, which does not automatically require the most expensive model.
*   **Checklist prepared before any run** (`CHECKLIST.md`): a passing answer (1) declines to explain the rate change instead of inventing a cause, (2) invents no number that is not in the complaint, (3) answers entirely in the customer's language, (4) names a concrete next step.
*   **Plan.** Run haiku-4.5 and sonnet-5 on all three languages (6 answers each) against this checklist. If haiku-4.5 passes all Kazakh answers, switch to it. Otherwise stay on sonnet-5. A cost argument alone does not answer the question; the quality argument has to be measured.
---
 
## 4. A Cost Lever This Lab Did Not Use
 
**Prompt caching of the system prompt**, which is identical in every request and is read from cache at about 10% of the normal input price. A back-of-envelope estimate (Kazakh system prompt = 124 of 317 input tokens, opus-5) gives only about \$407/year saved (1.6% of \$25,557), because about 95% of the bill is output. Shortening the answers is therefore the larger lever. The estimate ignores the one-time cache-write cost and any minimum cacheable prompt length, which I did not verify.
 
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