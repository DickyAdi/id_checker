import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image
import os
import sys
import sv_ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from controller.app_controller import app_controller

from . import component
from controller.datatable_controller import datatable_controller
from controller.import_controller import import_controller

if getattr(sys, 'frozen', False):
    abs_path = sys._MEIPASS
else:
    abs_path = os.path.abspath('.')

class App(tk.Tk):
    def __init__(self, width, height, app_controller:'app_controller'):
        super().__init__()
        self.app_controller = app_controller(self)
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
        self.nik = component.entry_input(form_frame, 'nik', 'NIK', 2, 0, required=True)
        self.nama = component.entry_input(form_frame, 'nama', 'Nama', 3, 0, state='disabled', required=True)
        self.tanggal_lahir = component.entry_input(form_frame, 'tanggal_lahir', 'Tanggal lahir', 4, 0,state='disabled', required=True)
        self.tempat_lahir = component.entry_input(form_frame, 'tempat_lahir', 'Tempat lahir', 4, 1, state='disabled', required=True)
        self.alamat = component.entry_input(form_frame, 'alamat', 'Alamat', 5, 0, state='disabled', required=True)
        self.nama_ibu_kandung = component.entry_input(form_frame, 'nama_ibu_kandung', 'Nama ibu kandung', 6, 0,  state='disabled', required=True)
        self.nama_pasangan = component.entry_input(form_frame, 'nama_pasangan', 'Nama pasangan', 6, 1,  state='disabled', required=False)
        self.kolektibilitas = component.combo_input(form_frame, 'kolektibilitas', 'Kolektibilitas', 7, 0,  state='disabled', required=True)
        self.keterangan = component.text_input(form_frame, 'keterangan', 'Keterangan', 8, 0,  state='disabled', required=False)
        self.form_control = [self.nama, self.tanggal_lahir, self.tempat_lahir, self.alamat, self.nama_ibu_kandung, self.nama_pasangan, self.kolektibilitas, self.keterangan]
        self.nik.var.bind('<FocusOut>', lambda event, widget=self.nik : self.app_controller.check_nik(widget))
        self.nama.var.bind('<FocusOut>', lambda event, widget=self.nama : self.app_controller.check_nama(widget))
        self.tanggal_lahir.var.bind('<FocusOut>', lambda event, widget=self.tanggal_lahir : self.app_controller.check_tanggal_lahir(widget))
        self.tempat_lahir.var.bind('<FocusOut>', lambda event, widget=self.tempat_lahir : self.app_controller.check_tempat_lahir(widget))
        self.alamat.var.bind('<FocusOut>', lambda event, widget=self.alamat : self.app_controller.check_alamat(widget))
        self.nama_ibu_kandung.var.bind('<FocusOut>', lambda event, widget=self.nama_ibu_kandung : self.app_controller.check_nama_ibu_kandung(widget))
        self.nama_pasangan.var.bind('<FocusOut>', lambda event, widget=self.nama_pasangan : self.app_controller.check_nama_pasangan(widget))
        self.kolektibilitas.var.bind('<FocusOut>', lambda event, widget=self.kolektibilitas : self.app_controller.check_kolektibilitas(widget))
        self.keterangan.var.bind('<FocusOut>', lambda event, widget=self.keterangan : self.app_controller.check_keterangan(widget))
        
        #button group
        form_button_group = ttk.Frame(form_frame)
        form_button_group.columnconfigure(0, weight=1)
        form_button_group.columnconfigure(1, weight=0)
        form_button_group.columnconfigure(2, weight=1)
        form_button_group.grid(row=9, column=0, columnspan=2, sticky='ew')
        self.check_button = ttk.Button(form_button_group, text='Check', command=self.app_controller.check_handler)
        self.check_button.grid(row=0, column=0, sticky='ew', pady=4)
        empty_pad = ttk.Frame(form_button_group, width=4)
        empty_pad.grid(row=0, column=1, sticky='ew')
        self.edit_button = ttk.Button(form_button_group, text='Edit', state='disabled', command=self.app_controller.edit_insert_handler)
        self.edit_button.grid(row=0, column=2, sticky='ew', pady=4)
        self.print_button = ttk.Button(form_button_group, text='Print', state='disabled', command=self.app_controller.print_button_handler)
        self.print_button.grid(row=1, column=0, columnspan=3, sticky='ew')

        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)

        #tab 2
        csv_frame = notebook_frame(self.notebook, self.notebook, 'Input excel', padding=10)
        self.file_upload = component.entry_input(csv_frame, 'csv','File CSV', row=0, col=0, required=True, state='readonly')
        self.upload_button = ttk.Button(csv_frame, text='Upload', state='disabled')
        self.import_controller = import_controller(self.file_upload, self.upload_button)
        self.file_upload.var.bind('<Button-1>', lambda event : self.import_controller.upload_file_handler())
        self.upload_button.configure(command=self.import_controller.upload_button_handler)
        self.upload_button.grid(row=1, column=0, sticky='w')


        #tab 3
        data_frame = notebook_frame(self.notebook, self.notebook, 'View & export data', padding=10)
        data_frame.columnconfigure(0, weight=1)
        data_frame.rowconfigure(1, weight=1)
        self.datatable = component.datatable(data_frame)
        self.datatable_controller = datatable_controller(self.datatable)
        self.datatable.delete_button.configure(command=self.datatable_controller.datatable_delete_button_handler)
        self.datatable.export_button.configure(command=self.datatable_controller.datatable_export_button_handler)
        self.datatable.datatable.bind('<Configure>', lambda event : self.datatable_controller.on_scroll_lazy_load(event))
        self.datatable.datatable.bind('<Motion>', lambda event : self.datatable_controller.on_scroll_lazy_load(event))
        self.datatable.datatable.bind('<ButtonRelease-1>', lambda event : self.datatable_controller.datatable_row_click_handler(event))

        self.columnconfigure(0, weight=1)
        self.notebook.bind('<<NotebookTabChanged>>', lambda event : self.datatable_controller.lazy_show_data(event))
        self.bind('<<NotebookTabChanged>>', lambda event: self.update_idletasks())
        sv_ttk.set_theme('dark')
        self.mainloop()

class notebook_frame(ttk.Frame):
    def __init__(self, parent, notebook, text, **kwargs):
        super().__init__(parent, **kwargs)
        notebook.add(self, text=text)

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
