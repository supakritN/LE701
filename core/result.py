from typing import Dict, List, Tuple, Any
import json


class Result:
    """
    One simulation / measurement result (one block).

    Responsibilities
    ----------------
    - Hold raw parsed data
    - Hold band (dip) analysis results
    """

    def __init__(self):
        # ----------------------
        # Raw parsed content
        # ----------------------
        self.config: Dict[str, float] = {}
        self.description: List[str] = []
        self.data: List[Tuple[float, float]] = []

        # ----------------------
        # Band (dip) analysis
        # ----------------------
        self.bands: List[Any] = []     # List[Band]
        self.n_bands: int = 0           # number of dips
        self.band_valid: bool = True    # False if extraction failed

    # ----------------------
    # Band setters
    # ----------------------
    def set_bands(self, bands: List[Any]) -> None:
        """
        Store extracted bands and auto-detect dip count.
        """
        self.bands = bands
        self.n_bands = len(bands)

    def invalidate_bands(self) -> None:
        """
        Mark dip extraction as invalid.
        """
        self.bands = []
        self.n_bands = 0
        self.band_valid = False

    # ----------------------
    # Accessors (existing)
    # ----------------------
    def get_description(self) -> List[str]:
        return self.description

    def get_config(self) -> Dict[str, float]:
        return self.config

    def get_config_json(self) -> str:
        return json.dumps(self.config, indent=2)

    def get_data(self) -> List[Tuple[float, float]]:
        return self.data

    def count_data(self) -> int:
        return len(self.data)

    # ----------------------
    # Debug representation
    # ----------------------
    def __repr__(self) -> str:
        return (
            "Result("
            f"params={len(self.config)}, "
            f"points={len(self.data)}, "
            f"bands={self.n_bands}, "
            f"valid={self.band_valid}"
            ")"
        )
