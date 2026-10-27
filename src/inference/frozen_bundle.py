"""
Centralized loader for the frozen inference bundle.

Loads once at application start:
    - TCN checkpoint  (nb08_artifacts/tcn_preliminary/tcn_autoencoder_best.pth)
    - MinMaxScaler    (nb08_artifacts/scaler.joblib)
    - Frozen threshold (nb08_artifacts/frozen_thresholds.json -> thresholds.tcn)
    - Ordered feature list (from scaler.feature_names_in_)
    - Window size      (from evaluation_sequences.npz X_threshold_seq.shape[1])
    - Architecture     (channels, kernel_size, dilations from NB08 Section 7.1)

This is the single source of truth for the frozen inference configuration.
No other module in this application will re-declare these values.

Reference:
    NB13 Tests A + B established score parity at 5.215e-08 max abs diff
    across 181,031 sequences with 0 flag disagreements at the frozen
    threshold 0.003906734725460411.

Will modify, tune, or retrain. Load the frozen artifacts as-is.
"""

from __future__ import annotations

import json
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F


# --- Architecture (verbatim from NB08 Section 7.1 / NB13 Cell 2) ---

class CausalConv1d(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, dilation):
        super().__init__()
        self.left_padding = (kernel_size - 1) * dilation
        self.conv = nn.Conv1d(
            in_channels,
            out_channels,
            kernel_size=kernel_size,
            dilation=dilation,
            padding=0,
        )

    def forward(self, x):
        return self.conv(F.pad(x, (self.left_padding, 0)))


class TCNBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, dilation):
        super().__init__()
        self.conv1 = CausalConv1d(in_channels, out_channels, kernel_size, dilation)
        self.conv2 = CausalConv1d(out_channels, out_channels, kernel_size, dilation)
        self.activation = nn.ReLU()
        self.residual = (
            nn.Identity()
            if in_channels == out_channels
            else nn.Conv1d(in_channels, out_channels, kernel_size=1)
        )

    def forward(self, x):
        residual = self.residual(x)
        x = self.activation(self.conv1(x))
        x = self.activation(self.conv2(x))
        return self.activation(x + residual)


class TCNAutoencoder(nn.Module):
    def __init__(self, n_features, channels, kernel_size, dilations):
        super().__init__()
        if len(channels) != len(dilations):
            raise ValueError("Each TCN block must have a dilation value.")

        encoder_layers = []
        in_channels = n_features
        for out_channels, dilation in zip(channels, dilations):
            encoder_layers.append(TCNBlock(in_channels, out_channels, kernel_size, dilation))
            in_channels = out_channels
        self.encoder = nn.Sequential(*encoder_layers)

        decoder_layers = []
        reversed_channels = list(reversed(channels))
        reversed_dilations = list(reversed(dilations))
        for index, dilation in enumerate(reversed_dilations):
            current_channels = reversed_channels[index]
            next_channels = (
                reversed_channels[index + 1]
                if index + 1 < len(reversed_channels)
                else n_features
            )
            decoder_layers.append(
                CausalConv1d(current_channels, next_channels, kernel_size, dilation)
            )
            if index + 1 < len(reversed_dilations):
                decoder_layers.append(nn.ReLU())
        self.decoder = nn.Sequential(*decoder_layers)

    def forward(self, x):
        if x.ndim != 3:
            raise ValueError("Expected input shape (batch, timesteps, features).")
        x = x.transpose(1, 2).contiguous()
        x = self.encoder(x)
        x = self.decoder(x)
        return x.transpose(1, 2).contiguous()


# --- Frozen-bundle constants (verified by NB13 Cell 1 / Cell 2) ---

DEFAULT_CHANNELS: tuple[int, ...]     = (32, 32, 32, 32)
DEFAULT_KERNEL_SIZE: int              = 3
DEFAULT_DILATIONS: tuple[int, ...]    = (1, 2, 4, 8)
EXPECTED_PARAM_COUNT: int             = 40_554
EXPECTED_CHECKPOINT_BYTES: int        = 172_469
EXPECTED_N_FEATURES: int              = 42
EXPECTED_WINDOW: int                  = 30


