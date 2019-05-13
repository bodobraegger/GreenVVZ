#!/usr/bin/python
# coding=utf8
import os
import mysql.connector
import models

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
    qry = ("SELECT SmObjId FROM modules")
    cursor.execute(qry)
    for row in cursor:
        cursor2 = cnx.cursor()
        mod = models.Module(row[0])
        if mod.update():
            qry2 = "UPDATE modules SET PiqYear=%(PiqYear)s, PiqSession=%(PiqSession)s, title=%(title)s WHERE SmObjId=%(SmObjId)s;"
            val = {'SmObjId': mod.SmObjId,
                   'PiqYear': mod.PiqYear,
                   'PiqSession': mod.PiqSession,
                   'title': mod.title
                   }
        else:
            qry2 = "DELETE FROM modules WHERE SmObjId=%(SmObjId)s"
            val = {'SmObjId': mod.SmObjId}

        try:
            cursor2.execute(qry2, val)
        except mysql.connector.Error as err:
            print("Error: {}".format(err))
            return False
        cursor2.close()

    cnx.commit()
    cnx.close()
    return True
