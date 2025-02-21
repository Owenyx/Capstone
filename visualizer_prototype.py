import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from Controller import Controller
from HEG_Controller import HEGController
from threading import Thread
import time
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt

# main visualizer class for the entire application
class Visualizer:
    def __init__(self):
        # controllers for the heg and eeg
        self.heg_controller = HEGController()
        self.eeg_controller = Controller()
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
        for F in (HomeFrame, HEGFrame, EEGFrame, ColorTrainingFrame):
            frame = F(self.main_frame, self)
            self.frames[F] = frame
            frame.pack(fill='both', expand=True)

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

    # fix to hold the connection
    def connect_device(self, calling_frame):
        Thread(target=self.connect_eeg, daemon=True, args=(calling_frame,)).start()

    # fix this so that the buttons are not here
    def connect_eeg(self, calling_frame):
        """Handles device connection"""
        # use the controller to find and connect to the device
        if self.eeg_controller.find_and_connect():
            self.eeg_connected = True
            calling_frame.connect_btn.configure(state=DISABLED)
            for btn in calling_frame.control_buttons.values():
                btn.configure(state=NORMAL)
            print("EEG device connected successfully!")
        else:
            print("Failed to connect to EEG device")

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

        color_button = ttk.Button(center_frame, text="Color Training", command=lambda: visualizer.show_frame(ColorTrainingFrame))
        color_button.pack(pady=10)


