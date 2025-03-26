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
import com.mojang.logging.LogUtils;
import org.slf4j.Logger;

public class InfoScreen extends Screen {

    public static final Logger LOGGER = LogUtils.getLogger();

    // Constants for the screen layout
    private final int buttonWidth = 200;
    private final int buttonHeight = 20;
    private final int gap = 30;
    private final int initialY = 60; // Y position for first button
    private int currentY = initialY; // Used to track button Y position

    private final Screen lastScreen;

    Button relativeUserActivity;

    Button calibrationBar;
    boolean showingCalibrationBar = false;
    String calibrationType;
    boolean calibrated = false;
    String calibrationText = "Calibrating...";
    int calibrationProgress = 0;


    public InfoScreen(Screen lastScreen) {
        super(Component.literal("BrainLink Info"));
        this.lastScreen = lastScreen;

        calibrationType = ModState.getInstance().CALIBRATION_TYPE;

        // Show calibration bar if the type is not none, and device is on, and device is not calibrated
        if (Config.getChosenDevice().equals("eeg") && !calibrationType.equals("none") && Config.getEnableDevice() && !isCalibrated()) {
            showingCalibrationBar = true;
        }
    }

    @Override
    protected void init() {
        super.init();

        // Add "Done" button at bottom
        this.addRenderableWidget(Button.builder(
            Component.translatable("gui.done"), // Button text
            button -> this.minecraft.setScreen(this.lastScreen)) // Return to previous screen
            .pos(this.width / 2 - 100, this.height - 27) // Position
            .width(buttonWidth) // Button width
            .build()
        );
    }
    
    @Override
    public void render(GuiGraphics guiGraphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(guiGraphics, mouseX, mouseY, partialTick);

        // Draw the title
        guiGraphics.drawCenteredString(this.font, this.title, this.width / 2, 20, 0xFFFFFF);

        super.render(guiGraphics, mouseX, mouseY, partialTick);

        currentY = initialY;

        // Relative user activity rendering

        guiGraphics.drawCenteredString(this.font, Component.literal(String.format("Relative User Activity: %.2f", DataManager.getInstance().getRelativeUserActivity())), this.width / 2, currentY + 5, 0xFFFFFF);

        currentY += gap;

        // Calibration bar rendering

        // Only render if we are supposed to
        if (showingCalibrationBar) {

            // Show calibration complete if calibrated
            if (calibrated || isCalibrated()) {
                calibrated = true; // We use the extra variable to avoid checking the device every time
                calibrationProgress = 100;
                calibrationText = "Calibration Complete";
            }
            
            else {
                // Determine which calibration progress to use
                if (calibrationType.equals("bipolar")) {
                    calibrationProgress = DataBridge.getInstance().getBipolarCalibrationProgress();
                }
                else { // Must be monopolar, and so calibrationType is the channel
                    calibrationProgress = DataBridge.getInstance().getMonopolarCalibrationProgress(calibrationType);
                }
            }
    
            // Get the width of how much of the progress bar to fill
            int progressWidth = (int) (buttonWidth * (calibrationProgress / 100.0));

            // Draw the uncalibrated progress bar in grey
            guiGraphics.fill(this.width / 2 - 100, currentY, this.width / 2 - 100 + buttonWidth, currentY + buttonHeight, 0xaa333333);

            // Draw the progress bar in green
            guiGraphics.fill(this.width / 2 - 100, currentY, this.width / 2 - 100 + progressWidth, currentY + buttonHeight, 0xaa00ff00);
        
            guiGraphics.drawCenteredString(this.font, Component.literal(calibrationText), this.width / 2, currentY + 6, 0xFFFFFF);

            currentY += gap;
        }
    }

    @Override
    public void onClose() {
        Minecraft.getInstance().setScreen(null);
    }

    private boolean isCalibrated() {
        // Determine if the device is calibrated
        if (calibrationType.equals("bipolar")) {
            return DataBridge.getInstance().isBipolarCalibrated();
        }
        else if (!calibrationType.equals("none")) { // else if monopolar
            return DataBridge.getInstance().isMonopolarCalibrated(calibrationType);
        }
        return false;
    }
}
