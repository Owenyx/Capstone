package com.owen.capstonemod.networking;

import com.owen.capstonemod.CapstoneMod;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.network.NetworkRegistry;
import net.minecraftforge.network.SimpleChannel;

public class ModMessages {
    private static final String PROTOCOL_VERSION = "1.0";
    public static final SimpleChannel INSTANCE = NetworkRegistry.newSimpleChannel(
        new ResourceLocation(CapstoneMod.MOD_ID, "main"),
        () -> PROTOCOL_VERSION,
        PROTOCOL_VERSION::equals,
        PROTOCOL_VERSION::equals
    );

    private static int packetId = 0;
    private static int id() {
        return packetId++;
    }

    public static void register() {
        INSTANCE.messageBuilder(UpdateAttributeC2SPacket.class, id())
            .encoder(UpdateAttributeC2SPacket::encode)
            .decoder(UpdateAttributeC2SPacket::new)
            .consumerMainThread(UpdateAttributeC2SPacket::handle)
            .add();
    }

    public static void sendToServer(UpdateAttributeC2SPacket packet) {
        INSTANCE.sendToServer(packet);
    }
} 