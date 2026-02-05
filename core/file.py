from pathlib import Path
from typing import List, Dict
import csv
import io
from collections import defaultdict, Counter

import pandas as pd

from .result import Result
from math_utils.signal_feature import extract_dips


class File:
    """
    Represents one input TXT file containing multiple Result blocks.
    """

    def __init__(self, path: Path, display_name: str | None = None):
        self.path: Path = path
        self.display_name: str = display_name or path.name
        self.results: List[Result] = []

        # Sweep overview (built after parsing)
        self.overview: Dict[str, pd.DataFrame] = {}

    # ======================
    # Parsing
    # ======================
    @classmethod
    def from_txt(cls, path: Path, display_name: str | None = None) -> "File":
        file_obj = cls(path, display_name)
        current_result: Result | None = None

        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue

                if line.startswith("#Parameters"):
                    current_result = Result()
                    current_result.config = cls._parse_config(line)
                    file_obj.results.append(current_result)
                    continue

                if line.startswith('#"') and current_result:
                    current_result.description = cls._parse_description(line[1:])
                    continue

                if line.startswith("#"):
                    continue

                if current_result:
                    parts = line.split()
                    if len(parts) == 2:
                        try:
                            x, y = map(float, parts)
                            current_result.data.append((x, y))
                        except ValueError:
                            pass

        file_obj._build_overview()
        return file_obj

    # ======================
    # Parsing helpers
    # ======================
    @staticmethod
    def _parse_config(line: str) -> Dict[str, float]:
        content = line.split("{", 1)[1].rsplit("}", 1)[0]
        cfg: Dict[str, float] = {}
        for item in content.split(";"):
            if "=" in item:
                k, v = item.split("=")
                cfg[k.strip()] = float(v)
        return cfg

    @staticmethod
    def _parse_description(line: str) -> List[str]:
        return [s.strip() for s in line.replace('"', "").split("\t") if s]

    # ======================
    # Sweep overview
    # ======================
    def _build_overview(self) -> None:
        self.overview = {}
        if not self.results:
            return

        param_values = defaultdict(list)
        for r in self.results:
            for k, v in r.config.items():
                param_values[k].append(v)

        for sweep_param, values in param_values.items():
            uniq = sorted(set(values))
            if len(uniq) <= 1:
                continue

            rows = [{
                "Parameter": f"[SWEEP] {sweep_param}",
                "Value(s)": ", ".join(map(str, uniq))
            }]

            for p, vals in param_values.items():
                if p == sweep_param:
                    continue
                if len(set(vals)) == 1:
                    rows.append({
                        "Parameter": p,
                        "Value(s)": str(vals[0])
                    })

            self.overview[sweep_param] = pd.DataFrame(rows)

    # ======================
    # Dip analysis (compute once)
    # ======================
    def analyze_bands_once(self) -> None:
        for r in self.results:
            if r.n_bands > 0 or not r.band_valid:
                continue
            try:
                bands = extract_dips(r.data)
                r.set_bands(bands)
            except Exception:
                r.invalidate_bands()

    # ======================
    # Dip summary (for UI)
    # ======================
    def dip_summary(self) -> Dict[str, int | None]:
        counts = Counter(
            r.n_bands for r in self.results if r.band_valid
        )
        if not counts:
            return {"expected": None}
        return {"expected": counts.most_common(1)[0][0]}