class FrozenBundleError(RuntimeError):
    """Raised when the frozen bundle cannot be loaded or fails verification."""


@dataclass(frozen=True)
class FrozenBundle:
    """Loaded frozen TCN bundle. All fields are read-only after construction."""
    model: TCNAutoencoder
    scaler: Any                          # sklearn MinMaxScaler
    threshold: float
    feature_names: tuple[str, ...]
    window_size: int
    n_features: int
    device: torch.device
    channels: tuple[int, ...]
    kernel_size: int
    dilations: tuple[int, ...]
    metadata: dict = field(default_factory=dict)

    def score_scaled(self, scaled_window: np.ndarray) -> float:
        """Score one already-scaled (window_size, n_features) window."""
        scaled_window = np.asarray(scaled_window, dtype=np.float32)
        expected = (self.window_size, self.n_features)
        if scaled_window.shape != expected:
            raise FrozenBundleError(
                f"Expected window shape {expected}, got {scaled_window.shape}."
            )
        tensor = torch.as_tensor(
            scaled_window, dtype=torch.float32, device=self.device,
        ).unsqueeze(0)
        with torch.no_grad():
            recon = self.model(tensor)
            return float(((recon - tensor) ** 2).mean().item())

    def predict(self, window: np.ndarray) -> tuple[float, bool]:
        """Scale, score, and threshold one (window_size, n_features) window."""
        window = np.asarray(window, dtype=np.float32)
        expected = (self.window_size, self.n_features)
        if window.shape != expected:
            raise FrozenBundleError(
                f"Expected window shape {expected}, got {window.shape}."
            )
        # Pass a DataFrame with the scaler's feature names as columns so:
        #   (1) scikit-learn does not warn about missing feature names, and
        #   (2) the scaler's own feature-order validation runs, adding a
        #       redundant check on top of src.inference.validate.
        named = pd.DataFrame(window, columns=self.feature_names)
        scaled = self.scaler.transform(named).astype(np.float32)
        score = self.score_scaled(scaled)
        return score, bool(score > self.threshold)

def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise FrozenBundleError(f"{label} not found: {path}")


