from EEG_Controller import Controller as EEGController
from HEG_Controller import HEGController
import time
from py4j.java_gateway import JavaGateway, GatewayParameters
from py4j.java_collections import ListConverter
from collections import deque
from threading import Thread
import atexit

class DataGateway:
    def __init__(self):
        ''' Controllers '''
        self.eeg = EEGController()
        self.heg = HEGController()

        ''' Java Gateway '''
        self.gateway = None
        # Register the close function to be called when the program exits
        atexit.register(self.close)
        self.last_ping = time.time()

        ''' State '''
        self.eeg_connected = False
        self.eeg_state = False

        # Data type is a string that can be:
        # - signal
        # - resist
        # - emotions_bipolar
        # - emotions_monopolar
        # - spectrum
        # - waves
        # It is set automatically based on the data path
        self._eeg_data_type = None # Is string or None

        # Data path takes the form of a string, e.g. "signal/O1"
        # See the setter definition for valid paths
        self._eeg_data_path = None # Is string or None

        self.heg_connected = False
        self.heg_state = False

        ''' Storage '''
        # 3 seconds of storage time is plenty since we will be accessing rapidly
        # And long term storage is on the Java side
        self.eeg.storage_time = 3
        
        # We rename the HEG key names to be the same as the EEG
        self.heg.readings['timestamps'] = self.heg.readings.pop('timestamp')
        self.heg.readings['values'] = self.heg.readings.pop('reading')

        ''' Data streams '''
        self.eeg_data = None # Is dictionary or None
        self.heg_data = self.heg.readings # dictionary with timestamps and values deques

        # This data will be sent to the Java side
        self.active_data = None

        ''' This is for clearing the EEG deques '''
        self.reset_args = {
            'signal': False,
            'resist': False,
            'emotions_bipolar': False,
            'emotions_monopolar': False,
            'spectrum': False,
            'waves': False
        }


    @property
    def eeg_data_type(self):
        return self._eeg_data_type
    

    @eeg_data_type.setter
    def eeg_data_type(self, type):

        # Set the previous data type to false
        self.reset_args[self._eeg_data_type] = False

        # Assign new type and set its reset arg to true
        self._eeg_data_type = type
        self.reset_args[type] = True


    def get_eeg_data_path(self):
        return self._eeg_data_path
    

    def set_eeg_data_path(self, path):
        # Sets the data type, data stream, and data path based on the given path

        # The mod only allows for valid paths, so we don't need to check

        # Set the data type based on the path
        self.eeg_data_type = path.split('/')[0]

        # Set the data stream based on the path
        try:
            self.eeg_data = self.eeg.deques
            for step in path.split('/'):
                self.eeg_data = self.eeg_data[step]
        except:
            raise ValueError("Invalid path")

        self._eeg_data_path = path


    def get_new_data(self):
        # Get a copy of the data so we can convert while the active data is being added to
        values = list(self.active_data['values'])
        timestamps = list(self.active_data['timestamps'])

        # Convert data into lists of doubles for java to recieve
        values = ListConverter().convert(values, self.gateway._gateway_client)
        timestamps = ListConverter().convert(timestamps, self.gateway._gateway_client)

        self.clear_active_data()

        return ListConverter().convert([values, timestamps], self.gateway._gateway_client)


    def clear_active_data(self):
        if self.eeg_state:
            self.eeg.reset_deques(self.reset_args[self.eeg_data_type])
        elif self.heg_state:
            self.heg.clear_readings()

    ''' Java Connection '''

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

    ''' EEG data collection '''

    def connect_eeg(self):
        # Returns True if connection is successful and False if not
        self.eeg_connected = self.eeg.find_and_connect()
        return self.eeg_connected


    def start_eeg_collection(self):
        # Must pass all checks before starting collection
        if not (self.eeg_connected and not self.eeg_state and not self.heg_state and self.eeg_data_type):
            raise ValueError("EEG cannot be started in this state")
        
        self.active_data = self.eeg_data
        self.eeg_state = True
        getattr(self.eeg, f'start_{self.eeg_data_type}_collection')()


    def stop_eeg_collection(self):
        if self.eeg_state:
            self.eeg.stop_collection()
            self.eeg_state = False

    ''' HEG data collection '''

    def connect_heg(self):
        # Returns True if connection is successful and False if not
        self.heg_connected = self.heg.connect()
        return self.heg_connected


    def start_heg_collection(self):
        # Must pass all checks before starting collection
        if not (self.heg_connected and not self.heg_state and not self.eeg_state):
            raise ValueError("HEG cannot be started in this state")

        self.active_data = self.heg_data
        self.heg_state = True
        self.heg.collect_data()


    def stop_heg_collection(self):
        if self.heg_state:
            self.heg.stop_reading()
            self.heg_state = False

    ''' Heartbeat '''

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

    ''' Shutdown '''

    def close(self):
        self.stop_eeg_collection()
        self.stop_heg_collection()
        if self.gateway:
            print("Shutting down gateway...")
            self.gateway.shutdown()
            self.gateway = None
            print("Gateway shut down")


    class Java:
        implements = ['com.owen.capstonemod.datamanagement.PythonInterface']


if __name__ == "__main__":
    gateway = DataGateway()
    gateway.last_call = time.time()
    while not gateway.connect_to_java():
        print("Failed to connect to Java gateway")
        time.sleep(1)

    # Only stop after close() is called
    while gateway.gateway is not None:
        time.sleep(1)


# Command to compile into exe
'''
pyinstaller --onefile --name JavaGateway --additional-hooks-dir=. --hidden-import py4j --hidden-import py4j.java_gateway --hidden-import py4j.java_collections --hidden-import pyneurosdk2 --hidden-import pyem-st-artifacts --hidden-import pyspectrum-lib --hidden-import EEG_Controller --hidden-import HEG_Controller JavaGateway.py
'''