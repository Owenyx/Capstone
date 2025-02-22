package com.owen.capstonemod.configscreen;

import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.CycleButton;
import net.minecraft.client.gui.components.AbstractSliderButton;
import net.minecraft.network.chat.Component;
import com.owen.capstonemod.Config;
import net.minecraft.client.gui.GuiGraphics;
import com.owen.capstonemod.Config.AttributeConfig;

public class ModifyAttributeScreen extends Screen {
    private final Screen lastScreen;
    private final String attributeName;
    private final AttributeConfig attribute;
    public ModifyAttributeScreen(Screen lastScreen, String attributeName) {
        super(Component.translatable("capstonemod.modifyattribute.title"));
        this.lastScreen = lastScreen;
        this.attributeName = attributeName;
        this.attribute = Config.ATTRIBUTES.get(attributeName);
    }

    @Override
    protected void init() {
        super.init();

        // isAffected Button
        this.addRenderableWidget(CycleButton.onOffBuilder(attribute.isAffected.get())
            .create(
                this.width / 2 - 100,
                50,
                200,
                20,
                Component.literal("Affected by brain activity"),
                (button, value) -> attribute.isAffected.set(value)
            ));

        // Scalar Enabled Button
        this.addRenderableWidget(CycleButton.onOffBuilder(attribute.scalarEnabled.get())
            .create(
                this.width / 2 - 100,
                80,
                200,
                20,
                Component.literal("Scalar Enabled"),
                (button, value) -> attribute.scalarEnabled.set(value)
            ));

        // Scalar Slider
        this.addRenderableWidget(new AbstractSliderButton(
            this.width / 2 - 100,  // x
            200,                   // y
            200,                   // width
            20,                    // height
            Component.literal("Scalar: " + attribute.scalar.get()),
            attribute.scalar.get() / 2.0  // normalize 0-2 range to 0-1
        ) {
            @Override
            protected void updateMessage() {
                setMessage(Component.literal("Scalar: " + String.format("%.1f", value * 2.0)));
            }

            @Override
            protected void applyValue() {
                attribute.scalar.set(value * 2.0);
            }
        });

        // Max Multiplier Slider
        this.addRenderableWidget(new AbstractSliderButton(
            this.width / 2 - 100,  // x
            140,                   // y
            200,                   // width
            20,                    // height
            Component.literal("Max Multiplier: " + attribute.maxMultiplier.get()),
            (attribute.maxMultiplier.get() - 1.0) / 4.0  // normalize 1-5 range to 0-1
        ) {
            @Override
            protected void updateMessage() {
                double actualValue = value * 4.0 + 1.0;  // convert back to 1-5 range
                setMessage(Component.literal("Max Multiplier: " + 
                    (actualValue >= 5.0 ? "None" : String.format("%.1f", actualValue))));
            }

            @Override
            protected void applyValue() {
                attribute.maxMultiplier.set(value * 4.0 + 1.0);
            }
        });
            
        // Min Multiplier Slider
        this.addRenderableWidget(new AbstractSliderButton(
            this.width / 2 - 100,  // x
            170,                   // y
            200,                   // width
            20,                    // height
            Component.literal("Min Multiplier: " + attribute.minMultiplier.get()),
            (attribute.minMultiplier.get() - 0.1) / 0.9  // normalize 0.1-1.0 range to 0-1
        ) {
            @Override
            protected void updateMessage() {
                double actualValue = value * 0.9 + 0.1;  // convert back to 0.1-1.0 range
                setMessage(Component.literal("Min Multiplier: " + String.format("%.1f", actualValue)));
            }

            @Override
            protected void applyValue() {
                attribute.minMultiplier.set(value * 0.9 + 0.1);
            }
        });

        // Invert Scalar Button
        this.addRenderableWidget(CycleButton.onOffBuilder(attribute.invertScalar.get())
            .create(
                this.width / 2 - 100,
                200,
                200,
                20,
                Component.literal("Invert Scalar"),
                (button, value) -> attribute.invertScalar.set(value)
            ));

        // Threshold Slider
        this.addRenderableWidget(new AbstractSliderButton(
            this.width / 2 - 100,  // x
            230,                   // y
            200,                   // width
            20,                    // height
            Component.literal("Threshold: " + attribute.threshold.get()),
            attribute.threshold.get() / 2.0  // normalize 0-2 range to 0-1
        ) {
            @Override
            protected void updateMessage() {
                setMessage(Component.literal("Threshold: " + String.format("%.1f", value * 2.0)));
            }

            @Override
            protected void applyValue() {
                attribute.threshold.set(value * 2.0);
            }
        });

        // Invert Threshold Button
        this.addRenderableWidget(CycleButton.onOffBuilder(attribute.invertThreshold.get())
            .create(
                this.width / 2 - 100,
                230,
                200,
                20,
                Component.literal("Invert Threshold"),
                (button, value) -> attribute.invertThreshold.set(value)
            ));

        // Done Button
        this.addRenderableWidget(Button.builder(
            Component.translatable("gui.done"),
            button -> this.minecraft.setScreen(this.lastScreen))
            .pos(this.width / 2 - 100, this.height - 27)
            .width(200)
            .build()
        );
    }

    @Override
    public void render(GuiGraphics guiGraphics, int mouseX, int mouseY, float partialTick) {
        this.renderBackground(guiGraphics, mouseX, mouseY, partialTick);
        
        // Draw the title
        guiGraphics.drawCenteredString(this.font, this.title, this.width / 2, 20, 0xFFFFFF);
        
        super.render(guiGraphics, mouseX, mouseY, partialTick);
    }
}
