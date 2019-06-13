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

def update_modules() -> bool:
    """ For each saved module, check if it still exists and/or changed, match in DB, delete too old ones"""
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True, buffered=True)
    # delete modules of semester no longer relevant (as defined by the default num_prev_semesters+1, or len(helpers.get_current_sessions())-2 +1
    no_longer_relevant_session = helpers.get_current_sessions(len(helpers.get_current_sessions())-1)[-1]
    cursor.execute("DELETE FROM module WHERE PiqYear = %(year)s AND PiqSession = %(session)s", no_longer_relevant_session)
    cursor.execute("SELECT SmObjId, PiqYear, PiqSession FROM module")
    for row in cursor:
        cursor2 = cnx.cursor()
        mod = models.Module(row['SmObjId'], row['PiqYear'], row['PiqSession'])
        current_values = mod.find_module_values()
        if current_values is not None:
            qry2 = "UPDATE module SET title=%(title)s WHERE SmObjId=%(SmObjId)s AND PiqYear = %(PiqYear)s AND PiqSession = %(PiqSession)s;"
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
