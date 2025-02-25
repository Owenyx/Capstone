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

public class AttributeManager {
    // Is server-side only
    private static AttributeManager instance;
    private final Map<UUID, Map<ResourceLocation, AttributeModifier>> playerModifiers = new HashMap<>();
    
    private AttributeManager() {}
    
    public static AttributeManager getInstance() {
        if (instance == null) {
            instance = new AttributeManager();
        }
        return instance;
    }
    
    public void updatePlayerAttribute(ServerPlayer player, ResourceLocation attribute, double multiplier) {

        // Add player if they don't exist
        addPlayer(player.getUUID());
        
        // Get the player's attribute instance
        UUID playerId = player.getUUID();
        // Need to convert attribute to Holder<Attribute> to get instance
        AttributeInstance attributeInstance = player.getAttribute(ForgeRegistries.ATTRIBUTES.getHolder(attribute).get());
        
        // Remove old modifier if it exists
        AttributeModifier oldModifier = playerModifiers.get(playerId).get(attribute);
        if (oldModifier != null) {
            attributeInstance.removeModifier(oldModifier);
        }
        
        // Create and apply new modifier
        AttributeModifier newModifier = new AttributeModifier(
            attribute,
            multiplier,
            AttributeModifier.Operation.ADD_MULTIPLIED_BASE
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