package minecraftbyexample.mbe60_network_messages;

import net.minecraft.entity.Entity;
import net.minecraft.entity.EntityType;
import net.minecraft.entity.SpawnReason;
import net.minecraft.entity.player.PlayerEntity;
import net.minecraft.entity.player.ServerPlayerEntity;
import net.minecraft.entity.projectile.FireballEntity;
import net.minecraft.nbt.CompoundNBT;
import net.minecraft.util.RegistryKey;
import net.minecraft.util.SoundEvents;
import net.minecraft.util.SoundCategory;
import net.minecraft.util.math.BlockPos;
import net.minecraft.util.math.vector.Vector3d;
import net.minecraft.util.text.ITextComponent;
import net.minecraft.world.DimensionType;
import net.minecraft.world.World;
import net.minecraft.world.server.ServerWorld;
import net.minecraftforge.fml.LogicalSide;
import net.minecraftforge.fml.network.NetworkEvent;
import net.minecraftforge.fml.network.PacketDistributor;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.util.Random;
import java.util.function.Supplier;

// Note from Owen: This is a modification of an example I found on GitHub
// The GitHub repo was specifically made to provide basic examples of how to mod Minecraft.
// All comments below this are from the original example.

/**
 * The MessageHandlerOnServer is used to process the network message once it has arrived on the Server side.
 * WARNING!  The MessageHandler  runs in its own thread.  This means that if your onMessage code
 * calls any vanilla objects, it may cause crashes or subtle problems that are hard to reproduce.
 * Your onMessage handler should create a task which is later executed by the client or server thread as
 * appropriate - see below.
 * User: The Grey Ghost
 * Date: 15/01/2015
 */
public class MessageHandlerOnServer {

  /**
   * Called when a message is received of the appropriate type.
   * CALLED BY THE NETWORK THREAD, NOT THE SERVER THREAD
   * @param message The message
   */
  public static void onMessageReceived(final UpdateAttributeMessageToServer message, Supplier<NetworkEvent.Context> ctxSupplier) {
    NetworkEvent.Context ctx = ctxSupplier.get();
    LogicalSide sideReceived = ctx.getDirection().getReceptionSide();
    ctx.setPacketHandled(true);

    if (sideReceived != LogicalSide.SERVER) {
      LOGGER.warn("UpdateAttributeMessageToServer received on wrong side:" + ctx.getDirection().getReceptionSide());
      return;
    }
    if (!message.isMessageValid()) {
      LOGGER.warn("UpdateAttributeMessageToServer was invalid" + message.toString());
      return;
    }

    // we know for sure that this handler is only used on the server side, so it is ok to assume
    //  that the ctx handler is a serverhandler, and that ServerPlayerEntity exists
    // Packets received on the client side must be handled differently!  See MessageHandlerOnClient

    final ServerPlayerEntity sendingPlayer = ctx.getSender();
    if (sendingPlayer == null) {
      LOGGER.warn("EntityPlayerMP was null when UpdateAttributeMessageToServer was received");
    }

    // This code creates a new task which will be executed by the server during the next tick,
    //  In this case, the task is to call messageHandlerOnServer.processMessage(message, sendingPlayer)
    ctx.enqueueWork(() -> AttributeManager.updateAttribute(sendingPlayer, message.getAttribute(), message.getMultiplier())); 
    // Note from Owen: I think this is where i call my method to update the attribute.
  }

  public static boolean isThisProtocolAcceptedByServer(String protocolVersion) {
    return StartupCommon.MESSAGE_PROTOCOL_VERSION.equals(protocolVersion);
  }

  private static final Logger LOGGER = LogManager.getLogger();
}