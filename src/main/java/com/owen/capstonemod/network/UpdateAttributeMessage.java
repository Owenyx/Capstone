package com.owen.capstonemod.network;

import com.owen.capstonemod.player.AttributeManager;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.ResourceLocation;
import net.minecraftforge.event.network.CustomPayloadEvent;
import net.minecraft.world.entity.ai.attributes.Attribute;
import net.minecraftforge.registries.ForgeRegistries;

public class UpdateAttributeMessage {

	private ResourceLocation attribute;
	private double multiplier;

	public UpdateAttributeMessage() {}

	public UpdateAttributeMessage(ResourceLocation attribute, double multiplier) {
		this.attribute = attribute;
		this.multiplier = multiplier;
	}

	public UpdateAttributeMessage(FriendlyByteBuf buf) {
		attribute = buf.readResourceLocation();
		multiplier = buf.readDouble();
	}

	public void encode(FriendlyByteBuf buf) {
		buf.writeResourceLocation(attribute);
		buf.writeDouble(multiplier);
	}

	public static void handle(UpdateAttributeMessage packet, CustomPayloadEvent.Context ctx) {
		ctx.enqueueWork(() -> {
			AttributeManager.getInstance().updatePlayerAttribute(ctx.getSender(), packet.attribute, packet.multiplier);
		});
		ctx.setPacketHandled(true);
	}
}