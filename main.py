# coding=utf8
# builtin
import os
import sys
import mysql.connector
from functools import wraps
import requests
import time
# from multiprocessing.pool import ThreadPool
from concurrent.futures import ThreadPoolExecutor
from itertools import groupby

# flask lib
from flask import Flask, json, jsonify, request, abort, render_template
# flask_cors extension for handling CORS, making corss-origin AJAX possible.
from flask_cors import CORS, cross_origin

# this codebase
import models
import updateModules
import helpers

# Initialize flask app
# SUB URL HANDLING HACK
# TODO: in production, a real WSGI server should be used, and the app should be served from root,
# with the SCRIPT_NAME and APPLICATION_ROOT env vars to handle routing.
prefix = ''
api_url = os.environ.get('API_URL', '/greenvvz')
if api_url[-1] == '/':
    os.environ['API_URL'] = api_url[:-1]

api_url = os.environ.get('API_URL')
if 'http' in api_url[:4]:
    prefix = '/' + api_url.split('/')[2:][-1]

app = Flask(__name__, static_url_path=f"{prefix}/static")
# SUB URL HANDLING DONE
# for handling CORS, making corss-origin AJAX possible.
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
# get SECRET_KEY from environment
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret')

# custom
app.config['API_URL'] = os.environ.get('API_URL', 'http://localhost:5000')

print(f"{app.config=}")

def require_appkey(view_function):
    """ decorator for checking the api-key, making unauthorized requests impossible """
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.args.get('key') and request.args.get('key') == app.config['SECRET_KEY']:
            return view_function(*args, **kwargs)
        else:
            abort(401)

    return decorated_function


@app.route('/greenvvz/echo', methods = ['GET', 'POST', 'PATCH', 'PUT', 'DELETE'])
@cross_origin()
@require_appkey
def hello_world():
    """ test echo """
    if request.method == 'GET':
        return "ECHO: GET\n"
    elif request.method == 'POST':
        return "ECHO: POST\n"
    elif request.method == 'PATCH':
        return "ECHO: PATCH\n"
    elif request.method == 'PUT':
        return "ECHO: PUT\n"
    elif request.method == 'DELETE':
        return "ECHO: DELETE"

@app.route('/admin')
@cross_origin()
@require_appkey
def admin():
    """ Administrator front end view """
    # for local testing
    studyprograms = {0: "Theologie: Vollstudienfach 120"}
    studyprogramid_moduleids = {0: [2]}
    secret_key = app.config['SECRET_KEY']

    return render_template('admin.html', **{
        'secret_key': secret_key,
        'api_url': app.config['API_URL'],
        # for filter-selectors.html include
        'sessions': helpers.get_current_sessions(),
            # optional, for local testing:
        'studyprogramid_moduleids': studyprogramid_moduleids,
        'studyprograms': studyprograms,
    })

@app.route('/public')
@cross_origin()
@require_appkey
def public():
    """ Public front end view """
    # for local testing
    studyprograms = {0: "Theologie: Vollstudienfach 120"}
    studyprogramid_moduleids = {0: [2]}

    try:
        studyprograms = get_studyprograms().get_data(as_text=True)
        studyprogramid_moduleids = get_studyprograms_modules().get_data(as_text=True)
    except mysql.connector.errors.InterfaceError as e:
        print("not possible in dev", e)

    return render_template('public.html', **{
        'secret_key': app.config['SECRET_KEY'],
        'api_url': app.config['API_URL'],
        # for filter-selectors.html
        'sessions': helpers.get_current_sessions(),
            # optional, for local testing:
        'studyprogramid_moduleids': studyprogramid_moduleids,
        'studyprograms': studyprograms,
    })

@app.route('/')
@cross_origin()
def info():
    """ Information about the API """
    return 'This is a small scale API to access and manipulate data about Sustainability-related Modules at the University of Zurich'

@app.route('/update')
@cross_origin()
def update():
    """ Update saved modules to match their course catalogue counterparts, be there any changes """
    if updateModules.update_modules():
        return 'modules updated', 200
    else:
        return 'error', 400

