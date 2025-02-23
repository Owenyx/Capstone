from py4j.java_gateway import JavaGateway
from EEG_Controller import Controller as EEGController
from HEG_Controller import HEGController


class DataGateway:
    def __init__(self):
        ''' Controllers '''
        self.eeg = EEGController()
        self.heg = HEGController()

        ''' State '''
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

        self.heg_state = False

        ''' Storage '''
        # 1 second of storage time is all that's needed since we will be accessing rapidly
        self.eeg.storage_time = 1 
        
        # Rename the HEG key names to match our expected format
        self.heg.readings['timestamps'] = self.heg.readings.pop('timestamp')
        self.heg.readings['values'] = self.heg.readings.pop('reading')

        ''' Data streams '''
        self.eeg_data = None # Is dictionary or None
        self.heg_data = self.heg.readings # dictionary with timestamps and values deques

        ''' This helps for resetting the EEG deques '''
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

    @property
    def eeg_data_path(self):
        return self._eeg_data_path
    
    @eeg_data_path.setter
    def eeg_data_path(self, path):
        ''' 
        Sets the data type, data stream, and data path based on the given path
        '''

        # Check if the path is valid
        # A valid path must have end in a dictionary of 2 deques
        end_dict = path.split('/')[-1]
        if len(end_dict) != 2:
            raise ValueError("Invalid path")

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

    def get_data(self):
        ''' 
        Will always return a dictionary of 2 deques, one for timestamps and one for values
        These will always be named 'timestamps' and 'values' respectively
        '''

        if self.eeg_state:
            data = self.eeg.deques[self.eeg_data_path]

            # Reset the deques after each collection so that each collection gets only new data
            self.eeg.reset_deques(self.reset_args[self.eeg_data_type])
            return data
        
        elif self.heg_state:
            data = self.heg_data

            # Reset for same reason as above
            self.heg.readings.clear_readings()
            return data
        
        else:
            return None
    
    def cleanup(self):
        # Add any cleanup code needed
        self.stop_eeg_collection()
        self.stop_heg_collection()
        self.eeg.cleanup()

    ''' EEG data collection '''
    def connect_eeg(self):
        return self.eeg.find_and_connect()
        # Will return True if connection is successful and False if not

    def start_eeg_collection(self):
        # Data path must be set before starting collection
        self.eeg_state = True
        getattr(self.eeg, f'start_{self.eeg_data_type}_collection')()

    def stop_eeg_collection(self):
        if self.eeg_state:
            self.eeg.stop_collection()
            self.eeg_state = False

    ''' HEG data collection '''
    def start_heg_collection(self):
        # Can be started at any time
        self.heg_state = True
        self.heg.collect_data()

    def stop_heg_collection(self):
        if self.heg_state:
            self.heg.stop_reading()
            self.heg_state = False
        

if __name__ == "__main__":
    # Create the gateway server
    gateway = GatewayServer(DataGateway())
    # Start the server
    gateway.start()
    print("Gateway Server Started")
    
    try:
        # Keep the program running
        while True:
            pass
    except KeyboardInterrupt:
        print("Shutting down server")
        gateway.shutdown()
        
    