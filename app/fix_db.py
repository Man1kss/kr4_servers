import sqlite3

conn = sqlite3.connect('app.db')
conn.execute('DROP TABLE IF EXISTS products')
conn.execute('''
    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(200) NOT NULL,
        price NUMERIC(10,2) NOT NULL,
        count INTEGER NOT NULL DEFAULT 0,
        description VARCHAR(1000) NOT NULL DEFAULT ''
    )
''')
conn.commit()
conn.close()
print('Таблица products пересоздана успешно!')