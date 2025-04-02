import subprocess
import threading

data_list = []

class HEGController:
    def __init__(self, chunk_size=6):
        self.process = None
        self.is_collecting = False
        self.chunk_size = chunk_size 
        self.current_chunk = []  # store current chunk
        self.is_collecting = False
        self.reader_thread= None
        #set=true, wait=false and waiting, clear=false
        self.stop_event = threading.Event()  # Stop signal for threads


    def start_collecting(self):
        if not self.process:
            print("Starting HEG...")
            #hh
            self.stop_event.clear()  # Reset stop flag

            self.process = subprocess.Popen(
                ["FocusMode\\main.exe"],  
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                #creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
            self.is_collecting = True
            self.reader_thread = threading.Thread(target=self._read_output)
            #self.reader_thread.daemon = True
            self.reader_thread.start()

    def _read_output(self):
        global data_list
        while self.process and self.is_collecting:
            #hh
            if self.stop_event.is_set():  #check if true, if true then HEG is off
                break
            line = self.process.stdout.readline()
            if not line:
                break
            line = line.strip()
            if line:
                self.current_chunk.append(line)
                if len(self.current_chunk) >= self.chunk_size:
                    data_list[0:self.chunk_size] = self.current_chunk
                    self.current_chunk = []  # Reset

    def stop_collecting(self):
        if self.process:
            print("Stopping HEG...")
            self.is_collecting = False
            self.stop_event.set()  # Tell thread to stop
            #hh
            try:
                self.process.terminate()
                self.process.wait(timeout=2)  # Ensure process is closed
            except subprocess.TimeoutExpired:
                print("Process did not terminate in time, killing it.")
                self.process.kill()
            self.process = None

        "kills thread"
        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join(timeout=1)  # Wait for thread to stop
            #resetting the thread
            self.reader_thread = None  
        data_list.clear()


    def get_data(self):
        global data_list
        flat_data = [float(x) for x in data_list]
        if len(flat_data) >= 30:
            return flat_data[-30:]
        else:
            return [] 
