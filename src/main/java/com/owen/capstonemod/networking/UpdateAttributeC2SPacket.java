package com.owen.capstonemod.networking;

import com.owen.capstonemod.player.AttributeManager;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraft.world.entity.player.Player;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.ResourceLocation;
import java.util.function.Supplier;

public class UpdateAttributeC2SPacket {
    private final Attribute attribute;
    private final double multiplier;
    
    public UpdateAttributeC2SPacket(Attribute attribute, double multiplier) {
        this.attribute = attribute;
        this.multiplier = multiplier;
    }
    
    public UpdateAttributeC2SPacket(FriendlyByteBuf buf) {
        ResourceLocation attributeId = buf.readResourceLocation();
        this.attribute = BuiltInRegistries.ATTRIBUTE.get(attributeId);
        this.multiplier = buf.readDouble();
    }
    
    public void encode(FriendlyByteBuf buf) {
        buf.writeResourceLocation(BuiltInRegistries.ATTRIBUTE.getKey(attribute));
        buf.writeDouble(multiplier);
    }
    
    public boolean handle(Supplier<Context> supplier) {
        Context context = supplier.get();
        context.enqueueWork(() -> {
            // This runs on the server!
            Player player = context.getSender();
            if (player != null) {
                AttributeManager.getInstance().updatePlayerAttribute(player, attribute, multiplier);
            }
        });
        return true;
    }
} 