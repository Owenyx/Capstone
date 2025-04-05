from EEG_Controller import Controller as EEGController
from HEG_Controller import HEGController
import time
from py4j.java_gateway import JavaGateway, GatewayParameters
from py4j.java_collections import ListConverter
from collections import deque
from threading import Thread
import atexit
import numpy as np


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

        # The mod only allows for valid paths, so we don't need to check for that

        # Set the data type based on the path
        self.eeg_data_type = path.split('/')[0]

        if self.eeg_data_type == 'waves':
            # Waves is a special case, the path is in the form of "waves/wave_type/percent_or_raw"
            # But we will average all 4 channels, and with the structure of the waves dict, we need to have the base data at waves level
            self.eeg_data = self.eeg.deques['waves']
        
        else:
            # Set the data stream based on the path
            self.eeg_data = self.eeg.deques
            for step in path.split('/'):
                self.eeg_data = self.eeg_data[step]

        self._eeg_data_path = path


    def get_new_data(self):
        # If no device is enabled, return empty lists
        if not self.eeg_state and not self.heg_state:
            return ListConverter().convert([[], []], self.gateway._gateway_client)

        # If the data type is signal or waves, use the average of the 4 channels
        # If the data type is resist, concatenate the values from each channel
        if self.eeg_state:

            if self.eeg_data_type == 'signal':
                # First get copies of each channel's values
                O1 = list(self.active_data['O1']['values'])
                O2 = list(self.active_data['O2']['values'])
                T3 = list(self.active_data['T3']['values'])
                T4 = list(self.active_data['T4']['values'])

                values = self._average_data(O1, O2, T3, T4)
                timestamps = list(self.active_data['O1']['timestamps']) # all timestamps are the same

            elif self.eeg_data_type == 'waves':
                # Path will be in the form of "waves/wave_type/percent_or_raw"
                wave_type = self._eeg_data_path.split('/')[1]
                percent_or_raw = self._eeg_data_path.split('/')[2]

                # Active data is just waves. get copies of each channel's values
                O1 = list(self.active_data['O1'][wave_type][percent_or_raw]['values'])
                O2 = list(self.active_data['O2'][wave_type][percent_or_raw]['values'])
                T3 = list(self.active_data['T3'][wave_type][percent_or_raw]['values'])
                T4 = list(self.active_data['T4'][wave_type][percent_or_raw]['values'])

                values = self._average_data(O1, O2, T3, T4)
                timestamps = list(self.active_data['O1'][wave_type][percent_or_raw]['timestamps']) # all timestamps are the same

            elif self.eeg_data_type == 'resist':
                # Active data is just resist. Concatenate the values from each channel

                # Get copies of each channel's values
                O1 = list(self.active_data['O1']['values'])
                O2 = list(self.active_data['O2']['values'])
                T3 = list(self.active_data['T3']['values'])
                T4 = list(self.active_data['T4']['values'])

                values = self._concatenate_data(O1, O2, T3, T4)
                timestamps = list(self.active_data['O1']['timestamps']) # all timestamps are the same

            else: # Access it normally
                # Get a copy of the data
                values = list(self.active_data['values'])
                timestamps = list(self.active_data['timestamps'])

        else: # HEG
            values = list(self.active_data['reading'])
            timestamps = list(self.active_data['timestamp'])

            # Silly fella Ethan thinks it's cool to store all the numbers as strings
            # So we need to convert them to floats
            values = [float(val) for val in values]

        # Convert data into lists of doubles for java to recieve
        transfer_values = ListConverter().convert(values, self.gateway._gateway_client)
        transfer_timestamps = ListConverter().convert(timestamps, self.gateway._gateway_client)

        self.clear_active_data()

        return ListConverter().convert([transfer_values, transfer_timestamps], self.gateway._gateway_client)
        

    def _average_data(self, *args):
        # All lists must be the same length for np.array to work
        # Get the minimum length of the lists
        min_length = min(len(arg) for arg in args)

        # If any list is empty, return an empty list
        if min_length == 0:
            return []

        # Get the last min_length values of each list
        arrays = np.array([arg[-min_length:] for arg in args])

        # Return the average of the lists
        return [float(val) for val in np.mean(arrays, axis=0)]


    def _concatenate_data(self, *args):
        # Create a flat list combining all lists
        combined = []
        for arg in args:
            combined.extend(arg)
        return combined


    def clear_active_data(self):
        if self.eeg_state:
            self.eeg.reset_deques(self.reset_args[self.eeg_data_type])
        elif self.heg_state:
            self.heg.clear_readings()
            # Need to reset the references with the way HEG clearing is done
            self.heg_data = self.heg.readings
            self.active_data = self.heg_data

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

            self.gateway = JavaGateway(
                start_callback_server=True,
                python_proxy_port=25334,  # port for callback
                gateway_parameters=GatewayParameters(port=25335),  # main port
                auto_convert=True
            )
            entry_point = self.gateway.entry_point
            entry_point.setPythonGateway(self)
            self.java_storage = entry_point.getData()
            self.start_heartbeat_check()
            return True
        except Exception as e:
            print(f"Error connecting to Java: {e}")
            if self.gateway:
                self.gateway.shutdown()
                self.gateway = None
            return False

    ''' EEG data collection '''

    def connect_eeg(self):
        # Returns True if connection is successful and False if not
        self.eeg_connected = self.eeg.find_and_connect()
        return self.eeg_connected


    def start_eeg_collection(self):
        # Must pass all checks before starting collection
        if not (self.eeg_connected and not self.eeg_state and not self.heg_state and self.eeg_data_type):
            return
        
        self.active_data = self.eeg_data
        self.eeg_state = True

        if self.eeg_data_type == 'waves':
            # Spectrum collection covers both spectrum and waves, and therefore there is no waves collection
            self.eeg.start_spectrum_collection() 
        else:
            getattr(self.eeg, f'start_{self.eeg_data_type}_collection')()


    def stop_eeg_collection(self):
        if self.eeg_state:
            self.eeg.stop_collection()
            self.eeg_state = False


    def get_bipolar_calibration_progress(self):
        return self.eeg.bipolar_calibration_progress
    

    def is_bipolar_calibrated(self):
        return self.eeg.is_bipolar_calibrated()


    def get_monopolar_calibration_progress(self, channel):
        return self.eeg.monopolar_calibration_progress[channel]
    

    def is_monopolar_calibrated(self, channel):
        return self.eeg.is_monopolar_calibrated(channel)
    

    ''' HEG data collection '''

    def connect_heg(self):
        # Returns True if connection is successful and False if not

        # The HEG does not have a connect method as it uses USB, so we'll just collect data for a moment to see if it's connected
        time_to_collect = 1
        self.heg.collect_data_for_time(time_to_collect)
        time.sleep(time_to_collect + 0.5)
        self.heg_connected = self.heg.collect_count > 0
        self.heg.clear_readings()
        return self.heg_connected


    def start_heg_collection(self):
        # Must pass all checks before starting collection
        if not (self.heg_connected and not self.heg_state and not self.eeg_state):
            return

        self.active_data = self.heg_data
        self.heg_state = True
        self.collection_thread = Thread(target=self.heg.collect_data, daemon=True)
        self.collection_thread.start()


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
            # If the last ping was more than 8 seconds ago, close the connection
            if time.time() - self.last_ping > 8:
                self.close()


    def ping(self):
        self.last_ping = time.time()

    ''' Shutdown '''

    def close(self):
        self.stop_eeg_collection()
        self.stop_heg_collection()
        if self.gateway:
            self.gateway.shutdown()
            self.gateway = None


    class Java:
        implements = ['com.owen.brainlink.datamanagement.PythonInterface']


if __name__ == "__main__":
    gateway = DataGateway()
    gateway.last_call = time.time()
    attempts = 0
    while not gateway.connect_to_java():
        attempts += 1
        time.sleep(3)
        if attempts > 5:
            raise Exception("Failed to connect to Java")

    # Only stop after close() is called
    while gateway.gateway is not None:
        time.sleep(1)


# Command to compile into exe
'''
pyinstaller --onefile --name JavaGateway --additional-hooks-dir=. --hidden-import py4j --hidden-import py4j.java_gateway --hidden-import py4j.java_collections --hidden-import pyneurosdk2 --hidden-import pyem-st-artifacts --hidden-import pyspectrum-lib --hidden-import EEG_Controller --hidden-import HEG_Controller JavaGateway.py
'''