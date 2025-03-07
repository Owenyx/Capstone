package com.owen.capstonemod.configscreen.eegdatapath;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.client.gui.components.Button;
import com.owen.capstonemod.Config;
import net.minecraft.client.gui.components.Tooltip;

public class PathRootScreen extends Screen {
    private final Screen lastScreen;
    private final String reccomendedPath;

    // Constants for the screen layout
    private final int buttonWidth = 200;
    private int gap = 30;
    private final int initialY = 30; // Y position for first button
    private int currentY = initialY; // Used to track button Y position

    public PathRootScreen(Screen lastScreen) {
        super(Component.translatable("capstonemod.pathrootscreen.title")); 
        this.lastScreen = lastScreen;
        this.reccomendedPath = "emotions_bipolar/attention/raw";
    }

    @Override
    protected void init() {
        super.init();

        gap = 30;

        // Path display
        Button pathDisplayButton = Button.builder(
            Component.literal("Current Path: " + Config.getEEGPath()),
            button -> {})
            .pos(this.width / 2 - 150, currentY)
            .width(300)
            .build();
        pathDisplayButton.active = false;
        this.addRenderableWidget(pathDisplayButton);

        // Reccomended Path Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Use Recommended Path"),
            button -> {
                Config.setEEGPath(this.reccomendedPath);
                // Update the path display button
                pathDisplayButton.setMessage(Component.literal("Current Path: " + Config.getEEGPath()));
            })
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build());

        gap = 35;

        // Manual Path display
        Button manualPathButton = Button.builder(
            Component.literal("Or Manually Select Path"),
            button -> {})
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build();
        manualPathButton.active = false;
        this.addRenderableWidget(manualPathButton);

        gap = 25;

        // Signal Branch Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Signal"),
            button -> minecraft.setScreen(new ChannelScreen(this, this, "signal/")))
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build()
            ).setTooltip(Tooltip.create(Component.translatable("capstonemod.signal.tooltip")));

        gap = 20;

        // Emotions Bipolar Branch Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Emotions Bipolar"),
            button -> minecraft.setScreen(new EmotionsScreen(this, this, "emotions_bipolar/")))
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build());

        // Emotions Monopolar Branch Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Emotions Monopolar"),
            button -> minecraft.setScreen(new ChannelScreen(this, this, "emotions_monopolar/")))
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build());

        // Waves Branch Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Waves"),
            button -> minecraft.setScreen(new ChannelScreen(this, this, "waves/")))
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build()
            ).setTooltip(Tooltip.create(Component.translatable("capstonemod.waves.tooltip")));

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