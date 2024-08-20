import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog
from pathlib import Path
from PIL import ImageTk, Image
import os
import sys
import sv_ttk

if getattr(sys, 'frozen', False):
    abs_path = sys._MEIPASS
else:
    abs_path = os.path.abspath('.')

class App(tk.Tk):
    def __init__(self, width, height):
        super().__init__()
        width = width
        height = height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width/2) - (width/2))
        y = int((screen_height/2) - (height/2))
        self.geometry(f'{width}x{height}+{x}+{y}')
        self.minsize(width, height)
        self.title("ID Checker")

        corporate_logo = image_label(self, './assets/img/logo_BJA_PNG(resize).png')
        

        self.mainloop()

class input_label:
    def __init__(self, parent):
        pass

class notebook_group(ttk.Notebook):
    def __init__(self, parent):
        super().__init__(parent)
        pass

class image_label(ttk.Label):
    def __init__(self, parent, image_path):
        super().__init__(parent)
        img = self.to_imagetk(image_path)
        label_image = ttk.Label(parent, image=img)
        label_image.image = img
        label_image.grid(row=0, column=0, sticky='n', pady=10, padx=15)
    def to_imagetk(self, image_path):
        image = Image.open(os.path.join(abs_path, image_path))
        image_tk = ImageTk.PhotoImage(image)
        return image_tk