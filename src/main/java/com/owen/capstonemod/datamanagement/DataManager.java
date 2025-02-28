package com.owen.capstonemod.datamanagement;

import com.mojang.logging.LogUtils;
import org.slf4j.Logger;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import com.owen.capstonemod.events.ConfigEvents;
import com.owen.capstonemod.events.ConfigEvents.EEGPathChangedEvent;
import org.apache.commons.collections4.queue.CircularFifoQueue;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.Attributes;
import com.owen.capstonemod.network.UpdateAttributeMessage;
import com.owen.capstonemod.Config;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.network.Channel;
import net.minecraftforge.network.ChannelBuilder;
import net.minecraftforge.network.SimpleChannel;
import com.owen.capstonemod.CapstoneMod;
import net.minecraftforge.network.PacketDistributor;
import net.minecraft.client.Minecraft;

/*
This class will be the centralized location for all EEG and HEG data management for the mod.
It is a singleton class, so only one instance will exist.
*/

public class DataManager {
    private static DataManager instance;

    private DataBridge dataBridge;

    private static SimpleChannel network;

    private static final Logger LOGGER = LogUtils.getLogger();

    // State variables
    private boolean isEEGConnected = false;
    private boolean continueUpdating = false;
    private boolean EEGRunning = false;
    private boolean HEGRunning = false;

    // Brain activity data
    private double baselineActivity = 0;
    private double rawUserActivity = 0;
    private double relativeUserActivity = 0;


    private DataManager() {
        dataBridge = DataBridge.getInstance();
        dataBridge.start();

        network = ChannelBuilder.named(ResourceLocation.fromNamespaceAndPath(CapstoneMod.MOD_ID, CapstoneMod.MOD_ID)).networkProtocolVersion(1).optionalClient().clientAcceptedVersions(Channel.VersionTest.exact(1)).simpleChannel();

        network.messageBuilder(UpdateAttributeMessage.class).encoder(UpdateAttributeMessage::encode).decoder(UpdateAttributeMessage::new).consumerMainThread(UpdateAttributeMessage::handle).add();
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

        startDataCollection();

        continueUpdating = true;

        Thread updateThread = new Thread(() -> {
            while (continueUpdating) {
                updateAll();
                try {
                Thread.sleep(Config.UPDATE_DELAY_MS.get());
            } catch (InterruptedException e) {
                    LOGGER.error("Update loop interrupted", e);
                    break;
                }
            }
        });
        updateThread.start();
    }

    private void stopUpdateLoop() {
        continueUpdating = false;
    }

    private void updateAll() {
        updateData();
        updateBaselineActivity();
        updateUserActivity();
        updatePlayerAttributes();
    }

    private void startDataCollection() {
        if (Config.getEnableEEG() && !EEGRunning) {
            dataBridge.startEEGCollection();
            EEGRunning = true;
        }
        if (Config.getEnableHEG() && !HEGRunning) {
            dataBridge.startHEGCollection();
            HEGRunning = true;
        }
    }

    private void stopDataCollection() {
        if (Config.getEnableEEG() && EEGRunning) {
            dataBridge.stopEEGCollection();
            EEGRunning = false;
        }
        if (Config.getEnableHEG() && HEGRunning) {
            dataBridge.stopHEGCollection();
            HEGRunning = false;
        }
    }

    private void updateData() {
        dataBridge.transferData();
    }

    private void updateBaselineActivity() {
        // Use the average of the last DATA_TIME_USED seconds of data to calculate the baseline brain activity
        baselineActivity = dataBridge.getArchivedDataSeconds(Config.DATA_TIME_USED.get()).average();
    }

    private void updateUserActivity() {
        // Update the raw and relative user activity
        CircularFifoQueue<Double> values = dataBridge.getData().getValues();
        // Use most recent value as current raw user activity
        rawUserActivity = values.get(values.size() - 1);
        // Calculate the relative user activity
        relativeUserActivity = rawUserActivity / baselineActivity;
    }

