import tkinter as Tk

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd

plt.style.use('fivethirtyeight')
# values for graph
x_vals = []
y_vals = []

def animate(i):
    data = pd.read_csv("HEG_readings.csv")
    x = data["timestamp"].tail(1000)
    y = data["reading"].tail(1000)
    # Get axes of figure
    ax = plt.gca()
    # Clear current data
    ax.cla()
    # Plot new data
    ax.plot(x, y)
    # Set fixed y-axis limits
    ax.set_ylim(0, 200)

# GUI
root = Tk.Tk()
label = Tk.Label(root, text="Realtime Animated Graph").grid(column=0, row=0)

# graph
canvas = FigureCanvasTkAgg(plt.gcf(), master=root)
canvas.get_tk_widget().grid(column=0, row=1)
# Create single plot
plt.gcf().add_subplot(1, 1, 1)

ani = FuncAnimation(plt.gcf(), animate, interval=10, blit=False)

Tk.mainloop()