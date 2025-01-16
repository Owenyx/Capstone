import sys
from PyQt6.QtWidgets import QApplication

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
from time import sleep

def main():
    # Create controller and connect to eeg
    controller = Controller()
    controller.find_and_connect()

    signal_file = "logs/signal.log"
    resist_file = "logs/resist.log"
    emotions_bipolar_file = "logs/emotions_bipolar.log"
    emotions_monopolar_file = "logs/emotions_monopolar.log"
    spectrum_file = "logs/spectrum.log"
    waves_file = "logs/waves.log"

    # Set which files to output to
    controller.signal_file = signal_file
    controller.resist_file = resist_file
    controller.emotions_bipolar_file = emotions_bipolar_file
    controller.emotions_monopolar_file = emotions_monopolar_file
    controller.spectrum_file = spectrum_file
    controller.waves_file = waves_file
    # Wipe existing files
    open(signal_file, 'w').close()
    open(resist_file, 'w').close()
    open(emotions_bipolar_file, 'w').close()
    open(emotions_monopolar_file, 'w').close()
    open(spectrum_file, 'w').close()
    open(waves_file, 'w').close()

    # Start collecting data
    controller.output_resist_data()
    sleep(5)
    controller.stop_resist()
    controller.output_signal_data()
    sleep(1)
    controller.stop_signal()
    controller.output_emotions_bipolar_data()
    sleep(25)
    controller.stop_emotions_bipolar()
    controller.output_emotions_monopolar_data()
    sleep(25)
    controller.stop_emotions_monopolar()
    controller.output_spectrum_data()
    sleep(5)
    controller.stop_spectrum()
    

