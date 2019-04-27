# coding=utf8
import os
import mysql.connector
import xml.etree.ElementTree as ET
from datetime import date
from functools import wraps
import requests
import time
# from multiprocessing.pool import ThreadPool
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, json, jsonify, request, abort, render_template
from flask_cors import CORS, cross_origin

import models
import updateModules
import helpers

app = Flask(__name__, static_url_path='/static')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret')
db_config = {
    'user': os.environ.get('DB_USER', 'test'),
    'password': os.environ.get('DB_PASSWORD', 'testpw'),
    'host': '127.0.0.1',
    'database': os.environ.get('DB_NAME', 'testdb'),
}


# decorator for checking the api-key
def require_appkey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.args.get('key') and request.args.get('key') == app.config['SECRET_KEY']:
            return view_function(*args, **kwargs)
        else:
            abort(401)

    return decorated_function


# Hello World
@app.route('/hello')
@cross_origin()
@require_appkey
def hello_world():
    return jsonify(hell0='world'), 200

# Front End Testing
@app.route('/front')
@cross_origin()
@require_appkey
def front():
    secret_key = app.config['SECRET_KEY']
    return render_template('front_test.html', secret_key=secret_key)

# Front End Dev Page
@app.route('/front_dev')
@cross_origin()
@require_appkey
def front_dev():
    baseUrlVvzUzh = 'https://studentservices.uzh.ch/uzh/anonym/vvz/index.html#/details/'
    whitelist = []
    blacklist = []
    searchterms = []
    found_modules= []
    secret_key = app.config['SECRET_KEY']

    try:
        whitelist = json.loads(get_whitelist())
        blacklist = json.loads(get_blacklist())
        searchterms = json.loads(get_searchterms().get_data())
        found_modules = json.loads(search().get_data())
        # found_modules = helpers.OrderedSet(json.loads(search().get_data())) - helpers.OrderedSet(whitelist) - helpers.OrderedSet(blacklist)
    except mysql.connector.errors.InterfaceError as e:
        print(e, "\n!!!only works on server!!!")
        test = {
            'PiqSession': '003',
            'PiqYear': 2018,
            'SmObjId': 50904112,
            'held_in': 3,
            'title': "ayy",
        }
        whitelist.append(test)
        blacklist.append(test)
        found_modules.append(test)
        searchterms.append({"id": 1, "term": "wut"})

    return render_template('front_dev.html', **{
        'whitelist': whitelist,
        'blacklist': blacklist,
        'searchterms': searchterms,
        'baseUrlVvzUzh': baseUrlVvzUzh,
        'secret_key': secret_key,
        'found_modules': found_modules,
        'date':date
    })

@app.route('/public')
@cross_origin()
@require_appkey
def public():
    baseUrlVvzUzh = 'https://studentservices.uzh.ch/uzh/anonym/vvz/index.html#/details/'
    whitelist = []
    blacklist = []
    searchterms = []
    found_modules= []
    secret_key = app.config['SECRET_KEY']

    try:
        whitelist = json.loads(get_whitelist())
        blacklist = json.loads(get_blacklist())
        searchterms = json.loads(get_searchterms().get_data())
        found_modules = json.loads(search().get_data())
        # found_modules = helpers.OrderedSet(json.loads(search().get_data())) - helpers.OrderedSet(whitelist) - helpers.OrderedSet(blacklist)
    except mysql.connector.errors.InterfaceError as e:
        print(e, "\n!!!only works on server!!!")
        test = {
            'PiqSession': '003',
            'PiqYear': 2018,
            'SmObjId': 50904112,
            'held_in': 3,
            'title': "ayy",
        }
        whitelist.append(test)
        blacklist.append(test)
        found_modules.append(test)
        searchterms.append({"id": 1, "term": "wut"})

    return render_template('public.html', **{
        'whitelist': whitelist,
        'blacklist': blacklist,
        'searchterms': searchterms,
        'baseUrlVvzUzh': baseUrlVvzUzh,
        'secret_key': secret_key,
        'found_modules': found_modules,
        'date':date
    })



# Information about the API
@app.route('/')
@cross_origin()
def info():
    return 'This is a small scale API to access and manipulate data about Sustainability-related Modules at the University of Zurich'


# serve public js-file
@app.route('/js/public')
@cross_origin()
def get_public_js():
    return app.send_static_file('public.js')


