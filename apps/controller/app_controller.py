import sys
import os
from pathlib import Path
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import List
import re

from utils import utils
from views.app import App
from views.input_component import input_group
from model.debitur import debitur
from services.debitur_service import debitur_service
from . import DATATABLE_BATCH, DATATABLE_LOADED_ROWS, IS_ALL_LOADED

class app_controller:
    def __init__(self, app:App):
        self.app = app
        # self.debitur = debitur()
        self.debitur_service = debitur_service()

    def check_handler(self):
        key = self.app.nik.var.get()
        res = self.debitur_service.find_record_by_key(key)
        if res:
            [var.enable_state() for var in self.app.form_control]
            self.app.nik.set_value(res.nik)
            self.app.nama.set_value(res.nama)
            self.app.tanggal_lahir.set_value(res.tanggal_lahir)
            self.app.tempat_lahir.set_value(res.tempat_lahir)
            self.app.alamat.set_value(res.alamat)
            self.app.nama_pasangan.set_value(res.nama_pasangan)
            self.app.nama_ibu_kandung.set_value(res.nama_ibu_kandung)
            self.app.kolektibilitas.set_value(res.kolektibilitas)
            self.app.keterangan.set_value(res.keterangan)
        else:
            response = messagebox.askquestion('Question', 'Data tidak terdaftar, input baru?')
            if response == 'yes':
                self.app.edit_button.configure(text='Insert', state='normal')
                [var.enable_state() for var in self.app.form_control]
            else:
                self.app.edit_button.configure(text='Edit', state='disabled')
                self.clear_all_input()
                # self.app.nik.clear_value()
                # for var in self.app.form_control:
                #     var.clear_value()
                #     var.disable_state()

    def clear_all_input(self):
        self.app.nik.clear_value()
        for var in self.app.form_control:
            var.clear_value()
            var.disable_state()

    def edit_insert_handler(self):
        # global IS_ALL_LOADED, DATATABLE_LOADED_ROWS
        # values = [self.app.nik.get_value()] + [var.get_value() for var in self.app.form_control]
        # var_name = [self.app.nik.var_name] + [var.var_name for var in self.app.form_control]
        data = {'nik' : self.app.nik.get_value(),
                'nama' : self.app.nama.get_value(),
                'tempat_lahir' : self.app.tempat_lahir.get_value(),
                'tanggal_lahir' : self.app.tanggal_lahir.get_value(),
                'alamat' : self.app.alamat.get_value(),
                'nama_ibu_kandung' : self.app.nama_ibu_kandung.get_value(),
                'kolektibilitas' : self.app.kolektibilitas.get_value(),
                'nama_pasangan' : self.app.nama_pasangan.get_value(),
                'keterangan' : self.app.keterangan.get_value()
        }
        if self.app.edit_button['text'] == 'Insert':
            if self.debitur_service.validate_on_submit_service(data):
                response, msg = self.debitur_service.insert_to_db(data)
                if response:
                    messagebox.showinfo('Success', 'Data sukses di input!')
                    self.clear_all_input()
                    self.app.edit_button.configure(text='Edit', state='disabled')
                else:
                    if msg == 'IntegrityError':
                        messagebox.showerror('Failed', 'NIK sudah terdaftar!')
                    elif msg == 'UnexpectedError':
                        messagebox.showerror('Failed', 'Unexpected Error!')
                    self.clear_all_input()
        elif self.app.edit_button['text'] == 'Edit':
            if self.debitur_service.validate_on_submit_service(data):
                response, msg = self.debitur_service.edit_record_service(data)
                if response:
                    messagebox.showinfo('Success', msg)
                    self.clear_all_input()
                    self.app.edit_button.configure(state='disabled')
                else:
                    messagebox.showerror('Failed', msg)
            else:
                messagebox.showerror('Invalid input', 'Cek ulang data!')

    def check_nik(self, widget:input_group):
        value = widget.var.get()
        if len(value) == 0 or (not len(value) == 16) and utils.check_valid_nik(value):
            widget.show_label_error('Digit NIK tidak sesuai atau data tidak boleh kosong.')
        else:
            widget.hide_label_error()
    
    def check_nama(self, widget:input_group):
        value = widget.var.get()
        if len(value) == 0 or not utils.check_valid_alphanum(value, nullable=False):
            widget.show_label_error('Nama harus alphanumeric atau data tidak boleh kosong.')
        else:
            widget.hide_label_error()
    
    def check_tanggal_lahir(self, widget:input_group):
        value = widget.var.get()
        if len(value) == 0:
            widget.show_label_error('Data tidak boleh kosong.')
        else:
            try:
                possible_date = utils.parse_date(value, True)
            except ValueError as e:
                widget.show_label_error('Format tidak sesuai!')
            else:
                del possible_date
                widget.hide_label_error()
    
    def check_tempat_lahir(self, widget:input_group):
        value = widget.var.get()
        if len(value) == 0 or not utils.check_valid_alphanum(value, nullable=False):
            widget.show_label_error('Tempat lahir harus alphanumeric atau data tidak boleh kosong.')
        else:
            widget.hide_label_error()
    
    def check_alamat(self, widget:input_group):
        value = widget.var.get()
        if len(value) == 0:
            widget.show_label_error('Data tidak boleh kosong.')
        else:
            widget.hide_label_error()
    
    def check_nama_pasangan(self, widget:input_group):
        value = widget.var.get()
        if not utils.check_valid_alphanum(value, nullable=True):
            widget.show_label_error('Nama pasangan harus alphanumeric.')
        else:
            widget.hide_label_error()
    
    def check_nama_ibu_kandung(self, widget:input_group):
        value = widget.var.get()
        if len(value) == 0 or not utils.check_valid_alphanum(value, nullable=False):
            widget.show_label_error('Nama ibu kandung harus alphanumeric dan tidak boleh kosong.')
        else:
            widget.hide_label_error()
    
    def check_kolektibilitas(self, widget:input_group):
        value = widget.var.get()
        if len(value) == 0:
            widget.show_label_error('Kolektibilitas harus diisi')
        else:
            widget.hide_label_error()
    
    def check_keterangan(self, widget:input_group):
        pass



    # def check_nik(self, widget:input_group):
    #     value = widget.var.get()
    #     if not self.debitur.validate_nik(value):
    #         widget.show_label_error('Digit NIK tidak sesuai atau data tidak boleh kosong.')
    #     else:
    #         widget.hide_label_error()
    
    # def check_nama(self, widget:input_group):
    #     value = widget.var.get()
    #     if not self.debitur.validate_nama(value):
    #         widget.show_label_error('Nama harus alphanumeric atau data tidak boleh kosong.')
    #     else:
    #         widget.hide_label_error()
    
    # def check_tanggal_lahir(self, widget:input_group):
    #     value = widget.var.get()
    #     if not self.debitur.validate_tanggal_lahir(value):
    #         widget.show_label_error('Data tidak boleh kosong atau format tidak sesuai.')
    #     else:
    #         widget.hide_label_error()
    
    # def check_tempat_lahir(self, widget:input_group):
    #     value = widget.var.get()
    #     if not self.debitur.validate_tempat_lahir(value):
    #         widget.show_label_error('Tempat lahir harus alphanumeric atau data tidak boleh kosong.')
    #     else:
    #         widget.hide_label_error()
    
    # def check_alamat(self, widget:input_group):
    #     value = widget.var.get()
    #     if not self.debitur.validate_alamat(value):
    #         widget.show_label_error('Data tidak boleh kosong.')
    #     else:
    #         widget.hide_label_error()
    
    # def check_nama_pasangan(self, widget:input_group):
    #     value = widget.var.get()
    #     if not self.debitur.validate_nama_pasangan(value):
    #         widget.show_label_error('Nama pasangan harus alphanumeric.')
    #     else:
    #         widget.hide_label_error()
    
    # def check_nama_ibu_kandung(self, widget:input_group):
    #     value = widget.var.get()
    #     if not self.debitur.validate_nama_ibu_kandung(value):
    #         widget.show_label_error('Nama ibu kandung harus alphanumeric dan tidak boleh kosong.')
    #     else:
    #         widget.hide_label_error()
    
    # def check_kolektibilitas(self, widget:input_group):
    #     value = widget.var.get()
    #     if not self.debitur.validate_kolektibilitas(value):
    #         widget.show_label_error('Kolektibilitas harus diisi')
    #     else:
    #         widget.hide_label_error()
    
    # def check_keterangan(self, widget:input_group):
    #     pass
    
    # def check_valid_alphanum(self, value, nullable=True):
    #     pattern_name = re.compile(r"^[A-Za-z0-9.,'`\-\(\)]+$")
    #     if len(value) == 0 and nullable:
    #         return True
    #     else:
    #         if pattern_name.match(value):
    #             return True
    #         else:
    #             return False
    # def check_valid_nik(self, digits):
    #     pattern = re.compile(r"%[0-9]$")
    #     if pattern.match(digits):
    #         return True
    #     else:
    #         return False
    # def parse_date(self, date_value:str, db_format=True):
    #     if db_format:
    #         return datetime.strptime(date_value, '%d-%m-%Y').strftime('%Y-%m-%d')
    #     else:
    #         return datetime.strptime(date_value, '%Y-%m-%d').strftime('%d-%m-%Y')