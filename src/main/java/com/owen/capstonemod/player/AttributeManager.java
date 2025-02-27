package com.owen.capstonemod.player;

import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import java.util.UUID;
import java.util.Map;
import java.util.HashMap;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.resources.ResourceLocation;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;
import net.minecraft.core.Holder;
import net.minecraft.world.entity.ai.attributes.Attributes;
import java.lang.reflect.Field;
import java.lang.invoke.StringConcatFactory;


public class AttributeManager {
    // Is server-side only
    private static AttributeManager instance;
    private final Map<UUID, Map<String, AttributeModifier>> playerModifiers = new HashMap<>();

    private static final Logger LOGGER = LogUtils.getLogger();

    private AttributeManager() {}
    
    public static AttributeManager getInstance() {
        if (instance == null) {
            instance = new AttributeManager();
        }
        return instance;
    }
    
    public void updatePlayerAttribute(ServerPlayer player, String attributeName, double multiplier) {
        LOGGER.info("Updating player attribute");

        // Add player if they don't exist
        addPlayer(player.getUUID());
        
        // Get the player's UUID
        UUID playerId = player.getUUID();
        LOGGER.info("Player ID: " + playerId);

        // debug
        LOGGER.info("Looking for attribute: {}", attributeName);
        
        // Get the attribute field using the name
        Field field = null;
        try {
            field = Attributes.class.getDeclaredField(attributeName);
        } catch (NoSuchFieldException e) {
            LOGGER.error("Attribute not found: {}", attributeName);
            return;
        }


        // Get the attribute holder from the field
        Holder<Attribute> attribute;
        try {
            attribute = (Holder<Attribute>) field.get(null);
        } catch (IllegalAccessException e) {
            LOGGER.error("Failed to access attribute: {}", attributeName);
            return;
        }
        
        AttributeInstance attributeInstance = player.getAttribute(attribute);

        // Get attribute resource loaction from the holder
        ResourceLocation location = attribute.unwrapKey().get().location();

        // Create new modifier
        AttributeModifier newModifier = new AttributeModifier(
            location,
            multiplier,
            AttributeModifier.Operation.ADD_MULTIPLIED_BASE
        );
        LOGGER.info("New modifier: " + newModifier);
        

        // Remove old modifier if it exists
        AttributeModifier oldModifier = playerModifiers.get(playerId).get(attributeName);
        if (oldModifier != null) {
            attributeInstance.removeModifier(oldModifier);
        }
        LOGGER.info("Removed old modifier");
        

        // Add new modifier
        attributeInstance.addTransientModifier(newModifier);
        LOGGER.info("Added new modifier");
        playerModifiers.get(playerId).put(attributeName, newModifier);
    }

    public void addPlayer(UUID playerId) {
        playerModifiers.put(playerId, new HashMap<>());
    }
    
    public void removePlayer(UUID playerId) {
        playerModifiers.remove(playerId);
    }
}