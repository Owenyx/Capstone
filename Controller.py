import sys
from PyQt6.QtWidgets import QApplication
from collections import deque
from time import sleep, time

# Create QApplication instance BEFORE any other imports
if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()

# Now import the rest
from neuro_impl.brain_bit_controller import BrainBitController
from neuro_impl.emotions_bipolar_controller import EmotionBipolar
from neuro_impl.emotions_monopolar_controller import EmotionMonopolar
from neuro_impl.spectrum_controller import SpectrumController


# TODO: 
# - Remove debug prints
# - Add a visual representation of the deques in another file
# - Make sure battery level is working
# - Change connect to device to wait until a device is connected
# - Change around handlers to maybe not be in the collection functions? And consolodate the all data collection callback
# - Track state of connection to device

class Controller:
    def __init__(self):
        self.brain_bit_controller = BrainBitController()
        self.emotion_bipolar_controller = EmotionBipolar()
        self.emotion_monopolar_controller = EmotionMonopolar()
        self.spectrum_controller = SpectrumController()

        self.bp_calibration_progress = 0 # Used for emotions
        self.mp_calibration_progress = {'O1': 0, 'O2': 0, 'T3': 0, 'T4': 0} # Used for emotions
        
        self.deques_size = 10000
        
        # Once the dictionary definitions are set in stone we will use helper functions to create duplicated dictionary structures because these definintions are huge
        # Here's what we have for now for helper functions:

        def create_timestamp_values_dict():
            return {
                'timestamps': deque(maxlen=self.deques_size),
                'values': deque(maxlen=self.deques_size)
            }

        def create_channel_dict():

            return {
                'O1': create_timestamp_values_dict(),
                'O2': create_timestamp_values_dict(),
                'T3': create_timestamp_values_dict(),
                'T4': create_timestamp_values_dict()
            }
        
        def create_raw_percent_dict():
            return {
                'raw': create_timestamp_values_dict(),
                'percent': create_timestamp_values_dict()
            }
        
        def create_emotions_dict():
            return {
                'calibration_progress': create_timestamp_values_dict(),
                'artefacted_sequence': create_timestamp_values_dict(),
                'artefacted_both_side': create_timestamp_values_dict(),
                'delta': create_raw_percent_dict(),
                'theta': create_raw_percent_dict(),
                'alpha': create_raw_percent_dict(),
                'beta': create_raw_percent_dict(),
                'gamma': create_raw_percent_dict(),
                'attention': create_raw_percent_dict(),
                'relaxation': create_raw_percent_dict()
            }
        def create_waves_dict():
            return {
                'delta': create_raw_percent_dict(),
                'theta' : create_raw_percent_dict(),
                'alpha': create_raw_percent_dict(),
                'beta': create_raw_percent_dict(),
                'gamma': create_raw_percent_dict()
            }

        # Now we set up the deques in a tree structure using dictionaries
        self.deques = {
            # Might add PackNum to singal data since it's part of the data packet that is outputted by the device
            'signal': create_channel_dict(),
            'resist': create_channel_dict(),
            'emotions_bipolar': create_emotions_dict(),
            'emotions_monopolar': {
                'O1': create_emotions_dict(),
                'O2': create_emotions_dict(),
                'T3': create_emotions_dict(),
                'T4': create_emotions_dict()
            },
            'spectrum': create_channel_dict(),
            'waves': {
                'O1': create_waves_dict(),
                'O2': create_waves_dict(),
                'T3': create_waves_dict(),
                'T4': create_waves_dict()
            }
        }
    
        # Set up event handlers each controller of processed data
        #Emotions Bipolar
        self.emotion_bipolar_controller.progressCalibrationCallback = self.bp_calibration_callback
        self.emotion_bipolar_controller.isArtifactedSequenceCallback = self.bp_is_artifacted_sequence_callback
        self.emotion_bipolar_controller.isBothSidesArtifactedCallback = self.bp_is_both_sides_artifacted_callback
        self.emotion_bipolar_controller.lastMindDataCallback = self.bp_mind_data_callback
        self.emotion_bipolar_controller.lastSpectralDataCallback = self.bp_last_spectral_data_callback
        self.emotion_bipolar_controller.rawSpectralDataCallback = self.bp_raw_spectral_data_callback

        #Emotions Monopolar
        self.emotion_monopolar_controller.progressCalibrationCallback = self.mp_calibration_callback
        self.emotion_monopolar_controller.isArtifactedSequenceCallback = self.mp_is_artifacted_sequence_callback
        self.emotion_monopolar_controller.isBothSidesArtifactedCallback = self.mp_is_both_sides_artifacted_callback
        self.emotion_monopolar_controller.lastMindDataCallback = self.mp_mind_data_callback
        self.emotion_monopolar_controller.lastSpectralDataCallback = self.mp_last_spectral_data_callback
        self.emotion_monopolar_controller.rawSpectralDataCallback = self.mp_raw_spectral_data_callback

        #Spectrum
        self.spectrum_controller.processedWaves = self.__processed_waves
        self.spectrum_controller.processedSpectrum = self.__processed_spectrum

    # Handler code
    # Bipolar handlers
    def bp_calibration_callback(self, progress):
        self.bp_calibration_progress = progress
        current_time = time()
        self.deques['emotions_bipolar']['calibration_progress']['timestamps'].append(current_time)
        self.deques['emotions_bipolar']['calibration_progress']['values'].append(progress)

    def bp_is_artifacted_sequence_callback(self, artifacted):
        current_time = time()
        self.deques['emotions_bipolar']['artefacted_sequence']['timestamps'].append(current_time)
        self.deques['emotions_bipolar']['artefacted_sequence']['values'].append(artifacted)

    def bp_is_both_sides_artifacted_callback(self, artifacted):
        current_time = time()
        self.deques['emotions_bipolar']['artefacted_both_side']['timestamps'].append(current_time)
        self.deques['emotions_bipolar']['artefacted_both_side']['values'].append(artifacted)

    def bp_mind_data_callback(self, data):
        current_time = time()
        for type in ['attention', 'relaxation']:
            self.deques['emotions_bipolar'][type]['raw']['timestamps'].append(current_time)
            self.deques['emotions_bipolar'][type]['raw']['values'].append(getattr(data, f"inst_{type}"))
            self.deques['emotions_bipolar'][type]['percent']['timestamps'].append(current_time)
            self.deques['emotions_bipolar'][type]['percent']['values'].append(getattr(data, f"rel_{type}"))

    def bp_last_spectral_data_callback(self, spectral_data): # Data from here is a percentage, so the value is < 1, just *100 to get the percentage
        current_time = time()
        for wave in ['delta', 'theta', 'alpha', 'beta', 'gamma']:
            self.deques['emotions_bipolar'][wave]['percent']['timestamps'].append(current_time)
            self.deques['emotions_bipolar'][wave]['percent']['values'].append(getattr(spectral_data, wave))

    def bp_raw_spectral_data_callback(self, spect_vals):# In the sample program, there was only raw values for Alpha and Beta, so if an issue arises, check here
        current_time = time()
        for wave in ['alpha', 'beta']:
            self.deques['emotions_bipolar'][wave]['raw']['timestamps'].append(current_time)
            self.deques['emotions_bipolar'][wave]['raw']['values'].append(getattr(spect_vals, wave))

    # Monopolar handlers
    def mp_calibration_callback(self, progress, channel):
        self.mp_calibration_progress[channel] = progress
        current_time = time()
        self.deques['emotions_monopolar'][channel]['calibration_progress']['timestamps'].append(current_time)
        self.deques['emotions_monopolar'][channel]['calibration_progress']['values'].append(progress)

    def mp_is_artifacted_sequence_callback(self, artifacted, channel):
        current_time = time()
        self.deques['emotions_monopolar'][channel]['artefacted_sequence']['timestamps'].append(current_time)
        self.deques['emotions_monopolar'][channel]['artefacted_sequence']['values'].append(artifacted)

    def mp_is_both_sides_artifacted_callback(self, artifacted, channel):
        current_time = time()
        self.deques['emotions_monopolar'][channel]['artefacted_both_side']['timestamps'].append(current_time)
        self.deques['emotions_monopolar'][channel]['artefacted_both_side']['values'].append(artifacted)

    def mp_mind_data_callback(self, data, channel):
        current_time = time()
        for type in ['attention', 'relaxation']:
            self.deques['emotions_monopolar'][channel][type]['raw']['timestamps'].append(current_time)
            self.deques['emotions_monopolar'][channel][type]['raw']['values'].append(getattr(data, f"inst_{type}"))
            self.deques['emotions_monopolar'][channel][type]['percent']['timestamps'].append(current_time)
            self.deques['emotions_monopolar'][channel][type]['percent']['values'].append(getattr(data, f"rel_{type}"))

    def mp_last_spectral_data_callback(self, spectral_data, channel): # Data from here is a percentage, so the value is < 1, just *100 to get the percentage
        current_time = time()
        for wave in ['delta', 'theta', 'alpha', 'beta', 'gamma']:
            self.deques['emotions_monopolar'][channel][wave]['percent']['timestamps'].append(current_time)
            self.deques['emotions_monopolar'][channel][wave]['percent']['values'].append(getattr(spectral_data, wave))

    def mp_raw_spectral_data_callback(self, spect_vals, channel): # In the sample program, there was only raw values for Alpha and Beta, so if an issue arises, check her
        current_time = time()
        for wave in ['alpha', 'beta']:
            self.deques['emotions_monopolar'][channel][wave]['raw']['timestamps'].append(current_time)
            self.deques['emotions_monopolar'][channel][wave]['raw']['values'].append(getattr(spect_vals, wave))

    # Spectrum handlers
    def __processed_waves(self, waves, channel):
        current_time = time()
        for wave in ['alpha', 'beta', 'theta', 'delta', 'gamma']:
            self.deques['waves'][channel][wave]['raw']['timestamps'].append(current_time)
            self.deques['waves'][channel][wave]['raw']['values'].append(getattr(waves, f"{wave}_raw"))
            self.deques['waves'][channel][wave]['percent']['timestamps'].append(current_time)
            self.deques['waves'][channel][wave]['percent']['values'].append(getattr(waves, f"{wave}_rel"))

    def __processed_spectrum(self, spectrum, channel):
        current_time = time()
        self.deques['spectrum'][channel]['timestamps'].append(current_time)
        self.deques['spectrum'][channel]['values'].append(spectrum)


    ''' Finding and connecting to the sensor '''
    def find_and_connect(self):
        #Callback for when sensors are found
        def on_sensors_found(sensors):
            self.sensors = sensors
        
        # Assign the callback to the controller and start scanning
        self.brain_bit_controller.sensorsFounded = on_sensors_found
        print("Scanning for 5 seconds...")
        self.brain_bit_controller.start_scan()
        
        # Wait for 5 seconds
        sleep(7)
        
        # Stop scanning
        self.brain_bit_controller.stop_scan()
        
        # Check if no sensors were found
        if not hasattr(self, 'sensors') or len(self.sensors) == 0:
            print("No sensors found")
            return False
        
        # Try to connect to the first available sensor
        try:
            self.brain_bit_controller.create_and_connect(sensor_info=self.sensors[0])
            print(f"Connected to sensor: {self.sensors[0].Name}")
            
            # Wait for connection to establish
            sleep(2)
            
        except Exception as e:
            print(f"Error connecting to sensor: {str(e)}")
            return False
        
        # Return True if connection was successful
        return True


    ''' Starting data collection and outputting data into the deques '''
    def start_all_data_collection(self):
        # Cannot do resist at the same time, must be done independently
        def on_signal_received(data):
            current_time = time()

            #Signal
            # Extract samples for each channel
            O1_samples = [sample.O1 for sample in data]
            O2_samples = [sample.O2 for sample in data]
            T3_samples = [sample.T3 for sample in data]
            T4_samples = [sample.T4 for sample in data]
            
            # Store each sample in the deques
            for value in O1_samples:
                self.deques['signal']['O1']['timestamps'].append(current_time)
                self.deques['signal']['O1']['values'].append(value)
            
            for value in O2_samples:
                self.deques['signal']['O2']['timestamps'].append(current_time)
                self.deques['signal']['O2']['values'].append(value)
                
            for value in T3_samples:
                self.deques['signal']['T3']['timestamps'].append(current_time)
                self.deques['signal']['T3']['values'].append(value)
                
            for value in T4_samples:
                self.deques['signal']['T4']['timestamps'].append(current_time)
                self.deques['signal']['T4']['values'].append(value)

            # Emotions Bipolar
            self.emotion_bipolar_controller.process_data(data)

            # Emotions Monopolar
            self.emotion_monopolar_controller.process_data(data)

            # Spectrum
            self.spectrum_controller.process_data(data)


        # Calibrate emotions
        self.emotion_bipolar_controller.start_calibration()
        self.emotion_monopolar_controller.start_calibration()

        self.brain_bit_controller.signalReceived = on_signal_received
        self.brain_bit_controller.start_signal()


    def start_signal_collection(self):
        def on_signal_received(data):
            current_time = time()
            
            # Extract samples for each channel
            O1_samples = [sample.O1 for sample in data]
            O2_samples = [sample.O2 for sample in data]
            T3_samples = [sample.T3 for sample in data]
            T4_samples = [sample.T4 for sample in data]
            
            # Store each sample in the deques
            for value in O1_samples:
                self.deques['signal']['O1']['timestamps'].append(current_time)
                self.deques['signal']['O1']['values'].append(value)
            
            for value in O2_samples:
                self.deques['signal']['O2']['timestamps'].append(current_time)
                self.deques['signal']['O2']['values'].append(value)
                
            for value in T3_samples:
                self.deques['signal']['T3']['timestamps'].append(current_time)
                self.deques['signal']['T3']['values'].append(value)
                
            for value in T4_samples:
                self.deques['signal']['T4']['timestamps'].append(current_time)
                self.deques['signal']['T4']['values'].append(value)
        
        self.brain_bit_controller.signalReceived = on_signal_received
        print("Starting signal collection...")
        self.brain_bit_controller.start_signal()
        self.brain_bit_controller.start_resist()
        

    def start_resist_collection(self):
        def on_resist_received(resist):
            current_time = time()
            # Split resistance data into respective channels
            for channel in ['O1', 'O2', 'T3', 'T4']:
                self.deques['resist'][channel]['timestamps'].append(current_time)
                self.deques['resist'][channel]['values'].append(getattr(resist, channel))
                
        self.brain_bit_controller.resistReceived = on_resist_received
        print("Starting resistance collection...")
        self.brain_bit_controller.start_resist()
        
    def start_emotions_bipolar_collection(self):    
        self.emotion_bipolar_controller.start_calibration()
        self.brain_bit_controller.signalReceived = self.emotion_bipolar_controller.process_data
        print("Starting bipolar emotions collection...")
        self.brain_bit_controller.start_signal()
        

    def start_emotions_monopolar_collection(self):
        self.emotion_monopolar_controller.start_calibration()
        self.brain_bit_controller.signalReceived = self.emotion_monopolar_controller.process_data
        print("Starting monopolar emotions collection...")
        self.brain_bit_controller.start_signal()
        

    def start_spectrum_collection(self):
        def signal_received(data):
            self.spectrum_controller.process_data(data)
        
        self.brain_bit_controller.signalReceived = signal_received
        print("Starting spectrum collection...")
        self.brain_bit_controller.start_signal()


    ''' Stopping data collection '''
    def stop_all_data_collection(self):
        self.stop_signal_collection()
        self.stop_resist_collection()

    def stop_signal_collection(self):
        print("Stopping signal collection...")
        self.brain_bit_controller.stop_signal()
        
    def stop_resist_collection(self):
        print("Stopping resistance collection...")
        self.brain_bit_controller.stop_resist()
        
    def stop_emotions_bipolar_collection(self):
        print("Stopping bipolar emotions collection...")
        self.brain_bit_controller.stop_signal()
        self.brain_bit_controller.signalReceived = None
        
    def stop_emotions_monopolar_collection(self):
        print("Stopping monopolar emotions collection...")
        self.brain_bit_controller.stop_signal()
        self.brain_bit_controller.signalReceived = None
        
    def stop_spectrum_collection(self):
        print("Stopping spectrum collection...")
        self.brain_bit_controller.stop_signal()
        self.brain_bit_controller.signalReceived = None


    ''' Properties '''
    @property
    def battery_level(self):
        return self.brain_bit_controller.sensorBattery
    
    @property
    def bipolar_is_calibrated(self):
        return self.emotion_bipolar_controller.is_calibrated
    
    @property
    def monopolar_is_calibrated(self):
        # Returns a dictionary of the calibration status of each channel
        return self.emotion_monopolar_controller.is_calibrated
