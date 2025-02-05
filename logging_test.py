from Controller import Controller
from time import sleep
import os

def log_deques_to_files(controller, base_dir="logs"):
    """Log all leaf deques to files, combining timestamps with their values."""
    
    # Create logs directory if it doesn't exist
    os.makedirs(base_dir, exist_ok=True)
    
    deques = controller.deques
    
    # Signal and Resist (same structure)
    for data_type in ['signal', 'resist']:
        for channel in ['O1', 'O2', 'T3', 'T4']:
            filename = f"{base_dir}/{data_type}_{channel}.csv"
            with open(filename, 'w') as f:
                f.write("timestamp,value\n")
                for t, v in zip(deques[data_type][channel]['timestamps'], 
                              deques[data_type][channel]['values']):
                    f.write(f"{t},{v}\n")
    
    # Emotions Bipolar
    for metric in ['calibration_progress', 'artefacted_sequence', 'artefacted_both_side']:
        filename = f"{base_dir}/emotions_bipolar_{metric}.csv"
        with open(filename, 'w') as f:
            f.write("timestamp,value\n")
            for t, v in zip(deques['emotions_bipolar'][metric]['timestamps'],
                          deques['emotions_bipolar'][metric]['values']):
                f.write(f"{t},{v}\n")
    
    # Handle percent data for all waves
    for wave in ['delta', 'theta', 'alpha', 'beta', 'gamma', 'attention', 'relaxation']:
        filename = f"{base_dir}/emotions_bipolar_{wave}_percent.csv"
        with open(filename, 'w') as f:
            f.write("timestamp,value\n")
            for t, v in zip(deques['emotions_bipolar'][wave]['percent']['timestamps'],
                          deques['emotions_bipolar'][wave]['percent']['values']):
                f.write(f"{t},{v}\n")
    
    # Handle raw data only for alpha and beta waves, as well as attention and relaxation
    for wave in ['alpha', 'beta', 'attention', 'relaxation']:
        filename = f"{base_dir}/emotions_bipolar_{wave}_raw.csv"
        with open(filename, 'w') as f:
            f.write("timestamp,value\n")
            for t, v in zip(deques['emotions_bipolar'][wave]['raw']['timestamps'],
                          deques['emotions_bipolar'][wave]['raw']['values']):
                f.write(f"{t},{v}\n")
    
    # Emotions Monopolar
    for channel in ['O1', 'O2', 'T3', 'T4']:
        for metric in ['calibration_progress', 'artefacted_sequence', 'artefacted_both_side']:
            filename = f"{base_dir}/emotions_monopolar_{channel}_{metric}.csv"
            with open(filename, 'w') as f:
                f.write("timestamp,value\n")
                for t, v in zip(deques['emotions_monopolar'][channel][metric]['timestamps'],
                              deques['emotions_monopolar'][channel][metric]['values']):
                    f.write(f"{t},{v}\n")
        
        # Handle percent data for all waves
        for wave in ['delta', 'theta', 'alpha', 'beta', 'gamma', 'attention', 'relaxation']:
            filename = f"{base_dir}/emotions_monopolar_{channel}_{wave}_percent.csv"
            with open(filename, 'w') as f:
                f.write("timestamp,value\n")
                for t, v in zip(deques['emotions_monopolar'][channel][wave]['percent']['timestamps'],
                              deques['emotions_monopolar'][channel][wave]['percent']['values']):
                    f.write(f"{t},{v}\n")
        
        # Handle raw data only for alpha and beta waves, as well as attention and relaxation
        for wave in ['alpha', 'beta', 'attention', 'relaxation']:
            filename = f"{base_dir}/emotions_monopolar_{channel}_{wave}_raw.csv"
            with open(filename, 'w') as f:
                f.write("timestamp,value\n")
                for t, v in zip(deques['emotions_monopolar'][channel][wave]['raw']['timestamps'],
                              deques['emotions_monopolar'][channel][wave]['raw']['values']):
                    f.write(f"{t},{v}\n")
    
    # Spectrum
    for channel in ['O1', 'O2', 'T3', 'T4']:
        filename = f"{base_dir}/spectrum_{channel}.csv"
        with open(filename, 'w') as f:
            f.write("timestamp,value\n")
            for t, v in zip(deques['spectrum'][channel]['timestamps'],
                          deques['spectrum'][channel]['values']):
                f.write(f"{t},{v}\n")
    
    # Waves
    for channel in ['O1', 'O2', 'T3', 'T4']:
        for wave in ['delta', 'theta', 'alpha', 'beta', 'gamma']:
            for data_type in ['raw', 'percent']:
                filename = f"{base_dir}/waves_{channel}_{wave}_{data_type}.csv"
                with open(filename, 'w') as f:
                    f.write("timestamp,value\n")
                    for t, v in zip(deques['waves'][channel][wave][data_type]['timestamps'],
                                  deques['waves'][channel][wave][data_type]['values']):
                        f.write(f"{t},{v}\n")

controller = Controller()

controller.find_and_connect()

# Data collection
controller.start_signal_collection()
print('Press Enter to stop signal collection')
#input()
sleep(5)    
controller.stop_signal_collection()


controller.start_resist_collection()
print('Press Enter to stop resist collection')
#input()
sleep(5)    
controller.stop_resist_collection()

controller.start_emotions_bipolar_collection()
print('Press Enter to stop emotions bipolar collection')
#input()
sleep(5)
controller.stop_emotions_bipolar_collection()


controller.start_emotions_monopolar_collection()
print('Press Enter to stop emotions monopolar collection')
#input()
sleep(5)
controller.stop_emotions_monopolar_collection()


controller.start_spectrum_collection()
print('Press Enter to stop spectrum collection')
#input()
sleep(5)
controller.stop_spectrum_collection()


# Log all data into files
log_deques_to_files(controller)

