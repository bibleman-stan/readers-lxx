# Septuagint (LXX) Reader — Claude Code Instructions (thin stub)

Operated by the **unified orchestrator-Claude** at `C:\Users\bibleman\`. If you spawned in
this workspace, hand off to the user-home Claude (it has full cross-repo + substrate context).

**STATUS: substrate-assembly phase. NO ATU/sense-line work until the Greek textual fabric
reaches parity** (see `README.md` + `~/repos/atu-method/docs/substrate.md` — the Textual Fabric Doctrine). Fabric first.

**Substrate ACQUIRED 2026-05-27 (PARTIAL):** `CenterBLC/LXX` = full Rahlfs-1935 **gold morphology** in Text-Fabric; `UD_Ancient_Greek-PTNK` = **gold syntax for Genesis+Ruth ONLY** (the only LXX syntax treebank in existence); UD-Greek PROIEL/Perseus (calibration). Plus **CATSS mirrored** (lxxmorph 67 files + LXX↔MT parallel 51 files) from the at-risk 1994 server. All at `readers-lxx/private/substrate/` (this repo's gitignored folder — relocated 2026-05-27 from the shared `biblical-corpora/` container, "each project gets its intuitive data"). So LXX = gold morph corpus-wide, gold *syntax* only for a sample — between BoFM (none) and Vulgate (full gold). Stan to send the CATSS courtesy declaration (R. Kraft d.2023 — confirm current steward). Inventories: `research/SUBSTRATE-INVENTORY.md` + `research/TOOLING-TEXTFABRIC.md`.

- What this is: a colometric ATU reading edition of the Septuagint. Sibling to
  readers-tanakh/gnt/bofm/vulgate.
- Substrate plan + resource inventory + the hybrid pipeline: `README.md`.
- LXX is the **thinnest-syntax** corpus (no BHSA-equivalent). Its unique asset: CATSS word-aligns
  LXX↔BHS, so BHSA syntax can be **projected** onto the Greek for Hebrew-source books — but that
  projection is the GIGO trap below, not gold.
- Cross-corpus methodology canon: `~/repos/atu-method/docs/`. The method is a **Container, not
  an Originator** — it organizes what the fabric supports; fabric quality bounds the claims.
- GIGO guardrail (BoFM-2026-05-27 lesson): a source-language-anchored projection (CATSS×BHSA →
  Greek) is a candidate, NOT target gold; validate each projected break on the Greek
  bidirectional ATU test.
- License gate: CATSS is non-commercial-OK + requires a user declaration + attribution
  (Kraft/Tov/CCAT). This program is non-commercial → clear. The CCAT gopher source is at-risk —
  mirror early.