# serve admin js-file
@app.route('/js/admin', methods=['GET'])
@cross_origin()
def get_admin_js():
    return app.send_static_file('admin.js')


# serve jquery-ui css-file
@app.route('/css/jqueryui', methods=['GET'])
@cross_origin()
def get_jquery_css():
    return app.send_static_file('jquery-ui.min.css')


# serve jquery-ui js-file
@app.route('/js/jqueryui', methods=['GET'])
@cross_origin()
def get_jquery_js():
    return app.send_static_file('jquery-ui.min.js')


# update all modules
@app.route('/update')
@cross_origin()
def update():
    if updateModules.update_db():
        return 'modules updated', 200
    else:
        return 'error', 400


# get whitelist
@app.route('/whitelist', methods=['GET'])
@cross_origin()
def get_whitelist():
    modules = []
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    qry = (
        "SELECT SmObjId, PiqYear, PiqSession, title, held_in FROM whitelist WHERE SmObjId NOT IN(SELECT SmObjId FROM blacklist) AND PiqYear != 0 ORDER BY title ASC")
    cursor.execute(qry)
    for module in cursor:
        for column, value in module.items():
            if type(value) is bytearray:
                module[column] = value.decode('utf-8')
        modules.append(module)
    cnx.close()
    return jsonify(modules)


# add module to whitelist and remove it from blacklist
@app.route('/whitelist/<int:module_id>', methods=['POST'])
@cross_origin()
@require_appkey
def add_whitelist(module_id):
    cnx = mysql.connector.connect(**db_config)
    qry = "INSERT IGNORE INTO whitelist (SmObjId, PiqYear, PiqSession, title, held_in) VALUES (%(SmObjId)s, %(PiqYear)s, %(PiqSession)s, %(title)s, %(held_in)s)"
    qry2 = "DELETE FROM blacklist WHERE SmObjId = %(SmObjId)s"
    module = models.Module(module_id)
    module.update()
    val = module.get_module()
    if val:
        try:
            cursor = cnx.cursor()
            cursor.execute(qry2, val)
            cnx.commit()
            cursor.close()
        except mysql.connector.Error as err:
            pass
        try:
            cursor = cnx.cursor()
            cursor.execute(qry, val)
            cnx.commit()
            cursor.close()
            cnx.close()
            return jsonify(val), 200
        except mysql.connector.Error as err:
            return "Error: {}".format(err), 409
    else:
        return 'No module found', 404


# remove module from whitelist and add to blacklist
@app.route('/whitelist/<int:module_id>', methods=['DELETE'])
@cross_origin()
@require_appkey
def remove_whitelist(module_id):
    cnx = mysql.connector.connect(**db_config)

    # read module from whitelist
    try:
        val = {'SmObjId': module_id}
        sel = "SELECT * FROM whitelist WHERE SmObjId = %(SmObjId)s"
        cursor = cnx.cursor(dictionary=True, buffered=True)
        cursor.execute(sel, val)
        if cursor.rowcount > 0:
            val = cursor.fetchone()
            for column, value in val.items():
                if type(value) is bytearray:
                    val[column] = value.decode('utf-8')
        else:
            return 'There is no module to delete', 404
    except mysql.connector.Error as err:
        return "Error: {}".format(err), 500

    # remove module from whitelist
    try:
        qry = "DELETE FROM whitelist WHERE SmObjId = %(SmObjId)s"
        cursor.execute(qry, val)
    except mysql.connector.Error as err:
        return "Error: {}".format(err), 500

    # add module to blacklist
    try:
        qry = "INSERT IGNORE INTO blacklist (SmObjId, PiqYear, PiqSession, title, held_in) VALUES (%(SmObjId)s, %(PiqYear)s, %(PiqSession)s, %(title)s, %(held_in)s)"
        cursor.execute(qry, val)
    except mysql.connector.Error as err:
        return "Error: {}".format(err), 500

    cnx.commit()
    cursor.close()
    cnx.close()
    return 'Deleted and moved module to blacklist', 200


# get blacklist
@app.route('/blacklist', methods=['GET'])
@cross_origin()
def get_blacklist():
    modules = []
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    qry = (
        "SELECT SmObjId, PiqYear, PiqSession, title, held_in FROM blacklist WHERE PiqYear != 0 ORDER BY title ASC")
    cursor.execute(qry)
    for module in cursor:
        for column, value in module.items():
            if type(value) is bytearray:
                module[column] = value.decode('utf-8')
        modules.append(module)
    return jsonify(modules)


