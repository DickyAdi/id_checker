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
        self.entry.set(value)
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
        self.var.configure(state='disabled')
    def set_value(self, value):
        self.var.set(value)
    def enable_state(self):
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

class datatable:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        self.frame.grid(row=0, column=0, sticky='nsew')
        self.label = ttk.Label(self.frame, text='Datatable')
        self.data_cols = ('id', 'nik', 'nama', 'tanggal_lahir', 'tempat_lahir', 'alamat', 'nama_ibu_kandung','nama_pasangan', 'kolektibilitas', 'keterangan')
        self.datatable = ttk.Treeview(self.frame, columns=self.data_cols, show='headings')
        self.datatable.heading('id', text='ID-CIF')
        self.datatable.heading('nik', text='NIK')
        self.datatable.heading('nama', text='Nama')
        self.datatable.heading('tanggal_lahir', text='Tanggal lahir')
        self.datatable.heading('tempat_lahir', text='Tempat lahir')
        self.datatable.heading('alamat', text='Alamat')
        self.datatable.heading('nama_ibu_kandung', text='Nama ibu kandung')
        self.datatable.heading('nama_pasangan', text='Nama pasangan')
        self.datatable.heading('kolektibilitas', text='Kolektibilitas')
        self.datatable.heading('keterangan', text='Keterangan')
        self.vertical_sb = ttk.Scrollbar(self.frame, orient='vertical', command=self.datatable.yview)
        self.horizontal_sb = ttk.Scrollbar(self.frame, orient='horizontal', command=self.datatable.xview)
        self.datatable.configure(xscrollcommand=self.horizontal_sb.set, yscrollcommand=self.vertical_sb.set)
        self.label.grid(row=0, column=0, columnspan=2, sticky='w')
        self.datatable.grid(row=1, column=0, sticky='new')
        self.vertical_sb.grid(row=1, column=1, sticky='ns')
        self.horizontal_sb.grid(row=2, column=0, sticky='ew')

        button_frame = ttk.Frame(self.frame)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.grid(row=3, column=0, sticky='ew')

        self.delete_button = ttk.Button(button_frame, text='Delete')
        self.export_button = ttk.Button(button_frame, text='Export all')
        self.delete_button.grid(row=0, column=0, sticky='w')
        self.export_button.grid(row=0, column=1, sticky='e')