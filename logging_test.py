from Controller import Controller
from time import sleep
import os

def log_deques_to_files(controller, base_dir="logs"):
    """
    Log all deques to files, organizing them in a folder structure that mirrors the dictionary structure.
    
    Folder structure will be:
    logs/
    ├── signal/
    │   ├── O1.csv
    │   ├── O2.csv
    │   ├── T3.csv
    │   └── T4.csv
    ├── resist/
    │   └── ...
    ├── emotions_bipolar/
    │   ├── calibration_progress.csv
    │   ├── artefacted_sequence.csv
    │   ├── waves/
    │   │   ├── delta/
    │   │   │   ├── raw.csv
    │   │   │   └── percent.csv
    │   │   └── ...
    │   └── mind/
    │       ├── attention/
    │       │   ├── raw.csv
    │       │   └── percent.csv
    │       └── relaxation/
    │           └── ...
    └── ...
    """
    
    # Create base logs directory
    os.makedirs(base_dir, exist_ok=True)
    
    deques = controller.deques
    
    # Signal and Resist (same structure)
    for data_type in ['signal', 'resist']:
        data_dir = os.path.join(base_dir, data_type)
        os.makedirs(data_dir, exist_ok=True)
        
        for channel in ['O1', 'O2', 'T3', 'T4']:
            filename = os.path.join(data_dir, f"{channel}.csv")
            with open(filename, 'w') as f:
                f.write("timestamp,value\n")
                for t, v in zip(deques[data_type][channel]['timestamps'], 
                              deques[data_type][channel]['values']):
                    f.write(f"{t},{v}\n")
    
    # Emotions Bipolar
    bp_dir = os.path.join(base_dir, "emotions_bipolar")
    os.makedirs(bp_dir, exist_ok=True)
    
    # Base metrics
    for metric in ['calibration_progress', 'artefacted_sequence', 'artefacted_both_side']:
        filename = os.path.join(bp_dir, f"{metric}.csv")
        with open(filename, 'w') as f:
            f.write("timestamp,value\n")
            for t, v in zip(deques['emotions_bipolar'][metric]['timestamps'],
                          deques['emotions_bipolar'][metric]['values']):
                f.write(f"{t},{v}\n")
    
    # Waves data
    bp_waves_dir = os.path.join(bp_dir, "waves")
    os.makedirs(bp_waves_dir, exist_ok=True)
    
    for wave in ['delta', 'theta', 'alpha', 'beta', 'gamma']:
        wave_dir = os.path.join(bp_waves_dir, wave)
        os.makedirs(wave_dir, exist_ok=True)
        
        # Percent data
        with open(os.path.join(wave_dir, "percent.csv"), 'w') as f:
            f.write("timestamp,value\n")
            for t, v in zip(deques['emotions_bipolar'][wave]['percent']['timestamps'],
                          deques['emotions_bipolar'][wave]['percent']['values']):
                f.write(f"{t},{v}\n")
        
        # Raw data (only for alpha and beta)
        if wave in ['alpha', 'beta']:
            with open(os.path.join(wave_dir, "raw.csv"), 'w') as f:
                f.write("timestamp,value\n")
                for t, v in zip(deques['emotions_bipolar'][wave]['raw']['timestamps'],
                              deques['emotions_bipolar'][wave]['raw']['values']):
                    f.write(f"{t},{v}\n")
    
    # Mind data (attention and relaxation)
    bp_mind_dir = os.path.join(bp_dir, "mind")
    os.makedirs(bp_mind_dir, exist_ok=True)
    
    for metric in ['attention', 'relaxation']:
        mind_metric_dir = os.path.join(bp_mind_dir, metric)
        os.makedirs(mind_metric_dir, exist_ok=True)
        
        for data_type in ['raw', 'percent']:
            filename = os.path.join(mind_metric_dir, f"{data_type}.csv")
            with open(filename, 'w') as f:
                f.write("timestamp,value\n")
                for t, v in zip(deques['emotions_bipolar'][metric][data_type]['timestamps'],
                              deques['emotions_bipolar'][metric][data_type]['values']):
                    f.write(f"{t},{v}\n")
    
    # Emotions Monopolar (similar structure for each channel)
    mp_dir = os.path.join(base_dir, "emotions_monopolar")
    
    for channel in ['O1', 'O2', 'T3', 'T4']:
        channel_dir = os.path.join(mp_dir, channel)
        os.makedirs(channel_dir, exist_ok=True)
        
        # Base metrics
        for metric in ['calibration_progress', 'artefacted_sequence', 'artefacted_both_side']:
            filename = os.path.join(channel_dir, f"{metric}.csv")
            with open(filename, 'w') as f:
                f.write("timestamp,value\n")
                for t, v in zip(deques['emotions_monopolar'][channel][metric]['timestamps'],
                              deques['emotions_monopolar'][channel][metric]['values']):
                    f.write(f"{t},{v}\n")
        
        # Waves data
        waves_dir = os.path.join(channel_dir, "waves")
        os.makedirs(waves_dir, exist_ok=True)
        
        for wave in ['delta', 'theta', 'alpha', 'beta', 'gamma']:
            wave_dir = os.path.join(waves_dir, wave)
            os.makedirs(wave_dir, exist_ok=True)
            
            # Percent data
            with open(os.path.join(wave_dir, "percent.csv"), 'w') as f:
                f.write("timestamp,value\n")
                for t, v in zip(deques['emotions_monopolar'][channel][wave]['percent']['timestamps'],
                              deques['emotions_monopolar'][channel][wave]['percent']['values']):
                    f.write(f"{t},{v}\n")
            
            # Raw data (only for alpha and beta)
            if wave in ['alpha', 'beta']:
                with open(os.path.join(wave_dir, "raw.csv"), 'w') as f:
                    f.write("timestamp,value\n")
                    for t, v in zip(deques['emotions_monopolar'][channel][wave]['raw']['timestamps'],
                                  deques['emotions_monopolar'][channel][wave]['raw']['values']):
                        f.write(f"{t},{v}\n")
        
        # Mind data
        mind_dir = os.path.join(channel_dir, "mind")
        os.makedirs(mind_dir, exist_ok=True)
        
        for metric in ['attention', 'relaxation']:
            metric_dir = os.path.join(mind_dir, metric)
            os.makedirs(metric_dir, exist_ok=True)
            
            for data_type in ['raw', 'percent']:
                filename = os.path.join(metric_dir, f"{data_type}.csv")
                with open(filename, 'w') as f:
                    f.write("timestamp,value\n")
                    for t, v in zip(deques['emotions_monopolar'][channel][metric][data_type]['timestamps'],
                                  deques['emotions_monopolar'][channel][metric][data_type]['values']):
                        f.write(f"{t},{v}\n")
    
    # Spectrum
    spectrum_dir = os.path.join(base_dir, "spectrum")
    os.makedirs(spectrum_dir, exist_ok=True)
    
    for channel in ['O1', 'O2', 'T3', 'T4']:
        filename = os.path.join(spectrum_dir, f"{channel}.csv")
        with open(filename, 'w') as f:
            f.write("timestamp,value\n")
            for t, v in zip(deques['spectrum'][channel]['timestamps'],
                          deques['spectrum'][channel]['values']):
                f.write(f"{t},{v}\n")
    
    # Waves
    waves_dir = os.path.join(base_dir, "waves")
    
    for channel in ['O1', 'O2', 'T3', 'T4']:
        channel_dir = os.path.join(waves_dir, channel)
        os.makedirs(channel_dir, exist_ok=True)
        
        for wave in ['delta', 'theta', 'alpha', 'beta', 'gamma']:
            wave_dir = os.path.join(channel_dir, wave)
            os.makedirs(wave_dir, exist_ok=True)
            
            for data_type in ['raw', 'percent']:
                filename = os.path.join(wave_dir, f"{data_type}.csv")
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

