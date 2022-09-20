import pathlib
from typing import Any
import yaml

__all__ = (
    'settings',
)

BASE_DIR = pathlib.Path(__file__).parent
config_path = BASE_DIR / "settings.yaml"


def get_config(path: pathlib.Path) -> dict[str, Any]:
    with open(path) as f:
        parsed_config = yaml.safe_load(f)
        return parsed_config

settings = get_config(config_path)
