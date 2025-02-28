from py4j.java_gateway import JavaGateway, GatewayParameters
import time
import random
from collections import deque
from threading import Thread

class TestDataGateway:
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
        
        ''' Java Connection '''
        self.gateway = None
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

    def start_heg_collection(self):
        self.heg_state = True
        print("Started HEG collection")

    def stop_heg_collection(self):
        self.heg_state = False
        print("Stopped HEG collection")

    def transfer_data(self):
        print(f"EEG state: {self.eeg_state}, HEG state: {self.heg_state}, Java storage: {self.java_storage}")
        if (self.eeg_state or self.heg_state) and self.java_storage is not None:
            # Generate random data
            self.value += random.uniform(-5, 5)
            value = max(50, min(100, self.value))  # Clamp between 50 and 100
            timestamp = time.time()
            # Transfer to Java
            print("1", time.time())
            Thread(target=self.java_storage.append, args=(float(value), float(timestamp))).start()
            #self.java_storage.append(value, timestamp)
            print(f"Transferred data: {value} at {timestamp}")

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
    while not gateway.connect_to_java():
        print("Failed to connect to Java gateway")
        time.sleep(1)

    '''try:
        while not gateway.shut_down:
            time.sleep(0.1) 
            if time.time() - gateway.last_ping > 3:
                print("Lost connection to Java gateway")
                attempt = 0
                while not gateway.connect_to_java() and attempt < 3:
                    print("Attempting to reconnect to Java gateway...")
                    time.sleep(1)
                    attempt += 1
                if attempt == 3:
                    print("Failed to reconnect to Java gateway")
                    return 0
    except KeyboardInterrupt:
        print("\nShutting down...")
        gateway.close()'''

        
if __name__ == "__main__":
    main()


'''
pyinstaller --onefile --name TestJavaGateway --hidden-import py4j --hidden-import py4j.java_gateway --hidden-import py4j.java_collections --hidden-import collections --hidden-import random --hidden-import time TestJavaGateway.py
'''