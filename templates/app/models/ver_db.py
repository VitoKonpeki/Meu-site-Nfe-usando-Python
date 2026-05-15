import sqlite3

conn = sqlite3.connect("contabilidade.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(usuarios)")
print(cursor.fetchall())

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tabelas:", cursor.fetchall())

conn.close()
