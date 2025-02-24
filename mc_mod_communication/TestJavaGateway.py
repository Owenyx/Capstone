from py4j.java_gateway import JavaGateway, GatewayParameters
import time
import random
from collections import deque

class TestDataGateway:
    def __init__(self):
        ''' State '''
        self.shut_down = False
        self.eeg_state = False
        self._eeg_data_type = None
        self._eeg_data_path = None
        
        ''' Storage '''
        # Simulate EEG data structure
        self.eeg_data = {
            'values': deque(maxlen=100),
            'timestamps': deque(maxlen=100)
        }
        
        ''' Java Connection '''
        self.gateway = None
        self.java_storage = None

    
    def get_eeg_data_path(self):
        return self._eeg_data_path
    
    def set_eeg_data_path(self, path):
        self._eeg_data_path = path
        print(f"Data path set to: {path}")

    def connect_to_java(self):
        try:
            print("Attempting to connect to Java gateway...")
            # Connect to java gateway on different ports for gateway and callback
            self.gateway = JavaGateway(
                start_callback_server=True,
                python_proxy_port=25335,  # Different port for callback
                gateway_parameters=GatewayParameters(port=25333)  # Main connection port
            )
            print("Got gateway, getting entry point...")
            entry_point = self.gateway.entry_point
            print("Got entry point, setting Python gateway...")
            entry_point.setPythonGateway(self)
            print("Set Python gateway, getting new data...")
            self.java_storage = entry_point.getData()
            print("Connected to Java gateway successfully")
            return True
        except Exception as e:
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

    def transfer_data(self):
        if self.eeg_state and self.java_storage is not None:
            # Generate random data
            value = random.uniform(0, 100)
            timestamp = time.time()
            
            # Transfer to Java
            self.java_storage.append(value, timestamp)
            print(f"Transferred data: {value} at {timestamp}")

    def close(self):
        self.stop_eeg_collection()
        self.shut_down = True
        print("Gateway shut down")

    class Java:
        implements = ['com.owen.capstonemod.datamanagement.PythonInterface']

if __name__ == "__main__":
    gateway = TestDataGateway()
    while not gateway.connect_to_java():
        print("Failed to connect to Java gateway")
        time.sleep(1)

    try:
        while not gateway.shut_down:
            time.sleep(0.1) 
    except KeyboardInterrupt:
        print("\nShutting down...")
        gateway.close()

'''
pyinstaller --onefile --name TestJavaGateway --hidden-import py4j --hidden-import py4j.java_gateway --hidden-import py4j.java_collections --hidden-import collections --hidden-import random --hidden-import time TestJavaGateway.py
'''