class Controller:
    def __init__(self):
        self.brain_bit_controller = BrainBitController()
        self.emotion_bipolar_controller = EmotionBipolar()
        self.emotion_monopolar_controller = EmotionMonopolar()
        self.spectrum_controller = SpectrumController()
        self.signal_file = None
        self.resist_file = None
        self.emotions_bipolar_file = None
        self.emotions_monopolar_file = None
        self.spectrum_file = None
        self.waves_file = None

        # Set up event handlers each controller
        self.emotion_bipolar_controller.progressCalibrationCallback = self.bp_calibration_callback
        self.emotion_bipolar_controller.isArtifactedSequenceCallback = self.bp_is_artifacted_sequence_callback
        self.emotion_bipolar_controller.isBothSidesArtifactedCallback = self.bp_is_both_sides_artifacted_callback
        self.emotion_bipolar_controller.lastMindDataCallback = self.bp_mind_data_callback
        self.emotion_bipolar_controller.lastSpectralDataCallback = self.bp_last_spectral_data_callback
        self.emotion_bipolar_controller.rawSpectralDataCallback = self.bp_raw_spectral_data_callback

        self.emotion_monopolar_controller.progressCalibrationCallback = self.mp_calibration_callback
        self.emotion_monopolar_controller.isArtifactedSequenceCallback = self.mp_is_artifacted_sequence_callback
        self.emotion_monopolar_controller.isBothSidesArtifactedCallback = self.mp_is_both_sides_artifacted_callback
        self.emotion_monopolar_controller.lastMindDataCallback = self.mp_mind_data_callback
        self.emotion_monopolar_controller.lastSpectralDataCallback = self.mp_last_spectral_data_callback
        self.emotion_monopolar_controller.rawSpectralDataCallback = self.mp_raw_spectral_data_callback

        self.spectrum_controller.processedWaves = self.__processed_waves
        self.spectrum_controller.processedSpectrum = self.__processed_spectrum

    # Handler code - these are all just copied and will be changed later
    # Bipolar handlers
    def bp_calibration_callback(self, progress):
        with open(self.emotions_bipolar_file, 'a') as f:
            f.write(f"Calibration progress: {progress}\n")

    def bp_is_artifacted_sequence_callback(self, artifacted):
        with open(self.emotions_bipolar_file, 'a') as f:
            f.write(f"Artefacted sequence: {artifacted}\n")

    def bp_is_both_sides_artifacted_callback(self, artifacted):
        with open(self.emotions_bipolar_file, 'a') as f:
            f.write(f"Artefacted both side: {artifacted}\n")

    def bp_mind_data_callback(self, data):
        with open(self.emotions_bipolar_file, 'a') as f:
            f.write(f"Attention: {round(data.rel_attention, 2)}%, Relaxation: {round(data.rel_relaxation, 2)}%, Raw Attention: {round(data.inst_attention, 2)}, Raw Relaxation: {round(data.inst_relaxation, 2)}\n")

    def bp_last_spectral_data_callback(self, spectral_data):
        with open(self.emotions_bipolar_file, 'a') as f:
            f.write(f"Delta: {round(spectral_data.delta * 100, 2)}%, Theta: {round(spectral_data.theta * 100, 2)}%, Alpha: {round(spectral_data.alpha * 100, 2)}%, Beta: {round(spectral_data.beta * 100, 2)}%, Gamma: {round(spectral_data.gamma * 100, 2)}%\n")

    def bp_raw_spectral_data_callback(self, spect_vals):
        with open(self.emotions_bipolar_file, 'a') as f:
            f.write(f"Alpha: {round(spect_vals.alpha, 2)}, Beta: {round(spect_vals.beta, 2)}\n")

    # Monopolar handlers
    def mp_calibration_callback(self, progress, channel):
        with open(self.emotions_monopolar_file, 'a') as f:
            f.write(f"{channel} - Calibration progress: {progress}\n")

    def mp_is_artifacted_sequence_callback(self, artifacted, channel):
        with open(self.emotions_monopolar_file, 'a') as f:
            f.write(f"{channel} - Artefacted sequence: {artifacted}\n")

    def mp_is_both_sides_artifacted_callback(self, artifacted, channel):
        with open(self.emotions_monopolar_file, 'a') as f:
            f.write(f"{channel} - Artefacted both side: {artifacted}\n")

    def mp_mind_data_callback(self, data, channel):
        with open(self.emotions_monopolar_file, 'a') as f:
            f.write(f"{channel} - Attention: {round(data.rel_attention, 2)}%, Relaxation: {round(data.rel_relaxation, 2)}%, Raw Attention: {round(data.inst_attention, 2)}, Raw Relaxation: {round(data.inst_relaxation, 2)}\n")

    def mp_last_spectral_data_callback(self, spectral_data, channel):
        with open(self.emotions_monopolar_file, 'a') as f:
            f.write(f"{channel} - Delta: {round(spectral_data.delta * 100, 2)}%, Theta: {round(spectral_data.theta * 100, 2)}%, Alpha: {round(spectral_data.alpha * 100, 2)}%, Beta: {round(spectral_data.beta * 100, 2)}%, Gamma: {round(spectral_data.gamma * 100, 2)}%\n")

    def mp_raw_spectral_data_callback(self, spect_vals, channel):
        with open(self.emotions_monopolar_file, 'a') as f:
            f.write(f"{channel} - Alpha: {round(spect_vals.alpha, 2)}, Beta: {round(spect_vals.beta, 2)}\n")

    # Spectrum handlers
    def __processed_waves(self, waves, channel):
        match channel:
            case 'O1':
                with open(self.spectrum_file, 'a') as f:
                    f.write(f"O1 Raw Values:\n")
                    f.write(f"Alpha: {round(waves.alpha_raw, 4)}\n")
                    f.write(f"Beta: {round(waves.beta_raw, 4)}\n") 
                    f.write(f"Theta: {round(waves.theta_raw, 4)}\n")
                    f.write(f"Delta: {round(waves.delta_raw, 4)}\n")
                    f.write(f"Gamma: {round(waves.gamma_raw, 4)}\n")
                    f.write(f"O1 Percentages:\n")
                    f.write(f"Alpha: {round(waves.alpha_rel * 100)}%\n")
                    f.write(f"Beta: {round(waves.beta_rel * 100)}%\n")
                    f.write(f"Theta: {round(waves.theta_rel * 100)}%\n") 
                    f.write(f"Delta: {round(waves.delta_rel * 100)}%\n")
                    f.write(f"Gamma: {round(waves.gamma_rel * 100)}%\n")
                    f.write("\n")
            case 'O2':
                with open(self.spectrum_file, 'a') as f:
                    f.write(f"O2 Raw Values:\n")
                    f.write(f"Alpha: {round(waves.alpha_raw, 4)}\n")
                    f.write(f"Beta: {round(waves.beta_raw, 4)}\n") 
                    f.write(f"Theta: {round(waves.theta_raw, 4)}\n")
                    f.write(f"Delta: {round(waves.delta_raw, 4)}\n")
                    f.write(f"Gamma: {round(waves.gamma_raw, 4)}\n")
                    f.write(f"O2 Percentages:\n")
                    f.write(f"Alpha: {round(waves.alpha_rel * 100)}%\n")
                    f.write(f"Beta: {round(waves.beta_rel * 100)}%\n")
                    f.write(f"Theta: {round(waves.theta_rel * 100)}%\n")
                    f.write(f"Delta: {round(waves.delta_rel * 100)}%\n")
                    f.write(f"Gamma: {round(waves.gamma_rel * 100)}%\n")
                    f.write("\n")
            case 'T3':
                with open(self.spectrum_file, 'a') as f:
                    f.write(f"T3 Raw Values:\n")
                    f.write(f"Alpha: {round(waves.alpha_raw, 4)}\n")
                    f.write(f"Beta: {round(waves.beta_raw, 4)}\n") 
                    f.write(f"Theta: {round(waves.theta_raw, 4)}\n")
                    f.write(f"Delta: {round(waves.delta_raw, 4)}\n")
                    f.write(f"Gamma: {round(waves.gamma_raw, 4)}\n")
                    f.write(f"T3 Percentages:\n")
                    f.write(f"Alpha: {round(waves.alpha_rel * 100)}%\n")
                    f.write(f"Beta: {round(waves.beta_rel * 100)}%\n")
                    f.write(f"Theta: {round(waves.theta_rel * 100)}%\n")
                    f.write(f"Delta: {round(waves.delta_rel * 100)}%\n")
                    f.write(f"Gamma: {round(waves.gamma_rel * 100)}%\n")
                    f.write("\n")
            case 'T4':
                with open(self.spectrum_file, 'a') as f:
                    f.write(f"T4 Raw Values:\n")
                    f.write(f"Alpha: {round(waves.alpha_raw, 4)}\n")
                    f.write(f"Beta: {round(waves.beta_raw, 4)}\n") 
                    f.write(f"Theta: {round(waves.theta_raw, 4)}\n")
                    f.write(f"Delta: {round(waves.delta_raw, 4)}\n")
                    f.write(f"Gamma: {round(waves.gamma_raw, 4)}\n")
                    f.write(f"T4 Percentages:\n")
                    f.write(f"Alpha: {round(waves.alpha_rel * 100)}%\n")
                    f.write(f"Beta: {round(waves.beta_rel * 100)}%\n")
                    f.write(f"Theta: {round(waves.theta_rel * 100)}%\n")
                    f.write(f"Delta: {round(waves.delta_rel * 100)}%\n")
                    f.write(f"Gamma: {round(waves.gamma_rel * 100)}%\n")
                    f.write("\n")
            case _:
                print('Unknown channel')

    def __processed_spectrum(self, spectrum, channel):
        match channel:
            case 'O1':
                with open(self.spectrum_file, 'a') as f:
                    f.write(f"O1 Spectrum:\n")
                    f.write(str(spectrum) + '\n')
                    f.write("\n")
            case 'O2':
                with open(self.spectrum_file, 'a') as f:
                    f.write(f"O2 Spectrum:\n")
                    f.write(str(spectrum) + '\n')
                    f.write("\n")
            case 'T3':
                with open(self.spectrum_file, 'a') as f:
                    f.write(f"T3 Spectrum:\n")
                    f.write(str(spectrum) + '\n')
                    f.write("\n")
            case 'T4':
                with open(self.spectrum_file, 'a') as f:
                    f.write(f"T4 Spectrum:\n")
                    f.write(str(spectrum) + '\n')
                    f.write("\n")
            case _:
                print('Unknown channel')

    # This function is for finding and connecting to the sensor, as well as setting up event handlers for it
    def find_and_connect(self):
        def on_sensors_found(sensors):
            self.sensors = sensors
        
        self.brain_bit_controller.sensorsFounded = on_sensors_found
        print("Scanning for 5 seconds...")
        self.brain_bit_controller.start_scan()
        
        sleep(5)
        
        self.brain_bit_controller.stop_scan()
        
        if not hasattr(self, 'sensors') or len(self.sensors) == 0:
            print("No sensors found")
            return
        
        try:
            # Connect to first available sensor
            self.brain_bit_controller.create_and_connect(sensor_info=self.sensors[0])
            print(f"Connected to sensor: {self.sensors[0].Name}")
            
            # Wait for connection to establish
            sleep(2)
            
        except Exception as e:
            print(f"Error connecting to sensor: {str(e)}")
            return

    # This next family of functions are for outputting data into files.
    
    def output_signal_data(self):
        def on_signal_received(data):
            with open(self.signal_file, 'a') as f:
                f.write(str(data) + '\n')
                
        self.brain_bit_controller.signalReceived = on_signal_received
        print("Starting signal collection...")
        self.brain_bit_controller.start_signal()
        


    def output_resist_data(self):
        def on_resist_received(resist):
            with open(self.resist_file, 'a') as f:
                f.write(str(resist) + '\n')
                
        self.brain_bit_controller.resistReceived = on_resist_received
        print("Starting resistance collection...")
        self.brain_bit_controller.start_resist()
        


    def output_emotions_bipolar_data(self):
        def on_spectral_data(data):
            with open(self.emotions_bipolar_file, 'a') as f:
                f.write(str(data) + '\n')
                    
        self.emotion_bipolar_controller.start_calibration()
        self.brain_bit_controller.signalReceived = self.emotion_bipolar_controller.process_data
        print("Starting bipolar emotions collection...")
        self.brain_bit_controller.start_signal()
        


    def output_emotions_monopolar_data(self):
            
        self.emotion_monopolar_controller.start_calibration()
        self.brain_bit_controller.signalReceived = self.emotion_monopolar_controller.process_data
        print("Starting monopolar emotions collection...")
        self.brain_bit_controller.start_signal()
        


    def output_spectrum_data(self):
        def signal_received(data):
            self.spectrum_controller.process_data(data)
        
        self.spectrum_controller.processedWaves = self.__processed_waves
        self.spectrum_controller.processedSpectrum = self.__processed_spectrum
        self.brain_bit_controller.signalReceived = signal_received
        print("Starting spectrum collection...")
        self.brain_bit_controller.start_signal()


    # This next family of functions are for stopping the data collection
    def stop_signal(self):
        print("Stopping signal collection...")
        self.brain_bit_controller.stop_signal()
        
    def stop_resist(self):
        print("Stopping resistance collection...")
        self.brain_bit_controller.stop_resist()
        
    def stop_emotions_bipolar(self):
        print("Stopping bipolar emotions collection...")
        self.brain_bit_controller.stop_signal()
        self.brain_bit_controller.signalReceived = None
        
    def stop_emotions_monopolar(self):
        print("Stopping monopolar emotions collection...")
        self.brain_bit_controller.stop_signal()
        self.brain_bit_controller.signalReceived = None
        
    def stop_spectrum(self):
        print("Stopping spectrum collection...")
        self.brain_bit_controller.stop_signal()
        self.brain_bit_controller.signalReceived = None


if __name__ == "__main__":
    main()

