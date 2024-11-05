#from ast import List
import yaml
from pydantic import BaseModel
from typing import Dict, List, Any

class Settings(BaseModel):
    models: Dict[str, Any]
    nutrition: List[str]
    database: Dict[str, Any]

    @classmethod
    def from_yaml(cls, yaml_file: str):
        with open(yaml_file, "r") as f:
            config_data = yaml.safe_load(f)
        return cls(**config_data)

settings = Settings.from_yaml("config.yaml")