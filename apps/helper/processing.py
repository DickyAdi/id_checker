import sys
import os
from pathlib import Path
import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import datetime as dt
from typing import List
import re
from PIL import ImageTk, Image
from xhtml2pdf import pisa

# from helper.dbconnect import dbconnect
import helper.dbconnect as dbconnect

if getattr(sys, 'frozen', False):
    abs_path = sys._MEIPASS
else:
    abs_path = os.path.abspath('.')

TREEVIEW_BATCH = 20
TREEVIEW_LOADED_ROWS = 0
ALL_DATA_LOADED = False

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

def to_imagetk(image_path:str):
    image = Image.open(os.path.join(abs_path, image_path))
    imagetk = ImageTk.PhotoImage(image)
    return imagetk

def insert_process(fields:List[tuple]):
    """insert a new data to the database

    Args:
        fields (List[Tuple]): List of tuples containing the data fields

    Returns:
        bool: Response of the insert process to the database, if True the process succeed otherwise False
    """
    global ALL_DATA_LOADED, TREEVIEW_LOADED_ROWS
    last_num = 1 if is_db_empty() else dbconnect.get_total_records()+1
    var = [var.get() if not isinstance(var, tk.Text) else var.get('1.0', tk.END) for var, _, x, y, z in fields]
    unique_id = str(f'0-{last_num:04d}')
    var.append(unique_id)
    var_name = [var_name for _, var_name, x, y, z in fields]
    var_name.append('id')
    data = (var_name, var)
    parsed_data = parse_input(data)
    response = dbconnect.insert_record(parsed_data)
    total_data = dbconnect.get_total_records()
    ALL_DATA_LOADED = TREEVIEW_LOADED_ROWS >= total_data
    return response

def edit_process(fields:List[tuple]):
    var = [var.get() if not isinstance(var, tk.Text) else var.get('1.0', tk.END) for var, _, x, y, z in fields]
    var_name = [var_name for _, var_name, x, y, z in fields]
    data = (var_name, var)
    parsed_data = parse_input(data)
    response = dbconnect.edit_record(parsed_data)
    return response

def processEntry(nik:ttk.Entry, nama:ttk.Entry, tanggal_lahir:ttk.Entry, tempat_lahir:ttk.Entry, alamat:ttk.Entry, nama_pasangan:ttk.Entry, nama_ibu_kandung, keterangan:tk.Text, kolektibilitas:ttk.Combobox,
                 nik_entry:tk.StringVar, nama_entry:tk.StringVar, tanggal_lahir_entry:tk.StringVar, tempat_lahir_entry:tk.StringVar, alamat_entry:tk.StringVar, nama_pasangan_entry:tk.StringVar, nama_ibu_kandung_entry,
                 editButton:ttk.Button, printButton:ttk.Button):
    """Processing an entry, whether its check, insert, or edit

    Args:
        nik (ttk.Entry): NIK input variable, must be filled
        nama (ttk.Entry): Nama input variable, must be filled
        tanggal_lahir (ttk.Entry): Tanggal lahir input variable, must be filled
        tempat_lahir (ttk.Entry): Tempat lahir input variable, must be filled
        alamat (ttk.Entry): Alamat input variable, must be filled
        nama_pasangan (ttk.Entry): Nama pasangan input variable, optional
        nama_ibu_kandung (ttk.Entry): Nama ibu kandung input variable, must be filled
        keterangan (tk.Text): Keterangan input variable, optional
        kolektibilitas (ttk.Combobox): Kolektibilitas input variable, must be filled
        nik_entry (tk.StringVar): NIK placeholder variable
        nama_entry (tk.StringVar): Nama placeholder variable
        tanggal_lahir_entry (tk.StringVar): Tanggal lahir placeholder variable
        tempat_lahir_entry (tk.StringVar): Tempat lahir placeholder variable
        alamat_entry (tk.StringVar): Alamat placeholder variable
        nama_pasangan_entry (tk.StringVar): Nama pasangan placeholder variable
        nama_ibu_kandung_entry (tk.StringVar): Nama ibu kandung placeholder variable
        editButton (ttk.Button): Edit button, later will be modified according to the condition
        printButton (ttk.Button): Print button, later will be modified according to the condition
    """
    key = nik.get()
    res = dbconnect.search_record(key)
    listVar = [nama, tanggal_lahir, tempat_lahir, alamat, nama_pasangan, nama_ibu_kandung, keterangan, kolektibilitas] #to make it easy to disable an input 
    #check whether search is found or not
    if res:
        #if found, proceed to possible edit by setting the edit button state, set the input state to normal, and fill the input with the record found data
        editButton.configure(state='normal')
        printButton.configure(state='normal')
        [var.configure(state='normal') for var in listVar]
        setEntry(nik_entry, res, 'nik')
        setEntry(nama_entry, res, 'nama')
        setEntry(tanggal_lahir_entry, res, 'tanggal_lahir')
        setEntry(tempat_lahir_entry, res, 'tempat_lahir')
        setEntry(alamat_entry, res, 'alamat')
        setEntry(nama_pasangan_entry, res, 'nama_pasangan')
        setEntry(nama_ibu_kandung_entry, res, 'nama_ibu_kandung')
        setText(keterangan, res, 'keterangan')
        setCombo(kolektibilitas, res, 'kolektibilitas')
    else:
        #if not found, ask if insert or ignore
        response = messagebox.askquestion('Question', 'No records found, insert instead?')
        #if insert, set edit button text to Insert and state to normal. Later in edit_button_handler, the process will check the button text value whether its Edit or Insert
        if response == 'yes':
            editButton.configure(text='Insert', state='normal')
            [var.configure(state='normal') if not isinstance(var, ttk.Combobox) else var.configure(state='readonly') for var in listVar]
        #if not insert, set edit button text back to Edit , state to disabled while clearing all of the input box, and disabled all the input state except NIK
        else:
            editButton.configure(text='Edit', state='disabled')
            nik.delete(0, tk.END)
            for var in listVar:
                if not isinstance(var, ttk.Combobox):
                    if isinstance(var, tk.Text):
                        var.delete('1.0', tk.END)
                    elif len(var.get()) != 0:
                        var.delete(0, tk.END)
                else:
                    var.set('')
                var.configure(state='disabled')

