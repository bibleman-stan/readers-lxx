#!/usr/bin/env python3
"""LXX-native ATU generator: ports readers-vulgate/scripts/vulgate_generate.py
onto the gold UD_Ancient_Greek-PTNK Text-Fabric at data/tf/0.1.

The UD architecture and the binding rules are UD-GENERAL and carried over
UNCHANGED. Only the LANGUAGE-SPECIFIC lexical sets are localized to Greek:

  * causal subordinators: Latin quia/quoniam/quod -> Greek ὅτι / διότι / ἐπεί /
    ἐπειδή / καθότι, detected as a `mark` lemma on an advcl. (NB: in this PTNK
    treebank γάρ is tagged `mark`, but it is a POSTPOSITIVE DISCOURSE
    connective, NOT a subordinator — it is deliberately EXCLUDED so we never
    bind a γάρ clause. ὅτι is also the content-"that" complementizer; the
    _CONTENT_VERBS suppression below keeps an object-ὅτι from binding as a
    causal ground.)
  * content-taking matrix verbs (speech / cognition / perception / emotion):
    the Latin set becomes Greek speech/cognition lemmas (λέγω, εἶπον, οἶδα,
    γινώσκω, ἀκούω, ὁράω, ...). When one of these governs an advcl-ὅτι, the
    ὅτι clause is an OBJECT clause mis-tagged advcl -> suppress the causal bind
    (err STAND, the safe under-merge side of the over-merge red line).

Everything else (clause-head STAND/BIND classification, R1 finite-frame
direction, coordination-inheritance + its _has_own_subject /
_coordinate_is_new_assertion guards, contentless-line merge) is identical to the
Vulgate generator.

This is a FIRST-PASS measurement draft. Not deployed, not committed.

Usage:
  cd C:/Users/bibleman/repos/readers-lxx
  PYTHONIOENCODING=utf-8 python scripts/lxx_generate.py GEN 1
  PYTHONIOENCODING=utf-8 python scripts/lxx_generate.py RUTH 1
"""
import sys
from tf.fabric import Fabric

TF_LOCATION = "C:/Users/bibleman/repos/readers-lxx/data/tf"
TF_MODULE = "0.1"

# Clause-head relations whose head sits OUTSIDE the clause it heads.
BIND_RELS = {"acl", "acl:relcl", "ccomp", "xcomp", "csubj", "csubj:pass"}
STAND_RELS = {"root", "conj", "parataxis"}
# advcl is conditional: finite advcl STANDS (then R1 may redirect); non-finite
# advcl BINDS. advcl:cmp / advcl:relcl are treated like advcl (Greek-present).

# Greek has only Part / Inf as non-finite VerbForm values (no Ger/Gdv).
_NONFINITE_VF = ("VerbForm=Part", "VerbForm=Inf")

# Greek causal subordinators (the Latin quia/quoniam/quod analogue). Detected as
# a `mark` lemma on an advcl. γάρ is EXCLUDED (postpositive discourse, not a
# subordinator). ὅτι is included but guarded by _CONTENT_VERBS (object-"that").
_CAUSAL_MARKS = {"ὅτι", "διότι", "ἐπεί", "ἐπειδή", "καθότι"}

_api = None


def load_api():
    global _api
    if _api is None:
        TF = Fabric(locations=TF_LOCATION, modules=TF_MODULE, silent="deep")
        _api = TF.load(
            "form lemma upos udrel morph is_root verse chapter "
            "book_code book_name ref sent_id head after",
            silent="deep",
        )
    return _api


def _morph(api, w):
    return api.F.morph.v(w) or ""


def _person_num(api, w):
    p = n = ""
    for tok in _morph(api, w).split("|"):
        if tok.startswith("Person="):
            p = tok
        elif tok.startswith("Number="):
            n = tok
    return (p, n)


