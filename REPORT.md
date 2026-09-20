# Lab 01 — The price of one request
**Report**
**Student:** Inamkhodzhayeva Karina 
**Course:** LLMs, Agentic AI and Reinforcement Learning / Narxoz University 
**Date:** 20.09.2026



## 1. Part 1: Predictions vs. Measured Values

### Pre-run Predictions (Intuitive Hypothesis)
*   RU / EN expected token ratio: 1.80x–2.00x
*   KK / EN expected token ratio: 2.00x–2.50x
*   Basis: The prediction was strictly based on the physical byte size of UTF-8 text. Cyrillic letters (both Russian and Kazakh) require 2 bytes per character, while English (ASCII) requires only 1 byte. Since the translated texts have roughly the same number of words, it was expected that their token costs would scale strictly with their physical data footprint (bytes).

### Measured Offline Metrics (part1_offline.py)

| Dataset Item | Language | Characters | Bytes | Words | Bytes / EN Ratio | Bytes / Char |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| SENTENCE | EN <br> RU <br> KK | 69 <br> 75 <br> 72 | 69 <br> 139 <br> 135 | 11 <br> 11 <br> 9 | 1.00x <br> 2.01x <br> 1.96x | 1.00 <br> 1.85 <br> 1.88 |
| COMPLAINT | EN <br> RU <br> KK | 300 <br> 315 <br> 344 | 300 <br> 576 <br> 640 | 54 <br> 45 <br> 42 | 1.00x <br> 1.92x <br> 2.13x | 1.00 <br> 1.83 <br> 1.86 |
| SYSTEM_PROMPT | EN <br> RU <br> KK | 175 <br> 181 <br> 206 | 175 <br> 331 <br> 380 | 34 <br> 27 <br> 28 | 1.00x <br> 1.89x <br> 2.17x | 1.00 <br> 1.83 <br> 1.84 |

### Post-Run Analysis (The Reality Gap in Tokenization)
The execution of part0_tokenizers.py demonstrated that tokenizers do not follow raw physical byte footprints. Instead, efficiency is determined by vocabulary density within the merge-table matrices.

| Tokenizer Model | Metric / Language | English (EN) | Russian (RU) | Kazakh (KK) |
| :--- | :--- | :---: | :---: | :---: |
| o200k_base (Modern) | Token Count <br> Multiplier vs. EN | 59 <br> 1.00x | 80 <br> 1.36x | 118 <br> 2.00x |
| cl100k_base (Legacy) | Token Count <br> Multiplier vs. EN | 59 <br> 1.00x | 146 <br> 2.47x | 265 <br> 4.49x |

Conclusion: My initial byte-centric hypothesis failed when applied to real production models. Russian text gets compressed efficiently by newer architectures. However, Kazakh faces a severe invisible premium under legacy tokenizers (cl100k_base), charging 4.49x more than English for matching semantics due to bad corpus representation during pre-training.

---

## 2. Core Task Extensions & The Kazakh Premium

### Task 1: Custom Corpus Item (my_item)
I added a custom contract clause to texts.py to check tokenization consistency across parallel translations.

| Tokenizer Model | English (EN) Tokens | Russian (RU) Tokens / Ratio | Kazakh (KK) Tokens / Ratio |
| :--- | :---: | :---: | :---: |
| o200k_base | 13 | 16 / 1.23x | 17 / 1.31x |
| cl100k_base | 13 | 30 / 2.31x | 39 / 3.00x |

### Task 2: Locating the Kazakh Premium (kk_common vs kk_special)
I isolated alphabet penalties by comparing Kazakh text lacking national alphabet extensions (kk_common: *"Бул мектеп кешені."*) against proper orthography (kk_special: *"Бұл мектеп кешені."*).

| Test Entry | Data Footprint | o200k_base Tokens | cl100k_base Tokens | Surcharge Impact |
| :--- | :---: | :---: | :---: | :---: |
| KK_COMMON (Shared Cyrillic) | 33 Bytes | 5 | 11 | Baseline |
| KK_SPECIAL (Native Kazakh) | 33 Bytes | 5 | 12 | +9% Token Surge |

Insight: The financial penalty for Kazakh does not stem from the alphabet or UTF-8 encoding. It exists entirely inside the tokenizer's merge tables, where native letters like *ә, ғ, қ, ң, ө, ұ, ү, і* are heavily penalized by older architectures due to their underrepresentation in the original training corpus. Merely introducing a single native letter (ұ) causes legacy tokenizers to break the byte sequence into fragments.

---

## 3. Financial Analysis (Annual Cost Tables)

I projected the annual API expenditures for a customer support queue processing 2,000 requests per day (730,000 requests/year), which simulates a mid-sized regional e-commerce or digital banking support system in Kazakhstan.

### Annual Bill Table (USD / Year)

| Model Architecture | English (EN) | Russian (RU) | Kazakh (KK) |
| :--- | :---: | :---: | :---: |
| haiku-4.5 | \$3,592 | \$4,627 | \$5,111 |
| sonnet-5 | \$7,183 | \$9,255 | \$10,223 |
| opus-5 | \$17,958 | \$23,137 | \$25,557 |
| fable-5.1 | \$35,916 | \$46,275 | \$51,115 |

### The Tokenizer vs. The Bill Distortion
Public discussions often confuse the Input Token Ratio with the Total Bill Ratio. As measured on opus-5:
| Metric Type | English (EN) | Russian (RU) | Kazakh (KK) | Cost Impact Vector |
| :--- | :---: | :---: | :---: | :--- |
| Input Only Ratio | 1.00x | 1.44x | 2.19x | Tokenizer structural property |
| Total Bill Ratio | 1.00x | 1.29x | 1.42x | Actual invoiced premium |

Why they differ: Output tokens are priced significantly higher than input tokens. Because the generated answers (output length) stabilize across languages, the extreme input token penalty of Kazakh (2.19x) gets diluted in the total bill, resulting in a lower real-world cost premium of 1.42x. However, the financial impact remains substantial: running a Kazakh queue instead of English costs \$7,599/year more for the exact same volume on opus-5.

---

## 4. Production Recommendation for Kazakh Support

### Recommended Model: sonnet-5

I evaluated the models based on a strict price-to-performance matrix:
1.  The Quality Threshold: Live customer support requires strict adherence to system prompt constraints (e.g., refusing to hallucinate reasons if data is missing, matching the customer's language natively). While haiku-4.5 is highly cost-effective, smaller models struggle with advanced contextual constraints and native Kazakh grammar. sonnet-5 provides flagship reasoning capabilities required for deterministic enterprise tasks.
2.  The Cost Trade-off: opus-5 is economically unviable for a standard support queue, costing \$25,557/year for Kazakh. sonnet-5 drops this cost down to \$10,223/year—saving over 60% of the budget while mitigating the structural Kazakh token premium compared to older-generation deployments.

---

## 5. Cost Optimization Levers

One major cost lever not utilized in this lab: Prompt Caching.  
Since the system_prompt remains identical across thousands of incoming user requests, caching the system prompt tokens after the first call allows subsequent requests to read from the cache at a fraction of the cost (~10% of the standard input price). This approach significantly slashes the running overhead of the language input premium.