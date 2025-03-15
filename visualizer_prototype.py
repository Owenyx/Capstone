import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from EEG_Controller import Controller as EEGController
from HEG_Controller import HEGController
from threading import Thread
import time
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import tkinter.filedialog as fd
import csv
import os

# main visualizer class for the entire application
class Visualizer:
    def __init__(self):
        # controllers for the heg and eeg
        self.heg_controller = HEGController()
        self.eeg_controller = EEGController()
        self.eeg_connected = False

        # configure the root window
        self.root = ttk.Window(themename="darkly")
        self.root.iconbitmap("neurofeedback.ico")
        self.root.title("Neurofeedback Visualizer")
        self.root.geometry("1024x768")

        # Create the main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)

        # Dictionary to store all frames
        self.frames = {}

        # Create and store all frames
        # if you add a new frame, you need to add it here
        for F in (HomeFrame, HEGFrame, EEGFrame, ColorTrainingFrame, ColorPredictorFrame):
            frame = F(self.main_frame, self)
            self.frames[F] = frame
            frame.pack(fill='both', expand=True)
            
        self.eeg_frames = [EEGFrame, ColorTrainingFrame, ColorPredictorFrame]

        # Show the initial frame
        self.show_frame(HomeFrame)

    def show_frame(self, frame_class):
        """Raises the specified frame to the top"""
        # Hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
        # Show the selected frame
        frame = self.frames[frame_class]
        frame.pack(fill='both', expand=True)

    def connect_device(self):
        self.connect_popup = ttk.Window(themename="darkly")
        self.connect_popup.title("Device Connection")
        self.connect_popup.geometry("300x100")
        self.connect_label = ttk.Label(self.connect_popup, text="Connecting to device...", anchor="center")
        self.connect_label.pack(expand=True, fill='both')
        Thread(target=self.connect_eeg, daemon=True).start()

    # fix this so that the buttons are not here
    def connect_eeg(self):
        """Handles device connection"""
        # use the controller to find and connect to the device
        if self.eeg_controller.find_and_connect():
            self.eeg_connected = True
            for frame in self.eeg_frames:
                self.frames[frame].connect_btn.configure(state=DISABLED)
                for btn in self.frames[frame].control_buttons.values():
                    btn.configure(state=NORMAL)
            print("EEG device connected successfully!")
            self.root.after(0, lambda: self.connect_label.configure(text="Device connected successfully!"))
            self.root.after(0, lambda: self.connect_label.configure(background="green"))
        else:
            print("Failed to connect to EEG device")
            self.root.after(0, lambda: self.connect_label.configure(text="Failed to connect to EEG device"))
            self.root.after(0, lambda: self.connect_label.configure(background="red"))
        self.root.after(2000, lambda: self.connect_popup.destroy())

    def run(self):
        self.root.mainloop()

# Create separate classes for each frame
class HomeFrame(ttk.Frame):
    def __init__(self, parent, visualizer):
        ttk.Frame.__init__(self, parent)
        
        # Create a container frame that will center our content
        center_frame = ttk.Frame(self)
        center_frame.pack(expand=True)
        
        label = ttk.Label(center_frame, text="Welcome to Neurofeedback Visualizer", font=("TkDefaultFont", 16))
        label.pack(pady=20)
        
        heg_button = ttk.Button(center_frame, text="HEG Visualizer", command=lambda: visualizer.show_frame(HEGFrame))
        heg_button.pack(pady=10)
        
        eeg_button = ttk.Button(center_frame, text="EEG Visualizer", command=lambda: visualizer.show_frame(EEGFrame))
        eeg_button.pack(pady=10)

        color_training_button = ttk.Button(center_frame, text="Color Training", command=lambda: visualizer.show_frame(ColorTrainingFrame))
        color_training_button.pack(pady=10)

        color_predictor_button = ttk.Button(center_frame, text="Color Predictor", command=lambda: visualizer.show_frame(ColorPredictorFrame))
        color_predictor_button.pack(pady=10)


