import subprocess
import threading
import time
import csv
import signal
from collections import deque

# TODO:
# write to a csv file for reading later

class HEGController:
    def __init__(self):
        # Use deques with a fixed maximum length for the current block.
        self.readings = {"timestamp": deque(maxlen=1000), "reading": deque(maxlen=1000)}
        # A list to archive data blocks once the deques fill up.
        self.archived_readings = {"timestamp": [], "reading": []}

        self.is_collecting = False

        self.collect_count = 0

    def start_collecting(self):
        # Start the C program as a subprocess

        print("Starting HEG")
        self.process = subprocess.Popen(
            ["Start HEG\\main.exe"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )

    def collect_data(self):

        self.start_collecting()

        print("Collecting data")

        self.is_collecting = True

        # Read and output lines from the subprocess until it terminates
        while self.is_collecting:
            for line in iter(self.process.stdout.readline, ''):
                # Append current time and the reading to their respective deques
                self.readings["timestamp"].append(time.time())
                self.readings["reading"].append(line.strip())

                self.collect_count += 1
                if self.collect_count % 1000 == 0:
                    self.archive_current_readings()

                if not self.is_collecting:
                    break

    def collect_data_for_time(self, time_in_seconds):
        thread = threading.Thread(target=self.collect_data)
        thread.start()
        time.sleep(time_in_seconds)
        self.stop_reading()
        thread.join()

    def save_readings_for_color(self, color):
        with open("HEG_readings.csv", "r") as infile:
            contents = infile.read()
        with open(f"HEG_readings_{color}.csv", "w") as outfile:
            outfile.write(contents)
            
    # stop the reading does not kill c program
    def stop_reading(self):
        self.is_collecting = False
        print("Stopping reading")
        print(f"Collected {self.collect_count} readings")

        #   HOLY SHIT THIS WORKS
        self.process.send_signal(signal.CTRL_BREAK_EVENT)
        try:
            self.process.wait(timeout=10)  # Waits up to 10 seconds
        except subprocess.TimeoutExpired:
            print("Process did not exit in time; you may need to force kill as a last resort.")

    def clear_readings(self):
        self.readings = {"timestamp": deque(maxlen=1000), "reading": deque(maxlen=1000)}
        self.collect_count = 0
        self.archived_readings = {"timestamp": [], "reading": []}

    def archive_current_readings(self):
        # Create a snapshot/copy of the current deque contents.
        
        self.archived_readings["timestamp"] += list(self.readings["timestamp"])
        self.archived_readings["reading"] += list(self.readings["reading"])

    def save_readings(self):
        self.archived_readings["timestamp"] += list(self.readings["timestamp"])
        self.archived_readings["reading"] += list(self.readings["reading"])

        field_names = ['timestamp', 'reading']
        with open("HEG_readings.csv", "w", newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)
            writer.writeheader()
            for timestamp, reading in zip(self.archived_readings["timestamp"], self.archived_readings["reading"]):
                writer.writerow({"timestamp": timestamp, "reading": reading})
        
        self.clear_readings()