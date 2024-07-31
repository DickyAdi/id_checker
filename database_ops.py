import sqlite3

def create_table():
    conn = sqlite3.connect('CHECKER_DATABASE.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS db_checker (
                nik INT PRIMARY KEY NOT NULL,
                nama TEXT NOT NULL,
                tanggal_lahir TEXT NOT NULL, 
                tempat_lahir TEXT NOT NULL,
                alamat TEXT NOT NULL,
                nama_ibu_kandung TEXT NOT NULL,
                nama_pasangan TEXT,
                kolektibilitas INT NOT NULL,
                keterangan TEXT
    )
    ''')
    conn.commit()
    conn.close()

with sqlite3.connect('CHECKER_DATABASE.db') as conn:
    # print(conn.execute('SELECT * FROM db_checker').description)
    conn.execute('DELETE FROM db_checker')
    # conn.execute('DROP TABLE db_checker')
    print('done')
# create_table()
# print('done')