package com.owen.brainlink.configscreen.eegdatapath;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Tooltip;

public class ChannelScreen extends Screen {
    // This is for emotions monopolar to branch off into different channels

    private final Screen lastScreen; // The screen that was shown before this one (to return to)
    private final Screen rootScreen; // The root screen that was shown before this one (to return to)
    private final String path;

    // Constants for the screen layout
    private final int buttonWidth = 200;
    private final int gap = 30;
    private final int initialY = 30; // Y position for first button
    private int currentY = initialY; // Used to track button Y position

    public ChannelScreen(Screen lastScreen, Screen rootScreen, String path) {
        super(Component.translatable("brainlink.channelscreen.title")); // Screen title
        this.lastScreen = lastScreen;
        this.rootScreen = rootScreen;
        this.path = path;
    }

    @Override
    protected void init() {
        super.init();
        
        // O1 Button
        this.addRenderableWidget(Button.builder(
            Component.literal("O1"),
            button -> this.minecraft.setScreen(new EmotionsScreen(this, this.rootScreen, this.path + "O1/")))
            .pos(this.width / 2 - 100, currentY)
            .width(buttonWidth)
            .build()
            ).setTooltip(Tooltip.create(Component.translatable("brainlink.o1.tooltip")));

        // O2 Button
        this.addRenderableWidget(Button.builder(
            Component.literal("O2"),
            button -> this.minecraft.setScreen(new EmotionsScreen(this, this.rootScreen, this.path + "O2/")))
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build()
            ).setTooltip(Tooltip.create(Component.translatable("brainlink.o2.tooltip")));

        // T3 Button
        this.addRenderableWidget(Button.builder(
            Component.literal("T3"),
            button -> this.minecraft.setScreen(new EmotionsScreen(this, this.rootScreen, this.path + "T3/")))
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build()
            ).setTooltip(Tooltip.create(Component.translatable("brainlink.t3.tooltip")));

        // T4 Button
        this.addRenderableWidget(Button.builder(
            Component.literal("T4"),
            button -> this.minecraft.setScreen(new EmotionsScreen(this, this.rootScreen, this.path + "T4/")))
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build()
            ).setTooltip(Tooltip.create(Component.translatable("brainlink.t4.tooltip")));

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