def parse_date(date_value:str):
    """Parse input string date to database format date

    Args:
        date_value (str): Application formatted date value

    Returns:
        str: Formatted date match for database 
    """
    possible_date = datetime.strptime(date_value, '%d-%m-%Y').strftime('%Y-%m-%d')
    return possible_date

def unparse_date(date_value:str):
    """Parse the database format date to application date

    Args:
        date_value (str): Database formatted date value

    Returns:
        str: Formatted date match for application
    """
    possible_date = datetime.strptime(date_value, '%Y-%m-%d').strftime('%d-%m-%Y')
    return possible_date

def parse_input(data:tuple):
    """Parse the input to match the format of the database

    Args:
        data (Tuple(List, List)): Tuple of 2 Lists, which are var_name and var. var_name match with the database column name.

    Returns:
        Tuple(List, List): Tuple of 2 Lists, which are var_name and var. var_name match with the database column name.
    """
    var_name, var = data
    for i in range(len(var_name)):
        if var_name[i] == 'nik':
            var[i] = int(var[i])
        elif var_name[i] == 'tanggal_lahir':
            var[i] = parse_date(var[i])
        elif var_name[i] == 'kolektibilitas':
            var[i] = int(KOLEKTIBILITAS_TO_IDX[var[i]])
        elif var_name[i] == 'keterangan':
            var[i] = var[i].strip()
    return (var_name, var)

def unparse_input(data:tuple):
    """Unparse the data to match the format of the program

    Args:
        data (tuple(List, List)): Tuple of 2 lists, which are var_name and var. var_name must match with the database column name

    Returns:
        Tuple(List, List): Tuple of 2 lists, which are var_name and var. var_name matched with the database column name
    """
    var_name, var = data
    for i in range(len(var_name)):
        if var_name[i] == 'nik':
            var[i] = str(var[i])
        elif var_name[i] == 'tanggal_lahir':
            var[i] = unparse_date(var[i])
        elif var_name[i] == 'kolektibilitas':
            var[i] = str(IDX_TO_KOLEKTIBILITAS[var[i]])
        elif var_name[i] == 'keterangan':
            var[i] = var[i].strip()
    return (var_name, var)


