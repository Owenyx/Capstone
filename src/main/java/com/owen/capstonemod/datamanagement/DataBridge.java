package com.owen.capstonemod.datamanagement;

import py4j.GatewayServer;
import py4j.ClientServer;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;
import java.util.ArrayDeque;


public class DataBridge {
    private DataGateway gateway;
    private TimeSeriesData archivedData;
    private TimeSeriesData newData;

    public DataBridge() {
        gateway = new GatewayServer.GatewayClient().getGateway().getPythonServerEntryPoint(DataGateway.class);
        archivedData = new TimeSeriesData();
        newData = new TimeSeriesData();
    }

    public static boolean initializeGateway() {
        // Starts the python-end gateway
        try {
            // Get the path to your Python script
            Path scriptPath = Paths.get("..", "..", "..", "mc_mod_communication", "JavaGateway.py");
            
            // Create ProcessBuilder with Python executable and script path
            processBuilder = new ProcessBuilder("python", scriptPath.toString());
            
            // Redirect error stream to output stream
            processBuilder.redirectErrorStream(true);
            
            // Start the process
            pythonProcess = processBuilder.start();
            
            // Optional: Wait a bit for Python to start up
            Thread.sleep(2000);  // 2 seconds
            
            return pythonProcess.isAlive();
            
        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
            return false;
        }
    }

    public TimeSeriesData archiveData() {
        // Archive the current new data
        archivedData.appendData(newData);
        return archivedData;
    }

    public TimeSeriesData updateNewData() {
        // Incoming python data NEEDS to be a dictionary with two keys: "timestamps" and "values" that each map to deques of values
        Map<String, ArrayDeque<Double>> pythonData = (Map<String, ArrayDeque<Double>>) gateway.get_data();
        if (pythonData != null) {
            // If data was recieved, append it to the current data and refresh the new data
            newData = new TimeSeriesData();

            ArrayDeque<Double> timestamps = pythonData.get("timestamps");
            ArrayDeque<Double> values = pythonData.get("values");

            for (int i = 0; i < timestamps.size() && i < values.size(); i++) {
                double timestamp = timestamps.poll();
                double value = values.poll();
                newData.appendData(value, timestamp);
            }
        }
        return newData;
    }

    public TimeSeriesData get_archived_data() {
        return archivedData;
    }

    public TimeSeriesData get_new_data() {
        return newData;
    }

    // EEG Methods
    public boolean connectEEG() {
        return gateway.connect_eeg();
    }

    public void startEEGCollection() {
        gateway.start_eeg_collection();
    }

    public void stopEEGCollection() {
        gateway.stop_eeg_collection();
    }

    public void setEEGDataPath(String path) {
        gateway.setEeg_data_path(path);
    }

    // HEG Methods
    public void startHEGCollection() {
        gateway.start_heg_collection();
    }

    public void stopHEGCollection() {
        gateway.stop_heg_collection();
    }

    // Cleanup
    public void cleanup() {
        gateway.cleanup();
    }
}