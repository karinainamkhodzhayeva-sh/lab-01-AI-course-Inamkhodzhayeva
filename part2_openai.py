"""Part 2 (OpenAI variant) -- the measurement. Needs an OpenAI API key for --call.
 
Mirrors part2_measure.py, but for an OpenAI model instead of Claude:
 
1. Token counts for every text in :mod:`texts`, in every language, using
   tiktoken (offline, free, no key needed). OpenAI has no free ``count_tokens``
   endpoint like Anthropic's, so this is the closest equivalent. The encoding
   used here is an assumption (see ENCODING_NAME); the authoritative number is
   always the ``prompt_tokens`` the API bills, which step 2 records.
2. With --call: one real request per language (system prompt + complaint), so
   you see the answer and the ``usage`` block. Three calls, because answer
   length is itself language-dependent. This is the only part that spends money.
   Output tokens INCLUDE hidden reasoning tokens (billed, never shown).
 
Prices are NOT hardcoded (they change). Copy them by hand from OpenAI's official
pricing page and pass them with --price-in / --price-out (USD per 1M tokens).
 
Results are written to measurements-openai-<model>.json.
 
Run:
    python part2_openai.py --model <model-id>           # count tokens only, free
    python part2_openai.py --model <model-id> --call    # also answer in en, ru, kk
    python part2_openai.py --model <model-id> --call --price-in <IN> --price-out <OUT>
"""
 
from __future__ import annotations
 
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional
 
import openai
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI
 
from texts import CORPUS, LANGUAGES
 
# Kazakh letters do not exist in the Windows cp1251 console encoding.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
 
#: Loads OPENAI_API_KEY from a .env file next to this script, if present.
load_dotenv()
 
#: Assumption: recent OpenAI models use o200k_base. Verify if it matters; the
#: billed prompt_tokens from --call is the number that counts.
ENCODING_NAME = "o200k_base"
 
#: Cap for output INCLUDING hidden reasoning tokens. Too small a cap makes a
#: reasoning model spend everything on thinking and return an empty/cut answer
#: (finish_reason == "length"), which makes the measurement unusable.
DEFAULT_MAX_COMPLETION_TOKENS = 4096
 
 
def count_corpus(encoding: tiktoken.Encoding) -> Dict[str, Dict[str, int]]:
    """Count tokens for every corpus item in every language (offline)."""
    return {
        item_id: {lang: len(encoding.encode(versions[lang])) for lang in LANGUAGES}
        for item_id, versions in CORPUS.items()
    }
 
 