# add module to blacklist and remove it from whitelist
@app.route('/blacklist/<int:module_id>', methods=['POST'])
@cross_origin()
@require_appkey
def add_blacklist(module_id):
    cnx = mysql.connector.connect(**db_config)
    qry = "INSERT IGNORE INTO blacklist (SmObjId, PiqYear, PiqSession, title, held_in) VALUES (%(SmObjId)s, %(PiqYear)s, %(PiqSession)s, %(title)s, %(held_in)s)"
    qry2 = "DELETE FROM whitelist WHERE SmObjId = %(SmObjId)s"
    module = models.Module(module_id)
    module.update()
    val = module.get_module()
    if val:
        try:
            cursor = cnx.cursor()
            cursor.execute(qry2, val)
            cnx.commit()
            cursor.close()
        except mysql.connector.Error as err:
            pass

        try:
            cursor = cnx.cursor()
            cursor.execute(qry, val)
            cnx.commit()
            cursor.close()
            cnx.close()
            return jsonify(val), 200
        except mysql.connector.Error as err:
            return "Error: {}".format(err), 409
    else:
        return 'No Module found', 404


# remove module from blacklist
@app.route('/blacklist/<int:module_id>', methods=['DELETE'])
@cross_origin()
@require_appkey
def remove_blacklist(module_id):
    cnx = mysql.connector.connect(**db_config)

    # read module from blacklist
    try:
        val = {'SmObjId': module_id}
        sel = "SELECT * FROM blacklist WHERE SmObjId = %(SmObjId)s"
        cursor = cnx.cursor(dictionary=True, buffered=True)
        cursor.execute(sel, val)
        if cursor.rowcount > 0:
            val = cursor.fetchone()
            for column, value in val.items():
                if type(value) is bytearray:
                    val[column] = value.decode('utf-8')
        else:
            return 'There is no module to delete', 404
    except mysql.connector.Error as err:
        return "Error: {}".format(err), 500

    # remove module from whitelist
    try:
        qry = "DELETE FROM blacklist WHERE SmObjId = %(SmObjId)s"
        cursor.execute(qry, val)
    except mysql.connector.Error as err:
        return "Error: {}".format(err), 500

    cnx.commit()
    cursor.close()
    cnx.close()
    return 'Deleted module from blacklist', 200


# get all search terms
@app.route('/searchterms', methods=['GET'])
@cross_origin()
def get_searchterms():
    terms = []
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    qry = (
        "SELECT id, term FROM searchterms ORDER BY term ASC")
    cursor.execute(qry)
    for row in cursor.fetchall():
        for column, value in row.items():
            if type(value) is bytearray:
                row[column] = value.decode('utf-8')
        terms.append(row)
    return jsonify(terms)


# add search term
@app.route('/searchterms', methods=['POST'])
@cross_origin()
@require_appkey
def add_searchterm():
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    data = request.form
    term = data['term']
    # term  =  'test'
    qry = "INSERT INTO searchterms (term) VALUES (%(term)s)"
    try:
        cursor.execute(qry, data)
        id = cursor.lastrowid
        cnx.commit()
        cnx.close()
        return jsonify({'id': id, 'term': term}), 200
    except mysql.connector.Error as err:
        cnx.close()
        return "Error: {}".format(err), 400


# remove search term
@app.route('/searchterms/<int:id>', methods=['DELETE'])
@cross_origin()
@require_appkey
def remove_searchterm(id):
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()
    qry = "DELETE FROM searchterms WHERE id= %(id)s"
    try:
        cursor.execute(qry, {'id': id})
        cnx.commit()
        cnx.close()
        return 'deleted', 200
    except mysql.connector.Error as err:
        cnx.close()
        return "Error: {}".format(err), 404


