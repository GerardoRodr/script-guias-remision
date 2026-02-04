import json
import os
from pathlib import Path

APP_NAME = "GuiasRemisionExtract"
CONFIG_FILE = "config.json"

class Config:
    def __init__(self):
        self.config_path = Path(CONFIG_FILE)
        self.config = self._load_config()

    def _load_config(self):
        if not self.config_path.exists():
            return {"excel_path": ""}
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"excel_path": ""}

    def save_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    @property
    def excel_path(self):
        return self.config.get("excel_path", "")

    @excel_path.setter
    def excel_path(self, path):
        self.config["excel_path"] = str(path)
        self.save_config()

settings = Config()
