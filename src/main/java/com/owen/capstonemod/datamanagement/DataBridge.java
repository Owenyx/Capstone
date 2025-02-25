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
import java.io.BufferedReader;
import java.io.InputStreamReader;

// This class is used to recieve and store data from the python gateway
// It can recieve data, start the python gateway, and connect the EEG
// When the class is instantiated, it will start a gateway server for python to access and start the python script that connects to this gateway
public class DataBridge {
    private static DataBridge instance;

    private Object gateway;

    private Process pythonProcess;
    private ProcessBuilder processBuilder;

    private TimeSeriesData data;
    private int dataStorageSize = 10000;

    // This will only be true if the connection to the python gateway is fully established
    private boolean pythonConnected = false;
    
    public static final Logger LOGGER = LogUtils.getLogger();

    private DataBridge() {
        // Initialize the data storage
        data = new TimeSeriesData(dataStorageSize);

        // Initialize the rest as null for now
        gateway = null;
        pythonProcess = null;
        processBuilder = null;
        // They will be set in the start method

        // Start debug thread to monitor newData
        Thread debugThread = new Thread(() -> {
            int lastSize = 0;
            while (true) {
                if (data.getValues().size() != lastSize) {
                    LOGGER.info("New data received - size: " + data.getValues().size());
                    lastSize = data.getValues().size();
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

        // Check and clear the defualt python callback port
        checkAndClearPort(25334);

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

    public ArrayView getArchivedDataSeconds(int seconds) {
        // This function will return the archived data for the last number of seconds
        // First convert both the timestamps and values to arrays
        Double[] timestamps = data.getTimestamps().toArray(new Double[0]);
        Double[] values = data.getValues().toArray(new Double[0]);
        
        // Get the target time (in seconds)
        double targetTime = System.currentTimeMillis()/1000 - seconds;

        // Find the index of the target time
        int targetIndex = findClosestIndex(timestamps, targetTime);

        // Get the data from the target index to the end of the array
        ArrayView targetData = new ArrayView(values, targetIndex);

        // Return the target data
        return targetData;
    }

    public TimeSeriesData getData() {
        return data;
    }

    public void clearData() {
        data.clear();
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

    private int findClosestIndex(Double[] array, double target) {
        // This is only used in the getArchivedDataSeconds method
        // It's a modification of binary search that finds the index of the closest value in an array to the target
        int left = 0;
        int right = array.length - 1;
        
        // Edge cases
        if (right < 0) return -1;  // empty array
        if (target <= array[0]) return 0;
        if (target >= array[right]) return right;

        // Binary search
        while (left <= right) {
            int mid = (left + right) / 2;
            
            if (array[mid] == target) {
                return mid; // Exact match
            }
            
            if (array[mid] < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
    
        // At this point, right < left
        // Compare the values at right and left to find closest
        if (right < 0) return 0;
        if (left >= array.length) return array.length - 1;
        
        double leftDiff = Math.abs(array[left] - target);
        double rightDiff = Math.abs(array[right] - target);
        
        return leftDiff < rightDiff ? left : right;
    }

    public static void checkAndClearPort(int port) {
        try {
            // Check if we're on Windows
            boolean isWindows = System.getProperty("os.name").toLowerCase().contains("win");
            
            if (isWindows) {
                // Windows command to find PID using the port
                ProcessBuilder findPID = new ProcessBuilder(
                    "cmd", "/c", "netstat -ano | findstr :" + port
                );
                
                Process process = findPID.start();
                try (BufferedReader reader = new BufferedReader(
                        new InputStreamReader(process.getInputStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        LOGGER.info("Port {} usage: {}", port, line);
                        
                        // Extract PID from the last column
                        String[] parts = line.trim().split("\\s+");
                        if (parts.length > 4) {
                            String pid = parts[parts.length - 1];
                            
                            // Kill the process
                            ProcessBuilder killProcess = new ProcessBuilder(
                                "cmd", "/c", "taskkill /F /PID " + pid
                            );
                            LOGGER.info("Attempting to kill process {}", pid);
                            Process killCmd = killProcess.start();
                            killCmd.waitFor();
                        }
                    }
                }
            } else {
                // Unix/Linux commands
                ProcessBuilder findPID = new ProcessBuilder(
                    "sh", "-c", "lsof -t -i:" + port
                );
                
                Process process = findPID.start();
                try (BufferedReader reader = new BufferedReader(
                        new InputStreamReader(process.getInputStream()))) {
                    String line;
                    while ((line = reader.readLine()) != null) {
                        String pid = line.trim();
                        LOGGER.info("Found process {} using port {}", pid, port);
                        
                        // Kill the process
                        ProcessBuilder killProcess = new ProcessBuilder(
                            "sh", "-c", "kill -9 " + pid
                        );
                        LOGGER.info("Attempting to kill process {}", pid);
                        Process killCmd = killProcess.start();
                        killCmd.waitFor();
                    }
                }
            }
        } catch (IOException | InterruptedException e) {
            LOGGER.error("Error checking/clearing port {}: {}", port, e.getMessage());
        }
    }

    // Cleanup
    public void close() {
        ((PythonInterface) gateway).close();
    }
}
