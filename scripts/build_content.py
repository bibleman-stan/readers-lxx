#!/usr/bin/env python3
"""build_content.py - Emit the LXX v1.5 Greek ATU text-files AND the
Brenton (1844) English verse-layer text-files that feed build_books.py.

Greek source  : the v1.5 mechanical ATU generator (scripts/lxx_generate.py)
                over the gold UD_Ancient_Greek-PTNK Text-Fabric at data/tf/0.1.
                Coverage = Genesis + Ruth (the only books in the PTNK gold).
English source: Brenton's English Septuagint (1844, public domain), USFM
                dataset from ebible.org cached at private/brenton/.

Output (committed, public):
  data/text-files/v1.5/grk/<NN-slug>/<slug>-<CC>.txt          (Greek ATU lines)
  data/text-files/v1.5/eng-brenton/<NN-slug>/<slug>-<CC>.txt  (Brenton verse text)

The Brenton layer is VERSE-LEVEL for this first build: the whole Brenton verse
is placed on the first ATU line of its verse block; remaining ATU lines of that
verse get a blank English line. A per-ATU interleave is a follow-up workflow.

COVERAGE NOTE: the PTNK gold treebank covers ONLY Genesis + Ruth. This script
emits ATU for exactly those two books and reports Brenton alignment over that
set.

Usage:
  cd C:/Users/bibleman/repos/readers-lxx
  PYTHONIOENCODING=utf-8 python scripts/build_content.py
  PYTHONIOENCODING=utf-8 python scripts/build_content.py --book GEN
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
GRK_DIR = os.path.join(REPO_ROOT, "data", "text-files", "v1.5", "grk")
ENG_DIR = os.path.join(REPO_ROOT, "data", "text-files", "v1.5", "eng-brenton")
BRENTON_DIR = os.path.join(REPO_ROOT, "private", "brenton")

if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
import lxx_generate as lx  # noqa: E402

# TF book_code -> (web slug, numbered-folder index, Brenton USFM filename)
# PTNK gold = Genesis + Ruth only.
BOOKS = [
    ("GEN",  "genesis", 1, "02-GENeng-Brenton.usfm"),
    ("RUTH", "ruth",    2, "09-RUTeng-Brenton.usfm"),
]

# Verse-level clause boundary patterns (English) - kept for the future
# per-ATU interleave; the v1 build emits the whole verse on the first line.
_CLAUSE_RE = re.compile(r"(?<=[.;:])\s+")
_COMMA_RE = re.compile(r"(?<=,)\s+")
_WS_RE = re.compile(r"\s+")

# USFM stripping. Brenton uses:
#   \v N  text...        : verse marker
#   \c N                 : chapter marker
#   \p \q \q1 \q2 \m     : paragraph / quote / margin markers (drop)
#   \sc ... \sc*         : small-caps (keep text)
#   \nd ... \nd*         : divine-name (keep text)
#   \f ... \f*           : footnote (DROP entire footnote, incl any embedded refs)
#   \x ... \x*           : cross-reference (DROP)
# Plus inline markers \ft \fr \fqa \fq etc. inside notes (all stripped with \f).
_FOOTNOTE_RE = re.compile(r"\\f\s.*?\\f\*", re.DOTALL)
_CROSSREF_RE = re.compile(r"\\x\s.*?\\x\*", re.DOTALL)
_INLINE_MARKER_RE = re.compile(r"\\(?:sc|nd|wj|qt|tl|bd|it|em|bk|pn|qs|qac|sig|ord|no|sup|add)\*?")
_PARA_MARKER_RE = re.compile(r"^\\(?:p|m|q[0-9]*|li[0-9]*|pi[0-9]*|s[0-9]*|nb|b|cls|qm[0-9]*|qa|pc|pmo|pmc|pmr|cl|d)\b.*$",
                              re.MULTILINE)
# Generic stray-backslash-marker sweep (catches anything we didn't enumerate)
_STRAY_BACKSLASH_RE = re.compile(r"\\[a-zA-Z][a-zA-Z0-9]*\*?")


def clean_brenton_text(s):
    """Strip USFM markup from a single verse's accumulated text."""
    s = _FOOTNOTE_RE.sub("", s)
    s = _CROSSREF_RE.sub("", s)
    # Remove paired character markers' opening/closing tags but keep the inner text.
    # \sc In\sc*  ->  In
    s = re.sub(r"\\(sc|nd|wj|qt|tl|bd|it|em|bk|pn|qs|qac|add)\s+", "", s)
    s = re.sub(r"\\(sc|nd|wj|qt|tl|bd|it|em|bk|pn|qs|qac|add)\*", "", s)
    # Sweep any remaining markers
    s = _STRAY_BACKSLASH_RE.sub("", s)
    s = _WS_RE.sub(" ", s).strip()
    return s


