"""
Build data/stories.jsonl from Project Gutenberg story collections.

Two ways to find story boundaries:
  --toc              read titles from the book's "Contents" list (Roman-numeral entries),
                     then locate each title as a standalone line in the body
  --heading REGEX    treat every line matching REGEX as a story title

Re-running for the same --prefix replaces that book's stories, so it is safe to repeat.
Without --write it only previews.
"""
import re, json, argparse, os
import difflib

START = re.compile(r"\*\*\*\s*START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*")
END = re.compile(r"\*\*\*\s*END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK")
ROMAN = re.compile(r"^\s*(?:[IVXLC]+|\d+)\.?\s+(.*\S)\s*$")
PAGE_TAIL = re.compile(r"\s{2,}\d+\s*$")


def strip_gutenberg(text):
    m = START.search(text)
    if m:
        text = text[m.end():]
    m = END.search(text)
    if m:
        text = text[:m.start()]
    return text.replace("\r\n", "\n").strip()


def norm(s):
    s = s.replace("\u2019", "'").replace("\u2018", "'").replace("_", "")
    s = re.sub(r"\[\d+\]", "", s)   # footnote markers like [21]
    return re.sub(r"\s+", " ", s).strip().rstrip(".").lower()

def parse_toc(lines, marker="contents", no_pages=False):
    """Return (titles, index of last contents line)."""
    start = next((i for i, l in enumerate(lines) if l.strip().lower() == marker), None)
    if start is None:
        raise SystemExit(f'No line equal to "{marker}" found. Use --toc-marker or --heading.')
    titles, i = [], start + 1
    while i < len(lines):
        line = lines[i]
        m = ROMAN.match(line)
        if m:
            rest = m.group(1)
            # title continues on following lines until one ends with a page number
            if not no_pages:
                while not PAGE_TAIL.search(rest) and i + 1 < len(lines):
                    i += 1
                    if lines[i].strip():
                        rest += " " + lines[i].strip()
            titles.append(PAGE_TAIL.sub("", rest).strip())
        elif line.strip():
            if PAGE_TAIL.search(line):
                pass          # unnumbered entry with a page number (nested tale, "Notes 290"): skip it
            elif titles:
                break         # first real non-entry line after the list (e.g. "INTRODUCTION.")
        i += 1
    return titles, i

def parse_toc_plain(lines, marker="contents", skip=()):
    """Contents list of bare titles, one per line. Ends at the first double blank line."""
    start = next((i for i, l in enumerate(lines) if l.strip().lower() == marker), None)
    if start is None:
        raise SystemExit(f'No line equal to "{marker}" found.')
    skipset = {norm(s) for s in skip}
    titles, blanks, i = [], 0, start + 1
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            blanks += 1
            if titles and blanks >= 2:
                break
        else:
            blanks = 0
            if norm(s) not in skipset:
                titles.append(s)
        i += 1
    return titles, i

def locate_titles(lines, titles, from_idx):
    """Find each title, in order: exact (1-3 wrapped lines), else fuzzy standalone line."""
    found, pos = [], from_idx
    for t in titles:
        target = norm(t)
        hit = None

        # 1. exact match, allowing the title to wrap over up to 3 lines
        for j in range(pos, len(lines)):
            cand = norm(lines[j])
            if not cand or not target.startswith(cand):
                continue
            joined, k = cand, j
            while joined != target and k + 1 < len(lines) and k - j < 2:
                k += 1
                if lines[k].strip():
                    joined = norm(joined + " " + lines[k])
            if joined == target:
                hit = (j, k)
                break

        # 2. fuzzy fallback: short line with blank lines around it
        if hit is None:
            for j in range(max(pos, 1), len(lines) - 1):
                s = lines[j].strip()
                if not s or len(s) > 90 or lines[j - 1].strip() or lines[j + 1].strip():
                    continue
                if difflib.SequenceMatcher(None, norm(s), target).ratio() >= 0.8:
                    hit = (j, j)
                    print(f"  NOTE: fuzzy match  '{t}'  ->  '{s}'")
                    break

        if hit is None:
            print(f"  WARNING: title not found in body: {t}")
            continue
        j, k = hit
        title = " ".join(lines[x].strip() for x in range(j, k + 1) if lines[x].strip()).replace("_", "").rstrip(".")
        found.append((k, title))
        pos = k + 1
    return found

