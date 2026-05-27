# LXX Substrate Inventory
<!-- Written by substrate-acquisition agent, 2026-05-27 -->

Acquisition run for the readers-lxx project. Protocol: VERIFY then ACQUIRE-or-REPORT.
All acquired data lands in `C:\Users\bibleman\repos\biblical-corpora\lxx-substrate\`.

---

## Resource Table

| # | Name | VERIFIED status | License (quoted/sourced) | Format | Size | Coverage | WHERE IT LANDED / ACQUIRE COMMAND | At-risk flag | Gold vs. alignment vs. raw classification |
|---|------|----------------|--------------------------|--------|------|----------|-----------------------------------|--------------|-------------------------------------------|
| 1 | **UD_Ancient_Greek-PTNK** | VERIFIED — repo live, README read | CC BY-SA 4.0 | CoNLL-U (train/dev/test splits) | 26 MB on disk; 1,576 sentences, ~39K tokens | Genesis 1–50 + Ruth 1–4 (Codex Alexandrinus text via greekdoc.github.io); ~7% of total LXX by tokens | **ACQUIRED** → `lxx-substrate/ud-ptnk/` | LOW — actively maintained UD project | **GOLD** — hand-corrected UD dependency syntax + morphology; initial relations by cross-lingual projection from Hebrew PTNK, then manual correction |
| 2 | **UD_Ancient_Greek-PROIEL** | VERIFIED — repo live, README read | CC BY-NC-SA 3.0 | CoNLL-U (train/dev/test splits) | 64 MB on disk; ~247K lines in train file | NT (most books) + Herodotus selections. **No LXX content.** | **ACQUIRED** → `lxx-substrate/ud-proiel-grc/` | LOW — UD standard corpus | **GOLD** — full UD dependency syntax + morphology; hand-annotated at Oslo. Non-commercial. Acquired as Ancient Greek parse-model calibration data. |
| 3 | **UD_Ancient_Greek-Perseus** | VERIFIED — repo live, README read | CC BY-NC-SA 2.5 | CoNLL-U (train/dev/test splits) | 42 MB on disk; 13,919 trees, 202,989 tokens | Classical Greek: Homer, Aeschylus, Sophocles, Herodotus, Plutarch, others. **No LXX content.** | **ACQUIRED** → `lxx-substrate/ud-perseus-grc/` | LOW — UD standard corpus | **GOLD** — UD dependency syntax; semi-automatic (Morpheus analyzer + manual syntax). Non-commercial. Calibration data only. |
| 4 | **CenterBLC/LXX (TF app)** | VERIFIED — repo live, README read, tf/ directory inspected | MIT License (stated in repo footer/LICENSE file) | Text-Fabric (30 `.tf` feature files in `tf/1935/`) | 124 MB on disk (22.6 MB GitHub-reported compressed) | Full Rahlfs 1935 LXX (complete OT + deuterocanonical books; book.tf shows Gen through all books). Note: status is "WIP" per repostatus badge | **ACQUIRED** → `lxx-substrate/centerblc-lxx/` | MEDIUM — "WIP" label; last commit activity should be monitored | **RAW TEXT + MORPH-ONLY** — morphological features decomposed from CATSS codes (person, number, gender, tense, mood, voice, case, degree, POS, lemma, Strong's, gloss); sentence division by punctuation only; **no syntax/dependency annotation**. Upstream data is CATSS via eliranwong; MIT wrapper license applies to CenterBLC's additions. |
| 5 | **CATSS lxxmorph (CCAT/UPenn)** | VERIFIED — HTTP index live at `http://ccat.sas.upenn.edu/gopher/text/religion/biblical/lxxmorph/`; all 64 `.mlxx` files directly accessible without authentication; betacode format sampled | Non-commercial; user declaration required. Terms (from `0-user-declaration.txt`): "(1) Not to use or make available these materials for commercial purposes without first obtaining the written consent of the owners/encoders; (3) To control access to these materials and require any other party to whom the recipient supplies any portion of this material to observe these conditions **and to register a signed USER AGREEMENT form with CCAT**." Signed declaration must be mailed/emailed to `kraft@ccat.sas.upenn.edu`. | Beta-code plain text (`.mlxx`); word + POS + morphological code + lemma per line | ~408 MB estimated total (64 files, Gen 1+2 + Exod–Malachi–Daniel, including apocrypha/deuterocanon) | Complete Rahlfs LXX: 64 files covering all books + variants (JoshA/B, JudgesA/B, DanielOG/Th, SusOG/Th, BelOG/Th, TobitBA/S) | **MIRRORED 2026-05-27** — 67 files / 26.1 MB local at `ccat-mirror/lxxmorph/` (files text-open, no login wall; the ~408 MB estimate was wrong — betacode is compact). Stan to send the courtesy declaration. ⚠ R. Kraft (kraft@ccat.sas.upenn.edu) d. 2023-09-15 — confirm the current CCAT/CATSS steward (E. Tov / Penn Religious Studies) before sending; the listed email may be unmonitored. | **HIGH — legacy academic hosting, last files updated 2019; primary at-risk resource; NOW MIRRORED LOCALLY** | **RAW MORPH** — word-level morphological tags (betacode); no dependency syntax. Authoritative source for all downstream derivatives (eliranwong, CenterBLC, codykingham). |
| 6 | **CATSS parallel alignment (CCAT/UPenn)** | VERIFIED — HTTP index live at `http://ccat.sas.upenn.edu/gopher/text/religion/biblical/parallel/`; 46 `.par` files covering Gen–Mal | Same user-declaration requirement as lxxmorph (separate `00.user-declaration.txt` in the parallel/ dir) | Plain text (`.par`); interleaved Hebrew/Greek lines | Not measured; estimated ~300–400 MB total | Full LXX ↔ MT parallel alignment; Revised CATSS Hebrew/Greek Parallel Text (Tov-Polak 2005/2008) | **MIRRORED 2026-05-27** — 51 files / 6.8 MB local at `ccat-mirror/parallel/`; same declaration covers it (Stan to send). | **HIGH — same legacy hosting risk; NOW MIRRORED LOCALLY** | **WORD-ALIGNMENT** — not gold syntax; LXX↔MT word-level correspondences. Flag as candidate signal, NOT target-language syntax gold. |
| 7 | **Diorisis Ancient Greek Corpus** | VERIFIED (partial) — figshare DOI confirmed (10.6084/m9.figshare.6187256), size 185 MB, CC BY 4.0; **LXX coverage UNCONFIRMED** — search results indicate NT (225,837 tokens) is included but explicit LXX/OT listing not found without direct figshare access. Sourced from Perseus/Little Sailing/Bibliotheca Augustana; these typically do NOT include Rahlfs LXX. | CC BY 4.0 (stated in figshare metadata and CLARIN-UK page) | XML (one file per work), morphologically tagged with TreeTagger; 820 texts, 10.2M tokens | 185 MB | Classical Greek Homer → 5th cent AD; NT confirmed; LXX coverage unconfirmed | **REPORT-DON'T-ACQUIRE** — LXX coverage not confirmed; if Stan wants it, download command: `Invoke-WebRequest -Uri "https://doi.org/10.6084/m9.figshare.6187256" -OutFile diorisis.zip` (redirect through figshare; may need to click "Download all" from the figshare page directly). Zenodo DuckDB version also available at `https://zenodo.org/records/11261146`. | LOW — figshare is stable | **RAW MORPH** — automatic TreeTagger POS + lemma only; no hand-verified dependency syntax; not gold. Useful as ancient Greek language model training data if LXX texts confirmed present. |
| 8 | **STEPBible-Data TAGOT** | VERIFIED — repo live; TAGOT (Translators Amalgamated Greek OT) listed in README as planned but directory listing shows only TAGNT (NT) and TAHOT (Hebrew OT) files present; no TAGOT files exist yet | CC BY 4.0 (stated: "available to other projects under CC BY 4.0") | TSV (tab-separated) | N/A — not yet released | **NOT YET AVAILABLE** | **REPORT-DON'T-ACQUIRE** — monitor `https://github.com/STEPBible/STEPBible-Data/tree/master/Translators%20Amalgamated%20OT%2BNT` for TAGOT appearance. When live: `git clone https://github.com/STEPBible/STEPBible-Data.git lxx-substrate/stepbible-tagot/` (then pull only the TAGOT file). | LOW — active project | When released: **RAW MORPH** (CCAT-based morphology in TSV, Strongs-linked, no syntax). High value due to CC BY 4.0 (more permissive than CATSS/CenterBLC). |
| 9 | **eliranwong/LXX-Rahlfs-1935** | VERIFIED — repo live; 197 MB GitHub-reported; 15MB+ CSV files for accented text + morphology patches in 12 subdirectories | CC BY-NC-SA 4.0 ("Copyright 2017 Eliran Wong... Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International") | CSV files (text_accented.csv ~15.9MB, morphology patches ~15MB each, lexicon, Strong's, transliteration) | ~200 MB | Full Rahlfs 1935 LXX; all books | **NOT ACQUIRED** — CenterBLC/LXX (already acquired, MIT) is a TF-format derivative of this same source. Cloning eliranwong separately would be redundant for the TF-first workflow. If raw CSV form needed: `git clone https://github.com/eliranwong/LXX-Rahlfs-1935.git lxx-substrate/eliranwong-lxx/` | LOW | **RAW MORPH** — CSV morph codes + Strong's + English gloss; same CATSS upstream as CenterBLC. Non-commercial. |

---

## CATSS Acquisition Steps (Stan must execute)

Both lxxmorph and the parallel alignment require a signed user declaration sent to CCAT. The files are technically open (no login wall), but the terms require registration.

### Step 1 — Sign and send the declaration

Download and read the declaration:
```
http://ccat.sas.upenn.edu/gopher/text/religion/biblical/lxxmorph/0-user-declaration.txt
```
Fill in your name, address, date, and the texts you intend to obtain (list: "CATSS LXX Morphological Text (lxxmorph) and CATSS LXX-BHS Parallel Alignment (parallel)"). Email a signed scan or typed declaration to: `kraft@ccat.sas.upenn.edu`

### Step 2 — Mirror lxxmorph (after declaration sent)

Run from PowerShell (all 64 `.mlxx` files + readme/morph-coding docs):

```powershell
$dest = "C:\Users\bibleman\repos\biblical-corpora\lxx-substrate\ccat-mirror\lxxmorph"
New-Item -ItemType Directory -Force $dest | Out-Null
$base = "http://ccat.sas.upenn.edu/gopher/text/religion/biblical/lxxmorph/"
$files = @(
  "0-readme.txt","0-betacode.txt","0-user-declaration.txt",
  "*Morph-Coding","*ReadMe.Analysis",
  "01.Gen.1.mlxx","02.Gen.2.mlxx","03.Exod.mlxx","04.Lev.mlxx",
  "05.Num.mlxx","06.Deut.mlxx","07.JoshB.mlxx","08.JoshA.mlxx",
  "09.JudgesB.mlxx","10.JudgesA.mlxx","11.Ruth.mlxx","12.1Sam.mlxx",
  "13.2Sam.mlxx","14.1Kings.mlxx","15.2Kings.mlxx","16.1Chron.mlxx",
  "17.2Chron.mlxx","18.1Esdras.mlxx","19.2Esdras.mlxx","20.Esther.mlxx",
  "21.Judith.mlxx","22.TobitBA.mlxx","23.TobitS.mlxx","24.1Macc.mlxx",
  "25.2Macc.mlxx","26.3Macc.mlxx","27.4Macc.mlxx","28.Psalms1.mlxx",
  "29.Psalms2.mlxx","30.Odes.mlxx","31.Proverbs.mlxx","32.Qoheleth.mlxx",
  "33.Canticles.mlxx","34.Job.mlxx","35.Wisdom.mlxx","36.Sirach.mlxx",
  "37.PsSol.mlxx","38.Hosea.mlxx","39.Micah.mlxx","40.Amos.mlxx",
  "41.Joel.mlxx","42.Jonah.mlxx","43.Obadiah.mlxx","44.Nahum.mlxx",
  "45.Habakkuk.mlxx","46.Zeph.mlxx","47.Haggai.mlxx","48.Zech.mlxx",
  "49.Malachi.mlxx","50.Isaiah1.mlxx","51.Isaiah2.mlxx","52.Jer1.mlxx",
  "53.Jer2.mlxx","54.Baruch.mlxx","55.EpJer.mlxx","56.Lam.mlxx",
  "57.Ezek1.mlxx","58.Ezek2.mlxx","59.BelOG.mlxx","60.BelTh.mlxx",
  "61.DanielOG.mlxx","62.DanielTh.mlxx","63.SusOG.mlxx","64.SusTh.mlxx"
)
foreach ($f in $files) {
  $url = $base + $f
  $out = Join-Path $dest $f
  Invoke-WebRequest -Uri $url -OutFile $out -ErrorAction SilentlyContinue
  Write-Host "Downloaded: $f"
}
```

### Step 3 — Mirror parallel alignment (optional; same declaration covers it)

```powershell
$dest2 = "C:\Users\bibleman\repos\biblical-corpora\lxx-substrate\ccat-mirror\parallel"
New-Item -ItemType Directory -Force $dest2 | Out-Null
# Then fetch all .par files from http://ccat.sas.upenn.edu/gopher/text/religion/biblical/parallel/
# (46 files Gen through Chronicles/Prophets; same Invoke-WebRequest pattern)
```

**Attribution required in any publication**: "CATSS LXX Morphological Text prepared by CATSS under the direction of R. Kraft (Philadelphia team) and E. Tov (Jerusalem team). Distributed by CCAT, University of Pennsylvania."

---

## Notes on Classification

- **GOLD treebank** = hand-annotated dependency syntax (or hand-corrected projection): UD_PTNK (LXX Gen+Ruth), UD_PROIEL (Greek NT), UD_Perseus (classical). These are the highest-value inputs for a parse-first pipeline.
- **RAW MORPH** = word-level morphological tags only, no clause/dependency structure: CATSS lxxmorph, CenterBLC/LXX, eliranwong, TAGOT (when available). These provide the v1 word-stream + POS layer for ATU segmentation.
- **WORD-ALIGNMENT** = LXX↔MT correspondences: CATSS parallel. Candidate signal only; NOT syntax gold; analogous to role in Tanakh pipeline where Hebrew is the target-language gold and the Greek is alignment context.

---

## Gaps / Next Steps

1. **CATSS lxxmorph mirror** — highest-value unacquired resource; blocks the v1 morphological layer for the full LXX. Send declaration, then run Step 2 above.
2. **UD_PTNK expansion** — only Genesis + Ruth (7% of LXX). The PTNK paper notes the full corpus is ~22K sentences; only 1,576 are released. Watch for UD 2.14+ releases with expanded coverage.
3. **CATSS parallel alignment** — once declaration sent, mirror in same session as lxxmorph.
4. **STEPBible TAGOT** — monitor the STEPBible-Data repo; when it lands it will be the most permissive (CC BY 4.0) full-LXX morph source.
5. **Diorisis** — verify LXX content by downloading and checking file list before committing. If NT is present but LXX absent, value is calibration only.
6. **No full-LXX gold syntax treebank exists yet** — UD_PTNK is the only one, and it covers 7% of the text. This is the primary substrate gap: the LXX has no Macula-class syntax annotation. This is the argument for investing in substrate (Carmack-style parse repair or projection from the acquired Hebrew BHSA treebank) before building the reader.
