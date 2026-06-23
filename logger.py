"""
logger.py
Handles timestamped event logging to file and colorized console output.
"""

import os
from datetime import datetime

# ANSI color codes for console alerts
COLORS = {
    "INFO": "\033[94m",      # Blue
    "SUCCESS": "\033[92m",   # Green
    "WARNING": "\033[93m",   # Yellow
    "CRITICAL": "\033[91m",  # Red
    "RESET": "\033[0m"
}

SEVERITY_LABELS = {
    "CREATED": "WARNING",
    "DELETED": "CRITICAL",
    "MODIFIED": "CRITICAL",
    "INFO": "INFO",
    "SUCCESS": "SUCCESS"
}


def _ensure_log_folder(log_file):
    folder = os.path.dirname(log_file)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)


def log_event(message, event_type="INFO", log_file="logs/fim.log", colorized=True):
    """
    Write a timestamped event to the log file and print it to console.
    event_type controls severity coloring (CREATED, DELETED, MODIFIED, INFO, SUCCESS).
    """
    _ensure_log_folder(log_file)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{event_type}] {message}"

    # Write to log file (always plain text, no color codes)
    with open(log_file, "a") as f:
        f.write(line + "\n")

    # Print to console, with color if enabled
    if colorized:
        severity = SEVERITY_LABELS.get(event_type, "INFO")
        color = COLORS.get(severity, COLORS["RESET"])
        print(f"{color}{line}{COLORS['RESET']}")
    else:
        print(line)