def get_modules(whitelisted: bool):
    """ Get modules saved in the database, either blacklisted or whitelisted, as JSON response """
    modules = []
    cnx, cursor = helpers.get_cnx_and_cursor()
    
    current_searchterms = [t.get('term') for t in json.loads(get_searchterms(with_deleted=False).get_data())]

    qry = (
        "SELECT * FROM module as m WHERE whitelisted = {whitelisted} ORDER BY title ASC".format(whitelisted=whitelisted))
    cursor.execute(qry)
    for module in cursor:
        if 'sqlite' in helpers.db_config['database']:
            module = dict(zip(module.keys(), module))
        for column, value in module.items():
            if type(value) is bytearray:
                module[column] = value.decode('utf-8')
        if module['searchterm'] not in current_searchterms:
            module['searchterm'] = '# '+ module['searchterm']

        modules.append(module)
    cnx.close()
    return jsonify(modules)

@app.route('/modules/whitelist', methods=['GET'])
@cross_origin()
def get_whitelist():
    return get_modules(whitelisted=1)

@app.route('/modules', methods=['POST'])
@cross_origin()
@require_appkey
def add_module():
    """ Add module to database. required in POST request body: SmObjId, PiqYear, PiqSession, whitelisted, searchterm """
    try:
        req_data = request.get_json()
        # get data from request body
        SmObjId = req_data['SmObjId']
        PiqYear = req_data['PiqYear']
        PiqSession = req_data['PiqSession']
        whitelisted = int(req_data['whitelisted'])
        searchterm = req_data['searchterm']
        searchterm_id = req_data['searchterm_id']
    except Exception as err:
            return "Error: {}\nfor module {}".format(err, SmObjId), 409


    try_save_module = save_module(SmObjId, PiqYear, PiqSession, whitelisted, searchterm, searchterm_id)
    # saving succeeded, create new tuple from module values dict and success code
    if isinstance(try_save_module, dict):
        return jsonify(try_save_module), 200
    # saving failed, tuple of string and error code
    elif isinstance(try_save_module, tuple): 
        return try_save_module


def save_module(SmObjId, PiqYear, PiqSession, whitelisted, searchterm, searchterm_id):
    # check if module exists in course catalogue, use values from there...
    m = models.Module(SmObjId, PiqYear, PiqSession)
    module_values = m.find_module_values()   
    # ... if it exists, ...
    if module_values is not None:
        module_values['whitelisted'] = whitelisted
        module_values['searchterm'] = searchterm
        module_values['searchterm_id'] = searchterm_id
        return helpers.save_module_to_db(module_values)
    else:
        return 'No module found', 404

@app.route('/modules/<int:module_id>', methods=['PUT'])
@cross_origin()
@require_appkey
def flag_module(module_id: int):
    """ Flag saved module as whitelisted or blacklisted, depending on request.args.get('whitelisted')"""
    whitelisted = int(request.args.get('whitelisted'))
    cnx, cursor = helpers.get_cnx_and_cursor()
    # flag module as either black or whitelisted.
    try:
        cursor.execute("UPDATE module SET whitelisted = {} WHERE id = {}".format(whitelisted, module_id))
    except mysql.connector.Error as err:
        return "Error: {}".format(err), 409

    cnx.commit()
    cursor.close()
    cnx.close()
    if whitelisted:
        return 'Whitelisted Module with Id {}'.format(module_id), 200
    else:
        return 'Blacklisted Module with Id {}'.format(module_id), 200
    

@app.route('/modules/blacklist', methods=['GET'])
@cross_origin()
def get_blacklist():
    return get_modules(whitelisted=0)

@app.route('/modules/<int:module_id>', methods=['DELETE'])
@cross_origin()
@require_appkey
def remove_module(module_id: int):
    """ remove module from database by id """
    try:
        val = {'module_id': module_id}
        cnx, cursor = helpers.get_cnx_and_cursor()
        qry = "DELETE FROM module WHERE id = %s"
        cursor.execute(qry, tuple(val.values()))
    except mysql.connector.Error as err:
        return "Error: {}".format(err), 500

    cnx.commit()
    cursor.close()
    cnx.close()
    return 'Deleted module', 200