class ColorTrainingFrame(ttk.Frame):
    def __init__(self, parent, visualizer):
        ttk.Frame.__init__(self, parent)
        self.visualizer = visualizer
        self.heg_controller = visualizer.heg_controller
        self.eeg_controller = visualizer.eeg_controller

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.create_control_panel()

    def create_control_panel(self):
        control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding=10)
        control_frame.pack(fill=X, pady=(0, 10))

        self.connect_btn = ttk.Button(
            control_frame,
            text="Connect to Device",
            command=lambda: self.visualizer.connect_device(self),
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
            self.start_EEG_training_button.configure(state=NORMAL)

        self.start_HEG_training_button = ttk.Button(control_frame, text="Start HEG Training", command=self.start_HEG_training)
        self.start_HEG_training_button.pack(side=LEFT, padx=5)

        self.back_button = ttk.Button(
            control_frame,
            text="Back to Home",
            command=lambda: self.visualizer.show_frame(HomeFrame),
            style="primary.TButton"
        )
        self.back_button.pack(side=LEFT, padx=5)

    def start_EEG_training(self):
        print("Starting EEG Training")
        # Create a new full-screen window for color training
        training_window = ttk.Toplevel(self.visualizer.root)
        training_window.attributes("-fullscreen", True)
        
        # Bind Escape key to cancel the training sequence
        training_window.bind("<Escape>", lambda e: training_window.destroy())
        
        # Define the sequence of (color, duration in milliseconds)
        color_steps = [
            ("gray", 30000),  # Gray for 30 seconds
            ("violet", 10000),  # Blue for 10 seconds
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

                # start collecting 
                if color == "gray":
                    total_duration = duration + color_steps[index + 1][1]
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
        self.eeg_controller.stop_signal_collection()
        directory = f"color_logs/signal_{color}"
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
        # self.create_emotions_bipolar_tab()
        # self.create_emotions_monopolar_tab()
        # self.create_spectrum_tab()
        
        # Initialize collection flags
        self.is_collecting = {
            'signal': False,
            'resist': False,
            'emotions_bipolar': False,
            'emotions_monopolar': False,
            'spectrum': False
        }
        self.plot_threads = {}

    def create_control_panel(self):
        """Creates the control panel with buttons"""
        control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding=10)
        control_frame.pack(fill=X, pady=(0, 10))

        self.connect_btn = ttk.Button(
            control_frame,
            text="Connect to Device",
            command=lambda: self.visualizer.connect_device(self),
            style="primary.TButton"
        )
        self.connect_btn.pack(side=LEFT, padx=5)

        if self.visualizer.eeg_connected:
            self.connect_btn.configure(state=DISABLED)

        self.control_buttons = {}
        for data_type in ['signal', 'resist', 'emotions_bipolar', 'emotions_monopolar', 'spectrum']:
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

    def create_data_tab(self, notebook, tab_title, ax_title_func, y_label, axes_attr_name, lines_attr_name, canvas_attr_name):

        frame = ttk.Frame(notebook)
        notebook.add(frame, text=tab_title)
    
        fig = Figure(figsize=(12, 8))
        axes_dict = {}
        lines_dict = {}
        channels = ['O1', 'O2', 'T3', 'T4']
        positions = [221, 222, 223, 224]
        
        for pos, channel in zip(positions, channels):
            ax = fig.add_subplot(pos)
            ax.set_title(ax_title_func(channel))
            ax.set_xlabel("Time (s)")
            ax.set_ylabel(y_label)
            axes_dict[channel] = ax
            line, = ax.plot([], [])
            lines_dict[channel] = line

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        
        # this is used as a string for the attribute name is passed
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


    # these windows need to be re-implemented but signal and resistance work

    # def create_emotions_bipolar_tab(self):
    #     """Creates the bipolar emotions tab"""
    #     bipolar_frame = ttk.Frame(self.notebook)
    #     self.notebook.add(bipolar_frame, text="Emotions (Bipolar)")

    #     fig = Figure(figsize=(12, 8))
    #     self.bipolar_axes = {
    #         'attention': fig.add_subplot(221),
    #         'relaxation': fig.add_subplot(222),
    #         'alpha': fig.add_subplot(223),
    #         'beta': fig.add_subplot(224)
    #     }

    #     self.bipolar_lines = {}
    #     for metric, ax in self.bipolar_axes.items():
    #         ax.set_title(f'{metric.title()}')
    #         ax.set_xlabel('Time (s)')
    #         ax.set_ylabel('Value')
    #         # Create two lines for raw and percent values
    #         self.bipolar_lines[metric] = {
    #             'raw': ax.plot([], [], label='Raw')[0],
    #             'percent': ax.plot([], [], label='Percent')[0]
    #         }
    #         ax.legend()

    #     canvas = FigureCanvasTkAgg(fig, master=bipolar_frame)
    #     canvas.draw()
    #     canvas.get_tk_widget().pack(fill=BOTH, expand=True)
    #     self.bipolar_canvas = canvas

    # def create_emotions_monopolar_tab(self):
    #     """Creates the monopolar emotions tab with channel selection"""
    #     monopolar_frame = ttk.Frame(self.notebook)
    #     self.notebook.add(monopolar_frame, text="Emotions (Monopolar)")

    #     # Create channel selector
    #     channel_frame = ttk.Frame(monopolar_frame)
    #     channel_frame.pack(fill=X)
    #     ttk.Label(channel_frame, text="Channel:").pack(side=LEFT, padx=5)
    #     self.monopolar_channel = ttk.StringVar(value='O1')
    #     channel_cb = ttk.Combobox(channel_frame, textvariable=self.monopolar_channel)
    #     channel_cb['values'] = ('O1', 'O2', 'T3', 'T4')
    #     channel_cb.pack(side=LEFT, padx=5)
    #     channel_cb.bind('<<ComboboxSelected>>', self.update_monopolar_display)

    #     # Create plots
    #     fig = Figure(figsize=(12, 8))
    #     self.monopolar_axes = {
    #         'attention': fig.add_subplot(221),
    #         'relaxation': fig.add_subplot(222),
    #         'alpha': fig.add_subplot(223),
    #         'beta': fig.add_subplot(224)
    #     }

    #     self.monopolar_lines = {}
    #     for metric, ax in self.monopolar_axes.items():
    #         ax.set_title(f'{metric.title()}')
    #         ax.set_xlabel('Time (s)')
    #         ax.set_ylabel('Value')
    #         self.monopolar_lines[metric] = {
    #             'raw': ax.plot([], [], label='Raw')[0],
    #             'percent': ax.plot([], [], label='Percent')[0]
    #         }
    #         ax.legend()

    #     canvas = FigureCanvasTkAgg(fig, master=monopolar_frame)
    #     canvas.draw()
    #     canvas.get_tk_widget().pack(fill=BOTH, expand=True)
    #     self.monopolar_canvas = canvas

    # def create_spectrum_tab(self):
    #     """Creates the spectrum data tab"""
    #     spectrum_frame = ttk.Frame(self.notebook)
    #     self.notebook.add(spectrum_frame, text="Spectrum")

    #     fig = Figure(figsize=(12, 8))
    #     self.spectrum_axes = {
    #         'O1': fig.add_subplot(221),
    #         'O2': fig.add_subplot(222),
    #         'T3': fig.add_subplot(223),
    #         'T4': fig.add_subplot(224)
    #     }

    #     self.spectrum_lines = {}
    #     for channel, ax in self.spectrum_axes.items():
    #         ax.set_title(f'Channel {channel} Spectrum')
    #         ax.set_xlabel('Frequency (Hz)')
    #         ax.set_ylabel('Amplitude')
    #         self.spectrum_lines[channel], = ax.plot([], [])

    #     canvas = FigureCanvasTkAgg(fig, master=spectrum_frame)
    #     canvas.draw()
    #     canvas.get_tk_widget().pack(fill=BOTH, expand=True)
    #     self.spectrum_canvas = canvas
    
    def update_signal_plots(self, frame):
        """Update signal plots for FuncAnimation on EEGFrame."""
        if not self.is_collecting['signal']:
            # Return the current line objects if collection is stopped
            return tuple(self.signal_lines[ch] for ch in ['O1', 'O2', 'T3', 'T4'])
        
        for channel in ['O1', 'O2', 'T3', 'T4']:
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
        return tuple(self.signal_lines[ch] for ch in ['O1', 'O2', 'T3', 'T4'])

    def update_resist_plots(self, frame):
        """Update resistance plots for FuncAnimation on EEGFrame."""
        if not self.is_collecting['resist']:
            return tuple(self.resist_lines[ch] for ch in ['O1', 'O2', 'T3', 'T4'])
        
        for channel in ['O1', 'O2', 'T3', 'T4']:
            timestamps = list(self.controller.deques['resist'][channel]['timestamps'])
            values = list(self.controller.deques['resist'][channel]['values'])
            
            if timestamps and values:
                relative_times = [t - timestamps[0] for t in timestamps]
                self.resist_lines[channel].set_data(relative_times, values)
                self.resist_axes[channel].relim()
                self.resist_axes[channel].autoscale_view()
        
        return tuple(self.resist_lines[ch] for ch in ['O1', 'O2', 'T3', 'T4'])


    # these windows need to be re-implemented but signal and resistance work
    # def update_emotions_bipolar_plots(self):
    #     """Updates the bipolar emotions plots"""
    #     while self.is_collecting['emotions_bipolar']:
    #         for metric in ['attention', 'relaxation', 'alpha', 'beta']:
    #             timestamps_raw = list(self.controller.deques['emotions_bipolar'][metric]['raw']['timestamps'])
    #             values_raw = list(self.controller.deques['emotions_bipolar'][metric]['raw']['values'])
    #             timestamps_percent = list(self.controller.deques['emotions_bipolar'][metric]['percent']['timestamps'])
    #             values_percent = list(self.controller.deques['emotions_bipolar'][metric]['percent']['values'])

    #             if timestamps_raw and values_raw:
    #                 relative_times = [t - timestamps_raw[0] for t in timestamps_raw]
    #                 self.bipolar_lines[metric]['raw'].set_data(relative_times, values_raw)

    #             if timestamps_percent and values_percent:
    #                 relative_times = [t - timestamps_percent[0] for t in timestamps_percent]
    #                 self.bipolar_lines[metric]['percent'].set_data(relative_times, values_percent)

    #             self.bipolar_axes[metric].relim()
    #             self.bipolar_axes[metric].autoscale_view()

    #         self.bipolar_canvas.draw_idle()
    #         time.sleep(0.1)

    # def update_monopolar_display(self, event=None):
    #     """Updates the monopolar display when channel is changed"""
    #     # This method will be called when the channel combobox selection changes
    #     pass

    # def update_emotions_monopolar_plots(self):
    #     """Updates the monopolar emotions plots"""
    #     while self.is_collecting['emotions_monopolar']:
    #         channel = self.monopolar_channel.get()
    #         for metric in ['attention', 'relaxation', 'alpha', 'beta']:
    #             timestamps_raw = list(self.controller.deques['emotions_monopolar'][channel][metric]['raw']['timestamps'])
    #             values_raw = list(self.controller.deques['emotions_monopolar'][channel][metric]['raw']['values'])
    #             timestamps_percent = list(self.controller.deques['emotions_monopolar'][channel][metric]['percent']['timestamps'])
    #             values_percent = list(self.controller.deques['emotions_monopolar'][channel][metric]['percent']['values'])

    #             if timestamps_raw and values_raw:
    #                 relative_times = [t - timestamps_raw[0] for t in timestamps_raw]
    #                 self.monopolar_lines[metric]['raw'].set_data(relative_times, values_raw)

    #             if timestamps_percent and values_percent:
    #                 relative_times = [t - timestamps_percent[0] for t in timestamps_percent]
    #                 self.monopolar_lines[metric]['percent'].set_data(relative_times, values_percent)

    #             self.monopolar_axes[metric].relim()
    #             self.monopolar_axes[metric].autoscale_view()

    #         self.monopolar_canvas.draw_idle()
    #         time.sleep(0.1)

    # def update_spectrum_plots(self):
    #     """Updates the spectrum plots"""
    #     while self.is_collecting['spectrum']:
    #         for channel in ['O1', 'O2', 'T3', 'T4']:
    #             timestamps = list(self.controller.deques['spectrum'][channel]['timestamps'])
    #             values = list(self.controller.deques['spectrum'][channel]['values'])

    #             if timestamps and values:
    #                 # For spectrum, we'll just plot the most recent FFT
    #                 if values:
    #                     latest_spectrum = values[-1]
    #                     frequencies = np.linspace(0, 100, len(latest_spectrum))  # Adjust frequency range as needed
    #                     self.spectrum_lines[channel].set_data(frequencies, latest_spectrum)
    #                     self.spectrum_axes[channel].relim()
    #                     self.spectrum_axes[channel].autoscale_view()

    #         self.spectrum_canvas.draw_idle()
    #         time.sleep(0.1)

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
            else:
                self.controller.start_signal_collection()
                self.anim = FuncAnimation(self.signal_canvas.figure, self.update_signal_plots, interval=100, blit=False)
                self.signal_canvas.draw()
            
        else:
            # Stop collection
            if data_type == 'resist':
                self.controller.stop_resist_collection()
            else:
                self.controller.stop_signal_collection()
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