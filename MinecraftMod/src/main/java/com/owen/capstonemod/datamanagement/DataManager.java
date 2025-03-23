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
import java.util.function.Supplier;
import net.minecraftforge.fml.common.Mod;
import com.owen.capstonemod.ModState;

/*
This class will be the centralized location for all EEG and HEG data management for the mod.
It is a singleton class, so only one instance will exist.
*/

@Mod.EventBusSubscriber(modid = CapstoneMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)
public class DataManager {
    private static DataManager instance;

    private DataBridge dataBridge;

    private static SimpleChannel network;

    private List<String> changingAttributes = new ArrayList<>();

    private static final Logger LOGGER = LogUtils.getLogger();

    // State variables
    private boolean deviceRunning = false;

    // Device functions
    private Runnable startDataCollection;
    private Runnable stopDataCollection;
    private Supplier<Boolean> connectDevice;

    // Brain activity data
    private double baselineActivity = 0;
    private double rawUserActivity = 0;
    private double relativeUserActivity = 0;


    private DataManager() {
        // Initialize the data bridge and start the gateway to Python
        dataBridge = DataBridge.getInstance();
        dataBridge.start();

        // Initialize the network
        network = ChannelBuilder.named(ResourceLocation.fromNamespaceAndPath(CapstoneMod.MOD_ID, CapstoneMod.MOD_ID)).networkProtocolVersion(1).optionalClient().clientAcceptedVersions(Channel.VersionTest.exact(1)).simpleChannel();

        // Register the update attribute message to the network
        network.messageBuilder(UpdateAttributeMessage.class).encoder(UpdateAttributeMessage::encode).decoder(UpdateAttributeMessage::new).consumerMainThread(UpdateAttributeMessage::handle).add();
    }

    public static DataManager getInstance() {
        
        if (instance == null) {
            instance = new DataManager();
            // Load any config needed
            instance.loadAttributes();
            instance.loadDevice();
        }
        return instance;
    }

    // Things to update:
    // - Brain activity data
    // - baseline brain activity
    // - user brain activity
    // - player attributes

