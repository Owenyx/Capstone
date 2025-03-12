package com.owen.capstonemod.datamanagement;

import jep.JepException;
import jep.JepConfig;
import jep.SubInterpreter;
import com.mojang.logging.LogUtils; 
import org.slf4j.Logger;
import java.util.Arrays;
import java.util.List;


// This class is used to recieve and store data from the devices through python
public class DataBridge {
    private static DataBridge instance;

    private SubInterpreter jep;

    private TimeSeriesData data;
    private int dataStorageSize = 20000;
    
    public static final Logger LOGGER = LogUtils.getLogger();

    private DataBridge() {
        // Initialize the data storage
        data = new TimeSeriesData(dataStorageSize);

        // Set up JEP to work with the python object responsible for controlling the devices
        try {
            JepConfig config = new JepConfig().addIncludePaths("src/main/resources");
            jep = new SubInterpreter(config);

            // Add the resources directory to the Python path
            jep.eval("import sys");
            jep.eval("sys.path.append('src/main/resources')");

            // Import and use the PythonBridge class
            jep.eval("from pythonBridge import PythonBridge");
            jep.eval("bridge = PythonBridge()");

        } catch (JepException e) {
            LOGGER.error("Error initializing JEP", e);
        }
    }

    public static DataBridge getInstance() {
        if (instance == null) {
            instance = new DataBridge();
        }
        return instance;
    }

    public void transferData() {
        try {
            // New data is returned as a list of two lists, the first is the values and the second is the timestamps
            Object[] result = (Object[]) jep.invoke("get_new_data");

            List<Double> values = Arrays.asList((Double[]) result[0]);
            List<Double> timestamps = Arrays.asList((Double[]) result[1]);

            data.append(values, timestamps);
        } catch (JepException e) {
            LOGGER.error("Error transferring data", e);
        }
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
        try {
            return (boolean) jep.invoke("bridge.connect_eeg()");
        } catch (JepException e) {
            LOGGER.error("Error connecting EEG", e);
            return false;
        }
    }

    public void startEEGCollection() {
        try {
            jep.eval("bridge.start_eeg_collection()");
        } catch (JepException e) {
            LOGGER.error("Error starting EEG collection", e);
        }
    }

    public void stopEEGCollection() {
        try {
            jep.eval("bridge.stop_eeg_collection()");
        } catch (JepException e) {
            LOGGER.error("Error stopping EEG collection", e);
        }
    }

    public void setEEGDataPath(String path) {
        LOGGER.info("Setting EEG data path to: " + path); // debug
        try {
            jep.eval("bridge.set_eeg_data_path('" + path + "')");
        } catch (JepException e) {
            LOGGER.error("Error setting EEG data path", e);
        }
        // debug
        try {
            LOGGER.info("EEG data path: " + (String) jep.invoke("bridge.get_eeg_data_path()"));
        } catch (JepException e) {
            LOGGER.error("Error getting EEG data path", e);
        }
        // end debug
    }

    // HEG Methods
    public boolean connectHEG() {
        try {
            return (boolean) jep.invoke("bridge.connect_heg()");
        } catch (JepException e) {
            LOGGER.error("Error connecting HEG", e);
            return false;
        }
    }

    public void startHEGCollection() {
        try {
            jep.eval("bridge.start_heg_collection()");
        } catch (JepException e) {
            LOGGER.error("Error starting HEG collection", e);
        }
    }

    public void stopHEGCollection() {
        try {
            jep.eval("bridge.stop_heg_collection()");
        } catch (JepException e) {
            LOGGER.error("Error stopping HEG collection", e);
        }
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
}
