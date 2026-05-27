# Text-Fabric Tooling Scout — LXX and Vulgate

Scout date: 2026-05-27. Everything marked VERIFIED was tested or resolved live in this session. Claims marked NOT VERIFIED could not be confirmed by live install or URL resolution.

---

## 1. Text-Fabric Core — Verified Install Facts

| Item | Finding |
|---|---|
| Install command | `pip install text-fabric` |
| Version installed | **13.1.0** (released 2026-01-15) |
| Python requirement | >=3.9.0; tested through 3.14; Python 3.12 confirmed working |
| Core imports | `from tf.fabric import Fabric` and `from tf.app import use` — both import cleanly |
| Small dataset load | `use('annotation/banks', checkout='latest', silent='deep')` — **VERIFIED** loads 99-word mini-corpus; queries work |
| Data download location | `~/text-fabric-data/github/<org>/<repo>/` — auto-created on first `use()` call |
| Project status | Actively maintained by Dirk Roorda (annotation org); 13 major versions since 2016 |

### Standard data-distribution pattern

Corpus data lives in GitHub repos under orgs like `annotation/`, `ETCBC/`, `CenterBLC/`. The `use()` function auto-downloads on first call:

```python
from tf.app import use
A = use("CenterBLC/LXX", version="1935")  # downloads to ~/text-fabric-data/github/CenterBLC/LXX/
```

Subsequent calls load from disk cache. Large corpora (BHSA ~2.5 GB on disk) should not be bulk-downloaded in this session; the load command is sufficient to verify the pattern.

### Conversion framework

`tf.convert.walker` is TF's built-in write-your-own-converter framework. It provides a `CV` (corpus visitor) object with `slot()`, `node()`, `feature()`, `edge()`, etc. You write a `director(cv)` function that walks your source format and fires TF actions. There is **no dedicated CoNLL-U module** — `tf.convert` contains only: `walker.py`, `mql.py`, `pandas.py`, `recorder.py`, `tf.py`. CoNLL-U→TF requires a custom director (see Section 4).

---

## 2. Ready-Made Text-Fabric Datasets

| Name | Repo | License | Load command | Coverage | Verified? |
|---|---|---|---|---|---|
| **BHSA** (we already have) | github.com/ETCBC/bhsa | CC BY-NC 4.0 | `use('etcbc/bhsa')` | Complete Hebrew Bible + full linguistic annotations (syntax, morphology, clauses, phrases) | Repo resolves, app dir in local TF cache — YES |
| **CenterBLC LXX** | github.com/CenterBLC/LXX | MIT | `use("CenterBLC/LXX", version="1935")` | Complete Rahlfs 1935 LXX; morphology decomposed (person/number/gender/tense/POS); sentence divisions by punctuation; NO syntax trees | Repo resolves, load command confirmed from README — YES |
| **CenterBLC N1904** | github.com/CenterBLC/N1904 | MIT | `use("CenterBLC/N1904")` (version TBD from docs) | Complete Nestle 1904 GNT; morphology + constituency syntax trees; last release 2024-07-27 | Repo resolves — YES (load command version needs checking against live app) |
| **CenterBLC NA** | github.com/CenterBLC/NA | MIT | `use("CenterBLC/NA", version="1904")` | Nestle-Aland 1904 GNT enhanced (similar to N1904 with CBLC additions); morphology only; no syntax trees yet | Repo resolves, load command confirmed — YES |
| **CenterBLC SBLGNT** | github.com/CenterBLC/SBLGNT | MIT | `use("CenterBLC/SBLGNT", version="2022")` | Complete SBLGNT; morphology decomposed; alphabetic lexeme order; frequency; no syntax trees | Repo resolves, load command confirmed — YES |
| **CATSS LXX (codykingham)** | github.com/codykingham/catss_lxx | No stated license (CCAT user agreement applies) | Not on TF auto-download; local Fabric load from cloned data | CATSS LXX converted to 11 TF features (POS, subtype, lex, case, gender, number, tense, voice, mood, person, degree); completeness unclear | Repo resolves — YES (license encumbered) |
| **ETCBC extrabiblical** | github.com/ETCBC/extrabiblical | MIT | TF format, local load | Non-masoretic Hebrew texts (NOT Greek); marked UNSUPPORTED | Repo resolves — YES (not relevant for LXX/Vulgate) |
| **UD_Ancient_Greek-PROIEL** | github.com/UniversalDependencies/UD_Ancient_Greek-PROIEL | CC BY-NC-SA 4.0 | CoNLL-U (not TF); GNT + Herodotus | Dependency syntax, morphology; NOT in TF format but convertible | Repo resolves — YES |
| **UD_Latin-PROIEL** | github.com/UniversalDependencies/UD_Latin-PROIEL | CC BY-NC-SA 3.0 | CoNLL-U (not TF); Vulgate NT + Caesar + Cicero + Palladius | Dependency syntax + morphology; Vulgate NT is the biblical Latin substrate; NOT in TF format | Repo resolves — YES |

