package com.owen.capstonemod.configscreen.eegdatapath;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
import net.minecraft.client.gui.GuiGraphics;

public class WavesScreen extends Screen {
    private final Screen lastScreen; // The screen that was shown before this one (to return to)
    private final Screen rootScreen; // The root screen that was shown before this one (to return to)
    private final String path;

    public WavesScreen(Screen lastScreen, Screen rootScreen, String path) {
        super(Component.translatable("capstonemod.configscreen.title")); // Screen title
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
            .pos(this.width / 2 - 100, 30)
            .width(200)
            .build()
        );

        // Beta Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Beta"),
            button -> this.minecraft.setScreen(new RawPercentScreen(this, this.rootScreen, this.path + "beta/")))
            .pos(this.width / 2 - 100, 60)
            .width(200)
            .build()
        );

        // Delta Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Delta"),
            button -> this.minecraft.setScreen(new RawPercentScreen(this, this.rootScreen, this.path + "delta/")))
            .pos(this.width / 2 - 100, 90)
            .width(200)
            .build()
        );

        // Theta Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Theta"),
            button -> this.minecraft.setScreen(new RawPercentScreen(this, this.rootScreen, this.path + "theta/")))
            .pos(this.width / 2 - 100, 120)
            .width(200)
            .build()
        );

        // Gamma Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Gamma"),
            button -> this.minecraft.setScreen(new RawPercentScreen(this, this.rootScreen, this.path + "gamma/")))
            .pos(this.width / 2 - 100, 150)
            .width(200)
            .build()
        );

        // Back Button
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