# get modules based on search terms, excluding those on white- and blacklist
@app.route('/search', methods=['GET'])
@cross_origin()
def search():
    # get searchterms
    terms = []
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    qry = (
        "SELECT term FROM searchterms")
    cursor.execute(qry)
    for row in cursor:
        terms.append(row['term'])

    # get results for all searchterms
    modules = []
    for session in [helpers.next_session(), helpers.current_session(), helpers.previous_session()]:
        for searchterm in terms:
            rURI = "https://studentservices.uzh.ch/sap/opu/odata/uzh/vvz_data_srv/SmSearchSet?$skip=0&$top=20&$orderby=SmStext%20asc&$filter=substringof('{0}',Seark)%20and%20PiqYear%20eq%20'{1}'%20and%20PiqSession%20eq%20'{2}'&$inlinecount=allpages".format(
                searchterm, session['year'], session['session'])

            r = requests.get(rURI)
            root = ET.fromstring(r.content)
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                for a in entry.findall('{http://www.w3.org/2005/Atom}content'):
                    modules.append({
                        'SmObjId': int(a[0].find('{http://schemas.microsoft.com/ado/2007/08/dataservices}Objid').text),
                        'PiqYear': int(a[0].find('{http://schemas.microsoft.com/ado/2007/08/dataservices}PiqYear').text),
                        'PiqSession': int(a[0].find(
                            '{http://schemas.microsoft.com/ado/2007/08/dataservices}PiqSession').text),
                        'title': a[0].find('{http://schemas.microsoft.com/ado/2007/08/dataservices}SmStext').text
                    })

    print('\n\n\nBEFORE UNIQUE\n\n\n')
    for e in modules:
        print(e)
    
    # remove duplicates
    #modules = [dict(t) for t in set([tuple(sorted(d.items())) for d in modules])]
    modules = list({frozenset(item.items()):item for item in modules}.values())

    # remove elements that are on whitelist unified with blacklist
    ids_whitelist = []
    cursor = cnx.cursor()
    cursor.execute("SELECT SmObjId FROM whitelist")
    for row in cursor:
        ids_whitelist.append(row[0])

    ids_blacklist = []
    cursor = cnx.cursor()
    cursor.execute("SELECT SmObjId FROM blacklist")
    for row in cursor:
        ids_blacklist.append(row[0])
    cursor.close()
    ids_white_u_blacklist = list(set(ids_whitelist + ids_blacklist))

    # print('\n\n\nBEFORE REMOVAL\n\n\n')
    # for e in modules:
    #     print(e)

    # for mod in modules:
    #     if int(mod.get('SmObjId')) in ids_white_u_blacklist:
    #         modules.remove(mod)
    #         # modules = [m for m in modules if m != mod]
    #         # print('To remove:', mod)
    #         # while mod in modules:
    #         #     print('REMOVED', mod)
    #         #     modules.remove(mod)
    
    # print('\n\n\nAFTER REMOVAL\n\n\n')
    # for e in modules:
    #     print(e)

    for mod in modules:
        if int(mod.get('SmObjId')) in ids_whitelist:
            mod['in_whitelist'] = 1
        if int(mod.get('SmObjId')) in ids_blacklist:
            mod['in_blacklist'] = 1

    return jsonify(modules)

"""
Request detail page for course object, add Module subobjects(dicts) as list to given course object 
"""
def find_modules_for_course(course):
    course['Modules'] = []
    rURI = models.Globals.URI_prefix+"EDetailsSet(EObjId='{}',PiqYear='{}',PiqSession='{}')?$expand=Rooms,Persons,Schedule,Schedule/Rooms,Schedule/Persons,Modules,Links".format(
        course.get('EObjId'), course.get('PiqYear'), course.get('PiqSession'))

    r = requests.get(rURI)
    root = ET.fromstring(r.content)

    # select all contents of entry elements in the link element titled 'Modules'
    for entry in root.findall("{http://www.w3.org/2005/Atom}link[@title='Modules'].//{http://www.w3.org/2005/Atom}entry"):
        for datapoints in entry.findall('{http://www.w3.org/2005/Atom}content/*'):
            course['Modules'].append({
                'SmObjId': int(datapoints.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}SmObjId').text),
                'SmText': datapoints.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}SmText').text,
                'PiqYear': int(datapoints.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}PiqYear').text),
                'PiqSession': int(datapoints.find(
                    '{http://schemas.microsoft.com/ado/2007/08/dataservices}PiqSession').text),
            })
    return course

