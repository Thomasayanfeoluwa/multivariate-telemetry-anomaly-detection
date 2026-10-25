# NB12 Verification Report

Generated: 2026-10-25T19:19:09.312361Z

## Frozen baseline integrity

- NB08 checksums: 15 / 15 matched (Cell 6)
- NB11 checksums: 3 / 3 matched (Cell 6)
- No frozen artifact modified during the project

## Reproducibility checks

- 10 / 10 checks passed (Cell 8)
- TCN frozen threshold reproduces bit-for-bit from frozen scores
- |delta| = 0.00e+00

## Selection decision

- **Outcome A** (from NB11): TCN Autoencoder, w30, MinMax, seed 42
- Threshold: 0.003907 (99th percentile, linear interpolation)
- NB11 final report verified present and unambiguous

## Notebook workflow

- 12 / 12 workflow notebooks present in `notebooks/`
- Execution order verified (numeric prefix)
- NB11 and NB12 use PROJECT_ROOT discovery (portable code)

## Portability status

- 2 notebooks clean (NB01, NB09): 0 hardcoded paths
- 8 notebooks require editing before re-run outside Kaggle (NB02–NB08, NB10)
- 2 notebooks are documentation-only flags (NB11, NB12 — code is portable)
- Remediation steps documented in Cell 7 §2

## Environment

- Audit environment: Python 3.11.14, Windows 10, AMD64
- Packages pinned in `requirements.txt` (12 packages)
- Training environment: Kaggle Tesla T4, versions partially lost (only NumPy 2.1.3 preserved)
- GPU: not available in audit environment (expected — audit is CPU-bound)

## Known limitations

- 15 limitations cataloged in Cell 9
- None affect the TCN selection
- 3 affect a from-scratch reproduction: environment drift, seed metadata, path portability

## Reproduction instructions

1. Ensure `data/raw/` contains normal.csv, attack.csv, List_of_attacks_Final.xlsx
2. Ensure `nb08_artifacts/`, `nb09_artifacts/`, `nb10_artifacts/`, `nb11_artifacts/` are present
3. `pip install -r nb12_artifacts/requirements.txt`
4. Open `notebooks/12_reproducibility.ipynb` in a fresh kernel
5. Run all cells top to bottom
6. Cell 7b will report portability status of NB01–NB10; expect 8 flagged (real issues) and 2 flagged (documentation only)
7. To fully re-run NB01–NB10, apply the mechanical portability edits described in Cell 7 §2
8. All NB12 outputs are written to `nb12_artifacts/` — nothing is overwritten elsewhere
