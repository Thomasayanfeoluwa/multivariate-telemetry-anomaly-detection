"""
SWaT Project — Universal Environment and Path Resolution Utility

Automatically detects runtime environment (Kaggle GPU/CPU, Google Colab, or Local machine),
locates raw data files (normal.csv, attack.csv) and existing model artifacts,
and provisions a guaranteed writable output directory (e.g. /kaggle/working/swat-artifacts).
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict, Any, Optional


def resolve_project_paths(verbose: bool = True) -> Dict[str, Any]:
    """
    Robustly locate data, model artifacts, and output directories across
    Kaggle, Google Colab, and local development environments.

    Returns:
        dict containing:
            PROJECT_ROOT: Path
            DATA_RAW_DIR: Path to directory containing normal.csv and attack.csv
            ARTIFACT_DIR: Path to directory containing existing models/scalers
            OUTPUT_DIR: Guaranteed writable Path for saving retrained models & scores
            IS_KAGGLE: bool
            IS_COLAB: bool
    """
    # Bulletproof environment detection:
    # On Kaggle, os.name is posix (Linux) and either KAGGLE_KERNEL_RUN_TYPE env var exists or /kaggle/input exists.
    is_kaggle = (
        (os.environ.get("KAGGLE_KERNEL_RUN_TYPE") is not None) or
        (os.name != "nt" and Path("/kaggle/input").is_dir())
    )
    is_colab = (
        ("google.colab" in sys.modules) or
        (os.name != "nt" and Path("/content").is_dir() and not is_kaggle)
    )

    raw_data_dir: Optional[Path] = None
    artifact_dir: Optional[Path] = None
    output_dir: Optional[Path] = None
    project_root: Optional[Path] = None

    if is_kaggle:
        project_root = Path("/kaggle/working")
        output_dir = project_root / "swat-artifacts"
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Search /kaggle/input recursively for normal.csv
        for p in Path("/kaggle/input").rglob("normal.csv"):
            if p.is_file():
                raw_data_dir = p.parent
                break

        # 2. Search /kaggle/input recursively for existing artifacts (e.g. scaler.joblib or evaluation_sequences.npz)
        for p in Path("/kaggle/input").rglob("scaler.joblib"):
            if p.is_file():
                artifact_dir = p.parent
                break
        
        if artifact_dir is None:
            for p in Path("/kaggle/input").rglob("evaluation_sequences.npz"):
                if p.is_file():
                    artifact_dir = p.parent
                    break
        
        if artifact_dir is None:
            artifact_dir = output_dir

    elif is_colab:
        project_root = Path("/content")
        output_dir = project_root / "swat-artifacts"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Check drive or local content
        for p in project_root.rglob("normal.csv"):
            if p.is_file():
                raw_data_dir = p.parent
                break
        for p in project_root.rglob("scaler.joblib"):
            if p.is_file():
                artifact_dir = p.parent
                break
        if artifact_dir is None:
            artifact_dir = output_dir

    else:
        # Local Environment (Windows / Mac / Linux)
        cwd = Path.cwd().resolve()
        project_root = next(
            (
                d for d in [cwd, *cwd.parents]
                if (d / "requirements.txt").is_file()
            ),
            cwd
        )

        # Search for raw data
        for cand in [
            project_root / "data" / "raw",
            project_root / "swat-dataset",
            cwd / "data" / "raw",
            cwd / "swat-dataset",
        ]:
            if (cand / "normal.csv").is_file():
                raw_data_dir = cand
                break

        # Search for artifacts
        for cand in [
            project_root / "swat-artifacts",
            project_root / "models",
            cwd / "swat-artifacts",
            cwd / "models",
        ]:
            if (cand / "scaler.joblib").is_file() or (cand / "evaluation_sequences.npz").is_file():
                artifact_dir = cand
                break

        if artifact_dir is None:
            artifact_dir = project_root / "swat-artifacts"
            artifact_dir.mkdir(parents=True, exist_ok=True)

        output_dir = artifact_dir

    if verbose:
        env_name = "Kaggle (Linux/GPU)" if is_kaggle else ("Google Colab" if is_colab else f"Local ({sys.platform})")
        print(f"[PATH RESOLVER] Environment: {env_name}")
        print(f"  Project Root : {project_root}")
        print(f"  Raw Data Dir : {raw_data_dir} (exists: {raw_data_dir.is_dir() if raw_data_dir else False})")
        print(f"  Artifact Dir : {artifact_dir} (exists: {artifact_dir.is_dir() if artifact_dir else False})")
        print(f"  Output Dir   : {output_dir} (writable: {os.access(output_dir, os.W_OK)})")

    return {
        "PROJECT_ROOT": project_root,
        "DATA_RAW_DIR": raw_data_dir,
        "ARTIFACT_DIR": artifact_dir,
        "OUTPUT_DIR": output_dir,
        "IS_KAGGLE": is_kaggle,
        "IS_COLAB": is_colab,
    }
