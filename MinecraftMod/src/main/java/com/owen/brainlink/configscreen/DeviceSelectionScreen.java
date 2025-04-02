package com.owen.brainlink.configscreen;

import net.minecraft.client.gui.screens.Screen;

import com.owen.brainlink.Config;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.client.gui.components.Button;

public class DeviceSelectionScreen extends Screen {
    private final Screen lastScreen;

    // Constants for the screen layout
    private final int buttonWidth = 200;
    private final int gap = 30;
    private final int initialY = 30; // Y position for first button
    private int currentY = initialY; // Used to track button Y position

    public DeviceSelectionScreen(Screen lastScreen) {
        super(Component.translatable("brainlink.deviceselection.title")); // Screen title
        this.lastScreen = lastScreen;
    }

    @Override
    protected void init() {
        super.init();

        // EEG Button
        this.addRenderableWidget(Button.builder(
            Component.translatable("brainlink.devicenames.eeg"),
            button ->  {
                Config.setChosenDevice("eeg");
                this.minecraft.setScreen(this.lastScreen);
            })
            .pos(this.width / 2 - 100, currentY)
            .width(buttonWidth)
            .build());

        // HEG Button
        this.addRenderableWidget(Button.builder(
            Component.translatable("brainlink.devicenames.heg"),
            button ->  {
                Config.setChosenDevice("heg");
                this.minecraft.setScreen(this.lastScreen);
            })
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build()); 

        // Back Button
        this.addRenderableWidget(Button.builder(
            Component.translatable("gui.back"),
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