def is_finite(api, w):
    """Finite if FEATS carry VerbForm=Fin, or a VERB/AUX with no non-finite
    VerbForm tag (a participle/infinitive never counts)."""
    m = _morph(api, w)
    if "VerbForm=Fin" in m:
        return True
    if api.F.upos.v(w) in ("VERB", "AUX"):
        return not any(t in m for t in _NONFINITE_VF)
    return False


def is_clause_head(api, w):
    rel = api.F.udrel.v(w)
    if api.F.is_root.v(w) == 1:
        return True
    if rel in STAND_RELS or rel in BIND_RELS:
        return True
    if rel in ("advcl", "advcl:cmp", "advcl:relcl"):
        return True
    return False


def governor_chain(api, w):
    chain = []
    seen = {w}
    cur = w
    while True:
        gov = api.E.head.f(cur)
        if not gov:
            break
        g = gov[0]
        if g in seen:
            break
        chain.append(g)
        seen.add(g)
        cur = g
    return chain


def subtree_has_finite(api, head, children_of):
    stack = [head]
    seen = set()
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        if is_finite(api, n):
            return True
        stack.extend(children_of.get(n, ()))
    return False


def _has_own_subject(api, w, children_of):
    for c in children_of.get(w, ()):
        if api.F.udrel.v(c) in ("nsubj", "nsubj:pass", "csubj", "csubj:pass"):
            return True
    return False


def _coordinate_is_new_assertion(api, w):
    """Veto on the inheritance-bind: a coordinate whose subject person/number
    SHIFTS vs its conjunct, inside a content/relative (ccomp/acl) frame, is a
    NEW independent assertion flattened into a speech/relative line — the
    over-merge the gate flags. Standing it is the safe under-merge side."""
    gov = api.E.head.f(w)
    if not gov:
        return False
    if _person_num(api, w) == _person_num(api, gov[0]):
        return False
    seen, c = {w}, w
    while True:
        g = api.E.head.f(c)
        if not g:
            return False
        g = g[0]
        if g in seen:
            return False
        seen.add(g)
        if api.F.udrel.v(g) == "conj":
            c = g
            continue
        return api.F.udrel.v(g) in ("ccomp", "acl", "acl:relcl")


# Greek content-taking matrix verbs (speech / cognition / perception / emotion).
# When one governs an advcl-ὅτι, the ὅτι clause is an OBJECT ("that"/recitative)
# clause mis-tagged advcl; binding it as a causal ground over-merges. Suppress
# -> STAND (the safe under-merge side of the over-merge red line). Lemmas given
# in their PTNK dictionary form (aorist εἶπον is a distinct lemma from λέγω).
_CONTENT_VERBS = {
    # speech
    "λέγω", "εἶπον", "λαλέω", "φημί", "ἀποκρίνομαι", "βοάω", "κράζω",
    "ἀναγγέλλω", "ἀπαγγέλλω", "διηγέομαι", "ὁμολογέω", "κηρύσσω", "μαρτυρέω",
    "γράφω", "ἐντέλλομαι", "κελεύω", "προστάσσω", "ἐρωτάω",
    # cognition
    "οἶδα", "γινώσκω", "ἐπίσταμαι", "νοέω", "συνίημι", "λογίζομαι", "νομίζω",
    "ἡγέομαι", "δοκέω", "πιστεύω", "μιμνήσκομαι", "μνημονεύω", "ἐνθυμέομαι",
    "κρίνω", "ἐλπίζω", "βούλομαι", "θέλω",
    # perception
    "ὁράω", "εἶδον", "βλέπω", "ἀκούω", "θεωρέω", "αἰσθάνομαι",
    # emotion
    "χαίρω", "θαυμάζω", "φοβέομαι", "λυπέομαι", "ἀγαλλιάομαι", "δοξάζω",
}


def _causal_ground_marks(api, w, children_of):
    """The `mark` children of advcl-head w whose lemma is a true Greek causal
    subordinator (_CAUSAL_MARKS). γάρ is excluded (discourse, not a mark we
    bind). A declarative/recitative ὅτι after a verb of knowing/saying is
    handled by the _CONTENT_VERBS guard below."""
    out = []
    for c in children_of.get(w, ()):
        if api.F.udrel.v(c) == "mark":
            if (api.F.lemma.v(c) or "") in _CAUSAL_MARKS:
                out.append(c)
    return out