    private void startUpdateLoop() {

        startDataCollection.run();

        deviceRunning = true;

        handleFOV();

        Thread updateThread = new Thread(() -> {
            while (deviceRunning) {
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
        deviceRunning = false;
        handleFOV();
        stopDataCollection.run();
        removeModifiers();
    }

    private void updateAll() {
        updateData();
        LOGGER.info("Updated data");
        updateBaselineActivity();
        LOGGER.info("Updated baseline activity");
        updateUserActivity();
        LOGGER.info("Updated user activity");
        updatePlayerAttributes();
        LOGGER.info("Updated player attributes");
        
        // Update the FOV scaling
        boolean isAffected = changingAttributes.contains("movement_speed");
        boolean FOVconstant = Config.getConstantMovementFOV();
        // If we are not keeping FOV constant, refresh the original FOV scaling incase the user changed the vanilla FOV scaling video setting
        if (!isAffected || !FOVconstant || !deviceRunning) {
            Config.FOV_SCALING.set(Minecraft.getInstance().options.fovEffectScale().get());
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
        // If baseline activity is 0, set relative user activity to 1, setting attributes to normal values
        // Baseline activity is 0 if no data is collected yet
        if (baselineActivity == 0) {
            relativeUserActivity = 1;
            return;
        }

        // Update the raw and relative user activity
        CircularFifoQueue<Double> values = dataBridge.getData().getValues();

        // Use most recent value as current raw user activity
        rawUserActivity = values.get(values.size() > 0 ? values.size() - 1 : 0);

        // Calculate the relative user activity
        relativeUserActivity = rawUserActivity / baselineActivity;
    }

    private void updatePlayerAttributes() {
        // Update the player attributes based on the relative brain activity

        // First check if the player is in the game
        if (Minecraft.getInstance().player == null) {
            return;
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

            LOGGER.info("--------------------------------");
            LOGGER.info("Relative user activity: {}", relativeUserActivity);

            Config.AttributeConfig config = Config.ATTRIBUTES.get(attributeName);
            
            multiplier *= config.scalar.get();

            if (config.invertScalar.get()) {
                multiplier = 1 / multiplier;
            }

            // The condition after && is because we set no limit if it is at its max, and we subtract 0.005 since 
            // the config menu slider rounds to two decimal places, and will therefore round up within 0.005 of the value
            if (multiplier > config.maxMultiplier.get() - 1 && config.maxMultiplier.get() <= Config.MAX_MAX_MULTIPLIER - 0.005) {
                multiplier = config.maxMultiplier.get() - 1;
            }

            if (multiplier < config.minMultiplier.get() - 1) {
                multiplier = config.minMultiplier.get() - 1;
            }
  
            if (config.invertThreshold.get()) { // If the threshold is inverted
                if (relativeUserActivity >= config.threshold.get()) {
                    multiplier = 0;
                }
            }
            else { // If the threshold is not inverted
                if (relativeUserActivity <= config.threshold.get()) {
                    multiplier = 0;
                }
            }
            LOGGER.info("Multiplier: {}", multiplier);

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

    public boolean connectDevice() {
        return connectDevice.get();
    }
    
    public void loadAttributes() {
        // This function is needed to ensure that the changingAttributes list is up to date when starting the game, as it always starts empty
        for (String attributeName : Config.ATTRIBUTES.keySet()) {
            Config.AttributeConfig config = Config.ATTRIBUTES.get(attributeName);
            if (config.getIsAffected()) {
                changingAttributes.add(attributeName);
            }
        }
    }

    public void loadDevice() {
        // Set the functions to use the correct device
        switch (Config.getChosenDevice()) {
            case "eeg":
                startDataCollection = dataBridge::startEEGCollection;
                stopDataCollection = dataBridge::stopEEGCollection;
                connectDevice = () -> dataBridge.connectEEG();
                break;
            case "heg":
                startDataCollection = dataBridge::startHEGCollection;
                stopDataCollection = dataBridge::stopHEGCollection;
                connectDevice = () -> dataBridge.connectHEG();
                break;
            default:
                break;
        }

        // Also refresh the EEG path for any related events to take effect
        Config.setEEGPath(Config.getEEGPath());
    }

    private void handleFOV() {
        // This removes FOV scaling if the following conditions are met:
        // - Movement speed is being affected by the headband
        // - Constant movement FOV is enabled
        // - The device is running
        // And sets the FOV scaling to the original value otherwise
        boolean isAffected = changingAttributes.contains("movement_speed");
        boolean FOVconstant = Config.getConstantMovementFOV();
        if (isAffected && FOVconstant && deviceRunning) {
            // Save the original FOV scaling value
            Config.FOV_SCALING.set(Minecraft.getInstance().options.fovEffectScale().get());
            // Set the FOV scaling to 0
            Minecraft.getInstance().options.fovEffectScale().set(0.0);
        }
        else {
            Minecraft.getInstance().options.fovEffectScale().set(Config.FOV_SCALING.get());
        }
    }

    private void removeModifiers() {
        // If the player isn't in the game, don't do anything
        if (Minecraft.getInstance().player == null) {
            return;
        }

        for (String attributeName : changingAttributes) {
            network.send(new UpdateAttributeMessage(attributeName.toUpperCase(), 0.0), PacketDistributor.SERVER.noArg());
        }
    }

    public double getRelativeUserActivity() {
        return relativeUserActivity;
    }

    @SubscribeEvent
    public void onChosenDeviceChanged(ConfigEvents.ChosenDeviceChangedEvent event) {
        String newDevice = event.getNewDevice();

        // Set the functions to use the correct device
        switch (newDevice) {
            case "eeg":
                startDataCollection = dataBridge::startEEGCollection;
                stopDataCollection = dataBridge::stopEEGCollection;
                connectDevice = () -> dataBridge.connectEEG();
                break;
            case "heg":
                startDataCollection = dataBridge::startHEGCollection;
                stopDataCollection = dataBridge::stopHEGCollection;
                connectDevice = () -> dataBridge.connectHEG();
                break;
            default:
                break;
        }

        dataBridge.clearData();
    }

    @SubscribeEvent
    public void onEnableDeviceChanged(ConfigEvents.EnableDeviceChangedEvent event) {
        LOGGER.info("onEnableDeviceChanged event received");
        boolean newState = event.getEnabled();
        if (newState && !deviceRunning && ModState.getInstance().getDeviceConnected()) {
            LOGGER.info("Starting update loop");
            startUpdateLoop();
        }
        else {
            LOGGER.info("Stopping update loop");
            stopUpdateLoop();
        }
    }

    @SubscribeEvent
    public void onEEGPathChanged(EEGPathChangedEvent event) {
        LOGGER.info("onEEGPathChanged event received");
        String newPath = event.getNewPath();
        dataBridge.setEEGDataPath(newPath);

        // Since we are working with a new type of data, clear any current data
        dataBridge.clearData();

        // If using emotions, set the calibration type
        String dataType = newPath.split("/")[0];
        if (dataType.equals("emotions_bipolar")) {
            ModState.getInstance().CALIBRATION_TYPE = "bipolar";
        }
        else if (dataType.equals("emotions_monopolar")) {
            // If monopolar, the part after / is the channel, we use that as the calibration type
            ModState.getInstance().CALIBRATION_TYPE = newPath.split("/")[1];
        }
        else {
            ModState.getInstance().CALIBRATION_TYPE = "none";
        }
    }

    @SubscribeEvent
    public void onIsAffectedChanged(ConfigEvents.IsAffectedChangedEvent event) {
        LOGGER.info("onIsAffectedChanged event received");
        String attributeName = event.getAttributeName();
        if (event.getNewState()) {
            // If the attribute is now being affected, add it to the list
            changingAttributes.add(attributeName);
        }
        else {
            changingAttributes.remove(attributeName);
            // Send packet to server to remove the current modifier
            network.send(new UpdateAttributeMessage(attributeName.toUpperCase(), 0.0), PacketDistributor.SERVER.noArg());
        }

        handleFOV();
    }

    @SubscribeEvent
    public void onConstantMovementFOVChanged(ConfigEvents.ConstantMovementFOVChangedEvent event) {
        handleFOV();
    }
}   

