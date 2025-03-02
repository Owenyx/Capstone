package com.owen.capstonemod.configscreen;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.client.gui.components.Button;
import java.util.concurrent.CompletableFuture;
import com.owen.capstonemod.datamanagement.DataManager;
import com.owen.capstonemod.configscreen.eegdatapath.PathRootScreen;
import com.owen.capstonemod.ModState;
import net.minecraft.client.gui.components.Tooltip;

public class EEGScreen extends Screen {
    private final Screen lastScreen;
    private boolean isSearching = false;
    private boolean connectionFailed = false;
    private long failureStartTime = 0;
    private Button eegConnectButton;

    // Constants for the screen layout
    private final int buttonWidth = 200;
    private final int buttonHeight = 20;
    private final int gap = 30;
    private final int initialY = 30; // Y position for first button
    private int currentY = initialY; // Used to track button Y position

    public EEGScreen(Screen lastScreen) {
        super(Component.translatable("capstonemod.eegscreen.title")); // Screen title
        this.lastScreen = lastScreen;
    }

    @Override
    protected void init() {
        super.init();

        // EEG Connect Button
        eegConnectButton = Button.builder(
            Component.literal("Connect EEG"),
            button -> { // what happens when clicked
                isSearching = true;
                button.active = false;
                button.setMessage(Component.literal("Searching for EEG..."));
                
                // Run connection in separate thread
                CompletableFuture.supplyAsync(() -> {
                    return DataManager.getInstance().connectEEG();
                }).thenAccept(success -> {
                    // Set message to connected or failed
                    isSearching = false;
                    if (success) {
                        button.setMessage(Component.literal("EEG Connected"));
                        ModState.EEG_CONNECTED = true;
                    } else {
                        connectionFailed = true;
                        failureStartTime = System.currentTimeMillis();
                        button.setMessage(Component.literal("EEG Connection Failed"));
                    }
                    button.active = true;
                });
            })
            .pos(this.width / 2 - 100, currentY)
            .width(buttonWidth)
            .build();

        this.addRenderableWidget(eegConnectButton);
        
        // Set data path button
        this.addRenderableWidget(Button.builder(
            Component.literal("Set Data Source"),
            button -> this.minecraft.setScreen(new PathRootScreen(this)))
            .pos(this.width / 2 - 100, currentY += gap)
            .width(buttonWidth)
            .build()
            ).setTooltip(Tooltip.create(Component.translatable("capstonemod.setdatasource.tooltip")));

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
            
            // Handle failure state timing for the EEG Connect Button
            if (connectionFailed) {
                if (System.currentTimeMillis() - failureStartTime > 2000) {
                    connectionFailed = false;
                    eegConnectButton.setMessage(Component.literal("Connect EEG"));
                }
            }
    
            // Draw EEG Connect button background based on state
            if (!isSearching && !connectionFailed && eegConnectButton.getMessage().getString().equals("EEG Connected")) {
                // Green background for connected state
                guiGraphics.fill(eegConnectButton.getX(), eegConnectButton.getY(), 
                               eegConnectButton.getX() + eegConnectButton.getWidth(), 
                               eegConnectButton.getY() + eegConnectButton.getHeight(), 
                               0x7700FF00);
            } else if (connectionFailed) {
                // Red background for failure state
                guiGraphics.fill(eegConnectButton.getX(), eegConnectButton.getY(), 
                               eegConnectButton.getX() + eegConnectButton.getWidth(), 
                               eegConnectButton.getY() + eegConnectButton.getHeight(), 
                               0x77FF0000);
            }
            
            // Draw the title
            guiGraphics.drawCenteredString(this.font, this.title, this.width / 2, 20, 0xFFFFFF);
            
        super.render(guiGraphics, mouseX, mouseY, partialTick);
    }
}
