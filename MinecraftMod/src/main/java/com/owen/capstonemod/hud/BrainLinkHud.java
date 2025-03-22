package com.owen.capstonemod.hud;

import com.owen.capstonemod.datamanagement.DataBridge;
import com.owen.capstonemod.datamanagement.DataManager;
import com.owen.capstonemod.ModState;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.Minecraft;
import net.minecraftforge.fml.common.Mod;
import com.owen.capstonemod.CapstoneMod;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import net.minecraftforge.client.event.InputEvent;
import org.lwjgl.glfw.GLFW;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.common.MinecraftForge;


@Mod.EventBusSubscriber(modid = CapstoneMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD)
public class BrainLinkHud extends Screen {

    // Relative user activity
    private int relX = 10;
    private int relY = 10;
    private int relWidth = 100;
    private int relHeight = 10;

    // Calibration bar
    private int calX = 10;
    private int calY = 25;
    private int calWidth = 100;
    private int calHeight = 10;

    public boolean visible = true;

    private static GuiGraphics guiGraphics;

    public BrainLinkHud() {
        super(Component.literal("BrainLink HUD"));
    }

    @Override
    protected void init() {
    }
    
    @Override
    public void render(GuiGraphics guiGraphics, int mouseX, int mouseY, float partialTicks) {

        // Relative user activity rendering
        
        double relativeUserActivity = DataManager.getInstance().getRelativeUserActivity();
        guiGraphics.drawString(Minecraft.getInstance().font, "Relative User Activity: " + relativeUserActivity, relX, relY, 0xaa00ff00);

        // Calibration bar rendering

        // Make sure the calibration type is not none
        if (ModState.getInstance().CALIBRATION_TYPE.equals("none")) {
            return;
        }

        int calibrationProgress = 0;

        if (ModState.getInstance().CALIBRATION_TYPE == "bipolar") {
            calibrationProgress = DataBridge.getInstance().getBipolarCalibrationProgress();
        }
        else { // Must be monopolar, and so CALIBRATION_TYPE is the channel
            calibrationProgress = DataBridge.getInstance().getMonopolarCalibrationProgress(ModState.getInstance().CALIBRATION_TYPE);
        }

        if (calibrationProgress == 100) {
            visible = false;
        }

        // Draw the calibration bar border
        guiGraphics.renderOutline(calX, calY, calX + calWidth, calY + calHeight, 0xaa000000);

        // Draw the green part of the calibration bar (progress)
        int progressWidth = (int) (calWidth * (calibrationProgress / 100.0));
        guiGraphics.fill(calX + 1, calY + 1, calX + progressWidth, calY + calHeight - 1, 0xaa00ff00);

        // Draw the gray part of the calibration bar (remaining)
        guiGraphics.fill(calX + 1 + progressWidth, calY + 1, calX + calWidth - 1, calY + calHeight - 1, 0xaa808080);
    }

    @Override
    public void onClose() {
        Minecraft.getInstance().setScreen(null);
    }
}
