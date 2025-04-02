package com.owen.brainlink.datamanagement;

import java.util.ArrayList;

public interface PythonInterface {
    public String get_eeg_data_type();
    public void set_eeg_data_type(String type);
    public String get_eeg_data_path();
    public void set_eeg_data_path(String path);
    public ArrayList<ArrayList<Double>> get_new_data();
    public void connect_to_java();
    public boolean connect_eeg();
    public void start_eeg_collection();
    public void stop_eeg_collection();
    public int get_bipolar_calibration_progress();
    public boolean is_bipolar_calibrated();
    public int get_monopolar_calibration_progress(String channel);
    public boolean is_monopolar_calibrated(String channel);
    public boolean connect_heg();
    public void start_heg_collection();
    public void stop_heg_collection();
    public void close();
    public void ping();
}

