package com.owen.capstonemod.datamanagement;

import py4j.GatewayServer;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import com.mojang.logging.LogUtils; 
import org.slf4j.Logger;
import java.util.ArrayList;
import com.owen.capstonemod.Config;


// This class is used to recieve and store data from the python gateway
// It can recieve data, start the python gateway, and connect the EEG
// When the class is instantiated, it will start a gateway server for python to access and start the python script that connects to this gateway
public class DataBridge {
    private static DataBridge instance;

    private Object gateway;

    private Process pythonProcess;
    private ProcessBuilder processBuilder;

    private TimeSeriesData data;
    private int dataStorageSize = 30000;

    // This will only be true if the connection to the python gateway is fully established
    private boolean pythonConnected = false;
    
    public static final Logger LOGGER = LogUtils.getLogger();

    private DataBridge() {
        // Initialize the data storage
        data = new TimeSeriesData(dataStorageSize);

        // Initialize the rest as null for now
        // They will be set in the start method
        gateway = null;
        pythonProcess = null;
        processBuilder = null;
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
            while (pythonProcess == null || !pythonProcess.isAlive()) {
                startPythonEnd();
                try {
                    Thread.sleep(5000);
                } catch (InterruptedException e) {
                    LOGGER.error("Python start thread interrupted", e);
                    break;
                }
            }
        });
        pythonStartThread.setDaemon(true);
        pythonStartThread.start();
    }

    private void startGatewayServer() {
        // Start the Java end gateway server
        // Python must use this same port to connect
        GatewayServer gatewayServer = new GatewayServer(this, 25335);
        gatewayServer.start();
        LOGGER.info("Gateway server started on port " + gatewayServer.getPort());
    }

    private boolean startPythonEnd() {
        // If the python process is already running, return true
        if (pythonProcess != null && pythonProcess.isAlive()) {
            LOGGER.error("Python process already running");
            return true;
        }

        try {
            // Get the path to the Python script
            Path currentPath = Paths.get("").toAbsolutePath();
            Path exePath = currentPath
                                .getParent()
                                .getParent()
                                .resolve("output")
                                .resolve("JavaGateway")
                                .resolve("JavaGateway.exe");

            
            // Create ProcessBuilder with the executable
            processBuilder = new ProcessBuilder(exePath.toString());
            
            // Redirect error stream to output stream
            processBuilder.redirectErrorStream(true);
            
            // Start the process
            pythonProcess = processBuilder.start();
            
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

        // Start a thread to transfer data to the python end every second
        Thread startHeartbeatThread = new Thread(() -> {
            while (true) {
                pingPython();
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    LOGGER.error("Heartbeat thread interrupted", e);
                    break;
                }
            }
        });
        startHeartbeatThread.setDaemon(true);
        startHeartbeatThread.start();

        // We also need to initialize set the EEG path to the config setting
        setEEGDataPath(Config.getEEGPath());
    }

    private void pingPython() {
        if (!pythonConnected) {
            LOGGER.error("Python connection not established");
            return;
        }

        // Ping the python end to keep it alive
        ((PythonInterface) gateway).ping();
    }

    public void transferData() {
        if (!pythonConnected) {
            LOGGER.error("Python connection not established");
            return;
        }
        if (gateway == null) {
            LOGGER.error("Gateway not set");
            return;
        }

        // Expects a list of two lists of doubles
        // The first list is the values and the second is the timestamps
        ArrayList<ArrayList<Double>> new_data = new ArrayList<>();

        try {
            new_data = ((PythonInterface) gateway).get_new_data();
        } catch (Exception e) {
            LOGGER.error("Error transferring data", e);
        }

        data.append(new_data.get(0), new_data.get(1));
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

        if (targetIndex == -1)  // Array is empty
            return new ArrayView(new Double[0], 0);

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
        if (!pythonConnected) {
            LOGGER.error("Python connection not established");
            return false;
        }
        return ((PythonInterface) gateway).connect_eeg();
    }

    public void startEEGCollection() {
        if (!pythonConnected) {
            LOGGER.error("Python connection not established");
            return;
        }
        ((PythonInterface) gateway).start_eeg_collection();
    }

    public void stopEEGCollection() {
        if (!pythonConnected) {
            LOGGER.error("Python connection not established");
            return;
        }
        ((PythonInterface) gateway).stop_eeg_collection();
    }

    public void setEEGDataPath(String path) {
        if (!pythonConnected) {
            LOGGER.error("Python connection not established");
            return;
        }
        ((PythonInterface) gateway).set_eeg_data_path(path);
    }

    public int getBipolarCalibrationProgress() {
        if (!pythonConnected) {
            LOGGER.error("Python connection not established");
            return -1;
        }
        return ((PythonInterface) gateway).get_bipolar_calibration_progress();
    }

    public boolean isBipolarCalibrated() {
        if (!pythonConnected) {
            LOGGER.error("Python connection not established");
            return false;
        }
        return ((PythonInterface) gateway).is_bipolar_calibrated();
    }

    public int getMonopolarCalibrationProgress(String channel) {
        if (!pythonConnected) {
            LOGGER.error("Python connection not established");
            return -1;
        }
        return ((PythonInterface) gateway).get_monopolar_calibration_progress(channel);
    }

    public boolean isMonopolarCalibrated(String channel) {
        if (!pythonConnected) {
            LOGGER.error("Python connection not established");
            return false;
        }

        return ((PythonInterface) gateway).is_monopolar_calibrated(channel);
    }

    // HEG Methods
    public boolean connectHEG() {
        if (!pythonConnected) {
            LOGGER.error("Python connection not established");
            return false;
        }
        return ((PythonInterface) gateway).connect_heg();
    }

    public void startHEGCollection() {
        if (!pythonConnected) {
            LOGGER.error("Python connection not established");
            return;
        }
        ((PythonInterface) gateway).start_heg_collection();
    }

    public void stopHEGCollection() {
        if (!pythonConnected) {
            LOGGER.error("Python connection not established");
            return;
        }
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

    // Cleanup
    public void close() {
        if (!pythonConnected) {
            LOGGER.error("Python connection not established");
            return;
        }
        ((PythonInterface) gateway).close();
    }
}
