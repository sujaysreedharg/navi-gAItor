"""Flight data parser supporting GA (Cirrus SR20) and T-38C telemetry."""
from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
import re
from typing import Dict, Tuple

import pandas as pd

from .config import get_settings

settings = get_settings()


@dataclass
class ParsedFlight:
    """Container for parsed telemetry."""

    dataframe: pd.DataFrame
    metadata: Dict[str, str]


class FlightDataParser:
    """Parse and normalize Garmin G1000 and T-38C CSV exports."""

    GARMIN_COLUMN_MAP = {
        "Lcl Date": "date",
        "Lcl Time": "time",
        "Latitude": "lat",
        "Longitude": "lon",
        "AltMSL": "alt_msl_ft",
        "AltInd": "alt_indicated_ft",
        "IAS": "airspeed_indicated_kt",
        "TAS": "airspeed_true_kt",
        "GndSpd": "groundspeed_kt",
        "VSpd": "vertical_speed_fpm",
        "Pitch": "pitch_deg",
        "Roll": "roll_deg",
        "HDG": "heading_deg",
        "TRK": "track_deg",
        "LatAc": "lateral_accel_g",
        "NormAc": "normal_accel_g",
        "E1 RPM": "engine_rpm",
        "E1 FFlow": "fuel_flow_gph",
        "E1 OilT": "oil_temp_f",
        "E1 OilP": "oil_pressure_psi",
        "E1 MAP": "manifold_pressure_hg",
        "E1 %Pwr": "engine_power_pct",
        "FQtyL": "fuel_qty_left_gal",
        "FQtyR": "fuel_qty_right_gal",
        "OAT": "outside_air_temp_c",
        "WndSpd": "wind_speed_kt",
        "WndDr": "wind_direction_deg",
        "AfcsOn": "afcs_on",
    }

    T38_COLUMN_MAP = {
        "IRIG_TIME": "time",
        "GPS_ALTITUDE": "alt_msl_ft",
        "ADC_PRESSURE_ALTITUDE": "alt_pressure_ft",
        "ADC_COMPUTED_AIRSPEED": "airspeed_indicated_kt",
        "ADC_TRUE_AIRSPEED": "airspeed_true_kt",
        "GPS_SPEED": "groundspeed_kt",
        "EGI_PITCH_ANGLE": "pitch_deg",
        "EGI_ROLL_ANGLE": "roll_deg",
        "EGI_TRUE_HEADING": "heading_deg",
        "PITCH_RATE_Q": "pitch_rate_dps",
        "ROLL_RATE_P": "roll_rate_dps",
        "YAW_RATE_R": "yaw_rate_dps",
        "NZ_NORMAL_ACCEL": "normal_accel_g",
        "NY_LATERAL_ACCEL": "lateral_accel_g",
        "ADC_MACH": "mach_number",
        "ADC_AOA_CORRECTED": "angle_of_attack_deg",
        "LEFT_ENGINE_RPM_N1": "left_engine_rpm_pct",
        "RIGHT_ENGINE_RPM_N1": "right_engine_rpm_pct",
    }

    def parse(self, file_bytes: bytes) -> ParsedFlight:
        df = self._read_csv(file_bytes)
        metadata = self._parse_metadata(file_bytes)
        aircraft_type = self._detect_aircraft_type(df)
        metadata["detected_aircraft"] = aircraft_type

        normalized_df = self._normalize(df, aircraft_type)
        normalized_df = normalized_df.dropna(how="all")

        return ParsedFlight(normalized_df.reset_index(drop=True), metadata)

    def _read_csv(self, file_bytes: bytes) -> pd.DataFrame:
        try:
            df = pd.read_csv(BytesIO(file_bytes), comment="#", low_memory=False)
        except Exception:
            lines = file_bytes.decode("utf-8", errors="ignore").splitlines()
            data_start = 0
            for i, line in enumerate(lines):
                if line and not line.startswith("#"):
                    data_start = i
                    break
            csv_data = "\n".join(lines[data_start:])
            df = pd.read_csv(BytesIO(csv_data.encode()), low_memory=False)
        df.columns = [str(c).strip() for c in df.columns]
        return df

    def _parse_metadata(self, file_bytes: bytes) -> Dict[str, str]:
        lines = file_bytes.decode("utf-8", errors="ignore").splitlines()
        metadata: Dict[str, str] = {}

        if lines and lines[0].startswith("#airframe_info"):
            for match in re.finditer(r"(\w+)=\"([^\"]+)\"", lines[0]):
                metadata[match.group(1)] = match.group(2)

        return metadata

    def _detect_aircraft_type(self, df: pd.DataFrame) -> str:
        columns_lower = [str(c).strip().lower() for c in df.columns]
        if "irig_time" in columns_lower:
            return "T38C"
        if "lcl time" in columns_lower or "lcl date" in columns_lower:
            return "CIRRUS_SR20"
        return "UNKNOWN"

    def _normalize(self, df: pd.DataFrame, aircraft_type: str) -> pd.DataFrame:
        column_map = self.T38_COLUMN_MAP if aircraft_type == "T38C" else self.GARMIN_COLUMN_MAP
        normalized = df.copy()

        for original, standard in column_map.items():
            if original in normalized.columns:
                normalized[standard] = normalized[original]

        normalized["time_seconds"] = range(len(normalized))

        numeric_columns = [
            "alt_msl_ft",
            "alt_indicated_ft",
            "airspeed_indicated_kt",
            "airspeed_true_kt",
            "groundspeed_kt",
            "vertical_speed_fpm",
            "pitch_deg",
            "roll_deg",
            "heading_deg",
            "normal_accel_g",
            "engine_rpm",
            "fuel_flow_gph",
            "fuel_qty_left_gal",
            "fuel_qty_right_gal",
        ]

        for col in numeric_columns:
            if col in normalized.columns:
                normalized[col] = pd.to_numeric(normalized[col], errors="coerce")

        if "afcs_on" in normalized.columns:
            normalized["afcs_on"] = (
                normalized["afcs_on"]
                .astype(str)
                .str.strip()
                .str.lower()
                .apply(lambda x: 1 if x in {"1", "true", "on", "y"} else 0)
            )

        return normalized


def parse_flight(file_bytes: bytes) -> pd.DataFrame:
    parser = FlightDataParser()
    parsed = parser.parse(file_bytes)
    return parsed.dataframe


def parse_flight_with_metadata(file_bytes: bytes) -> Tuple[pd.DataFrame, Dict[str, str]]:
    parser = FlightDataParser()
    parsed = parser.parse(file_bytes)
    return parsed.dataframe, parsed.metadata