@app.route('/searchterms', methods=['GET'])
@cross_origin()
def get_searchterms(with_deleted=False):
    """ get all search terms from DB """
    terms = []
    cnx, cursor = helpers.get_cnx_and_cursor()
    qry = (
        "SELECT id, term FROM searchterm ORDER BY term ASC")
    cursor.execute(qry)
    # decode encoded strings to make them human readable
    for row in cursor.fetchall():
        if 'sqlite' in helpers.db_config['database']:
            row = dict(zip(row.keys(), row))
        for column, value in row.items():
            if type(value) is bytearray:
                row[column] = value.decode('utf-8')
        terms.append(row)
    if with_deleted:
        qry = ("""
            SELECT DISTINCT searchterm AS term, searchterm_id AS id 
            FROM module m 
            WHERE searchterm NOT IN (
                SELECT term 
                FROM searchterm s 
            )
            ORDER BY searchterm ASC;"""
        )
        cursor.execute(qry)
        for row in cursor.fetchall():
            if 'sqlite' in helpers.db_config['database']:
                row = dict(zip(row.keys(), row))
            for column, value in row.items():
                if type(value) is bytearray:
                    row[column] = value.decode('utf-8')
                if column == 'term':
                    row[column] = '# ' + value
            terms.append(row)
    cursor.close()
    cnx.close()

    return jsonify(terms)


# add search term
@app.route('/searchterms', methods=['POST'])
@cross_origin()
@require_appkey
def add_searchterm():
    """ Add searchterm to DB, term is supplied in form data """
    cnx, cursor = helpers.get_cnx_and_cursor()
    data = request.form
    term = data['term']
    qry = "REPLACE INTO searchterm (term) VALUES ( %s )"
    try:
        cursor.execute(qry, tuple([term]))
        id = cursor.lastrowid
        cnx.commit()
        cnx.close()
        return jsonify({'id': id, 'term': term}), 200
    except mysql.connector.Error as err:
        cnx.close()
        return "Error: {}".format(err), 400

@app.route('/searchterms/<int:searchterm_id>', methods=['PUT'])
@cross_origin()
@require_appkey
def update_searchterm(searchterm_id: int):
    """ Update searchterm in DB, term is supplied in form data """
    cnx, cursor = helpers.get_cnx_and_cursor()
    term = request.values.to_dict()['term']
    qry = "UPDATE searchterm SET term = %s WHERE id = %s"
    try:
        cursor.execute(qry, tuple([term, searchterm_id]))
        cnx.commit()
        cnx.close()
        return jsonify({'id': searchterm_id, 'term': term}), 200
    except Exception as err:
        cnx.close()
        return "Error: {}".format(err), 400

@app.route('/searchterms/<int:searchterm_id>', methods=['DELETE'])
@cross_origin()
@require_appkey
def remove_searchterm(searchterm_id: int):
    """ remove searchterm from DB via id """
    cnx, cursor = helpers.get_cnx_and_cursor()
    cursor = cnx.cursor()
    qry = "DELETE FROM searchterm WHERE id = %s"
    try:
        cursor.execute(qry, tuple([searchterm_id]))
        cnx.commit()
        cnx.close()
        return 'deleted', 200
    except mysql.connector.Error as err:
        cnx.close()
        return "Error: {}".format(err), 404


