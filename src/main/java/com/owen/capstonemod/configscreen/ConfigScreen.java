package com.owen.capstonemod.configscreen;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.CycleButton;
import net.minecraft.client.gui.components.AbstractSliderButton;
import net.minecraft.network.chat.Component;
import com.owen.capstonemod.Config;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Tooltip;
import com.owen.capstonemod.ModState;

public class ConfigScreen extends Screen {
    private final Screen lastScreen; // The screen that was shown before this one (to return to)
    
    public ConfigScreen(Screen lastScreen) {
        super(Component.translatable("capstonemod.configscreen.title")); // Screen title
        this.lastScreen = lastScreen;
    }

    @Override
    protected void init() {
        super.init();
        
        // EEG Screen Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Manage EEG"),
            button -> this.minecraft.setScreen(new EEGScreen(this)))
            .pos(this.width / 2 - 100, 30)
            .width(200)
            .build());

        // EEG Toggle Button
        CycleButton<Boolean> eegToggle = CycleButton.onOffBuilder(Config.ENABLE_EEG.get())
            .create(
                this.width / 2 - 100, // x position
                60, // y position
                200, // width
                20, // height
                Component.literal("EEG Control"), // button label
                (button, value) -> Config.ENABLE_EEG.set(value) // what happens when clicked
            );
        eegToggle.active = ModState.EEG_CONNECTED;
        this.addRenderableWidget(eegToggle);

        // HEG Toggle Button
        this.addRenderableWidget(CycleButton.onOffBuilder(Config.ENABLE_HEG.get())
            .create(
                this.width / 2 - 100, 
                90, 
                200, 
                20, 
                Component.literal("HEG Control"), 
                (button, value) -> Config.ENABLE_HEG.set(value) 
            ));

        // Update Delay Slider
        this.addRenderableWidget(new AbstractSliderButton(
            this.width / 2 - 100,  // x
            120,                   // y
            200,                   // width
            20,                    // height
            Component.literal("Update Delay (ms): " + Config.UPDATE_DELAY_MS.get()),
            (Config.UPDATE_DELAY_MS.get() - 1.0) / 999.0  // Normalize from 1-1000 to 0-1
        ) {
            @Override
            protected void updateMessage() {
                setMessage(Component.literal("Update Delay (ms): " + (int)(value * 999 + 1)));
            }

            @Override
            protected void applyValue() {
                Config.UPDATE_DELAY_MS.set((int)(value * 999 + 1));
            }
        }).setTooltip(Tooltip.create(Component.translatable("capstonemod.updatedelay.tooltip")));
        
        // Data Time Used Slider
        this.addRenderableWidget(new AbstractSliderButton(
            this.width / 2 - 100,  // x
            150,                   // y
            200,                   // width
            20,                    // height
            Component.literal("Data Time Used (s): " + Config.DATA_TIME_USED.get()),
            (Config.DATA_TIME_USED.get() - 1.0) / 299.0  // Normalize from 1-300 to 0-1
        ) {
            @Override
            protected void updateMessage() {
                setMessage(Component.literal("Data Time Used (s): " + (int)(value * 299 + 1)));
            }

            @Override
            protected void applyValue() {
                Config.DATA_TIME_USED.set((int)(value * 299 + 1));
            }
        }).setTooltip(Tooltip.create(Component.translatable("capstonemod.datatimeused.tooltip")));

        // Player Attribute Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Modify Player Attributes"), 
            button -> this.minecraft.setScreen(new AttributesListScreen(this))) 
            .pos(this.width / 2 - 100, 180) 
            .width(200) 
            .build()
        );

        // Add "Done" button at bottom
        this.addRenderableWidget(Button.builder(
            Component.translatable("gui.done"), // Button text
            button -> this.minecraft.setScreen(this.lastScreen)) // Return to previous screen
            .pos(this.width / 2 - 100, this.height - 27) // Position
            .width(200) // Button width
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
