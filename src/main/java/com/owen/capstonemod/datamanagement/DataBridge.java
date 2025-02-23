package com.owen.capstonemod.datamanagement;

import py4j.GatewayServer;
import py4j.ClientServer;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;
import java.util.ArrayDeque;
import com.mojang.logging.LogUtils;
import org.slf4j.Logger;

// This class is used to recieve and store data from the python gateway
// It can recieve data, start the python gateway, and connect the EEG
// When the class is instantiated, it will start the python gateway and create a gateway connection to the Python server
public class DataBridge {
    private static Process pythonProcess;
    private static ProcessBuilder processBuilder;
    private DataGateway gateway;
    private TimeSeriesData archivedData;
    private TimeSeriesData newData;
    private int storageSize = 300;
    public static final Logger LOGGER = LogUtils.getLogger(); // debug

    public DataBridge() {
        // Start the python gateway
        if (!startPythonGateway()) {
            throw new RuntimeException("Failed to start Python gateway");
        }
        
        try {
            // Create a gateway connection to the Python server
            ClientServer gateway = new ClientServer(null);
            gateway.startServer();
            
            // Get the Python gateway object
            this.gateway = (DataGateway) gateway.getPythonServerEntryPoint(new Class[]{DataGateway.class});
            
            archivedData = new TimeSeriesData(storageSize);
            newData = new TimeSeriesData(storageSize);
        } catch (Exception e) {
            throw new RuntimeException("Failed to initialize DataBridge after gateway start", e);
        }
    }

    public static boolean startPythonGateway() {
        // Starts the python-end gateway
        try {
            // Get the path to the Python script
            Path scriptPath = Paths.get("..", "..", "..", "..", "..", "..", "..", "..", "mc_mod_communication", "JavaGateway.py");
            LOGGER.info("Python script path: " + scriptPath.toString()); // debug
            
            // Create ProcessBuilder with Python executable and script path
            processBuilder = new ProcessBuilder("python", scriptPath.toString());
            
            // Redirect error stream to output stream
            processBuilder.redirectErrorStream(true);

            if (pythonProcess != null && pythonProcess.isAlive()) {
                LOGGER.info("Python process already running"); // debug
                return true;
            }
            
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

    public TimeSeriesData updateData() {
        // Incoming python data NEEDS to be a dictionary with two keys: "timestamps" and "values" that each map to deques of values
        Map<String, ArrayDeque<Double>> pythonData = (Map<String, ArrayDeque<Double>>) gateway.get_data();
        if (pythonData != null) {
            // If data was recieved, append it to the current data and refresh the new data
            newData = new TimeSeriesData(storageSize);

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

    public TimeSeriesData getArchivedData() {
        return archivedData;
    }

    public TimeSeriesData getNewData() {
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