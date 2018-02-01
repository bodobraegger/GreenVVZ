#!/usr/bin/python
# coding=utf8
import mysql.connector
import module as m

db_config = {
    'user': 'greenvvz',
    'password': 'greenvvzpw',
    'host': '127.0.0.1',
    'database': 'greenvvzdb',
}


def update_db():
    return update_whitelist() and update_blacklist()


def update_whitelist():
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(buffered=True)
    qry = ("SELECT SmObjId FROM whitelist")
    cursor.execute(qry)
    for row in cursor:
        cursor2 = cnx.cursor()
        mod = m.Module(row[0])
        if mod.update():
            qry2 = "UPDATE whitelist SET PiqYear=%(PiqYear)s, PiqSession=%(PiqSession)s, held_in=%(held_in)s, title=%(title)s WHERE SmObjId=%(SmObjId)s;"
            val = {'SmObjId': mod.SmObjId,
                   'PiqYear': mod.PiqYear,
                   'PiqSession': mod.PiqSession,
                   'held_in': mod.held_in,
                   'title': mod.title
                   }
        else:
            qry2 = "DELETE FROM whitelist WHERE SmObjId=%(SmObjId)s"
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


def update_blacklist():
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(buffered=True)
    qry = ("SELECT SmObjId FROM blacklist")
    cursor.execute(qry)
    for row in cursor:
        cursor2 = cnx.cursor()
        mod = m.Module(row[0])
        if mod.update():
            qry2 = "UPDATE blacklist SET PiqYear=%(PiqYear)s, PiqSession=%(PiqSession)s, held_in=%(held_in)s, title=%(title)s WHERE SmObjId=%(SmObjId)s;"
            val = {'SmObjId': mod.SmObjId,
                   'PiqYear': mod.PiqYear,
                   'PiqSession': mod.PiqSession,
                   'held_in': mod.held_in,
                   'title': mod.title
                   }
        else:
            qry2 = "DELETE FROM blacklist WHERE SmObjId=%(SmObjId)s"
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