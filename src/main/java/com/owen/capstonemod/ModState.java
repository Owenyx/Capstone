package com.owen.capstonemod;

import net.minecraftforge.eventbus.api.SubscribeEvent;
import com.owen.capstonemod.events.ConfigEvents;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = CapstoneMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)
public class ModState {
    // Device Connection States
    public static boolean DEVICE_CONNECTED = false; // If chosen device is connected
    public static boolean EEG_CONNECTED = false;
    public static boolean HEG_CONNECTED = false;

    @SubscribeEvent
    public void onChosenDeviceChanged(ConfigEvents.ChosenDeviceChangedEvent event) {
        String newDevice = event.getNewDevice();
        switch (newDevice) {
            case "EEG":
                DEVICE_CONNECTED = EEG_CONNECTED;
                break;
            case "HEG":
                DEVICE_CONNECTED = HEG_CONNECTED;
                break;
        }
    }
}

