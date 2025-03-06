package com.owen.capstonemod.events;

import net.minecraftforge.eventbus.api.Event;

public class ConfigEvents {

    public static class ChosenDeviceChangedEvent extends Event {
        private final String newDevice;

        public ChosenDeviceChangedEvent(String newDevice) {
            this.newDevice = newDevice;
        }

        public String getNewDevice() {
            return newDevice;
        }
    }

    public static class EnableDeviceChangedEvent extends Event {
        private final boolean enabled;

        public EnableDeviceChangedEvent(boolean enabled) {
            this.enabled = enabled;
        }

        public boolean getEnabled() {
            return enabled;
        }
    }


    public static class EEGPathChangedEvent extends Event {
        private final String newPath;
        
        public EEGPathChangedEvent(String newPath) {
            this.newPath = newPath;
        }
        
        public String getNewPath() {
            return newPath;
        }
    }


    public static class IsAffectedChangedEvent extends Event {
        private final String attributeName;
        private final boolean newState;

        public IsAffectedChangedEvent(String attributeName, boolean newState) {
            this.attributeName = attributeName;
            this.newState = newState;
        }

        public String getAttributeName() {
            return attributeName;
        }

        public boolean getNewState() {
            return newState;
        }
    }


    public static class ConstantMovementFOVChangedEvent extends Event {
        private final boolean newState;

        public ConstantMovementFOVChangedEvent(boolean newState) {
            this.newState = newState;
        }

        public boolean getNewState() {
            return newState;
        }
    }
}