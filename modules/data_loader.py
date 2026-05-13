import os
from pathlib import Path

import pandas as pd


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def get_dataset_path(name: str) -> Path:
    return get_project_root() / "datasets" / name


class DataLoader:
    FILE_NAMES = {
        "sample": "tmp_xx_ontology_sample0.xlsx",
        "behave": "tmp_xx_ontology_sample_history_behave.xlsx",
        "history_plc": "tmp_xx_ontology_sample_history_plc.xlsx",
        "profile": "tmp_xx_ontology_sample_profi.xlsx",
        "qw": "tmp_xx_ontology_sample_qw.xlsx",
    }

    def load_all(self) -> dict[str, pd.DataFrame]:
        root = get_project_root()
        datasets = {}
        for key, fname in self.FILE_NAMES.items():
            path = root / "datasets" / fname
            datasets[key] = pd.read_excel(path)
        return datasets