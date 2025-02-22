import subprocess
import time
import sys

def main():
    # Start the Python server
    server = subprocess.Popen([sys.executable, "eeg_server.py"])
    
    # Wait a moment for the server to start
    time.sleep(2)
    
    # Start the Java program
    java = subprocess.Popen(["java", "-jar", "your-java-program.jar"])
    
    try:
        # Wait for Java program to finish
        java.wait()
    finally:
        # Cleanup
        server.terminate()
        server.wait()

if __name__ == "__main__":
    main()