def setEntry(var:ttk.Entry, val:dict, param:str):
    """Set the Entry value in the views

    Args:
        var (tk.StringVar): Entry value placeholder
        val (Dict): Dictionary of the search result
        param (str): Name of selected data
    """
    if param == 'tanggal_lahir':
        var.set(unparse_date(val[param]))
    else:
        var.set(val[param])

def setText(var:tk.Text, val:dict, param:str):
    """Set the Text value in the views

    Args:
        var (tk.StringVar): Text value placeholder
        val (Dict): Dictionary of the search result
        param (str): Name of selected data
    """
    var.delete('1.0', tk.END)
    if val[param]:
        var.insert(tk.END, val[param])

def setCombo(var:ttk.Combobox, val:dict, param:str):
    """Set the Combobox value in the views

    Args:
        var (tk.IntVar): _description_
        val (Dict): Dictionary of the search result
        param (str): Name of the selected data
    """
    var.set(IDX_TO_KOLEKTIBILITAS[val[param]])

def validate_input(var:ttk.Entry|ttk.Combobox|tk.Text, var_name:str, reset_bg:str, var_label:ttk.Label, error_label:ttk.Label):
    """Real-time input validation, used in the input box in the views

    Args:
        var (ttk.Entry | ttk.Combobox | tk.Text): Input variable reference (pass by reference)
        var_name (str): Name of the selected input and must match the name of the column on the database
        reset_bg (str): Color to reset error label color back to default
        var_label (ttk.Label): Label of the input
        error_label (ttk.Label): Error label of the input
    """
    def check_valid_alphanum(name, nullable=True):
        pattern_name = re.compile(r"^[A-Za-z0-9.', \-]+$")
        if len(name) == 0 and nullable:
            return True
        else:
            if pattern_name.match(name):
                return True
            else:
                return False
    def check_valid_nik(digits):
        pattern = re.compile(r"%[0-9]$")
        if pattern.match(digits):
            return True
        else:
            return False

    if var_name == 'nik':
        if len(var.get()) == 0 or (not len(var.get()) == 16 and check_valid_nik(var.get())):
            var_label.configure(foreground='red')
            error_label.configure(text='Digit NIK tidak sesuai atau data tidak boleh kosong')
            return False
        else:
            var_label.configure(foreground=reset_bg)
            error_label.configure(text='')
            return True
    elif var_name == 'nama':
        if len(var.get()) == 0 or not check_valid_alphanum(var.get(), nullable=False):
            var_label.configure(foreground='red')
            error_label.configure(text='Nama harus alphanumeric atau data tidak boleh kosong')
            return False
        else:
            var_label.configure(foreground=reset_bg)
            error_label.configure(text='')
            return True
    elif var_name == 'tanggal_lahir':
        if len(var.get()) == 0:
            var_label.configure(foreground='red')
            error_label.configure(text='Data tidak boleh kosong')
            return False
        else:
            try:
                possibleDate = parse_date(var.get())
            except ValueError:
                var_label.configure(foreground='red')
                error_label.configure(text='Pastikan format tanggal sudah sesuai dan benar')
                return False
            else:
                var_label.configure(foreground=reset_bg)
                error_label.configure(text='')
                del possibleDate
                return True
    elif var_name == 'tempat_lahir':
        if len(var.get()) == 0 or not check_valid_alphanum(var.get(), nullable=False):
            var_label.configure(foreground='red')
            error_label.configure(text='Tempat lahir harus alphanumeric atau data tidak boleh kosong')
            return False
        else:
            var_label.configure(foreground=reset_bg)
            error_label.configure(text='')
            return True
    elif var_name == 'alamat':
        if len(var.get()) == 0:
            var_label.configure(foreground='red')
            error_label.configure(text='Data tidak boleh kosong')
            return False
        else:
            var_label.configure(foreground=reset_bg)
            error_label.configure(text='')
            return True
    elif var_name == 'nama_pasangan':
        if not check_valid_alphanum(var.get()):
            var_label.configure(foreground='red')
            error_label.configure(text='Nama pasangan harus alphanumeric')
            return False
        else:
            var_label.configure(foreground=reset_bg)
            error_label.configure(text='')
            return True
    elif var_name == 'nama_ibu_kandung':
        if len(var.get()) == 0 or not check_valid_alphanum(var.get(), nullable=False):
            var_label.configure(foreground='red')
            error_label.configure(text='Nama ibu kandung harus alphanumeric')
            return False
        else:
            var_label.configure(foreground=reset_bg)
            error_label.configure(text='')
            return True
    elif var_name == 'kolektibilitas':
        if len(var.get()) == 0:
            var_label.configure(foreground='red')
            error_label.configure(text='Data tidak boleh kosong')
            return False
        else:
            var_label.configure(foreground=reset_bg)
            error_label.configure(text='')
            return True
    elif var_name == 'keterangan':
        return True