def _is_causal_anaphoric_ground(api, w, children_of):
    """Audited SAFE sub-class of the causal-bind rule: a FOLLOWING causal advcl
    binds BACKWARD into its main clause (one ATU) ONLY when it is a short, flat,
    anaphoric ground (the Beatitudes pattern). Four guards keep it off the
    over-merge red line:
      1. marker is a true causal subordinator (_CAUSAL_MARKS);
      2. governing verb is NOT a content verb (object-ὅτι guard);
      3. no NEW proper-noun referent in the subtree (anaphoric ground only);
      4. flat (no nested finite clause-head) AND short (subtree <= 8 words).
    """
    if not _causal_ground_marks(api, w, children_of):
        return False
    gov = api.E.head.f(w)
    if gov and (api.F.lemma.v(gov[0]) or "") in _CONTENT_VERBS:
        return False
    stack, sub, seen = [w], [], set()
    while stack:
        n = stack.pop()
        if n in seen:
            continue
        seen.add(n)
        sub.append(n)
        stack.extend(children_of.get(n, ()))
    if len(sub) > 8:
        return False
    if any(api.F.upos.v(n) == "PROPN" for n in sub):
        return False
    _NESTED = {"advcl", "advcl:cmp", "advcl:relcl", "ccomp", "acl", "acl:relcl",
               "conj", "csubj", "csubj:pass", "parataxis"}
    for n in sub:
        if n is w:
            continue
        if api.F.udrel.v(n) in _NESTED and is_finite(api, n):
            return False
    return True


def _is_frame_quote(api, w):
    """Frame|quote BREAK: w is a ccomp/csubj clause-head whose governor is a
    content-taking matrix verb (_CONTENT_VERBS — speech/cognition/perception).
    Then w is the QUOTE/CONTENT-clause; break the default ccomp BIND so the
    speech/cognition frame and its content render on separate ATU lines.

    Validated cross-corpus: BHSA Hebrew (original), BoFM EModE (197 instances,
    0 regressions, deployed 2026-05-27), GNT (Macula). Ported here unchanged
    -- only the Greek lemma set (_CONTENT_VERBS) is the language-specific part."""
    gov = api.E.head.f(w)
    if not gov:
        return False
    return (api.F.lemma.v(gov[0]) or "") in _CONTENT_VERBS


def _clause_head_of(api, w):
    if is_clause_head(api, w):
        return w
    for g in governor_chain(api, w):
        if is_clause_head(api, g):
            return g
    return w


# Silver-projection (2026-05-29): BHSA Hebrew ATU breaks projected through CATSS
# onto PTNK Greek, adjudicated on the Greek bidirectional test by parallel Sonnet,
# audited by 2 parallel Opus lenses (over-merge + atomicity). 92 survivors of 117
# Sonnet-passes from 53 chapters; gate HALTED, survivors returned and now applied
# here as candidate-augmentation -- each survivor adds a forced STAND clause-head
# at its break-point, on top of PTNK's clause-detection.
import json as _json
import os as _os
import re as _re

_SILVER = None


def _load_silver_breaks():
    """Lazy-load the silver-projection survivor JSON; cache by (book, chapter)."""
    global _SILVER
    if _SILVER is not None:
        return _SILVER
    _SILVER = {}
    path = _os.path.join(
        _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
        "data", "silver_projection_survivors.json"
    )
    if not _os.path.isfile(path):
        return _SILVER
    with open(path, encoding="utf-8") as f:
        data = _json.load(f)
    # chapter field is "<slug>-NN"; map slug -> TF book_code
    _SLUG_TO_CODE = {"genesis": "GEN", "ruth": "RUTH"}
    for s in data.get("survivors", []):
        ch = s.get("chapter", "")
        m = _re.match(r"^([a-z]+)-(\d+)$", ch)
        if not m:
            continue
        slug, chap_s = m.group(1), int(m.group(2))
        code = _SLUG_TO_CODE.get(slug)
        if not code:
            continue
        ref = s.get("ref", "")
        rm = _re.match(r"^(\d+):(\d+)$", ref)
        if not rm:
            continue
        verse = int(rm.group(2))
        _SILVER.setdefault((code, chap_s, verse), []).append(s)
    return _SILVER


