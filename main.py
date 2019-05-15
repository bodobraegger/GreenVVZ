# coding=utf8
import os
import mysql.connector
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
    # studyprograms_ids = {}
    secret_key = app.config['SECRET_KEY']

    try:
        whitelist = json.loads(get_whitelist().get_data())
        blacklist = json.loads(get_blacklist().get_data())
        searchterms = json.loads(get_searchterms().get_data())
        found_modules = json.loads(search().get_data())
        # studyprograms_ids = json.loads(get_modules_studyprograms().get_data())
    except mysql.connector.errors.InterfaceError as e:
        print(e, "\n!!!only works on server!!!")
        test = {
            'PiqSession': 3,
            'PiqYear': 2018,
            'SmObjId': 50904112,
            'title': "ayy",
            'whitelisted': 1,
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
        # 'modules_studyprograms': modules_studyprograms,
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
        whitelist = json.loads(get_whitelist().get_data())
        blacklist = json.loads(get_blacklist().get_data())
        searchterms = json.loads(get_searchterms().get_data())
        found_modules = json.loads(search().get_data())
        # found_modules = helpers.OrderedSet(json.loads(search().get_data())) - helpers.OrderedSet(whitelist) - helpers.OrderedSet(blacklist)
    except mysql.connector.errors.InterfaceError as e:
        print(e, "\n!!!only works on server!!!")
        test = {
            'PiqSession': 3,
            'PiqYear': 2018,
            'SmObjId': 50904112,
            'title': "ayy",
            'whitelisted': 1,
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
    return get_modules(whitelisted=1)

def get_modules(whitelisted):
    modules = []
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True)
    qry = (
        "SELECT * FROM modules WHERE whitelisted = {whitelisted} ORDER BY title ASC".format(whitelisted=whitelisted))
    cursor.execute(qry)
    for module in cursor:
        for column, value in module.items():
            if type(value) is bytearray:
                module[column] = value.decode('utf-8')
        modules.append(module)
    cnx.close()
    return jsonify(modules)

def add_module(module_id, PiqYear, PiqSession, whitelisted):
    m = models.Module(module_id)
    module_values = m.find_module_values(PiqYear, PiqSession)
    if module_values is not None:
        try:
            cnx = mysql.connector.connect(**db_config)
            qry = "INSERT INTO modules (SmObjId, PiqYear, PiqSession, title, whitelisted) VALUES (%(SmObjId)s, %(PiqYear)s, %(PiqSession)s, %(title)s, %(whitelisted)s) ON DUPLICATE KEY UPDATE whitelisted=%(whitelisted)s"
            module_values['whitelisted'] = whitelisted
            cursor = cnx.cursor()
            cursor.execute(qry, module_values)
            study_programs = find_studyprograms_for_module(module_id, PiqYear, PiqSession)
            for sp in study_programs:
                qry1 = "INSERT IGNORE INTO studyprograms (CgHighObjid, CgHighText) VALUES (%(CgHighObjid)s, %(CgHighText)s)"
                val1 = {
                    'CgHighObjid': sp['CgHighObjid'],
                    'CgHighText':  sp['CgHighText'],
                }
                cursor.execute(qry1, val1)
                qry2 = "INSERT IGNORE INTO modules_studyprograms (SmObjId, CgHighObjid) VALUES (%(SmObjId)s, %(CgHighObjid)s)"
                val2 = {
                    'SmObjId': module_values['SmObjId'],
                    'CgHighObjid': sp['CgHighObjid'],
                }
                cursor.execute(qry2, val2)
            cnx.commit()
            cursor.close()
            cnx.close()
            return jsonify(module_values), 200
        except mysql.connector.Error as err:
            return "Error: {}".format(err), 409
    else:
        return 'No module found', 404
    

# add module to whitelist and remove it from blacklist
@app.route('/whitelist/<int:PiqYear>/<int:PiqSession>/<int:module_id>', methods=['POST'])
@cross_origin()
@require_appkey
def add_whitelist(module_id, PiqYear, PiqSession):
    return add_module(module_id, PiqYear, PiqSession, whitelisted=1)


# remove module from whitelist and add to blacklist
@app.route('/whitelist/<int:PiqYear>/<int:PiqSession>/<int:module_id>', methods=['DELETE'])
@cross_origin()
@require_appkey
def remove_whitelist(module_id):
    return flag_module(module_id, whitelisted=0)

def flag_module(module_id, whitelisted):
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor(dictionary=True, buffered=True)
    # remove module from whitelist
    try:
        qry = "UPDATE modules SET whitelisted = {whitelisted} WHERE SmObjId = {module_id}".format(whitelisted=whitelisted, module_id=module_id)
        cursor.execute(qry)
    except mysql.connector.Error as err:
        return "Error: {}".format(err), 500

    cnx.commit()
    cursor.close()
    cnx.close()
    if whitelisted:
        return 'Whitelisted Module with Id {}'.format(module_id), 200
    else:
        return 'Blacklisted Module with Id {}'.format(module_id), 200
    

# get blacklist
@app.route('/blacklist', methods=['GET'])
@cross_origin()
def get_blacklist():
    return get_modules(whitelisted=0)


# add module to blacklist and remove it from whitelist
@app.route('/blacklist/<int:PiqYear>/<int:PiqSession>/<int:module_id>', methods=['POST'])
@cross_origin()
@require_appkey
def add_blacklist(module_id, PiqYear, PiqSession):
    return add_module(module_id, PiqYear, PiqSession, whitelisted=0)


# remove module from blacklist
@app.route('/blacklist/<int:PiqYear>/<int:PiqSession>/<int:module_id>', methods=['DELETE'])
@cross_origin()
@require_appkey
def remove_blacklist(module_id, PiqYear, PiqSession):
    # remove module
    try:
        cnx = mysql.connector.connect(**db_config)
        val = {'SmObjId': module_id, 'PiqYear': PiqYear, 'PiqSession': PiqSession}
        cursor = cnx.cursor(dictionary=True, buffered=True)
        qry = "DELETE FROM modules WHERE SmObjId = %(SmObjId)s AND PiqYear = %(PiqYear)s AND PiqSession = %(PiqSession)s AND whitelisted = 0"
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
    start_time = time.perf_counter()
    # get searchterms
    terms = []
    try:
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT term FROM searchterms")
        for row in cursor:
            terms.append(row['term'])
        cursor.close()
    except Exception as e:
        print('not possible in dev', e)
        terms+=['Nachhaltigkeit', 'Sustainability']

    # get results for all searchterms
    modules = []
    for session in [helpers.next_session(), helpers.current_session(), helpers.previous_session()]:
        for searchterm in terms:
            rURI = "https://studentservices.uzh.ch/sap/opu/odata/uzh/vvz_data_srv/SmSearchSet?$skip=0&$top=20&$orderby=SmStext%20asc&$filter=substringof('{0}',Seark)%20and%20PiqYear%20eq%20'{1}'%20and%20PiqSession%20eq%20'{2}'&$inlinecount=allpages&$format=json".format(
                searchterm, session['year'], session['session'])

            r = requests.get(rURI)

            for module in r.json()['d']['results']:
                modules.append({
                    'SmObjId':    int(module['Objid']),
                    'title':          module['SmStext'],
                    'PiqYear':    int(module['PiqYear']),
                    'PiqSession': int(module['PiqSession']),
                })

    # print('\n\n\nBEFORE UNIQUE\n\n\n')
    # for e in modules:
    #     print(e)
    
    # remove duplicates
    #modules = [dict(t) for t in set([tuple(sorted(d.items())) for d in modules])]
    modules += json.loads(search_upwards().get_data())
    modules = list({frozenset(item.items()):item for item in modules}.values())
    elapsed_time = time.perf_counter() - start_time
    print("elapsed: getting modules", elapsed_time)


    # flag elements that are on whitelist unified with blacklist
    modules = check_which_saved(modules)

    return jsonify(modules)


def check_which_saved(modules):
    try:
        # flag elements that are on whitelist unified with blacklist
        saved_modules = {}
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT SmObjId, PiqYear, PiqSession, whitelisted FROM modules")
        for row in cursor:
            saved_modules[(row['SmObjId'], row['PiqYear'], row['PiqSession'])]=row['whitelisted']
        cursor.close()


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
            module_key = (int(mod.get('SmObjId')), int(mod.get('PiqYear')), int(mod.get('PiqSession')))
            if module_key in saved_modules.keys():
                mod['whitelisted'] = saved_modules[module_key]
        

    except mysql.connector.errors.InterfaceError as e:
        print(e)
    return modules


"""
Request detail page for course object, add Module subobjects(dicts) as list to given course object 
"""
def find_modules_for_course(course):
    course['Modules'] = []
    rURI = models.Globals.URI_prefix+"EDetailsSet(EObjId='{}',PiqYear='{}',PiqSession='{}')?$expand=Rooms,Persons,Schedule,Schedule/Rooms,Schedule/Persons,Modules,Links&$format=json".format(
        course.get('EObjId'), course.get('PiqYear'), course.get('PiqSession'))

    r = requests.get(rURI)

    # select each result of the 'Modules' subelement
    for module in r.json()['d']['Modules']['results']:
        course['Modules'].append({
            'SmObjId':    int(module['SmObjId']),
            'title':          module['SmText'],
            'PiqYear':    int(module['PiqYear']),
            'PiqSession': int(module['PiqSession']),
        })
    course['Modules'] = list({frozenset(item.items()) : item for item in course['Modules']}.values())
    return course['Modules']

"""
Request detail page for module object, add Studyprogrm subobjects(dicts) as list to given module obj
"""
def find_studyprograms_for_module(module_id, PiqYear, PiqSession):
    m = models.Module(module_id)
    module_values = m.find_module_values(PiqYear, PiqSession)
    module_values['Partof'] = []
    # SmDetailsSet(SmObjId='50934872',PiqYear='2018',PiqSession='004')?$expand=Partof%2cOrganizations%2cResponsible%2cEvents%2cEvents%2fPersons%2cOfferPeriods
    rURI = models.Globals.URI_prefix+"SmDetailsSet(SmObjId='{}',PiqYear='{}',PiqSession='{}')?$expand=Partof%2cOrganizations%2cResponsible%2cEvents%2cEvents%2fPersons%2cOfferPeriods&$format=json".format(
        module_values.get('SmObjId'), module_values.get('PiqYear'), module_values.get('PiqSession'))
    # async with aiohttp.ClientSession() as session:
    #     r = await fetch_content(session, rURI)
    r = requests.get(rURI)

    for studyprogram in r.json()['d']['Partof']['results']:
        module_values['Partof'].append({
            'CgHighObjid':    studyprogram['ScObjid'],
            'CgHighText':     studyprogram['CgHighText'],
            # CgCategorySort: "25"
            'CgHighCategory': studyprogram['CgHighCategory'],
            # CgHighObjid: "50724643"
            # CgHighText: "Allgemeine Ausbildung (1UF)"
            # CgLowCategory: "Area"
            # CgLowObjid: "50724651"
            # CgLowText: "Fachdidaktik"
            # Corestep: true
            # OObjid: "50000007"
            # OText: "00\nFaculty of Arts and Social Sciences"
            # Oblig: false
            # PiqSession: "000"
            # PiqYear: "0000"
            # ScObjid: "50720073"
            # ScText: "Teaching Diploma for Upper Secondary Education (1 TS)"
            # SmObjId: "50911009"
        })
    module_values['Partof'] = list({frozenset(item.items()) : item for item in module_values['Partof']}.values())
    return module_values['Partof']

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
            rURI = models.Globals.URI_prefix+"ESearchSet?$skip=0&$top=20&$orderby=EStext%20asc&$filter=substringof('{0}',Seark)%20and%20PiqYear%20eq%20'{1}'%20and%20PiqSession%20eq%20'{2}'&$inlinecount=allpages&$format=json".format(
                searchterm, session['year'], session['session'])
            r = requests.get(rURI)
            for course in r.json()['d']['results']:
                courses.append({
                    'EObjId':     int(course['Objid']),
                    'EStext':         course['EStext'],
                    'PiqYear':    int(course['PiqYear']),
                    'PiqSession': int(course['PiqSession']),
                })
        # remove duplicates
        # courses = list({frozenset(item.items()) : item for item in courses}.values())

        
        # takes about 6 seconds for the two dev terms
        with ThreadPoolExecutor(max_workers=len(courses)+5) as executor:
            executor.map(find_modules_for_course, courses)
            # executor.map(wrap_execute_for_modules_in_course, courses)

        # takes >20 seconds for the two dev terms.        
        # for course in courses:
        #     find_modules_for_course(course)
            
        #     for module in course['Modules']:
        #         find_studyprograms_for_module(module)
            # print(course)
    for course in courses:
        modules += course['Modules']
    modules = list({frozenset(item.items()):item for item in modules}.values())
    elapsed_time = time.perf_counter() - start_time
    modules = check_which_saved(modules)
    print("elapsed: getting courses->modules->studyprograms", elapsed_time)
    return jsonify(modules)

@app.route('/modules_studyprograms', methods=['GET'])
@cross_origin()
def get_modules_studyprograms():
    # modules_studyprograms = {}
    # cnx = mysql.connector.connect(**db_config)
    # cursor = cnx.cursor(dictionary=True)
    # qry = (
    #     "SELECT SmObjId, CgHighObjid, CgHighText, CgCategorySort FROM modules JOIN modules_studyprograms JOIN studyprograms ORDER BY title ASC"
    # cursor.execute(qry)
    # for row in cursor:
    #     for column, value in row.items():
    #         if type(value) is bytearray:
    #             row[column] = value.decode('utf-8')
    #     modules_studyprograms[row[0]] = {
    #         'CgHighObjid': row[1],
    #         'CgHighText': row[2]
    #     }
    # cnx.close()
    # return jsonify(modules)
    pass

if __name__ == "__main__":
    app.run()

# Get modules from either the black or white list database, for in template use.