import ttkbootstrap as ttk
import tkinter as tk
from ttkbootstrap.constants import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from EEG_Controller import Controller as EEGController
from HEG_Controller import HEGController
from threading import Thread
import time, os
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import tkinter.filedialog as fd
from Macro.Macro import Macro
from PIL import Image, ImageTk
from create_color_predictor import ColorPredictor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, ConfusionMatrixDisplay
import pandas as pd
import tkinter.font as tkFont

plt.style.use("seaborn-v0_8-dark")
plt.rcParams['axes.edgecolor'] = 'black'
plt.rcParams['axes.linewidth'] = 1.0


# main visualizer class for the entire application
class Visualizer:
    def __init__(self):
        # controllers for the heg and eeg
        self.heg_controller = HEGController()
        self.eeg_controller = EEGController()
        self.eeg_connected = False

        # configure the root window in windowed full screen mode
        self.root = ttk.Window(themename="darkly")
        self.root.iconbitmap("Window Icons/neurofeedback.ico")
        self.root.title("Neurofeedback Visualizer")
        self.root.state("zoomed")

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(family="Helvetica", size=11)
        
        # create the main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True)

        # dictionary to store all frames
        self.frames = {}

        # create and store all frames
        # if you add a new frame, you need to add it here
        for F in (HomeFrame, HEGFrame, EEGFrame, ColorTrainingFrame, ColorPredictorFrame, MacroFrame):
            frame = F(self.main_frame, self)
            self.frames[F] = frame
            frame.pack(fill='both', expand=True)
            
        self.eeg_frames = [EEGFrame, ColorTrainingFrame, ColorPredictorFrame]

        self.show_frame(HomeFrame)

    def show_frame(self, frame_class):
        """Raises the specified frame to the top"""
        # hide all frames
        for frame in self.frames.values():
            frame.pack_forget()
        # show the selected frame
        frame = self.frames[frame_class]
        frame.pack(fill='both', expand=True)

    def connect_device(self):
        self.connect_popup = ttk.Window(themename="darkly")
        self.connect_popup.title("Device Connection")
        self.connect_popup.geometry("300x100")

        self.connect_label = ttk.Label(self.connect_popup, text="Connecting to device...", anchor="center", background="#222222", foreground="white")
        self.connect_label.pack(expand=True, fill='both')
        Thread(target=self.connect_eeg, daemon=True).start()

    # fix this so that the buttons are not here
    def connect_eeg(self):
        """Handles device connection"""

        # use the controller to find and connect to the device
        if self.eeg_controller.find_and_connect():
            self.eeg_connected = True
            for frame in self.eeg_frames:
                self.frames[frame].device_connected()

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

# create separate classes for each frame
class HomeFrame(ttk.Frame):
    def __init__(self, parent, visualizer):
        ttk.Frame.__init__(self, parent)
        
        # create a container frame that will center our content
        center_frame = ttk.Frame(self)
        center_frame.pack(expand=True)
        
        # frame for the title
        title_frame = ttk.Frame(center_frame)
        title_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=(20, 30))
        
        # app logo
        logo_img = tk.PhotoImage(file="Window Icons/brain.png")
        logo_label = ttk.Label(title_frame, image=logo_img)
        logo_label.image = logo_img
        logo_label.pack(side=TOP, pady=(0, 10))
        
        # app title
        label = ttk.Label(title_frame, text="Neurofeedback Visualizer", 
                          font=("Helvetica", 24, "bold"), foreground="#4dabf7")
        label.pack(side=TOP)
        
        # app subtitle
        subtitle = ttk.Label(title_frame, text="Neurofeedback Visualizer and Brain-Computer Interface Toolkit", 
                           font=("Helvetica", 12), foreground="#adb5bd")
        subtitle.pack(side=TOP, pady=(5, 0))

        # create a container for the buttons
        button_frame = ttk.Frame(center_frame, padding=15)
        button_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        btn_width = 30
        btn_padding = 15
        
        # first row of buttons
        row1_frame = ttk.Frame(button_frame)
        row1_frame.pack(fill=X, pady=(0, btn_padding))
        
        heg_img = tk.PhotoImage(file="Window Icons/red_blood_cells.png")
        heg_button = ttk.Button(row1_frame, text="HEG Visualizer", image=heg_img, 
                               compound="left", command=lambda: visualizer.show_frame(HEGFrame), 
                               width=btn_width, style="info.TButton")
        heg_button.image = heg_img
        heg_button.pack(side=LEFT, padx=(0, btn_padding))
        
        eeg_img = tk.PhotoImage(file="Window Icons/eeg.png")
        eeg_button = ttk.Button(row1_frame, text="EEG Visualizer", image=eeg_img, 
                               compound="left", command=lambda: visualizer.show_frame(EEGFrame), 
                               width=btn_width, style="info.TButton")
        eeg_button.image = eeg_img
        eeg_button.pack(side=LEFT)
        
        # second row of buttons
        row2_frame = ttk.Frame(button_frame)
        row2_frame.pack(fill=X, pady=(0, btn_padding))

        color_training_img = tk.PhotoImage(file="Window Icons/color_training.png")
        color_training_button = ttk.Button(row2_frame, text="Color Training", image=color_training_img, 
                                         compound="left", command=lambda: visualizer.show_frame(ColorTrainingFrame), 
                                         width=btn_width, style="success.TButton")
        color_training_button.image = color_training_img
        color_training_button.pack(side=LEFT, padx=(0, btn_padding))

        color_predictor_img = tk.PhotoImage(file="Window Icons/color_predictor.png")
        color_predictor_button = ttk.Button(row2_frame, text="Color Predictor", image=color_predictor_img, 
                                          compound="left", command=lambda: visualizer.show_frame(ColorPredictorFrame), 
                                          width=btn_width, style="success.TButton")
        color_predictor_button.image = color_predictor_img
        color_predictor_button.pack(side=LEFT)
        
        # third row
        row3_frame = ttk.Frame(button_frame)
        row3_frame.pack(fill=X)
        
        macro_img = tk.PhotoImage(file="Window Icons/macro.png")
        macro_button = ttk.Button(row3_frame, text="Macro", image=macro_img, 
                                compound="left", command=lambda: visualizer.show_frame(MacroFrame), 
                                width=btn_width, style="warning.TButton")
        macro_button.image = macro_img
        macro_button.pack(side=LEFT, padx=(0, btn_padding))

