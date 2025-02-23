package com.owen.capstonemod.player;

import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.player.Player;

public class AttributeManager {
    private final AttributeInstance moveSpeed;
    private final AttributeInstance jumpHeight;

    public AttributeManager(Player player) {
        moveSpeed = player.getAttribute(Attributes.MOVEMENT_SPEED);
        jumpHeight = player.getAttribute(Attributes.JUMP_STRENGTH);
    }
}