def load_frozen_bundle(root: Path | str, device: str = "cpu") -> FrozenBundle:
    """Load and verify the frozen inference bundle from a project root."""
    root = Path(root).resolve()

    ckpt_path   = root / "nb08_artifacts" / "tcn_preliminary" / "tcn_autoencoder_best.pth"
    scaler_path = root / "nb08_artifacts" / "scaler.joblib"
    frozen_path = root / "nb08_artifacts" / "frozen_thresholds.json"
    seqs_path   = root / "nb08_artifacts" / "evaluation_sequences.npz"

    _require_file(ckpt_path,   "TCN checkpoint")
    _require_file(scaler_path, "Scaler")
    _require_file(frozen_path, "Frozen thresholds")
    _require_file(seqs_path,   "Evaluation sequences (for window-size verification)")

    size = ckpt_path.stat().st_size
    if size != EXPECTED_CHECKPOINT_BYTES:
        raise FrozenBundleError(
            f"Checkpoint size {size} != expected {EXPECTED_CHECKPOINT_BYTES}. "
            "Refusing to load — this may not be the selected NB11 checkpoint."
        )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # tolerate scikit-learn version-drift warning
        scaler = joblib.load(scaler_path)

    if not hasattr(scaler, "feature_names_in_"):
        raise FrozenBundleError(
            "Scaler has no feature_names_in_; cannot verify feature order."
        )
    features = tuple(str(f) for f in scaler.feature_names_in_)
    if len(features) != EXPECTED_N_FEATURES:
        raise FrozenBundleError(
            f"Scaler has {len(features)} features, expected {EXPECTED_N_FEATURES}."
        )

    frozen = json.loads(frozen_path.read_text(encoding="utf-8"))
    if "thresholds" not in frozen or "tcn" not in frozen["thresholds"]:
        raise FrozenBundleError(
            "frozen_thresholds.json is missing thresholds.tcn."
        )
    threshold = float(frozen["thresholds"]["tcn"])

    with np.load(seqs_path) as seq:
        if "X_threshold_seq" not in seq.files:
            raise FrozenBundleError(
                "evaluation_sequences.npz missing X_threshold_seq."
            )
        window_size     = int(seq["X_threshold_seq"].shape[1])
        n_features_seq  = int(seq["X_threshold_seq"].shape[2])

    if window_size != EXPECTED_WINDOW:
        raise FrozenBundleError(
            f"Window size {window_size} != expected {EXPECTED_WINDOW}."
        )
    if n_features_seq != len(features):
        raise FrozenBundleError(
            f"evaluation_sequences.npz has {n_features_seq} features, "
            f"scaler has {len(features)}."
        )

    dev = torch.device(device)
    model = TCNAutoencoder(
        n_features=len(features),
        channels=list(DEFAULT_CHANNELS),
        kernel_size=DEFAULT_KERNEL_SIZE,
        dilations=list(DEFAULT_DILATIONS),
    ).to(dev)

    try:
        state = torch.load(ckpt_path, map_location=dev, weights_only=True)
    except TypeError:
        state = torch.load(ckpt_path, map_location=dev)
    if isinstance(state, dict) and "model_state_dict" in state:
        state = state["model_state_dict"]
    model.load_state_dict(state, strict=True)
    model.eval()

    param_count = sum(p.numel() for p in model.parameters() if p.requires_grad)
    if param_count != EXPECTED_PARAM_COUNT:
        raise FrozenBundleError(
            f"Parameter count {param_count} != expected {EXPECTED_PARAM_COUNT}."
        )

    metadata = {
        "checkpoint_relative_path": str(ckpt_path.relative_to(root)),
        "checkpoint_bytes": size,
        "scaler_type": type(scaler).__name__,
        "threshold_source": "frozen_thresholds.json/thresholds.tcn",
        "threshold_procedure": frozen.get("sources", {}).get("tcn", ""),
        "learned_percentile": frozen.get("learned_percentile"),
        "learned_interpolation": frozen.get("learned_interpolation"),
        "param_count": int(param_count),
        "device": str(dev),
    }

    return FrozenBundle(
        model=model,
        scaler=scaler,
        threshold=threshold,
        feature_names=features,
        window_size=window_size,
        n_features=len(features),
        device=dev,
        channels=tuple(DEFAULT_CHANNELS),
        kernel_size=DEFAULT_KERNEL_SIZE,
        dilations=tuple(DEFAULT_DILATIONS),
        metadata=metadata,
    )


if __name__ == "__main__":
    # Standalone smoke test. Run from the project root:
    #     python src/inference/frozen_bundle.py
    #
    # This entry point does not require src/inference/__init__.py; the
    # package file can be an empty placeholder added later when the
    # FastAPI app imports the module normally.
    import sys

    root = Path.cwd()
    if not (root / "nb08_artifacts").is_dir():
        print(f"ERROR: {root} does not contain nb08_artifacts/. Run from project root.")
        sys.exit(1)

    bundle = load_frozen_bundle(root)
    print("Frozen bundle loaded and verified:")
    print(f"  threshold:     {bundle.threshold!r}")
    print(f"  window_size:   {bundle.window_size}")
    print(f"  n_features:    {bundle.n_features}")
    print(f"  features[0]:   {bundle.feature_names[0]}")
    print(f"  features[-1]:  {bundle.feature_names[-1]}")
    print(f"  device:        {bundle.device}")
    print(f"  param_count:   {bundle.metadata['param_count']}")

    # Parity probe against NB13 Cell 2's first known score.
    with np.load(root / "nb08_artifacts" / "evaluation_sequences.npz") as seq:
        sample_window = seq["X_threshold_seq"][0]

    score = bundle.score_scaled(sample_window)
    print(f"  first-seq score (scaled already): {score!r}")
    print(f"  NB13 Cell 2 first score:          0.00071584")
    print(f"  |diff|:                           {abs(score - 0.00071584):.3e}")