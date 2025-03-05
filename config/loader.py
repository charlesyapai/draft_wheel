# draft_wheel/config/loader.py

import os
import yaml

class ConfigRetrieval:
    def __init__(self, config_file_path: str):
        self.config_file_path = config_file_path
        self._config = {}
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file_path):
            print(f"[WARNING] Config file '{self.config_file_path}' not found; using defaults.")
            self._config = {}
            return
        with open(self.config_file_path, "r", encoding="utf-8") as f:
            self._config = yaml.safe_load(f) or {}

    def get_config(self) -> dict:
        return self._config
