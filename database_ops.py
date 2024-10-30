import sqlite3

def create_table():
    conn = sqlite3.connect('CHECKER_DATABASE.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS db_checker (
                id TEXT NOT NULL,
                nik INT PRIMARY KEY NOT NULL,
                nama TEXT NOT NULL,
                tanggal_lahir TEXT NOT NULL, 
                tempat_lahir TEXT NOT NULL,
                alamat TEXT NOT NULL,
                nama_ibu_kandung TEXT NOT NULL,
                nama_pasangan TEXT,
                kolektibilitas INT NOT NULL,
                keterangan TEXT,
                created_at TEXT NOT NULL,
                last_edit TEXT
    )
    ''')
    conn.commit()
    conn.close()

def create_prepopulated_table():
    conn = sqlite3.connect('CHECKER_DATABASE.db')
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS prepopulated_table (
                is_prepopulated NUMERIC PRIMARY KEY NOT NULL DEFAULT 0)
    '''
    )

    cur.execute('INSERT OR IGNORE INTO prepopulated_table (is_prepopulated) VALUES (0)')
    conn.commit()
    conn.close()

with sqlite3.connect('CHECKER_DATABASE.db') as conn:
#     print(conn.execute('SELECT * FROM db_checker').description)
    # conn.execute('DELETE FROM db_checker')
    # res = conn.execute('SELECT id FROM db_checker ORDER BY CAST(SUBSTR(id, 3) AS INTEGER) DESC LIMIT 1').fetchone()
    # print(res[0])
    conn.execute('DROP TABLE db_checker')
    # conn.execute('DROP TABLE prepopulated_table')
    print('done')
create_table()
create_prepopulated_table()
# print('done')