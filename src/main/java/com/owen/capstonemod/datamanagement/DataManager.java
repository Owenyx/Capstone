package com.owen.capstonemod.datamanagement;

/*
This class will be the centralized location for all EEG and HEG data management for the mod.
It is a singleton class, so only one instance will exist.
*/

public class DataManager {
    private static DataManager instance;
    private DataBridge dataBridge;
    private boolean isEEGConnected = false;

    private DataManager() {
        dataBridge = new DataBridge();
    }

    public static DataManager getInstance() {
        if (instance == null) {
            instance = new DataManager();
        }
        return instance;
    }

    public boolean connectEEG() {
        return dataBridge.connectEEG();
    }

    public void startEEGCollection() {
        dataBridge.startEEGCollection();
    }

    public void stopEEGCollection() {
        dataBridge.stopEEGCollection();
    }

    public boolean isEEGConnected() {
        return isEEGConnected;
    }
}   