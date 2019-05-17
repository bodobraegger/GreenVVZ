#!/usr/bin/python
# coding=utf8
import os
import mysql.connector
import models
import helpers

db_config = {
    'user': os.environ.get('DB_USER', 'test'),
    'password': os.environ.get('DB_PASSWORD', 'testpw'),
    'host': '127.0.0.1',
    'database': os.environ.get('DB_NAME', 'testdb'),
}


def update_db():
    return update_modules() # and update_blacklist()


def update_modules():
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(buffered=True)
    qry = ("SELECT SmObjId, PiqYear, PiqSession FROM module")
    cursor.execute(qry)
    for row in cursor:
        cursor2 = cnx.cursor(dictionary=True)
        mod = models.Module(row['SmObjId'])
        current_values = mod.find_module_values(row['PiqYear'], row['PiqSession'])
        if current_values is not None:
            qry2 = "UPDATE modules SET title=%(title)s WHERE SmObjId=%(SmObjId)s AND PiqYear = %(PiqYear)s AND PiqSession = %(PiqSession)s;"
            val = current_values

        else:
            qry2 = "DELETE FROM module WHERE SmObjId=%(SmObjId)s AND PiqYear = %(PiqYear)s AND PiqSession = %(PiqSession)s"
            val = row
        try:
            cursor2.execute(qry2, val)
        except mysql.connector.Error as err:
            print("Error: {}".format(err))
            return False
        cursor2.close()

    cnx.commit()
    cnx.close()
    return True
