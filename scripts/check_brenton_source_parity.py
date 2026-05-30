#!/usr/bin/env python3
"""Source-of-truth parity gate: alnum-normalized concatenation of each verse's
aligned eng-brenton output MUST equal the alnum-normalized Brenton USFM source
for that verse. Catches token loss/addition introduced by LLM realignment.

Stronger than check_brenton_parity.py (which compares working tree to git
INDEX -- only catches drift from the PRIOR commit, not absolute correctness)."""
import os
import re
import sys

REPO = "C:/Users/bibleman/repos/readers-lxx"
os.chdir(REPO)
sys.path.insert(0, os.path.join(REPO, "scripts"))
import build_content as bc  # noqa: E402


def alnum(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def parse_eng(path):
    out, ref, lines = {}, None, []
    for L in open(path, encoding="utf-8"):
        s = L.strip()
        if re.match(r"^\d+:\d+$", s):
            if ref is not None:
                out[ref] = " ".join(lines)
            ref, lines = s, []
        elif s:
            lines.append(s)
    if ref is not None:
        out[ref] = " ".join(lines)
    return out


BOOKS = [
    ("01-genesis", "genesis", 50, "02-GENeng-Brenton.usfm"),
    ("02-ruth",    "ruth",     4, "09-RUTeng-Brenton.usfm"),
]

bad = []
checked = 0
for dir_, slug, nchaps, usfm in BOOKS:
    src = bc.apply_versification(bc.load_brenton(usfm), "GEN" if slug == "genesis" else "RUTH")
    for ch in range(1, nchaps + 1):
        ch2 = f"{ch:02d}"
        eng_path = f"data/text-files/v1.5/eng-brenton/{dir_}/{slug}-{ch2}.txt"
        if not os.path.isfile(eng_path):
            continue
        cur = parse_eng(eng_path)
        for ref, joined in cur.items():
            m = re.match(r"^(\d+):(\d+)$", ref)
            if not m:
                continue
            chap, verse = int(m.group(1)), int(m.group(2))
            src_text = src.get((chap, verse), "")
            checked += 1
            if alnum(joined) != alnum(src_text):
                bad.append(f"{eng_path} {ref}  "
                           f"(eng_alnum={len(alnum(joined))}, "
                           f"src_alnum={len(alnum(src_text))})")

print(f"Brenton source parity: {len(bad)} mismatches across {checked} verses")
for b in bad[:30]:
    print(" ", b)
