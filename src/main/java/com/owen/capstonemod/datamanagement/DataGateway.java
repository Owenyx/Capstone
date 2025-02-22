package com.owen.capstonemod.datamanagement;

import java.util.Map;
import java.util.ArrayDeque;

// This interface is used to communicate with the Python gateway
public interface DataGateway {
    // These method signatures must exactly match the Python class methods
    boolean connect_eeg();
    void start_eeg_collection();
    void stop_eeg_collection();
    void setEeg_data_path(String path);
    
    void start_heg_collection();
    void stop_heg_collection();
    
    Map<String, ArrayDeque<Double>> get_data();
    void cleanup();
} 