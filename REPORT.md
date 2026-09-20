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

### Post-run Analysis (The Reality Gap)
When measuring actual tokens across different tokenizers (part0_tokenizers.py), the initial hypothesis was broken due to tokenizer merge-table efficiency:

*   Measured Ratios (COMPLAINT item):
    *   o200k_base (Modern): RU/EN = 1.36x | KK/EN = 2.00x
    *   cl100k_base (Legacy): RU/EN = 2.47x | KK/EN = 4.49x

Conclusion: Tokenizers do not follow raw bytes. While Russian text is compressed efficiently by newer models, Kazakh suffers an "invisible premium" on older tokenizers (cl100k_base), making it 4.49x more expensive than English for the exact same semantic content, despite having a similar byte size.

---

## 2. Core Task Extensions & The Kazakh Premium

### Task 1: Custom Corpus Item (my_item)
A custom contract clause was added to texts.py to check tokenization consistency:
*   o200k_base: RU/EN = 1.23x | KK/EN = 1.31x
*   cl100k_base: RU/EN = 2.31x | KK/EN = 3.00x

### Task 2: Locating the Kazakh Premium (kk_common vs kk_special)
To isolate what causes the Kazakh cost overhead, we compared a text written with shared Cyrillic characters (kk_common: *"Бул мектеп кешені."*) against the correct spelling with native Kazakh letters (kk_special: *"Бұл мектеп кешені."*).

*   Physical properties (Part 1): Both strings are identical (18 chars, 33 bytes, 1.83 bytes/char).
*   Token counts (Part 0): 
    *   o200k_base: Both strings cost 5 tokens (0% increase).
    *   cl100k_base: kk_common costs 11 tokens, while kk_special costs 12 tokens (+9% increase for a single character "ұ").

Insight: The financial penalty for Kazakh does not stem from the alphabet or UTF-8 encoding. It exists entirely inside the tokenizer's merge tables, where native letters like *ә, ғ, қ, ң, ө, ұ, ү, і* are heavily penalized by older architectures due to their underrepresentation in the original training corpus.

---

## 3. Financial Analysis (Annual Cost Tables)

We project the annual API expenditures for a customer support queue processing 2,000 requests per day (justified as a mid-sized regional e-commerce or digital banking support system in Kazakhstan).

### Annual Bill Table (USD / Year)

| Model Architecture | English (EN) | Russian (RU) | Kazakh (KK) |
| :--- | :--- | :--- | :--- |
| haiku-4.5 | \$3,592 | \$4,627 | \$5,111 |
| sonnet-5 | \$7,183 | \$9,255 | \$10,223 |
| opus-5 | \$17,958 | \$23,137 | \$25,557 |
| fable-5.1 | \$35,916 | \$46,275 | \$51,115 |

### The Tokenizer vs. The Bill Distortion
Public discussions often confuse the Input Token Ratio with the Total Bill Ratio. As measured on opus-5:
*   Input Only Ratio (Tokenizer property): RU = 1.44x | KK = 2.19x
*   Total Bill Ratio (Actual cost multiplier): RU = 1.29x | KK = 1.42x

Why they differ: Output tokens are priced significantly higher than input tokens. Because the generated answers (output length) stabilize across languages, the extreme input token penalty of Kazakh (2.19x) gets diluted in the total bill, resulting in a lower real-world cost premium of 1.42x. 
*   *Financial impact on opus-5:* Running a Kazakh queue instead of English costs \$7,599/year more for the exact same volume.

## 4. Production Recommendation for Kazakh Support

Recommended Model: sonnet-5

### Cost & Quality Argument
1.  The Quality Threshold: Live customer support requires strict adherence to system prompt constraints (e.g., refusing to hallucinate reasons if data is missing, matching the customer's language natively). While haiku-4.5 is highly cost-effective, smaller models struggle with advanced contextual constraints and native Kazakh grammar. sonnet-5 provides near-旗舰 quality, matching the reasoning skills required for deterministic enterprise tasks.
2.  The Cost Trade-off: opus-5 is economically unviable for a standard support queue, costing \$25,557/year for Kazakh. sonnet-5 drops this cost down to \$10,223/year—saving over 60% of the budget while mitigating the structural Kazakh token premium compared to older-generation deployments.

---

## 5. Cost Optimization Levers
One major cost lever not utilized in this lab: Prompt Caching.  
Since the system_prompt remains identical across thousands of incoming user metadata structures, caching the system prompt tokens after the first call allows subsequent requests to read from the cache at a fraction of the cost (~10% of the standard input price), significantly slashing the running overhead of the input premium.