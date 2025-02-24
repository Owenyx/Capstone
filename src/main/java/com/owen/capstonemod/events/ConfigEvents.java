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
}