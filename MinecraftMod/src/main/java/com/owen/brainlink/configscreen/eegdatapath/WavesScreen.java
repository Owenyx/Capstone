package com.owen.brainlink.configscreen.eegdatapath;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
import net.minecraft.client.gui.GuiGraphics;

public class WavesScreen extends Screen {
    private final Screen lastScreen; // The screen that was shown before this one (to return to)
    private final Screen rootScreen; // The root screen that was shown before this one (to return to)
    private final String path;

    // Constants for the screen layout
    private final int buttonWidth = 200;
    private final int gap = 30;
    private final int initialY = 30; // Y position for first button
    private int currentY = initialY; // Used to track button Y position

    public WavesScreen(Screen lastScreen, Screen rootScreen, String path) {
        super(Component.translatable("brainlink.wavesscreen.title")); // Screen title
        this.lastScreen = lastScreen;
        this.rootScreen = rootScreen;
        this.path = path;
    }

    @Override
    protected void init() {
        super.init();
        
        // Alpha Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Alpha"),
            button -> this.minecraft.setScreen(new RawPercentScreen(this, this.rootScreen, this.path + "alpha/")))
            .pos(this.width / 2 - 100, currentY)
            .width(buttonWidth)
            .build()
        );

        // Beta Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Beta"),
            button -> this.minecraft.setScreen(new RawPercentScreen(this, this.rootScreen, this.path + "beta/")))
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build()
        );

        // Delta Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Delta"),
            button -> this.minecraft.setScreen(new RawPercentScreen(this, this.rootScreen, this.path + "delta/")))
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build()
        );

        // Theta Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Theta"),
            button -> this.minecraft.setScreen(new RawPercentScreen(this, this.rootScreen, this.path + "theta/")))
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build()
        );

        // Gamma Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Gamma"),
            button -> this.minecraft.setScreen(new RawPercentScreen(this, this.rootScreen, this.path + "gamma/")))
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build()
        );

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
