package com.owen.capstonemod.configscreen.eegdatapath;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
import net.minecraft.client.gui.GuiGraphics;
import com.owen.capstonemod.Config;

public class EmotionsScreen extends Screen {
    private final Screen lastScreen; // The screen that was shown before this one (to return to)
    private final Screen rootScreen; // The root screen that was shown before this one (to return to)
    private final String path;
    
    public EmotionsScreen(Screen lastScreen, Screen rootScreen, String path) {
        super(Component.translatable("capstonemod.configscreen.title")); // Screen title
        this.lastScreen = lastScreen;
        this.rootScreen = rootScreen;
        this.path = path;
    }

    @Override
    protected void init() {
        super.init();
        
        // Attention Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Attention"),
            button -> minecraft.setScreen(new RawPercentScreen(this, this.rootScreen, this.path + "attention/")))
            .pos(this.width / 2 - 100, 30)
            .width(200)
            .build());

        // Relaxation Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Relaxation"),
            button -> minecraft.setScreen(new RawPercentScreen(this, this.rootScreen, this.path + "relaxation/")))
            .pos(this.width / 2 - 100, 55)
            .width(200)
            .build());

        // Alpha Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Alpha Waves"),
            button -> minecraft.setScreen(new RawPercentScreen(this, this.rootScreen, this.path + "alpha/")))
            .pos(this.width / 2 - 100, 80)
            .width(200)
            .build());

        // Beta Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Beta Waves"),
            button -> minecraft.setScreen(new RawPercentScreen(this, this.rootScreen, this.path + "beta/")))
            .pos(this.width / 2 - 100, 105)
            .width(200)
            .build());

        // Delta Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Delta Waves (%)"),
            button -> {
                Config.setEEGPath(this.path + "delta");
                this.minecraft.setScreen(this.rootScreen);
            })
            .pos(this.width / 2 - 100, 130)
            .width(200)
            .build());

        // Theta Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Theta Waves (%)"),
            button -> {
                Config.setEEGPath(this.path + "theta");
                this.minecraft.setScreen(this.rootScreen);
            })
            .pos(this.width / 2 - 100, 155)
            .width(200)
            .build());
        
        // Gamma Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Gamma Waves (%)"),
            button -> {
                Config.setEEGPath(this.path + "gamma");
                this.minecraft.setScreen(this.rootScreen);
            })
            .pos(this.width / 2 - 100, 180)
            .width(200)
            .build());

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
