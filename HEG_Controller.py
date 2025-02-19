import subprocess
import threading
import time
import csv
import signal

# TODO:
# write to a csv file for reading later

class HEGController:
    def __init__(self):
        self.readings = {"timestamp": [], "reading": []}

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

        fieldnames = ["timestamp", "reading"]

        with open("HEG_readings.csv", "w") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
        
        # Read and output lines from the subprocess until it terminates
        while self.is_collecting:
            for line in iter(self.process.stdout.readline, ''):
                with open("HEG_readings.csv", "a") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writerow({"timestamp": time.time(), "reading": line.strip()})
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
        #   HOLY SHIT THIS WORKS
        self.process.send_signal(signal.CTRL_BREAK_EVENT)
        try:
            self.process.wait(timeout=10)  # Waits up to 10 seconds
        except subprocess.TimeoutExpired:
            print("Process did not exit in time; you may need to force kill as a last resort.")

    def clear_readings(self):
        self.readings = {"timestamp": [], "reading": []}