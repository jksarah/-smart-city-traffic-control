import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def load_config(path=CONFIG_PATH):
    with open(path, encoding="utf-8") as config_file:
        return json.load(config_file)
