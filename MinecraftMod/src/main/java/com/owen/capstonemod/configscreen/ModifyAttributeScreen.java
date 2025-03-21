package com.owen.capstonemod.configscreen;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.CycleButton;
import net.minecraft.client.gui.components.AbstractSliderButton;
import net.minecraft.network.chat.Component;
import com.owen.capstonemod.Config;
import net.minecraft.client.gui.GuiGraphics;
import com.owen.capstonemod.Config.AttributeConfig;
import net.minecraft.client.gui.components.Tooltip;


public class ModifyAttributeScreen extends Screen {
    private final Screen lastScreen;
    private final AttributeConfig attribute;

    // Constants for the screen layout
    private final int buttonWidth = 200;
    private final int buttonHeight = 20;
    private final int gap = 22;
    private final int initialY = 30; // Y position for first button
    private int currentY = initialY; // Used to track button Y position

    public ModifyAttributeScreen(Screen lastScreen, String attributeName) {
        super(Component.translatable("capstonemod.modifyattribute.title"));
        this.lastScreen = lastScreen;
        this.attribute = Config.ATTRIBUTES.get(attributeName);
    }

    @Override
    protected void init() {
        super.init();

        // isAffected Button
        this.addRenderableWidget(CycleButton.onOffBuilder(attribute.getIsAffected())
            .create(
                this.width / 2 - 100,
                currentY,
                buttonWidth,
                buttonHeight,
                Component.literal("Affected by Brain Activity"),
                (button, value) -> attribute.setIsAffected(value)
            ));

        // Scalar Slider
        this.addRenderableWidget(new AbstractSliderButton(
            this.width / 2 - 100,  // x
            currentY += gap,                   // y
            buttonWidth,                   // width
            buttonHeight,                    // height
            Component.literal("Scalar: " + 
                (attribute.scalar.get() == 0.0 ? "Disabled" : String.format("%.2f", attribute.scalar.get()))),
            attribute.scalar.get() / Config.MAX_SCALAR  // normalize 0-5 range to 0-1
        ) {
            @Override
            protected void updateMessage() {
                double actualValue = value * Config.MAX_SCALAR;
                setMessage(Component.literal("Scalar: " + 
                (actualValue == 0.0 ? "Disabled" : String.format("%.2f", actualValue))));
            }

            @Override
            protected void applyValue() {
                attribute.scalar.set(value * Config.MAX_SCALAR);
            }
        }).setTooltip(Tooltip.create(Component.translatable("capstonemod.scalar.tooltip")));

        // Invert Scalar Button
        this.addRenderableWidget(CycleButton.onOffBuilder(attribute.invertScalar.get())
            .create(
                this.width / 2 - 100,
                currentY += gap,
                buttonWidth,
                buttonHeight,
                Component.literal("Invert Scalar"),
                (button, value) -> attribute.invertScalar.set(value)
            )).setTooltip(Tooltip.create(Component.translatable("capstonemod.invertscalar.tooltip")));

        // Max Multiplier Slider
        this.addRenderableWidget(new AbstractSliderButton(
            this.width / 2 - 100,  // x
            currentY += gap,                   // y
            buttonWidth,                   // width
            buttonHeight,                    // height
            Component.literal("Max Multiplier: " + 
                (attribute.maxMultiplier.get() >= Config.MAX_MAX_MULTIPLIER ? "None" : String.format("%.2f", attribute.maxMultiplier.get()))),
            (attribute.maxMultiplier.get() / Config.MAX_MAX_MULTIPLIER)  
        ) {
            @Override
            protected void updateMessage() {
                double actualValue = value * Config.MAX_MAX_MULTIPLIER; 
                setMessage(Component.literal("Max Multiplier: " + 
                    (actualValue >= Config.MAX_MAX_MULTIPLIER ? "None" : String.format("%.2f", actualValue))));
            }

            @Override
            protected void applyValue() {
                attribute.maxMultiplier.set(value * Config.MAX_MAX_MULTIPLIER);
            }
        }).setTooltip(Tooltip.create(Component.translatable("capstonemod.maxmultiplier.tooltip")));
            
        // Min Multiplier Slider
        this.addRenderableWidget(new AbstractSliderButton(
            this.width / 2 - 100,  // x
            currentY += gap,                   // y
            buttonWidth,                   // width
            buttonHeight,                    // height
            Component.literal("Min Multiplier: " + String.format("%.2f", attribute.minMultiplier.get())),
            (attribute.minMultiplier.get() / Config.MAX_MIN_MULTIPLIER)
        ) {
            @Override
            protected void updateMessage() {
                double actualValue = value * Config.MAX_MIN_MULTIPLIER; 
                setMessage(Component.literal("Min Multiplier: " + String.format("%.2f", actualValue)));
            }

            @Override
            protected void applyValue() {
                attribute.minMultiplier.set(value * Config.MAX_MIN_MULTIPLIER);
            }
        }).setTooltip(Tooltip.create(Component.translatable("capstonemod.minmultiplier.tooltip")));

        // Threshold Slider
        this.addRenderableWidget(new AbstractSliderButton(
            this.width / 2 - 100,  // x
            currentY += gap,                   // y
            buttonWidth,                   // width
            buttonHeight,                    // height
            Component.literal("Threshold: " + String.format("%.2f", attribute.threshold.get())),
            attribute.threshold.get() / Config.MAX_THRESHOLD  // normalize 0-2 range to 0-1
        ) {
            @Override
            protected void updateMessage() {
                setMessage(Component.literal("Threshold: " + String.format("%.2f", value * Config.MAX_THRESHOLD)));
            }

            @Override
            protected void applyValue() {
                attribute.threshold.set(value * Config.MAX_THRESHOLD);
            }
        }).setTooltip(Tooltip.create(Component.translatable("capstonemod.threshold.tooltip")));

        // Invert Threshold Button
        this.addRenderableWidget(CycleButton.onOffBuilder(attribute.invertThreshold.get())
            .create(
                this.width / 2 - 100,
                currentY += gap,
                buttonWidth,
                buttonHeight,
                Component.literal("Invert Threshold"),
                (button, value) -> attribute.invertThreshold.set(value)
            )).setTooltip(Tooltip.create(Component.translatable("capstonemod.invertthreshold.tooltip")));

        // Constant Movement FOV Button, only shown if the attribute is movement_speed
        if (attribute.name.equals("movement_speed")) {
            this.addRenderableWidget(CycleButton.onOffBuilder(Config.getConstantMovementFOV())
                .create(
                this.width / 2 - 100,
                currentY += gap,
                buttonWidth,
                buttonHeight,
                Component.literal("Constant Movement FOV"),
                (button, value) -> Config.setConstantMovementFOV(value)
                )).setTooltip(Tooltip.create(Component.translatable("capstonemod.constantmovementfov.tooltip")));
        }

        // Done Button
        this.addRenderableWidget(Button.builder(
            Component.translatable("gui.done"),
            button -> this.minecraft.setScreen(this.lastScreen))
            .pos(this.width / 2 - 100, this.height - 27)
            .width(200)
            .build()
        );

        // Reset currentY to initial value
        currentY = initialY;
    }

    @Override
    public void render(GuiGraphics guiGraphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(guiGraphics, mouseX, mouseY, partialTick);
        
        // Draw the title
        guiGraphics.drawCenteredString(this.font, this.title, this.width / 2, 20, 0xFFFFFF);
        
        super.render(guiGraphics, mouseX, mouseY, partialTick);
    }
}
