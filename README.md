## Summary

This is a Python script that monitors changes to files in a specified directory and logs any modifications to a system log file. It calculates the SHA256 hash of each file in the directory and compares it to a baseline file to detect changes. If a change is detected, it logs the time and type of change (content or permissions) in a system log file.

## Features

- Calculates the SHA256 hash of each file in the monitored directory.
- Compares the hash of each file to a baseline file to detect changes.
- Logs any changes to the system log file, including the time and type of change (content or permissions).
- Supports monitoring of subdirectories.

## Dependencies

The script requires the following dependencies, which can be installed using `pip`:

- `watchdog`: A Python library for monitoring file system events.
- `pathlib`: A Python library for working with file paths.
- `datetime`: A Python library for working with dates and times.
- `json`: A Python library for working with JSON data.
- `hashlib`: A Python library for working with cryptographic hashes.

## Usage

To use the script, follow these steps:

1. Clone the repository to your local machine.
2. Navigate to the directory containing the script.
3. Run the script with the command `python main.py`.
4. When prompted, enter the path of the directory you want to monitor (do not select current directory or expect recursion like behavior )
5. The script will begin monitoring the directory and logging any changes to the system log file.
6. To stop monitoring, press `CTRL + C`.
