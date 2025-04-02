package com.owen.brainlink;

import com.mojang.logging.LogUtils;
import com.owen.brainlink.configscreen.MainConfigScreen;
import com.owen.brainlink.configscreen.eegdatapath.PathRootScreen;
import com.owen.brainlink.datamanagement.DataManager;

import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;

import net.minecraftforge.fml.ModContainer;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.client.ConfigScreenHandler;

import java.lang.Thread;
import net.minecraftforge.fml.event.config.ModConfigEvent;
import net.minecraft.client.Minecraft;


// The value here should match an entry in the META-INF/mods.toml file
@Mod(BrainLink.MOD_ID)
public class BrainLink {
    // Define mod id in a common place for everything to reference
    public static final String MOD_ID = "brainlink";
    // Directly reference a slf4j logger
    public static final Logger LOGGER = LogUtils.getLogger();

    
    public BrainLink(FMLJavaModLoadingContext context) {
        
        // Get mod container
        ModContainer modContainer = ModList.get().getModContainerById("brainlink")
            .orElseThrow(() -> new RuntimeException("Mod container not found!"));
            
        // Register config screen factory
        modContainer.registerExtensionPoint(
            ConfigScreenHandler.ConfigScreenFactory.class,
            () -> new ConfigScreenHandler.ConfigScreenFactory(
                (minecraft, screen) -> new MainConfigScreen(screen)
            )
        );

        // Register config
        context.registerConfig(ModConfig.Type.COMMON, Config.SPEC);
        
        MinecraftForge.EVENT_BUS.register(this);
    }


    @Mod.EventBusSubscriber(modid = BrainLink.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)
    public static class ConfigEventHandler {
        @SubscribeEvent
        public static void onConfigLoad(ModConfigEvent.Loading event) {
            // Check if the loaded config is the one you're interested in
            if (event.getConfig().getSpec() == Config.SPEC) {
                
                // Reset certain configs to default values
                Config.setEnableDevice(false);

                // If the game was closed while testing resistance, the path is set to "resist"
                // In this case, just reset the path to the reccomended one
                if (Config.getEEGPath().equals("resist")) 
                    Config.setEEGPath(PathRootScreen.reccomendedPath);

                // Set the FOV scaling to the original value, which is saved in config
                Minecraft.getInstance().options.fovEffectScale().set(Config.FOV_SCALING.get());

                // Initialize the data manager and mod state in a new thread
                new Thread(() -> {
                    try {
                        // Register the data manager instance to the event bus and initialize it simultaneously
                        MinecraftForge.EVENT_BUS.register(DataManager.getInstance());
                        // Same for mod state
                        MinecraftForge.EVENT_BUS.register(ModState.getInstance());
                    } catch (Exception e) {
                    LOGGER.error("Failed to initialize data manager", e);
                }
                }).start();
            }
        }
    }
}
