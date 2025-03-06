package com.owen.capstonemod.configscreen;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
import net.minecraft.client.gui.GuiGraphics;


public class AttributesListScreen extends Screen {
    // This screen will contain a collection of buttons that will allow the player to select the attribute configure

    private final Screen lastScreen;

    // Constants for the screen layout
    private final int buttonWidth = 200;
    private final int gap = 30;
    private final int initialY = 30; // Y position for first button
    private int currentY = initialY; // Used to track button Y position
    
    public AttributesListScreen(Screen lastScreen) {
        super(Component.translatable("capstonemod.attributeslist.title")); // Screen title
        this.lastScreen = lastScreen;
    }

    @Override
    protected void init() {
        super.init();

        // Speed Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Movement Speed"), 
            button -> this.minecraft.setScreen(new ModifyAttributeScreen(this, "movement_speed")))
            .pos(this.width / 2 - 100, currentY) 
            .width(buttonWidth) 
            .build()
        );

        // Jump Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Jump Strength"), 
            button -> this.minecraft.setScreen(new ModifyAttributeScreen(this, "jump_strength")))
            .pos(this.width / 2 - 100, currentY += gap) 
            .width(buttonWidth) 
            .build()
        );

        // Done Button
        this.addRenderableWidget(Button.builder(
            Component.translatable("gui.done"), 
            button -> this.minecraft.setScreen(this.lastScreen)) 
            .pos(this.width / 2 - 100, this.height - 27) 
            .width(buttonWidth) 
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

