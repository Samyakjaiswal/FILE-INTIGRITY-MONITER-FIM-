
# File Integrity Monitor (FIM)

A simple, beginner-friendly file integrity monitoring tool written in pure Python.

## Run

```
python main.py
```

## First Steps

1. Edit `config.json` (or use the Settings Menu) to set `watch_paths` to the folders/files you want to monitor.
2. Choose option `1` to create a baseline.
3. Choose option `2` to run a scan and detect changes (created/deleted/modified files).
4. Choose option `3` for continuous real-time monitoring, or option `4` for a fixed number of scheduled scans.

## Files

- `main.py` — CLI menu and entry point
- `monitor.py` — scanning, baseline, and change detection logic
- `hash_utils.py` — SHA256/SHA1/MD5 hashing helpers
- `config.py` — loads/saves `config.json`
- `reporting.py` — CSV/JSON report export, history, duplicate detection
- `logger.py` — timestamped, colorized event logging
- `config.json` — user settings
- `logs/fim.log` — event log (created on first run)
- `baselines/baseline.json` — stored file hashes (created on first run)
- `reports/` — exported CSV/JSON reports

No third-party dependencies are required.
