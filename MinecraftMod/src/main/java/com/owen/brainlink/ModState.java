package com.owen.brainlink;

import com.owen.brainlink.events.ConfigEvents;

import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;


@Mod.EventBusSubscriber(modid = BrainLink.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)
public class ModState {

    private static ModState instance;

    // Device Connection States
    private boolean DEVICE_CONNECTED = false; // If chosen device is connected
    public boolean DEVICE_CONNECTING = false;
    public boolean EEG_CONNECTED = false;
    public boolean HEG_CONNECTED = false;

    // Calibration
    // Can either be "none", "bipolar", "O1", "O2", "T3", or "T4"
    // If it is one of the four channels, then the calibration is monopolar
    public String CALIBRATION_TYPE = "none";

    private static final Logger LOGGER = LogUtils.getLogger();

    
    public static ModState getInstance() {
        if (instance == null) {
            instance = new ModState();
        }
        return instance;
    }

    public void setDeviceConnected(boolean newState) {
        // Set the active device connection state
        this.DEVICE_CONNECTED = newState;

        // Save the connection state incase of device switching

        try {
            switch (Config.getChosenDevice()) {
                case "eeg":
                    EEG_CONNECTED = newState;
                    break;
                case "heg":
                    HEG_CONNECTED = newState;
                    break;
            }
        }
        catch (Exception e) {
            LOGGER.error("Error setting device connected", e);
        }
    }

    public boolean getDeviceConnected() {
        return DEVICE_CONNECTED;
    }


    @SubscribeEvent
    public void onChosenDeviceChanged(ConfigEvents.ChosenDeviceChangedEvent event) {
        String newDevice = event.getNewDevice();
        switch (newDevice) {
            case "eeg":   
                // Don't use the setter here
                DEVICE_CONNECTED = EEG_CONNECTED;
                break;
            case "heg":
                DEVICE_CONNECTED = HEG_CONNECTED;
                break;
        }
    }
}

