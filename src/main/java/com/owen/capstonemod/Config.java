package com.owen.capstonemod;

import net.minecraftforge.common.ForgeConfigSpec;
import java.util.HashMap;
import java.util.Map;

public class Config {
    public static final ForgeConfigSpec.Builder BUILDER = new ForgeConfigSpec.Builder();
    public static final ForgeConfigSpec SPEC;

    // Main toggles
    public static final ForgeConfigSpec.BooleanValue ENABLE_EEG;
    public static final ForgeConfigSpec.BooleanValue ENABLE_HEG;

    // Data configuration
    public static final ForgeConfigSpec.IntValue UPDATE_DELAY_MS;
    public static final ForgeConfigSpec.IntValue DATA_TIME_USED;

    // Player attribute modifiers
    public static final Map<String, AttributeConfig> ATTRIBUTES = new HashMap<>();

    public static class AttributeConfig {
        public final ForgeConfigSpec.BooleanValue isAffected;
        public final ForgeConfigSpec.DoubleValue scalar;
        public final ForgeConfigSpec.BooleanValue invertScalar;
        public final ForgeConfigSpec.DoubleValue maxMultiplier;
        public final ForgeConfigSpec.DoubleValue minMultiplier;
        public final ForgeConfigSpec.DoubleValue threshold;
        public final ForgeConfigSpec.BooleanValue invertThreshold;

        public AttributeConfig(String name, ForgeConfigSpec.Builder builder) {
            builder.push(name + " Settings"); // Creates a subcategory

            isAffected = builder
                    .comment("Enable or disable if the attribute is affected by brain activity.")
                    .define(name + "isAffected", false);

            scalar = builder
                    .comment("Controls how much the attribute is affected by brain activity.")
                    .defineInRange(name + "scalar", 1.0D, 0.0D, 5.0D);

            invertScalar = builder
                    .comment("Invert the scalar so that the attribute scales in the opposite direction of brain activity.")
                    .define(name + "invertScalar", false);

            maxMultiplier = builder
                    .comment("The maximum multiplier for this attribute. If less than Min Multiplier, Min Multiplier will be used instead.")
                    .defineInRange(name + "maxMultiplier", 5.0D, 0.0D, 5.0D);

            minMultiplier = builder
                    .comment("The minimum multiplier for this attribute.")
                    .defineInRange(name + "minMultiplier", 0.0D, 0.0D, 5.0D);

            threshold = builder
                    .comment("If the brain activity is above this threshold, the attribute will be affected. If the brain activity is below this threshold, the attribute will not be affected.")
                    .defineInRange(name + "threshold", 0.0D, 0.0D, 2.0D);

            invertThreshold = builder
                    .comment("Invert the threshold so that the attribute is affected when the brain activity is below the threshold.")
                    .define(name + "invertThreshold", false);

            builder.pop();
        }
    }

    
    // Potion effects are another idea
    
    
    

    static {
        BUILDER.push("Brain Link Configuration"); // Creates a category

        // Main toggles
        ENABLE_EEG = BUILDER
                .comment("Enable or disable all EEG functionality")
                .define("enableEEG", false);

        ENABLE_HEG = BUILDER
                .comment("Enable or disable all HEG functionality")
                .define("enableHEG", false);

        // Data configuration
        UPDATE_DELAY_MS = BUILDER
                .comment("Update delay in milliseconds. This delay is how often the brain activity is checked and the player is modified.")
                .defineInRange("updateDelayMs", 100, 1, 1000);

        DATA_TIME_USED = BUILDER
                .comment("Determines how many seconds of recent data to use for calculating a baseline for the brain activity.")
                .defineInRange("dataTimeUsed", 30, 1, 300);

        // Player attribute modifiers
        ATTRIBUTES.put("speed", new AttributeConfig("speed", BUILDER));
        ATTRIBUTES.put("jump", new AttributeConfig("jump", BUILDER));

        BUILDER.pop();
        SPEC = BUILDER.build();
    }
}