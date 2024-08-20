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
    def __init__(self, nama, nik, tempat_lahir, tanggal_lahir, alamat, nama_ibu_kandung, kolektibilitas, nama_pasangan=None, keterangan=None):
        self.nama = nama
        self.nik = nik
        self.tempat_lahir = tempat_lahir
        self.tanggal_lahir = tanggal_lahir
        self.alamat = alamat
        self.nama_ibu_kandung = nama_ibu_kandung
        self.kolektibilitas = kolektibilitas
        self.nama_pasangan = nama_pasangan
        self.keterangan = keterangan
    def search_record(key:int, db_name:str=None, root:str='./'):
        db_path = os.path.join(root, DB) if db_name else os.path.join(root, db_name)
        query = f'''
            SELECT * FROM db_checker where nik = :nik
        '''
        param_value = {'nik' : key}
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            result = conn.execute(query, param_value).fetchone()
            return result if result else None