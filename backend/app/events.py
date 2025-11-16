"""Event detection utilities for Mission Debrief AI."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

import numpy as np
import pandas as pd


@dataclass
class Event:
    type: str
    time_seconds: float
    severity: str
    description: str
    payload: Dict[str, Any]

    def as_dict(self) -> Dict[str, Any]:
        data = {
            "type": self.type,
            "time_seconds": self.time_seconds,
            "severity": self.severity,
            "description": self.description,
        }
        data.update(self.payload)
        return data


class FlightEventDetector:
    def __init__(self, df: pd.DataFrame):
        self.df = df.fillna(0)
        self.events: List[Event] = []

    def detect_all_events(self) -> List[Dict[str, Any]]:
        detectors = [
            self.detect_takeoff,
            self.detect_landing,
            self.detect_steep_turns,
            self.detect_stalls,
            self.detect_overspeed,
            self.detect_high_g,
        ]

        for detector in detectors:
            self.events.extend(detector())

        serialized = [event.as_dict() for event in self.events]
        serialized.sort(key=lambda e: e["time_seconds"])
        return serialized

    def detect_takeoff(self) -> List[Event]:
        events: List[Event] = []
        if "vertical_speed_fpm" not in self.df.columns:
            return events

        climbing = self.df[self.df["vertical_speed_fpm"] > 300]
        if climbing.empty:
            return events

        idx = climbing.index[0]
        events.append(
            Event(
                type="TAKEOFF",
                time_seconds=float(self.df.loc[idx, "time_seconds"]),
                severity="info",
                description="Takeoff detected via sustained climb",
                payload={
                    "altitude_ft": float(self.df.get("alt_msl_ft", pd.Series([0])).iloc[idx] if "alt_msl_ft" in self.df.columns else 0),
                    "airspeed_kt": float(self.df.get("airspeed_indicated_kt", pd.Series([0])).iloc[idx] if "airspeed_indicated_kt" in self.df.columns else 0),
                },
            )
        )
        return events

    def detect_landing(self) -> List[Event]:
        events: List[Event] = []
        if "alt_msl_ft" not in self.df.columns:
            return events

        last_segment = self.df.tail(max(3, int(len(self.df) * 0.2)))
        low_alt = last_segment[last_segment["alt_msl_ft"] < 300]
        if low_alt.empty:
            return events

        idx = low_alt.index[-1]
        events.append(
            Event(
                type="LANDING",
                time_seconds=float(self.df.loc[idx, "time_seconds"]),
                severity="info",
                description="Landing detected near ground with descent",
                payload={
                    "vertical_speed_fpm": float(self.df.get("vertical_speed_fpm", pd.Series([0])).iloc[idx] if "vertical_speed_fpm" in self.df.columns else 0),
                    "airspeed_kt": float(self.df.get("airspeed_indicated_kt", pd.Series([0])).iloc[idx] if "airspeed_indicated_kt" in self.df.columns else 0),
                },
            )
        )
        return events

    def detect_steep_turns(self) -> List[Event]:
        events: List[Event] = []
        if "roll_deg" not in self.df.columns:
            return events

        steep = self.df[self.df["roll_deg"].abs() > 30].copy()
        if steep.empty:
            return events

        steep["group"] = (steep.index.to_series().diff().fillna(0) > 5).cumsum()
        for _, group in steep.groupby("group"):
            if len(group) < 3:
                continue
            max_bank_idx = group["roll_deg"].abs().idxmax()
            max_bank = group.loc[max_bank_idx, "roll_deg"]
            severity = "warning" if abs(max_bank) > 45 else "info"
            events.append(
                Event(
                    type="STEEP_TURN",
                    time_seconds=float(group.loc[max_bank_idx, "time_seconds"]),
                    severity=severity,
                    description=f"Steep turn {abs(max_bank):.1f}° over {len(group)}s",
                    payload={
                        "max_bank_deg": float(max_bank),
                        "duration_seconds": int(len(group)),
                        "altitude_ft": float(group.get("alt_msl_ft", pd.Series([0])).iloc[0] if "alt_msl_ft" in group.columns else 0),
                    },
                )
            )
        return events

    def detect_stalls(self) -> List[Event]:
        events: List[Event] = []
        if "airspeed_indicated_kt" not in self.df.columns or "alt_msl_ft" not in self.df.columns:
            return events

        min_alt = self.df["alt_msl_ft"].min()
        suspected = self.df[(self.df["airspeed_indicated_kt"] < 50) & (self.df["alt_msl_ft"] > min_alt + 500)]
        for idx in suspected.index[:5]:
            events.append(
                Event(
                    type="STALL_WARNING",
                    time_seconds=float(self.df.loc[idx, "time_seconds"]),
                    severity="critical",
                    description=f"Low airspeed {self.df.loc[idx, 'airspeed_indicated_kt']:.0f} kt at {self.df.loc[idx, 'alt_msl_ft']:.0f} ft",
                    payload={
                        "airspeed_kt": float(self.df.loc[idx, "airspeed_indicated_kt"]),
                        "altitude_ft": float(self.df.loc[idx, "alt_msl_ft"]),
                    },
                )
            )
        return events

    def detect_overspeed(self) -> List[Event]:
        events: List[Event] = []
        if "airspeed_indicated_kt" not in self.df.columns:
            return events

        VNE = 200
        overspeed = self.df[self.df["airspeed_indicated_kt"] > VNE]
        for idx in overspeed.index[:10]:
            events.append(
                Event(
                    type="OVERSPEED",
                    time_seconds=float(self.df.loc[idx, "time_seconds"]),
                    severity="critical",
                    description=f"Overspeed {self.df.loc[idx, 'airspeed_indicated_kt']:.0f} kt (Vne {VNE})",
                    payload={
                        "airspeed_kt": float(self.df.loc[idx, "airspeed_indicated_kt"]),
                        "vne_kt": VNE,
                        "altitude_ft": float(self.df.get("alt_msl_ft", pd.Series([0])).iloc[idx] if "alt_msl_ft" in self.df.columns else 0),
                    },
                )
            )
        return events

    def detect_high_g(self) -> List[Event]:
        events: List[Event] = []
        if "normal_accel_g" not in self.df.columns:
            return events

        g_pos, g_neg = 3.8, -1.52
        exceed = self.df[(self.df["normal_accel_g"] > g_pos) | (self.df["normal_accel_g"] < g_neg)]
        for idx in exceed.index[:10]:
            g_load = self.df.loc[idx, "normal_accel_g"]
            events.append(
                Event(
                    type="HIGH_G_LOAD",
                    time_seconds=float(self.df.loc[idx, "time_seconds"]),
                    severity="warning",
                    description=f"High G load {g_load:.2f}G",
                    payload={
                        "g_load": float(g_load),
                        "altitude_ft": float(self.df.get("alt_msl_ft", pd.Series([0])).iloc[idx] if "alt_msl_ft" in self.df.columns else 0),
                    },
                )
            )
        return events


def compute_flight_summary(df: pd.DataFrame) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "total_duration_seconds": int(len(df)),
        "total_duration_minutes": round(len(df) / 60, 1),
    }

    if "alt_msl_ft" in df.columns:
        summary["max_altitude_ft"] = float(df["alt_msl_ft"].max())
        summary["min_altitude_ft"] = float(df["alt_msl_ft"].min())
        summary["avg_altitude_ft"] = float(df["alt_msl_ft"].mean())

    if "airspeed_indicated_kt" in df.columns:
        summary["max_airspeed_kt"] = float(df["airspeed_indicated_kt"].max())
        summary["avg_airspeed_kt"] = float(df["airspeed_indicated_kt"].mean())

    if "vertical_speed_fpm" in df.columns:
        summary["max_climb_rate_fpm"] = float(df["vertical_speed_fpm"].max())
        summary["max_descent_rate_fpm"] = float(df["vertical_speed_fpm"].min())

    if "roll_deg" in df.columns:
        summary["max_bank_angle_deg"] = float(df["roll_deg"].abs().max())

    if "normal_accel_g" in df.columns:
        summary["max_positive_g"] = float(df["normal_accel_g"].max())
        summary["max_negative_g"] = float(df["normal_accel_g"].min())

    if {"fuel_qty_left_gal", "fuel_qty_right_gal"}.issubset(df.columns):
        left = pd.to_numeric(df["fuel_qty_left_gal"], errors="coerce")
        right = pd.to_numeric(df["fuel_qty_right_gal"], errors="coerce")
        initial = (left.iloc[0] if not pd.isna(left.iloc[0]) else 0) + (
            right.iloc[0] if not pd.isna(right.iloc[0]) else 0
        )
        final = (left.iloc[-1] if not pd.isna(left.iloc[-1]) else 0) + (
            right.iloc[-1] if not pd.isna(right.iloc[-1]) else 0
        )
        summary["fuel_consumed_gal"] = float(initial - final)

    return summary
