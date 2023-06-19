import tkinter as tk
from tkinter import ttk
from guiconfig import *

class View:
    def __init__(self, controller):
        # Displays the application gui
        self.c = controller
        self.root = tk.Tk()     # sets up the tkinter window root
        self.root.geometry(APP_SIZE)
        self.root.title(APP_TITLE)
        self.WindowSetUp()              # keep all the gui widgets in one place
        self.root.mainloop()            # start the application loop and capture events

    def WindowSetUp(self):
        # LEFT PANEL #
        self.LeftPanel = tk.Frame(self.root)
        self.LeftPanel.grid(row=0, column=0)
        ##############
        # CENTER #
        self.Center = tk.Frame(self.root)
        self.Center.grid(row=0, column=1)
        self.TimePeriod_dropdown = ttk.Combobox(self.Center, values=TIME_DISPLAY_VALUES, font=SMALL_FONT, state='readonly')
        self.TimePeriod_dropdown.grid(row=0, column=0)
        self.searchbar = tk.Entry(self.Center, font=NORMAL_FONT)
        self.searchbar.grid(row=0, column=1)
        self.search_button = tk.Button(self.Center, text='Search', font=SMALL_FONT, command=lambda:self.c.RunSearch(self.searchbar.get(), self.TimePeriod_dropdown.get()))
        self.search_button.grid(row=0, column=2)
        ##########
        # RIGHT PANEL #
        self.RightPanel = tk.Frame(self.root)
        self.RightPanel.grid(row=0, column=2)
        ###############