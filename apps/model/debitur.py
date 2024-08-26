import os
import sqlite3
import sys
from pathlib import Path
from datetime import datetime
from typing import List
import re

from utils import utils

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
    def __init__(self, db_name:str=None, root:str='./'):
        self.id:str = ''
        self.nik:str = ''
        self.nama:str = ''
        self.tanggal_lahir:str = ''
        self.tempat_lahir:str = ''
        self.alamat:str = ''
        self.nama_ibu_kandung:str = ''
        self.nama_pasangan:str = ''
        self.kolektibilitas:int = None
        self.keterangan:str = ''
        self.keys = ['id', 'nik', 'nama', 'tanggal_lahir', 'tempat_lahir', 'alamat', 'nama_ibu_kandung', 'nama_pasangan', 'kolektibilitas', 'keterangan']
        self.db_path = os.path.join(root, DB) if db_name == None else os.path.join(root, db_name)

    def _get_values(self):
        values = [self.id, self.nik, self.nama, self.tanggal_lahir, self.tempat_lahir, self.alamat, self.nama_ibu_kandung, self.nama_pasangan, self.kolektibilitas, self.keterangan]
        return values

    def create_debitur_from_dict(self, data:dict):
        new_debitur = debitur()
        parsed_data = self.parse_data(data)
        new_debitur.id = parsed_data['id'] if 'id' in parsed_data.keys() else ''
        new_debitur.nik = parsed_data['nik']
        new_debitur.nama = parsed_data['nama']
        new_debitur.tanggal_lahir = parsed_data['tanggal_lahir']
        new_debitur.tempat_lahir = parsed_data['tempat_lahir']
        new_debitur.alamat = parsed_data['alamat']
        new_debitur.nama_ibu_kandung = parsed_data['alamat']
        new_debitur.nama_pasangan = parsed_data['nama_pasangan']
        new_debitur.kolektibilitas = parsed_data['kolektibilitas']
        new_debitur.keterangan = parsed_data['keterangan']
        return new_debitur


    def search_record(self, key:int):
        query = f'''
            SELECT * FROM db_checker where nik = :nik
        '''
        param_value = {'nik' : key}
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            result = conn.execute(query, param_value).fetchone()
            if result:
                result = self.unparse_data(dict(result))
                new_debitur = debitur()
                new_debitur.id = result['id']
                new_debitur.nik = result['nik']
                new_debitur.nama = result['nama']
                new_debitur.tanggal_lahir = result['tanggal_lahir']
                new_debitur.tempat_lahir = result['tempat_lahir']
                new_debitur.alamat = result['alamat']
                new_debitur.nama_ibu_kandung = result['nama_ibu_kandung']
                new_debitur.nama_pasangan = result['nama_pasangan']
                new_debitur.kolektibilitas = result['kolektibilitas']
                new_debitur.keterangan = result['keterangan']
                return (True, new_debitur)
            else:
                return (False, None)

    def insert_record(self):
        data_parameterized = ', '.join(['?'] * len(self._get_values()))
        query = f'''
            INSERT INTO db_checker ({', '.join(self.keys)})
            VALUES ({data_parameterized})
        '''
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(query, self._get_values())
                conn.commit()
            except sqlite3.IntegrityError as e:
                conn.rollback()
                print(e)
                return (False, 'IntegrityError')
            except sqlite3.Error as e:
                conn.rollback()
                print(e)
                return (False, 'UnexpectedError')
            else:
                return (True, 'Success')
    
    def delete_record(self, key):
        query = f'''
            DELETE FROM db_checker
            WHERE nik = ?
        '''
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(query, (key,))
                conn.commit()
            except sqlite3.Error as e:
                conn.rollback()
                return False
            else:
                return True

    def get_total_records(self):
        query = f'''
            SELECT COUNT(nik) FROM db_checker
        '''
        with sqlite3.connect(self.db_path) as conn:
            try:
                res = conn.execute(query).fetchone()
            except sqlite3.Error as e:
                print(f'Something went wrong {e}')
                return 0
            else:
                return res[0]

    def edit_record(self):
        keys = [key for key in self.keys if key != 'id']
        values = [val for val in self._get_values() if val != self.id]
        data_parameterized = ', '.join([f'{field} = :{field}' for field in keys])
        parameterized_values = {field:data for field,data in zip(keys, values)}
        condition_clause = f'nik = :nik'
        query = f'''
            UPDATE db_checker
            SET {data_parameterized}
            WHERE {condition_clause}
        '''
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute(query, parameterized_values)
                conn.commit()
            except sqlite3.Error as e:
                print(query)
                conn.rollback()
                return (False, f'Something went wrong {e}')
            else:
                return (True, 'Data berhasil di edit.')
    
    def get_all_records(self, offset=0, limit=0):
        if limit:
            query = f'''
                SELECT * FROM db_checker LIMIT {limit} OFFSET {offset}
            '''
        else:
            query = f'''
                SELECT * FROM db_checker
            '''
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.row_factory = sqlite3.Row
                res = conn.execute(query).fetchall()
                res = [self.unparse_data(dict(parsed)) for parsed in res]
            except sqlite3.Error as e:
                return (False, None)
            else:
                return (True, res)


    def is_db_empty(self):
        return self.get_total_records() == 0
    

    def validate_nik(self, value):
        if len(value) == 0 or (not len(value) == 16) and utils.check_valid_nik(value):
            return False
        else:
            return True
    
    def validate_nama(self, value):
        if len(value) == 0 or not utils.check_valid_alphanum(value, nullable=False):
            return False
        else:
            return True
    
    def validate_tanggal_lahir(self, value):
        if len(value) == 0:
            return False
        else:
            try:
                possible_date = utils.parse_date(value, True)
            except ValueError as e:
                return False
            else:
                del possible_date
                return True
    
    def validate_tempat_lahir(self, value):
        if len(value) == 0 or not utils.check_valid_alphanum(value, nullable=False):
            return False
        else:
            return True
    
    def validate_alamat(self, value):
        if len(value) == 0:
            return False
        else:
            return True
    
    def validate_nama_pasangan(self, value):
        if not utils.check_valid_alphanum(value, nullable=True):
            return False
        else:
            return True
    
    def validate_nama_ibu_kandung(self, value):
        if len(value) == 0 or not utils.check_valid_alphanum(value, nullable=False):
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
    
    def validate(self, name, value):
        if name == 'nik':
            return self.validate_nik(value)
        elif name == 'nama':
            return self.validate_nama(value)
        elif name == 'tanggal_lahir':
            return self.validate_tanggal_lahir(value)
        elif name == 'tempat_lahir':
            return self.validate_tempat_lahir(value)
        elif name == 'alamat':
            return self.validate_alamat(value)
        elif name == 'nama_pasangan':
            return self.validate_nama_pasangan(value)
        elif name == 'nama_ibu_kandung':
            return self.validate_nama_ibu_kandung(value)
        elif name == 'kolektibilitas':
            return self.validate_kolektibilitas(value)
        elif name == 'keterangan':
            return self.validate_keterangan(value)
    
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
    #     """Parse date input

    #     Args:
    #         date_value (str): Date value
    #         db_format (bool, optional): If True, it will parse the value to database format, else it will parse the value to application format. Defaults to True.

    #     Returns:
    #         str: parsed date
    #     """
    #     if db_format:
    #         return datetime.strptime(date_value, '%d-%m-%Y').strftime('%Y-%m-%d')
    #     else:
    #         return datetime.strptime(date_value, '%Y-%m-%d').strftime('%d-%m-%Y')

    def parse_data(self, data:dict):
        for key, val in data.items():
            if key == 'nik':
                data[key] = int(val)
            elif key == 'tanggal_lahir':
                data[key] = utils.parse_date(val)
            elif key == 'kolektibilitas':
                data[key] = int(KOLEKTIBILITAS_TO_IDX[val])
            elif key == 'keterangan':
                data[key] = val.strip()
        return data
    
    def unparse_data(self, data:dict):
        for key, val in data.items():
            if key == 'nik':
                data[key] = str(val)
            elif key == 'tanggal_lahir':
                data[key] = utils.parse_date(val, False)
            elif key == 'kolektibilitas':
                data[key] = str(IDX_TO_KOLEKTIBILITAS[val])
            elif key == 'keterangan':
                data[key] = val.strip()
        return data
