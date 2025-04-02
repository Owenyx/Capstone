import tkinter as tk
from tkinter import ttk
import random #randomizing
import pygame #audio
import tkinter.font as font
from PIL import Image, ImageTk  # Needed for JPG/PNG support- for hourglass pic
import re #font organizing
from tkinter import filedialog #open file dialog
import fitz  # read/extract pdf file
import threading 
import numpy as np #threading
import time

#style list
style = ['bold italic', 'bold', 'italic', 'normal']

def display_timing():
    global click
    if time_on==True:
        click+=1
        if(click % 2==0): timing.pack_forget()
        else: 
             timing.pack(padx=10,side="right", anchor="w")


click=1
def update_timing(time_going:bool):
    global ms
    if time_going==True:
        ms += 1  # Increment milliseconds
        
        seconds = int (ms // 1000)
        milliseconds = ms % 1000
        minutes = int( seconds/60)
        hours = int(minutes/60)

        timing.config(text=f"{hours}:{minutes}:{seconds}:{milliseconds:03d}")  # Update the label with seconds and milliseconds
        # Call the function again after 1 ms
        frame.after(1, lambda: update_timing((time_going)))
    else: 
        ms=0

# Initialize milliseconds
ms = 0
     
root = tk.Tk()
root.title("Focus Mode")
root.geometry("1200x700")  # wide, tall

#restrict window resizing
root.minsize(600, 600)  # Minimum size: 300x200

#original bg color
original_bg = "pink"
timingframe_bg = "blue"
root.configure(bg="black")
  
# List of symbol/system fonts to exclude
excluded_fonts = ["Marlett", "Wingdings", "Wingdings 2", "Wingdings 3", "Webdings", "Symbol", "Segoe UI Symbol", 
                  "Bookshelf Symbol 7", "Kunstler Script", "MT Extra", "Edwardian Script ITC", "Small Fonts", "MS Outlook",
                  "Palace Script MT", "Parchment", "MS Reference Specialty","Segoe MDL2 Assets","Segoe Fluent Icons"]
#get all fonts
font_families = font.families()
#filtering fonts
pattern = re.compile(r'^[A-Za-z0-9 _-]+$')
english_fonts = [f for f in font_families if pattern.match(f) and f not in excluded_fonts]

audioing = ["aud1.mp3", "aud2.mp3","aud3.mp3", 
            "audio4.mp3",  "audio5.mp3",  "audio6.mp3"]
audFile = "aud1.mp3" #initalize sound

def randomizing(): 
    global audFile
    ms = 0  # Reset focused timing
    r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    bgColor  = f'#{r:02x}{g:02x}{b:02x}'  #RGB to Hex
    textColor = f'#{255-r:02x}{255-g:02x}{255-b:02x}'  # Inverted
    audFile = random.choices(audioing)[0] #rand audio from audioing list
    BIN = random.choices(style)[0]
    fontN= random.choices(english_fonts)[0]
    FontSize = random.randint(22, 47)
    #listing = [textColor, color, BIN, fontN, FontSize]
    label.config(fg= textColor, bg=bgColor, font=(fontN, FontSize, BIN))
    canvas.configure(bg=bgColor)
    #frame.configure(bg=bgColor)

def extract_text():
    # Open file dialog to select a PDF
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    
    if file_path:
        doc = fitz.open(file_path)  # Open PDF
        texting = ""

        # save pdf text
        for page in doc:
            texting += page.get_text("text") + "\n"

    label.config(text=texting)
    randomizing()

def display_text(event=None):    
    entered= entry.get()
    if entry.get() == '': 
        entered = "example text"
        entry.insert(0, "Enter text here") 
    label.config(text=entered)

#initalizing it-only called once
pygame.mixer.init()

def play_audio():
    global audFile
    pygame.mixer.music.stop()
    audFile = random.choice(audioing) #rand audio from audioing list
    pygame.mixer.music.load(audFile)
    pygame.mixer.music.play()


"""top bar is made all below"""
#image any png/jpg
image = Image.open("FocusMode\\Hourglass.png")  
image = image.resize((100, 100))   # Resize to 100x100 pixels
photo = ImageTk.PhotoImage(image)


timingframe = tk.Frame(root, bg=timingframe_bg)
# Expand like a bar
timingframe.pack(fill="x", side="top", anchor="n", expand=True)

# Entry widget to get user input
entry = tk.Entry(timingframe, text="enter text here", font=("Arial", 14))
entry.insert(0, "Enter text here") 
entry.pack(padx=10, pady=10, side="bottom", expand=True, fill="x")


buttonCol= "black"
buttonfg="white"
textPDF = tk.Button(timingframe, bg=buttonCol, fg=buttonfg, text="upload PDF file",font=("Arial", 14), command= extract_text)#place(x=300, y=0)
textPDF.pack(padx=10, side="right")

buttonText = tk.Button(timingframe, bg=buttonCol, fg=buttonfg,text="enter text",font=("Arial", 14), command= display_text)#.place(x=100, y=50)
buttonText.pack(padx=10,side="right")

buttonRand = tk.Button(timingframe, bg=buttonCol, fg=buttonfg,text="randomize",font=("Arial", 14), command= randomizing)#.place(x=0, y=50)
buttonRand.pack(padx=10,side="right")

#play audio on button command
audButton = tk.Button(timingframe,bg=buttonCol, fg=buttonfg, text="Play a Sound", font=("Arial", 10), command=play_audio)
audButton.pack(padx=10,side="right", anchor="w")

trending = 0

#the text saying if user is focused or not
focus = tk.Label(timingframe, bg=timingframe_bg, text="Don't lose your focus please",  font=("Arial", 14, "underline"))
focus.pack(padx=10,side="left")

trendtext= tk.Label(timingframe, bg=timingframe_bg, text=("Your current trend is: "),  font=("Arial", 14))
trendtext.pack(padx=10,side="left")

trendLabel = tk.Label(timingframe, bg="black", text=(trending),fg=buttonfg, font=("Arial", 14))
trendLabel.pack(pady=10,side="left")

buttonImage = tk.Button(timingframe, bg=timingframe_bg, image=photo, borderwidth=0, command= display_timing)#place(x=300, y=0)
buttonImage.pack(padx=10,side="right", anchor="e")

timing = tk.Label(timingframe,text="time focused", bg=timingframe_bg, font=("Helvetica", 24))#.place(x=300, y=80)
timing.pack(padx=10,side="right", anchor="w")



"""scrollbar is made all below"""
#scrollbar is made all below fill="x", side="top", anchor="n", expand=True)
frame = ttk.Frame(root)
frame.pack(fill="both", side="top", anchor="n", expand=True, pady=20)

canvas = tk.Canvas(frame, width=100, height=600, bg=original_bg) 
#creating this before the canvas so the scrollbar fills the whole bottom
scrollbarX = ttk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
scrollbarX.pack(side="bottom", fill="x")


canvas.pack(side="left", fill="both", expand=True)

scrollbarY = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
scrollbarY.pack(side="right", fill="y")

scroll_frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbarY.set, xscrollcommand=scrollbarX.set)

