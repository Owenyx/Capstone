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
import com.owen.capstonemod.datamanagement.DataManager;


public class ConfigScreen extends Screen {
    private final Screen lastScreen; // The screen that was shown before this one (to return to)

    private CycleButton<Boolean> eegToggle;
    private CycleButton<Boolean> hegToggle;
    
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
        eegToggle = CycleButton.onOffBuilder(Config.ENABLE_EEG.get())
            .create(
                this.width / 2 - 100, // x position
                60, // y position
                200, // width
                20, // height
                Component.literal("EEG Control"), // button label
                (button, value) -> handleEEGToggle() // what happens when clicked
            );
        eegToggle.active = ModState.EEG_CONNECTED;
        this.addRenderableWidget(eegToggle);

        // HEG Toggle Button
        hegToggle = CycleButton.onOffBuilder(Config.ENABLE_HEG.get())
            .create(
                this.width / 2 - 100, 
                90, 
                200, 
                20, 
                Component.literal("HEG Control"), 
                (button, value) -> handleHEGToggle() 
            );
        this.addRenderableWidget(hegToggle);

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

    private void handleEEGToggle() {
        // Avoid both being on by turning off the other button
        // Ex: If ENABLE_EEG is off, turn off heg toggle button and set ENABLE_EEG to true
        hegToggle.active = Config.ENABLE_EEG.get();
        // Set the config
        Config.setEnableEEG(!Config.ENABLE_EEG.get());
    }

    private void handleHEGToggle() {
        // Avoid both being on by turning off the other button
        // Ex: If ENABLE_HEG is off, turn off eeg toggle button and set ENABLE_HEG to true, but only if EEG is connected
        eegToggle.active = Config.ENABLE_HEG.get() && DataManager.getInstance().isEEGConnected();
        // Set the config
        Config.setEnableHEG(!Config.ENABLE_HEG.get());
    }

    @Override
    public void render(GuiGraphics guiGraphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(guiGraphics, mouseX, mouseY, partialTick);
        
        // Draw the title
        guiGraphics.drawCenteredString(this.font, this.title, this.width / 2, 20, 0xFFFFFF);
        
        super.render(guiGraphics, mouseX, mouseY, partialTick);
    }
}
