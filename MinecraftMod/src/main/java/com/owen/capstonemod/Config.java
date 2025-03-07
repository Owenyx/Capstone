package com.owen.capstonemod;

import net.minecraftforge.common.ForgeConfigSpec;
import java.util.HashMap;
import java.util.Map;
import net.minecraftforge.common.MinecraftForge;
import com.owen.capstonemod.events.ConfigEvents;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class Config {
    public static final ForgeConfigSpec.Builder BUILDER = new ForgeConfigSpec.Builder();
    public static final ForgeConfigSpec SPEC;

    public static final Logger LOGGER = LogManager.getLogger();

    // Main configs
    private static final ForgeConfigSpec.ConfigValue<String> CHOSEN_DEVICE; // "eeg" or "heg" or "none"
    private static final ForgeConfigSpec.BooleanValue ENABLE_DEVICE;

    // Data configuration
    private static final ForgeConfigSpec.ConfigValue<String> EEG_PATH;
    public static final ForgeConfigSpec.IntValue UPDATE_DELAY_MS;
    public static final ForgeConfigSpec.IntValue DATA_TIME_USED;

    // Player attribute modifiers
    public static final Map<String, AttributeConfig> ATTRIBUTES = new HashMap<>();
    private static final ForgeConfigSpec.BooleanValue CONSTANT_MOVEMENT_FOV;

    // Max, min, and default values for the configs, not changable by players
    public static final int DEFAULT_UPDATE_DELAY_MS = 100;
    public static final int MAX_UPDATE_DELAY_MS = 1000;
    public static final int MIN_UPDATE_DELAY_MS = 50; // 50ms should be the lowest as thats how often the game updates

    public static final int DEFAULT_DATA_TIME_USED = 30;
    public static final int MAX_DATA_TIME_USED = 300;
    public static final int MIN_DATA_TIME_USED = 1;

    public static final double DEFAULT_SCALAR = 1.0D;
    public static final double MAX_SCALAR = 5.0D;
    public static final double MIN_SCALAR = 0.0D;

    public static final double DEFAULT_MAX_MULTIPLIER = 5.0D;
    public static final double MAX_MAX_MULTIPLIER = 5.0D;
    public static final double MIN_MAX_MULTIPLIER = 0.0D;

    public static final double DEFAULT_MIN_MULTIPLIER = 0.0D;
    public static final double MAX_MIN_MULTIPLIER = 5.0D;
    public static final double MIN_MIN_MULTIPLIER = 0.0D;

    public static final double DEFAULT_THRESHOLD = 0.0D;
    public static final double MAX_THRESHOLD = 2.0D;
    public static final double MIN_THRESHOLD = 0.0D;

    public static class AttributeConfig {
        public final String name;
        private final ForgeConfigSpec.BooleanValue isAffected;
        public final ForgeConfigSpec.DoubleValue scalar;
        public final ForgeConfigSpec.BooleanValue invertScalar;
        public final ForgeConfigSpec.DoubleValue maxMultiplier;
        public final ForgeConfigSpec.DoubleValue minMultiplier;
        public final ForgeConfigSpec.DoubleValue threshold;
        public final ForgeConfigSpec.BooleanValue invertThreshold;

        public AttributeConfig(String name, ForgeConfigSpec.Builder builder) {
            this.name = name;
            builder.push(name + " Settings"); // Creates a subcategory

            isAffected = builder
                    .comment("Enable or disable if the attribute is affected by brain activity.")
                    .define(name + "isAffected", false);

            scalar = builder
                    .comment("Controls how much the attribute is affected by brain activity.")
                    .defineInRange(name + "scalar", DEFAULT_SCALAR, MIN_SCALAR, MAX_SCALAR);

            invertScalar = builder
                    .comment("Invert the scalar so that the attribute scales in the opposite direction of brain activity.")
                    .define(name + "invertScalar", false);

            maxMultiplier = builder
                    .comment("The maximum multiplier for this attribute. If less than Min Multiplier, Min Multiplier will be used instead.")
                    .defineInRange(name + "maxMultiplier", DEFAULT_MAX_MULTIPLIER, MIN_MAX_MULTIPLIER, MAX_MAX_MULTIPLIER);

            minMultiplier = builder
                    .comment("The minimum multiplier for this attribute.")
                    .defineInRange(name + "minMultiplier", DEFAULT_MIN_MULTIPLIER, MIN_MIN_MULTIPLIER, MAX_MIN_MULTIPLIER);

            threshold = builder
                    .comment("If the brain activity is above this threshold, the attribute will be affected. If the brain activity is below this threshold, the attribute will not be affected.")
                    .defineInRange(name + "threshold", DEFAULT_THRESHOLD, MIN_THRESHOLD, MAX_THRESHOLD);

            invertThreshold = builder
                    .comment("Invert the threshold so that the attribute is affected when the brain activity is below the threshold.")
                    .define(name + "invertThreshold", false);

            builder.pop();
        }

        public boolean getIsAffected() {
            return isAffected.get();
        }
        public void setIsAffected(boolean newState) {
            isAffected.set(newState);
            MinecraftForge.EVENT_BUS.post(new ConfigEvents.IsAffectedChangedEvent(name, newState));
        }
    }

    
    // Potion effects are another idea
    

    static {
        BUILDER.push("Brain Link Configuration"); // Creates a category

        CHOSEN_DEVICE = BUILDER
                .comment("The device that is currently selected.")
                .define("chosenDevice", "none");

        // Main toggles
        ENABLE_DEVICE = BUILDER
                .comment("Enable or disable the currently selected device.")
                .define("enableDevice", false);

        // Data configuration
        EEG_PATH = BUILDER
                .comment("The path to the EEG storage holding the desired data.")
                .define("eegPath", "emotions_bipolar/attention/raw");

        UPDATE_DELAY_MS = BUILDER
                .comment("Update delay in milliseconds. This delay is how often the brain activity is checked and the player is modified.")
                .defineInRange("updateDelayMs", DEFAULT_UPDATE_DELAY_MS, MIN_UPDATE_DELAY_MS, MAX_UPDATE_DELAY_MS);

        DATA_TIME_USED = BUILDER
                .comment("Determines how many seconds of recent data to use for calculating a baseline for the brain activity.")
                .defineInRange("dataTimeUsed", DEFAULT_DATA_TIME_USED, MIN_DATA_TIME_USED, MAX_DATA_TIME_USED);

        CONSTANT_MOVEMENT_FOV = BUILDER
                .comment("If true, player FOV will be constant while under the effect of mod-related speed changes.")
                .define("constantMovementFOV", true);

        // Player attribute modifiers
        ATTRIBUTES.put("movement_speed", new AttributeConfig("movement_speed", BUILDER));
        ATTRIBUTES.put("jump_strength", new AttributeConfig("jump_strength", BUILDER));

        BUILDER.pop();
        SPEC = BUILDER.build();
    }

    // Add setters and getters for any config attribute that needs an event fired when it is changed

    // CHOSEN_DEVICE
    public static String getChosenDevice() {
        return CHOSEN_DEVICE.get();
    }
    public static void setChosenDevice(String newDevice) {
        CHOSEN_DEVICE.set(newDevice);
        MinecraftForge.EVENT_BUS.post(new ConfigEvents.ChosenDeviceChangedEvent(newDevice));
    }

    // ENABLE_DEVICE
    public static boolean getEnableDevice() {
        return ENABLE_DEVICE.get();
    }
    public static void setEnableDevice(boolean newState) {
        ENABLE_DEVICE.set(newState);
        LOGGER.info("Setting enable device to " + newState);
        MinecraftForge.EVENT_BUS.post(new ConfigEvents.EnableDeviceChangedEvent(newState));
    }

    // EEG_PATH
    public static String getEEGPath() {
        return EEG_PATH.get();
    }
    public static void setEEGPath(String newPath) {
        EEG_PATH.set(newPath);
        MinecraftForge.EVENT_BUS.post(new ConfigEvents.EEGPathChangedEvent(newPath));
    }

    // CONSTANT_MOVEMENT_FOV
    public static boolean getConstantMovementFOV() {
        return CONSTANT_MOVEMENT_FOV.get();
    }
    public static void setConstantMovementFOV(boolean newState) {
        CONSTANT_MOVEMENT_FOV.set(newState);
        MinecraftForge.EVENT_BUS.post(new ConfigEvents.ConstantMovementFOVChangedEvent(newState));
    }
}