### What does NOT exist (verified negative)

- **Macula-LXX**: Clear-Bible/Macula has `macula-greek` (GNT) and `macula-hebrew` (HB) only. No Macula-LXX or Macula-Latin exists as of this scout. The `macula-greek` format is USFM/XML, not TF natively, though conversion projects exist.
- **CenterBLC Vulgate**: CenterBLC has 9 repos total — all Greek NT or Hebrew; no Latin.
- **ETCBC LXX**: ETCBC focus is Hebrew. No LXX TF dataset from them.
- **CenterBLC MT-LXX**: Exists (73 commits, no README/license) — appears to be a Macula-to-TF conversion project (`sp_data_gnt`), not a published LXX dataset. Do not rely on it.

---

## 3. cfabric-mcp / Context-Fabric — Verdict

### What it is

Context-Fabric (github.com/Context-Fabric/context-fabric) describes itself as "the next evolution of Text-Fabric" — a graph-based corpus engine that replaces TF's storage layer with memory-mapped arrays, adds a REST API layer, and ships `cfabric-mcp` as a monorepo subpackage (`libs/mcp`) providing an MCP server.

If functional, `cfabric-mcp` would let Claude (or any MCP client) run Text-Fabric graph queries as tools — analogous to how the Zotero MCP server works — without requiring Python in the client.

### Maturity assessment — DO NOT ADOPT YET

| Signal | Finding |
|---|---|
| GitHub stars | 6 |
| GitHub forks | 1 |
| PyPI publish | **NOT published** — `pip install context-fabric` fails with "No matching distribution found." The README badge claims PyPI publication but it is not live. |
| cfabric-mcp PyPI | Also not published |
| Releases/tags | 24 tags exist in the repo (install from source only) |
| Last commit | January 2026 (recent but sparse) |
| Issues open | 2 |

### Install path if you want to test from source

```bash
git clone https://github.com/Context-Fabric/context-fabric
cd context-fabric
pip install -e libs/core
pip install -e libs/mcp
cfabric-mcp --corpus /path/to/bhsa
```

This has NOT been verified in this session (PyPI path failed; source install not attempted).

### Verdict

Context-Fabric/cfabric-mcp is **pre-release vaporware from a tooling perspective** — conceptually sound, architecturally interesting, but not installable from PyPI, 6-star adoption, no community traction. It would let Claude run TF queries as MCP tools exactly as desired, but adopting it now means:
- Depending on an unstable, unpublished library
- Possible breaking changes at any tag
- No community support

**Recommendation**: Watch the repo. Do not build LXX/Vulgate pipeline infrastructure on it. Instead, use `text-fabric` 13.x directly from Python scripts (the proven path), and revisit cfabric-mcp when it publishes a stable PyPI release with >50 stars.

---

## 4. CoNLL-U → Text-Fabric Pipeline

### Situation

