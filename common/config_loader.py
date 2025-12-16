# common/config_loader.py

import yaml
from pathlib import Path

def load_config(path: str):
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(file_path, "r") as f:
        return yaml.safe_load(f)