def clean(body_lines):
    text = "\n".join(body_lines)
    text = re.sub(r"\[Footnote[^\]]*\]", " ", text, flags=re.S)
    text = re.sub(r"\[Illustration[^\]]*\]", " ", text, flags=re.S)
    text = re.sub(r"(?m)(?<=\n\n)[ \t]*\[\d+\][^\n]*(?:\n(?![ \t]*\n)[^\n]*)*", "", text)  # footnote definitions
    text = re.sub(r"\[\d+\]", "", text)                       # footnote markers
    text = re.sub(r"^\s*(\*\s*){3,}$", "", text, flags=re.M)  # * * * * * separators
    text = text.replace("_", "")                              # italics markup
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)              # unwrap hard-wrapped lines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    text = re.sub(r"\s*(?:(?:Thus|Here|So|Now) my story endeth,?\s*)?The Natiya-thorn withereth.*$",
                  "", text, flags=re.S | re.I)                              # closing formula
    text = re.sub(r"\s*(?:Thus|Here|So|Now) my story endeth[.,]?\s*$", "", text, flags=re.I)  # bare ending
    text = re.sub(r"\n\n[IVXLC]{1,7}$", "", text)                           # next story's numeral
    text = re.sub(r"\s*(?:End of (?:the )?Project Gutenberg|\*\*\* ?END).*$", "", text, flags=re.S | re.I)
    text = re.sub(r"\s*End of (?:the )?Project Gutenberg.*$", "", text, flags=re.S | re.I)
    return text.strip()

def pretty_title(t):
    t = re.sub(r"\s*\[\d+\]", "", t).strip().strip('"').rstrip(".").strip()
    if t.isupper():                                # ALL CAPS -> Title Case
        t = t.title()
        t = re.sub(r"\b(Of|The|And|A|An|To|In|On|Who|Whom|With|For)\b(?!$)",
                   lambda m: m.group(1).lower(), t)
        t = t[0].upper() + t[1:]
        t = t.replace("'S", "'s")
    return t

def body_limit(lines, toc_end, stop_pattern):
    """Index of the first Notes-style line after the contents list, so titles in the notes can't match."""
    rx = re.compile(stop_pattern, re.I)
    return next((j for j in range(toc_end, len(lines)) if rx.match(lines[j])), len(lines))

def to_roman(n):
    out = ""
    for v, s in [(100, "C"), (90, "XC"), (50, "L"), (40, "XL"), (10, "X"), (9, "IX"),
                 (5, "V"), (4, "IV"), (1, "I")]:
        while n >= v:
            out += s
            n -= v
    return out


