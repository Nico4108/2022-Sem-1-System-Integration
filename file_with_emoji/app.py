import sqlite3

with open('GSM1.c9yUHM') as emoji:
    data = emoji.read()
    lines = data.split('\n')
    msg = lines[-1]
    print(msg)

    

db = sqlite3.connect('emojidatabase.db')

#db.execute('CHARACTER SET=utf8mb4 COLLATE utf8mb4_unicode_ci')
#db.execute('CREATE TABLE emojii ("id" INTEGER NOT NULL PRIMARY KEY, "val" TEXT)')
t = 'test'
#db.execute('CREATE DATABASE emojidatabase')
#db.execute('SET SESSION character_set_results = utf8mb4')
db.execute('PRAGMA encoding = "UTF-16le"')
db.execute(f"INSERT INTO emojii (id, val) VALUES (8, '{msg}')")


db.commit()
