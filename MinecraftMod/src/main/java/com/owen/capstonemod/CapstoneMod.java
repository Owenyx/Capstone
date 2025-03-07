package com.owen.capstonemod;

import com.mojang.logging.LogUtils;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import org.slf4j.Logger;
import com.owen.capstonemod.datamanagement.DataManager;
import net.minecraftforge.fml.ModContainer;
import net.minecraftforge.fml.ModList;
import net.minecraftforge.client.ConfigScreenHandler;
import com.owen.capstonemod.configscreen.ConfigScreen;
import java.lang.Thread;
import net.minecraftforge.fml.event.config.ModConfigEvent;

// The value here should match an entry in the META-INF/mods.toml file
@Mod(CapstoneMod.MOD_ID)
public class CapstoneMod {
    // Define mod id in a common place for everything to reference
    public static final String MOD_ID = "capstonemod";
    // Directly reference a slf4j logger
    public static final Logger LOGGER = LogUtils.getLogger();

    
    public CapstoneMod(FMLJavaModLoadingContext context) {
        IEventBus modEventBus = context.getModEventBus();
        modEventBus.addListener(this::commonSetup);
        
        // Get mod container
        ModContainer modContainer = ModList.get().getModContainerById("capstonemod")
            .orElseThrow(() -> new RuntimeException("Mod container not found!"));
            
        // Register config screen factory
        modContainer.registerExtensionPoint(
            ConfigScreenHandler.ConfigScreenFactory.class,
            () -> new ConfigScreenHandler.ConfigScreenFactory(
                (minecraft, screen) -> new ConfigScreen(screen)
            )
        );

        // Register config
        context.registerConfig(ModConfig.Type.COMMON, Config.SPEC);
        
        MinecraftForge.EVENT_BUS.register(this);
    }

    private void commonSetup(final FMLCommonSetupEvent event) {
        // Common setup code (runs on both client and server)
        LOGGER.info("COMMON SETUP");
    }


    @Mod.EventBusSubscriber(modid = CapstoneMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)
    public static class ConfigEventHandler {
        @SubscribeEvent
        public static void onConfigLoad(ModConfigEvent.Loading event) {
            // Check if the loaded config is the one you're interested in
            if (event.getConfig().getSpec() == Config.SPEC) {
                
                // Reset certain configs to default values
                Config.setEnableDevice(false);

                // Initialize the data manager
                new Thread(() -> {
                    try {
                        DataManager.getInstance();
                    } catch (Exception e) {
                    LOGGER.error("Failed to initialize data manager", e);
                }
                }).start();
            }
        }
    }
}