class ColorTrainingFrame(ttk.Frame):
    def __init__(self, parent, visualizer):
        ttk.Frame.__init__(self, parent)
        self.visualizer = visualizer
        self.heg_controller = visualizer.heg_controller
        self.eeg_controller = visualizer.eeg_controller
        self.save_file_path = None
        self.save_file_name = "Training Data"

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.create_control_panel()

    def create_control_panel(self):
        control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding=10)
        control_frame.pack(fill=X, pady=(0, 10))

        self.connect_btn = ttk.Button(
            control_frame,
            text="Connect to Device",
            command=lambda: self.visualizer.connect_device(),
            style="primary.TButton"
        )
        self.connect_btn.pack(side=LEFT, padx=5)

        self.control_buttons = {}
        self.start_EEG_training_button = ttk.Button(control_frame, text="Start EEG Training", command=self.start_EEG_training)
        self.start_EEG_training_button.pack(side=LEFT, padx=5)
        self.start_EEG_training_button.configure(state=DISABLED)
        self.control_buttons["EEG Training"] = self.start_EEG_training_button

        if self.visualizer.eeg_connected:
            self.connect_btn.configure(state=DISABLED)
            # self.start_EEG_training_button.configure(state=NORMAL)

        self.start_HEG_training_button = ttk.Button(control_frame, text="Start HEG Training", command=self.start_HEG_training)
        self.start_HEG_training_button.pack(side=LEFT, padx=5)

        if self.save_file_path is None:
            self.start_HEG_training_button.configure(state=DISABLED)

        self.back_button = ttk.Button(
            control_frame,
            text="Back to Home",
            command=lambda: self.visualizer.show_frame(HomeFrame),
            style="primary.TButton"
        )
        self.back_button.pack(side=LEFT, padx=5)

        # Update the button to allow selecting a folder instead of a file.
        self.choose_folder_btn = ttk.Button(
            control_frame,
            text="Select Folder",
            command=self.choose_folder,
            style="primary.TButton"
        )
        self.choose_folder_btn.pack(side=LEFT, padx=5)

        # Add a label to display the selected folder.
        self.folder_label = ttk.Label(
            control_frame,
            text="None",
            foreground="white"
        )
        self.folder_label.pack(side=LEFT, padx=5)

    def choose_folder(self):
        # Open a directory chooser dialog so the user can select a folder to save the training data.
        folder_path = fd.askdirectory(
            title="Select Folder to Save Training Data",
            initialdir="."
        )
        if folder_path:
            self.save_file_path = folder_path  # Optionally, rename to self.save_folder_path for clarity.
            self.folder_label.configure(text=f"Selected folder: {self.save_file_path}")
            # self.file_path = os.path.join(self.save_file_path, self.save_file_name)

            # Optionally, enable the HEG training button if selecting the folder is required.
            self.start_HEG_training_button.configure(state=NORMAL)
            if self.visualizer.eeg_connected:
                self.start_EEG_training_button.configure(state=NORMAL)

    def start_EEG_training(self):
        print("Starting EEG Training")
        self.eeg_controller.storage_time = 30
        # Create a new full-screen window for color training
        training_window = ttk.Toplevel(self.visualizer.root)
        training_window.attributes("-fullscreen", True)
        
        # Bind Escape key to cancel the training sequence
        training_window.bind("<Escape>", lambda e: training_window.destroy())
        
        gray_duration = 30000
        target_color_duration = self.eeg_controller.storage_time * 1000
        
        # Define the sequence of (color, duration in milliseconds)
        color_steps = [
            ("gray", gray_duration),
            ("blue", target_color_duration),
            ("gray", gray_duration),
            ("green", target_color_duration),
            ("gray", gray_duration),
            ("red", target_color_duration)
        ]
        
        def run_step(index):
            # Check if window still exists (i.e., training has not been canceled)
            if not training_window.winfo_exists():
                return
            if index < len(color_steps):
                color, duration = color_steps[index]                
                training_window.configure(bg=color)

                # start collecting 
                if color == "gray":
                    total_duration = gray_duration + target_color_duration
                    Thread(
                        target=lambda: self.collect_eeg_data_for_color(color_steps[index + 1][0], total_duration)
                    ).start()

                training_window.after(duration, lambda: run_step(index + 1))
            else:
                training_window.destroy()
        
        run_step(0)
        
    # NEW helper method added to the class
    def collect_eeg_data_for_color(self, color, duration_ms):

        duration_sec = duration_ms / 1000.0
        # just collecting the spectrum data for now until we know what data we have to work with
        self.eeg_controller.start_spectrum_collection()
        time.sleep(duration_sec)
        self.eeg_controller.stop_collection()
        directory = self.save_file_path + f"/signal_{color}"
        self.eeg_controller.log_deques_to_files(directory, signal=True, spectrum=True, waves=True)

    def start_HEG_training(self):
        print("Starting HEG Training")

        # Create a new full-screen window for color training
        training_window = ttk.Toplevel(self.visualizer.root)
        training_window.attributes("-fullscreen", True)
        
        # Bind Escape key to cancel the training sequence
        training_window.bind("<Escape>", lambda e: training_window.destroy())
        
        # Define the sequence of (color, duration in milliseconds)
        color_steps = [
            ("gray", 30000),  # Gray for 30 seconds
            ("blue", 10000),  # Blue for 10 seconds
            ("gray", 30000),  # Gray for 30 seconds
            ("green", 10000), # Green for 10 seconds
            ("gray", 30000),  # Gray for 30 seconds
            ("red", 10000)    # Red for 10 seconds
        ]
        
        def run_step(index):
            # Check if window still exists (i.e., training has not been canceled)
            if not training_window.winfo_exists():
                return
            if index < len(color_steps):
                color, duration = color_steps[index]
                training_window.configure(bg=color)
                
                # If the step is not gray, then collect data during this phase
                if color != "gray":
                    Thread(
                        target=lambda: self.collect_data_for_color_step(color, duration)
                    ).start()
                
                training_window.after(duration, lambda: run_step(index + 1))
            else:
                training_window.destroy()
        
        run_step(0)

    # NEW helper method added to the class
    def collect_data_for_color_step(self, color, duration_ms):
        """
        For a given non-gray color phase, run the data collection for the length of that phase.
        Converts duration from ms to seconds, collects CSV data, and then saves & clears it.
        """
        duration_sec = duration_ms / 1000.0
        self.heg_controller.collect_data_for_time(duration_sec)
        self.heg_controller.save_readings_for_color(color)


