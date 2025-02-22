package com.owen.capstonemod.datamanagement;

/*
This class will be the centralized location for all EEG and HEG data management for the mod.
*/

public class DataManager {
    private DataBridge dataBridge;

    public DataManager() {
        dataBridge = new DataBridge();
    }

    public void initializeEEG() {
        DataBridge.startPythonGateway();
        dataBridge.connectEEG();
    }

    public void initializeHEG() {
        DataBridge.startPythonGateway();
    }
    

}   