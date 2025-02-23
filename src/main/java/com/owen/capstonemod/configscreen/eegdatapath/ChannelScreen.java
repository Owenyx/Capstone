package com.owen.capstonemod.configscreen;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
import net.minecraft.client.gui.GuiGraphics;
import com.owen.capstonemod.Config;

public class ChannelScreen extends Screen {
    private final Screen lastScreen; // The screen that was shown before this one (to return to)
    private final String path;
    
    public ChannelScreen(Screen lastScreen, String path) {
        super(Component.translatable("capstonemod.configscreen.title")); // Screen title
        this.lastScreen = lastScreen;
        this.path = path;
    }

    @Override
    protected void init() {
        super.init();
        
        // O1 Button
        this.addRenderableWidget(Button.builder(
            Component.literal("O1"),
            button -> Config.EEG_PATH.set(this.path + "O1"))
            .pos(this.width / 2 - 100, 30)
            .width(200)
            .build());

        // O2 Button
        this.addRenderableWidget(Button.builder(
            Component.literal("O2"),
            button -> Config.EEG_PATH.set(this.path + "O2"))
            .pos(this.width / 2 - 100, 60)
            .width(200)
            .build());

        // T3 Button
        this.addRenderableWidget(Button.builder(
            Component.literal("T3"),
            button -> Config.EEG_PATH.set(this.path + "T3"))
            .pos(this.width / 2 - 100, 90)
            .width(200)
            .build());

        // T4 Button
        this.addRenderableWidget(Button.builder(
            Component.literal("T4"),
            button -> Config.EEG_PATH.set(this.path + "T4"))
            .pos(this.width / 2 - 100, 120)
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