class ColorPredictorFrame(ttk.Frame):
    def __init__(self, parent, visualizer):
        ttk.Frame.__init__(self, parent)
        self.visualizer = visualizer

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        self.create_control_panel()
        
        self.is_predicting = False
        self.color = "blue"
        self.color_frame = tk.Frame(self.main_frame, bg=self.color)
        self.color_label = ttk.Label(self.main_frame, text=self.color.capitalize(), font=("TkDefaultFont", 24), foreground=self.color.capitalize(), justify="center")
        
    def create_control_panel(self):
        control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding=10)
        control_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        
        self.connect_btn = ttk.Button(
            control_frame,
            text="Connect to Device",
            command=lambda: self.visualizer.connect_device(),
            style="primary.TButton"
        )
        self.connect_btn.pack(side=LEFT, padx=5)
        
        self.control_buttons = {}
        self.start_prediction_button = ttk.Button(control_frame, text="Start Prediction", command=self.toggle_prediction)
        self.start_prediction_button.pack(side=LEFT, padx=5)
        self.start_prediction_button.configure(state=NORMAL)
        self.control_buttons["Prediction"] = self.start_prediction_button
                    
        self.color_buttons = {}
        for color in ["blue", "green", "red"]:
            btn = ttk.Button(
                control_frame,
                text=color.capitalize(),
                command=lambda c=color: self.change_color(c),
                style="primary.TButton"
            )
            btn.configure(state=NORMAL)
            btn.pack(side=LEFT, padx=5)
            self.color_buttons[color] = btn
        
        self.back_button = ttk.Button(
            control_frame,
            text="Back to Home",
            command=lambda: self.visualizer.show_frame(HomeFrame),
            style="primary.TButton"
        )
        self.back_button.pack(side=LEFT, padx=5)

    def toggle_prediction(self):
        self.is_predicting = not self.is_predicting
        if self.is_predicting:
            for btn in self.color_buttons.values():
                btn.configure(state=NORMAL)
            
            # Configure the row of self.main_frame holding the color_frame to expand.
            # Assuming your control panel is in row 0, this sets row 1 to take all available vertical space.
            
            # Place the color_frame in row 1 (without a fixed rowspan)
            self.color_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
            self.color_frame.configure(bg=self.color)
            self.color_label.grid(row=1, column=1, sticky="nsew", padx=(0, 10), pady=(0, 10))
            self.color_label.configure(text=self.color.capitalize(), foreground=self.color.capitalize())
            
            self.start_prediction_button.configure(text="Stop Prediction", style="danger.TButton")
        else:
            for btn in self.color_buttons.values():
                btn.configure(state=DISABLED)
            
            self.color_frame.grid_forget()
            self.color_label.grid_forget()
            
            self.start_prediction_button.configure(text="Start Prediction", style="primary.TButton")

    def change_color(self, color):
        self.color = color
        if self.is_predicting:
            self.color_frame.configure(bg=color)
            self.color_label.configure(text=color.capitalize(), foreground=color.capitalize())

