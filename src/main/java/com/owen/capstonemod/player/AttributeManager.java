package com.owen.capstonemod.player;

import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.player.Player;
import java.util.UUID;
import java.util.Map;
import java.util.HashMap;
import net.minecraftforge.fml.common.FMLCommonHandler;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;


public class AttributeManager {
    // Is server-side only
    private static AttributeManager instance;
    private final Map<UUID, Map<Attribute, AttributeModifier>> playerModifiers = new HashMap<>();
    
    private AttributeManager() {
        if (FMLCommonHandler.instance().getEffectiveSide().isClient()) {
            throw new IllegalStateException("AttributeManager must be server-side!");
        }
    }
    
    public static AttributeManager getInstance() {
        if (instance == null) {
            instance = new AttributeManager();
        }
        return instance;
    }
    
    public void updatePlayerAttribute(Player player, Attribute attribute, double multiplier) {
        if (player.level().isClientSide()) {
            throw new IllegalStateException("Must be called server-side!");
        }

        // Add player if they don't exist
        addPlayer(player.getUUID());
        
        // Get the player's attribute instance
        UUID playerId = player.getUUID();
        AttributeInstance attributeInstance = player.getAttribute(attribute);
        
        // Remove old modifier if it exists
        AttributeModifier oldModifier = playerModifiers.get(playerId);
        if (oldModifier != null) {
            attributeInstance.removeModifier(oldModifier);
        }
        
        // Create and apply new modifier
        AttributeModifier newModifier = new AttributeModifier(
            UUID.randomUUID(),
            attribute.getDescriptionId() + "_modifier",
            multiplier,
            AttributeModifier.Operation.MULTIPLY_BASE
        );
        
        attributeInstance.addTransientModifier(newModifier);
        playerModifiers.get(playerId).put(attribute, newModifier);
    }

    public void addPlayer(UUID playerId) {
        playerModifiers.put(playerId, new HashMap<>());
    }
    
    public void removePlayer(UUID playerId) {
        playerModifiers.remove(playerId);
    }
}