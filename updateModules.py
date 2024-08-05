#!/usr/bin/python
# coding=utf8
import mysql.connector
import models
import helpers

def update_modules() -> bool:
    """ For each saved module, check if it still exists and/or changed, match in DB, delete too old ones"""
    cnx, cursor = helpers.get_cnx_and_cursor()
    current_sessions = helpers.get_current_sessions(padded=False)
    # delete modules of semester no longer relevant (as defined by the default num_prev_semesters+1, or len(helpers.get_current_sessions())-2 +1
    no_longer_relevant_session = helpers.get_current_sessions(len(current_sessions)-1, padded=False)[-1]
    cursor.execute(f"DELETE FROM module WHERE PiqYear = %s AND PiqSession = %s", tuple(no_longer_relevant_session.values()))
    cnx.commit()
    cursor.close()

    update_modules_from_session(cnx, 
        session_to_poll_from=current_sessions[3], 
        session_to_store_in =current_sessions[1])
    update_modules_from_session(cnx, 
        session_to_poll_from=current_sessions[2], 
        session_to_store_in =current_sessions[0])


    cnx.close()

    return True

def update_or_delete(cnx, row):
    cursor = cnx.cursor()
    mod = models.Module(row['SmObjId'], row['PiqYear'], row['PiqSession'])
    current_values = mod.find_module_values()
    if current_values is not None:
        qry2 = "UPDATE module SET title=%s WHERE SmObjId=%s AND PiqYear = %s AND PiqSession = %s;"
        val = (current_values['title'], row['SmObjId'], row['PiqYear'], row['PiqSession'])
    else:
        qry2 = "DELETE FROM module WHERE SmObjId=%s AND PiqYear = %s AND PiqSession = %s"
        val = tuple(row.values())
    try:
        cursor.execute(qry2, val)
    except mysql.connector.Error as err:
        print("Error: {}".format(err))
    cursor.close()

def update_modules_from_session(cnx, session_to_poll_from, session_to_store_in):
    cursor2 = cnx.cursor(dictionary=True, buffered=True)
    cursor2.execute("SELECT * FROM module WHERE PiqYear = %s AND PiqSession = %s", tuple(session_to_poll_from.values()))
    # print("session_to_poll_from:", session_to_poll_from)
    # print("session_to_store_in:", session_to_store_in)
    for row in cursor2:
        # if the title were to change of a module of the current semester
        # update_or_delete(cnx, row)
        # port modules from a year ago to the currnt semester:
        # next_session = helpers.get_next_session(row['PiqYear'], row['PiqSession'])
        # mod = models.Module(row['SmObjId'], next_session['year'], next_session['session'])
        mod = models.Module(row['SmObjId'], session_to_store_in['year'], session_to_store_in['session'])
        print("current module from db:", row['title'], " --- whitelisted: ", row['whitelisted'])
        # check if already saved in next year, if so, skip adding it!
        cursor = cnx.cursor()
        cursor.execute("SELECT 1 FROM module WHERE SmObjId= %s AND PiqYear = %s AND PiqSession = %s LIMIT 1", tuple(mod.get_module().values())[:-2])
        result = cursor.fetchone()
        cursor.close()
        if result == None:
            next_values = mod.find_module_values()
            if(next_values != None):
                print("FOUND:", next_values['title'], " --- whitelisted: ", row['whitelisted'])
                # main.save_module(next_values['SmObjId'], next_values['PiqYear'], next_values['PiqSession'], row['whitelisted'],  row['searchterm'], row['searchterm_id'])
                next_values['whitelisted'] = row['whitelisted']
                next_values['searchterm'] = row['searchterm']
                next_values['searchterm_id'] = row['searchterm_id']
                helpers.save_module_to_db(next_values)
    cursor2.close()