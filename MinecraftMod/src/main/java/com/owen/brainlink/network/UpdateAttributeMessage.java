package com.owen.brainlink.network;

import com.owen.brainlink.player.AttributeManager;

import net.minecraft.network.FriendlyByteBuf;
import net.minecraftforge.event.network.CustomPayloadEvent;

public class UpdateAttributeMessage {

	private String attributeName;
	private double multiplier;

	public UpdateAttributeMessage() {}

	public UpdateAttributeMessage(String attributeName, double multiplier) {
		this.attributeName = attributeName;
		this.multiplier = multiplier;
	}

	public UpdateAttributeMessage(FriendlyByteBuf buf) {
		attributeName = buf.readUtf();
		multiplier = buf.readDouble();
	}

	public void encode(FriendlyByteBuf buf) {
		buf.writeUtf(attributeName);
		buf.writeDouble(multiplier);
	}

	public static void handle(UpdateAttributeMessage packet, CustomPayloadEvent.Context ctx) {
		ctx.enqueueWork(() -> {
			AttributeManager.getInstance().updatePlayerAttribute(ctx.getSender(), packet.attributeName, packet.multiplier);
		});
		ctx.setPacketHandled(true);
	}
}