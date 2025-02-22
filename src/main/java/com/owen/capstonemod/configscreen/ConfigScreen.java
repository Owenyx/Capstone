package com.owen.capstonemod.configscreen;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.CycleButton;
import net.minecraft.client.gui.components.AbstractSliderButton;
import net.minecraft.network.chat.Component;
import com.owen.capstonemod.Config;
import net.minecraft.client.gui.GuiGraphics;

public class ConfigScreen extends Screen {
    private final Screen lastScreen; // The screen that was shown before this one (to return to)
    
    public ConfigScreen(Screen lastScreen) {
        super(Component.translatable("capstonemod.configscreen.title")); // Screen title
        this.lastScreen = lastScreen;
    }

    @Override
    protected void init() {
        super.init();
        
        // EEG Toggle Button
        this.addRenderableWidget(CycleButton.onOffBuilder(Config.ENABLE_EEG.get())
            .create(
                this.width / 2 - 100, // x position
                50, // y position
                200, // width
                20, // height
                Component.literal("EEG Control"), // button label
                (button, value) -> Config.ENABLE_EEG.set(value) // what happens when clicked
            ));

        // HEG Toggle Button
        this.addRenderableWidget(CycleButton.onOffBuilder(Config.ENABLE_HEG.get())
            .create(
                this.width / 2 - 100, 
                80, 
                200, 
                20, 
                Component.literal("HEG Control"), 
                (button, value) -> Config.ENABLE_HEG.set(value) 
            ));

        // Update Delay Slider
        this.addRenderableWidget(new AbstractSliderButton(
            this.width / 2 - 100,  // x
            110,                   // y
            200,                   // width
            20,                    // height
            Component.literal("Update Delay: " + Config.UPDATE_DELAY_MS.get()),
            Config.UPDATE_DELAY_MS.get() / 1000.0
        ) {
            @Override
            protected void updateMessage() {
                setMessage(Component.literal("Update Delay: " + (int)(value * 1000)));
            }

            @Override
            protected void applyValue() {
                Config.UPDATE_DELAY_MS.set((int)(value * 1000));
            }
        });
        
        // Data Time Used Slider
        this.addRenderableWidget(new AbstractSliderButton(
            this.width / 2 - 100,  // x
            140,                   // y
            200,                   // width
            20,                    // height
            Component.literal("Data Time Used: " + Config.DATA_TIME_USED.get()),
            Config.DATA_TIME_USED.get() / 300.0
        ) {
            @Override
            protected void updateMessage() {
                setMessage(Component.literal("Data Time Used: " + (int)(value * 300)));
            }

            @Override
            protected void applyValue() {
                Config.DATA_TIME_USED.set((int)(value * 300));
            }
        });

        // Player Attribute Button
        this.addRenderableWidget(Button.builder(
            Component.literal("Player Attribute"), 
            button -> this.minecraft.setScreen(new AttributesListScreen(this))) 
            .pos(this.width / 2 - 100, 170) 
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
