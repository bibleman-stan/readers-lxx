# readers-lxx — Septuagint (LXX) colometric reader (SUBSTRATE-FIRST; not yet started)

Sibling to readers-tanakh / readers-gnt / readers-bofm. Part of the ATU (Atomic Thought
Unit) colometry program. **Operated by the unified orchestrator-Claude at `C:\Users\bibleman\`.**

## STATUS: substrate-assembly phase — NO ATU/sense-line work yet

Per the program's hard-won lesson (the BoFM over-merge ordeal, 2026-05-27): **do not draw a
single ATU boundary until the textual fabric reaches a parity threshold.** Fabric first;
superstructure second. See `~/repos/atu-method/docs/substrate.md` when written.

LXX is the **thinnest-syntax** of the four+ corpora (no BHSA-equivalent). Its unique asset:
CATSS word-aligns LXX↔BHS, so BHSA syntax can be **projected** onto the Greek for Hebrew-source
books — but see the GIGO caveat (this is exactly the BoFM-Isaiah trap).

## Substrate plan (assemble + VERIFY before any colometry)

Leads from the 2026-05-27 sweep — **UNVERIFIED until pulled** (confirm license/format/coverage).
**License gate (resolved):** CATSS is non-commercial-OK + requires a user declaration + proper
attribution (Kraft/Tov/CCAT). This program is non-commercial → clear.

| Resource | Provides | License (verify) | Format | Status |
|---|---|---|---|---|
| **CATSS** (via CenterBLC TF, fallback codykingham TF) | morphologically-tagged Rahlfs LXX | CATSS non-comm + declaration | Text-Fabric | morphology base |
| **UD Ancient Greek-PTNK** | hand-tagged syntax for PARTS of LXX (Codex Alexandrinus portions) | check | CoNLL-U | gold layer (partial) |
| **CATSS parallel × BHSA** | project Hebrew syntax→Greek for Hebrew-source books (Gen, Pss, Isa…) | CATSS | alignment | the unique asset (GIGO-cautioned) |
| **Diorisis** (820 texts, ~10M words, incl. LXX) | clean big-corpus background; permissive | CC BY 4.0 | XML / duckdb | background |
| Stanza / odyCy | mechanical parser | open | CoNLL-U | parser |
| **CCAT gopher** (`ccat.sas.upenn.edu/gopher/text/religion/biblical/`) | LXX morphology + the CATSS Hebrew-Greek parallel + NETS English | CATSS | text | **AT-RISK — MIRROR EARLY** |
| Context-Fabric `cfabric-mcp` | lets Claude query TF corpora natively (MCP) | open | MCP | tooling (eval) |

**Hard cases:** books w/ no Hebrew source (Wisdom, 2 Macc) AND outside UD-PTNK → scope out of
v1, or accept documented model-output syntax. Poetic books (Pss/Job/Prov) = highest oversight.

## Hybrid annotation pipeline (substrate-build → v0/v1)

1. Mechanical parse (Stanza/odyCy). 2. Gold-check (UD-PTNK). 3. **Alignment-projection** (CATSS×BHSA →
Greek) — **GIGO CAVEAT** (BoFM-Isaiah lesson): projected Hebrew structure is a *candidate*, NOT
Greek-target gold; KJV/translation divergence means each projected break must pass the **Greek**
bidirectional ATU test. 4. LLM (Claude) adjudication only (never parse from scratch); per-token
provenance + confidence. The syntactic substrate is explicitly HYBRID (hand/projected/model) —
document the epistemic status per book.

## Methodology
Cross-corpus canon: `~/repos/atu-method/docs/`. Container, not Originator; fabric quality bounds claims.