def validate_submit(fields_list:List):
    """Validate input on submit, employ validate_input to validate all the inputs

    Args:
        fields_list (List[Tuples]): A list containing all the input used in the validate_input

    Returns:
        bool: If True then all input is valid, otherwise False
    """
    all_valid = True
    for var, var_name, reset_bg, label, label_error in fields_list:
        if not validate_input(var, var_name, reset_bg, label, label_error):
            all_valid = False
    return all_valid

def clear_all_input(input_fields:List):
    """Clear all values from the input in the views

    Args:
        input_fields (List): List of input variables
    """
    for field in input_fields:
        if isinstance(field, ttk.Combobox):
            field.set('')
        elif isinstance(field, ttk.Entry):
            field.delete(0, tk.END)
        elif isinstance(field, tk.Text):
            field.delete('1.0', tk.END)

def upload_file_handler(entry_var:tk.StringVar, upload_button:ttk.Button):
    """Handling an upload file Entry by passing the path of the files

    Args:
        entry_var (tk.StringVar): Value placeholder of the file path
        upload_button (ttk.Button): Form upload button
    """
    filetypes = [("Excel csv format file", "*.csv")]
    try:
        file_path = filedialog.askopenfilename(title='Select file',filetypes=filetypes)
        entry_var.set(file_path)
        if file_path:
            upload_button.configure(state='normal')
    except:
        messagebox.showerror('Error', 'Terjadi error!')

def validate_upload(entry_var:tk.StringVar):
    """Validate a file upload

    Args:
        entry_var (tk.StringVar): Value placeholder of the file path

    Returns:
        bool: True if validated, False otherwise
    """
    if entry_var:
        possible_path = Path(entry_var.get())
        if possible_path.suffix == '.csv':
            return True
        else:
            return False
    else:
        return False

def validate_row_csv(dict_row:dict):
    """Validate each row from csv

    Args:
        dict_row (dict): dictionary read from csv

    Returns:
        List: List of columns that contain error values
    """
    error_list = []
    def check_valid_alphanum(name, nullable=True):
        pattern_name = re.compile(r"^[A-Za-z0-9.', \-\(\)]+$")
        if len(name) == 0 and nullable:
            return True
        else:
            if pattern_name.match(name):
                return True
            else:
                return False

    def check_valid_nik(digits):
        pattern = re.compile(r"^[0-9]$")
        return True if pattern.match(digits) else False

    for key, val in dict_row.items():
        if key == 'nik':
            if len(val) == 0 or (not len(val) == 16 and check_valid_nik(val)):
                error_list.append(key)
        elif key == 'nama':
            if len(val) == 0 or not check_valid_alphanum(val, False):
                error_list.append(key)
        elif key == 'tanggal_lahir':
            # print(val)
            # print(len(val))
            if len(val) == 0:
                error_list.append(key)
            else:
                # print(datetime.strptime(val, "%d-%m-y").strftime("%Y-%m-%d"))
                try:
                    possible_date = parse_date(val)
                    # print(possible_date)
                except:
                    error_list.append(key)
        elif key == 'tempat_lahir':
            if len(val) == 0 or not check_valid_alphanum(val, False):
                error_list.append(key)
        elif key == 'alamat':
            if len(val) == 0:
                error_list.append(key)
        elif key == 'nama_pasangan':
            if not check_valid_alphanum(val):
                error_list.append(key)
        elif key == 'nama_ibu_kandung':
            if not check_valid_alphanum(val, False):
                error_list.append(key)
        elif key == 'keterangan':
            continue
        elif key == 'kolektibilitas':
            if len(val) == 0:
                error_list.append(key)
    return error_list

