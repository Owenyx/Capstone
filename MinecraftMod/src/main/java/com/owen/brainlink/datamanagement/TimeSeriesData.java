package com.owen.brainlink.datamanagement;

import org.apache.commons.collections4.queue.CircularFifoQueue;
import java.util.ArrayList;

public class TimeSeriesData {
    private final CircularFifoQueue<Double> values;
    private final CircularFifoQueue<Double> timestamps;
    
    public TimeSeriesData(int maxSize) {
        this.values = new CircularFifoQueue<>(maxSize);
        this.timestamps = new CircularFifoQueue<>(maxSize);
    }
    
    public void append(double value, double timestamp) {
        values.add(value);
        timestamps.add(timestamp);
    }

    public void append(ArrayList<Double> values, ArrayList<Double> timestamps) {
        this.values.addAll(values);
        this.timestamps.addAll(timestamps);
    }

    public CircularFifoQueue<Double> getTimestamps() {
        return timestamps;
    }

    public CircularFifoQueue<Double> getValues() {
        return values;
    }

    public void clear() {
        values.clear();
        timestamps.clear();
    }
}