"""
Request detail page for module object, add Studyprogrm subobjects(dicts) as list to given module obj
"""
def find_studyprograms_for_module(module):
    module['Partof'] = []
    # SmDetailsSet(SmObjId='50934872',PiqYear='2018',PiqSession='004')?$expand=Partof%2cOrganizations%2cResponsible%2cEvents%2cEvents%2fPersons%2cOfferPeriods
    rURI = models.Globals.URI_prefix+"SmDetailsSet(SmObjId='{}',PiqYear='{}',PiqSession='{}')?$expand=Partof%2cOrganizations%2cResponsible%2cEvents%2cEvents%2fPersons%2cOfferPeriods".format(
        module.get('SmObjId'), module.get('PiqYear'), module.get('PiqSession'))
    # async with aiohttp.ClientSession() as session:
    #     r = await fetch_content(session, rURI)
    r = requests.get(rURI)
    root = ET.fromstring(r.content)
    for entry in root.findall("{http://www.w3.org/2005/Atom}link[@title='Partof'].//{http://www.w3.org/2005/Atom}entry"):
        for datapoints in entry.findall('{http://www.w3.org/2005/Atom}content/*'):
            module['Partof'].append({
                'ScObjid': int(datapoints.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}ScObjid').text),
                'ScText': datapoints.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}ScText').text,
                'OText': datapoints.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}OText').text,
                'CgHighObjid': datapoints.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}CgHighObjid').text,
                'CgHighText': datapoints.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}CgHighText').text,
                'CgHighCategory': datapoints.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}CgHighCategory').text,
                'CgHighObjid': datapoints.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}CgHighObjid').text,
                'CgLowObjid': datapoints.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}CgLowObjid').text,
                'CgLowText': datapoints.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}CgLowText').text,
                'CgLowCategory': datapoints.find('{http://schemas.microsoft.com/ado/2007/08/dataservices}CgLowCategory').text,
            })
    return module

"""
Wrapper function to be able to parallelize finding studyprograms for modules
"""
def wrap_execute_for_modules_in_course(course):
    with ThreadPoolExecutor(max_workers=10) as executor:
        return executor.map(find_studyprograms_for_module, course['Modules'])
    # return ThreadPool(len(course['Modules'])).imap_unordered(find_studyprograms_for_module, course['Modules'])

"""
Find course matches, then find containing modules, containing study programs
"""
@app.route('/search_upwards', methods=['GET'])
@cross_origin()
def search_upwards():
    start_time = time.perf_counter()
    # get searchterms
    terms = []
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT term FROM searchterms")
        for row in cursor:
            terms.append(row['term'])
    except Exception as e:
        print('not possible in dev', e)
        terms+=['Nachhaltigkeit', 'Sustainability']

    # get results for all searchterms
    courses = []
    modules = []
    for session in [helpers.next_session(), helpers.current_session(), helpers.previous_session()]:
        for searchterm in terms:
            rURI = models.Globals.URI_prefix+"ESearchSet?$skip=0&$top=20&$orderby=EStext%20asc&$filter=substringof('{0}',Seark)%20and%20PiqYear%20eq%20'{1}'%20and%20PiqSession%20eq%20'{2}'&$inlinecount=allpages".format(
                searchterm, session['year'], session['session'])
            r = requests.get(rURI)
            root = ET.fromstring(r.content)
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                for a in entry.findall('{http://www.w3.org/2005/Atom}content'):
                    courses.append({
                        'EObjId': int(a[0].find('{http://schemas.microsoft.com/ado/2007/08/dataservices}Objid').text),
                        'EText': a[0].find('{http://schemas.microsoft.com/ado/2007/08/dataservices}EStext').text,
                        'PiqYear': int(a[0].find('{http://schemas.microsoft.com/ado/2007/08/dataservices}PiqYear').text),
                        'PiqSession': int(a[0].find(
                            '{http://schemas.microsoft.com/ado/2007/08/dataservices}PiqSession').text),
                    })
        # remove duplicates
        #courses = [dict(t) for t in set([tuple(sorted(d.items())) for d in courses])]
        # courses = list({frozenset(item.items()):item for item in courses}.values())
        
        # takes about 6 seconds for the two dev terms
        with ThreadPoolExecutor(max_workers=len(courses)) as executor:
            x = executor.map(find_modules_for_course, courses)
            y = executor.map(wrap_execute_for_modules_in_course, courses)

        # takes >20 seconds for the two dev terms.        
        # for course in courses:
        #     find_modules_for_course(course)
            
        #     for module in course['Modules']:
        #         find_studyprograms_for_module(module)
            # print(course)

    elapsed_time = time.perf_counter() - start_time
    print("elapsed", elapsed_time)
    return jsonify(courses)


if __name__ == "__main__":
    app.run()

# Get modules from either the black or white list database, for in template use.