def upload_process(entry_var:tk.StringVar):
    """Whole process of inserting records via .csv files

    Args:
        entry_var (tk.StringVar): Value placeholder of the file path

    Returns:
        Tuple(bool, str): Tuple of Success boolean and message to views
    """
    global ALL_DATA_LOADED, TREEVIEW_LOADED_ROWS
    def format_to_parse(dict_value):
        var_name = list(dict_value.keys())
        var = list(dict_value.values())
        return (var_name, var)
    def parsed_to_row(tuple_values):
        var_names, vars = tuple_values
        new_row = {}
        for var_name, var in zip(var_names, vars):
            new_row[var_name] = var
        return new_row
    if validate_upload(entry_var):
        total_rows = 0
        last_id = 1 if is_db_empty() else dbconnect.get_total_records()+1
        validated = []
        duplicated_records = set()
        with open(os.path.join(abs_path, entry_var.get()), 'r', encoding='utf-8-sig', newline='') as file:
            header = file.readline()
            delim = ',' if len(header.split(',')) > 1 else ';'
            file.seek(0)
            reader = csv.DictReader(file, delimiter=delim)
            for i, row in enumerate(reader):
                is_unique = True if dbconnect.search_record(row['nik']) == None else False
                not_duplicate = True if row['nik'] not in duplicated_records else False
                if is_unique and not_duplicate:
                    duplicated_records.add(row['nik'])
                    not_valid = validate_row_csv(row)
                    if not_valid:
                        return (False, f'Terdapat error di row {i+2} kolom {not_valid}')
                    parsed_row = parsed_to_row(parse_input(format_to_parse(row)))
                    parsed_row['id'] = str(f'0-{last_id:04d}')
                    validated.append(parsed_row)
                    last_id += 1
                    total_rows += 1
                else:
                    return (False, f"Data dengan NIK {row['nik']} di row {i+2} sudah terdaftar atau terdapat duplikat pada file!")
        res, msg = dbconnect.insert_record_via_csv(validated)
        if res:
            total_data = dbconnect.get_total_records()
            ALL_DATA_LOADED = TREEVIEW_LOADED_ROWS >= total_data
            return (True, f'{total_rows} Data berhasil di insert')
        else:
            if msg == 'IntegrityError':
                return (False, 'Pastikan data di dalam csv adalah unique!')
            elif msg == 'UnexpectedError':
                return (False, 'Unexpected Error. Error di database!')
    else:
        return (False, 'Pastikan file yang di-upload adalah file csv')

def show_all_data(tree_view:ttk.Treeview):
    """Show all data from database to view using ttk.Treeview

    Args:
        tree_view (ttk.Treeview): Treeview variable where the data will be shown
        loaded_rows (int): Number of loaded rows to indicate the range of the next lazy load
        batch (int): Number of records that will be loaded in each batch

    Returns:
        bool: True if succeed otherwise False
    """
    global TREEVIEW_BATCH, ALL_DATA_LOADED, TREEVIEW_LOADED_ROWS
    if ALL_DATA_LOADED:
        return False
    else:
        total_records = dbconnect.get_total_records()
        fields = ['id', 'nik', 'nama', 'tanggal_lahir', 'tempat_lahir', 'alamat', 'nama_pasangan', 'nama_ibu_kandung', 'kolektibilitas', 'keterangan']
        success, data = dbconnect.select_all_records(limit=TREEVIEW_BATCH, offset=TREEVIEW_LOADED_ROWS)
        if success and data:
            for row in data:
                _, unparsed_value = unparse_input((fields, list(row)))
                TREEVIEW_LOADED_ROWS += 1
                tree_view.insert('', tk.END, values=unparsed_value)
            ALL_DATA_LOADED = TREEVIEW_LOADED_ROWS >= total_records
            return True
        else:
            return False

def delete_tree_row(key:int):
    """Delete data based on clicked treeview row

    Args:
        key (str): row's NIK

    Returns:
        Tuple(bool, str): success flag and message
    """
    global TREEVIEW_LOADED_ROWS
    res = dbconnect.delete_selected_records(key)
    if res:
        if TREEVIEW_LOADED_ROWS > 0:
            TREEVIEW_LOADED_ROWS -= 1
        return (True, f'Data dengan NIK {key} telah di delete')
    else:
        return (False, f'Terjadi error!')

def is_db_empty():
    """Check if database is empty

    Returns:
        bool: True if database is empty, False otherwise
    """
    return dbconnect.get_total_records() == 0

