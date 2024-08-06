from datetime import date
from dateutil.relativedelta import relativedelta
import os
import mysql.connector
import sqlite3
from dotenv import load_dotenv
load_dotenv(override=True)


def get_session(ref_date = date.today(), target_date = None, padded=True) -> dict:
    """
    returns a dictionary containing the values 'year' and 'session' as of ref_date (default is today)
    ref_date to compare to the target_date, which is feb of the ref year by default
        SPRING: PREV YEAR 004
        FALL:   SAME YEAR 003
    """
    spring = 4
    fall = 3
    if padded:
        spring = '004'
        fall = '003'
    # if no target_date given, simply use ref_date year and 1. feb
    target_date = target_date if target_date != None else date(ref_date.year, 2, 1)
    if ref_date < target_date:
        return {'year': ref_date.year - 1, 'session': fall}
    elif ref_date < target_date+relativedelta(months=6):
        return {'year': ref_date.year - 1, 'session': spring}
    else:
        return {'year': ref_date.year, 'session': fall}

def get_current_sessions(num_prev_semesters: int = 6, padded=True) -> list:
    """ Get next, current, and last num_prev_semesters sessions: DEFINE DEFAULT HERE, OTHERWISE ADAPT updateModules.py"""
    sessions = [ # next session (6 months from now)
        get_session(date.today()+relativedelta(months=6), padded=padded), 
        get_session(date.today(), padded=padded)
    ] # current session
    # previous sessions: 6 months back per semester
    for months in range(6, 6*num_prev_semesters+1, 6):
        sessions.append(get_session(date.today()-relativedelta(months=months), padded=padded))
    return sessions

def get_next_session(ref_year, ref_sem) -> dict:
    semester = 4 if ref_sem == 3 else 3
    year = ref_year if ref_sem == 3 else ref_year+1
    return {'year': year, 'session': semester}

def current_year() -> int:
    """ returns current year as int """
    return date.today().year

### DB helpers
# Database config from environment.
db_config = {
    'user': os.environ.get('DB_USER', 'test'),
    'password': os.environ.get('DB_PASSWORD', 'testpw'),
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'testdb'),
}

def get_cnx_and_cursor():
    cnx = mysql.connector.connect(**db_config)
    if 'sqlite' in db_config['database']:
        cnx.row_factory = sqlite3.Row
        cursor = cnx.cursor()
    else:
        cursor = cnx.cursor(dictionary=True, buffered=True)
    return cnx, cursor

if not os.environ.get('DB_NAME'):
    import sqlite3
    db_config = {'database': 'db.sqlite'}
    mysql.connector.connect = sqlite3.connect
    if not os.path.isfile('db.sqlite'):
        print("no db.sqlite file found, creating new one")
        cnx, cursor = get_cnx_and_cursor()
        with open('tables_creation_sqlite.sql', 'r') as f:
            cursor.executescript(f.read())
        cnx.commit()
        cnx.close()
print(f"{db_config=}")

def save_module_to_db(module_values: dict):
    # safety
    module_id = 0
    try:
        # try to save into database
        cnx, cursor = get_cnx_and_cursor()
        qry = "REPLACE INTO module (SmObjId, PiqYear, PiqSession, title, whitelisted, searchterm, searchterm_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"

        study_programs = module_values.pop('Partof')
        cursor.execute(qry, tuple(module_values.values()))
        module_id = cursor.lastrowid
        if module_id == 0:
            cursor.execute("SELECT id FROM module WHERE SmObjId = %s AND PiqYear = %s AND PiqSession = %s", tuple(module_values.values()))
            for row in cursor:
                print("module_id = cursor.lastrowid did not work", row)
                module_id = row[0]
        cnx.commit()
        cursor.close()

        # if a module is to be saved, find the corresponding studyprograms and save them too
        save_studyprograms_for_module(module_id, study_programs)
        cnx.close()
        return module_values
    except mysql.connector.Error as err:
        return "Error: {}\nfor module {}".format(err, module_id), 409


def save_studyprograms_for_module(module_id: int, studyprograms: list):
    """ Save studyprogams for module in database, establish relationship"""
    # print('deleting studyprogams', studyprograms, 'for module', module_id)
    cnx, cursor = get_cnx_and_cursor()
    studyprogram_id = 0
    for sp in studyprograms:
        cursor = cnx.cursor()
        qry1 = "REPLACE INTO studyprogram (CgHighText, CgHighCategory) VALUES (%s, %s)"
        val1 = (sp['CgHighText'], sp['CgHighCategory'])

        cursor.execute(qry1, val1)
        studyprogram_id = cursor.lastrowid
        # if the study_program == 0, the insert failed (likely, because the studyprogram already exists)
        if studyprogram_id == 0:
            # thus, you can find the studyprogam using the values, and grab the id.
            cursor.execute("SELECT id FROM studyprogram WHERE CgHighText = %s AND CgHighCategory = %s", val1)
            for row in cursor:
                print("duplicate studyprogram?: studyprogram_id = cursor.lastrowid did not work, potential match id in db: ", row[0])
                studyprogram_id = row[0]
        cnx.commit()

        # insert entry in designated database, to match Many-To-Many relationship Modules-To-Studyprograms
        qry2 = "REPLACE INTO module_studyprogram (module_id, studyprogram_id) VALUES (%s, %s)"
        val2 = (module_id, studyprogram_id)
        cursor.execute(qry2, val2)
        cnx.commit()
        cursor.close()