    private void updatePlayerAttributes() {
        // Update the player attributes based on the relative brain activity

        // First check if the player is in the game
        if (Minecraft.getInstance().player == null) {
            return;
        }

        // Create a list of attributes to change
        List<String> changingAttributes = new ArrayList<>();

        // Add all attributes that are affected by brain activity to the list
        for (Map.Entry<String, Config.AttributeConfig> entry : Config.ATTRIBUTES.entrySet()) {
            String key = entry.getKey();
            Config.AttributeConfig value = entry.getValue();
            if (value.isAffected.get()) {
                changingAttributes.add(key);
            }
        }

        // Calculate the multiplier for each attribute
        Map<String, Double> multipliers = new HashMap<>();
        for (String attributeName : changingAttributes) {
            double multiplier = relativeUserActivity;

            // Modifiers are calculated by adding the multiplied base value
            // For example,if base = 1, multiplier = 2, the total will be 1 + 1*2 = 3
            // We subtract 1 from the multiplier so that a multiplier of 2 would double the value instead
            multiplier -= 1;
            // We subtract 1 in some of the following calculations for the same reason

            LOGGER.info("Baseline activity: {}", baselineActivity);
            LOGGER.info("Relative user activity: {}", relativeUserActivity);
            LOGGER.info("Multiplier 1: {}", multiplier);

            Config.AttributeConfig config = Config.ATTRIBUTES.get(attributeName);
            
            multiplier *= config.scalar.get();
            LOGGER.info("Multiplier 2: {}", multiplier);
            if (config.invertScalar.get()) {
                multiplier = 1 / multiplier;
            }
            LOGGER.info("Multiplier 3: {}", multiplier);
            // The condition after && is because we set no limit if it is at its max, and we subtract 0.1 since the config menu rounds to one decimal place
            if (multiplier > config.maxMultiplier.get() - 1 && config.maxMultiplier.get() <= Config.MAX_MAX_MULTIPLIER - 0.1) {
                multiplier = config.maxMultiplier.get();
            }
            LOGGER.info("Multiplier 4: {}", multiplier);
            if (multiplier < config.minMultiplier.get() - 1) {
                multiplier = config.minMultiplier.get();
            }
            LOGGER.info("Multiplier 5: {}", multiplier);    
            if (config.invertThreshold.get()) { // If the threshold is inverted
                if (relativeUserActivity >= config.threshold.get() - 1) {
                    multiplier = 0;
                }
            }
            else { // If the threshold is not inverted
                if (relativeUserActivity <= config.threshold.get() - 1) {
                    multiplier = 0;
                }
            }
            LOGGER.info("Multiplier 6: {}", multiplier);

            multipliers.put(attributeName, multiplier);
        }

        // Create map of actual Attribute objects
        Map<String, Attribute> attributes = new HashMap<>();
        for (String attributeName : changingAttributes) {
            switch (attributeName) {
                case "movement_speed":
                    attributes.put(attributeName, Attributes.MOVEMENT_SPEED.value());
                    break;
                case "jump_strength":
                    attributes.put(attributeName, Attributes.JUMP_STRENGTH.value());
                    break;
                default:
                    break;
            }
        }

        for (String attributeName : changingAttributes) {
            // Send packet to server requesting the change
            // We change the name to uppercase as the attribute manager expects it that way
            network.send(new UpdateAttributeMessage(attributeName.toUpperCase(), multipliers.get(attributeName)), PacketDistributor.SERVER.noArg());
        }
    }

    public boolean connectEEG() {
        isEEGConnected = dataBridge.connectEEG();
        return isEEGConnected;
    }

    public boolean isEEGConnected() {
        return isEEGConnected;
    }

    @SubscribeEvent
    public void onEEGPathChanged(EEGPathChangedEvent event) {
        String newPath = event.getNewPath();
        dataBridge.setEEGDataPath(newPath);
    }

    @SubscribeEvent
    public void onEnableEEGChanged(ConfigEvents.EnableEEGChangedEvent event) {
        boolean newState = event.getEnabled();
        if (newState && isEEGConnected && !continueUpdating) {
            startUpdateLoop();
        }
        else {
            stopUpdateLoop();
        }
    }

    @SubscribeEvent
    public void onEnableHEGChanged(ConfigEvents.EnableHEGChangedEvent event) {
        boolean newState = event.getEnabled();
        if (newState && !continueUpdating) {
            startUpdateLoop();
        }
        else {
            stopUpdateLoop();
        }
    }
}   