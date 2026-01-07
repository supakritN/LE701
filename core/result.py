from typing import Dict, List, Tuple
import json


class Result:
    """
    One simulation / measurement result.
    """

    def __init__(self):
        self.config: Dict[str, float] = {}
        self.description: List[str] = []
        self.data: List[Tuple[float, float]] = []

    # ----------------------
    # Accessors
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
    # Representation
    # ----------------------
    def __repr__(self) -> str:
        return (
            f"Result("
            f"config={len(self.config)} params, "
            f"description={self.description}, "
            f"data_points={len(self.data)})"
        )
