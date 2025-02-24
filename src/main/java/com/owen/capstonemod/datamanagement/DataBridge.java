package com.owen.capstonemod.datamanagement;

import py4j.GatewayServer;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;
import java.util.LinkedList;
import java.util.List;
import com.mojang.logging.LogUtils; 
import org.slf4j.Logger;
import java.io.File; 

// This class is used to recieve and store data from the python gateway
// It can recieve data, start the python gateway, and connect the EEG
// When the class is instantiated, it will start a gateway server for python to access and start the python script that connects to this gateway
public class DataBridge {
    private static DataBridge instance;

    private Object gateway;

    private Process pythonProcess;
    private ProcessBuilder processBuilder;

    private TimeSeriesData archivedData;
    private TimeSeriesData newData;
    private int storageSize = 300;
    private int archiveTime = 30;

    // This will only be true if the connection to the python gateway is fully established
    private boolean pythonConnected = false;
    
    public static final Logger LOGGER = LogUtils.getLogger();

    private DataBridge() {
        // Initialize the data storage
        archivedData = new TimeSeriesData(storageSize);
        newData = new TimeSeriesData(storageSize);

        // Initialize the rest as null for now
        gateway = null;
        pythonProcess = null;
        processBuilder = null;
        // They will be set in the start method

        // Start debug thread to monitor newData
        Thread debugThread = new Thread(() -> {
            int lastSize = 0;
            while (true) {
                if (newData.getValues().size() != lastSize) {
                    LOGGER.info("New data received - size: " + newData.getValues().size());
                    lastSize = newData.getValues().size();
                }
                try {
                    Thread.sleep(1000); // Check every second
                } catch (InterruptedException e) {
                    LOGGER.error("Debug thread interrupted", e);
                    break;
                }
            }
        });
        debugThread.setDaemon(true); // Make it a daemon thread so it doesn't prevent JVM shutdown
        debugThread.start();
    }

    public static DataBridge getInstance() {
        if (instance == null) {
            instance = new DataBridge();
        }
        return instance;
    }

    public void start() {
        // Start the gateway server
        startGatewayServer();
        // Start the python end with a thread
        // Keep trying to start the python end every 5 seconds until it succeeds
        Thread pythonStartThread = new Thread(() -> {
            boolean result = false;
            while (!result) {
                result = startPythonEnd();
                try {
                    Thread.sleep(5000);
                } catch (InterruptedException e) {
                    LOGGER.error("Python start thread interrupted", e);
                    break;
                }
            }
            LOGGER.info("Python end started");
        });
        pythonStartThread.setDaemon(true);
        pythonStartThread.start();
    }

    private void startGatewayServer() {
        // Start the Java end gateway server
        // Python must use this same port to connect
        GatewayServer gatewayServer = new GatewayServer(this, 25333);
        gatewayServer.start();
        LOGGER.info("Gateway server started on port " + gatewayServer.getPort());
    }

    private boolean startPythonEnd() {
        // If the python process is already running, return true
        if (pythonProcess != null && pythonProcess.isAlive()) {
            LOGGER.info("Python process already running");
            return true;
            
        }
        try {
            // Get the path to the Python script
            Path currentPath = Paths.get("").toAbsolutePath();
            Path exePath = currentPath
                                .getParent()
                                .getParent()
                                .resolve("dist")
                                .resolve("TestJavaGateway.exe");
            
            // Create ProcessBuilder with the executable
            processBuilder = new ProcessBuilder(exePath.toString());
            
            // Redirect error stream to output stream
            processBuilder.redirectErrorStream(true);
            
            // Start the process
            pythonProcess = processBuilder.start();

            // Read the output stream in a separate thread debug
            Thread outputThread = new Thread(() -> {
                try (java.io.BufferedReader reader = new java.io.BufferedReader(
                        new java.io.InputStreamReader(pythonProcess.getInputStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        LOGGER.info("Process output: " + line);
                    }
                } catch (IOException e) {
                    LOGGER.error("Error reading process output", e);
                }
            });
            outputThread.setDaemon(true);
            outputThread.start();
            
            // Check if process is running
            boolean isAlive = pythonProcess.isAlive();
            if (!isAlive) {
                LOGGER.error("Process exited with code: " + pythonProcess.exitValue());
            } else {
                LOGGER.info("Python process started successfully");
            }
            
            return isAlive;
            
        } catch (IOException e) {
            LOGGER.error("Error starting python end", e);
            return false;
        }
    }

    // Python will use this method to set the gateway object
    public void setPythonGateway(Object gateway) {
        this.gateway = gateway;
        this.pythonConnected = true;
        LOGGER.info("Python connection established");
    }

    public void transferData() {
        ((PythonInterface) gateway).transfer_data();
    }

    public TimeSeriesData archiveData() {
        // Archive the current new data
        archivedData.append(newData);
        return archivedData;
    }

    public void setArchiveTime(int newTime) {
        // HERE !!!!!!!!!!!!!!!!;
    }

    public TimeSeriesData getArchivedData() {
        return archivedData;
    }

    public TimeSeriesData getNewData() {
        return newData;
    }

    // EEG Methods
    public boolean connectEEG() {
        return ((PythonInterface) gateway).connect_eeg();
    }

    public void startEEGCollection() {
        ((PythonInterface) gateway).start_eeg_collection();
    }

    public void stopEEGCollection() {
        ((PythonInterface) gateway).stop_eeg_collection();
    }

    public void setEEGDataPath(String path) {
        ((PythonInterface) gateway).set_eeg_data_path(path);
    }

    // HEG Methods
    public void startHEGCollection() {
        ((PythonInterface) gateway).start_heg_collection();
    }

    public void stopHEGCollection() {
        ((PythonInterface) gateway).stop_heg_collection();
    }

    // Cleanup
    public void close() {
        ((PythonInterface) gateway).close();
    }
}
