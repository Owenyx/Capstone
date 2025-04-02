package com.owen.capstonemod.configscreen;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
import net.minecraft.client.gui.GuiGraphics;


public class AttributesListScreen extends Screen {
    // This screen will contain a collection of buttons that will allow the player to select the attribute configure

    // The buttons are laid out in pairs side by side for related attributes

    // The attributes that can be modified are:
    // - Movement Speed
    // - Jump Strength (safe_fall_distance is also added with it)
    // - Attack Damage
    // - Armor
    // - Mining Speed
    // - Reach (block_interaction_range, but entity_interaction_range is also added with it)
    // - Lung Capacity
    // - Swim Speed
    // - Size
    // - Step Height
    

    private final Screen lastScreen;

    // Constants for the screen layout
    private final int buttonWidth = 150;
    private final int xGap = 10;
    private final int yGap = 25;
    private final int initialY = 30; // Y position for first button
    private int currentY = initialY; // Used to track button Y position
    
    public AttributesListScreen(Screen lastScreen) {
        super(Component.translatable("capstonemod.attributeslist.title")); // Screen title
        this.lastScreen = lastScreen;
    }

    @Override
    protected void init() {
        super.init();

        int totalWidth = (buttonWidth * 2) + xGap;
        int startX = (this.width - totalWidth) / 2;

        // Change all attributes button
        this.addRenderableWidget(Button.builder(
            Component.literal("Change All Attributes"),
            button -> this.minecraft.setScreen(new ModifyAttributeScreen(this, "all")))
            .pos(this.width / 2 - 100, currentY)
            .width(200)
            .build()
        );

        currentY += yGap;

        // Speed Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Movement Speed"), 
            button -> this.minecraft.setScreen(new ModifyAttributeScreen(this, "movement_speed")))
            .pos(startX, currentY) 
            .width(buttonWidth) 
            .build()
        );

        // Jump height Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Jump Height"), 
            button -> this.minecraft.setScreen(new ModifyAttributeScreen(this, "jump_strength")))
            .pos(startX + buttonWidth + xGap, currentY) 
            .width(buttonWidth) 
            .build()
        );

        currentY += yGap;

        // Attack Damage Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Attack Damage"), 
            button -> this.minecraft.setScreen(new ModifyAttributeScreen(this, "attack_damage")))
            .pos(startX, currentY) 
            .width(buttonWidth) 
            .build()
        );

        // Defense Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Defense"), 
            button -> this.minecraft.setScreen(new ModifyAttributeScreen(this, "armor")))
            .pos(startX + buttonWidth + xGap, currentY) 
            .width(buttonWidth) 
            .build()
        );

        currentY += yGap;

        // Block Break Speed Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Mining Speed"), 
            button -> this.minecraft.setScreen(new ModifyAttributeScreen(this, "block_break_speed")))
            .pos(startX, currentY) 
            .width(buttonWidth) 
            .build()
        );

        // Block Interaction Range Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Reach"), 
            button -> this.minecraft.setScreen(new ModifyAttributeScreen(this, "block_interaction_range")))
            .pos(startX + buttonWidth + xGap, currentY) 
            .width(buttonWidth) 
            .build()
        );

        currentY += yGap;

        // Oxygen Bonus Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Lung Capacity"), 
            button -> this.minecraft.setScreen(new ModifyAttributeScreen(this, "oxygen_bonus")))
            .pos(startX, currentY) 
            .width(buttonWidth) 
            .build()
        );

        // Water Movement Efficiency Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Swim Speed"), 
            button -> this.minecraft.setScreen(new ModifyAttributeScreen(this, "water_movement_efficiency")))
            .pos(startX + buttonWidth + xGap, currentY) 
            .width(buttonWidth) 
            .build()
        );

        currentY += yGap;

        // Scale Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Size"), 
            button -> this.minecraft.setScreen(new ModifyAttributeScreen(this, "scale")))   
            .pos(startX, currentY) 
            .width(buttonWidth) 
            .build()
        );

        // Step Height Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Step Height"), 
            button -> this.minecraft.setScreen(new ModifyAttributeScreen(this, "step_height"))) 
            .pos(startX + buttonWidth + xGap, currentY) 
            .width(buttonWidth) 
            .build()
        );


        // Done Button
        this.addRenderableWidget(Button.builder(
            Component.translatable("gui.done"), 
            button -> this.minecraft.setScreen(this.lastScreen)) 
            .pos(this.width / 2 - 100, this.height - 27) 
            .width(200) 
            .build()
        );

        // Reset currentY to initial value
        currentY = initialY;
    }

    @Override
    public void render(GuiGraphics guiGraphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(guiGraphics, mouseX, mouseY, partialTick);
        
        // Draw the title
        guiGraphics.drawCenteredString(this.font, this.title, this.width / 2, 20, 0xFFFFFF);
        
        super.render(guiGraphics, mouseX, mouseY, partialTick);
    }
}

