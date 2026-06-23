"""
monitor.py
Core file integrity monitoring logic: scanning, baseline management,
and change detection (created/deleted/modified).
"""

import os
import json
import shutil
import time
from datetime import datetime

from hash_utils import calculate_hash, get_file_size
from logger import log_event


def _should_ignore(file_path, ignore_extensions, ignore_folders):
    """Check if a file should be skipped based on config rules."""
    for folder in ignore_folders:
        if folder in file_path.split(os.sep):
            return True
    ext = os.path.splitext(file_path)[1]
    if ext in ignore_extensions:
        return True
    return False


def scan_files(watch_paths, ignore_extensions, ignore_folders, algorithm="sha256"):
    """
    Walk all watch_paths and return a dict:
    { file_path: {"hash": ..., "size": ..., "last_seen": ...} }
    """
    results = {}

    for base_path in watch_paths:
        if not os.path.exists(base_path):
            continue

        if os.path.isfile(base_path):
            file_list = [base_path]
        else:
            file_list = []
            for root, dirs, files in os.walk(base_path):
                # Skip ignored folders in-place so os.walk doesn't enter them
                dirs[:] = [d for d in dirs if d not in ignore_folders]
                for name in files:
                    file_list.append(os.path.join(root, name))

        for file_path in file_list:
            if _should_ignore(file_path, ignore_extensions, ignore_folders):
                continue

            file_hash = calculate_hash(file_path, algorithm)
            if file_hash is None:
                continue

            results[os.path.normpath(file_path)] = {
                "hash": file_hash,
                "size": get_file_size(file_path),
                "last_seen": datetime.now().isoformat()
            }

    return results


def load_baseline(baseline_file):
    """Load the stored baseline hashes from disk. Returns {} if none exists."""
    if not os.path.exists(baseline_file):
        return {}
    with open(baseline_file, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_baseline(baseline_data, baseline_file):
    """Save baseline data to disk, creating folders as needed."""
    folder = os.path.dirname(baseline_file)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
    with open(baseline_file, "w") as f:
        json.dump(baseline_data, f, indent=4)


def backup_baseline(baseline_file):
    """Make a timestamped backup copy of the current baseline file."""
    if not os.path.exists(baseline_file):
        return None
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{baseline_file}.{timestamp}.bak"
    shutil.copy2(baseline_file, backup_path)
    return backup_path


def compare_to_baseline(current_scan, baseline_data):
    """
    Compare current scan results to the baseline.
    Returns a dict with lists of 'created', 'deleted', 'modified' file paths.
    """
    current_paths = set(current_scan.keys())
    baseline_paths = set(baseline_data.keys())

    created = list(current_paths - baseline_paths)
    deleted = list(baseline_paths - current_paths)

    modified = []
    for path in current_paths & baseline_paths:
        if current_scan[path]["hash"] != baseline_data[path]["hash"]:
            modified.append(path)

    return {"created": created, "deleted": deleted, "modified": modified}


def run_scan(config, update_baseline_after=False):
    """
    Perform a full scan: load baseline, scan files, compare, log results.
    Optionally updates the baseline afterward.
    Returns the changes dict and the current scan results.
    """
    baseline_data = load_baseline(config["baseline_file"])

    current_scan = scan_files(
        config["watch_paths"],
        config["ignore_extensions"],
        config["ignore_folders"],
        config["hash_algorithm"]
    )

    changes = compare_to_baseline(current_scan, baseline_data)

    log_file = config["log_file"]
    colorized = config.get("colorized_output", True)

    for path in changes["created"]:
        log_event(f"File created: {path}", "CREATED", log_file, colorized)
    for path in changes["deleted"]:
        log_event(f"File deleted: {path}", "DELETED", log_file, colorized)
    for path in changes["modified"]:
        log_event(f"File modified: {path}", "MODIFIED", log_file, colorized)

    total_changes = len(changes["created"]) + len(changes["deleted"]) + len(changes["modified"])
    if total_changes == 0:
        log_event("Scan complete. No changes detected.", "SUCCESS", log_file, colorized)
    else:
        log_event(f"Scan complete. {total_changes} change(s) detected.", "INFO", log_file, colorized)

    if update_baseline_after or config.get("auto_update_baseline", False):
        save_baseline(current_scan, config["baseline_file"])

    return changes, current_scan


def create_baseline(config):
    """Create a fresh baseline from the current state of watched files."""
    current_scan = scan_files(
        config["watch_paths"],
        config["ignore_extensions"],
        config["ignore_folders"],
        config["hash_algorithm"]
    )
    save_baseline(current_scan, config["baseline_file"])
    log_event(
        f"Baseline created with {len(current_scan)} file(s).",
        "SUCCESS",
        config["log_file"],
        config.get("colorized_output", True)
    )
    return current_scan


def real_time_monitor(config, interval=None):
    """
    Continuously scan at a fixed interval until interrupted (Ctrl+C).
    """
    if interval is None:
        interval = config.get("scan_interval_seconds", 10)

    log_event("Starting real-time monitoring. Press Ctrl+C to stop.", "INFO",
               config["log_file"], config.get("colorized_output", True))

    try:
        while True:
            run_scan(config)
            time.sleep(interval)
    except KeyboardInterrupt:
        log_event("Real-time monitoring stopped by user.", "INFO",
                   config["log_file"], config.get("colorized_output", True))
