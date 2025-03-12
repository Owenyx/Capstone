
import time
import random
from collections import deque

class PythonBridge:
    def __init__(self):
        ''' State '''
        self.eeg_state = False
        self.heg_state = False
        self._eeg_data_type = None
        self._eeg_data_path = None
        
        ''' Storage '''
        # Simulate EEG data structure
        self.eeg_data = {
            'values': deque(maxlen=100),
            'timestamps': deque(maxlen=100)
        }

        ''' Data mimicing '''
        self.value = 75

    
    def get_eeg_data_path(self):
        return self._eeg_data_path
    
    def set_eeg_data_path(self, path):
        self._eeg_data_path = path
        print(f"Data path set to: {path}")

    def connect_eeg(self):
        print("Simulating EEG connection...")
        time.sleep(2)
        print("Simulated EEG connected")
        return True

    def start_eeg_collection(self):
        self.last_call = time.time()
        self.eeg_state = True
        print("Started EEG collection")

    def stop_eeg_collection(self):
        self.eeg_state = False
        print("Stopped EEG collection")

    # In the actual program, this will collect data for a moment and check if any was collected
    def connect_heg(self):
        print("Simulating HEG connection...")
        time.sleep(2)
        print("Simulated HEG connected")
        return True

    def start_heg_collection(self):
        self.last_call = time.time()
        self.heg_state = True
        print("Started HEG collection")

    def stop_heg_collection(self):
        self.heg_state = False
        print("Stopped HEG collection")

    def get_new_data(self):
        print(f"EEG state: {self.eeg_state}, HEG state: {self.heg_state}, Java storage: {self.java_storage}")
        if (self.eeg_state or self.heg_state) and self.java_storage is not None:
            # Generate random data
            values = deque(maxlen=100)
            timestamps = deque(maxlen=100)
            time_passed = time.time() - self.last_call
            loop_amount = int(time_passed * 100)  # Example: 100 iterations per second passed
            for i in range(loop_amount):
                self.value += random.uniform(-2, 2)
                # Clamp between 50 and 100
                if self.value > 100:
                    self.value = 100
                elif self.value < 50:
                    self.value = 50
                values.append(self.value)
                timestamps.append(time.time())

            self.last_call = time.time()

            return list(values), list(timestamps)