class HEGFrame(ttk.Frame):
    def __init__(self, parent, visualizer):
        ttk.Frame.__init__(self, parent)
        self.visualizer = visualizer

        self.controller = visualizer.heg_controller

        # everything sits on this main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.is_collecting = False
        
        # control panel is the buttons at the top of the window
        self.create_control_panel()

        self.create_plot()

        self.collection_thread = None

    def create_control_panel(self):
        """Creates the control panel with buttons"""
        control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding=10)
        control_frame.pack(fill=X, pady=(0, 10))
        
        self.collection_button = ttk.Button(
            control_frame,
            text="Start HEG Session",
            command=self.toggle_collection,
            style="primary.TButton"
        )
        self.collection_button.pack(side=LEFT, padx=5)

        self.save_button = ttk.Button(
            control_frame,
            text="Save HEG Readings",
            command=self.controller.save_readings,
            style="primary.TButton"
        )
        self.save_button.pack(side=LEFT, padx=5)
        self.save_button.configure(state=DISABLED)

        self.back_button = ttk.Button(
            control_frame,
            text="Back to Home",
            command=lambda: self.visualizer.show_frame(HomeFrame),
            style="primary.TButton"
        )
        self.back_button.pack(side=LEFT, padx=5)
    
    def create_plot(self):
        plot_frame = ttk.Frame(self.main_frame)
        plot_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Add a label above the graph to display the current reading.
        self.reading_label = ttk.Label(plot_frame, text="Current Reading: N/A", font=("TkDefaultFont", 12))
        self.reading_label.pack(side=TOP, anchor="w", pady=(0, 5))

        self.fig = Figure(figsize=(12, 8))
        self.plot = self.fig.add_subplot()

        # Create a persistent line object (initially empty)
        self.line, = self.plot.plot([], [])

        # Set axis labels and tick settings
        self.plot.set_title("HEG Readings")
        self.plot.set_xlabel("Time")
        self.plot.set_ylabel("Reading")
        self.plot.set_ylim(0, 200)

        canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        self.plot_canvas = canvas
        self.anim = None

    def update_plot(self, frame):
        if not self.is_collecting:
            return self.line,
        
        # Retrieve data from deques in the controller
        x = list(self.controller.readings["timestamp"])
        y = list(self.controller.readings["reading"])
        
        # Convert y-values from string to float
        try:
            y = [float(val) for val in y]
        except ValueError:
            # If conversion fails, skip updating this frame.
            return self.line,
        
        # Update the current reading label with the latest reading value.
        if y:
            current_reading = y[-1]
            self.reading_label.configure(text=f"Current Reading: {current_reading}")
        else:
            self.reading_label.configure(text="Current Reading: N/A")
        
        # Update the persistent line's data instead of clearing the plot
        self.line.set_data(x, y)
        # Update the axis view limits (autoscale the x-axis; y-axis remains fixed)
        self.plot.relim()
        self.plot.autoscale_view(scalex=True, scaley=False)
        return self.line,

    # start and stop the HEG_Controller.py program here
    def toggle_collection(self):
        if not self.is_collecting:
            self.back_button.configure(state=DISABLED)
            self.save_button.configure(state=DISABLED)
            self.is_collecting = True
            self.collection_button.configure(
                text="Stop HEG Collection",
                style="danger.TButton"
            )
            self.collection_thread = Thread(target=self.controller.collect_data, daemon=True)
            self.collection_thread.start()
            self.anim = FuncAnimation(self.fig, self.update_plot, interval=100, blit=False)
            self.plot_canvas.draw()
        else:
            self.is_collecting = False
            self.controller.stop_reading()
            self.back_button.configure(state=NORMAL)
            self.save_button.configure(state=NORMAL)
            self.collection_button.configure(
                text="Start HEG Collection",
                style="primary.TButton"
            )
            if self.anim:
                self.anim.event_source.stop()


