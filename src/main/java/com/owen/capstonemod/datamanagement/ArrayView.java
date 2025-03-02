package com.owen.capstonemod.datamanagement;

import java.util.Arrays;

public class ArrayView {
    // This class is used to view a subset of an array with good efficiency
    private final Double[] array;
    private final int from;
    private final int length;
    
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

    public int average() {
        double sum = 0;
        for (int i = from; i < from + length; i++) {
            sum += array[i];
        }
        return (int) (sum / length);
    }

    public Double[] toArray() {
        return Arrays.copyOfRange(array, from, from + length);
    }
}