import sqlite3

connection = sqlite3.connect("gym.db")
connection.execute("PRAGMA foreign_keys = ON;")

with open("schema.sql") as f:
    connection.executescript(f.read())

connection.close()
print("¡Base de datos gym.db creada con éxito!")