import sys
from PyQt6.QtWidgets import QApplication
from collections import deque
from time import sleep, time
import os
import copy
from threading import Thread
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
# - Add a visual representation of the deques in another file
# - Track state of connection to device

class Controller:
    def __init__(self):
        self.brain_bit_controller = BrainBitController()
        self.emotion_bipolar_controller = EmotionBipolar()
        self.emotion_monopolar_controller = EmotionMonopolar()
        self.spectrum_controller = SpectrumController()

        self.bipolar_calibration_progress = 0 # Used for emotions
        self.monopolar_calibration_progress = {'O1': 0, 'O2': 0, 'T3': 0, 'T4': 0} # Used for emotions
        
        self._storage_time = 10 # How long to store data for in seconds

        self.signal_freq = 250 # Hz
        self.resist_freq = 1 # Hz
        self.emotions_freq = 25 # Hz
        self.spectrum_freq = 5 # Hz
        self.waves_freq = 5 # Hz

        # Calculate the size of the deques based on the storage time and the frequency of the data
        self.signal_size = self._storage_time*self.signal_freq
        self.resist_size = self._storage_time*self.resist_freq
        self.emotions_size = self._storage_time*self.emotions_freq
        self.spectrum_size = self._storage_time*self.spectrum_freq
        self.waves_size = self._storage_time*self.waves_freq
        
        # Once the dictionary definitions are set in stone we will use helper functions to create duplicated dictionary structures because these definintions are huge
        # Here's what we have for now for helper functions:

        def create_timestamp_values_dict(size=1000):
            return {
                'timestamps': deque(maxlen=size),
                'values': deque(maxlen=size)
            }

        def create_channel_dict(size=1000):

            return {
                'O1': create_timestamp_values_dict(size),
                'O2': create_timestamp_values_dict(size),
                'T3': create_timestamp_values_dict(size),
                'T4': create_timestamp_values_dict(size)
            }
        
        def create_raw_percent_dict(size=1000):
            return {
                'raw': create_timestamp_values_dict(size),
                'percent': create_timestamp_values_dict(size)
            }
        
        def create_emotions_dict(size=1000):
            return {
                'calibration_progress': create_timestamp_values_dict(size),
                'artefacted_sequence': create_timestamp_values_dict(size),
                'artefacted_both_side': create_timestamp_values_dict(size),
                'delta': create_raw_percent_dict(size),
                'theta': create_raw_percent_dict(size),
                'alpha': create_raw_percent_dict(size),
                'beta': create_raw_percent_dict(size),
                'gamma': create_raw_percent_dict(size),
                'attention': create_raw_percent_dict(size),
                'relaxation': create_raw_percent_dict(size)
            }
        def create_waves_dict(size=1000):
            return {
                'delta': create_raw_percent_dict(size),
                'theta' : create_raw_percent_dict(size),
                'alpha': create_raw_percent_dict(size),
                'beta': create_raw_percent_dict(size),
                'gamma': create_raw_percent_dict(size)
            }

        # Now we set up the deques in a tree structure using dictionaries
        def create_deques():
            return {
                'signal': create_channel_dict(self.signal_size),
                'resist': create_channel_dict(self.resist_size),
                'emotions_bipolar': create_emotions_dict(self.emotions_size),
                'emotions_monopolar': {
                    'O1': create_emotions_dict(self.emotions_size),
                    'O2': create_emotions_dict(self.emotions_size),
                    'T3': create_emotions_dict(self.emotions_size),
                    'T4': create_emotions_dict(self.emotions_size)
                },
                'spectrum': create_channel_dict(self.spectrum_size),
                'waves': {
                    'O1': create_waves_dict(self.waves_size),
                    'O2': create_waves_dict(self.waves_size),
                    'T3': create_waves_dict(self.waves_size),
                    'T4': create_waves_dict(self.waves_size)
                }
            }
        
        self.deques = create_deques()
    
        # Set up event handlers

        # Signal
        ''' Signal handler is set in the start_collection functions according to data collection type '''

        # Resist
        self.brain_bit_controller.resistReceived = self.on_resist_received

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
        self.spectrum_controller.processedWaves = self._processed_waves
        self.spectrum_controller.processedSpectrum = self._processed_spectrum

        # Battery
        self.brain_bit_controller.sensorBattery = self.on_battery_changed

    # Handler code

    def on_resist_received(self, resist):
        current_time = time()
        # Split resistance data into respective channels
        for channel in ['O1', 'O2', 'T3', 'T4']:
            # Skip if value is the same as the last value for this channel
            if (len(self.deques['resist'][channel]['values']) > 0 and 
                self.deques['resist'][channel]['values'][-1] == getattr(resist, channel)):
                continue

            self.deques['resist'][channel]['timestamps'].append(current_time)
            self.deques['resist'][channel]['values'].append(getattr(resist, channel))

    # Bipolar handlers
    def bp_calibration_callback(self, progress):
        self.bipolar_calibration_progress = progress
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
        self.monopolar_calibration_progress[channel] = progress
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
    def _processed_waves(self, waves, channel):
        current_time = time()
        for wave in ['alpha', 'beta', 'theta', 'delta', 'gamma']:
            self.deques['waves'][channel][wave]['raw']['timestamps'].append(current_time)
            self.deques['waves'][channel][wave]['raw']['values'].append(getattr(waves, f"{wave}_raw"))
            self.deques['waves'][channel][wave]['percent']['timestamps'].append(current_time)
            self.deques['waves'][channel][wave]['percent']['values'].append(getattr(waves, f"{wave}_rel"))

    def _processed_spectrum(self, spectrum, channel):
        current_time = time()
        self.deques['spectrum'][channel]['timestamps'].append(current_time)
        self.deques['spectrum'][channel]['values'].append(spectrum)

    def on_battery_changed(self, battery):
        self.battery_level = battery


    ''' Finding and connecting to the sensor '''
    def find_and_connect(self, timeout=20):
        #Callback for when sensors are found
        def on_sensors_found(sensors):
            self.sensors = sensors
        
        # Assign the callback to the controller and start scanning
        self.brain_bit_controller.sensorsFounded = on_sensors_found
        self.brain_bit_controller.start_scan()
        
        # Wait for sensors to be found, timeout after timeout seconds
        start_time = time()
        while not hasattr(self, 'sensors') or len(self.sensors) == 0:
            if time() - start_time > timeout:
                return False
            sleep(0.1)
        
        # Stop scanning
        self.brain_bit_controller.stop_scan()
        
        # Try to connect to the first available sensor
        try:
            self.brain_bit_controller.create_and_connect(sensor_info=self.sensors[0])
            
            # Wait for connection to establish
            sleep(2)
            
        except Exception as e:
            return False
        
        # Return True if connection was successful
        return True


    ''' Starting data collection and outputting data into the deques '''
    def start_all_data_collection(self):
        # Cannot do resist at the same time, must be done independently
        def on_signal_received(data):

            #Signal
            self.output_signal_data(data)
            
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
            self.output_signal_data(data)
        
        self.brain_bit_controller.signalReceived = on_signal_received
        self.brain_bit_controller.start_signal()
        
    def start_resist_collection(self):
        # Handler already set
        self.brain_bit_controller.start_resist()
        
    def start_emotions_bipolar_collection(self):    
        self.emotion_bipolar_controller.start_calibration()
        self.brain_bit_controller.signalReceived = self.emotion_bipolar_controller.process_data
        self.brain_bit_controller.start_signal()
        
    def start_emotions_monopolar_collection(self):
        self.emotion_monopolar_controller.start_calibration()
        self.brain_bit_controller.signalReceived = self.emotion_monopolar_controller.process_data
        self.brain_bit_controller.start_signal()

    def start_spectrum_collection(self):
        def signal_received(data):
            self.spectrum_controller.process_data(data)
        
        self.brain_bit_controller.signalReceived = signal_received
        self.brain_bit_controller.start_signal()

    def output_signal_data(self, data):
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


    ''' Stopping data collection '''
    def stop_signal_collection(self):
        self.brain_bit_controller.stop_signal()
        
    def stop_resist_collection(self):
        self.brain_bit_controller.stop_resist()

    
    ''' Reset deques '''
    def _clear_recursive(self, data_structure):
        if isinstance(data_structure, dict):
            for value in data_structure.values():
                self._clear_recursive(value)
        elif isinstance(data_structure, list):
            data_structure.clear()

    def reset_deques(self, signal=True, resist=True, emotions_bipolar=True, emotions_monopolar=True, spectrum=True, waves=True):
        if signal:
            self._clear_recursive(self.deques['signal'])
        if resist:
            self._clear_recursive(self.deques['resist'])
        if emotions_bipolar:
            self._clear_recursive(self.deques['emotions_bipolar'])
        if emotions_monopolar:
            self._clear_recursive(self.deques['emotions_monopolar'])
        if spectrum:
            self._clear_recursive(self.deques['spectrum'])
        if waves:
            self._clear_recursive(self.deques['waves'])
            

    ''' Properties '''
    @property
    def storage_time(self):
        return self._storage_time
    
    @storage_time.setter
    # When the storage time is changed, we need to re-initialize the deques with the new sizes
    def storage_time(self, value):
        self._storage_time = value
        self.signal_size = self._storage_time*self.signal_freq
        self.resist_size = self._storage_time*self.resist_freq
        self.emotions_size = self._storage_time*self.emotions_freq
        self.spectrum_size = self._storage_time*self.spectrum_freq
        self.waves_size = self._storage_time*self.waves_freq

        self.deques = self.create_deques()

    @property
    def bipolar_is_calibrated(self):
        return self.emotion_bipolar_controller.is_calibrated
    
    @property
    def monopolar_is_calibrated(self):
        # Returns true only if all channels are calibrated
        calibration_dict = self.emotion_monopolar_controller.is_calibrated
        return all(calibration_dict.values())


    ''' Logging to file '''
    def _write_deques_to_file(self, dict, base_path):
        if 'timestamps' in dict and 'values' in dict:
            # This is a leaf node with timestamp/value deques
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(base_path), exist_ok=True)
            
            # Write/overwrite the file
            with open(base_path + '.csv', 'w') as f:
                f.write("timestamp,value\n")
                for t, v in zip(dict['timestamps'], dict['values']):
                    f.write(f"{t},{v}\n")
        else:
            # This is an internal node with more dictionaries
            for key, value in dict.items():
                self._write_deques_to_file(value, base_path + f"/{key}")

    def log_deques_to_files(self, base_path="logs", signal=False, resist=False, emotions_bipolar=False, emotions_monopolar=False, spectrum=False, waves=False):
        # Data collection must be stopped before logging
        # Create a deep copy of the entire deques structure
        snapshot = copy.deepcopy(self.deques)
        
        # Log each deque in a separate thread now that we've copied
        if signal:
            Thread(target=self._write_deques_to_file, args=(snapshot['signal'], base_path + "/signal")).start()
        if resist:
            Thread(target=self._write_deques_to_file, args=(snapshot['resist'], base_path + "/resist")).start()
        if emotions_bipolar:
            Thread(target=self._write_deques_to_file, args=(snapshot['emotions_bipolar'], base_path + "/emotions_bipolar")).start()
        if emotions_monopolar:
            Thread(target=self._write_deques_to_file, args=(snapshot['emotions_monopolar'], base_path + "/emotions_monopolar")).start()
        if spectrum:
            Thread(target=self._write_deques_to_file, args=(snapshot['spectrum'], base_path + "/spectrum")).start()
        if waves:
            Thread(target=self._write_deques_to_file, args=(snapshot['waves'], base_path + "/waves")).start()
            

