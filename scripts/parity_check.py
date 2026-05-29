#!/usr/bin/env python3
"""ATU parity check: for each verse, the concatenation of the generated ATU
lines' word slots must equal the verse's source word-slot sequence exactly
(token-for-token, order preserved). Only line breaks are added by the
generator; no token may be dropped, duplicated, or reordered.

Usage:
  PYTHONIOENCODING=utf-8 python scripts/parity_check.py GEN 1
  PYTHONIOENCODING=utf-8 python scripts/parity_check.py            # all GEN+RUTH
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")
import lxx_generate as G


def check_chapter(api, book, chap):
    lines = G.generate(book, chap)
    # group emitted word-slot lists by verse
    by_verse = {}
    for ln in lines:
        by_verse.setdefault(ln["verse"], []).extend(ln["words"])

    F, L = api.F, api.L
    verses = sorted(
        v for v in F.otype.s("verse")
        if F.book_code.v(v) == book and F.chapter.v(v) == chap
    )
    bad = 0
    checked = 0
    for v in verses:
        vnum = F.verse.v(v)
        src = list(L.d(v, "word"))               # source order
        gen = by_verse.get(vnum, [])
        checked += 1
        if sorted(gen) != sorted(src) or gen != src:
            # mismatch in membership OR order
            bad += 1
            print(f"  PARITY FAIL {book} {chap}:{vnum}")
            sf = [F.form.v(w) for w in src]
            gf = [F.form.v(w) for w in gen]
            print(f"    src({len(sf)}): {' '.join(sf)}")
            print(f"    gen({len(gf)}): {' '.join(gf)}")
    return checked, bad


def main():
    api = G.load_api()
    F = api.F
    if len(sys.argv) > 2:
        targets = [(sys.argv[1], int(sys.argv[2]))]
    else:
        # all chapters of GEN + RUTH
        targets = []
        seen = set()
        for v in F.otype.s("verse"):
            key = (F.book_code.v(v), F.chapter.v(v))
            if key not in seen:
                seen.add(key)
                targets.append(key)
        targets.sort()

    total_checked = total_bad = 0
    for book, chap in targets:
        c, b = check_chapter(api, book, chap)
        total_checked += c
        total_bad += b

    print(f"\nPARITY: {total_checked} verses checked, {total_bad} mismatches")
    print("PARITY", "OK" if total_bad == 0 else "FAILED")
    return 0 if total_bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
