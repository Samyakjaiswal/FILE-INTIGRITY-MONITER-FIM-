"""
main.py
Command-line interface for the File Integrity Monitor.
"""

import sys
import os

from config import load_config, save_config, update_setting
from monitor import run_scan, create_baseline, real_time_monitor, backup_baseline
from reporting import (
    export_report_csv,
    export_report_json,
    append_change_history,
    print_summary,
    print_duplicate_report
)
from logger import log_event

MENU = """
=========================================
   File Integrity Monitor (FIM)
=========================================
1. Create / Reset Baseline
2. Run a Single Scan
3. Start Real-Time Monitoring
4. Scheduled Scan (run once every N seconds, N times)
5. Export Last Scan Report (CSV)
6. Export Last Scan Report (JSON)
7. Show Duplicate Files
8. Backup Current Baseline
9. Settings Menu
0. Exit
=========================================
"""

SETTINGS_MENU = """
--- Settings Menu ---
1. Show current settings
2. Add a watch path
3. Add an ignored extension
4. Add an ignored folder
5. Change hash algorithm (sha256 / sha1 / md5)
6. Toggle auto-update baseline (on/off)
7. Toggle colorized output (on/off)
0. Back to main menu
---------------------
"""


def settings_menu(config):
    while True:
        print(SETTINGS_MENU)
        choice = input("Choose an option: ").strip()

        if choice == "1":
            for key, value in config.items():
                print(f"  {key}: {value}")

        elif choice == "2":
            path = input("Enter path to watch: ").strip()
            config["watch_paths"].append(path)
            save_config(config)
            print(f"Added watch path: {path}")

        elif choice == "3":
            ext = input("Enter extension to ignore (e.g. .tmp): ").strip()
            if not ext.startswith("."):
                ext = "." + ext
            config["ignore_extensions"].append(ext)
            save_config(config)
            print(f"Now ignoring extension: {ext}")

        elif choice == "4":
            folder = input("Enter folder name to ignore (e.g. __pycache__): ").strip()
            config["ignore_folders"].append(folder)
            save_config(config)
            print(f"Now ignoring folder: {folder}")

        elif choice == "5":
            algo = input("Enter algorithm (sha256/sha1/md5): ").strip().lower()
            if algo in ("sha256", "sha1", "md5"):
                config["hash_algorithm"] = algo
                save_config(config)
                print(f"Hash algorithm set to {algo}")
            else:
                print("Invalid algorithm choice.")

        elif choice == "6":
            config["auto_update_baseline"] = not config.get("auto_update_baseline", False)
            save_config(config)
            print(f"Auto-update baseline is now: {config['auto_update_baseline']}")

        elif choice == "7":
            config["colorized_output"] = not config.get("colorized_output", True)
            save_config(config)
            print(f"Colorized output is now: {config['colorized_output']}")

        elif choice == "0":
            break

        else:
            print("Invalid option. Try again.")


def main():
    config = load_config()

    # Make sure the first watch path exists so a first run has something to scan
    for path in config["watch_paths"]:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

    last_changes = None
    last_scan = None

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        if choice == "1":
            create_baseline(config)

        elif choice == "2":
            last_changes, last_scan = run_scan(config)
            print_summary(last_changes, last_scan)
            append_change_history(last_changes)

        elif choice == "3":
            try:
                real_time_monitor(config)
            except KeyboardInterrupt:
                print("\nStopped monitoring.")

        elif choice == "4":
            try:
                interval = int(input("Seconds between scans: ").strip())
                count = int(input("Number of scans to run: ").strip())
            except ValueError:
                print("Please enter valid numbers.")
                continue

            import time
            for i in range(count):
                print(f"\nRunning scheduled scan {i + 1}/{count}...")
                last_changes, last_scan = run_scan(config)
                print_summary(last_changes, last_scan)
                append_change_history(last_changes)
                if i < count - 1:
                    time.sleep(interval)

        elif choice == "5":
            if last_changes is None:
                print("No scan has been run yet. Run a scan first (option 2).")
                continue
            path = export_report_csv(last_changes, last_scan, config["report_folder"])
            print(f"CSV report saved to: {path}")

        elif choice == "6":
            if last_changes is None:
                print("No scan has been run yet. Run a scan first (option 2).")
                continue
            path = export_report_json(last_changes, last_scan, config["report_folder"])
            print(f"JSON report saved to: {path}")

        elif choice == "7":
            if last_scan is None:
                print("No scan has been run yet. Run a scan first (option 2).")
                continue
            print_duplicate_report(last_scan)

        elif choice == "8":
            backup_path = backup_baseline(config["baseline_file"])
            if backup_path:
                print(f"Baseline backed up to: {backup_path}")
            else:
                print("No existing baseline to back up.")

        elif choice == "9":
            settings_menu(config)
            config = load_config()  # reload in case settings changed

        elif choice == "0":
            print("Exiting File Integrity Monitor. Goodbye!")
            sys.exit(0)

        else:
            print("Invalid option. Please choose a number from the menu.")


if __name__ == "__main__":
    main()
