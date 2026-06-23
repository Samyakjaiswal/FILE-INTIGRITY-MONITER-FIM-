"""
hash_utils.py
Functions for calculating file hashes (SHA256, SHA1, MD5).
"""

import hashlib
import os

CHUNK_SIZE = 8192  # Read files in 8KB chunks to handle large files safely


def calculate_hash(file_path, algorithm="sha256"):
    """
    Calculate the hash of a file using the given algorithm.
    Returns the hex digest string, or None if the file can't be read.
    """
    algorithm = algorithm.lower()

    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "sha1":
        hasher = hashlib.sha1()
    elif algorithm == "md5":
        hasher = hashlib.md5()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    try:
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except (FileNotFoundError, PermissionError, OSError):
        return None


def get_file_size(file_path):
    """Return file size in bytes, or 0 if it can't be read."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def find_duplicate_files(file_hashes):
    """
    Given a dict of {file_path: hash}, return a dict of
    {hash: [list of file paths]} for hashes that appear more than once.
    """
    hash_to_files = {}
    for path, file_hash in file_hashes.items():
        if file_hash is None:
            continue
        hash_to_files.setdefault(file_hash, []).append(path)

    duplicates = {h: paths for h, paths in hash_to_files.items() if len(paths) > 1}
    return duplicates
