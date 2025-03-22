package com.owen.capstonemod.configscreen;

import com.owen.capstonemod.datamanagement.DataBridge;
import com.owen.capstonemod.datamanagement.DataManager;
import com.owen.capstonemod.ModState;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
import com.owen.capstonemod.Config; 

public class InfoScreen extends Screen {

    // Constants for the screen layout
    private final int buttonWidth = 200;
    private final int buttonHeight = 20;
    private final int gap = 30;
    private final int initialY = 30; // Y position for first button
    private int currentY = initialY; // Used to track button Y position

    private final Screen lastScreen;

    Button relativeUserActivity;

    Button calibrationBar;
    boolean showingCalibrationBar = false;
    int calX;
    int calY;

    public InfoScreen(Screen lastScreen) {
        super(Component.literal("BrainLink Info"));
        this.lastScreen = lastScreen;

        // Show calibration bar if the type is not none, and device is on, and bipolar is not calibrated
        if (!ModState.getInstance().CALIBRATION_TYPE.equals("none") && Config.getEnableDevice() && !DataBridge.getInstance().isBipolarCalibrated()) {
            showingCalibrationBar = true;
        }
    }

    @Override
    protected void init() {
        super.init();

        // Relative user activity Text Display
        relativeUserActivity = Button.builder(
            Component.literal(String.format("Relative User Activity: %.2f", DataManager.getInstance().getRelativeUserActivity())),
            button -> {})
            .pos(this.width / 2 - 100, currentY)
            .width(buttonWidth)
            .build();
        this.addRenderableWidget(relativeUserActivity);
        relativeUserActivity.active = false;

        // Calibration bar
        if (showingCalibrationBar) {

            calX = this.width / 2 - 100;
            calY = currentY += gap;

            calibrationBar = Button.builder(
                Component.literal("Calibration Progress"),
                button -> {})
                .pos(calX, calY)
                .width(buttonWidth)
                .build();
            this.addRenderableWidget(calibrationBar);

        }


        // Add "Done" button at bottom
        this.addRenderableWidget(Button.builder(
            Component.translatable("gui.done"), // Button text
            button -> this.minecraft.setScreen(this.lastScreen)) // Return to previous screen
            .pos(this.width / 2 - 100, this.height - 27) // Position
            .width(buttonWidth) // Button width
            .build()
        );

        // Reset currentY to initial value
        currentY = initialY;
    }
    
    @Override
    public void render(GuiGraphics guiGraphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(guiGraphics, mouseX, mouseY, partialTick);

        // Relative user activity rendering

        relativeUserActivity.setMessage(Component.literal(String.format("Relative User Activity: %.2f", DataManager.getInstance().getRelativeUserActivity())));

        // Calibration bar rendering

        // Only render if we are supposed to
        if (showingCalibrationBar) {

            // Stop showing calibration bar if calibrated
            if (DataBridge.getInstance().isBipolarCalibrated()) {
                showingCalibrationBar = false;
                calibrationBar.setMessage(Component.literal("Calibration Complete"));
            }

            int calibrationProgress = 0;
            
            // Determine which calibration progress to use
            if (ModState.getInstance().CALIBRATION_TYPE == "bipolar") {
                calibrationProgress = DataBridge.getInstance().getBipolarCalibrationProgress();
            }
            else { // Must be monopolar, and so CALIBRATION_TYPE is the channel
                calibrationProgress = DataBridge.getInstance().getMonopolarCalibrationProgress(ModState.getInstance().CALIBRATION_TYPE);
            }

            // Draw the calibration progress over the bar, coloured green
            int progressWidth = (int) (buttonWidth * (calibrationProgress / 100.0));
            guiGraphics.fill(calX + 1, calY + 1, calX + progressWidth, calY + buttonHeight - 1, 0x8800ff00);
        }

        // Draw the title
        guiGraphics.drawCenteredString(this.font, this.title, this.width / 2, 20, 0xFFFFFF);

        super.render(guiGraphics, mouseX, mouseY, partialTick);
    }

    @Override
    public void onClose() {
        Minecraft.getInstance().setScreen(null);
    }
}
