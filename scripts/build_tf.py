#!/usr/bin/env python3
"""Build the LXX-Greek Text-Fabric from the gold UD_Ancient_Greek-PTNK CoNLL-U
treebank (Genesis + Ruth — the only hand-corrected LXX syntax that exists).

Ported from readers-vulgate/scripts/build_tf.py (the gold UD_Latin-PROIEL
converter). Same node/feature scheme so the cross-corpus upos/udrel layer stays
harmonized across Tanakh/GNT/Vulgate/LXX.

Node types (coarsest -> finest):
  document(LXX) -> book -> chapter -> verse -> word(slot)

GREEK-SPECIFIC PORTING ADAPTATION (vs Vulgate)
----------------------------------------------
The PTNK treebank's sentence segmentation does NOT align to verses: 29 Genesis
sentences span 2-4 distinct verse refs. The Vulgate build keyed each whole
sentence to its first token's Ref; that would misplace the tail tokens of a
cross-verse sentence. Here every WORD is bucketed to ITS OWN token `Ref=`
verse, so a sentence that crosses a verse boundary places each token under the
correct verse node. `sentence` is therefore NOT a nesting section; the original
sent_id is preserved as a per-word feature, and the dependency `head` edge
(global slot->slot) still links a token to its governor even across a verse cut.

Slot (word) features:
  form        NFC-normalised Greek surface form
  lemma       lemma (NFC)
  upos        UD universal POS (canonical cross-corpus feature)
  xpos        native POS (PTNK leaves this '_'; stored as '_')
  morph       FEATS column (UD morphological features string)
  udrel       UD dependency relation (canonical cross-corpus feature)
  is_root     1 where head == 0 (sentence root)
  syn_source  "ptnk-gold" for all tokens (provenance mandate §9 of substrate.md)
  text_source "lxx"
  sent_id     original PTNK sent_id of the sentence this word belongs to
  head        EDGE dep->governor (global slot edge; absent for roots)

Book/chapter/verse features:
  book_code   GEN | RUTH
  book_name   Genesis | Ruth
  chapter     int
  verse       int
  ref         BOOKCODE_CHAPTER.VERSE (for verse nodes)

Document features:
  text_source "lxx"
  title       "Septuagint (Rahlfs) — gold-syntax sample: Genesis + Ruth"

Output: data/tf/0.1/  (load with Fabric(locations='data/tf', modules='0.1'))
"""
import re, sys, unicodedata
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

from tf.convert.walker import CV
from tf.fabric import Fabric

REPO = Path(__file__).resolve().parent.parent
CONLLU_DIR = REPO / "private" / "substrate" / "ud-ptnk" / "not-to-release" / "ready"
TF_DIR = REPO / "data" / "tf"
VERSION = "0.1"

# Source CoNLL-U files, in canonical reading order (Genesis then Ruth).
CONLLU_FILES = [CONLLU_DIR / "genesis.conllu", CONLLU_DIR / "ruth.conllu"]

# ---- book ordering and display names ----------------------------------------

BOOK_ORDER = ["GEN", "RUTH"]
BOOK_NAME = {"GEN": "Genesis", "RUTH": "Ruth"}

# ---- CoNLL-U parsing --------------------------------------------------------

def nfc(s):
    return unicodedata.normalize("NFC", s)


def parse_conllu_files(paths):
    """Yield sentence dicts in document order.
    Each dict: {sent_id, text, tokens:[{id,form,lemma,upos,xpos,morph,head,udrel,ref_raw}]}.
    Multiword (n-m) and empty-node (n.m) lines are skipped.
    """
    for path in paths:
        cur_sent_id = None
        cur_text = None
        cur_tokens = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if line.startswith("# sent_id"):
                    cur_sent_id = line.split(" = ", 1)[1].strip() if " = " in line else line
                elif line.startswith("# text"):
                    cur_text = line.split(" = ", 1)[1] if " = " in line else ""
                elif line == "":
                    if cur_tokens:
                        yield {"sent_id": cur_sent_id, "text": cur_text or "", "tokens": cur_tokens}
                    cur_tokens = []
                    cur_sent_id = None
                    cur_text = None
                elif line.startswith("#"):
                    pass
                else:
                    parts = line.split("\t")
                    if len(parts) < 10:
                        continue
                    idx = parts[0]
                    if "-" in idx or "." in idx:
                        continue
                    misc = parts[9]
                    ref_m = re.search(r"Ref=([^\|\s]+)", misc)
                    ref_raw = ref_m.group(1) if ref_m else ""
                    cur_tokens.append({
                        "id": int(idx),
                        "form": nfc(parts[1]),
                        "lemma": nfc(parts[2]) if parts[2] != "_" else nfc(parts[1]),
                        "upos": parts[3] if parts[3] != "_" else "X",
                        "xpos": parts[4],          # PTNK leaves this '_'
                        "morph": parts[5] if parts[5] != "_" else "",
                        "head": int(parts[6]) if parts[6] != "_" else 0,
                        "udrel": parts[7] if parts[7] != "_" else "_",
                        "ref_raw": ref_raw,
                        # trailing whitespace: empty if MISC says SpaceAfter=No
                        # (Greek punctuation attaches to its word) else a space.
                        "after": "" if "SpaceAfter=No" in misc else " ",
                    })
            if cur_tokens:
                yield {"sent_id": cur_sent_id, "text": cur_text or "", "tokens": cur_tokens}