class ColorTrainingFrame(ttk.Frame):
    def __init__(self, parent, visualizer):
        ttk.Frame.__init__(self, parent)
        self.visualizer = visualizer
        self.eeg_controller = visualizer.eeg_controller
        self.save_file_path = None
        self.save_file_name = "Training Data"
        self.training_seconds = 30

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

        self.training_seconds_label = ttk.Label(control_frame, text=f"Training Seconds: ")
        self.training_seconds_label.pack(side=LEFT, padx=5)

        self.training_seconds_entry = ttk.Entry(control_frame)
        self.training_seconds_entry.insert(END, self.training_seconds)
        self.training_seconds_entry.pack(side=LEFT, padx=5)

        self.training_seconds_entry.bind("<FocusOut>", self.update_training_seconds)
        self.training_seconds_entry.bind("<Return>", self.update_training_seconds)

        # update the button to allow selecting a folder instead of a file.
        self.choose_folder_btn = ttk.Button(
            control_frame,
            text="Select Folder",
            command=self.choose_folder,
            style="primary.TButton"
        )
        self.choose_folder_btn.pack(side=LEFT, padx=5)

        # add a label to display the selected folder.
        self.folder_label = ttk.Label(
            control_frame,
            text="None",
            foreground="white"
        )
        self.folder_label.pack(side=LEFT, padx=5)

        self.back_button = ttk.Button(
            control_frame,
            text="Back to Home",
            command=lambda: self.visualizer.show_frame(HomeFrame),
            style="primary.TButton"
        )
        self.back_button.pack(side=LEFT, padx=5)

    def update_training_seconds(self, event):
        if self.training_seconds_entry.get().isdigit():
            self.training_seconds = int(self.training_seconds_entry.get())

    def device_connected(self):
        self.connect_btn.configure(state=DISABLED)
        if self.save_file_path:
            self.start_EEG_training_button.configure(state=NORMAL)

    def choose_folder(self):
        # open a directory chooser dialog so the user can select a folder to save the training data.
        folder_path = fd.askdirectory(
            title="Select Folder to Save Training Data",
            initialdir="."
        )
        if folder_path:
            self.save_file_path = folder_path
            self.folder_label.configure(text=f"Selected folder: {os.path.basename(self.save_file_path)}")
            # self.file_path = os.path.join(self.save_file_path, self.save_file_name)

            # optionally, enable the HEG training button if selecting the folder is required.
            if self.visualizer.eeg_connected:
                self.start_EEG_training_button.configure(state=NORMAL)

    def start_EEG_training(self):
        print("Starting EEG Training")
        self.eeg_controller.storage_time = self.training_seconds
        # create a new full-screen window for color training
        training_window = ttk.Toplevel(self.visualizer.root)
        training_window.attributes("-fullscreen", True)
        
        # bind Escape key to cancel the training sequence
        training_window.bind("<Escape>", lambda e: training_window.destroy())
        
        gray_duration = 30000
        target_color_duration = self.eeg_controller.storage_time * 1000
        
        # define the sequence of (color, duration in milliseconds)
        color_steps = [
            ("gray", gray_duration),
            ("blue", target_color_duration),
            ("gray", gray_duration),
            ("green", target_color_duration),
            ("gray", gray_duration),
            ("red", target_color_duration)
        ]
        
        def run_step(index):
            # check if window still exists (i.e., training has not been canceled)
            if not training_window.winfo_exists():
                return
            if index < len(color_steps):
                color, duration = color_steps[index]                
                training_window.configure(bg=color)

                # start collecting 
                if color == "gray":
                    total_duration = gray_duration + target_color_duration
                    Thread(
                        daemon=True,
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

class ColorPredictorFrame(ttk.Frame):
    def __init__(self, parent, visualizer):
        ttk.Frame.__init__(self, parent)
        self.visualizer = visualizer
        self.eeg_controller = visualizer.eeg_controller
        self.color_predictor = None
        self.folder_path = None

        self.true_labels = []
        self.predicted_labels = []

        self.accuracy = 0

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        self.main_frame.rowconfigure(1, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        self.create_control_panel()
        
        self.is_predicting = False
        self.color = "blue"

        self.color_frame = tk.Frame(self.main_frame, bg=self.color)

        self.statistics_frame = ttk.Frame(self.main_frame)

        self.color_label = ttk.Label(self.statistics_frame, text=f"Prediction: None", font=("TkDefaultFont", 24))
        self.color_label.pack(side=TOP, padx=5, pady=5)

        self.prediction_accuracy_label = ttk.Label(self.statistics_frame, text=f"Accuracy: {self.accuracy:.2f}%", font=("TkDefaultFont", 24))
        self.prediction_accuracy_label.pack(side=TOP, padx=5, pady=5)

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

        self.train_model_btn = ttk.Button(
            control_frame,
            text="Train Model",
            command=lambda: self.train_model(),
            style="primary.TButton"
        )
        self.train_model_btn.pack(side=LEFT, padx=5)

        self.folder_label = ttk.Label(control_frame, text="Training Data Folder: None")
        self.folder_label.pack(side=LEFT, padx=5)
        
        self.control_buttons = {}
        self.start_prediction_button = ttk.Button(control_frame, text="Start Prediction", command=self.toggle_prediction)
        self.start_prediction_button.pack(side=LEFT, padx=5)
        self.start_prediction_button.configure(state=DISABLED)
        self.control_buttons["Prediction"] = self.start_prediction_button
                    
        self.color_buttons = {}
        for color in ["blue", "green", "red"]:
            btn = ttk.Button(
                control_frame,
                text=color.capitalize(),
                command=lambda c=color: self.change_color(c),
                style="primary.TButton"
            )
            btn.configure(state=DISABLED)
            btn.pack(side=LEFT, padx=5)
            self.color_buttons[color] = btn
        
        self.back_button = ttk.Button(
            control_frame,
            text="Back to Home",
            command=lambda: self.visualizer.show_frame(HomeFrame),
            style="primary.TButton"
        )
        self.back_button.pack(side=LEFT, padx=5)

    def device_connected(self):
        self.connect_btn.configure(state=DISABLED)
        if self.folder_path:
            for btn in self.control_buttons.values():
                btn.configure(state=NORMAL)

    def train_model(self):
        print("Training model")
        self.folder_path = fd.askdirectory(
            title="Select Training Data Folder",
            initialdir="."
        )
        # check if the folder has the appropriate subfolders
        if not os.path.exists(os.path.join(self.folder_path, "signal_blue")):
            print("Folder does not contain signal_blue subfolder")
            return
        if not os.path.exists(os.path.join(self.folder_path, "signal_green")):
            print("Folder does not contain signal_green subfolder")
            return
        if not os.path.exists(os.path.join(self.folder_path, "signal_red")):
            print("Folder does not contain signal_red subfolder")
            return
        
        self.training_popup = ttk.Window(themename="darkly")
        self.training_popup.title("Training Model")
        self.training_popup.geometry("600x500")

        self.training_label = ttk.Label(self.training_popup, text="Training model...", anchor="center", background="#222222", foreground="white")
        self.training_label.pack(fill=BOTH, expand=True)

        self.training_thread = Thread(target=self.train_helper, daemon=True)
        self.training_thread.start()
        self.check_training_thread()

        self.folder_label.configure(text=f"Training Data Folder: {os.path.basename(self.folder_path)}")

        if self.visualizer.eeg_connected:
            for btn in self.control_buttons.values():
                btn.configure(state=NORMAL)

    def check_training_thread(self):
        if self.training_thread.is_alive():
            # schedule the check again after 100ms
            self.training_popup.after(100, self.check_training_thread)
        else:
            # training thread has finished
            self.training_label.destroy()

            self.statistics_notebook = ttk.Notebook(self.training_popup)
            self.statistics_notebook.pack(fill=BOTH, expand=True)

            # Statistics tab
            statistics_tab = ttk.Frame(self.statistics_notebook)
            self.statistics_notebook.add(statistics_tab, text="Model Statistics")

            accuracy = accuracy_score(self.y_test, self.y_pred) * 100
            precision = precision_score(self.y_test, self.y_pred, average='macro') * 100
            recall = recall_score(self.y_test, self.y_pred, average='macro') * 100
            f1 = f1_score(self.y_test, self.y_pred, average='macro') * 100            
            
            hist_fig = Figure(figsize=(6, 3), dpi=100)
            hist_ax = hist_fig.add_subplot(111)
            metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score']
            values = [accuracy, precision, recall, f1]
            bars = hist_ax.bar(metrics, values, color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
            for bar in bars:
                height = bar.get_height()
                hist_ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                             f'{height:.1f}%', ha='center', va='bottom')
            hist_ax.set_ylim(0, 105)
            hist_ax.set_ylabel('Percentage (%)')
            hist_ax.set_title('Model Performance Metrics')
            hist_fig.tight_layout()

            hist_canvas = FigureCanvasTkAgg(hist_fig, master=statistics_tab)
            hist_canvas.draw()
            hist_canvas.get_tk_widget().pack(fill=BOTH, expand=True)
            

            # confusion matrix tab
            confusion_matrix_tab = ttk.Frame(self.statistics_notebook)
            disp = ConfusionMatrixDisplay.from_predictions(
                self.y_test,
                self.y_pred,
                display_labels=["blue", "green", "red"],
            )
            fig, ax = plt.subplots()
            disp.plot(ax=ax, colorbar=True, cmap=plt.cm.Blues)
            ax.set_title("Confusion Matrix for Color Prediction")
            
            canvas = FigureCanvasTkAgg(fig, master=confusion_matrix_tab)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=True)
            self.statistics_notebook.add(confusion_matrix_tab, text="Confusion Matrix")

            # alpha waves tab
            alpha_waves_tab = ttk.Frame(self.statistics_notebook)
            self.statistics_notebook.add(alpha_waves_tab, text="Alpha Waves")

            alpha_fig = Figure(figsize=(6, 3), dpi=100)
            alpha_ax = alpha_fig.add_subplot(111)

            data = [self.color_predictor.train_blue_df['O1_alpha'], self.color_predictor.train_blue_df['O2_alpha'],
                    self.color_predictor.train_green_df['O1_alpha'], self.color_predictor.train_green_df['O2_alpha'],
                    self.color_predictor.train_red_df['O1_alpha'], self.color_predictor.train_red_df['O2_alpha']]

            # Create a styled boxplot using patch_artist for custom colors, similar to the histogram style
            box = alpha_ax.boxplot(data, labels=["Blue O1", "Blue O2", "Green O1", "Green O2", "Red O1", "Red O2"],
                                    patch_artist=True)
            box_colors = ['#3498db', '#3498db', '#2ecc71', '#2ecc71', '#e74c3c', '#e74c3c']
            for patch, color in zip(box['boxes'], box_colors):
                patch.set_facecolor(color)
                patch.set_edgecolor('black')
                patch.set_alpha(0.7)
            for whisker in box['whiskers']:
                whisker.set_color('black')
            for cap in box['caps']:
                cap.set_color('black')
            for median in box['medians']:
                median.set_color('yellow')

            alpha_ax.set_title("Alpha Waves", fontsize=12)
            alpha_ax.set_xlabel("Color", fontsize=10)
            alpha_ax.set_ylabel("Alpha Wave", fontsize=10)
            alpha_fig.tight_layout()

            alpha_canvas = FigureCanvasTkAgg(alpha_fig, master=alpha_waves_tab)
            alpha_canvas.draw()
            alpha_canvas.get_tk_widget().pack(fill=BOTH, expand=True)

            # beta waves tab
            beta_waves_tab = ttk.Frame(self.statistics_notebook)
            self.statistics_notebook.add(beta_waves_tab, text="Beta Waves")

            beta_fig = Figure(figsize=(6, 3), dpi=100)
            beta_ax = beta_fig.add_subplot(111)

            data = [self.color_predictor.train_blue_df['O1_beta'], self.color_predictor.train_blue_df['O2_beta'],
                    self.color_predictor.train_green_df['O1_beta'], self.color_predictor.train_green_df['O2_beta'],
                    self.color_predictor.train_red_df['O1_beta'], self.color_predictor.train_red_df['O2_beta']]

            # Create a styled boxplot using patch_artist for custom colors, similar to the histogram style
            box = beta_ax.boxplot(data, labels=["Blue O1", "Blue O2", "Green O1", "Green O2", "Red O1", "Red O2"],
                                    patch_artist=True)
            box_colors = ['#3498db', '#3498db', '#2ecc71', '#2ecc71', '#e74c3c', '#e74c3c']
            for patch, color in zip(box['boxes'], box_colors):
                patch.set_facecolor(color)
                patch.set_edgecolor('black')
                patch.set_alpha(0.7)
            for whisker in box['whiskers']:
                whisker.set_color('black')
            for cap in box['caps']:
                cap.set_color('black')
            for median in box['medians']:
                median.set_color('yellow')

            beta_ax.set_title("Beta Waves", fontsize=12)
            beta_ax.set_xlabel("Color", fontsize=10)
            beta_ax.set_ylabel("Beta Wave", fontsize=10)
            beta_fig.tight_layout()

            beta_canvas = FigureCanvasTkAgg(beta_fig, master=beta_waves_tab)
            beta_canvas.draw()
            beta_canvas.get_tk_widget().pack(fill=BOTH, expand=True)

            # theta waves tab
            theta_waves_tab = ttk.Frame(self.statistics_notebook)
            self.statistics_notebook.add(theta_waves_tab, text="Theta Waves")

            theta_fig = Figure(figsize=(6, 3), dpi=100)
            theta_ax = theta_fig.add_subplot(111)

            data = [self.color_predictor.train_blue_df['O1_theta'], self.color_predictor.train_blue_df['O2_theta'],
                    self.color_predictor.train_green_df['O1_theta'], self.color_predictor.train_green_df['O2_theta'],
                    self.color_predictor.train_red_df['O1_theta'], self.color_predictor.train_red_df['O2_theta']]

            # Create a styled boxplot using patch_artist for custom colors, similar to the histogram style
            box = theta_ax.boxplot(data, labels=["Blue O1", "Blue O2", "Green O1", "Green O2", "Red O1", "Red O2"],
                                    patch_artist=True)
            box_colors = ['#3498db', '#3498db', '#2ecc71', '#2ecc71', '#e74c3c', '#e74c3c']
            for patch, color in zip(box['boxes'], box_colors):
                patch.set_facecolor(color)
                patch.set_edgecolor('black')
                patch.set_alpha(0.7)
            for whisker in box['whiskers']:
                whisker.set_color('black')
            for cap in box['caps']:
                cap.set_color('black')
            for median in box['medians']:
                median.set_color('yellow')

            theta_ax.set_title("Theta Waves", fontsize=12)
            theta_ax.set_xlabel("Color", fontsize=10)
            theta_ax.set_ylabel("Theta Wave", fontsize=10)
            theta_fig.tight_layout()

            theta_canvas = FigureCanvasTkAgg(theta_fig, master=theta_waves_tab)
            theta_canvas.draw()
            theta_canvas.get_tk_widget().pack(fill=BOTH, expand=True)
            
    def train_helper(self):
        self.color_predictor = ColorPredictor(self.folder_path)
        self.model = self.color_predictor.best_model
        self.y_test = self.color_predictor.y_test
        self.y_pred = self.color_predictor.y_pred

    def toggle_prediction(self):
        self.is_predicting = not self.is_predicting
        if self.is_predicting:
            for btn in self.color_buttons.values():
                btn.configure(state=NORMAL)
            
            # configure the row of self.main_frame holding the color_frame to expand.

            self.color_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
            self.color_frame.configure(bg=self.color)

            self.statistics_frame.grid(row=1, column=1, sticky="nsew", padx=(0, 10), pady=(0, 10))

            self.start_prediction_button.configure(text="Stop Prediction", style="danger.TButton")

            self.eeg_controller.start_spectrum_collection()
            
            Thread(target=self.predict_color, daemon=True).start()
        else:
            self.eeg_controller.stop_collection()

            for btn in self.color_buttons.values():
                btn.configure(state=DISABLED)
            
            self.color_frame.grid_forget()
            self.color_label.grid_forget()
            
            self.start_prediction_button.configure(text="Start Prediction", style="primary.TButton")
        
    def predict_color(self):
        while self.is_predicting:
            if len(self.eeg_controller.deques["waves"]["O1"]["alpha"]['percent']["values"]) > 0:
                O1_alpha = self.eeg_controller.deques["waves"]["O1"]["alpha"]['percent']["values"][-1]
                O2_alpha = self.eeg_controller.deques["waves"]["O2"]["alpha"]['percent']["values"][-1]
                O1_beta = self.eeg_controller.deques["waves"]["O1"]["beta"]['percent']["values"][-1]
                O2_beta = self.eeg_controller.deques["waves"]["O2"]["beta"]['percent']["values"][-1]
                O1_theta = self.eeg_controller.deques["waves"]["O1"]["theta"]['percent']["values"][-1]
                O2_theta = self.eeg_controller.deques["waves"]["O2"]["theta"]['percent']["values"][-1]

                test_row = pd.DataFrame({
                    'O1_alpha': [O1_alpha],
                    'O2_alpha': [O2_alpha],
                    'O1_beta': [O1_beta],
                    'O2_beta': [O2_beta],
                    'O1_theta': [O1_theta],
                    'O2_theta': [O2_theta]
                })
                prediction = self.model.predict(test_row)
                
                self.true_labels.append(self.color)
                self.predicted_labels.append(prediction[0])

                self.accuracy = accuracy_score(self.true_labels, self.predicted_labels) * 100
                self.precision = precision_score(self.true_labels, self.predicted_labels, average='macro') * 100
                self.recall = recall_score(self.true_labels, self.predicted_labels, average='macro') * 100
                self.f1_score = f1_score(self.true_labels, self.predicted_labels, average='macro') * 100


                # print(f"Prediction: {prediction[0].capitalize()}")
                # print(f"Accuracy: {self.accuracy:.2f}%")
                self.after(0, lambda: self.color_label.configure(text=f"Prediction: {prediction.capitalize()}"))
                self.after(0, lambda: self.prediction_accuracy_label.configure(text=f"Accuracy: {self.accuracy:.2f}%"))

            time.sleep(0.1)

    def change_color(self, color):
        self.color = color
        if self.is_predicting:
            self.color_frame.configure(bg=color)

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

        # add a label above the graph to display the current reading.
        self.reading_label = ttk.Label(plot_frame, text="Current Reading: N/A", font=("TkDefaultFont", 12))
        self.reading_label.pack(side=TOP, anchor="w", pady=(0, 5))

        self.fig = Figure(figsize=(12, 8))
        self.plot = self.fig.add_subplot()

        # create a persistent line object (initially empty)
        self.line, = self.plot.plot([], [])

        # set axis labels and tick settings
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
        
        # retrieve data from deques in the controller
        x = list(self.controller.readings["timestamp"])
        y = list(self.controller.readings["reading"])
        
        # convert y-values from string to float
        try:
            y = [float(val) for val in y]
        except ValueError:
            # if conversion fails, skip updating this frame.
            return self.line,
        
        # update the current reading label with the latest reading value.
        if y:
            current_reading = y[-1]
            self.reading_label.configure(text=f"Current Reading: {current_reading}")
        else:
            self.reading_label.configure(text="Current Reading: N/A")
        
        # update the persistent line's data instead of clearing the plot
        self.line.set_data(x, y)
        # update the axis view limits (autoscale the x-axis; y-axis remains fixed)
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
        
        # initialize Controller for EEG data
        self.controller = visualizer.eeg_controller

        self.anim_list = []
        
        # everything sits on this main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # control panel is the buttons at the top of the window
        self.create_control_panel()
        
        # use a notebook to switch between different sets of plots
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=BOTH, expand=True)
        
        # create tabs
        self.create_signal_tab()
        self.create_resistance_tab()
        self.create_emotions_bipolar_raw_tab()
        self.create_emotions_bipolar_percent_tab()
        self.create_alpha_waves_tab()
        self.create_beta_waves_tab()
        self.create_theta_waves_tab()

        # initialize collection flags
        self.is_collecting = {
            'signal': False,
            'resist': False,
            'emotions_bipolar_raw': False,
            'emotions_bipolar_percent': False,
            'waves': False,
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
        for data_type in ['signal', 'resist', 'emotions_bipolar_raw', 'emotions_bipolar_percent', 'waves']:
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
            command=lambda: self.back_to_home(),
            style="primary.TButton"
        )
        self.back_button.pack(side=LEFT, padx=5)

    def device_connected(self):
        self.connect_btn.configure(state=DISABLED)
        for btn in self.control_buttons.values():
            btn.configure(state=NORMAL)

    def back_to_home(self):
        self.notebook.select(self.notebook.tabs()[0])
        self.visualizer.show_frame(HomeFrame)

    def create_data_tab(self, notebook, tab_title, ax_title_func, y_label, axes_attr_name, lines_attr_name, canvas_attr_name, plots):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=tab_title)
        
        fig = Figure(figsize=(12, 8))
        axes_dict = {}
        lines_dict = {}
        
        positions = [221, 222, 223, 224]

        for pos, plot in zip(positions, plots):
            ax = fig.add_subplot(pos)
            ax.set_title(ax_title_func(plot))
            ax.set_xlabel("Time (s)")
            ax.set_ylabel(y_label)
            axes_dict[plot] = ax
            line, = ax.plot([], [])
            lines_dict[plot] = line

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
            canvas_attr_name="signal_canvas",
            plots=['O1', 'O2', 'T3', 'T4']
        )

    def create_resistance_tab(self):
        self.create_data_tab(
            notebook=self.notebook,
            tab_title="Resistance",
            ax_title_func=lambda ch: f"Channel {ch} Resistance",
            y_label="Resistance (Ohms)",
            axes_attr_name="resist_axes",
            lines_attr_name="resist_lines",
            canvas_attr_name="resist_canvas",
            plots=['O1', 'O2', 'T3', 'T4']
        )

    def create_emotions_bipolar_raw_tab(self):
        self.create_data_tab(
            notebook=self.notebook,
            tab_title="Emotions Bipolar Raw",
            ax_title_func=lambda metric: f"{metric.title()} (Raw)",
            y_label="Raw Value",
            axes_attr_name="bipolar_raw_axes",
            lines_attr_name="bipolar_raw_lines",
            canvas_attr_name="bipolar_raw_canvas",
            plots=['attention', 'relaxation', 'alpha', 'beta']
        )

    def create_emotions_bipolar_percent_tab(self):
        self.create_data_tab(
            notebook=self.notebook,
            tab_title="Emotions Bipolar Percent",
            ax_title_func=lambda metric: f"{metric.title()} (Percent)",
            y_label="Percent Value",
            axes_attr_name="bipolar_percent_axes",
            lines_attr_name="bipolar_percent_lines",
            canvas_attr_name="bipolar_percent_canvas",
            plots=['attention', 'relaxation', 'alpha', 'beta']
        )

    def create_alpha_waves_tab(self):
        self.create_data_tab(
            notebook=self.notebook,
            tab_title="Alpha Waves Percent",
            ax_title_func=lambda metric: f"{metric.title()} Alpha Waves",
            y_label="Percent Value",
            axes_attr_name="alpha_waves_axes",
            lines_attr_name="alpha_waves_lines",
            canvas_attr_name="alpha_waves_canvas",
            plots=['O1', 'O2', 'T3', 'T4'],
        )

    def create_beta_waves_tab(self):
        self.create_data_tab(
            notebook=self.notebook,
            tab_title="Beta Waves Percent",
            ax_title_func=lambda metric: f"{metric.title()} Beta Waves",
            y_label="Percent Value",
            axes_attr_name="beta_waves_axes",
            lines_attr_name="beta_waves_lines",
            canvas_attr_name="beta_waves_canvas",
            plots=['O1', 'O2', 'T3', 'T4'],
        )

    def create_theta_waves_tab(self):
        self.create_data_tab(
            notebook=self.notebook,
            tab_title="Theta Waves Percent",
            ax_title_func=lambda metric: f"{metric.title()} Theta Waves",
            y_label="Percent Value",
            axes_attr_name="theta_waves_axes",
            lines_attr_name="theta_waves_lines",
            canvas_attr_name="theta_waves_canvas",
            plots=['O1', 'O2', 'T3', 'T4'],
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
    
    def update_alpha_waves_plots(self, frame):
        """Update alpha waves plots for FuncAnimation on EEGFrame."""
        channels = ['O1', 'O2', 'T3', 'T4']
        if not self.is_collecting['waves']:
            return tuple(self.alpha_waves_lines[ch] for ch in channels)
        
        for channel in channels:
            timestamps = list(self.controller.deques['waves'][channel]['alpha']['percent']['timestamps'])
            values = list(self.controller.deques['waves'][channel]['alpha']['percent']['values'])
            
            if timestamps and values:
                relative_times = [t - timestamps[0] for t in timestamps]
                self.alpha_waves_lines[channel].set_data(relative_times, values)
                self.alpha_waves_axes[channel].relim()
                self.alpha_waves_axes[channel].autoscale_view()
        
        return tuple(self.alpha_waves_lines[ch] for ch in channels)
    
    def update_beta_waves_plots(self, frame):
        """Update beta waves plots for FuncAnimation on EEGFrame."""
        channels = ['O1', 'O2', 'T3', 'T4']
        if not self.is_collecting['waves']:
            return tuple(self.beta_waves_lines[ch] for ch in channels)
        
        for channel in channels:
            timestamps = list(self.controller.deques['waves'][channel]['beta']['percent']['timestamps'])
            values = list(self.controller.deques['waves'][channel]['beta']['percent']['values'])
            
            if timestamps and values:
                relative_times = [t - timestamps[0] for t in timestamps]
                self.beta_waves_lines[channel].set_data(relative_times, values)
                self.beta_waves_axes[channel].relim()
                self.beta_waves_axes[channel].autoscale_view()
        
        return tuple(self.beta_waves_lines[ch] for ch in channels)
    
    def update_theta_waves_plots(self, frame):
        """Update theta waves plots for FuncAnimation on EEGFrame."""
        channels = ['O1', 'O2', 'T3', 'T4']
        if not self.is_collecting['waves']:
            return tuple(self.theta_waves_lines[ch] for ch in channels)
        
        for channel in channels:
            timestamps = list(self.controller.deques['waves'][channel]['theta']['percent']['timestamps'])
            values = list(self.controller.deques['waves'][channel]['theta']['percent']['values'])
            
            if timestamps and values:
                relative_times = [t - timestamps[0] for t in timestamps]
                self.theta_waves_lines[channel].set_data(relative_times, values)
                self.theta_waves_axes[channel].relim()
                self.theta_waves_axes[channel].autoscale_view()
        
        return tuple(self.theta_waves_lines[ch] for ch in channels)
    
    def display_calibration_window(self):
        self.calibration_popup = ttk.Window(themename="darkly")
        self.calibration_popup.title("Calibration")
        self.calibration_popup.geometry("300x200")

        self.calibration_label = ttk.Label(self.calibration_popup, text="Calibration progress:")
        self.calibration_label.pack()

        self.calibration_progress_bar = ttk.Progressbar(self.calibration_popup, orient=HORIZONTAL, style="danger.Horizontal.TProgressbar")
        self.calibration_progress_bar.pack()

        self.calibration_percentage = ttk.Label(self.calibration_popup, text="0%")
        self.calibration_percentage.pack()

        # Start updating without a cross-thread call
        self.update_calibration_progress()

    def update_calibration_progress(self):
        # Update the progress bar value on the main thread
        self.calibration_progress_bar.configure(value=self.controller.bipolar_calibration_progress)
        self.calibration_percentage.configure(text=f"{self.controller.bipolar_calibration_progress}%")
        if not self.controller.is_bipolar_calibrated():
            # Schedule the next update after 100ms
            self.calibration_progress_bar.after(100, self.update_calibration_progress)
        else:
            self.calibration_popup.destroy()

    def toggle_collection(self, data_type):
        if not self.is_collecting[data_type]:
            self.control_buttons[data_type].configure(
                text=f"Stop {data_type.replace('_', ' ').title()}",
                style="danger.TButton"
            )
            # disable all other buttons
            for other_data_type in self.control_buttons:
                if other_data_type != data_type:
                    self.control_buttons[other_data_type].configure(state=DISABLED)

            self.is_collecting[data_type] = True
            if data_type == 'resist':
                self.controller.start_resist_collection()
                self.anim = FuncAnimation(self.resist_canvas.figure, self.update_resist_plots, interval=100, blit=False)
                self.anim_list.append(self.anim)
                self.resist_canvas.draw()
            elif data_type == 'emotions_bipolar_raw':
                self.controller.start_emotions_bipolar_collection()
                self.display_calibration_window()
                self.anim = FuncAnimation(self.bipolar_raw_canvas.figure, self.update_bipolar_raw_plots, interval=100, blit=False)
                self.anim_list.append(self.anim)
                self.bipolar_raw_canvas.draw()
            elif data_type == 'emotions_bipolar_percent':
                self.controller.start_emotions_bipolar_collection()
                self.display_calibration_window()
                self.anim = FuncAnimation(self.bipolar_percent_canvas.figure, self.update_bipolar_percent_plots, interval=100, blit=False)
                self.anim_list.append(self.anim)
                self.bipolar_percent_canvas.draw()
            elif data_type == 'waves':
                self.controller.start_spectrum_collection()
                self.anim_alpha = FuncAnimation(self.alpha_waves_canvas.figure, self.update_alpha_waves_plots, interval=100, blit=False)
                self.anim_list.append(self.anim_alpha)
                self.alpha_waves_canvas.draw()
                
                self.anim_beta = FuncAnimation(self.beta_waves_canvas.figure, self.update_beta_waves_plots, interval=100, blit=False)
                self.anim_list.append(self.anim_beta)
                self.beta_waves_canvas.draw()

                self.anim_theta = FuncAnimation(self.theta_waves_canvas.figure, self.update_theta_waves_plots, interval=100, blit=False)
                self.anim_list.append(self.anim_theta)
                self.theta_waves_canvas.draw()
            else:
                self.controller.start_signal_collection()
                self.anim = FuncAnimation(self.signal_canvas.figure, self.update_signal_plots, interval=100, blit=False)
                self.anim_list.append(self.anim)
                self.signal_canvas.draw()
            
        else:
            # Stop collection
            self.controller.stop_collection()
            if self.anim_list:
                for anim in self.anim_list:
                    anim.event_source.stop()
            self.anim_list = []
            self.is_collecting[data_type] = False
            # Wait for the thread to finish
            self.control_buttons[data_type].configure(
                text=f"Start {data_type.replace('_', ' ').title()}",
                style="success.TButton"
            )
            # enable all other buttons
            for other_data_type in self.control_buttons:
                if other_data_type != data_type:
                    self.control_buttons[other_data_type].configure(state=NORMAL)


class MacroFrame(ttk.Frame):
    def __init__(self, parent, visualizer):
        ttk.Frame.__init__(self, parent)
        self.visualizer = visualizer

        self.eeg_controller = self.visualizer.eeg_controller
        self.heg_controller = self.visualizer.heg_controller

        self.macro = Macro()

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        self.saved_macros_folder = "Macro/saved_macros"
        self.save_file_name = None

        self.icons_folder = "Macro/Icons"

        self.icon_images = {}
        for icon in os.listdir(self.icons_folder):
            icon_path = os.path.join(self.icons_folder, icon)
            icon_image = Image.open(icon_path)
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.icon_images[icon[:-4]] = icon_photo

        self.special_icons = {
            "key_press_?": "key_press_question_mark",
            "key_release_?": "key_release_question_mark",
            "key_press_\"": "key_press_double_quote",
            "key_release_\"": "key_release_double_quote",
            "key_press_*": "key_press_star",
            "key_release_*": "key_release_star",
            "key_press_\\": "key_press_backslash",
            "key_release_\\": "key_release_backslash",
            "key_press_|": "key_press_pipe",
            "key_release_|": "key_release_pipe",
            "key_press_<": "key_press_less_than",
            "key_release_<": "key_release_less_than",
            "key_press_>": "key_press_greater_than",
            "key_release_>": "key_release_greater_than",
            "key_press_/": "key_press_slash",
            "key_release_/": "key_release_slash",
        }

        self.equivalent_keys = {
            "key_press_alt_l": "key_press_alt",
            "key_release_alt_l": "key_release_alt",
            "key_press_alt_gr": "key_press_alt",
            "key_release_alt_gr": "key_release_alt",
            "key_press_shift_l": "key_press_shift",
            "key_release_shift_l": "key_release_shift",
            "key_press_shift_r": "key_press_shift",
            "key_release_shift_r": "key_release_shift",
            "key_press_ctrl_l": "key_press_ctrl",
            "key_release_ctrl_l": "key_release_ctrl",
            "key_press_ctrl_r": "key_press_ctrl",
            "key_release_ctrl_r": "key_release_ctrl",
        }

        self.controls = []

        self.current_sub_frame = None

        self.replay_loop = False

        self.record_movement = tk.BooleanVar(value=False)

        self.create_create_macro_frame()
        self.create_load_macro_frame()
        self.create_assign_to_key_frame()

        self.create_control_panel()

    def create_control_panel(self):
        control_frame = ttk.LabelFrame(self.main_frame, text="Controls", padding=10)
        control_frame.pack(fill=X, pady=(0, 10))

        self.create_new_btn = ttk.Button(
            control_frame,
            text="Create New Macro",
            command=lambda: self.switch_sub_frame(self.create_macro_frame),
            style="primary.TButton"
        )
        self.create_new_btn.pack(side=LEFT, padx=5)
        self.controls.append(self.create_new_btn)

        self.load_btn = ttk.Button(
            control_frame,
            text="Load Macro",
            command=lambda: self.switch_sub_frame(self.load_macro_frame),
            style="primary.TButton"
        )
        self.load_btn.pack(side=LEFT, padx=5)
        self.controls.append(self.load_btn)

        self.assign_to_key_btn = ttk.Button(
            control_frame,
            text="Assign Macro to Key",
            command=lambda: self.switch_sub_frame(self.assign_to_key_frame),
            style="primary.TButton"
        )
        self.assign_to_key_btn.pack(side=LEFT, padx=5)
        self.controls.append(self.assign_to_key_btn)

        self.back_btn = ttk.Button(
            control_frame,
            text="Back to Home",
            command=lambda: self.clear_sub_frame(),
            style="primary.TButton"
        )
        self.back_btn.pack(side=LEFT, padx=5)
        self.controls.append(self.back_btn)

    def create_create_macro_frame(self):
        self.create_macro_frame = ttk.Frame(self.main_frame)
        self.create_macro_frame.columnconfigure(0, weight=1)
        self.create_macro_frame.columnconfigure(1, weight=1)
        self.create_macro_frame.columnconfigure(2, weight=1)

        self.create_macro_frame.rowconfigure(0, weight=1)
        self.create_macro_frame.rowconfigure(1, weight=3)
        self.create_macro_frame.rowconfigure(2, weight=1)

        self.description_frame = ttk.Frame(self.create_macro_frame)
        self.description_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.config_frame = ttk.Frame(self.create_macro_frame)
        self.config_frame.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        self.icons_frame = ttk.Frame(self.create_macro_frame, borderwidth=2, relief="solid")
        self.icons_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        self.btns_frame = ttk.Frame(self.create_macro_frame)
        self.btns_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        # discription frame
        name_label = ttk.Label(self.description_frame, text="Macro Name:")
        name_label.grid(row=0, column=0, padx=5, pady=5)

        self.name_entry = ttk.Entry(self.description_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry.bind("<FocusOut>", lambda event: self.set_save_file_name())
        self.name_entry.bind("<Return>", lambda event: self.set_save_file_name())
        self.controls.append(self.name_entry)

        type_label = ttk.Label(self.description_frame, text="Type:")
        type_label.grid(row=1, column=0, padx=5, pady=5)
        
        self.replay_mode_var = tk.StringVar(value="once")
        self.play_once_rb = ttk.Radiobutton(
            self.description_frame,
            text="Play Once",
            variable=self.replay_mode_var,
            value="once",
            command=lambda: self.change_replay_mode("once")
        )
        self.play_once_rb.grid(row=1, column=1, padx=5, pady=5)
        self.controls.append(self.play_once_rb)

        self.play_loop_rb = ttk.Radiobutton(
            self.description_frame,
            text="Toggle Loop",
            variable=self.replay_mode_var,
            value="loop",
            command=lambda: self.change_replay_mode("loop")
        )
        self.play_loop_rb.grid(row=1, column=2, padx=5, pady=5)
        self.controls.append(self.play_loop_rb)

        # config frame
        self.constant_delay_var = tk.BooleanVar(value=False)
        self.toggle_constant_delay_box = ttk.Checkbutton(self.config_frame, text="Use Constant Delay:", variable=self.constant_delay_var, command=self.toggle_constant_delay)
        self.toggle_constant_delay_box.grid(row=0, column=0, padx=5, pady=5)
        self.controls.append(self.toggle_constant_delay_box)

        validate_delay = (self.register(lambda new_text: new_text.isdigit() or new_text == ""), '%P')
        self.constant_delay_entry = ttk.Entry(self.config_frame, validate='key', validatecommand=validate_delay)
        self.constant_delay_entry.grid(row=0, column=1, padx=5, pady=5)
        self.constant_delay_entry.insert(0, "50")
        self.constant_delay_entry.bind("<Return>", self.set_constant_delay)
        self.constant_delay_entry.bind("<FocusOut>", self.set_constant_delay)
        self.controls.append(self.constant_delay_entry)
        
        milliseconds_label = ttk.Label(self.config_frame, text="ms")
        milliseconds_label.grid(row=0, column=2, padx=5, pady=5)

        self.config_option_var = tk.BooleanVar(value=False)
        self.toggle_config_option = ttk.Checkbutton(self.config_frame, text="Config Option 2", variable=self.config_option_var)
        self.toggle_config_option.grid(row=1, column=0, padx=5, pady=5)
        self.controls.append(self.toggle_config_option)

        self.toggle_record_movement = ttk.Checkbutton(self.config_frame, text="Record Movement", variable=self.record_movement)
        self.toggle_record_movement.grid(row=1, column=1, padx=5, pady=5)
        self.controls.append(self.toggle_record_movement)

        # icons frame
        self.icons_text = ttk.ScrolledText(self.icons_frame)
        self.icons_text.pack(fill=BOTH, expand=True, padx=5, pady=5)
        # This prevents any key-presses (typing, backspace, etc.) from modifying the widget.
        self.icons_text.bind("<Key>", lambda event: "break")
        # Optionally, block paste operations explicitly:
        self.icons_text.bind("<<Paste>>", lambda event: "break")
        
        # buttons frame
        self.record_input_btn = ttk.Button(self.btns_frame, text="Record Input", command=self.record_input)
        self.record_input_btn.grid(row=0, column=0, padx=5, pady=5)
        self.controls.append(self.record_input_btn)

        self.save_btn = ttk.Button(self.btns_frame, text="Save", command=self.save_macro)
        self.save_btn.grid(row=0, column=1, padx=5, pady=5)
        self.save_btn.configure(state=DISABLED)
        self.controls.append(self.save_btn)

        self.clear_btn = ttk.Button(self.btns_frame, text="Clear Macro", command=self.clear_macro)
        self.clear_btn.grid(row=0, column=2, padx=5, pady=5)
        self.controls.append(self.clear_btn)

    def record_input(self):
        for btn in self.controls:
           btn.configure(state=DISABLED)
        if self.record_movement.get():
            if len(self.macro.inputs) > 0:
                self.macro.append_sequence(record_movements=True)
                Thread(target=self.check_sequence, args=[len(self.macro.inputs) - 1], daemon=True).start()
            else:
                self.macro.record_sequence(record_movements=True)
                Thread(target=self.check_sequence, args=[0], daemon=True).start()
        else:
            if len(self.macro.inputs) > 0:
                self.macro.append_sequence()
                Thread(target=self.check_sequence, args=[len(self.macro.inputs) - 1], daemon=True).start()
            else:
                self.macro.record_sequence()
                Thread(target=self.check_sequence, args=[0], daemon=True).start()

    def check_sequence(self, index):
        last_index = index
        while self.macro.recording:
            if len(self.macro.inputs) > last_index:
                for i in range(last_index, len(self.macro.inputs)):
                    print(self.macro.inputs[i])

                    # for keys
                    if self.macro.inputs[i].startswith("key_"):
                        if self.macro.inputs[i] in self.special_icons:
                            image = self.icon_images[self.special_icons[self.macro.inputs[i]]]

                        elif self.macro.inputs[i] in self.equivalent_keys:
                            image = self.icon_images[self.equivalent_keys[self.macro.inputs[i]]]

                        else:
                            image = self.icon_images[self.macro.inputs[i].lower()]
                        self.after(0, lambda: self.icons_text.image_create(END, image=image))

                    # for delays
                    elif self.macro.inputs[i].startswith("delay"):
                        delay = float(self.macro.inputs[i].split("_")[1]) * 1000
                        self.after(0, lambda: self.icons_text.insert(END, f" {delay:.0f}ms "))

                    # for mouse movements
                    elif self.macro.inputs[i].startswith("mouse_move"):
                        image = self.icon_images["mouse_move"]
                        self.after(0, lambda: self.icons_text.image_create(END, image=image))
                    
                    # for mouse inputs that are not movements
                    else:
                        if self.macro.inputs[i].startswith('mouse_press_Button.x'):
                            image = self.icon_images["mouse_press_Button.x"]
                        elif self.macro.inputs[i].startswith('mouse_release_Button.x'):
                            image = self.icon_images["mouse_release_Button.x"]
                        else:
                            image = self.icon_images[self.macro.inputs[i]]
                        self.after(0, lambda: self.icons_text.image_create(END, image=image))

                    self.after(0, lambda: self.icons_text.see(END))

                last_index = len(self.macro.inputs)
            time.sleep(0.00000001)

        for btn in self.controls:
            btn.configure(state=NORMAL)
        self.configure_save_btn()
        print(self.macro.inputs)

    def configure_save_btn(self):
        if self.save_file_name is None:
            self.save_btn.configure(state=DISABLED)
            return
        if len(self.macro.inputs) == 0:
            self.save_btn.configure(state=DISABLED)
            return
        self.save_btn.configure(state=NORMAL)

    def save_macro(self):
        self.macro.save_macro(self.save_file_name)

    def clear_macro(self):
        self.name_entry.delete(0, END)
        self.icons_text.delete(1.0, END)
        self.configure_save_btn()
        self.macro.clear_macro()

    def set_save_file_name(self):
        file_name = self.name_entry.get().strip()
        invalid_chars = set('/\\:*?"<>|')
        if file_name and not any(char in invalid_chars for char in file_name):
            self.save_file_name = file_name
            print(self.save_file_name)
        else:
            self.name_entry.delete(0, END)
        self.configure_save_btn()

    def change_replay_mode(self, mode):
        if mode == "once":
            self.play_once_btn.configure(state=DISABLED)
            self.play_loop_btn.configure(state=NORMAL)
            self.replay_loop = False
        elif mode == "loop":
            self.play_once_btn.configure(state=NORMAL)
            self.play_loop_btn.configure(state=DISABLED)
            self.replay_loop = True

    def toggle_constant_delay(self):
        if self.constant_delay_var.get():
            self.macro.constant_delay = True
            print(self.macro.constant_delay_time)
            self.icons_text.delete(1.0, END)
            self.update_sequence(constant_delay=True)

        else:
            self.macro.constant_delay = False
            print(self.macro.constant_delay_time)
            self.icons_text.delete(1.0, END)
            self.update_sequence(constant_delay=False)

    def set_constant_delay(self):
        if self.constant_delay_entry.get() == "":
            self.constant_delay_entry.insert(0, "50")
            self.macro.constant_delay_time = 50
        else:
            self.macro.constant_delay_time = float(self.constant_delay_entry.get())

    def create_load_macro_frame(self):
        self.load_macro_frame = ttk.Frame(self.main_frame)
        load_text = ttk.Label(self.load_macro_frame, text="Load Macro")
        load_text.pack(side=TOP, padx=5, pady=5)

        self.macro_listbox = tk.Listbox(self.load_macro_frame, selectmode=SINGLE)
        self.macro_listbox.pack(side=TOP, padx=5, pady=5, expand=True, fill=BOTH)

        self.macro_files = os.listdir(self.saved_macros_folder)
        for file in self.macro_files:
            self.macro_listbox.insert(END, file)

        self.macro_listbox.bind("<Double-Button-1>", self.load_macro)
        # Bind right-click to show the context menu
        self.macro_listbox.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        listbox = event.widget
        # Determine the index of the item under the mouse pointer
        index = listbox.nearest(event.y)
        # Optionally select the item so the user sees which one was interacted with
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(index)
        
        # Create a context menu
        context_menu = tk.Menu(listbox, tearoff=0)
        context_menu.add_command(label="Load Macro", command=lambda: self.load_macro(None))
        context_menu.add_command(label="Delete Macro", command=lambda: self.delete_macro(index))
        
        # Display the menu at the mouse pointer's position
        context_menu.post(event.x_root, event.y_root)
    
    def delete_macro(self, index):
        file_to_delete = self.macro_files[index]
        full_path = os.path.join(self.saved_macros_folder, file_to_delete)
        if os.path.exists(full_path):
            os.remove(full_path)
            self.update_listbox()

    def load_macro(self, event):
        selected_macro = self.macro_listbox.curselection()
        print(self.macro_files[selected_macro[0]])
        self.clear_macro()
        self.macro.load_from_file(self.macro_files[selected_macro[0]])
        self.name_entry.insert(0, self.macro_files[selected_macro[0]])
        self.save_file_name = self.macro_files[selected_macro[0]]
        self.update_sequence()
        self.switch_sub_frame(self.create_macro_frame)
        self.configure_save_btn()

    def update_sequence(self, constant_delay=False):
        for i in range(0, len(self.macro.inputs)):
            # for keys
            if self.macro.inputs[i].startswith("key_"):
                if self.macro.inputs[i] in self.special_icons:
                    image = self.icon_images[self.special_icons[self.macro.inputs[i]]]

                elif self.macro.inputs[i] in self.equivalent_keys:
                    image = self.icon_images[self.equivalent_keys[self.macro.inputs[i]]]

                else:
                    image = self.icon_images[self.macro.inputs[i].lower()]
                self.icons_text.image_create(END, image=image)

            # for delays
            elif self.macro.inputs[i].startswith("delay"):
                if not constant_delay:
                    delay = float(self.macro.inputs[i].split("_")[1]) * 1000
                    self.icons_text.insert(END, f" {delay:.0f}ms ")
                else:
                    self.icons_text.insert(END, f" {self.macro.constant_delay_time:.0f}ms ")

            # for mouse movements
            elif self.macro.inputs[i].startswith("mouse_move"):
                image = self.icon_images["mouse_move"]
                self.icons_text.image_create(END, image=image)
            
            # for mouse inputs that are not movements
            else:
                if self.macro.inputs[i].startswith('mouse_press_Button.x'):
                    image = self.icon_images["mouse_press_Button.x"]
                elif self.macro.inputs[i].startswith('mouse_release_Button.x'):
                    image = self.icon_images["mouse_release_Button.x"]
                else:
                    image = self.icon_images[self.macro.inputs[i]]
                self.icons_text.image_create(END, image=image)

        self.icons_text.see(END)

    def update_listbox(self):
        self.macro_listbox.delete(0, END)
        self.macro_files = os.listdir(self.saved_macros_folder)
        for file in self.macro_files:
            self.macro_listbox.insert(END, file)

    def create_assign_to_key_frame(self):
        self.assign_to_key_frame = ttk.Frame(self.main_frame)

    def switch_sub_frame(self, sub_frame):
        self.update_listbox()
        if self.current_sub_frame:
            self.current_sub_frame.pack_forget()
        self.current_sub_frame = sub_frame
        self.current_sub_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
    
    def clear_sub_frame(self):
        if self.current_sub_frame:
            self.current_sub_frame.pack_forget()
        self.current_sub_frame = None
        self.visualizer.show_frame(HomeFrame)

if __name__ == "__main__":
    visualizer = Visualizer()
    visualizer.run()