class EEGFrame(ttk.Frame):
    def __init__(self, parent, visualizer):
        ttk.Frame.__init__(self, parent)
        self.visualizer = visualizer
        
        # Initialize Controller for EEG data
        self.controller = visualizer.eeg_controller
        
        # everything sits on this main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # control panel is the buttons at the top of the window
        self.create_control_panel()
        
        # use a notebook to switch between different sets of plots
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # Create tabs
        self.create_signal_tab()
        self.create_resistance_tab()
        self.create_emotions_bipolar_raw_tab()
        self.create_emotions_bipolar_percent_tab()
        
        # Initialize collection flags
        self.is_collecting = {
            'signal': False,
            'resist': False,
            'emotions_bipolar_raw': False,
            'emotions_bipolar_percent': False,
        }
        self.plot_threads = {}

    def create_control_panel(self):
        """Creates the control panel with buttons"""
        control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding=10)
        control_frame.pack(fill=X, pady=(0, 10))

        self.connect_btn = ttk.Button(
            control_frame,
            text="Connect to Device",
            command=self.visualizer.connect_device,
            style="primary.TButton"
        )
        self.connect_btn.pack(side=LEFT, padx=5)

        if self.visualizer.eeg_connected:
            self.connect_btn.configure(state=DISABLED)

        self.control_buttons = {}
        for data_type in ['signal', 'resist', 'emotions_bipolar_raw', 'emotions_bipolar_percent']:
            btn = ttk.Button(
                control_frame,
                text=f"Start {data_type.replace('_', ' ').title()}",
                command=lambda dt=data_type: self.toggle_collection(dt),
                style="success.TButton"
            )
            btn.pack(side=LEFT, padx=5)
            if not self.visualizer.eeg_connected:
                btn.configure(state=DISABLED)
            self.control_buttons[data_type] = btn
        
        self.back_button = ttk.Button(
            control_frame,
            text="Back to Home",
            command=lambda: self.visualizer.show_frame(HomeFrame),
            style="primary.TButton"
        )
        self.back_button.pack(side=LEFT, padx=5)

    def create_data_tab(self, notebook, tab_title, ax_title_func, y_label, axes_attr_name, lines_attr_name, canvas_attr_name, items=None, positions=None):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=tab_title)
        
        fig = Figure(figsize=(12, 8))
        axes_dict = {}
        lines_dict = {}
        
        # Default to EEG channels if no custom items are provided.
        if items is None:
            items = ['O1', 'O2', 'T3', 'T4']
        
        # Default positions: if none are provided and there are four items, use a 2x2 layout.
        if positions is None:
            if len(items) == 4:
                positions = [221, 222, 223, 224]
            else:
                # For other numbers, a simple row layout is used.
                positions = [int(f"11{i+1}") for i in range(len(items))]
        
        for pos, item in zip(positions, items):
            ax = fig.add_subplot(pos)
            ax.set_title(ax_title_func(item))
            ax.set_xlabel("Time (s)")
            ax.set_ylabel(y_label)
            axes_dict[item] = ax
            line, = ax.plot([], [])
            lines_dict[item] = line

        fig.tight_layout(pad=2.0)
        
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        
        setattr(self, axes_attr_name, axes_dict)
        setattr(self, lines_attr_name, lines_dict)
        setattr(self, canvas_attr_name, canvas)

    def create_signal_tab(self):
        self.create_data_tab(
            notebook=self.notebook,
            tab_title="Signal",
            ax_title_func=lambda ch: f"Channel {ch}",
            y_label="Amplitude",
            axes_attr_name="signal_axes",
            lines_attr_name="signal_lines",
            canvas_attr_name="signal_canvas"
        )

    def create_resistance_tab(self):
        self.create_data_tab(
            notebook=self.notebook,
            tab_title="Resistance",
            ax_title_func=lambda ch: f"Channel {ch} Resistance",
            y_label="Resistance (kΩ)",
            axes_attr_name="resist_axes",
            lines_attr_name="resist_lines",
            canvas_attr_name="resist_canvas"
        )

    def create_emotions_bipolar_raw_tab(self):
        items = ['attention', 'relaxation', 'alpha', 'beta']
        self.create_data_tab(
            notebook=self.notebook,
            tab_title="Emotions (Bipolar) Raw",
            ax_title_func=lambda metric: f"{metric.title()} (Raw)",
            y_label="Raw Value",
            axes_attr_name="bipolar_raw_axes",
            lines_attr_name="bipolar_raw_lines",
            canvas_attr_name="bipolar_raw_canvas",
            items=items,
            positions=[221, 222, 223, 224]
        )

    def create_emotions_bipolar_percent_tab(self):
        items = ['attention', 'relaxation', 'alpha', 'beta']
        self.create_data_tab(
            notebook=self.notebook,
            tab_title="Emotions (Bipolar) Percent",
            ax_title_func=lambda metric: f"{metric.title()} (Percent)",
            y_label="Percent Value",
            axes_attr_name="bipolar_percent_axes",
            lines_attr_name="bipolar_percent_lines",
            canvas_attr_name="bipolar_percent_canvas",
            items=items,
            positions=[221, 222, 223, 224]
        )

    def update_signal_plots(self, frame):
        """Update signal plots for FuncAnimation on EEGFrame."""
        channels = ['O1', 'O2', 'T3', 'T4']
        if not self.is_collecting['signal']:
            # Return the current line objects if collection is stopped
            return tuple(self.signal_lines[ch] for ch in channels)
        
        for channel in channels:
            # Get data from controller's deques
            timestamps = list(self.controller.deques['signal'][channel]['timestamps'])
            values = list(self.controller.deques['signal'][channel]['values'])
            
            if timestamps and values:
                # Convert timestamps to relative time (seconds from start)
                relative_times = [t - timestamps[0] for t in timestamps]
                # Update the line data
                self.signal_lines[channel].set_data(relative_times, values)
                # Recalculate plot limits
                self.signal_axes[channel].relim()
                # Update the view to show all data
                self.signal_axes[channel].autoscale_view()
        
        # Return updated artists to FuncAnimation (helps with blitting, if enabled)
        return tuple(self.signal_lines[ch] for ch in channels)

    def update_resist_plots(self, frame):
        """Update resistance plots for FuncAnimation on EEGFrame."""
        channels = ['O1', 'O2', 'T3', 'T4']
        if not self.is_collecting['resist']:
            return tuple(self.resist_lines[ch] for ch in channels)
        
        for channel in channels:
            timestamps = list(self.controller.deques['resist'][channel]['timestamps'])
            values = list(self.controller.deques['resist'][channel]['values'])
            
            if timestamps and values:
                relative_times = [t - timestamps[0] for t in timestamps]
                self.resist_lines[channel].set_data(relative_times, values)
                self.resist_axes[channel].relim()
                self.resist_axes[channel].autoscale_view()
        
        return tuple(self.resist_lines[ch] for ch in channels)

    def update_bipolar_raw_plots(self, frame):
        """Update bipolar raw plots for FuncAnimation on EEGFrame."""
        metrics = ['attention', 'relaxation', 'alpha', 'beta']
        if not self.is_collecting['emotions_bipolar_raw']:
            return tuple(self.bipolar_raw_lines[m] for m in metrics)
        
        for metric in metrics:
            timestamps = list(self.controller.deques['emotions_bipolar'][metric]['raw']['timestamps'])
            values = list(self.controller.deques['emotions_bipolar'][metric]['raw']['values'])

            
            if timestamps and values:
                relative_times = [t - timestamps[0] for t in timestamps]
                self.bipolar_raw_lines[metric].set_data(relative_times, values)
                self.bipolar_raw_axes[metric].relim()
                self.bipolar_raw_axes[metric].autoscale_view()
        
        return tuple(self.bipolar_raw_lines[m] for m in metrics)

    def update_bipolar_percent_plots(self, frame):
        """Update bipolar percent plots for FuncAnimation on EEGFrame."""
        metrics = ['attention', 'relaxation', 'alpha', 'beta']
        if not self.is_collecting['emotions_bipolar_percent']:
            return tuple(self.bipolar_percent_lines[m] for m in metrics)
        
        for metric in metrics:
            timestamps = list(self.controller.deques['emotions_bipolar'][metric]['percent']['timestamps'])
            values = list(self.controller.deques['emotions_bipolar'][metric]['percent']['values'])

            if timestamps and values:
                relative_times = [t - timestamps[0] for t in timestamps]
                self.bipolar_percent_lines[metric].set_data(relative_times, values)
                self.bipolar_percent_axes[metric].relim()
                self.bipolar_percent_axes[metric].autoscale_view()
        
        return tuple(self.bipolar_percent_lines[m] for m in metrics)
    
    def display_calibration_window(self):
        self.calibration_popup = ttk.Window(themename="darkly")
        self.calibration_popup.title("Calibration")
        self.calibration_popup.geometry("300x200")
        self.calibration_progress_bar = ttk.Progressbar(self.calibration_popup, orient=HORIZONTAL, style="danger.Horizontal.TProgressbar")
        self.calibration_progress_bar.pack()

        # Start updating without a cross-thread call
        self.update_calibration_label()

    def update_calibration_label(self):
        # Update the progress bar value on the main thread
        self.calibration_progress_bar.configure(value=self.controller.bipolar_calibration_progress)
        if not self.controller.bipolar_is_calibrated:
            # Schedule the next update after 100ms
            self.calibration_progress_bar.after(100, self.update_calibration_label)
        else:
            self.calibration_popup.destroy()

    def toggle_collection(self, data_type):
        if not self.is_collecting[data_type]:
            self.control_buttons[data_type].configure(
                text=f"Stop {data_type.replace('_', ' ').title()}",
                style="danger.TButton"
            )
            self.is_collecting[data_type] = True
            if data_type == 'resist':
                self.controller.start_resist_collection()
                self.anim = FuncAnimation(self.resist_canvas.figure, self.update_resist_plots, interval=100, blit=False)
                self.resist_canvas.draw()
            elif data_type == 'emotions_bipolar_raw':
                self.controller.start_emotions_bipolar_collection()
                self.display_calibration_window()
                self.anim = FuncAnimation(self.bipolar_raw_canvas.figure, self.update_bipolar_raw_plots, interval=100, blit=False)
                self.bipolar_raw_canvas.draw()
            elif data_type == 'emotions_bipolar_percent':
                self.controller.start_emotions_bipolar_collection()
                self.display_calibration_window()
                self.anim = FuncAnimation(self.bipolar_percent_canvas.figure, self.update_bipolar_percent_plots, interval=100, blit=False)
                self.bipolar_percent_canvas.draw()
            else:
                self.controller.start_signal_collection()
                self.anim = FuncAnimation(self.signal_canvas.figure, self.update_signal_plots, interval=100, blit=False)
                self.signal_canvas.draw()
            
        else:
            # Stop collection
            self.controller.stop_collection()
            if self.anim:
                self.anim.event_source.stop()
            self.is_collecting[data_type] = False
            # Wait for the thread to finish
            self.control_buttons[data_type].configure(
                text=f"Start {data_type.replace('_', ' ').title()}",
                style="success.TButton"
            )

if __name__ == "__main__":
    visualizer = Visualizer()
    visualizer.run()