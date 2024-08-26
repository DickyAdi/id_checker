import os
import csv
from pathlib import Path
from datetime import datetime

from . import IS_ALL_LOADED, DATATABLE_BATCH, DATATABLE_LOADED_ROWS
from model.debitur import debitur
from views.component import input_group
# from views.app import App


class debitur_controller:
    def __init__(self):
        self.debitur = debitur()

    def search_key(self, key:str):
        res, data = self.debitur.search_record(key)
        return (res, data)
    
    def insert(self, data:dict):
        global IS_ALL_LOADED, DATATABLE_LOADED_ROWS
        last_num = 1 if self.debitur.is_db_empty() else self.debitur.get_total_records()+1
        unique_id = str(f'0-{last_num:04d}')
        data['id'] = unique_id
        new_debitur = self.debitur.create_debitur_from_dict(data)
        response, msg = new_debitur.insert_record()
        IS_ALL_LOADED = DATATABLE_LOADED_ROWS >= self.debitur.get_total_records()
        return (response, msg)
    
    def edit(self, data:dict):
        new_debitur = self.debitur.create_debitur_from_dict(data)
        response, msg = new_debitur.edit_record()
        return (response, msg)
    
    def validate_on_submit(self, data:dict):
        all_valid = True
        for key, val in data.items():
            if not self.debitur.validate(key, val):
                all_valid = False
        return all_valid
    
    def delete(self, key:str):
        global DATATABLE_LOADED_ROWS
        res = self.debitur.delete_record(key)
        if res:
            if DATATABLE_LOADED_ROWS > 0:
                DATATABLE_LOADED_ROWS -= 1
            return (True, f'Data dengan NIK {key} telah di delete!')
        else:
            return (False, f'Terjadi error!')