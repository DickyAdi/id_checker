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

        self.head_frame = ttk.Frame(self, padding=5)
        self.corporate_logo = image_label(self.head_frame, 'apps/assets/img/logo_BJA_PNG(resize).png', 0, 0)
        self.head_frame.grid(row=0, column=0, sticky='nsew')

        #tab 1
        self.notebook = notebook_group(self, 1, 0)
        form_frame = notebook_frame(self.notebook, self.notebook, 'Data', padding=10)

        #form
        self.nik = entry_input(form_frame, 'NIK', 2, 0, required=True)
        self.nama = entry_input(form_frame, 'Nama', 3, 0, required=True)
        self.tanggal_lahir = entry_input(form_frame, 'Tanggal lahir', 4, 0, required=True)
        self.tempat_lahir = entry_input(form_frame, 'Tempat lahir', 4, 1, required=True)
        self.alamat = entry_input(form_frame, 'Alamat', 5, 0, required=True)
        self.nama_ibu_kandung = entry_input(form_frame, 'Nama ibu kandung', 6, 0, required=True)
        self.nama_pasangan = entry_input(form_frame, 'Nama pasangan', 7, 0, required=False)
        self.kolektibilitas = combo_input(form_frame, 'Kolektibilitas', 8, 0, required=True)
        self.keterangan = text_input(form_frame, 'Keterangan', 9, 0, required=False)
        
        #button group
        form_button_group = ttk.Frame(form_frame)
        form_button_group.columnconfigure(0, weight=1)
        form_button_group.columnconfigure(1, weight=0)
        form_button_group.columnconfigure(2, weight=1)
        form_button_group.grid(row=10, column=0, columnspan=2, sticky='ew')
        self.check_button = ttk.Button(form_button_group, text='Check')
        self.check_button.grid(row=0, column=0, sticky='ew', pady=4)
        empty_pad = ttk.Frame(form_button_group, width=4)
        empty_pad.grid(row=0, column=1, sticky='ew')
        self.edit_button = ttk.Button(form_button_group, text='Edit')
        self.edit_button.grid(row=0, column=2, sticky='ew', pady=4)
        self.print_button = ttk.Button(form_button_group, text='Print')
        self.print_button.grid(row=1, column=0, columnspan=3, sticky='ew')

        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)

        #tab 2
        csv_frame = notebook_frame(self.notebook, self.notebook, 'Input excel', padding=10)
        self.file_upload = entry_input(csv_frame, 'File CSV', row=0, col=0, required=True)
        self.upload_button = ttk.Button(csv_frame, text='Upload')
        self.upload_button.grid(row=1, column=0, sticky='w')


        #tab 3
        data_frame = notebook_frame(self.notebook, self.notebook, 'View & export data', padding=10)
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(1, weight=1)
        self.datatable = datatable(data_frame)


        self.columnconfigure(0, weight=1)
        self.bind('<<NotebookTabChanged>>', lambda event: self.update_idletasks())
        sv_ttk.set_theme('dark')
        self.mainloop()

class notebook_frame(ttk.Frame):
    def __init__(self, parent, notebook, text, **kwargs):
        super().__init__(parent, **kwargs)
        notebook.add(self, text=text)

class input_group:
    def __init__(self, parent, var_name:str, row, col, required=True):
        self.row = row
        self.col = col
        if required and var_name[-1] != '*':
            self.var_name = var_name + '*'
        else:
            self.var_name = var_name
        self.frame = ttk.Frame(parent, padding=4)
        self.frame.columnconfigure(0, weight=1)
        self.label = ttk.Label(self.frame, text=self.var_name)
        self.error_label = ttk.Label(self.frame, text='', font=('TkDefaultFont', 8), foreground='red')
        self.var = self.create_entry_var()
        self.reset_bg = self.label.cget('foreground')
        self.label.grid(row=0, column=0, sticky='w')
        self.var.grid(row=1, column=0, sticky='ew')
        self.place_widget()
    def place_widget(self):
        self.frame.grid(row=self.row, column=self.col, sticky='nsew')
    def create_entry_var(self):
        raise NotImplementedError('Method not implemented, override the subclass instead')

class entry_input(input_group):
    def __init__(self, parent, var_name: str, row, col, required=True):
        self.entry = tk.StringVar()
        super().__init__(parent, var_name, row, col, required)
    def create_entry_var(self):
        self.var = ttk.Entry(self.frame, textvariable=self.entry)
        return self.var

class combo_input(input_group):
    def __init__(self, parent, var_name: str, row, col, required=True):
        self.combo_box_values = ['Lancar', 'Kurang lancar', 'Diragukan', 'Macet', 'Daftar hitam']
        self.entry = tk.IntVar()
        super().__init__(parent, var_name, row, col, required)
    def create_entry_var(self):
        self.var = ttk.Combobox(self.frame, values=self.combo_box_values)
        return self.var

class text_input(input_group):
    def __init__(self, parent, var_name: str, row, col, required=True):
        super().__init__(parent, var_name, row, col, required)
    def create_entry_var(self):
        self.var = tk.Text(self.frame, height=5)
        return self.var
    def place_widget(self):
        self.frame.grid(row=self.row, column=self.col, columnspan=2, sticky='ew')

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


class notebook_group(ttk.Notebook):
    def __init__(self, parent, row, col):
        super().__init__(parent)
        self.grid(row=row, column=col, sticky='nsew', padx=10, pady=10)

class image_label(ttk.Label):
    def __init__(self, parent, image_path, row, col):
        super().__init__(parent)
        img = self.to_imagetk(image_path)
        label_image = ttk.Label(parent, image=img)
        label_image.image = img
        label_image.pack()
    def to_imagetk(self, image_path):
        image = Image.open(os.path.join(abs_path, image_path))
        image_tk = ImageTk.PhotoImage(image)
        return image_tk


if __name__ == '__main__':
    App(650, 680)