package com.owen.capstonemod.events;

import net.minecraftforge.eventbus.api.Event;

public class ConfigEvents {

    public static class EEGPathChangedEvent extends Event {
        private final String newPath;
        
        public EEGPathChangedEvent(String newPath) {
            this.newPath = newPath;
        }
        
        public String getNewPath() {
            return newPath;
        }
    }

    public static class EnableEEGChangedEvent extends Event {
        private final boolean enabled;

        public EnableEEGChangedEvent(boolean enabled) {
            this.enabled = enabled;
        }

        public boolean getEnabled() {
            return enabled;
        }
    }

    public static class EnableHEGChangedEvent extends Event {
        private final boolean enabled;

        public EnableHEGChangedEvent(boolean enabled) {
            this.enabled = enabled;
        }

        public boolean getEnabled() {
            return enabled;
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