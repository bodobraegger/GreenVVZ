import sqlite3

connection = sqlite3.connect('db.sqlite')


with open('tables_creation.sql') as f:
    connection.executescript(f.read())

connection.close()