package com.owen.capstonemod.datamanagement;

import py4j.GatewayServer;
import py4j.Gateway;

public class EEGReader {
    private Gateway gateway;
    private Object eegGateway;
    
    public EEGReader() {
        gateway = new Gateway();
        eegGateway = gateway.getGateway().getObject("eeg_gateway");
    }
    
    public double[] getLatestData() {
        return (double[]) gateway.getGateway().invoke("get_latest_data", eegGateway);
    }
    
    public static void main(String[] args) {
        EEGReader reader = new EEGReader();
        // Use the data
        double[] data = reader.getLatestData();
    }
}