def locate_by_numerals(lines, titles, from_idx, limit):
    """Body headings are a Roman numeral alone on a line, then the title. Numerals must appear in order."""
    found, pos = [], from_idx
    for n, t in enumerate(titles, 1):
        numeral = to_roman(n)
        j = next((x for x in range(pos, limit) if lines[x].strip().rstrip(".") == numeral), None)
        if j is None:
            print(f"  WARNING: numeral {numeral} not found for: {t}")
            continue
        k = j + 1
        while k < limit and not lines[k].strip():          # skip blank lines
            k += 1
        while k + 1 < limit:                                # skip title lines (wrapped, or a second all-caps title)
            nxt = k + 1
            while nxt < limit and not lines[nxt].strip():
                nxt += 1
            if nxt < limit and nxt - k <= 3 and lines[nxt].strip().isupper() and len(lines[nxt].strip()) < 100:
                k = nxt
            else:
                break
        found.append((k, t))
        pos = k + 1
    return found

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--file", required=True)
    p.add_argument("--prefix", required=True, help="id prefix, e.g. jacobs")
    p.add_argument("--source", required=True, help='e.g. "Indian Fairy Tales (Jacobs, 1892)"')
    p.add_argument("--region", default="Unknown")
    p.add_argument("--toc", action="store_true", help="find titles from the Contents list")
    p.add_argument("--toc-plain", action="store_true", help="Contents list is bare titles, no numerals")
    p.add_argument("--skip", default="", help="comma-separated contents entries to ignore (e.g. Preface)")
    p.add_argument("--toc-marker", default="contents")
    p.add_argument("--heading", help="regex matching each story title line")
    p.add_argument("--stop", default=r"^\s*notes( and references)?\s*\.?\s*$",
                   help="regex: first matching line after the last story ends it")
    p.add_argument("--min-chars", type=int, default=500)
    p.add_argument("--out", default="data/stories.jsonl")
    p.add_argument("--write", action="store_true")
    p.add_argument("--numeral-heads", action="store_true",
                   help="body headings are a Roman numeral alone on a line (use with --toc)")
    p.add_argument("--no-pages", action="store_true", help="contents entries have no page numbers")
    a = p.parse_args()

    if not (a.toc or a.toc_plain or a.heading):
        raise SystemExit("Give --toc, --toc-plain or --heading REGEX")

    text = strip_gutenberg(open(a.file, encoding="utf-8-sig").read())
    lines = text.split("\n")

    if a.toc_plain:
        skip = [s.strip() for s in a.skip.split(",") if s.strip()]
        titles, toc_end = parse_toc_plain(lines, a.toc_marker, skip)
        print(f"Contents list has {len(titles)} entries")
        heads = locate_titles(lines[:body_limit(lines, toc_end, a.stop)], titles, toc_end)
    elif a.toc:
        titles, toc_end = parse_toc(lines, a.toc_marker, a.no_pages)
        print(f"Contents list has {len(titles)} entries")
        limit = body_limit(lines, toc_end, a.stop)
        if a.numeral_heads:
            heads = locate_by_numerals(lines, titles, toc_end, limit)
        else:
            heads = locate_titles(lines[:limit], titles, toc_end)
    else:
        rx = re.compile(a.heading)
        heads = [(i, l.strip()) for i, l in enumerate(lines) if rx.match(l)]

    if not heads:
        raise SystemExit("No story headings found.")

    # where the last story ends
    stop_rx = re.compile(a.stop, re.I)
    last_end = next((j for j in range(heads[-1][0] + 1, len(lines)) if stop_rx.match(lines[j])), len(lines))
    if last_end == len(lines):
        print("  NOTE: no --stop line found after the last story; it runs to the end of the book.")

    stories = []
    for k, (idx, title) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else last_end
        body = clean(lines[idx + 1:end])
        if len(body) >= a.min_chars:
            stories.append((title, body))

    print(f"Found {len(stories)} stories")
    for i, (title, body) in enumerate(stories, 1):
        print(f"{i:3d}. {title[:62]:62s} {len(body):6d} chars")

    if not a.write:
        print("\nPreview only. Re-run with --write to save to", a.out)
        return

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    rows = []
    if os.path.exists(a.out):
        with open(a.out, encoding="utf-8") as f:
            rows = [json.loads(l) for l in f if l.strip()]
        rows = [r for r in rows if not r["id"].startswith(a.prefix + "_")]  # replace this book only
    for i, (title, body) in enumerate(stories, 1):
        rows.append({
            "id": f"{a.prefix}_{i:03d}",
            "title": pretty_title(title),
            "region": a.region,
            "theme": "unknown",   # tagged by an LLM step later
            "language": "English",
            "source": a.source,
            "text": body,
        })
    with open(a.out, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Wrote {len(rows)} total stories to {a.out}")


if __name__ == "__main__":
    main()