No maintained, published CoNLL-U→TF converter exists as a standalone tool. This is a verified negative: PyPI search and GitHub search found no `conllu2tf` or equivalent.

### The correct path: tf.convert.walker

TF ships its own conversion framework (`tf.convert.walker.CV`) designed exactly for this purpose. You write a `director(cv)` function that:
1. Opens the CoNLL-U file with the `conllu` Python library (`pip install conllu`)
2. Iterates sentences → tokens
3. Calls `cv.slot()` for each token (word = slot)
4. Calls `cv.node('sentence')`, `cv.node('clause')` etc. for hierarchical structure
5. Calls `cv.feature(node, attr=value)` to attach UD fields (lemma, UPOS, XPOS, deprel, head, feats)

The CV framework handles all TF internal wiring (otype, oslots, otext config).

### Effort estimate for UD_Latin-PROIEL → TF (Vulgate NT substrate)

| Task | Estimate |
|---|---|
| Write `director(cv)` for flat CoNLL-U (slots + sentence nodes + UD features) | 2-3 hours |
| Add dependency-edge layer (head→dependent edges as TF edge features) | 1-2 hours |
| Add section hierarchy (book/chapter/verse from sentence metadata) | 1-2 hours (PROIEL CoNLL-U has comment fields with source IDs) |
| Validation + round-trip check | 1-2 hours |
| **Total for working Vulgate NT TF dataset from UD_Latin-PROIEL** | **5-9 hours** |

For UD_Ancient_Greek-PROIEL (GNT alignment check), the same director works with minimal changes (~1-2 hours reuse). The `conllu` library (`EmilStenstrom/conllu`) is the right parser — well-maintained, handles all standard UD fields.

### Effort estimate for CenterBLC LXX → augmented with syntax

CenterBLC/LXX is already a TF dataset (morphology). It lacks syntax trees. To add them: the CATSS LXX (codykingham) has a compatible TF conversion from CCAT data. Merging would require feature-alignment work (~4-6 hours) but avoids rebuilding the base layer.

---

## 5. Summary Recommendation

**Single highest-leverage move**: acquire `CenterBLC/LXX` as the LXX substrate (MIT, complete Rahlfs 1935, already TF, `use("CenterBLC/LXX", version="1935")`) and write a `tf.convert.walker`-based converter for `UD_Latin-PROIEL` CoNLL-U to produce a Vulgate NT TF dataset. This combination:

- Eliminates the BoFM-style "no treebank, use Stanza on EModE" problem for LXX (morphology already done, in TF)
- Provides a real dependency treebank for the Vulgate NT (UD_Latin-PROIEL, CC BY-NC-SA 3.0) in ~5-9 hours of converter work
- Keeps everything in the native TF ecosystem so the same Python query patterns as BHSA work immediately
- Costs nothing vs. buying/licensing commercial resources

**Do not**: build on cfabric-mcp now (not on PyPI, 6 stars), rebuild LXX morphology from scratch (CenterBLC already did it), or wait for a Macula-LXX (it does not exist).

**Watch list**:
- Context-Fabric/context-fabric — check back when PyPI package appears
- CenterBLC/MT-LXX — unlicensed, no README now; may mature into a Macula→TF bridge
- UD_Ancient_Greek-PROIEL — identical converter to Latin-PROIEL gives you a second GNT dependency treebank for cross-checking against Macula

---

*Sources verified: github.com/annotation/text-fabric, github.com/CenterBLC (LXX, N1904, NA, SBLGNT, MT-LXX), github.com/ETCBC/bhsa, github.com/codykingham/catss_lxx, github.com/Context-Fabric/context-fabric, github.com/UniversalDependencies/UD_Latin-PROIEL, github.com/UniversalDependencies/UD_Ancient_Greek-PROIEL. PyPI install tests: text-fabric (SUCCESS 13.1.0), context-fabric (FAIL — not published), cfabric-mcp (FAIL — not published). Live TF load test: annotation/banks loaded and queried successfully (99 words, 5 node types).*
