"""Risk scoring and rule-based events for Mission Debrief AI."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

GA_SIGNALS = [
    ("alt_msl_ft", "Altitude", "ft", "left"),
    ("airspeed_indicated_kt", "Airspeed", "kt", "right"),
    ("vertical_speed_fpm", "Vertical Speed", "fpm", "left"),
    ("pitch_deg", "Pitch", "deg", "left"),
    ("roll_deg", "Roll", "deg", "left"),
    ("normal_accel_g", "Normal G", "g", "right"),
    ("afcs_on", "AFCS", "bool", "band"),
]

T38_SIGNALS = [
    ("egi_altitude", "EGI Altitude", "ft", "left"),
    ("adc_true_airspeed", "True Airspeed", "kt", "right"),
    ("adc_aoa_corrected", "AOA", "deg", "left"),
    ("nz_normal_accel", "Nz", "g", "right"),
    ("roll_rate_p", "Roll Rate", "deg/s", "left"),
    ("pitch_rate_q", "Pitch Rate", "deg/s", "left"),
]


def _column_exists(df: pd.DataFrame, column: str) -> bool:
    return column in df.columns


def compute_hf_index(df: pd.DataFrame) -> pd.Series:
    """Compute a simple human-factor risk index (0-100)."""

    components = []
    if _column_exists(df, "vertical_speed_fpm"):
        components.append(np.clip(np.abs(df["vertical_speed_fpm"]) / 1500, 0, 1.2))
    if _column_exists(df, "roll_deg"):
        components.append(np.clip(np.abs(df["roll_deg"]) / 45, 0, 1.2))
    if _column_exists(df, "normal_accel_g"):
        components.append(np.clip(np.abs(df["normal_accel_g"] - 1.0) / 1.5, 0, 1.2))
    if _column_exists(df, "adc_aoa_corrected"):
        components.append(np.clip(df["adc_aoa_corrected"] / 15.0, 0, 1.2))
    if _column_exists(df, "nz_normal_accel"):
        components.append(np.clip(np.abs(df["nz_normal_accel"]) / 4.0, 0, 1.2))

    if not components:
        return pd.Series(np.zeros(len(df)))

    stacked = np.vstack([c.fillna(0).to_numpy() for c in components])
    score = stacked.mean(axis=0)
    return pd.Series(np.clip(score * 80 + 10, 0, 100), index=df.index)


@dataclass
class RuleEvent:
    rule: str
    severity: str
    timestamp: float
    description: str
    values: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        return {
            "rule": self.rule,
            "severity": self.severity,
            "time_seconds": self.timestamp,
            "description": self.description,
            "values": self.values,
        }


def _value(df: pd.DataFrame, column: str, idx: int, default: Optional[float] = None) -> Optional[float]:
    if column in df.columns:
        value = df.iloc[idx][column]
        if pd.isna(value):
            return default
        return float(value)
    return default


def generate_rule_events(df: pd.DataFrame) -> List[Dict[str, Any]]:
    events: List[RuleEvent] = []
    if "hf_index" in df.columns:
        risk_segment = df[df["hf_index"] > 70]
        for idx in risk_segment.index:
            events.append(
                RuleEvent(
                    rule="HF_RISK_HIGH",
                    severity="warning",
                    timestamp=float(df.loc[idx, "time_seconds"]),
                    description="Human-factor risk exceeds threshold",
                    values={"hf_index": round(float(df.loc[idx, "hf_index"]), 1)},
                )
            )

    if {"roll_deg", "alt_msl_ft"}.issubset(df.columns):
        low_alt_bank = df[(df["alt_msl_ft"] < 800) & (df["roll_deg"].abs() > 30)]
        for idx in low_alt_bank.index:
            events.append(
                RuleEvent(
                    rule="LOW_ALTITUDE_BANK",
                    severity="critical" if abs(df.loc[idx, "roll_deg"]) > 45 else "warning",
                    timestamp=float(df.loc[idx, "time_seconds"]),
                    description="Steep bank near the ground",
                    values={
                        "alt_ft": round(float(df.loc[idx, "alt_msl_ft"]), 0),
                        "bank_deg": round(float(df.loc[idx, "roll_deg"]), 1),
                    },
                )
            )

    if {"adc_aoa_corrected", "nz_normal_accel"}.issubset(df.columns):
        aoa_margin = df[(df["adc_aoa_corrected"] > 15) & (df["nz_normal_accel"] > 3)]
        for idx in aoa_margin.index:
            events.append(
                RuleEvent(
                    rule="AOA_MARGIN_LOW",
                    severity="critical",
                    timestamp=float(df.loc[idx, "time_seconds"]),
                    description="High AOA with elevated Nz",
                    values={
                        "aoa_deg": round(float(df.loc[idx, "adc_aoa_corrected"]), 1),
                        "nz_g": round(float(df.loc[idx, "nz_normal_accel"]), 2),
                    },
                )
            )

    return [event.as_dict() for event in sorted(events, key=lambda e: e.timestamp)]


def build_signal_payload(df: pd.DataFrame, aircraft_type: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    signals = T38_SIGNALS if aircraft_type == "T38C" else GA_SIGNALS
    available_signals = [s for s in signals if _column_exists(df, s[0])]

    matrix_columns = ["time_seconds"] + [key for key, *_ in available_signals]
    signal_matrix = df[matrix_columns].copy().fillna(method="ffill").fillna(method="bfill")

    meta = [
        {"key": key, "label": label, "unit": unit, "axis": axis}
        for key, label, unit, axis in available_signals
    ]

    data = signal_matrix.to_dict(orient="records")
    return meta, data


def build_presets(df: pd.DataFrame) -> List[Dict[str, Any]]:
    presets: List[Dict[str, Any]] = []
    duration = float(df["time_seconds"].max()) if not df.empty else 0

    def clamp_window(start: float, length: float = 30) -> Tuple[float, float]:
        end = min(duration, start + length)
        return (start, end)

    if "vertical_speed_fpm" in df.columns:
        climb = df[df["vertical_speed_fpm"] > 300]
        if not climb.empty:
            start = float(climb.iloc[0]["time_seconds"])
            presets.append({"id": "takeoff", "label": "Takeoff", "window": clamp_window(start, 40)})

    if "alt_msl_ft" in df.columns:
        low_work = df[(df["alt_msl_ft"] > 200) & (df["alt_msl_ft"] < 1500)]
        if not low_work.empty:
            mid = float(low_work.iloc[len(low_work) // 2]["time_seconds"])
            presets.append({"id": "pattern", "label": "Pattern Work", "window": clamp_window(max(0, mid - 20), 40)})

    if "adc_aoa_corrected" in df.columns:
        high_aoa = df[df["adc_aoa_corrected"] > 12]
        if not high_aoa.empty:
            start = float(high_aoa.iloc[0]["time_seconds"] - 5)
            presets.append({"id": "high_aoa", "label": "High-AoA", "window": clamp_window(max(0, start), 25)})

    if not presets and duration:
        presets.append({"id": "full", "label": "Full Flight", "window": (0, duration)})

    return presets
