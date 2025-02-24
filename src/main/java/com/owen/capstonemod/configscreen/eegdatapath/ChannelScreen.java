package com.owen.capstonemod.configscreen.eegdatapath;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
import net.minecraft.client.gui.GuiGraphics;
import com.owen.capstonemod.Config;
import net.minecraft.client.gui.components.Tooltip;

public class ChannelScreen extends Screen {
    // This is the same as the SignalScreen except it branches off further in a its path,
    // unlike other branches with channels

    private final Screen lastScreen; // The screen that was shown before this one (to return to)
    private final Screen rootScreen; // The root screen that was shown before this one (to return to)
    private final String path;
    private final String next;

    public ChannelScreen(Screen lastScreen, Screen rootScreen, String path) {
        super(Component.translatable("capstonemod.configscreen.title")); // Screen title
        this.lastScreen = lastScreen;
        this.rootScreen = rootScreen;
        
        this.path = path;
        // Changes button function based on the path that led here
        if (path.contains("emotions_monopolar")) {
            next = "emotions";
        } else if (path.contains("waves")) { // Waves path
            next = "waves";
        } else {
            next = "signal"; // Set signal channel in this case, don't branch
        }
    }

    @Override
    protected void init() {
        super.init();
        
        // O1 Button
        this.addRenderableWidget(Button.builder(
            Component.literal("O1"),
            button -> {
                if (next.equals("emotions")) {
                    this.minecraft.setScreen(new EmotionsScreen(this, this.rootScreen, this.path + "O1/"));
                } else if (next.equals("waves")) {
                    this.minecraft.setScreen(new WavesScreen(this, this.rootScreen, this.path + "O1/"));
                } else { // Signal path
                    Config.setEEGPath(this.path + "O1");
                    this.minecraft.setScreen(this.rootScreen);
                }
            })
            .pos(this.width / 2 - 100, 30)
            .width(200)
            .build()
            ).setTooltip(Tooltip.create(Component.translatable("capstonemod.o1.tooltip")));

        // O2 Button
        this.addRenderableWidget(Button.builder(
            Component.literal("O2"),
            button -> {
                if (next.equals("emotions")) {
                    this.minecraft.setScreen(new EmotionsScreen(this, this.rootScreen, this.path + "O2/"));
                } else if (next.equals("waves")) {
                    this.minecraft.setScreen(new WavesScreen(this, this.rootScreen, this.path + "O2/"));
                } else { // Signal path
                    Config.setEEGPath(this.path + "O2");
                    this.minecraft.setScreen(this.rootScreen);
                }
            })
            .pos(this.width / 2 - 100, 60)
            .width(200)
            .build()
            ).setTooltip(Tooltip.create(Component.translatable("capstonemod.o2.tooltip")));

        // T3 Button
        this.addRenderableWidget(Button.builder(
            Component.literal("T3"),
            button -> {
                if (next.equals("emotions")) {
                    this.minecraft.setScreen(new EmotionsScreen(this, this.rootScreen, this.path + "T3/"));
                } else if (next.equals("waves")) {
                    this.minecraft.setScreen(new WavesScreen(this, this.rootScreen, this.path + "T3/"));
                } else { // Signal path
                    Config.setEEGPath(this.path + "T3");
                    this.minecraft.setScreen(this.rootScreen);
                }
            })
            .pos(this.width / 2 - 100, 90)
            .width(200)
            .build()
            ).setTooltip(Tooltip.create(Component.translatable("capstonemod.t3.tooltip")));

        // T4 Button
        this.addRenderableWidget(Button.builder(
            Component.literal("T4"),
            button -> {
                if (next.equals("emotions")) {
                    this.minecraft.setScreen(new EmotionsScreen(this, this.rootScreen, this.path + "T4/"));
                } else if (next.equals("waves")) {
                    this.minecraft.setScreen(new WavesScreen(this, this.rootScreen, this.path + "T4/"));
                } else { // Signal path
                    Config.setEEGPath(this.path + "T4");
                    this.minecraft.setScreen(this.rootScreen);
                }
            })
            .pos(this.width / 2 - 100, 120)
            .width(200)
            .build()
            ).setTooltip(Tooltip.create(Component.translatable("capstonemod.t4.tooltip")));

        // Done Button
        this.addRenderableWidget(Button.builder(
            Component.translatable("gui.back"),
            button -> this.minecraft.setScreen(this.lastScreen))
            .pos(this.width / 2 - 100, this.height - 27)
            .width(200) 
            .build()
        );
    }

    @Override
    public void render(GuiGraphics guiGraphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(guiGraphics, mouseX, mouseY, partialTick);
        
        // Draw the title
        guiGraphics.drawCenteredString(this.font, this.title, this.width / 2, 20, 0xFFFFFF);
        
        super.render(guiGraphics, mouseX, mouseY, partialTick);
    }
}
