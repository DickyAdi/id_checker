import os
import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from typing import List
import re

IDX_TO_KOLEKTIBILITAS = {
    1 : 'Lancar',
    2 : 'Kurang lancar',
    3 : 'Diragukan',
    4 : 'Macet',
    5 : 'Daftar hitam'
}
KOLEKTIBILITAS_TO_IDX = {
    'Lancar' : 1,
    'Kurang lancar' : 2,
    'Diragukan' : 3,
    'Macet' : 4,
    'Daftar hitam' : 5
}
if getattr(sys, 'frozen', False):
    abs_path = sys._MEIPASS
else:
    abs_path = os.path.abspath('.')
DB = os.path.join(abs_path, 'CHECKER_DATABASE.db')
class debitur:
    def __init__(self, nik='', id='', nama='', tempat_lahir='', tanggal_lahir='', alamat='', nama_ibu_kandung='', kolektibilitas=None, nama_pasangan='', keterangan=''):
        self.id = id
        self.nik = nik
        self.nama = nama
        self.tanggal_lahir = tanggal_lahir
        self.tempat_lahir = tempat_lahir
        self.alamat = alamat
        self.nama_ibu_kandung = nama_ibu_kandung
        self.nama_pasangan = nama_pasangan
        self.kolektibilitas = kolektibilitas
        self.keterangan = keterangan

    def search_record(self, key:int, db_name:str=None, root:str='./'):
        db_path = os.path.join(root, DB) if db_name == None else os.path.join(root, db_name)
        query = f'''
            SELECT * FROM db_checker where nik = :nik
        '''
        param_value = {'nik' : key}
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            result = conn.execute(query, param_value).fetchone()
            if result:
                self.id = result['id']
                self.nik = result['nik']
                self.nama = result['nama']
                self.tanggal_lahir = result['tanggal_lahir']
                self.tempat_lahir = result['tempat_lahir']
                self.alamat = result['alamat']
                self.nama_ibu_kandung = result['nama_ibu_kandung']
                self.nama_pasangan = result['nama_pasangan']
                self.kolektibilitas = result['kolektibilitas']
                self.keterangan = result['keterangan']
                return True
            else:
                False

    def validate_nik(self, value):
        if len(value) == 0 or (not len(value) == 16) and self.check_valid_nik(value):
            return False
        else:
            return True
    
    def validate_nama(self, value):
        if len(value) == 0 or not self.check_valid_alphanum(value, nullable=False):
            return False
        else:
            return True
    
    def validate_tanggal_lahir(self, value):
        if len(value) == 0:
            return False
        else:
            try:
                possible_date = self.parse_date(value, True)
            except ValueError as e:
                return False
            else:
                del possible_date
                return True
    
    def validate_tempat_lahir(self, value):
        if len(value) == 0 or not self.check_valid_alphanum(value, nullable=False):
            return False
        else:
            return True
    
    def validate_alamat(self, value):
        if len(value) == 0:
            return False
        else:
            return True
    
    def validate_nama_pasangan(self, value):
        if not self.check_valid_alphanum(value, nullable=True):
            return False
        else:
            return True
    
    def validate_nama_ibu_kandung(self, value):
        if len(value) == 0 or not self.check_valid_alphanum(value, nullable=False):
            return False
        else:
            return True
    
    def validate_kolektibilitas(self, value):
        if len(value) == 0:
            return False
        else:
            return True
    
    def validate_keterangan(self, value):
        return True
    
    def check_valid_alphanum(self, value, nullable=True):
        pattern_name = re.compile(r"^[A-Za-z0-9.,'`\-\(\)]+$")
        if len(value) == 0 and nullable:
            return True
        else:
            if pattern_name.match(value):
                return True
            else:
                return False
    def check_valid_nik(self, digits):
        pattern = re.compile(r"%[0-9]$")
        if pattern.match(digits):
            return True
        else:
            return False
    def parse_date(self, date_value:str, db_format=True):
        if db_format:
            return datetime.strptime(date_value, '%d-%m-%Y').strftime('%Y-%m-%d')
        else:
            return datetime.strptime(date_value, '%Y-%m-%d').strftime('%d-%m-%Y')

