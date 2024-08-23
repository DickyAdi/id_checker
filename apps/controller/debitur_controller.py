import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import List
import re
from typing import TYPE_CHECKING


from model.debitur import debitur
from views.input_component import input_group
from views.app import App


class debitur_controller:
    def __init__(self):
        # self.app = app
        self.debitur = debitur()

    def search_key(self, key:str):
        res = self.debitur.search_record(key)
        return res
    
    # def is_db_empty(self):
    #     return self.debitur.is_db_empty()

    # def get_total_records(self):
    #     return self.debitur.get_total_records()
    
    def insert(self, data:dict):
        last_num = 1 if self.debitur.is_db_empty() else self.debitur.get_total_records()+1
        unique_id = str(f'0-{last_num:04d}')
        data['nik'] = unique_id
        parsed_data = self.debitur.parse_data(data)
        response = self.debitur.insert_record(parsed_data)
        return response
    
    def edit(self, data:dict):
        parsed_data = self.debitur.parse_data(data)
        response = self.debitur.edit_record(parsed_data)
        return response
    
    def validate_on_submit(self, data:dict):
        all_valid = True
        for key, val in data.items():
            if not self.debitur.validate(key, val):
                all_valid = False
        return all_valid

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