def load_brenton(usfm_filename):
    """Parse a Brenton USFM file -> {(chapter, verse): text}.

    Verses can span multiple physical lines (USFM allows wrapping); a verse
    accumulates text from its \\v marker until the next \\v or \\c marker.
    """
    path = os.path.join(BRENTON_DIR, usfm_filename)
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        raw = f.read()

    # Drop \p/\m/\q* paragraph markers (whole line each)
    raw = _PARA_MARKER_RE.sub("", raw)

    out = {}
    cur_chap = None
    cur_verse = None
    cur_text_parts = []

    def flush():
        if cur_chap is not None and cur_verse is not None and cur_text_parts:
            text = clean_brenton_text(" ".join(cur_text_parts))
            if text:
                out[(cur_chap, cur_verse)] = text

    # Token-walk: split on whitespace but preserve the original spacing for clean_brenton.
    # Simpler: scan line by line for \c / \v markers, accumulate trailing text.
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        # Header lines we don't care about
        if stripped.startswith("\\id ") or stripped.startswith("\\h ") \
                or stripped.startswith("\\toc") or stripped.startswith("\\mt") \
                or stripped.startswith("\\rem") or stripped.startswith("\\ide") \
                or stripped.startswith("\\usfm "):
            continue
        # Chapter marker: \c N
        m = re.match(r"^\\c\s+(\d+)\b(.*)$", stripped)
        if m:
            flush()
            cur_chap = int(m.group(1))
            cur_verse = None
            cur_text_parts = []
            # Anything after \c N on the same line is rare; ignore.
            continue
        # Verse marker: \v N text...
        m = re.match(r"^\\v\s+(\d+)\b\s*(.*)$", stripped)
        if m:
            flush()
            cur_verse = int(m.group(1))
            cur_text_parts = [m.group(2)]
            continue
        # Otherwise: continuation of the current verse (USFM line-wrapped text).
        if cur_verse is not None:
            cur_text_parts.append(stripped)

    flush()
    return out


def write_chapter(out_dir, slug, idx, chap, blocks):
    """blocks = list of (ref, [text_lines]). Writes the colometric file format:
    ref line, ATU lines, blank line between verses."""
    folder = os.path.join(out_dir, f"{idx:02d}-{slug}")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{slug}-{chap:02d}.txt")
    parts = []
    for ref, lines in blocks:
        parts.append(ref)
        parts.extend(lines)
        parts.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts) + "\n")
    return path


def chapters_in_tf(api, book_code):
    F = api.F
    chs = set()
    for v in F.otype.s("verse"):
        if F.book_code.v(v) == book_code:
            chs.add(F.chapter.v(v))
    return sorted(chs)


def split_eng_to_lines(eng_text, atu_lines):
    """Verse-level placement: full English verse on the FIRST ATU line, blanks
    on the rest. Returns exactly len(atu_lines) entries so the layers stay
    line-aligned. A per-ATU LLM-alignment is a follow-up workflow."""
    n = len(atu_lines)
    if n == 0:
        return []
    if not eng_text:
        return [""] * n
    return [eng_text] + [""] * (n - 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--book", default=None, help="TF book_code, e.g. GEN or RUTH")
    args = ap.parse_args()

    api = lx.load_api()

    selected = BOOKS
    if args.book:
        selected = [b for b in BOOKS if b[0] == args.book.upper()]
        if not selected:
            print(f"Unknown book {args.book}", file=sys.stderr)
            sys.exit(1)

    cov = {
        "tf_verses": 0,
        "eng_aligned": 0,
        "eng_missing": defaultdict(list),
    }

    for book_code, slug, idx, brenton_file in selected:
        eng = load_brenton(brenton_file)
        chs = chapters_in_tf(api, book_code)
        book_verses = 0
        book_aligned = 0
        for chap in chs:
            lines = lx.generate(book_code, chap)
            by_verse = []
            seen_ref = {}
            for ln in lines:
                ref = ln["ref"]
                txt = lx.render(api, ln)
                if ref not in seen_ref:
                    seen_ref[ref] = len(by_verse)
                    by_verse.append([ref, [], ln["verse"]])
                by_verse[seen_ref[ref]][1].append(txt)

            grk_blocks = []
            eng_blocks = []
            for ref, atu_lines, vnum in by_verse:
                grk_blocks.append((ref, atu_lines))
                eng_text = eng.get((chap, vnum), "")
                book_verses += 1
                cov["tf_verses"] += 1
                if eng_text:
                    book_aligned += 1
                    cov["eng_aligned"] += 1
                else:
                    cov["eng_missing"][slug].append(f"{chap}:{vnum}")
                eng_lines = split_eng_to_lines(eng_text, atu_lines)
                eng_blocks.append((ref, eng_lines))

            write_chapter(GRK_DIR, slug, idx, chap, grk_blocks)
            write_chapter(ENG_DIR, slug, idx, chap, eng_blocks)

        pct = (100.0 * book_aligned / book_verses) if book_verses else 0.0
        print(f"  {slug:<8} {len(chs):>2} ch  {book_verses:>4} TF-vv  "
              f"Brenton-aligned {book_aligned:>4} ({pct:5.1f}%)")

    print("\n=== BRENTON COVERAGE OVER TF-PRESENT VERSES ===")
    print(f"Greek (TF) verses emitted : {cov['tf_verses']}")
    print(f"Brenton-aligned           : {cov['eng_aligned']} "
          f"({100.0*cov['eng_aligned']/max(cov['tf_verses'],1):.1f}%)")
    total_missing = sum(len(v) for v in cov["eng_missing"].values())
    print(f"Brenton mismatches (no Brenton verse at TF ref): {total_missing}")
    for slug in sorted(cov["eng_missing"]):
        miss = cov["eng_missing"][slug]
        print(f"   {slug:<8} {len(miss):>3}  {', '.join(miss[:12])}"
              + (" ..." if len(miss) > 12 else ""))

    report = {
        "tf_verses": cov["tf_verses"],
        "eng_aligned": cov["eng_aligned"],
        "eng_mismatches_total": total_missing,
        "eng_mismatches_by_book": {k: v for k, v in cov["eng_missing"].items()},
    }
    os.makedirs(os.path.join(REPO_ROOT, "research"), exist_ok=True)
    with open(os.path.join(REPO_ROOT, "research", "brenton-coverage.json"),
              "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print("\nWrote research/brenton-coverage.json")


if __name__ == "__main__":
    main()
