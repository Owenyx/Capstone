
'''Notes from Owen:'''
# This is a prototype for the EEG visualizer, mainly for testing my Controller class and learning the other libraries.
# It was all made by AI, and there are a ton of comments I got it to add for learning these libraries.
# It uses ttkbootstrap for the GUI, matplotlib for the plots, and my Controller class to manage the data.


# ttkbootstrap is a themed version of tkinter's ttk widgets
# It provides modern-looking widgets with built-in themes
import ttkbootstrap as ttk
from ttkbootstrap.constants import *  # Import constants like LEFT, RIGHT, BOTH, etc.

# matplotlib is a plotting library for creating static, animated, and interactive visualizations
import matplotlib.pyplot as plt
# FigureCanvasTkAgg allows embedding matplotlib plots in tkinter windows
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# Figure is the top-level container for all plot elements
from matplotlib.figure import Figure
import numpy as np
from Controller import Controller
from threading import Thread
import time

class EEGGUI:
    def __init__(self):
        # Create the main window using ttkbootstrap
        # themename can be: cosmo, flatly, litera, minty, lumen, sandstone, yeti, pulse, united, darkly, superhero
        self.root = ttk.Window(themename="darkly")
        self.root.title("EEG Data Visualizer")
        self.root.geometry("1200x800")  # Set initial window size

        # Initialize our Controller class for EEG data
        self.controller = Controller()

        # Create the main container frame
        # ttk.Frame is a container widget that can hold other widgets
        self.main_frame = ttk.Frame(self.root)
        # pack() is a geometry manager that organizes widgets in blocks
        # fill=BOTH means the frame will expand both horizontally and vertically
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Create control panel with buttons
        self.create_control_panel()

        # Create notebook (tabbed interface) for different data views
        # ttk.Notebook creates a tabbed interface where each tab can contain different widgets
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=BOTH, expand=True, pady=(10, 0))

        # Create different tabs for various data visualizations
        self.create_signal_tab()
        self.create_resistance_tab()
        self.create_emotions_bipolar_tab()
        self.create_emotions_monopolar_tab()
        self.create_spectrum_tab()

        # Initialize flags for tracking data collection status
        self.is_collecting = {
            'signal': False,
            'resist': False,
            'emotions_bipolar': False,
            'emotions_monopolar': False,
            'spectrum': False
        }
        # Dictionary to store plotting threads
        self.plot_threads = {}

    def create_control_panel(self):
        """Creates the control panel with buttons"""
        # LabelFrame is a frame with a label/title
        control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding=10)
        control_frame.pack(fill=X, pady=(0, 10))  # X means fill horizontally only

        # Create connect button with primary style (blue in most themes)
        self.connect_btn = ttk.Button(
            control_frame, 
            text="Connect to Device", 
            command=self.connect_device,
            style="primary.TButton"  # ttkbootstrap style - primary is usually blue
        )
        self.connect_btn.pack(side=LEFT, padx=5)

        # Create collection buttons for each data type
        self.collection_buttons = {}
        for data_type in ['signal', 'resist', 'emotions_bipolar', 'emotions_monopolar', 'spectrum']:
            # Create button with success style (green in most themes)
            btn = ttk.Button(
                control_frame,
                text=f"Start {data_type.replace('_', ' ').title()}",
                # Using lambda to pass parameter to callback function
                command=lambda dt=data_type: self.toggle_collection(dt),
                style="success.TButton"
            )
            btn.pack(side=LEFT, padx=5)
            btn.configure(state=DISABLED)  # Initially disabled until device is connected
            self.collection_buttons[data_type] = btn

    def create_signal_tab(self):
        """Creates the signal data tab with matplotlib plots"""
        signal_frame = ttk.Frame(self.notebook)
        self.notebook.add(signal_frame, text="Signal")

        # Create a matplotlib figure to hold the plots
        # figsize specifies width and height in inches
        fig = Figure(figsize=(12, 8))
        
        # Create 4 subplots in a 2x2 grid (221 means 2x2 grid, first position)
        self.signal_axes = {
            'O1': fig.add_subplot(221),  # Top left
            'O2': fig.add_subplot(222),  # Top right
            'T3': fig.add_subplot(223),  # Bottom left
            'T4': fig.add_subplot(224)   # Bottom right
        }

        # Initialize empty line plots for each channel
        self.signal_lines = {}
        for channel, ax in self.signal_axes.items():
            ax.set_title(f'Channel {channel}')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Amplitude')
            # plot returns a tuple, we only need the first element (the line object)
            self.signal_lines[channel], = ax.plot([], [])

        # Create canvas to display the matplotlib figure in tkinter
        canvas = FigureCanvasTkAgg(fig, master=signal_frame)
        canvas.draw()  # Initial draw of the empty plots
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        self.signal_canvas = canvas

    def create_resistance_tab(self):
        """Creates the resistance data tab"""
        resist_frame = ttk.Frame(self.notebook)
        self.notebook.add(resist_frame, text="Resistance")

        fig = Figure(figsize=(12, 8))
        self.resist_axes = {
            'O1': fig.add_subplot(221),
            'O2': fig.add_subplot(222),
            'T3': fig.add_subplot(223),
            'T4': fig.add_subplot(224)
        }

        self.resist_lines = {}
        for channel, ax in self.resist_axes.items():
            ax.set_title(f'Channel {channel} Resistance')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Resistance (kΩ)')
            self.resist_lines[channel], = ax.plot([], [])

        canvas = FigureCanvasTkAgg(fig, master=resist_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        self.resist_canvas = canvas

    def create_emotions_bipolar_tab(self):
        """Creates the bipolar emotions tab"""
        bipolar_frame = ttk.Frame(self.notebook)
        self.notebook.add(bipolar_frame, text="Emotions (Bipolar)")

        fig = Figure(figsize=(12, 8))
        self.bipolar_axes = {
            'attention': fig.add_subplot(221),
            'relaxation': fig.add_subplot(222),
            'alpha': fig.add_subplot(223),
            'beta': fig.add_subplot(224)
        }

        self.bipolar_lines = {}
        for metric, ax in self.bipolar_axes.items():
            ax.set_title(f'{metric.title()}')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Value')
            # Create two lines for raw and percent values
            self.bipolar_lines[metric] = {
                'raw': ax.plot([], [], label='Raw')[0],
                'percent': ax.plot([], [], label='Percent')[0]
            }
            ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=bipolar_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        self.bipolar_canvas = canvas

    def create_emotions_monopolar_tab(self):
        """Creates the monopolar emotions tab with channel selection"""
        monopolar_frame = ttk.Frame(self.notebook)
        self.notebook.add(monopolar_frame, text="Emotions (Monopolar)")

        # Create channel selector
        channel_frame = ttk.Frame(monopolar_frame)
        channel_frame.pack(fill=X)
        ttk.Label(channel_frame, text="Channel:").pack(side=LEFT, padx=5)
        self.monopolar_channel = ttk.StringVar(value='O1')
        channel_cb = ttk.Combobox(channel_frame, textvariable=self.monopolar_channel)
        channel_cb['values'] = ('O1', 'O2', 'T3', 'T4')
        channel_cb.pack(side=LEFT, padx=5)
        channel_cb.bind('<<ComboboxSelected>>', self.update_monopolar_display)

        # Create plots
        fig = Figure(figsize=(12, 8))
        self.monopolar_axes = {
            'attention': fig.add_subplot(221),
            'relaxation': fig.add_subplot(222),
            'alpha': fig.add_subplot(223),
            'beta': fig.add_subplot(224)
        }

        self.monopolar_lines = {}
        for metric, ax in self.monopolar_axes.items():
            ax.set_title(f'{metric.title()}')
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('Value')
            self.monopolar_lines[metric] = {
                'raw': ax.plot([], [], label='Raw')[0],
                'percent': ax.plot([], [], label='Percent')[0]
            }
            ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=monopolar_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        self.monopolar_canvas = canvas

    def create_spectrum_tab(self):
        """Creates the spectrum data tab"""
        spectrum_frame = ttk.Frame(self.notebook)
        self.notebook.add(spectrum_frame, text="Spectrum")

        fig = Figure(figsize=(12, 8))
        self.spectrum_axes = {
            'O1': fig.add_subplot(221),
            'O2': fig.add_subplot(222),
            'T3': fig.add_subplot(223),
            'T4': fig.add_subplot(224)
        }

        self.spectrum_lines = {}
        for channel, ax in self.spectrum_axes.items():
            ax.set_title(f'Channel {channel} Spectrum')
            ax.set_xlabel('Frequency (Hz)')
            ax.set_ylabel('Amplitude')
            self.spectrum_lines[channel], = ax.plot([], [])

        canvas = FigureCanvasTkAgg(fig, master=spectrum_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True)
        self.spectrum_canvas = canvas

    def connect_device(self):
        """Handles device connection"""
        if self.controller.find_and_connect():
            self.connect_btn.configure(state=DISABLED)
            for btn in self.collection_buttons.values():
                btn.configure(state=NORMAL)
            ttk.MessageBox.show_info(
                title="Success", 
                message="Device connected successfully!"
            )
        else:
            ttk.MessageBox.show_error(
                title="Error", 
                message="Failed to connect to device"
            )

    def toggle_collection(self, data_type):
        """Toggles data collection for the specified type"""
        if not self.is_collecting[data_type]:
            # Start collection
            getattr(self.controller, f'start_{data_type}_collection')()
            self.is_collecting[data_type] = True
            self.collection_buttons[data_type].configure(
                text=f"Stop {data_type.replace('_', ' ').title()}", 
                style="danger.TButton"
            )
            
            # Start the plotting thread
            self.plot_threads[data_type] = Thread(
                target=getattr(self, f'update_{data_type}_plots'),
                daemon=True
            )
            self.plot_threads[data_type].start()
        else:
            # Stop collection
            getattr(self.controller, f'stop_{data_type}_collection')()
            self.is_collecting[data_type] = False
            self.collection_buttons[data_type].configure(
                text=f"Start {data_type.replace('_', ' ').title()}", 
                style="success.TButton"
            )

    def update_signal_plots(self):
        """Updates the signal plots with new data"""
        while self.is_collecting['signal']:
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

            # Redraw the canvas with the new data
            # draw_idle() is more efficient than draw() for animations
            self.signal_canvas.draw_idle()
            time.sleep(0.1)  # Small delay to prevent excessive updates

    def update_resist_plots(self):
        """Updates the resistance plots"""
        while self.is_collecting['resist']:
            for channel in ['O1', 'O2', 'T3', 'T4']:
                timestamps = list(self.controller.deques['resist'][channel]['timestamps'])
                values = list(self.controller.deques['resist'][channel]['values'])

                if timestamps and values:
                    relative_times = [t - timestamps[0] for t in timestamps]
                    self.resist_lines[channel].set_data(relative_times, values)
                    self.resist_axes[channel].relim()
                    self.resist_axes[channel].autoscale_view()

            self.resist_canvas.draw_idle()
            time.sleep(0.1)

    def update_emotions_bipolar_plots(self):
        """Updates the bipolar emotions plots"""
        while self.is_collecting['emotions_bipolar']:
            for metric in ['attention', 'relaxation', 'alpha', 'beta']:
                timestamps_raw = list(self.controller.deques['emotions_bipolar'][metric]['raw']['timestamps'])
                values_raw = list(self.controller.deques['emotions_bipolar'][metric]['raw']['values'])
                timestamps_percent = list(self.controller.deques['emotions_bipolar'][metric]['percent']['timestamps'])
                values_percent = list(self.controller.deques['emotions_bipolar'][metric]['percent']['values'])

                if timestamps_raw and values_raw:
                    relative_times = [t - timestamps_raw[0] for t in timestamps_raw]
                    self.bipolar_lines[metric]['raw'].set_data(relative_times, values_raw)

                if timestamps_percent and values_percent:
                    relative_times = [t - timestamps_percent[0] for t in timestamps_percent]
                    self.bipolar_lines[metric]['percent'].set_data(relative_times, values_percent)

                self.bipolar_axes[metric].relim()
                self.bipolar_axes[metric].autoscale_view()

            self.bipolar_canvas.draw_idle()
            time.sleep(0.1)

    def update_monopolar_display(self, event=None):
        """Updates the monopolar display when channel is changed"""
        # This method will be called when the channel combobox selection changes
        pass

    def update_emotions_monopolar_plots(self):
        """Updates the monopolar emotions plots"""
        while self.is_collecting['emotions_monopolar']:
            channel = self.monopolar_channel.get()
            for metric in ['attention', 'relaxation', 'alpha', 'beta']:
                timestamps_raw = list(self.controller.deques['emotions_monopolar'][channel][metric]['raw']['timestamps'])
                values_raw = list(self.controller.deques['emotions_monopolar'][channel][metric]['raw']['values'])
                timestamps_percent = list(self.controller.deques['emotions_monopolar'][channel][metric]['percent']['timestamps'])
                values_percent = list(self.controller.deques['emotions_monopolar'][channel][metric]['percent']['values'])

                if timestamps_raw and values_raw:
                    relative_times = [t - timestamps_raw[0] for t in timestamps_raw]
                    self.monopolar_lines[metric]['raw'].set_data(relative_times, values_raw)

                if timestamps_percent and values_percent:
                    relative_times = [t - timestamps_percent[0] for t in timestamps_percent]
                    self.monopolar_lines[metric]['percent'].set_data(relative_times, values_percent)

                self.monopolar_axes[metric].relim()
                self.monopolar_axes[metric].autoscale_view()

            self.monopolar_canvas.draw_idle()
            time.sleep(0.1)

    def update_spectrum_plots(self):
        """Updates the spectrum plots"""
        while self.is_collecting['spectrum']:
            for channel in ['O1', 'O2', 'T3', 'T4']:
                timestamps = list(self.controller.deques['spectrum'][channel]['timestamps'])
                values = list(self.controller.deques['spectrum'][channel]['values'])

                if timestamps and values:
                    # For spectrum, we'll just plot the most recent FFT
                    if values:
                        latest_spectrum = values[-1]
                        frequencies = np.linspace(0, 100, len(latest_spectrum))  # Adjust frequency range as needed
                        self.spectrum_lines[channel].set_data(frequencies, latest_spectrum)
                        self.spectrum_axes[channel].relim()
                        self.spectrum_axes[channel].autoscale_view()

            self.spectrum_canvas.draw_idle()
            time.sleep(0.1)

    def run(self):
        """Starts the GUI main loop"""
        self.root.mainloop()

if __name__ == "__main__":
    app = EEGGUI()
    app.run()

