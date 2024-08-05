from datetime import date
from dateutil.relativedelta import relativedelta
import os
import mysql.connector
import sqlite3

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
    'host': '127.0.0.1',
    'database': os.environ.get('DB_NAME', 'testdb'),
}
if not os.environ.get('DB_NAME'):
    import sqlite3
    db_config = {'database': 'db.sqlite'}
    mysql.connector.connect = sqlite3.connect
    if not os.path.isfile('db.sqlite'):
        print("no db.sqlite file found, creating new one")
        cnx, cursor = get_cnx_and_cursor()
        with open('tables_creation.sql', 'r') as f:
            cursor.executescript(f.read())
        cnx.commit()
        cnx.close()
print(f"{db_config=}")

def get_cnx_and_cursor():
    cnx = mysql.connector.connect(**db_config)
    if 'sqlite' in db_config['database']:
        cnx.row_factory = sqlite3.Row
        cursor = cnx.cursor()
    else:
        cursor = cnx.cursor(dictionary=True, buffered=True)
    return cnx, cursor