@app.route('/search/<int:year>/<int:session>', methods=['GET'])
@cross_origin()
def search(year: int, session: int):
    """ get modules based on search terms, marking those already on white- and blacklist """
    # record time for this very slow operation
    start_time = time.perf_counter()
    # get searchterms, and biggest module id
    terms = []
    terms_ids = {}
    id_not_currently_in_use = 999
    try:
        cnx, cursor = helpers.get_cnx_and_cursor()
        cursor.execute("SELECT term, id FROM searchterm")
        for row in cursor:
            terms.append(row['term'])
            terms_ids[row['term']] = row['id']

        cursor.execute("SELECT MAX(id) FROM module")
        # to make sure that all modules have unique CSS ids, make smallest suggestion_module_id = max(module_id)+999
        id_not_currently_in_use = cursor.fetchone()['MAX(id)'] + 999

        cursor.close()
        cnx.close()
    except Exception as e:
        print(type(e), e)

    # get results for all searchterms
    modules = []
    for searchterm in terms:
        # new API has no or search
        # if "&" in searchterm:
        #     temp_searchterms = ["substringof('{0}',Seark)".format(t.strip()) for t in searchterm.split("&")]
        #     modFilter = ' or '.join(temp_searchterms)
        # else:
        #     modFilter = f"substringof('{searchterm}',Seark)"

        next_results = 100
        processed_results = 0
        total_results = next_results
        while(processed_results < total_results):
            total_results = -1
            # rURI = f"{models.Globals.URI_prefix}/SmSearchSet?$skip={processed_results}&$top={next_results}&$orderby=SmStext asc&$filter=({modFilter}) and PiqYear eq '{year}' and PiqSession eq '{str(session).zfill(3)}'&$inlinecount=allpages&$format=json"
            # use new URI structure:
            # SMSearch?$count=true&$search="green"&$select=ObjectAbbreviation,ObjectNameText,OShortText,Points,CategoryText&$orderby=ObjectNameTextSort&$filter=AcademicYear eq '2024' and AcademicPeriod eq '003' and Points ge 0 and Points le 1000&$skip=0&$top=100
            rURI = f"{models.Globals.URI_prefix}/SMSearch?$count=true&$search={searchterm}&$select=ObjectAbbreviation,ObjectNameText,OShortText,Points,CategoryText&$orderby=ObjectNameTextSort&$filter=AcademicYear eq '{year}' and AcademicPeriod eq '{str(session).zfill(3)}' and Points ge 0 and Points le 1000&$skip={processed_results}&$top={next_results}"
            try:
                r = requests.get(rURI)
                total_results = int(r.json()["@odata.count"])

                for module in r.json()["value"]:
                    modules.append({
                        'SmObjId':    int(module['ObjectId']),
                        'title':          module['ObjectNameText'],
                        'PiqYear':    int(module['AcademicYear']),
                        'PiqSession': int(module['AcademicPeriod']),
                        'searchterm': searchterm,
                        'searchterm_id': terms_ids[searchterm],
                    })
                
                processed_results += next_results

            except Exception as e:
                print(f"ERROR: Processing the module request for term '{searchterm}' failed: {type(e)}; {e}", 400)
            processed_results += next_results


    # also search for modules associated with courses for same search
    modules += json.loads(search_upwards(year, session).get_data())

    # remove duplicates for mutable types
    keyfunc = lambda d: (d['SmObjId'], d['PiqYear'], d['PiqSession'])
    giter = groupby(sorted(modules, key=keyfunc), keyfunc)
    modules_no_duplicates = [next(g[1]) for g in giter]

    # flag elements that are already in database
    modules = check_which_saved(modules_no_duplicates)
    for i, mod in enumerate(modules_no_duplicates):
        # fake a database-like Id for easier identification in html
        mod['id'] = id_not_currently_in_use+i
        mod['searchterm_id'] = terms_ids.get(mod['searchterm'], -999)

    elapsed_time = time.perf_counter() - start_time
    print(f"elapsed: getting {len(modules_no_duplicates)} modules {elapsed_time}")

    return jsonify(modules_no_duplicates)


def check_which_saved(modules: list):
    """ Check which modules are saved, and mark them as either white- or blacklisted accordingly """
    try:
        # flag elements that are already in database
        saved_modules = {}
        cnx, cursor = helpers.get_cnx_and_cursor()
        cursor.execute("SELECT SmObjId, PiqYear, PiqSession, whitelisted FROM module")
        for row in cursor:
            saved_modules[(row['SmObjId'], row['PiqYear'], row['PiqSession'])]=row['whitelisted']
        cursor.close()

        for mod in modules:
            module_key = (int(mod.get('SmObjId')), int(mod.get('PiqYear')), int(mod.get('PiqSession')))
            if module_key in saved_modules.keys():
                mod['whitelisted'] = saved_modules[module_key]
        

    except mysql.connector.errors.InterfaceError as e:
        print(e)
    return modules

