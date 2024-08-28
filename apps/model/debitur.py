import os
import sqlite3
import sys
import csv
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


    def search_record(self, key:int, get=True):
        query = f'''
            SELECT * FROM db_checker where nik = :nik
        '''
        param_value = {'nik' : key}
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            result = conn.execute(query, param_value).fetchone()
            if get:
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
            else:
                if result:
                    return True
                else:
                    return False

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
    
    def batch_insert_records(self, data):
        keys = list(data[0].keys())
        data = [tuple(val.values()) for val in data]
        parameterized_values = ', '.join(['?'] * len(keys))
        query = f'''
            INSERT INTO db_checker ({', '.join(keys)}) VALUES ({parameterized_values})
        '''
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.executemany(query, data)
                conn.commit()
            except sqlite3.IntegrityError as e:
                conn.rollback()
                return (False, 'IntegrityError', str(e))
            except sqlite3.Error as e:
                conn.rollback()
                return (False, 'UnexpectedError', str(e))
            else:
                return (True, 'Success', '')
    
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
    
    def get_max_id(self):
        query = f'''
            SELECT id
            FROM db_checker
            ORDER BY CAST(SUBSTR(id, 3) as INTEGER) DESC
            LIMIT 1
        '''
        with sqlite3.connect(self.db_path) as conn:
            try:
                res = conn.execute(query).fetchone()
            except sqlite3.Error as e:
                return None
            else:
                if res:
                    return int(res[0].split('-')[1])
                else:
                    return None

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
        if len(value) == 0 or (len(value) != 16 or utils.check_valid_nik(value)):
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

    def is_valid_csv_row(self, data:dict):
        error_cols = []
        for key, val in data.items():
            is_valid = self.validate(key, val)
            if not is_valid:
                error_cols.append(key)
        return error_cols

    def read_csv(self, file_path):
        respond = {
            'success' : None,
            'msg' : None,
            'total_rows' : None,
            'validated' : None
        }
        total_rows = 0
        last_id = 1 if self.is_db_empty() else self.get_max_id()+1
        duplicated = set()
        validated = []
        with open(os.path.join(abs_path, file_path), 'r', encoding='utf-8-sig', newline='') as file:
            header = file.readline()
            delim = ',' if len(header.split(',')) > 1 else ';'
            file.seek(0)
            reader = csv.DictReader(file, delimiter=delim)
            for i, row in enumerate(reader):
                is_unique = not self.search_record(row['nik'], False)
                not_duplicate = True if row['nik'] not in duplicated else False
                if is_unique and not_duplicate:
                    duplicated.add(row['nik'])
                    not_valid_rows = self.is_valid_csv_row(row)
                    if not_valid_rows:
                        # return (False, f'Terdapat error di row {i+2} kolom {not_valid_rows}')
                        respond['success'] = False
                        respond['msg'] = f'Terdapat error di row {i+2} kolom {not_valid_rows}'
                        return respond
                    parsed_row = self.parse_data(row)
                    parsed_row['id'] = str(f'0-{last_id:04d}')
                    validated.append(parsed_row)
                    last_id += 1
                    total_rows += 1
                else:
                    # return (False, f"Data dengan NIK {row['nik']} di row {i+2} sudah terdaftar ataupun terdapat duplikat pada file!")
                    respond['success'] = False
                    respond['msg'] = f"Data dengan NIK {row['nik']} di row {i+2} sudah terdaftar ataupun terdapat duplikat pada file!"
                    return respond
            respond['success'] = True
            respond['msg'] = f'Read success'
            respond['total_rows'] = total_rows
            respond['validated'] = validated
            return respond

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