def _form_norm(s):
    """Strip diacritics/punctuation for robust form-matching."""
    return _re.sub(r"[^Ͱ-Ͽἀ-῿]", "", (s or "").lower())


def _find_silver_break_word(api, verse_words, greek_left):
    """Given the survivor's greek_left text, find the word in the verse that
    sits IMMEDIATELY AFTER the last content token of greek_left -- that word
    is the projected break-point and should become a forced STAND clause-head.

    Strategy: take the last 1-3 content tokens of greek_left, find their
    consecutive match in verse_words by normalized form, return the word
    that follows. Skip tokens that are pure punctuation."""
    F = api.F
    left_tokens = [t for t in _re.split(r"\s+", greek_left or "") if t.strip()]
    # Drop pure punctuation tokens at the end (commas, mid-dots, periods)
    content_tokens = [t for t in left_tokens if any(_form_norm(t))]
    if not content_tokens:
        return None
    sig = content_tokens[-3:]
    sig_norm = [_form_norm(t) for t in sig]
    forms = [_form_norm(F.form.v(w) or "") for w in verse_words]
    # Find consecutive match of sig_norm in forms; return word at next position
    for i in range(len(forms) - len(sig_norm) + 1):
        if all(forms[i + j] == sig_norm[j] for j in range(len(sig_norm))):
            tail = i + len(sig_norm)
            # Skip over any PUNCT-tagged token following the sig (rides preceding line)
            while tail < len(verse_words) and F.upos.v(verse_words[tail]) == "PUNCT":
                tail += 1
            if tail < len(verse_words):
                return verse_words[tail]
            return None
    # Fallback: match just the last 1 content token
    if sig_norm:
        last = sig_norm[-1]
        for i, fn in enumerate(forms):
            if fn == last:
                tail = i + 1
                while tail < len(verse_words) and F.upos.v(verse_words[tail]) == "PUNCT":
                    tail += 1
                if tail < len(verse_words):
                    return verse_words[tail]
    return None