@app.route('/search_upwards/<int:year>/<int:session>', methods=['GET'])
@cross_origin()
def search_upwards(year: int, session: int):
    """
        Find course matches, then find containing modules, # and containing study programs
    """
    start_time = time.perf_counter()
    # get searchterms
    terms = []
    terms_ids = {}
    try:
        cnx, cursor = helpers.get_cnx_and_cursor()
        cursor.execute("SELECT term, id FROM searchterm")
        for row in cursor:
            terms.append(row['term'])
            terms_ids[row['term']] = row['id']
    except Exception as e:
        print('not possible in dev', e)
        terms+=['Nachhaltigkeit', 'Sustainability']
        terms_ids['Nachhaltigkeit'] = 0
        terms_ids['Sustainability'] = 1

    # get results for all searchterms
    courses = []
    modules = []
    # for session in helpers.get_current_sessions():
    for searchterm in terms:
        if "&" in searchterm:
            searchterms = ["substringof('{0}',Seark)".format(t.strip()) for t in searchterm.split("&")]
            modFilter = ' or '.join(searchterms)
        else:
            modFilter = f"substringof('{searchterm}',Seark)"
               
        next_results = 100
        processed_results = 0
        total_results = next_results
        while(processed_results < total_results):
            total_results = -1
            rURI = f"{models.Globals.URI_prefix}/ESearchSet?$skip={processed_results}&$top={next_results}&$orderby=EStext asc&$filter=({modFilter}) and PiqYear eq '{year}' and PiqSession eq '{str(session).zfill(3)}'&$inlinecount=allpages&$format=json"
            # use new URI structure:
            # ESearch?$count=true&$search="green"&$select=ETitelText,EObjectAbbreviation,EVNumber,RoomId,RoomText,ScheduleSummaryText,HasSchedule,DCategory,DCategoryText,Language,Lecturer&$orderby=ETitelTextSort&$filter=AcademicYear eq '2024' and AcademicPeriod eq '003'&$skip=0&$top=100 
            rURI = f"{models.Globals.URI_prefix}/ESearch?$count=true&$search={searchterm}&$select=ETitelText,EObjectAbbreviation,EVNumber,RoomId,RoomText,ScheduleSummaryText,HasSchedule,DCategory,DCategoryText,Language,Lecturer&$orderby=ETitelTextSort&$filter=AcademicYear eq '{year}' and AcademicPeriod eq '{str(session).zfill(3)}'&$skip={processed_results}&$top={next_results}"
            try:
                r = requests.get(rURI)
                total_results = int(r.json()["@odata.count"])
                
                for course in r.json()["value"]:
                    courses.append({
                        'EObjId':     int(course['ObjectId']),
                        'EStext':         course['ETitelText'],
                        'PiqYear':    int(course['AcademicYear']),
                        'PiqSession': int(course['AcademicPeriod']),
                        'searchterm': searchterm,
                        'searchterm_id': terms_ids[searchterm],
                    })
                                
                    processed_results += next_results

            except Exception as e:
                print("ERROR: Processing the course request for term '{}' failed: {}; {}\n{}".format(searchterm, type(e), e, rURI), 400)
            processed_results += next_results

    # parallel execution: takes about 6 seconds for the two dev terms
    with ThreadPoolExecutor(max_workers=len(courses)+5) as executor:
        executor.map(find_modules_for_course, courses)
        # uncomment this to find studyprograms in one go
        # executor.map(wrap_execute_for_modules_in_course, courses)

    # sequential execution: takes >20 seconds for the two dev terms.        
    # for course in courses:
    #     find_modules_for_course(course)
    for course in courses:
        modules += course['Modules']

    elapsed_time = time.perf_counter() - start_time
    print("elapsed: getting courses->modules", elapsed_time)
    return jsonify(modules)

