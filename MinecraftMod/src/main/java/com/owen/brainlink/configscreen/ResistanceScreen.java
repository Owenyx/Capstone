package com.owen.brainlink.configscreen;

import net.minecraft.client.gui.screens.Screen;

import com.owen.brainlink.Config;
import com.owen.brainlink.datamanagement.DataBridge;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.client.gui.components.Button;

public class ResistanceScreen extends Screen {
    private final Screen lastScreen;

    // Constants for the screen layout
    private final int buttonWidth = 200;
    private final int gap = 30;
    private final int initialY = 30; // Y position for first button
    private int currentY = initialY; // Used to track button Y position

    private long lastUpdateTime = 0;

    // Resistance variables
    // Above 2,000,000 is determined as good from the company's sample code
    private final int goodThreshold = 2_000_000;

    private Button O1Display;
    private Button O2Display;
    private Button T3Display;
    private Button T4Display;

    private String lastDataPath;

    public ResistanceScreen(Screen lastScreen) {
        super(Component.translatable("brainlink.devicescreen.title")); // Screen title
        this.lastScreen = lastScreen;

        // Save currenlty selected path
        lastDataPath = Config.getEEGPath();

        // Start resistance collection
        Config.setEEGPath("resist");
        DataBridge.getInstance().startEEGCollection();
    }

    @Override
    protected void init() {
        super.init();

        // O1 Display
        O1Display = Button.builder(
            Component.literal("O1"),
            button -> {})
            .pos(this.width / 2 - 100, currentY)
            .width(buttonWidth)
            .build();
        this.addRenderableWidget(O1Display);
        O1Display.active = false;

        // O2 Display
        O2Display = Button.builder(
            Component.literal("O2"),
            button -> {})
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build();
        this.addRenderableWidget(O2Display);
        O2Display.active = false;

        // T3 Display
        T3Display = Button.builder(
            Component.literal("T3"),
            button -> {})
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build();
        this.addRenderableWidget(T3Display);
        T3Display.active = false;

        // T4 Display
        T4Display = Button.builder(
            Component.literal("T4"),
            button -> {})
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build();
        this.addRenderableWidget(T4Display);
        T4Display.active = false;

        // Done Button
        this.addRenderableWidget(Button.builder(
            Component.translatable("gui.done"),
            button -> {
                cleanUp();
                this.minecraft.setScreen(this.lastScreen);
            })
            .pos(this.width / 2 - 100, this.height - 27)
            .width(buttonWidth) 
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

        // If a second has passed, update the resistance values
        long currentTime = System.currentTimeMillis();
        if (currentTime - lastUpdateTime >= 1000) {
            // Get the most recent resistance values
            DataBridge.getInstance().transferData();
            Double[] resistanceValues = DataBridge.getInstance().getArchivedDataSeconds(1).toArray();

            int length = resistanceValues.length;

            // Update the resistance values
            if (length >= 4) {
                O1Display.setMessage(Component.literal("O1: " + (resistanceValues[length - 4] > goodThreshold && resistanceValues[length - 4] < Double.POSITIVE_INFINITY ? "Good" : "Poor")));
                O2Display.setMessage(Component.literal("O2: " + (resistanceValues[length - 3] > goodThreshold && resistanceValues[length - 3] < Double.POSITIVE_INFINITY ? "Good" : "Poor")));
                T3Display.setMessage(Component.literal("T3: " + (resistanceValues[length - 2] > goodThreshold && resistanceValues[length - 2] < Double.POSITIVE_INFINITY ? "Good" : "Poor")));
                T4Display.setMessage(Component.literal("T4: " + (resistanceValues[length - 1] > goodThreshold && resistanceValues[length - 1] < Double.POSITIVE_INFINITY ? "Good" : "Poor")));
            }

            lastUpdateTime = currentTime;
        }

        super.render(guiGraphics, mouseX, mouseY, partialTick);
    }

    @Override
    public void onClose() {
        cleanUp();
        super.onClose();
    }

    private void cleanUp() {
        DataBridge.getInstance().stopEEGCollection();
        Config.setEEGPath(lastDataPath);
    }
}
