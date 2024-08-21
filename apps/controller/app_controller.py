import sys
import os
from pathlib import Path
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import List
import re

# from apps.app import input_group
from model.debitur import debitur

class app_controller:
    def __init__(self, app):
        self.app = app
        self.debitur = debitur()

    def process_search(self):
        key = self.app.nik.var.get()
        res = self.debitur.search_record(key)
        if res:
            [var.enable_state() for var in self.app.form_control]
        else:
            response = messagebox.askquestion('Question', 'Data tidak terdaftar, input baru?')
            if response == 'yes':
                self.app.edit_button.configure(text='Insert', state='normal')
                [var.enable_state() for var in self.app.form_control]
            else:
                self.app.edit_button.configure(text='Edit', state='disabled')
                self.app.nik.clear_value()
                for var in self.app.form_control:
                    var.clear_value()
                    var.disable_state()