def find_modules_for_course(course: dict):
    """
    Request detail page for course object, add Module subobjects(dicts) as list to given course object 
    """
    course['Modules'] = []
    # rURI = models.Globals.URI_prefix+"/EDetailsSet(EObjId='{}',PiqYear='{}',PiqSession='{}')?$expand=Rooms,Persons,Schedule,Schedule/Rooms,Schedule/Persons,Modules,Links&$format=json".format(
    #     course.get('EObjId'), course.get('PiqYear'), course.get('PiqSession')) #named params with **dict
    # use new URI structure:
    # EDetailsSet(EObjId='51225236',PiqYear='2024',PiqSession='003')?sap-client=001&$expand=Rooms,Persons,Schedule,Schedule/Rooms,Schedule/Persons,Modules,Links
    rURI = f"{models.Globals.URI_prefix_details}/EDetailsSet(EObjId='{course.get('EObjId')}',PiqYear='{course.get('PiqYear')}',PiqSession='{course.get('PiqSession')}')?sap-client=001&$expand=Rooms,Persons,Schedule,Schedule/Rooms,Schedule/Persons,Modules,Links&$format=json"
    try:
        r = requests.get(rURI)
        # select each result of the 'Modules' subelement
        for module in r.json()['d']['Modules']['results']:
            course['Modules'].append({
                'SmObjId':    int(module['SmObjId']),
                'title':          module['SmText'],
                'PiqYear':    int(module['PiqYear']),
                'PiqSession': int(module['PiqSession']),
                'searchterm': course['searchterm'],
                'searchterm_id': course['searchterm_id'],
            })
        course['Modules'] = list({frozenset(item.items()) : item for item in course['Modules']}.values())
    except Exception as e:
        print("ERROR: Processing the module request for course '{}' failed: {}".format(course['EStext'], e))
    
    return course['Modules']

@app.route('/studyprograms', methods=['GET'])
@cross_origin()
def get_studyprograms():
    """ Get distinct studyprograms associated with modules in the whitelist """
    studyprogram_idlist = []
    studyprogram_textlist = []
    cnx, cursor = helpers.get_cnx_and_cursor()
    # Select all studyprograms for modules on the whitelist
    qry_p1 = """
    SELECT DISTINCT s.* 
        FROM studyprogram AS s 
        INNER JOIN module_studyprogram AS m_s 
        INNER JOIN module AS m 
    WHERE m.id = m_s.module_id AND s.id = m_s.studyprogram_id AND m.whitelisted = 1"""
    # If a specific semester is selected currently, only show for modules in that semester
    qry_p2 = " AND m.PiqYear = {} AND m.PiqSession = {}".format(request.args.get('PiqYear'), request.args.get('PiqSession')) if request.args.get('PiqSession', 'all_semesters') != "all_semesters" else ""
    cursor.execute(qry_p1+qry_p2+" ORDER BY s.CgHighText, s.CgHighCategory;")
    for row in cursor:
        if 'sqlite' in helpers.db_config['database']:
            row = dict(zip(row.keys(), row))
        for column, value in row.items():
            if type(value) is bytearray:
                row[column] = value.decode('utf-8')
        studyprogram_idlist.append(row['id'])
        studyprogram_textlist.append("{CgHighText}: {CgHighCategory}".format(**row))
    cnx.close()
    return jsonify([studyprogram_idlist, studyprogram_textlist])

@app.route('/studyprograms_modules', methods=['GET'])
@cross_origin()
def get_studyprograms_modules():
    """ Get Module-Studyprogramids assocations as a dictionary """
    studyprogramid_moduleids = {}
    try: 
        cnx, cursor = helpers.get_cnx_and_cursor()
        cursor.execute("SELECT * FROM module_studyprogram AS m_s INNER JOIN module AS m WHERE m_s.module_id = m.id AND whitelisted = 1;")
        for row in cursor:
            if 'sqlite' in helpers.db_config['database']:
                row = dict(zip(row.keys(), row))
            for column, value in row.items():
                if type(value) is bytearray:
                    row[column] = value.decode('utf-8')
            if studyprogramid_moduleids.get(row['studyprogram_id']) is None:
                studyprogramid_moduleids[row['studyprogram_id']] = []
            studyprogramid_moduleids[row['studyprogram_id']].append(row['module_id'])
        cnx.close()
    except mysql.connector.Error as err:
        return "Error: {}".format(err), 500
    return jsonify(studyprogramid_moduleids)

if __name__ == "__main__":
    p = sys.argv[1] if 1 < len(sys.argv) else 5000
    app.run(port = p, debug = app.config['DEBUG'])
