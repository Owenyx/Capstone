package com.owen.capstonemod.datamanagement;

import com.mojang.logging.LogUtils;
import org.slf4j.Logger;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import com.owen.capstonemod.events.ConfigEvents;
import com.owen.capstonemod.events.ConfigEvents.EEGPathChangedEvent;
import org.apache.commons.collections4.queue.CircularFifoQueue;
import net.minecraftforge.fml.loading.FMLEnvironment;
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
        // Ensure this is only called on the client side
        if (!FMLEnvironment.dist.isClient()) {
            throw new IllegalStateException("DataManager should only be accessed on the client side!");
        }
        
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
        updateBaselineActivity();
        updateUserActivity();
        updatePlayerAttributes();
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
        for (String attribute : changingAttributes) {
            double multiplier = relativeUserActivity;

            Config.AttributeConfig config = Config.ATTRIBUTES.get(attribute);
            
            multiplier *= config.scalar.get();
            if (config.invertScalar.get()) {
                multiplier = 1 / multiplier;
            }

            if (multiplier > config.maxMultiplier.get()) {
                multiplier = config.maxMultiplier.get();
            }

            if (multiplier < config.minMultiplier.get()) {
                multiplier = config.minMultiplier.get();
            }

            if (config.invertThreshold.get()) { // If the threshold is inverted
                if (relativeUserActivity <= config.threshold.get()) {
                    multiplier = 0;
                }
            }
            else { // If the threshold is not inverted
                if (relativeUserActivity >= config.threshold.get()) {
                    multiplier = 0;
                }
            }

            multipliers.put(attribute, multiplier);
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
            // Get resource location of attribute
            ResourceLocation attributeLocation = ResourceLocation.tryParse("minecraft:attribute." + attributeName);
            // Send packet to server requesting the change
            network.send(new UpdateAttributeMessage(attributeLocation, multipliers.get(attributeName)), PacketDistributor.SERVER.noArg());
        }
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
}   