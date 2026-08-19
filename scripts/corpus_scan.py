"""
Experiment 2 -- is Hinglish absent because our filters remove it, or because it
was never crawled?

Classifies documents by script and by romanized-Hindi function-word rate, and
reports the Hinglish share. Run it on BOTH the raw crawl and the cleaned corpus:
if Hinglish is present in raw and missing from clean, the filters are the cause.

    python scripts/corpus_scan.py <file.jsonl> [more.jsonl ...]

Result on the ERA V5 Session 4 corpus (2026-08):
    raw crawl      13 / 13,218 docs = 0.098%
    cleaned         7 / 14,073 docs = 0.050%
Threshold was <1% => it was never crawled. Filters are NOT the cause.
"""
import json, re, sys, glob
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # Windows cp1252 safety
except AttributeError:
    pass

# romanized-Hindi function words with no English collision.
# NOTE: "the" must never be in this list -- it matches every English document.
HINDI_ROMAN = set(
    "hai hain nahi nahin kya aur mein hum tum yeh yah woh bhi karke raha rahi rahe tha thi "
    "kyun kyunki jab tab lekin phir sirf toh bahut accha acha theek thik matlab yaar bhai "
    "abhi kuch kaise kitna chalo dekho hoga hogi karna karta karti liye wala wali".split()
)
SCRIPTS = [("Devanagari", 0x0900, 0x097F), ("Bengali/Assamese", 0x0980, 0x09FF),
           ("Odia", 0x0B00, 0x0B7F), ("Telugu", 0x0C00, 0x0C7F),
           ("Tamil", 0x0B80, 0x0BFF), ("Arabic/Urdu", 0x0600, 0x06FF)]

MIN_HITS, MIN_RATE = 8, 0.02      # thresholds for calling a document Hinglish


def script_counts(text: str) -> Counter:
    c = Counter()
    for ch in text:
        if ch.isascii() and ch.isalpha():
            c["Latin"] += 1
            continue
        o = ord(ch)
        for name, lo, hi in SCRIPTS:
            if lo <= o <= hi:
                c[name] += 1
                break
    return c


def classify(text: str):
    sc = script_counts(text)
    latin = sc["Latin"]
    indic = sum(v for k, v in sc.items() if k != "Latin")
    toks = re.findall(r"[a-z]+", text.lower())
    hits = sum(1 for w in toks if w in HINDI_ROMAN)
    rate = hits / max(len(toks), 1)

    if latin == 0 and indic == 0:
        return "empty", sc, rate
    if indic == 0:
        return ("HINGLISH" if hits >= MIN_HITS and rate >= MIN_RATE
                else "plain Latin"), sc, rate
    if latin == 0:
        return "pure Indic script", sc, rate
    share = latin / (latin + indic)
    if 0.15 < share < 0.85:
        return "CODE-MIXED", sc, rate
    return ("Indic + trace Latin" if share <= 0.15 else "Latin + trace Indic"), sc, rate


def main(paths):
    files = [f for p in paths for f in glob.glob(p)]
    if not files:
        sys.exit(f"no files matched {paths}")
    total, cls, scr, examples = 0, Counter(), Counter(), []
    for path in files:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    text = json.loads(line).get("text", "") or ""
                except json.JSONDecodeError:
                    continue
                total += 1
                label, sc, rate = classify(text)
                cls[label] += 1
                scr += sc
                if label in ("HINGLISH", "CODE-MIXED") and len(examples) < 5:
                    examples.append((path, label, round(rate, 3),
                                     text[:110].replace("\n", " ")))

    print(f"{total:,} documents from {len(files)} file(s)\n")
    chars = sum(scr.values()) or 1
    print("characters by script")
    for k, v in scr.most_common():
        print(f"  {k:20s} {v:12,d}  {v/chars*100:5.1f}%")
    print("\ndocument classification")
    for k, v in cls.most_common():
        print(f"  {v:7,d}  {v/total*100:6.3f}%   {k}")
    print(f"\nHINGLISH share: {cls['HINGLISH']/total*100:.3f}%"
          f"   (<1% => never crawled, not filtered out)")
    if examples:
        print("\nsamples")
        for p, l, r, t in examples:
            print(f"  [{l} rate={r}] {t}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["*.jsonl"])
