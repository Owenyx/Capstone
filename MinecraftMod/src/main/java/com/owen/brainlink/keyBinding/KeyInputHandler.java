package com.owen.brainlink.keyBinding;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.InputEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

import com.owen.brainlink.BrainLink;
import com.owen.brainlink.Config;
import com.owen.brainlink.ModState;
import com.owen.brainlink.configscreen.InfoScreen;
import com.owen.brainlink.configscreen.MainConfigScreen;

import net.minecraft.client.Minecraft;
import net.minecraft.network.chat.Component;

@Mod.EventBusSubscriber(modid = BrainLink.MOD_ID, value = Dist.CLIENT)
public class KeyInputHandler {

    @SubscribeEvent
    public static void onKeyInput(InputEvent.Key event) {
        // Info screen
        if (ModKeyBinds.INFO_KEYBIND.consumeClick()) {
            Minecraft.getInstance().setScreen(new InfoScreen(Minecraft.getInstance().screen));
        }

        // Configuration screen
        if (ModKeyBinds.CONFIG_KEYBIND.consumeClick()) {
            Minecraft.getInstance().setScreen(new MainConfigScreen(Minecraft.getInstance().screen));
        }

        // Toggle device
        if (ModKeyBinds.DEVICE_TOGGLE_KEYBIND.consumeClick()) {

            // Only toggle if device is connected
            if (ModState.getInstance().getDeviceConnected()) {
                Config.setEnableDevice(!Config.getEnableDevice());

                // Display message to player saying the new state of the device
                Minecraft.getInstance().player.displayClientMessage(Component.literal("Device " + (Config.getEnableDevice() ? "enabled" : "disabled")), false);
            }
            else {
                Minecraft.getInstance().player.displayClientMessage(Component.literal("Device is not connected"), false);
            }
        }
    }
}