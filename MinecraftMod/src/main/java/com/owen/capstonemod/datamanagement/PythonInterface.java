package com.owen.capstonemod.datamanagement;

public interface PythonInterface {
    public String get_eeg_data_type();
    public void set_eeg_data_type(String type);
    public String get_eeg_data_path();
    public void set_eeg_data_path(String path);
    public void transfer_data();
    public void connect_to_java();
    public boolean connect_eeg();
    public void start_eeg_collection();
    public void stop_eeg_collection();
    public boolean connect_heg();
    public void start_heg_collection();
    public void stop_heg_collection();
    public void close();
    public void ping();
}

