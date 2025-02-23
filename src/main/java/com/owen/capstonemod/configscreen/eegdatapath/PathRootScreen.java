package com.owen.capstonemod.configscreen.eegdatapath;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.client.gui.components.Button;
import com.owen.capstonemod.Config;

public class PathRootScreen extends Screen {
    private final Screen lastScreen;

    public PathRootScreen(Screen lastScreen) {
        super(Component.translatable("capstonemod.configscreen.title")); 
        this.lastScreen = lastScreen;
        this.reccomendedPath = "emotions_bipolar/attention/raw";
    }

    @Override
    protected void init() {
        super.init();

        // Path display
        guiGraphics.drawString(this.font, 
            "Current Path: " + Config.EEG_PATH.get(),
            this.width / 2 - 100,
            40,
            0xFFFFFF);

        // Reccomended Path Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Use Reccomended Path"),
            button -> Config.EEG_PATH.set(this.reccomendedPath))
            .pos(this.width / 2 - 100, 60)
            .width(200)
            .build());

        // Path display
        guiGraphics.drawString(this.font,
            "Select Path Manually",
            this.width / 2 - 100,
            100,
            0xFFFFFF);

        // Signal Branch Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Signal"),
            button -> minecraft.setScreen(new ChannelScreen(this, "signal/")))
            .pos(this.width / 2 - 100, 120)
            .width(200)
            .build());

        // Emotions Bipolar Branch Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Emotions Bipolar"),
            button -> minecraft.setScreen(new EmotionsScreen(this, "emotions_bipolar/")))
            .pos(this.width / 2 - 100, 140)
            .width(200)
            .build());

        // Emotions Monopolar Branch Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Emotions Monopolar"),
            button -> minecraft.setScreen(new ChannelScreen(this, "emotions_monopolar/")))
            .pos(this.width / 2 - 100, 160)
            .width(200)
            .build());

        // Waves Branch Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Waves"),
            button -> minecraft.setScreen(new ChannelScreen(this, "waves/")))
            .pos(this.width / 2 - 100, 180)
            .width(200)
            .build());

        // Done Button
        this.addRenderableWidget(Button.builder(
            Component.translatable("gui.done"),
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