# ---- ref parsing ------------------------------------------------------------

_REF_RE = re.compile(r"^([A-Z0-9]+)_(\d+)\.(\d+)$")

def parse_ref(ref_raw):
    """Parse 'GEN_1.1' -> ('GEN', 1, 1). Returns None if not in this format."""
    m = _REF_RE.match(ref_raw)
    if m:
        return m.group(1), int(m.group(2)), int(m.group(3))
    return None

# ---- grouping (WORD-level by token Ref; sentences may cross verses) ---------

def group_words(conllu_paths):
    """Bucket every token to its own (book, chapter, verse) in reading order.
    Returns book_data[book][chapter][verse] = [token_dict (with 'sent_id' added)].
    Each token_dict keeps its source 'head' (intra-sentence local id) plus a
    unique 'uid' so head edges can be rebuilt across the whole corpus.
    """
    book_data = {}        # {book: {chapter: {verse: [tok]}}}
    # We also need, per sentence, the local-id -> uid map to rebuild head edges.
    sentences = []        # list of (sent_id, {local_id: uid})
    uid_counter = 0
    skipped = 0

    for sent in parse_conllu_files(conllu_paths):
        local_to_uid = {}
        for tok in sent["tokens"]:
            parsed = parse_ref(tok["ref_raw"])
            if parsed is None:
                skipped += 1
                continue
            book, chap, verse = parsed
            uid_counter += 1
            tok2 = dict(tok)
            tok2["uid"] = uid_counter
            tok2["sent_id"] = sent["sent_id"]
            tok2["sent_text"] = sent["text"]
            local_to_uid[tok["id"]] = uid_counter
            book_data.setdefault(book, {}).setdefault(chap, {}).setdefault(verse, []).append(tok2)
        sentences.append((sent["sent_id"], local_to_uid, sent["tokens"]))

    return book_data, sentences, skipped

# ---- Walker (director) ------------------------------------------------------

def director(cv):
    stats = {"books": 0, "chapters": 0, "verses": 0, "words": 0,
             "root_words": 0, "edge_pairs": 0, "sentences": 0}

    book_data, sentences, skipped = group_words(CONLLU_FILES)
    stats["sentences"] = len(sentences)

    # First emit all slots (verse-by-verse) and record uid -> tf-slot.
    uid_to_slot = {}

    doc_node = cv.node("document")
    cv.feature(doc_node, text_source="lxx", title=TEXT_SOURCE_TITLE)

    for book_code in BOOK_ORDER:
        if book_code not in book_data:
            continue
        bk = cv.node("book")
        cv.feature(bk, book_code=book_code, book_name=BOOK_NAME.get(book_code, book_code),
                   text_source="lxx")
        stats["books"] += 1

        for chap_num in sorted(book_data[book_code]):
            ch = cv.node("chapter")
            cv.feature(ch, book_code=book_code, chapter=chap_num, text_source="lxx")
            stats["chapters"] += 1

            for verse_num in sorted(book_data[book_code][chap_num]):
                vs = cv.node("verse")
                cv.feature(vs, book_code=book_code, chapter=chap_num, verse=verse_num,
                           ref=f"{book_code}_{chap_num}.{verse_num}", text_source="lxx")
                stats["verses"] += 1

                for tok in book_data[book_code][chap_num][verse_num]:
                    w = cv.slot()
                    is_root = 1 if tok["head"] == 0 else 0
                    cv.feature(w,
                               form=tok["form"],
                               lemma=tok["lemma"],
                               upos=tok["upos"],
                               xpos=tok["xpos"],
                               morph=tok["morph"],
                               udrel=tok["udrel"],
                               is_root=is_root,
                               after=tok["after"],
                               syn_source="ptnk-gold",
                               text_source="lxx",
                               sent_id=tok["sent_id"])
                    uid_to_slot[tok["uid"]] = w
                    stats["words"] += 1
                    if is_root:
                        stats["root_words"] += 1

                cv.terminate(vs)
            cv.terminate(ch)
        cv.terminate(bk)

    cv.terminate(doc_node)

    # Emit head edges AFTER all slots exist (dep -> governor), rebuilt from the
    # per-sentence local-id -> uid maps. Works across verse cuts because TF
    # slots are global.
    for sent_id, local_to_uid, tokens in sentences:
        for tok in tokens:
            if tok["head"] == 0:
                continue
            dep_uid = local_to_uid.get(tok["id"])
            gov_uid = local_to_uid.get(tok["head"])
            if dep_uid is None or gov_uid is None:
                continue
            dep_slot = uid_to_slot.get(dep_uid)
            gov_slot = uid_to_slot.get(gov_uid)
            if dep_slot is None or gov_slot is None:
                continue
            cv.edge(dep_slot, gov_slot, head=None)
            stats["edge_pairs"] += 1

    print(f"\nNODE COUNTS:")
    print(f"  book      {stats['books']}")
    print(f"  chapter   {stats['chapters']}")
    print(f"  verse     {stats['verses']}")
    print(f"  word      {stats['words']}  (slots)")
    print(f"  is_root=1 {stats['root_words']}")
    print(f"  head edges {stats['edge_pairs']}")
    print(f"  sentences {stats['sentences']}  (sent_id stored as word feature)")
    if skipped:
        print(f"  WARNING: {skipped} tokens had no parseable Ref= and were skipped")


