import os
import sys
import json
import hashlib
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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

def load_baseline(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def detect_changes(file_path, baseline_data):
    current_file_info = get_file_info(file_path)

    for file_info in baseline_data:
        if file_info["path"] == current_file_info["path"]:
            if file_info["hash"] != current_file_info["hash"]:
                print(f"File content changed: {file_path}")
            if file_info["permissions"] != current_file_info["permissions"]:
                print(f"File permissions changed: {file_path}")
            return

    print(f"New file detected: {file_path}")

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, baseline_data):
        self.baseline_data = baseline_data

    def on_modified(self, event):
        if not event.is_directory:
            print(f"File modified: {event.src_path}")
            detect_changes(event.src_path, self.baseline_data)

    def on_created(self, event):
        if not event.is_directory:
            print(f"File created: {event.src_path}")
            detect_changes(event.src_path, self.baseline_data)

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"File deleted: {event.src_path}")

def monitor_directory(directory, baseline_data):
    event_handler = FileChangeHandler(baseline_data)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == "__main__":
    
    while True:
        directory = input("Enter a file path to monitor or type 'exit' to quit: ")
        if directory.lower() == 'exit':
            break
        if os.path.exists(directory):
            baseline_file = "baseline_data.json"
            baseline_data = load_baseline(baseline_file)
            print(f"Monitoring directory: {directory}")
            monitor_directory(directory, baseline_data)
        else:
            print(f"The directory '{directory}' does not exist. Please enter a valid path.")