def generate(book_code, chap):
    api = load_api()
    F, E, L = api.F, api.E, api.L

    verses = [
        v for v in F.otype.s("verse")
        if F.book_code.v(v) == book_code and F.chapter.v(v) == chap
    ]
    verses.sort()

    chap_words = []
    for v in verses:
        chap_words.extend(L.d(v, "word"))
    chap_words = sorted(set(chap_words))
    children_of = {}
    for w in chap_words:
        gov = E.head.f(w)
        if gov:
            children_of.setdefault(gov[0], []).append(w)

    clause_heads = {w for w in chap_words if is_clause_head(api, w)}

    def precedes_governor(w):
        gov = E.head.f(w)
        if not gov:
            return False
        return w < gov[0]

    bind = {}
    _conj_pending = []
    for w in clause_heads:
        rel = F.udrel.v(w)
        if F.is_root.v(w) == 1:
            bind[w] = False
            continue
        if rel == "parataxis":
            bind[w] = False
            continue
        if rel == "conj":
            _conj_pending.append(w)
            continue
        if rel in ("advcl", "advcl:cmp", "advcl:relcl"):
            if not precedes_governor(w) and _is_causal_anaphoric_ground(api, w, children_of):
                # R3: short flat anaphoric causal ground FOLLOWING its main
                # clause binds BACKWARD (one ATU) — the Beatitudes pattern.
                bind[w] = True
            elif is_finite(api, w):
                # R1: finite frame preceding its governor binds FORWARD; finite
                # advcl following its head stands.
                bind[w] = precedes_governor(w)
            else:
                bind[w] = True  # non-finite participle/infinitive frame binds
            continue
        if rel in BIND_RELS:
            if rel in ("ccomp", "csubj", "csubj:pass") and _is_frame_quote(api, w):
                bind[w] = False  # frame|quote BREAK
            else:
                bind[w] = True
            continue
        bind[w] = False

    # --- 2nd pass: COORDINATION INHERITANCE (UD-general, unchanged) ----------
    def _conjunct_bind(w):
        seen = {w}
        c = w
        while True:
            gov = E.head.f(c)
            if not gov:
                return False
            g = gov[0]
            if g in seen:
                return False
            seen.add(g)
            if F.udrel.v(g) == "conj":
                c = g
                continue
            stands_alone = is_clause_head(api, g) and not bind.get(g, False)
            return not stands_alone

    for w in _conj_pending:
        if not subtree_has_finite(api, w, children_of):
            bind[w] = True
        elif _has_own_subject(api, w, children_of):
            bind[w] = False
        else:
            bind[w] = _conjunct_bind(w) and not _coordinate_is_new_assertion(api, w)

    def atu_root(w):
        ch = _clause_head_of(api, w)
        node = ch
        seen = {node}
        while True:
            if node in clause_heads and not bind.get(node, False):
                return node
            nxt = None
            for g in governor_chain(api, node):
                if is_clause_head(api, g):
                    nxt = g
                    break
            if nxt is None or nxt in seen:
                return node
            seen.add(nxt)
            node = nxt

    atu_of = {}
    for w in chap_words:
        atu_of[w] = atu_root(w)

    verse_of_word = {}
    for w in chap_words:
        vn = L.u(w, "verse")[0]
        verse_of_word[w] = (F.chapter.v(vn), F.verse.v(vn))

    # --- Silver-projection break application (post-atu_root) -------------
    # BHSA Hebrew ATU breaks projected via CATSS onto PTNK Greek; survivors of
    # the (c)-pipeline gate (parallel Sonnet adjudicate + 2-lens Opus audit).
    # PTNK's clause-detection misses verbless elliptical predications and
    # nominal-coordination predications -- silver-projection ADDS the missed
    # break-points by directly reassigning atu_of for the words at/after each
    # projected break. Doing this AFTER atu_root() avoids fighting the UD
    # _clause_head_of() walk which only recognizes UD clause-heads.
    _silver = _load_silver_breaks()
    _verse_words = {}
    for w in chap_words:
        vn = L.u(w, "verse")[0]
        _verse_words.setdefault(F.verse.v(vn), []).append(w)
    for verse_num, _ws in _verse_words.items():
        _ws_sorted = sorted(_ws)
        for proj in _silver.get((book_code, chap, verse_num), []):
            bw = _find_silver_break_word(api, _ws_sorted, proj.get("greek_left", ""))
            if bw is None:
                continue
            old_atu = atu_of[bw]
            bw_idx = _ws_sorted.index(bw)
            # All same-old-atu words at/after bw in surface order go to a new
            # ATU rooted at bw itself (bw is a valid word ID, unique).
            for w in _ws_sorted[bw_idx:]:
                if atu_of[w] == old_atu:
                    atu_of[w] = bw

    # Punctuation rides the line it FOLLOWS (surface order), not its UD head's
    # clause: a clause-final comma / · / period must not start the next ATU line.
    # Reassign each PUNCT token to the immediately preceding same-verse word's ATU.
    _pseq = sorted(chap_words)
    for _i, _w in enumerate(_pseq):
        if _i > 0 and F.upos.v(_w) == "PUNCT":
            _prev = _pseq[_i - 1]
            if verse_of_word[_prev] == verse_of_word[_w]:
                atu_of[_w] = atu_of[_prev]

    seq = sorted(chap_words)
    out = []
    run, run_atu, run_v = [], None, None
    for w in seq:
        a = atu_of[w]
        vref = verse_of_word[w]
        if run and (a != run_atu or vref != run_v):
            out.append((min(run), run_v, run))
            run = []
        run.append(w)
        run_atu, run_v = a, vref
    if run:
        out.append((min(run), run_v, run))

    out.sort(key=lambda x: x[0])

    lines = _merge_contentless(api, [(v, ws) for _, v, ws in out])

    return [
        {"ref": f"{chap}:{v[1]}", "chapter": v[0], "verse": v[1], "words": ws}
        for v, ws in lines
    ]


