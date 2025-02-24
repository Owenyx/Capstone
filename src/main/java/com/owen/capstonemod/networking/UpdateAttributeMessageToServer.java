package com.owen.capstonemod.networking;

import net.minecraft.entity.EntityType;
import net.minecraft.network.PacketBuffer;
import net.minecraft.util.math.vector.Vector3d;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import net.minecraftforge.registries.ForgeRegistries;
import net.minecraft.entity.ai.attributes.Attribute;
import net.minecraft.entity.ai.attributes.Attributes;

import java.util.Random;

// Note from Owen: This is a modification of an example I found on GitHub
// The GitHub repo was specifically made to provide basic examples of how to mod Minecraft.
// All comments below this are from the original example.

/**
 * This Network Message is sent from the client to the server, to tell it to spawn projectiles at a particular location.
 * Typical usage:
 * PREREQUISITES:
 *   have previously setup SimpleChannel, registered the message class and the handler
 *
 * 1) User creates an AirStrikeMessageToServer(projectile, targetCoordinates)
 * 2) simpleChannel.sendToServer(airstrikeMessageToServer);
 * 3) Forge network code calls airstrikeMessageToServer.encode() to copy the message member variables to a PacketBuffer, ready for sending
 * ... bytes are sent over the network and arrive at the server....
 * 4) Forge network code calls airstrikeMessageToServer.decode() to recreate the airstrickeMessageToServer instance by reading
 *    from the PacketBuffer into the member variables
 * 6) the handler.onMessage(airStrikeMessageToServer) is called to process the message
 *
 * User: The Grey Ghost
 * Date: 15/01/2015
 */
public class UpdateAttributeMessageToServer
{
  public UpdateAttributeMessageToServer(Attribute i_attribute, double i_multiplier)
  {
    attribute = i_attribute;
    multiplier = i_multiplier;
    messageIsValid = true;
  }

  public Attribute getAttribute() {
    return attribute;
  }

  public double getMultiplier() {
    return multiplier;
  }

  public boolean isMessageValid() {
    return messageIsValid;
  }

  // not a valid way to construct the message
  private UpdateAttributeMessageToServer()
  {
    messageIsValid = false;
  }

  /**
   * Called by the network code once it has received the message bytes over the network.
   * Used to read the PacketBuffer contents into your member variables
   * @param buf
   */
  public static UpdateAttributeMessageToServer decode(PacketBuffer buf)
  {
    UpdateAttributeMessageToServer retval = new UpdateAttributeMessageToServer();
    try {
      retval.attribute = ForgeRegistries.ATTRIBUTES.getValue(buf.readResourceLocation());
      double multiplier = buf.readDouble();
      retval.multiplier = multiplier;

      // these methods may also be of use for your code:
      // for Itemstacks - ByteBufUtils.readItemStack()
      // for NBT tags ByteBufUtils.readTag();
      // for Strings: ByteBufUtils.readUTF8String();
      // NB that PacketBuffer is a derived class of ByteBuf
    } catch (IllegalArgumentException | IndexOutOfBoundsException e) {
      LOGGER.warn("Exception while reading UpdateAttributeMessageToServer: " + e);
      return retval;
    }
    retval.messageIsValid = true;
    return retval;
  }

  /**
   * Called by the network code.
   * Used to write the contents of your message member variables into the PacketBuffer, ready for transmission over the network.
   * @param buf
   */
  public void encode(PacketBuffer buf)
  {
    if (!messageIsValid) return;
    buf.writeResourceLocation(attribute.getRegistryName());
    buf.writeDouble(multiplier);

    // these methods may also be of use for your code:
    // for Itemstacks - ByteBufUtils.writeItemStack()
    // for NBT tags ByteBufUtils.writeTag();
    // for Strings: ByteBufUtils.writeUTF8String();
    // NB that PacketBuffer is a derived class of ByteBuf
  }

  @Override
  public String toString()  {
    return "UpdateAttributeMessageToServer[attribute=" + String.valueOf(attribute)
                                                  + ", multiplier=" + String.valueOf(multiplier) + "]";
  }

  private Attribute attribute;
  private double multiplier;
  private boolean messageIsValid;

  private static final Logger LOGGER = LogManager.getLogger();
}