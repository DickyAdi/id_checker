import tkinter as tk
from tkinter import ttk


class input_group:
    def __init__(self, parent, var_name:str, var_text, row, col, state='normal',required=True):
        self.row = row
        self.col = col
        self.state = state
        self.var_name = var_name
        if required and var_text[-1] != '*':
            self.var_text = var_text + '*'
        else:
            self.var_text = var_text
        self.frame = ttk.Frame(parent, padding=4)
        self.frame.columnconfigure(0, weight=1)
        self.label = ttk.Label(self.frame, text=self.var_text)
        self.error_label = ttk.Label(self.frame, text='', font=('TkDefaultFont', 8), foreground='red')
        self.var:ttk.Entry | ttk.Combobox | tk.Text = self.create_entry_var()
        self.reset_bg = self.label.cget('foreground')
        self.label.grid(row=0, column=0, sticky='w')
        self.error_label.grid(row=0, column=0)
        self.var.grid(row=1, column=0, sticky='ew')
        self.place_widget()
    def place_widget(self):
        self.frame.grid(row=self.row, column=self.col, sticky='nsew')
    def create_entry_var(self):
        raise NotImplementedError('Method not implemented, override the subclass instead')
    def show_label_error(self, message):
        self.label.configure(foreground='red')
        self.error_label.configure(text=message)
    def hide_label_error(self):
        self.label.configure(foreground=self.reset_bg)
        self.error_label.configure(text='')
    def set_value(self, value):
        self.var.set(value)
    def get_value(self):
        return self.var.get()
    def clear_value(self):
        self.var.delete(0, tk.END)
    def enable_state(self):
        self.var.configure(state='normal')
    def disable_state(self):
        self.var.configure(state='disabled')

class entry_input(input_group):
    def __init__(self, parent, var_name: str, var_text, row, col, state='normal',required=True):
        self.entry = tk.StringVar()
        super().__init__(parent, var_name, var_text, row, col, state, required)
    def create_entry_var(self):
        self.var = ttk.Entry(self.frame, textvariable=self.entry, state=self.state)
        return self.var

class combo_input(input_group):
    def __init__(self, parent, var_name: str, var_text, row, col, state='normal',required=True):
        self.combo_box_values = ['Lancar', 'Kurang lancar', 'Diragukan', 'Macet', 'Daftar hitam']
        self.entry = tk.IntVar()
        super().__init__(parent, var_name, var_text, row, col, state, required)
    def create_entry_var(self):
        self.var = ttk.Combobox(self.frame, values=self.combo_box_values, state=self.state)
        return self.var
    def disable_state(self):
        self.var.configure(state='readonly')
    def clear_value(self):
        self.var.set('')

class text_input(input_group):
    def __init__(self, parent, var_name: str, var_text, row, col, state='normal', required=True):
        super().__init__(parent, var_name, var_text, row, col, state, required)
    def create_entry_var(self):
        self.var = tk.Text(self.frame, height=5, state=self.state)
        return self.var
    def place_widget(self):
        self.frame.grid(row=self.row, column=self.col, columnspan=2, sticky='ew')
    def set_value(self, value):
        self.var.delete('1.0', tk.END)
        if value:
            self.var.insert(tk.END, value)
    def get_value(self):
        return self.var.get('1.0', tk.END)
    def clear_value(self):
        self.var.delete('1.0', tk.END)