#!/usr/bin/python
# coding=utf8
import os
import mysql.connector
from requests.models import HTTPError 
import models
import helpers
import main

db_config = {
    'user': os.environ.get('DB_USER', 'test'),
    'password': os.environ.get('DB_PASSWORD', 'testpw'),
    'host': '127.0.0.1',
    'database': os.environ.get('DB_NAME', 'testdb'),
}

def update_modules() -> bool:
    """ For each saved module, check if it still exists and/or changed, match in DB, delete too old ones"""
    cnx = mysql.connector.connect(**db_config)

    cursor = cnx.cursor()
    current_sessions = helpers.get_current_sessions()
    # delete modules of semester no longer relevant (as defined by the default num_prev_semesters+1, or len(helpers.get_current_sessions())-2 +1
    no_longer_relevant_session = helpers.get_current_sessions(len(current_sessions)-1)[-1]
    cursor.execute("DELETE FROM module WHERE PiqYear = %(year)s AND PiqSession = %(session)s", no_longer_relevant_session)
    cnx.commit()
    cursor.close()

    cursor2 = cnx.cursor(dictionary=True, buffered=True)
    last_relevant_session = current_sessions[3]
    cursor2.execute("SELECT * FROM module WHERE PiqYear = %(year)s AND PiqSession = %(session)s", last_relevant_session)
    current_session = current_sessions[1]
    # print("last_relevant_session:", last_relevant_session)
    # print("current_session:", current_session)
    for row in cursor2:
        # if the title were to change of a module of the current semester
        # update_or_delete(cnx, row)
        # port modules from a year ago to the currnt semester:
        # next_session = helpers.get_next_session(row['PiqYear'], row['PiqSession'])
        # mod = models.Module(row['SmObjId'], next_session['year'], next_session['session'])
        mod = models.Module(row['SmObjId'], current_session['year'], current_session['session'])
        print("current module from db:", row)
        next_values = mod.find_module_values()
        if(next_values != None):
            print("FOUND:", next_values['title'], " --- whitelisted: ", row['whitelisted'])
            # main.save_module(next_values['SmObjId'], next_values['PiqYear'], next_values['PiqSession'], row['whitelisted'],  row['searchterm'], row['searchterm_id'])
            qry = "INSERT INTO module (SmObjId, PiqYear, PiqSession, title, whitelisted, searchterm, searchterm_id) VALUES (%(SmObjId)s, %(PiqYear)s, %(PiqSession)s, %(title)s, %(whitelisted)s, %(searchterm)s, %(searchterm_id)s) ON DUPLICATE KEY UPDATE whitelisted=%(whitelisted)s"
            next_values['whitelisted'] = row['whitelisted']
            next_values['searchterm'] = row['searchterm']
            next_values['searchterm_id'] = row['searchterm_id']
            cursor = cnx.cursor()
            cursor.execute(qry, next_values)
            cnx.commit()
            cursor.close()
    cursor2.close()
    cnx.close()

    return True

def update_or_delete(cnx, row):
    cursor2 = cnx.cursor(dictionary=True, buffered=True)
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
    cursor2.close()