scroll_frame.bind(
    "<Configure>",
    #calls the code like a function once scrollable.frame changes due to config
    lambda e: 
    canvas.configure(scrollregion=canvas.bbox("all")) #bbox = bounding box of all widgets
)

#the text the user is reading and can use scrollbar on
label = tk.Label(scroll_frame,text="example text",  font=("Arial", 14),  wraplength=1000)
label.pack(side="bottom", expand=True, fill="both", anchor="nw") #, pady=10)
#if enter is pressed, return/display text
entry.bind("<Return>", display_text)


from testing import HEGController
# Create the HEGController and TrendMonitor objects

controller = HEGController(chunk_size=30)
#trend values all done below
class TrendMonitor:
    def __init__(self, controller, funcCall):
        self.controller = controller
        self.funcCall = funcCall
        self.numbers = []

    def start_monitoring(self):
        while not controller.stop_event.is_set():
            global trending
            #if HEG is off break out
            if controller.stop_event.is_set():
                break
            root.after(1, trendLabel.config, {'text': trending})
            k=5
            time.sleep(3)
            chunk = self.controller.get_data()
            chunk = [float(x) for x in chunk]
            for i in range(0, len(chunk), k): 
                self.numbers.append(np.mean(chunk[i:i+k])) 
            trend = float(np.sum(np.diff(self.numbers)))
            trending = round (trend, 4)
            self.numbers.clear()
            print(f"Trend: {trend}")
            #call funccall with this trend val
            self.funcCall(trend)  

# Show button if not focused
def update_focus(trend):
    global trending
    global count
    global ms
    #if HEG is on
    if not controller.stop_event.is_set():
        print(trend)
        if trend==0.0: 
            root.after(2, focus.config, {'text': "Toggle the HEG button"})
            root.after(0, trendLabel.config, {'text': ""})
            root.after(0, trendtext.config, {'text': ""})

        elif trend > 0:  root.after(0, focus.config, {'text': "You are currently focused"}) 
        else:
            ms = 0  # Reset focused timing
            root.after(1, randomizing)
            root.after(0, focus.config, {'text': "NOT FOCUSED"})
            count+=1
            #play a sound if foucs lost for the 3rd time
            if count>=2:
                (root.after(1, play_audio))
                count=0
    else: 
        root.after(2, focus.config, {'text': "Toggle the HEG button"}) 
        root.after(0, trendLabel.config, {'text': ""})
        root.after(0, trendtext.config, {'text': ""})

count = 0
time_on=False
def connecting():
    global ms
    global time_on
    """Toggle HEG connection."""
    if controller.is_collecting:
        controller.stop_collecting()
        update_timing(False)
        timing.pack_forget()
        time_on=False
        root.after(0, trendLabel.config, {'text': ""})
        root.after(0, trendtext.config, {'text': ""})
        connectButton.config(text="Connect HEG", bg="green")
    else:
        controller.start_collecting()
        update_timing(True)
        time_on=True
        timing.pack(padx=10,side="right", anchor="w")
        root.after(0, trendtext.config, {'text': "Your current trend is: "})
        connectButton.config(text="Disconnect HEG", bg="red")


    trend_monitor = TrendMonitor(controller, update_focus)
    # Run the trend monitoring in a background thread so that it is always finding your current focus trend
    monitor_thread = threading.Thread(target=trend_monitor.start_monitoring)
    monitor_thread.daemon = True
    monitor_thread.start()

connectButton = tk.Button(timingframe, bg="green", fg=buttonfg,text="connect HEG",font=("Arial", 14), command= connecting)#.place(x=100, y=50)
connectButton.pack(padx=10,side="left")


randomizing()

# Run the application
tk.mainloop()
controller.stop_collecting()
