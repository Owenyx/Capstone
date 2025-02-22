package com.owen.capstonemod;

import com.mojang.logging.LogUtils;
import net.minecraft.client.Minecraft;
import net.minecraft.core.registries.Registries;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.CreativeModeTabs;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.event.BuildCreativeModeTabContentsEvent;
import net.minecraftforge.event.server.ServerStartingEvent;
import net.minecraftforge.eventbus.api.IEventBus;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.fml.event.lifecycle.FMLClientSetupEvent;
import net.minecraftforge.fml.event.lifecycle.FMLCommonSetupEvent;
import net.minecraftforge.fml.javafmlmod.FMLJavaModLoadingContext;
import net.minecraftforge.registries.DeferredRegister;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraftforge.registries.RegistryObject;
import org.slf4j.Logger;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.ai.attributes.AttributeInstance;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.attributes.AttributeModifier;
import java.util.UUID;
import com.owen.capstonemod.datamanagement.DataManager;
import com.owen.capstonemod.configscreen.ModMenuEvents;

// The value here should match an entry in the META-INF/mods.toml file
@Mod(CapstoneMod.MOD_ID)
public class CapstoneMod {
    // Define mod id in a common place for everything to reference
    public static final String MOD_ID = "capstonemod";
    // Directly reference a slf4j logger
    public static final Logger LOGGER = LogUtils.getLogger();

    // Store the UUID so we can update/remove the same modifier
    private static final UUID SPEED_MODIFIER_UUID = UUID.fromString("d5d0d878-b85c-4c8d-8f4e-3b5d4d9a1f80");

    public CapstoneMod(FMLJavaModLoadingContext context) {
        IEventBus modEventBus = context.getModEventBus();
        modEventBus.addListener(this::commonSetup);
        
        // Register ourselves for server and other game events we are interested in
        MinecraftForge.EVENT_BUS.register(this);
        // Register our mod's ForgeConfigSpec so that Forge can create and load the config file for us
        context.registerConfig(ModConfig.Type.COMMON, Config.SPEC);
        
        // Register the menu events
        MinecraftForge.EVENT_BUS.register(new ModMenuEvents());
    }

    private void commonSetup(final FMLCommonSetupEvent event) {
        // Common setup code (runs on both client and server)
        LOGGER.info("COMMON SETUP");
    }

    // You can use EventBusSubscriber to automatically register all static methods in the class annotated with @SubscribeEvent
    @Mod.EventBusSubscriber(modid = MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
    public static class ClientModEvents {
        @SubscribeEvent
        public static void onClientSetup(FMLClientSetupEvent event) {
            event.enqueueWork(() -> {
                LOGGER.info("Initializing EEG/HEG Gateway...");
                // Initialize the data manager
                //DataManager dataManager = new DataManager();
                //try {
                    // Start your Python gateway/EEG systems
                    // Example:
                    // DataBridge.initialize();
                //} catch (Exception e) {
                //    LOGGER.error("Failed to initialize EEG systems", e);
                //}
            });
        }
    }

    /*public void updatePlayerSpeed(Player player, double speedMultiplier) {
        AttributeInstance moveSpeed = player.getAttribute(Attributes.MOVEMENT_SPEED);
        
        // Remove existing modifier if present
        moveSpeed.removeModifier(SPEED_MODIFIER_UUID);
        
        // Add new modifier
        AttributeModifier speedModifier = new AttributeModifier(
            SPEED_MODIFIER_UUID,
            "eeg_speed_modifier",
            speedMultiplier - 1.0, // Convert multiplier to modifier value
            AttributeModifier.Operation.MULTIPLY_TOTAL
        );
        
        moveSpeed.addTransientModifier(speedModifier);
    }*/
}
