import os
from datetime import datetime
import json
import hashlib
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# function to calculate the SHA256 hash of a file
def generate_file_hash(file_path):
    sha256_hash = hashlib.sha256()

    # read the file in blocks of 4096 bytes and update the hash object
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            # code credit; https://stackoverflow.com/questions/31632168/does-for-line-in-file-work-with-binary-files-in-python
            sha256_hash.update(byte_block)

    # Return the hex digest of the hash object as a string
    return sha256_hash.hexdigest()

# function to get file information (path, hash, size, permissions)
def get_file_info(file_path):
    file_stats = os.stat(file_path)

    # returns JSON
    return {
        "path": str(file_path),
        "hash": generate_file_hash(file_path),
        "size": file_stats.st_size,
        "permissions": oct(file_stats.st_mode)[-3:]
    }

# function to load baseline data from a JSON file
def load_baseline(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

# function to save baseline data to a JSON file
def save_baseline(file_path, baseline_data):
    with open(file_path, "w") as f:
        json.dump(baseline_data, f, indent=2)

# function to detect changes to a file and log them to the system log file
def detect_changes(file_path, baseline_data, del_flag):
    current_file_info = get_file_info(file_path)
    day = datetime.now().strftime("%F")
    date = datetime.now().strftime("%Y-%m-%d_%H:%M:%S.%f")
    print(f"Change detected check log! sys_log_{day}")

    # opens the system log file in append mode and write the change to the file
    with open(f'sys_log_{day}', 'a') as f:
        if del_flag:
            f.write(f"{date} File deleted: {file_path}\n")
        else:
            for file_info in baseline_data:
                if file_info["path"] == current_file_info["path"]:
                    if file_info["hash"] != current_file_info["hash"]:
                        f.write(f"{date} File content changed: {file_path}\n")
                        file_info["hash"] = current_file_info["hash"]
                        break
                    if file_info["permissions"] != current_file_info["permissions"]:
                        f.write(f"{date} File permissions changed: {file_path}\n")
                        file_info["permissions"] = current_file_info["permissions"]
                        break
                    return

            else:
                f.write(f"{date} New file detected: {file_path}\n")
                baseline_data.append(current_file_info)

            save_baseline(baseline_file, baseline_data)

# define class to handle file system events
class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, baseline_data):
        self.baseline_data = baseline_data

    #defines three fuctions for each action
    def on_modified(self, event):
        if not event.is_directory:
            print(f"File modified: {event.src_path}")
            detect_changes(event.src_path, self.baseline_data, del_flag = False)

    def on_created(self, event):
        if not event.is_directory:
            print(f"File created: {event.src_path}")
            detect_changes(event.src_path, self.baseline_data, del_flag = False)

    def on_deleted(self, event):
        if not event.is_directory:
            print(f"File deleted: {event.src_path}")
            detect_changes(event.src_path, self.baseline_data, del_flag = True)
            

# watchdog filechange handler/observer
def monitor_directory(directory, baseline_data):
    event_handler = FileChangeHandler(baseline_data)
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()

    #break points on exeption
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()


# starts main
if __name__ == "__main__":
    while True:
        # valdiates input
        directory = input("Enter a file path to monitor or type 'q' to quit: ")
        if directory.lower() == 'q':
            break
        if os.path.exists(directory):
            baseline_file = "baseline_data.json"
            baseline_data = load_baseline(baseline_file)
            print(f"Monitoring directory: {directory}")
            monitor_directory(directory, baseline_data)
        else:
            print(f"The directory '{directory}' does not exist. Please enter a valid path.")