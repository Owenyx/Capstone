package com.owen.capstonemod.datamanagement;

import java.util.Arrays;
import org.slf4j.Logger;
import com.mojang.logging.LogUtils;


public class ArrayView {
    // This class is used to view a subset of an array with good efficiency
    private final Double[] array;
    private final int from;
    private final int length;
    public static final Logger LOGGER = LogUtils.getLogger();
    

    public ArrayView(Double[] array, int from) {
        this.array = array;
        this.from = from;
        this.length = array.length - from;
    }
    
    public Double get(int index) {
        if (index >= length) throw new IndexOutOfBoundsException();
        return array[from + index];
    }
    
    public int size() {
        return length;
    }

    public double average() {
        if (length == 0) {
            return 0;
        }

        double sum = 0;
        for (int i = from; i < from + length; i++) {
            sum += array[i];
        }
        return (sum / length);
    }

    public Double[] toArray() {
        LOGGER.info("Array length: " + length);
        LOGGER.info("Array from: " + from);
        LOGGER.info("Array to: " + (from + length));
        return Arrays.copyOfRange(array, from, from + length);
    }
}