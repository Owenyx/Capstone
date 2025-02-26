package com.owen.capstonemod.player;

import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import java.util.UUID;
import java.util.Map;
import java.util.HashMap;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.registries.ForgeRegistries;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;
import java.util.Optional;
import net.minecraft.core.Holder;
import net.minecraft.world.entity.ai.attributes.Attributes;


public class AttributeManager {
    // Is server-side only
    private static AttributeManager instance;
    private final Map<UUID, Map<ResourceLocation, AttributeModifier>> playerModifiers = new HashMap<>();

    private static final Logger LOGGER = LogUtils.getLogger();

    private AttributeManager() {}
    
    public static AttributeManager getInstance() {
        if (instance == null) {
            instance = new AttributeManager();
        }
        return instance;
    }
    
    public void updatePlayerAttribute(ServerPlayer player, ResourceLocation attribute, double multiplier) {
        LOGGER.info("Updating player attribute");

        // Add player if they don't exist
        addPlayer(player.getUUID());
        
        // Get the player's attribute instance
        UUID playerId = player.getUUID();
        LOGGER.info("Player ID: " + playerId);
        // Need to convert attribute to Holder<Attribute> to get instance
        //AttributeInstance attributeInstance = player.getAttribute(ForgeRegistries.ATTRIBUTES.getHolder(attribute).get());

        // Debug log the attribute we're trying to get
        LOGGER.info("Looking for attribute: {}", attribute);
        
        // Get the attribute from registry
        Attribute registryAttribute = ForgeRegistries.ATTRIBUTES.getValue(attribute);
        LOGGER.info("Registry attribute: {}", registryAttribute);

        // Get the holder from the registry
        Optional<Holder<Attribute>> holder = ForgeRegistries.ATTRIBUTES.getHolder(attribute);
        if (holder.isEmpty()) {
            LOGGER.error("Could not get holder for attribute: {}", attribute);
            return;
        }

        // Get the attribute instance using the holder
        AttributeInstance attributeInstance = player.getAttribute(holder.get());
        if (attributeInstance == null) {
            LOGGER.error("Player does not have attribute: {}", attribute);
            return;
        }

        LOGGER.info("Attribute instance set");



        // Create new modifier
        AttributeModifier newModifier = new AttributeModifier(
            attribute,
            multiplier,
            AttributeModifier.Operation.ADD_MULTIPLIED_BASE
        );
        LOGGER.info("New modifier: " + newModifier);
        

        // Remove old modifier if it exists
        AttributeModifier oldModifier = playerModifiers.get(playerId).get(attribute);
        if (oldModifier != null) {
            attributeInstance.removeModifier(oldModifier);
        }
        LOGGER.info("Removed old modifier");
        

        // Add new modifier
        attributeInstance.addTransientModifier(newModifier);
        LOGGER.info("Added new modifier");
        playerModifiers.get(playerId).put(attribute, newModifier);
    }

    public void addPlayer(UUID playerId) {
        playerModifiers.put(playerId, new HashMap<>());
    }
    
    public void removePlayer(UUID playerId) {
        playerModifiers.remove(playerId);
    }
}