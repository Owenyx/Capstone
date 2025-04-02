package com.owen.capstonemod.keyBinding;

import net.minecraft.client.KeyMapping;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;
import com.owen.capstonemod.CapstoneMod;

@Mod.EventBusSubscriber(modid = CapstoneMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)
public class ModKeyBinds {
    // Define a keybind with a name, category, and default key
    public static final KeyMapping INFO_KEYBIND = new KeyMapping(
        "Info Screen",
        GLFW.GLFW_KEY_B, // Default key (B in this case)
        "Brain Link Mod" // The category for the keybind
    );

    public static final KeyMapping CONFIG_KEYBIND = new KeyMapping(
        "Configuration Screen",
        GLFW.GLFW_KEY_G, 
        "Brain Link Mod"
    );

    public static final KeyMapping DEVICE_TOGGLE_KEYBIND = new KeyMapping(
        "Toggle Device",
        GLFW.GLFW_KEY_V,
        "Brain Link Mod" 
    );

    @SubscribeEvent
    public static void registerKeyMappings(RegisterKeyMappingsEvent event) {
        event.register(INFO_KEYBIND);
        event.register(CONFIG_KEYBIND);
        event.register(DEVICE_TOGGLE_KEYBIND);
    }
}