def dump_to_csv(path:str):
    """Dump all database records to csv

    Args:
        path (str): Path like

    Returns:
        Tuple(bool, str): Tuple of success boolean and message
    """
    possible_path = Path(path)
    file_name = f'{datetime.now().strftime("%d-%m-%Y")}_database_dump.csv'
    column_name = ['id', 'nik', 'nama', 'tanggal_lahir', 'tempat_lahir', 'alamat', 'nama_pasangan', 'nama_ibu_kandung', 'kolektibilitas', 'keterangan']
    if possible_path.is_dir():
        con, datas = dbconnect.select_all_records()
        if con:
            try:
                with open(os.path.join(possible_path, file_name), 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(column_name)
                    for data in datas:
                        _, unparse_value = unparse_input((column_name, list(data)))
                        writer.writerow(unparse_value)
            except IOError as e:
                return (False, f'Error pada saat process dumping csv {e}')
            except Exception as e:
                return (False, f'Unexpected Error {e}')
            else:
                return (True, f'Data berhasil di export dengan nama {file_name} di folder {possible_path}')
    else:
        return (False, f'{str(possible_path)} bukan merupakan sebuah directory')

def print_pdf(key:str, output_path:str):
    """Export or print the founded records using NIK as the key

    Args:
        key (str): key to search the data, in this case is NIK
        output_path (str): The output path where the file will be stored
    
    Returns:
        Tuple(bool, str): Tuple of success boolean and message.
    """
    def format_to_parse(dict_value):
        var_name = list(dict_value.keys())
        var = list(dict_value.values())
        return (var_name, var)
    def parsed_to_row(tuple_values):
        var_names, vars = tuple_values
        new_row = {}
        for var_name, var in zip(var_names, vars):
            new_row[var_name] = var
        return new_row
    
    possible_path = Path(output_path)
    dataDict = parsed_to_row(unparse_input(format_to_parse(dict(dbconnect.search_record(key)))))
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
            src='{os.path.join(abs_path,'./assets/img/kop_surat.jpg')}'
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
                    <td>{dataDict['id']}</td>
                </tr>
                <tr>
                    <td class='first-col'>NIK</td>
                    <td class='align-colon'>:</td>
                    <td>{dataDict['nik']}</td>
                </tr>
                <tr>
                    <td class='first-col'>Nama</td>
                    <td class='align-colon'>:</td>
                    <td>{dataDict['nama']}</td>
                </tr>
                <tr>
                    <td class='first-col'>Tempat Lahir</td>
                    <td class='align-colon'>:</td>
                    <td>{dataDict['tempat_lahir']}</td>
                </tr>
                <tr>
                    <td class='first-col'>Tanggal Lahir</td>
                    <td class='align-colon'>:</td>
                    <td>{dataDict['tanggal_lahir']}</td>
                </tr>
                <tr>
                    <td class='first-col'>Alamat</td>
                    <td class='align-colon'>:</td>
                    <td>{dataDict['alamat']}</td>
                </tr>
                <tr>
                    <td class='first-col'>Nama Pasangan</td>
                    <td class='align-colon'>:</td>
                    <td>{dataDict['nama_pasangan']}</td>
                </tr>
                <tr>
                    <td class='first-col'>Nama Ibu Kandung</td>
                    <td class='align-colon'>:</td>
                    <td>{dataDict['nama_ibu_kandung']}</td>
                </tr>
                <tr>
                    <td class='first-col'>Kolektibilitas</td>
                    <td class='align-colon'>:</td>
                    <td>{dataDict['kolektibilitas']}</td>
                </tr>
                <tr>
                    <td class='first-col'>Keterangan</td>
                    <td class='align-colon'>:</td>
                    <td>{dataDict['keterangan']}</td>
                </tr>
            </table>
        </body>
    </html>
    """
    if possible_path.is_dir():
        file_name = os.path.join(possible_path, f'{dataDict["nama"]}_{dataDict["nik"]}_{datetime.now().strftime("%d-%m-%Y")}.pdf')
        try:
            with open(file_name, 'w+b') as output_file:
                pdf_writer_status = pisa.CreatePDF(html_code, dest=output_file)
        except Exception as e:
            print(f'Something went wrong {e}')
            return (False, f'Something went wrong')
        else:
            return (pdf_writer_status, f'Data sudah di cetak! Cek {possible_path}')
    else:
        return (False, f'{possible_path} bukan merupakan sebuah direktori!')