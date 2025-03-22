package com.owen.capstonemod.keyBinding;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.InputEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraft.client.Minecraft;

import com.owen.capstonemod.CapstoneMod;
import com.owen.capstonemod.hud.BrainLinkHud;


@Mod.EventBusSubscriber(modid = CapstoneMod.MOD_ID, value = Dist.CLIENT)
public class KeyInputHandler {

    @SubscribeEvent
    public static void onKeyInput(InputEvent.Key event) {
        // If key is pressed, open the brain link hud
        if (ModKeyBinds.CUSTOM_KEYBIND.consumeClick()) {
            System.out.println("Custom keybind pressed!");

            if (Minecraft.getInstance().screen == null) {
                Minecraft.getInstance().setScreen(new BrainLinkHud());
            }

            // Close the screen if the hotkey while the screen is open
            else {
                Minecraft.getInstance().setScreen(null);
            }
        }
    }
}