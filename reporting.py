"""
reporting.py
Generates scan reports (CSV/JSON), tracks change history, and computes
duplicate file statistics.
"""

import os
import json
import csv
from datetime import datetime

from hash_utils import find_duplicate_files


def _ensure_folder(folder):
    if folder and not os.path.exists(folder):
        os.makedirs(folder)


def build_report_data(changes, current_scan):
    """Build a flat list of report rows from the changes dict."""
    rows = []
    for path in changes["created"]:
        rows.append({"event": "CREATED", "path": path, "hash": current_scan[path]["hash"],
                     "size": current_scan[path]["size"]})
    for path in changes["deleted"]:
        rows.append({"event": "DELETED", "path": path, "hash": "", "size": ""})
    for path in changes["modified"]:
        rows.append({"event": "MODIFIED", "path": path, "hash": current_scan[path]["hash"],
                      "size": current_scan[path]["size"]})
    return rows


def export_report_csv(changes, current_scan, report_folder="reports"):
    """Export scan changes to a timestamped CSV file. Returns the file path."""
    _ensure_folder(report_folder)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(report_folder, f"report_{timestamp}.csv")

    rows = build_report_data(changes, current_scan)

    with open(file_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["event", "path", "hash", "size"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    return file_path


def export_report_json(changes, current_scan, report_folder="reports"):
    """Export scan changes to a timestamped JSON file. Returns the file path."""
    _ensure_folder(report_folder)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(report_folder, f"report_{timestamp}.json")

    rows = build_report_data(changes, current_scan)
    output = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "created": len(changes["created"]),
            "deleted": len(changes["deleted"]),
            "modified": len(changes["modified"])
        },
        "events": rows
    }

    with open(file_path, "w") as f:
        json.dump(output, f, indent=4)

    return file_path


def append_change_history(changes, history_file="logs/history.json"):
    """Append this scan's changes to a running history file."""
    _ensure_folder(os.path.dirname(history_file))

    history = []
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []

    history.append({
        "timestamp": datetime.now().isoformat(),
        "created": changes["created"],
        "deleted": changes["deleted"],
        "modified": changes["modified"]
    })

    with open(history_file, "w") as f:
        json.dump(history, f, indent=4)


def print_summary(changes, current_scan):
    """Print a simple scan summary with statistics to the console."""
    total_files = len(current_scan)
    created = len(changes["created"])
    deleted = len(changes["deleted"])
    modified = len(changes["modified"])

    print("\n--- Scan Summary ---")
    print(f"Total files monitored: {total_files}")
    print(f"Created:  {created}")
    print(f"Deleted:  {deleted}")
    print(f"Modified: {modified}")
    print("--------------------\n")


def print_duplicate_report(current_scan):
    """Find and print duplicate files based on matching hashes."""
    file_hashes = {path: data["hash"] for path, data in current_scan.items()}
    duplicates = find_duplicate_files(file_hashes)

    if not duplicates:
        print("No duplicate files found.")
        return

    print("\n--- Duplicate Files ---")
    for file_hash, paths in duplicates.items():
        print(f"Hash {file_hash[:12]}...:")
        for path in paths:
            print(f"  - {path}")
    print("-----------------------\n")
