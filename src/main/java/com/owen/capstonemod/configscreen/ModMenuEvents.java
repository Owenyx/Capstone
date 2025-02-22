package com.owen.capstonemod.configscreen;

import net.minecraft.client.gui.screens.PauseScreen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.network.chat.Component;
import net.minecraftforge.client.event.ScreenEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraft.client.Minecraft;

@OnlyIn(Dist.CLIENT)
public class ModMenuEvents {
    
    @SubscribeEvent
    public void onScreenInit(ScreenEvent.Init.Post event) {
        if (event.getScreen() instanceof PauseScreen) {
            int buttonWidth = 200;
            int buttonHeight = 20;
            // Add button just above the Options button
            event.addListener(Button.builder(
                Component.literal("Brain Control Settings"),
                button -> Minecraft.getInstance().setScreen(new ConfigScreen(event.getScreen())))
                .pos(event.getScreen().width / 2 - buttonWidth / 2, event.getScreen().height / 4 + 80)
                .width(buttonWidth)
                .build());
        }
    }
} 