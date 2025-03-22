package com.owen.capstonemod.keyBinding;

import net.minecraft.client.KeyMapping;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;
import com.owen.capstonemod.CapstoneMod;

@Mod.EventBusSubscriber(modid = CapstoneMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)
public class ModKeyBinds {
    // Define a keybind with a name, category, and default key
    public static final KeyMapping CUSTOM_KEYBIND = new KeyMapping(
        "key.capstonemod.custom_keybind", // The translation key for the keybind
        GLFW.GLFW_KEY_B, // Default key (B in this case)
        "key.categories.capstonemod" // The category for the keybind
    );

    @SubscribeEvent
    public static void registerKeyMappings(RegisterKeyMappingsEvent event) {
        event.register(CUSTOM_KEYBIND);
    }
}