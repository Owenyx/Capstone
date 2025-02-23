package com.owen.capstonemod.configscreen;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.network.chat.Component;
import net.minecraft.client.gui.components.Button;
import java.util.concurrent.CompletableFuture;
import com.owen.capstonemod.datamanagement.DataManager;

public class EEGScreen extends Screen {
    private final Screen lastScreen;
    private boolean isSearching = false;
    private boolean connectionFailed = false;
    private long failureStartTime = 0;
    private Button eegConnectButton;

    public EEGScreen(Screen lastScreen) {
        super(Component.translatable("capstonemod.configscreen.title")); // Screen title
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
                    } else {
                        connectionFailed = true;
                        failureStartTime = System.currentTimeMillis();
                        button.setMessage(Component.literal("EEG Connection Failed"));
                    }
                    button.active = true;
                });
            })
            .pos(this.width / 2 - 100, 30)
            .width(200)
            .build();

        this.addRenderableWidget(eegConnectButton);

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
