package com.owen.capstonemod.configscreen;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.client.gui.components.Button;
import com.owen.capstonemod.configscreen.eegdatapath.PathRootScreen;
import com.owen.capstonemod.Config;
import com.owen.capstonemod.datamanagement.DataManager;
import net.minecraft.client.resources.language.I18n;
import com.owen.capstonemod.ModState;
import net.minecraft.client.gui.components.Tooltip;

public class DeviceScreen extends Screen {
    private final Screen lastScreen;

    private Button deviceSelectionButton;
    private Button resistanceButton;

    // Device connection variables
    private Button connectDeviceButton;
    private boolean connectionFailed = false;
    private double connectingEffectTime = 0;
    private int dots = 1;
    private double failedEffectTime = 0;

    // Constants for the screen layout
    private final int buttonWidth = 200;
    private final int buttonHeight = 20;
    private final int gap = 30;
    private final int initialY = 30; // Y position for first button
    private int currentY = initialY; // Used to track button Y position

    public DeviceScreen(Screen lastScreen) {
        super(Component.translatable("capstonemod.devicescreen.title")); // Screen title
        this.lastScreen = lastScreen;
    }

    @Override
    protected void init() {
        super.init();

        // Decide device name to display
        String chosenDevice;
        switch (Config.getChosenDevice()) {
            case "eeg":
                chosenDevice = I18n.get("capstonemod.devicenames.eeg"); // The I18n class is used for translations
                break;
            case "heg":
                chosenDevice = I18n.get("capstonemod.devicenames.heg");
                break;
            default:
                chosenDevice = "None";
        }

        // Selected device display
        Button selectedDeviceDisplay = Button.builder(
            Component.literal("Current Device: " + chosenDevice),
            button -> {})
            .pos(this.width / 2 - 100, currentY)
            .width(buttonWidth)
            .build();
        selectedDeviceDisplay.active = false;
        this.addRenderableWidget(selectedDeviceDisplay);

        // Device Selection button
        deviceSelectionButton = Button.builder(
            Component.literal("Select Device"),
            button -> this.minecraft.setScreen(new DeviceSelectionScreen(this)))
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build();
        this.addRenderableWidget(deviceSelectionButton);

        // Connect to device button
        connectDeviceButton = Button.builder(
            Component.translatable("Connect to Device"),
            button ->  {
                new Thread(() -> {
                    ModState.DEVICE_CONNECTING = true;
                    ModState.DEVICE_CONNECTED = DataManager.getInstance().connectDevice();
                    if (!ModState.DEVICE_CONNECTED) {
                        connectionFailed = true;
                        failedEffectTime = System.currentTimeMillis();
                    }
                    ModState.DEVICE_CONNECTING = false;
                }).start();
            })
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build();
        this.addRenderableWidget(connectDeviceButton);

        
        // Show EEG specific buttons if EEG is selected
        if (Config.getChosenDevice().equals("eeg")) {

            // Select EEG Path button
            this.addRenderableWidget(Button.builder(
                Component.literal("Select Device Data Source"),
                button -> this.minecraft.setScreen(new PathRootScreen(this)))
                .pos(this.width / 2 - 100, currentY += gap)
                .width(buttonWidth)
                .build()).setTooltip(Tooltip.create(Component.translatable("capstonemod.setdatasource.tooltip")));

            // Resistance screen button
            resistanceButton = Button.builder(
                Component.literal("Test Resistance"),
                button -> this.minecraft.setScreen(new ResistanceScreen(this)))
                .pos(this.width / 2 - 100, currentY += gap)
                .width(buttonWidth)
                .build();
            this.addRenderableWidget(resistanceButton);

            if (Config.getEEGPath().contains("emotions"))
            // Calibration screen button
            this.addRenderableWidget(Button.builder(
                Component.literal("Calibrate"),
                button -> this.minecraft.setScreen(new CalibrationScreen(this)))
                .pos(this.width / 2 - 100, currentY += gap)
                .width(buttonWidth)
                .build());
        }
        
        // Done Button
        this.addRenderableWidget(Button.builder(
            Component.translatable("gui.done"),
            button -> this.minecraft.setScreen(this.lastScreen))
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

        // Don't allow user to change device if connecting
        if (ModState.DEVICE_CONNECTING) {
            deviceSelectionButton.active = false;
        }
        else {
            deviceSelectionButton.active = true;
        }

        // Ensure that device is connected before allowing user to test resistance
        if (ModState.DEVICE_CONNECTED && Config.getChosenDevice().equals("eeg")) {
            resistanceButton.active = true;
        }
        else {
            resistanceButton.active = false;
        }
        
        // Ensure that a device is chosen before allowing the user to connect
        if (Config.getChosenDevice().equals("none")) {
            connectDeviceButton.active = false;
        }

        // Handle device connection button
        else if (ModState.DEVICE_CONNECTING) {
            // Disable button
            connectDeviceButton.active = false;
            connectDeviceButton.setMessage(Component.literal("Connecting..."));

            // Effect to show connecting, is just a ... that cycles
            double timeDifference = System.currentTimeMillis() - connectingEffectTime;
            if (timeDifference > 500) {
                dots++;
                if (dots > 3) {
                    dots = 1;
                }
                connectingEffectTime = System.currentTimeMillis();
            }
            connectDeviceButton.setMessage(Component.literal("Connecting" + ".".repeat(dots)));

        } else if (ModState.DEVICE_CONNECTED) {
            connectDeviceButton.active = false;
            connectDeviceButton.setMessage(Component.literal("Connected"));
        }

        else if (connectionFailed) {
            // Show that connection failed for 2.5 seconds
            connectDeviceButton.active = true;
            connectDeviceButton.setMessage(Component.literal("Connection Failed"));
            if (System.currentTimeMillis() - failedEffectTime > 2500) {
                connectionFailed = false;
            }
        }

        else {
            // Return to normal, not connected state
            connectDeviceButton.active = true;
            connectDeviceButton.setMessage(Component.literal("Connect to Device"));
        }
        
        // Draw the title
        guiGraphics.drawCenteredString(this.font, this.title, this.width / 2, 20, 0xFFFFFF);
            
        super.render(guiGraphics, mouseX, mouseY, partialTick);
    }
}
