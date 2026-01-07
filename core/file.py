from pathlib import Path
from typing import List, Dict
import csv
import io

from .result import Result


class File:
    """
    Represents one input TXT file containing multiple Result blocks.
    """

    def __init__(self, path: Path, display_name: str | None = None):
        self.path: Path = path
        self.display_name: str = display_name or path.name
        self.results: List[Result] = []

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

                # ---- New result block ----
                if line.startswith("#Parameters"):
                    current_result = Result()
                    current_result.config = cls._parse_config(line)
                    file_obj.results.append(current_result)
                    continue

                # ---- Description ----
                if line.startswith('#"') and current_result:
                    current_result.description = cls._parse_description(line[1:])
                    continue

                # ---- Comment / separator ----
                if line.startswith("#"):
                    continue

                # ---- Data ----
                if current_result:
                    parts = line.split()
                    if len(parts) == 2:
                        try:
                            x, y = map(float, parts)
                            current_result.data.append((x, y))
                        except ValueError:
                            pass

        return file_obj

    @staticmethod
    def _parse_config(line: str) -> Dict[str, float]:
        """
        Parse:
        #Parameters = {a=1; b=2; c=3}
        """
        content = line.split("{", 1)[1].rsplit("}", 1)[0]
        cfg: Dict[str, float] = {}

        for item in content.split(";"):
            if "=" in item:
                k, v = item.split("=")
                cfg[k.strip()] = float(v)

        return cfg

    @staticmethod
    def _parse_description(line: str) -> List[str]:
        """
        Parse:
        "Frequency / GHz"    "S2,1 (2) [Magnitude]"
        """
        return [s.strip() for s in line.replace('"', "").split("\t") if s]

    # ======================
    # Accessors
    # ======================
    def get_results(self) -> List[Result]:
        return self.results

    def get_result(self) -> List[Result]:
        # alias for convenience
        return self.results

    # ======================
    # Parameter classification
    # ======================
    def independent_parameters(self) -> Dict[str, List[float]]:
        """
        Parameters whose values vary across results (sweep variables).
        """
        if not self.results:
            return {}

        keys = self.results[0].config.keys()
        indep: Dict[str, List[float]] = {}

        for k in keys:
            values = [r.config.get(k) for r in self.results]
            if len(set(values)) > 1:
                indep[k] = values

        return indep

    def control_parameters(self) -> Dict[str, float]:
        """
        Parameters whose values are fixed across all results.
        """
        if not self.results:
            return {}

        keys = self.results[0].config.keys()
        ctrl: Dict[str, float] = {}

        for k in keys:
            values = {r.config.get(k) for r in self.results}
            if len(values) == 1:
                ctrl[k] = values.pop()

        return ctrl

    # ======================
    # Summary (console)
    # ======================
    def summary(self) -> None:
        print(f"\nFile: {self.display_name}")
        print(f"Results: {len(self.results)}")

        if not self.results:
            return

        desc = self.results[0].description
        indep = self.independent_parameters()
        ctrl = self.control_parameters()

        if desc:
            print(f"X-axis: {desc[0]}")
            if len(desc) > 1:
                print(f"Y-axis: {desc[1]}")

        print("Independent parameter(s):")
        if indep:
            for k, v in indep.items():
                print(f"  {k}: {sorted(set(v))}")
        else:
            print("  None")

        print("Control parameter(s):")
        if ctrl:
            for k, v in ctrl.items():
                print(f"  {k} = {v}")
        else:
            print("  None")

        print("\nResults detail:")
        for i, r in enumerate(self.results, 1):
            label = ", ".join(
                f"{k}={r.config[k]}" for k in indep
            ) if indep else "fixed"

            print(f"[{i}] {label} | points={r.count_data()}")

    # ======================
    # CSV Export (in-memory)
    # ======================
    def export_csv_bytes(self) -> Dict[str, bytes]:
        """
        Export CSVs as in-memory bytes (for Streamlit download).
        Returns: {filename: bytes}
        """
        outputs: Dict[str, bytes] = {}

        def write_csv(rows: List[dict]) -> bytes:
            buf = io.StringIO()
            writer = csv.DictWriter(buf, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
            return buf.getvalue().encode("utf-8")

        data_rows = []
        meta_rows = []
        config_rows = []

        for i, r in enumerate(self.results, 1):
            # data.csv
            for x, y in r.data:
                data_rows.append({
                    "file": self.display_name,
                    "result_id": i,
                    "x": x,
                    "y": y
                })

            # meta.csv
            meta_rows.append({
                "file": self.display_name,
                "result_id": i,
                "x_label": r.description[0] if r.description else "",
                "y_label": r.description[1] if len(r.description) > 1 else "",
                "points": r.count_data()
            })

            # config.csv
            for k, v in r.config.items():
                config_rows.append({
                    "file": self.display_name,
                    "result_id": i,
                    "parameter": k,
                    "value": v
                })

        if data_rows:
            outputs["data.csv"] = write_csv(data_rows)
        if meta_rows:
            outputs["meta.csv"] = write_csv(meta_rows)
        if config_rows:
            outputs["config.csv"] = write_csv(config_rows)

        return outputs
