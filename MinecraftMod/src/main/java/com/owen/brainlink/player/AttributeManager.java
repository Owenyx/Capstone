package com.owen.brainlink.player;

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

        // Add player if they don't exist
        addPlayer(player.getUUID());
        
        // Get the player's UUID
        UUID playerId = player.getUUID();

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

        AttributeModifier.Operation operation = AttributeModifier.Operation.ADD_MULTIPLIED_BASE;

        if (attributeName.equals("ARMOR") || attributeName.equals("OXYGEN_BONUS")
            || attributeName.equals("WATER_MOVEMENT_EFFICIENCY")) {
            // These attributes have 0 as the base value, so we need to add in order to add defense while naked
            operation = AttributeModifier.Operation.ADD_VALUE;
            if (attributeName.equals("ARMOR")) {
                multiplier = 5*multiplier; // 5 seems to be a good base number for armor
            } else if (attributeName.equals("WATER_MOVEMENT_EFFICIENCY")) {
                multiplier = 0.5*multiplier; 
            }
            // Oxygen bonus is *1 so we just keep the multiplier as is for addition
        }

        // Create new modifier
        AttributeModifier newModifier = new AttributeModifier(
            location,
            multiplier,
            operation
        );
        
        // Add new modifier or update existing one
        attributeInstance.addOrUpdateTransientModifier(newModifier);

        // Record it in the map
        playerModifiers.get(playerId).put(attributeName, newModifier);
    }

    public void addPlayer(UUID playerId) {
        playerModifiers.put(playerId, new HashMap<>());
    }
    
    public void removePlayer(UUID playerId) {
        playerModifiers.remove(playerId);
    }
}