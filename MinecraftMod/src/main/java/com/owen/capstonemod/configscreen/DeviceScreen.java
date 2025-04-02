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
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;


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

    private static final Logger LOGGER = LogManager.getLogger();

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
                    ModState.getInstance().DEVICE_CONNECTING = true;
                    ModState.getInstance().setDeviceConnected(DataManager.getInstance().connectDevice());
                    if (!ModState.getInstance().getDeviceConnected()) {
                        connectionFailed = true;
                        failedEffectTime = System.currentTimeMillis();
                    }
                    ModState.getInstance().DEVICE_CONNECTING = false;
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
                Component.literal("Test Connection to Skin"),
                button -> this.minecraft.setScreen(new ResistanceScreen(this)))
                .pos(this.width / 2 - 100, currentY += gap)
                .width(buttonWidth)
                .build();
            this.addRenderableWidget(resistanceButton);

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
        if (ModState.getInstance().DEVICE_CONNECTING) {
            deviceSelectionButton.active = false;
        }
        else {
            deviceSelectionButton.active = true;
        }

        // Ensure that EEG is connected before allowing user to test resistance
        if (Config.getChosenDevice().equals("eeg")) {
            if (ModState.getInstance().EEG_CONNECTED) {
                resistanceButton.active = true;
            }
            else {
                resistanceButton.active = false;
            }
        }

        // Handle device connection button
        
        // Ensure that a device is chosen before allowing the user to connect
        if (Config.getChosenDevice().equals("none")) {
            connectDeviceButton.active = false;
        }

        // Device is connecting
        else if (ModState.getInstance().DEVICE_CONNECTING) {
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

        } 

        // Device is connected
        else if (ModState.getInstance().getDeviceConnected()) {
            connectDeviceButton.active = false;
            connectDeviceButton.setMessage(Component.literal("Connected"));
        }

        // Connection failed
        else if (connectionFailed) {
            // Show that connection failed for 2.5 seconds
            connectDeviceButton.active = true;
            connectDeviceButton.setMessage(Component.literal("Connection Failed"));
            if (System.currentTimeMillis() - failedEffectTime > 2500) {
                connectionFailed = false;
            }
        }

        // Device is not connected
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
