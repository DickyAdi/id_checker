import sqlite3
import os
import sys

if getattr(sys, 'frozen', False):
    abs_path = sys._MEIPASS
else:
    abs_path = os.path.abspath('.')

DB = os.path.join(abs_path, 'CHECKER_DATABASE.db')

def get_total_records(db_name:str=None, root:str='./'):
    """Get total rows in the database

    Args:
        db_name (str, optional): Database file names. Defaults to None.
        root (str, optional): Root path where the database located. Defaults to './'.

    Returns:
        int: Number of rows
    """
    db_path = os.path.join(root, DB) if db_name == None else os.path.join(root, db_name)
    query = f'''
        SELECT COUNT(nik) FROM db_checker
    '''
    with sqlite3.connect(db_path) as conn:
        try:
            res = conn.execute(query).fetchone()
        except sqlite3.Error as e:
            print(f'something went wrong {e}')
            return 0
        else:
            return res[0]


def search_record(key:int, db_name:str=None, root:str='./'):
    """Search and return records based on nik

    Args:
        key (int): key to be found
        db_name (str, optional): Name of the database. Defaults to CHECKER_DATABASE.
        root (str, optional): Root of the apps that contain database. Defaults to './'.

    Returns:
        List or None: founded records if exists, otherwise None
    """
    db_path = os.path.join(root, DB) if db_name == None else os.path.join(root, db_name)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = '''SELECT * FROM db_checker WHERE nik = :nik'''
        par = {'nik' : key}
        cursor.execute(query, par)
    result = cursor.fetchone()
    return result if result else None

def insert_record(data_fields, db_name:str=None, root:str='./'):
    """Insert a single record via program to database

    Args:
        data_fields (Tuple(List, List)): Tuple of 2 list which contains var_name and var. var_name should match the database columns
        db_name (str, optional): Database file name. Defaults to None.
        root (str, optional): Root path of the database. Defaults to './'.

    Returns:
        bool: True if process succeed. False otherwise
    """
    fields, data = data_fields
    db_path = os.path.join(root, DB) if db_name == None else os.path.join(root, db_name)
    data_parameterized = ', '.join(['?'] * len(data))
    query = f'''
        INSERT INTO db_checker ({', '.join(fields)})
        VALUES ({data_parameterized})
    '''
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, data)
            conn.commit()
    except sqlite3.Error:
        print('something went wrong')
        return False
    else:
        return True

def edit_record(data_fields, db_name:str=None, root:str='./'):
    """Edit a records via program

    Args:
        data_fields (Tuple(List, List)): Tuple of 2 list which contains var_name and var. var_name should match the database columns
        db_name (str, optional): Database file name. Defaults to None.
        root (str, optional): Root path of the database. Defaults to './'.

    Returns:
        bool: True if process succeed. False otherwise
    """
    db_path = os.path.join(root, DB) if db_name==None else os.path.join(root, db_name)
    fields, data = data_fields
    # key = data[0]
    data_parameterized = ', '.join([f'{field} = :{field}' for field in fields])
    parameterized_values = {field : data for field, data in zip(fields, data)}
    condition_clause = f'nik = :nik'
    query = f'''
        UPDATE db_checker
        SET {data_parameterized}
        WHERE {condition_clause}
    '''
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, parameterized_values)
            conn.commit()
    except sqlite3.Error:
        print('something went wrong')
        return False
    else:
        return True

def insert_record_via_csv(data_fields, db_name:str=None, root:str='./'):
    """Insert records via csv

    Args:
        data_fields (List[Dict]): List of dictionaries read from csv
        db_name (str, optional): Database file name. Defaults to None.
        root (str, optional): Root path of the database. Defaults to './'.

    Returns:
        tuple(bool, str): success flag boolean and message
    """
    db_path = os.path.join(root, DB) if db_name == None else os.path.join(root, db_name)
    fields = list(data_fields[0].keys())
    data = [tuple(val.values()) for val in data_fields]
    parameterized_values = ', '.join(['?'] * len(fields))
    query = f'''
        INSERT INTO db_checker ({', '.join(fields)}) VALUES ({parameterized_values})
    '''
    with sqlite3.connect(db_path) as conn:
        try:
            conn.executemany(query, data)
            conn.commit()
        except sqlite3.IntegrityError as e:
            conn.rollback()
            return (False, 'IntegrityError')
        except sqlite3.Error as e:
            conn.rollback()
            return (False, 'UnexpectedError')
        else:
            return (True, 'Success')

def select_all_records(limit=None, offset=None, db_name:str=None, root:str='./'):
    """Select all records from database using lazy load

    Args:
        limit (int) : Limit select for lazy load
        offset (int) : Number of loaded data for indexing
        db_name (str, optional): Database file name. Defaults to None.
        root (str, optional): Root path of the database. Defaults to './'.

    Returns:
        Tuple(bool, List): Tuple of bool and list, bool indicate whether the process is success or not while list is the result of the process. 
    """
    db_path = os.path.join(root, DB) if db_name == None else os.path.join(root, db_name)
    # print(limit, offset)
    if limit != 0:
        query = f'''
            SELECT * FROM db_checker LIMIT {limit} OFFSET {offset}
        '''
    else:
        query = '''
            SELECT * FROM db_checker
        '''
    # print(query)
    with sqlite3.connect(db_path) as conn:
        try:
            res = conn.execute(query).fetchall()
        except sqlite3.Error as e:
            print(f'Something went wrong {e}')
            return (False, None)
        else:
            return (True, res)

def delete_selected_records(key:int, db_name:str=None, root:str='./'):
    """Delete records based on key which is NIK

    Args:
        key (str): Records key
        db_name (str, optional): Database file name. Defaults to None.
        root (str, optional): Root path which database file located. Defaults to './'.

    Returns:
        bool: True if process succeed, False otherwise
    """
    db_path = os.path.join(root, DB) if db_name == None else os.path.join(root, db_name)
    query = f'''
        DELETE FROM db_checker
        WHERE nik = ?
    '''
    with sqlite3.connect(db_path) as conn:
        try:
            conn.execute(query, (key,))
            conn.commit()
        except sqlite3.Error as e:
            print(f'Something went wrong {e}')
            conn.rollback()
            return False
        else:
            return True

