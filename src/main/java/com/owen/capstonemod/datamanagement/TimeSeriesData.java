package com.owen.capstonemod.datamanagement;

import org.apache.commons.collections4.queue.CircularFifoQueue;


public class TimeSeriesData {
    private final CircularFifoQueue<Double> values;
    private final CircularFifoQueue<Double> timestamps;
    
    public TimeSeriesData(int maxSize) {
        this.values = new CircularFifoQueue<>(maxSize);
        this.timestamps = new CircularFifoQueue<>(maxSize);
    }
    
    public void appendData(double value, double timestamp) {
        values.add(value);
        timestamps.add(timestamp);
    }

    public void appendData(TimeSeriesData data) {
        timestamps.addAll(data.getTimestamps());
        values.addAll(data.getValues());
    }

    public CircularFifoQueue<Double> getTimestamps() {
        return timestamps;
    }

    public CircularFifoQueue<Double> getValues() {
        return values;
    }
}