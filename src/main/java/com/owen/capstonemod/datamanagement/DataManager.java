package com.owen.capstonemod.datamanagement;

import com.mojang.logging.LogUtils;
import org.slf4j.Logger;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import com.owen.capstonemod.events.ConfigEvents;
import com.owen.capstonemod.events.ConfigEvents.EEGPathChangedEvent;
import com.owen.capstonemod.events.ConfigEvents.DataTimeUsedChangedEvent;
/*
This class will be the centralized location for all EEG and HEG data management for the mod.
It is a singleton class, so only one instance will exist.
*/

public class DataManager {
    private static DataManager instance;
    private DataBridge dataBridge;
    private static final Logger LOGGER = LogUtils.getLogger();
    private boolean isEEGConnected = false;
    private double baselineActivity = 0;
    private double rawUserActivity = 0;
    private double relativeUserActivity = 0;

    private DataManager() {
        dataBridge = DataBridge.getInstance();
        dataBridge.start();
    }

    public static DataManager getInstance() {
        if (instance == null) {
            instance = new DataManager();
        }
        return instance;
    }

    // Things to update:
    // - Brain activity data
    // - baseline brain activity
    // - user brain activity
    // - player attributes

    private void startUpdateLoop() {
        while (true) {
            updateAll();
            try {
                Thread.sleep(Config.UPDATE_DELAY_MS.get());
            } catch (InterruptedException e) {
                LOGGER.error("Update loop interrupted", e);
                break;
            }
        }
    }

    private void updateAll() {
        updateData();
        updateBaselineActivity();
        updateUserActivity();
        updatePlayerAttributes();
    }

    private void updateData() {
        // Get the new data from the data bridge
        double[] newData = dataBridge.getNewData();
        // Update the raw user activity
        rawUserActivity = newData[0];
    }

    private void updateBaselineActivity() {
        // Use the average of the last DATA_TIME_USED seconds of data to calculate the baseline brain activity
        baselineActivity = average(dataBridge.getArchivedData());
    }

    private void updateUserActivity() {

    }

    private void updatePlayerAttributes() {

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

    @SubscribeEvent
    public void onEEGPathChanged(EEGPathChangedEvent event) {
        String newPath = event.getNewPath();
        LOGGER.info("EEG data path changed to: " + newPath);
        dataBridge.setEEGDataPath(newPath);
    }

    @SubscribeEvent
    public void onDataTimeUsedChanged(DataTimeUsedChangedEvent event) {
        int newDataTimeUsed = event.getNewDataTimeUsed();
        LOGGER.info("Data time used changed to: " + newDataTimeUsed);
        dataBridge.setArchiveTime(newDataTimeUsed);
    }
}   