_FUNC_UPOS = {"ADP", "CCONJ", "SCONJ", "DET", "PART", "AUX", "PUNCT"}


def _has_content(api, ws):
    for w in ws:
        if api.F.upos.v(w) not in _FUNC_UPOS:
            return True
    return False


def _merge_contentless(api, lines):
    """Fold any function-word-only line into a neighbor. Greek postpositives /
    coordinators (δέ/γάρ/οὖν/τε/ἀλλά/καί-as-trailing) fold backward; everything
    else folds forward.

    VERSE-SAFE (Greek port fix): a contentless line is folded into a neighbor
    ONLY when that neighbor shares its verse `v`. PTNK sentences cross verse
    boundaries (e.g. GEN 49:3-4 are one sentence), so a verse-final punctuation
    line must never be carried into the next verse's first line — that drifts a
    token across the verse boundary and breaks per-verse parity. If a
    contentless line has no same-verse neighbor to absorb it, it stays as its
    own standalone line under its own verse (it still renders inline at display
    time, but its verse attribution is preserved)."""
    _BACKWARD = {"δέ", "γάρ", "οὖν", "τε", "μέν", "ἄρα", "γε", "δή", "τοίνυν"}
    out = []
    pend = []          # forward-pending contentless words (carried to next content line)
    pend_v = None      # verse of the pending words
    for v, ws in lines:
        if not _has_content(api, ws):
            lemmas = {api.F.lemma.v(w) for w in ws}
            # backward-fold ONLY into a same-verse predecessor
            if lemmas & _BACKWARD and out and out[-1][0] == v:
                ov, ows = out[-1]
                out[-1] = (ov, sorted(ows + ws))
            else:
                # forward-pend, but a verse change flushes the prior pend as a
                # standalone same-verse line (never cross the boundary)
                if pend and pend_v != v:
                    out.append((pend_v, sorted(pend)))
                    pend = []
                pend.extend(ws)
                pend_v = v
            continue
        # content line: absorb forward-pend only if it shares this verse
        if pend and pend_v == v:
            merged = sorted(pend + ws)
            pend = []
            pend_v = None
        else:
            if pend:  # pend belongs to a different verse: emit it standalone
                out.append((pend_v, sorted(pend)))
                pend = []
                pend_v = None
            merged = ws
        out.append((v, merged))
    if pend:
        # trailing contentless pend: fold into a same-verse predecessor if any,
        # else keep standalone under its own verse
        if out and out[-1][0] == pend_v:
            ov, ows = out[-1]
            out[-1] = (ov, sorted(ows + pend))
        else:
            out.append((pend_v, sorted(pend)))
    return out


def render(api, line):
    return "".join(api.T.text(w) for w in line["words"]).strip()


def verse_word_sequence(api, book_code, chap, verse):
    F, L = api.F, api.L
    for v in F.otype.s("verse"):
        if F.book_code.v(v) == book_code and F.chapter.v(v) == chap and F.verse.v(v) == verse:
            return list(L.d(v, "word"))
    return []


def main():
    book = sys.argv[1] if len(sys.argv) > 1 else "GEN"
    chap = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    api = load_api()
    lines = generate(book, chap)
    print(f"=== {book} {chap}: LXX v1.5 draft (PTNK-gold TF) ===\n")
    cur = None
    for ln in lines:
        if ln["ref"] != cur:
            if cur is not None:
                print()
            print(ln["ref"])
            cur = ln["ref"]
        print("  " + render(api, ln))


if __name__ == "__main__":
    main()