def one_real_request(
    client: OpenAI, model: str, lang: str, max_completion_tokens: int
) -> Optional[Dict[str, object]]:
    """Send one request (system prompt + complaint) and return billed usage.
 
    Returns:
        A mapping with input/output/reasoning token counts, finish_reason and the
        answer text, or ``None`` if the model refused to answer.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": CORPUS["system_prompt"][lang]},
            {"role": "user", "content": CORPUS["complaint"][lang]},
        ],
        max_completion_tokens=max_completion_tokens,
    )
    choice = response.choices[0]
 
    if getattr(choice.message, "refusal", None):
        print(f"  model declined: {choice.message.refusal}")
        return None
 
    usage = response.usage
    details = getattr(usage, "completion_tokens_details", None)
    reasoning = (getattr(details, "reasoning_tokens", 0) or 0) if details else 0
 
    print(f"  finish_reason: {choice.finish_reason}")
    print("  --- answer ---")
    print("  " + (choice.message.content or "").replace("\n", "\n  "))
    print(f"  billed: {usage.prompt_tokens} in, {usage.completion_tokens} out "
          f"(of which {reasoning} hidden reasoning)")
    if choice.finish_reason == "length":
        print(f"  NOTE: answer was cut off at max_completion_tokens={max_completion_tokens}. "
              "This measurement is unusable -- rerun with a larger --max-completion-tokens.")
 
    return {
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,  # includes hidden reasoning tokens
        "reasoning_tokens": reasoning,
        "finish_reason": choice.finish_reason,
        "answer": choice.message.content,
    }
 
 
def print_costs(billed: Dict[str, Dict[str, object]], price_in: float,
                price_out: float, requests_per_day: int) -> None:
    """Print per-request and annual cost plus the two ratios that get confused."""
    per_request = {
        lang: (billed[lang]["input_tokens"] * price_in
               + billed[lang]["output_tokens"] * price_out) / 1_000_000
        for lang in LANGUAGES
    }
    print(f"\nCOST in USD at {price_in}/1M input, {price_out}/1M output")
    print(f"{'':<26}" + "".join(f"{lang.upper():>12}" for lang in LANGUAGES))
    print(f"{'per request':<26}" + "".join(f"{per_request[l]:>12.5f}" for l in LANGUAGES))
    label = f"per year @ {requests_per_day}/day"
    print(f"{label:<26}" + "".join(
        f"{per_request[l] * requests_per_day * 365:>12,.0f}" for l in LANGUAGES))
 
    print("\nTWO RATIOS THAT ARE NOT THE SAME NUMBER")
    base_in = billed["en"]["input_tokens"]
    print(f"{'input only':<26}" + "".join(
        f"{billed[l]['input_tokens'] / base_in:>11.2f}x" for l in LANGUAGES))
    print(f"{'total bill':<26}" + "".join(
        f"{per_request[l] / per_request['en']:>11.2f}x" for l in LANGUAGES))
 
 
def main() -> int:
    """Count tokens for the whole corpus, optionally make real requests."""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", required=True,
                        help="OpenAI model id, exactly as on the official models page")
    parser.add_argument("--call", action="store_true",
                        help="also answer the complaint in each language (this costs money)")
    parser.add_argument("--max-completion-tokens", type=int,
                        default=DEFAULT_MAX_COMPLETION_TOKENS)
    parser.add_argument("--price-in", type=float, help="USD per 1M input tokens")
    parser.add_argument("--price-out", type=float, help="USD per 1M output tokens")
    parser.add_argument("--requests-per-day", type=int, default=2000)
    args = parser.parse_args()
 
    print(f"counting tokens offline with tiktoken {ENCODING_NAME} (free, no model run)")
    encoding = tiktoken.get_encoding(ENCODING_NAME)
    counts = count_corpus(encoding)
    for item_id, per_lang in counts.items():
        row = "  ".join(f"{lang}={per_lang[lang]}" for lang in LANGUAGES)
        print(f"  {item_id:<16} {row}")
 
    billed: Dict[str, Dict[str, object]] = {}
    if args.call:
        try:
            client = OpenAI()
        except openai.OpenAIError as exc:
            print(f"could not build a client: {exc}", file=sys.stderr)
            print("add  OPENAI_API_KEY=sk-...  to your .env file.", file=sys.stderr)
            return 1
 
        print(f"\nanswering the same complaint on {args.model}, in each language:")
        for lang in LANGUAGES:
            print(f"\n[{lang}]")
            try:
                result = one_real_request(client, args.model, lang, args.max_completion_tokens)
            except openai.RateLimitError as exc:
                print(f"rate limited or out of credit: {exc}", file=sys.stderr)
                return 1
            except openai.APIStatusError as exc:
                print(f"API error {exc.status_code}: {exc}", file=sys.stderr)
                return 1
            except openai.APIConnectionError as exc:
                print(f"could not reach the API: {exc}", file=sys.stderr)
                return 1
            if result is not None:
                billed[lang] = result
 
        if len(billed) == len(LANGUAGES):
            if args.price_in is not None and args.price_out is not None:
                print_costs(billed, args.price_in, args.price_out, args.requests_per_day)
            else:
                print("\nNo prices given, so no cost table. "
                      "Add --price-in and --price-out (USD per 1M tokens).")
        else:
            print("\nNot every language produced an answer, so no cost table.")
 
    safe_name = args.model.replace("/", "_").replace(":", "_")
    output_path = Path(__file__).with_name(f"measurements-openai-{safe_name}.json")
    payload = {
        "model": args.model,
        "tokenizer_used_for_token_counts": ENCODING_NAME,
        "token_counts": counts,
        "request_tokens": {l: billed[l]["input_tokens"] for l in billed} or None,
        "one_request_billed": billed or None,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                           encoding="utf-8")
    print(f"\nwrote {output_path.name}")
    return 0
 
 
if __name__ == "__main__":
    sys.exit(main())
 