# ---- Feature metadata -------------------------------------------------------

TEXT_SOURCE_TITLE = "Septuagint (Rahlfs) — gold-syntax sample: Genesis + Ruth"

GENERIC_META = dict(
    name="lxx-greek",
    version=VERSION,
    purpose=(
        "Septuagint Greek Text-Fabric, gold-syntax sample (Genesis + Ruth) "
        "from the UD_Ancient_Greek-PTNK hand-corrected dependency treebank, "
        "serialized to BHSA-ecosystem format with the harmonized upos/udrel "
        "cross-corpus layer (sibling of readers-vulgate v0.1)."
    ),
    source="UD_Ancient_Greek-PTNK (gold hand-corrected LXX syntax + morphology)",
    writtenBy="readers-lxx/scripts/build_tf.py",
)

OTEXT = {
    "fmt:text-orig-full": "{form}{after}",
    "sectionTypes": "book,chapter,verse",
    "sectionFeatures": "book_name,chapter,verse",
    "structureTypes": "document,book,chapter,verse",
    "structureFeatures": "title,book_name,chapter,verse",
}

FEATURE_META = {
    "form": {"description": "Greek surface form (NFC-normalized Unicode)"},
    "after": {"description": "trailing whitespace after the token (empty when MISC SpaceAfter=No, i.e. punctuation attaches to its word); reproduces exact source spacing"},
    "lemma": {"description": "lemma (PTNK; NFC-normalized); falls back to form if absent"},
    "upos": {"description": (
        "UD universal POS — CANONICAL CROSS-CORPUS FEATURE. Same name/schema as "
        "BHSA, GNT Macula, and the Vulgate TF. Source: PTNK manual annotation.")},
    "xpos": {"description": "native POS tag ('_' in PTNK — unused; kept for schema parity)"},
    "morph": {"description": "UD FEATS string (morphological features; '_' absent -> empty string)"},
    "udrel": {"description": (
        "UD dependency relation — CANONICAL CROSS-CORPUS FEATURE. Same name/schema "
        "as BoFM, GNT, and the Vulgate TF. Source: PTNK manual annotation.")},
    "is_root": {"description": "1 if this token is the syntactic root of its sentence (head==0); 0 otherwise"},
    "syn_source": {"description": "provenance of syntactic annotation; always 'ptnk-gold' for this corpus"},
    "text_source": {"description": "source work key: always 'lxx'"},
    "sent_id": {"description": (
        "original PTNK sent_id of the sentence containing this word; sentences are "
        "NOT a section node here because PTNK sentences cross verse boundaries")},
    "head": {"description": (
        "dependency head edge (dep -> governor); absent for roots (is_root=1). "
        "Dependent points TO governor (same as BHSA `mother` convention). Global "
        "slot edge: links across verse cuts within a PTNK sentence.")},
    "ref": {"description": "canonical reference BOOKCODE_CHAPTER.VERSE for verse nodes (e.g. GEN_1.1)"},
    "book_code": {"description": "book code: GEN | RUTH"},
    "book_name": {"description": "book display name: Genesis | Ruth"},
    "chapter": {"description": "chapter number (integer)"},
    "verse": {"description": "verse number (integer)"},
    "title": {"description": "human-readable title of the source work"},
}

INT_FEATURES = {"chapter", "verse", "is_root"}


def main():
    out = TF_DIR / VERSION
    out.mkdir(parents=True, exist_ok=True)
    print(f"Building LXX Greek TF v{VERSION} -> {out}", flush=True)

    cv = CV(Fabric(locations=str(out), silent="deep"))
    ok = cv.walk(
        director,
        slotType="word",
        otext=OTEXT,
        generic=GENERIC_META,
        intFeatures=INT_FEATURES,
        featureMeta=FEATURE_META,
        warn=None,
    )
    print("\nBUILD", "OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
