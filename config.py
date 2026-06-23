"""
config.py
Handles loading and saving the JSON configuration file.
"""

import json
import os

DEFAULT_CONFIG = {
    "watch_paths": ["./watched"],
    "ignore_extensions": [".tmp", ".log"],
    "ignore_folders": ["__pycache__", ".git"],
    "hash_algorithm": "sha256",
    "baseline_file": "baselines/baseline.json",
    "log_file": "logs/fim.log",
    "report_folder": "reports",
    "scan_interval_seconds": 10,
    "auto_update_baseline": False,
    "colorized_output": True
}

CONFIG_PATH = "config.json"


def load_config(path=CONFIG_PATH):
    """Load config.json, creating it with defaults if missing."""
    if not os.path.exists(path):
        save_config(DEFAULT_CONFIG, path)
        return DEFAULT_CONFIG.copy()

    with open(path, "r") as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            config = DEFAULT_CONFIG.copy()

    # Fill in any missing keys with defaults
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value

    return config


def save_config(config, path=CONFIG_PATH):
    """Save the given config dictionary to file."""
    with open(path, "w") as f:
        json.dump(config, f, indent=4)


def update_setting(key, value, path=CONFIG_PATH):
    """Update a single setting and save it."""
    config = load_config(path)
    config[key] = value
    save_config(config, path)
    return config
