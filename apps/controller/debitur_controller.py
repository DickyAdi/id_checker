import os
import csv
from pathlib import Path
from datetime import datetime
from xhtml2pdf import pisa

import controller
from model.debitur import debitur
from views.component import input_group

class debitur_controller:
    def __init__(self):
        self.debitur = debitur()

    def search_key(self, key:str):
        res, data = self.debitur.search_record(key)
        return (res, data)
    
    def insert(self, data:dict):
        last_num = 1 if self.debitur.is_db_empty() else self.debitur.get_max_id()+1
        unique_id = str(f'0-{last_num:04d}')
        data['id'] = unique_id
        new_debitur = self.debitur.create_debitur_from_dict(data)
        response, msg = new_debitur.insert_record()
        total_data = self.debitur.get_total_records()
        controller.IS_ALL_LOADED = controller.DATATABLE_LOADED_ROWS >= total_data
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
        res = self.debitur.delete_record(key)
        if res:
            if controller.DATATABLE_LOADED_ROWS > 0:
                controller.DATATABLE_LOADED_ROWS -= 1
            return (True, f'Data dengan NIK {key} telah di delete!')
        else:
            return (False, f'Terjadi error!')

    def create_pdf(self, key:str, path:str):
        possible_path = Path(path)
        status, data = self.debitur.search_record(key)
        html_code = f"""
        <!DOCTYPE html>
        <html lang='en'>
            <head>
                <meta charset='UTF-8' />
                <title>Template PDF Testing</title>
                <style>
                    @page {{
                        size: letter portrait;
                        @frame content_frame {{
                            left: 50pt;
                            width: 512pt;
                            top: 50pt;
                            height: 692pt;
                        }}
                    }}
                    .align-colon {{
                        text-align : center;
                        width : 10pt;
                    }}
                    .first-col {{
                        text-align : left;
                        width: 120pt;
                    }}
                    .main-table {{
                        margin-left: 50px;
                        font-size : 12px;
                    }}
                    p {{
                        font-size : 12px;
                    }}
                </style>
            </head>
            <body>
                <img 
                src='{os.path.join(controller.abs_path,'apps/assets/img/kop_surat.jpg')}'
                alt='Corporate logo'
                style='display:inline-block; width:auto; height:auto; text-align:right;'
                />
                <hr />
                <br>
                <table style='font-size:14px; font-weight: bold;'>
                    <tr>
                        <td>Data debitur</td>
                    </tr>
                </table>
                <br>
                <table class='main-table'>
                    <tr>
                        <td class='first-col'>Id</td>
                        <td class='align-colon'>:</td>
                        <td>{data.id}</td>
                    </tr>
                    <tr>
                        <td class='first-col'>NIK</td>
                        <td class='align-colon'>:</td>
                        <td>{data.nik}</td>
                    </tr>
                    <tr>
                        <td class='first-col'>Nama</td>
                        <td class='align-colon'>:</td>
                        <td>{data.nama}</td>
                    </tr>
                    <tr>
                        <td class='first-col'>Tempat Lahir</td>
                        <td class='align-colon'>:</td>
                        <td>{data.tempat_lahir}</td>
                    </tr>
                    <tr>
                        <td class='first-col'>Tanggal Lahir</td>
                        <td class='align-colon'>:</td>
                        <td>{data.tanggal_lahir}</td>
                    </tr>
                    <tr>
                        <td class='first-col'>Alamat</td>
                        <td class='align-colon'>:</td>
                        <td>{data.alamat}</td>
                    </tr>
                    <tr>
                        <td class='first-col'>Nama Pasangan</td>
                        <td class='align-colon'>:</td>
                        <td>{data.nama_pasangan}</td>
                    </tr>
                    <tr>
                        <td class='first-col'>Nama Ibu Kandung</td>
                        <td class='align-colon'>:</td>
                        <td>{data.nama_ibu_kandung}</td>
                    </tr>
                    <tr>
                        <td class='first-col'>Kolektibilitas</td>
                        <td class='align-colon'>:</td>
                        <td>{data.kolektibilitas}</td>
                    </tr>
                    <tr>
                        <td class='first-col'>Keterangan</td>
                        <td class='align-colon'>:</td>
                        <td>{data.keterangan}</td>
                    </tr>
                </table>
            </body>
        </html>
        """
        if possible_path.is_dir():
            if status:
                file_name = os.path.join(possible_path, f'{data.nama}_{data.nik}_{datetime.now().strftime("%d-%m-%Y")}.pdf')
                try:
                    with open(file_name, 'w+b') as output_file:
                        pdf_writes_status = pisa.CreatePDF(html_code, dest=output_file)
                except Exception as e:
                    return (False, f'Somehting went wrong!\nDetail:{str(e)}')
                else:
                    return (pdf_writes_status, f'Data sudah di cetak! Cek {str(possible_path)}')
            else:
                return (False, f'Data dengan NIK {key} tidak ada!')
        else:
            return (False, f'{str(possible_path)} bukan merupakan sebuah direktori!')