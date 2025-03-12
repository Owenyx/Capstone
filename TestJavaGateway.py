from py4j.java_gateway import JavaGateway, GatewayParameters
from py4j.java_collections import ListConverter
import time
import random
from collections import deque
from threading import Thread
import atexit

class TestDataGateway:
    def __init__(self):
        ''' State '''
        self.eeg_state = False
        self.heg_state = False
        self._eeg_data_type = None
        self._eeg_data_path = None
        self.last_call = None
    

        ''' Storage '''
        # Simulate EEG data structure
        self.eeg_data = {
            'values': deque(maxlen=100),
            'timestamps': deque(maxlen=100)
        }
        
        ''' Java Connection '''
        self.gateway = None
        # Register the close function to be called when the program exits
        atexit.register(self.close)
        self.java_storage = None
        self.last_ping = time.time()

        ''' Data mimicing '''
        self.value = 75

    
    def get_eeg_data_path(self):
        return self._eeg_data_path
    
    def set_eeg_data_path(self, path):
        self._eeg_data_path = path
        print(f"Data path set to: {path}")

    def connect_to_java(self):
        try:
            # First try to clean up any existing gateway
            if self.gateway:
                try:
                    self.gateway.shutdown()
                    self.gateway = None
                except:
                    pass

            print("Attempting to connect to Java gateway...")
            self.gateway = JavaGateway(
                start_callback_server=True,
                python_proxy_port=25334,  # port for callback
                gateway_parameters=GatewayParameters(port=25335),  # main port
                auto_convert=True
            )
            print("Got gateway, getting entry point...")
            entry_point = self.gateway.entry_point
            print("Got entry point, setting Python gateway...")
            entry_point.setPythonGateway(self)
            print("Set Python gateway, getting new data...")
            self.java_storage = entry_point.getData()
            print("Connected to Java gateway successfully")
            self.start_heartbeat_check()
            return True
        except Exception as e:
            if self.gateway:
                self.gateway.shutdown()
                self.gateway = None
            print(f"Failed to connect: {e}")
            return False

    def connect_eeg(self):
        print("Simulating EEG connection...")
        time.sleep(2)
        print("Simulated EEG connected")
        return True

    def start_eeg_collection(self):
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
        self.heg_state = True
        print("Started HEG collection")

    def stop_heg_collection(self):
        self.heg_state = False
        print("Stopped HEG collection")

    def get_new_data(self):
        print(f"EEG state: {self.eeg_state}, HEG state: {self.heg_state}, Java storage: {self.java_storage}")
        if (self.eeg_state or self.heg_state) and self.java_storage is not None:
            print("Generating new data")
            # Generate random data
            values = deque(maxlen=100)
            print('1')
            timestamps = deque(maxlen=100)
            print('2')
            time_passed = time.time() - self.last_call
            print(f"Time passed: {time_passed}")
            loop_amount = int(time_passed * 100) + 1  # Example: 100 iterations per second passed
            print('4')
            for i in range(loop_amount):
                self.value += random.uniform(-2, 2)
                # Clamp between 50 and 100
                if self.value > 100:
                    self.value = 100
                elif self.value < 50:
                    self.value = 50
                values.append(float(self.value))
                timestamps.append(float(time.time()))

            self.last_call = time.time()
            #print(f"Values: {values}, Timestamps: {timestamps}")

            print('5')

            j_values = ListConverter().convert(values, self.gateway._gateway_client)
            j_timestamps = ListConverter().convert(timestamps, self.gateway._gateway_client)

            print('6')

            return ListConverter().convert([j_values, j_timestamps], self.gateway._gateway_client)

            # This following sequence seems odd but it prevents deadlocks so I'm gonna keep it
            # Incase of future debugging i think they were caused by the the Java and Python programs calling each other at the same time
            '''self.transfer_thread = Thread(target=self.java_storage.append, args=(j_values, j_timestamps))
            self.transfer_thread.start()
            self.transfer_thread.join()'''

    def start_heartbeat_check(self):
        self.ping()
        self.heartbeat_thread = Thread(target=self.check_heartbeat)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()

    def check_heartbeat(self):
        while True:
            time.sleep(3.5)
            if time.time() - self.last_ping > 3:
                self.close()

    def ping(self):
        print("Pinging..." , time.time())
        self.last_ping = time.time()
        
    def close(self):
        self.stop_eeg_collection()
        self.stop_heg_collection()
        if self.gateway:
            print("Shutting down gateway...")
            self.gateway.shutdown()  # Use shutdown instead of just close
            self.gateway = None
            print("Gateway shut down")

    class Java:
        implements = ['com.owen.capstonemod.datamanagement.PythonInterface']



def main():
    gateway = TestDataGateway()
    gateway.last_call = time.time()
    while not gateway.connect_to_java():
        print("Failed to connect to Java gateway")
        time.sleep(1)

        
if __name__ == "__main__":
    main()


'''
pyinstaller --onefile --name TestJavaGateway --hidden-import py4j --hidden-import py4j.java_gateway --hidden-import py4j.java_collections TestJavaGateway.py
'''