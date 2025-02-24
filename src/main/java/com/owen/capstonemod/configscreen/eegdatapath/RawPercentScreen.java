package com.owen.capstonemod.configscreen.eegdatapath;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
import net.minecraft.client.gui.GuiGraphics;
import com.owen.capstonemod.Config;

public class RawPercentScreen extends Screen {
    private final Screen lastScreen; // The screen that was shown before this one (to return to)
    private final Screen rootScreen; // The root screen that was shown before this one (to return to)
    private final String path;

    public RawPercentScreen(Screen lastScreen, Screen rootScreen, String path) {
        super(Component.translatable("capstonemod.configscreen.title")); // Screen title
        this.lastScreen = lastScreen;
        this.rootScreen = rootScreen;
        this.path = path;
    }

    @Override
    protected void init() {
        super.init();

        // Raw Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Raw"),
            button -> {
                Config.setEEGPath(this.path + "raw");
                this.minecraft.setScreen(this.rootScreen);
            })
            .pos(this.width / 2 - 100, 80)
            .width(200)
            .build());

        // Percent Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Percent"),
            button -> {
                Config.setEEGPath(this.path + "percent");
                this.minecraft.setScreen(this.rootScreen);
            })
            .pos(this.width / 2 - 100, 110)
            .width(200)
            .build());
        
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
