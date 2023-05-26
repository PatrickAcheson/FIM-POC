import os
from datetime import datetime
import json
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Function to calculate the SHA256 hash of a file
def generate_file_hash(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(
            lambda: f.read(4096), b""): sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# Function to get file information (path, hash, size, permissions)
def get_file_info(file_path):
    file_stats = os.stat(file_path)
    return {"path": str(file_path),
            "hash": generate_file_hash(file_path),
            "size": file_stats.st_size,
            "permissions": oct(file_stats.st_mode)[-3:]}

# Function to load baseline data from a JSON file
def load_baseline(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

# Function to save baseline data to a JSON file
def save_baseline(file_path, baseline_data):
    with open(file_path, "w") as f:
        json.dump(baseline_data, f, indent=2)

# Function to log change in the system log file
def log_change(date, change_type, file_path):
    with open(f'sys_log_{date}', 'a') as f:
        f.write(
            f"{datetime.now().strftime('%Y-%m-%d_%H:%M:%S.%f')} {change_type} {file_path}\n")

# Function to detect changes to a file and log them


def detect_changes(file_path, baseline_data, change_type):
    current_file_info = get_file_info(file_path)
    day = datetime.now().strftime("%F")
    print(f"Change detected check log! sys_log_{day}")
    log_change(day, change_type, file_path)
    for file_info in baseline_data:
        if file_info["path"] == current_file_info["path"]:
            if file_info["hash"] != current_file_info["hash"]:
                log_change(day, "File content changed:", file_path)
                file_info["hash"] = current_file_info["hash"]
            if file_info["permissions"] != current_file_info["permissions"]:
                log_change(day, "File permissions changed:", file_path)
                file_info["permissions"] = current_file_info["permissions"]
            return
    baseline_data.append(current_file_info)
    save_baseline(baseline_file, baseline_data)

# Class to handle file system events
# https://pythonhosted.org/watchdog/api.html#event-classes


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, baseline_data):
        self.baseline_data = baseline_data

    def on_modified(self, event):
        if not event.is_directory:
            detect_changes(event.src_path, self.baseline_data, "File modified:")

    def on_created(self, event):
        if not event.is_directory:
            detect_changes(event.src_path, self.baseline_data, "File created:")

    def on_deleted(self, event):
        if not event.is_directory:
            detect_changes(event.src_path, self.baseline_data, "File deleted:")

# Function to monitor a directory
def monitor_directory(directory, baseline_data):
    observer = Observer()
    observer.schedule(FileChangeHandler(baseline_data),
                      directory, recursive=True)
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


# Main function
if __name__ == "__main__":
    while True:
        directory = input("Enter a file path to monitor or type 'q' to quit: ")
        if directory.lower() == 'q':
            break
        if os.path.exists(directory):
            baseline_file = "baseline_data.json"
            baseline_data = load_baseline(baseline_file)
            print(f"Monitoring directory: {directory}")
            monitor_directory(directory, baseline_data)
        else:
            print(
                f"The directory '{directory}' does not exist. Please enter a valid path.")
