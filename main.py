import os
import hashlib
import json
from pathlib import Path

def generate_file_hash(file_path):
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()

def get_file_info(file_path):
    file_stats = os.stat(file_path)

    return {
        "path": str(file_path),
        "hash": generate_file_hash(file_path),
        "size": file_stats.st_size,
        "permissions": oct(file_stats.st_mode)[-3:]
    }

def generate_baseline(directory, output_file):
    baseline_data = []

    for root, _, files in os.walk(directory):
        for file in files:
            file_path = Path(root) / file
            baseline_data.append(get_file_info(file_path))

    with open(output_file, "w") as f:
        json.dump(baseline_data, f, indent=2)

if __name__ == "__main__":
    directory = "./"
    output_file = "baseline_data.json"
    generate_baseline(directory, output_file)
    print(f"Baseline generated and saved to {output_file}")
