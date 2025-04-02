package com.owen.brainlink.configscreen;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.CycleButton;
import net.minecraft.client.gui.components.AbstractSliderButton;
import net.minecraft.network.chat.Component;

import com.owen.brainlink.Config;
import com.owen.brainlink.Config.AttributeConfig;

import net.minecraft.client.gui.GuiGraphics;
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

    private boolean initialIsAffected;
    private double initialScalar;
    private boolean initialInvertScalar;
    private double initialMaxMultiplier;
    private double initialMinMultiplier;
    private double initialThreshold;
    private boolean initialInvertThreshold;


    public ModifyAttributeScreen(Screen lastScreen, String attributeName) {
        super(Component.translatable("brainlink.modifyattribute.title"));
        this.lastScreen = lastScreen;
        this.attribute = Config.ATTRIBUTES.get(attributeName);

        // Save the initial state of the attributes if all attributes are being changed
        // This is so we only update the aspects that are being changed
        if (attributeName.equals("all")) {
            initialIsAffected = attribute.getIsAffected();
            initialScalar = attribute.scalar.get();
            initialInvertScalar = attribute.invertScalar.get();
            initialMaxMultiplier = attribute.maxMultiplier.get();
            initialMinMultiplier = attribute.minMultiplier.get();
            initialThreshold = attribute.threshold.get();
            initialInvertThreshold = attribute.invertThreshold.get();
        }
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
        }).setTooltip(Tooltip.create(Component.translatable("brainlink.scalar.tooltip")));

        // Invert Scalar Button
        this.addRenderableWidget(CycleButton.onOffBuilder(attribute.invertScalar.get())
            .create(
                this.width / 2 - 100,
                currentY += gap,
                buttonWidth,
                buttonHeight,
                Component.literal("Invert Scalar"),
                (button, value) -> attribute.invertScalar.set(value)
            )).setTooltip(Tooltip.create(Component.translatable("brainlink.invertscalar.tooltip")));

        // Max Multiplier Slider
        this.addRenderableWidget(new AbstractSliderButton(
            this.width / 2 - 100, 
            currentY += gap,                 
            buttonWidth,                   
            buttonHeight,                    
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
        }).setTooltip(Tooltip.create(Component.translatable("brainlink.maxmultiplier.tooltip")));
            
        // Min Multiplier Slider
        this.addRenderableWidget(new AbstractSliderButton(
            this.width / 2 - 100,  
            currentY += gap,                
            buttonWidth,                   
            buttonHeight,                    
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
        }).setTooltip(Tooltip.create(Component.translatable("brainlink.minmultiplier.tooltip")));

        // Threshold Slider
        this.addRenderableWidget(new AbstractSliderButton(
            this.width / 2 - 100, 
            currentY += gap,                  
            buttonWidth,                  
            buttonHeight,                   
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
        }).setTooltip(Tooltip.create(Component.translatable("brainlink.threshold.tooltip")));

        // Invert Threshold Button
        this.addRenderableWidget(CycleButton.onOffBuilder(attribute.invertThreshold.get())
            .create(
                this.width / 2 - 100,
                currentY += gap,
                buttonWidth,
                buttonHeight,
                Component.literal("Invert Threshold"),
                (button, value) -> attribute.invertThreshold.set(value)
            )).setTooltip(Tooltip.create(Component.translatable("brainlink.invertthreshold.tooltip")));

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
                )).setTooltip(Tooltip.create(Component.translatable("brainlink.constantmovementfov.tooltip")));
        }

        // Done Button
        this.addRenderableWidget(Button.builder(
            Component.translatable("gui.done"),
            button -> {
                if (attribute.name.equals("all")) 
                    updateAllAttributes();
                
                this.minecraft.setScreen(this.lastScreen);
            })
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

    private void updateAllAttributes() {
        // Update the aspects that are being changed for all attributes
        // Only change an aspect if it is different from the initial value
        // i.e. if the value was modified while the user was on the 'all' screen
        for (AttributeConfig otherAttribute : Config.ATTRIBUTES.values()) {

            // Skip safe_fall_distance and entity_interaction_range as they share configs with other attributes
            if (otherAttribute.name.equals("safe_fall_distance") || otherAttribute.name.equals("entity_interaction_range"))
                continue;
            
            // We do an extra check here to make sure we don't try changing isAffected to a state it is already in.
            // The functionality of the event handler messes things up if it sets the state to the same value it already is.
            // The others have no event handler so we don't need to check them
            if (initialIsAffected != attribute.getIsAffected() && otherAttribute.getIsAffected() != attribute.getIsAffected()) 
                otherAttribute.setIsAffected(attribute.getIsAffected());
            
            if (initialScalar != attribute.scalar.get()) 
                otherAttribute.scalar.set(attribute.scalar.get());
            
            if (initialInvertScalar != attribute.invertScalar.get()) 
                otherAttribute.invertScalar.set(attribute.invertScalar.get());
            
            if (initialMaxMultiplier != attribute.maxMultiplier.get()) 
                otherAttribute.maxMultiplier.set(attribute.maxMultiplier.get());
            
            if (initialMinMultiplier != attribute.minMultiplier.get()) 
                otherAttribute.minMultiplier.set(attribute.minMultiplier.get());
            
            if (initialThreshold != attribute.threshold.get()) 
                otherAttribute.threshold.set(attribute.threshold.get());
            
            if (initialInvertThreshold != attribute.invertThreshold.get()) 
                otherAttribute.invertThreshold.set(attribute.invertThreshold.get());
        }
    }

    @Override
    public void onClose() {
        super.onClose();

        // If all attributes are being changed, update them accordingly
        if (attribute.name.equals("all")) 
            updateAllAttributes();
    }
}
