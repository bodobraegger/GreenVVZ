# coding=utf8
import requests
import xml.etree.ElementTree as ET
import re
from datetime import date


# returns a dictionary containing the values 'year' and 'session' as of today
def current_session():
    if date.today() < date(date.today().year, 2, 1):
        return {'year': current_year() - 1, 'session': '003'}
    elif date.today() < date(date.today().year, 8, 1):
        return {'year': current_year() - 1, 'session': '004'}
    else:
        return {'year': current_year(), 'session': '003'}


# returns a dictionary containing the values 'year' and 'session' of the upcoming semester
def next_session():
    if date.today() < date(date.today().year, 2, 1):
        return {'year': current_year() - 1, 'session': '004'}
    elif date.today() < date(date.today().year, 8, 1):
        return {'year': current_year(), 'session': '003'}
    else:
        return {'year': current_year(), 'session': '004'}


# returns a dictionary containing the values 'year' and 'session' of the previous semester
def previous_session():
    if date.today() < date(date.today().year, 2, 1):
        return {'year': current_year() - 2, 'session': '004'}
    elif date.today() < date(date.today().year, 8, 1):
        return {'year': current_year() - 1, 'session': '003'}
    else:
        return {'year': current_year() - 1, 'session': '004'}


# returns current year as int
def current_year():
    return date.today().year


# input: A string in the form "SmDetailsSet(SmObjId='00000000',PiqYear='0000',PiqSession='000')"
# return: outputs the elements of the key as dictionary (SmObjId, PiqYear, PiqSession)
def decode_key(key_string):
    regex = r"((?P<id>SmObjId=\'(\d*)\'),(?P<year>PiqYear=\'(\d*)\'),(?P<session>PiqSession=\'(\d*)\'))"
    # test_str = unicode(key_string)
    matches = re.search(regex, key_string)
    return {'SmObjId': matches.group(3), 'PiqYear': matches.group(5), 'PiqSession': matches.group(7)}


class Module:
    # constructor
    def __init__(self, SmObjId):
        self.SmObjId = SmObjId
        self.PiqSession = 0
        self.PiqYear = 0
        self.held_in = 0
        self.title = ''

    # check if a module exists in specified year and session and return dict with SmObjId, PiqYear, PiqSession, held_in and title
    # return None if module doesn't exist
    def module_exists(self, year, session):
        try:
            rURI = "https://studentservices.uzh.ch/sap/opu/odata/uzh/vvz_data_srv/SmDetailsSet(SmObjId='{0}',PiqYear='{1}'," \
                   "PiqSession='{2}')?$expand=Partof%2cOrganizations%2cResponsible%2cEvents%2cEvents%2fPersons%2cOfferPeriods".format(
                self.SmObjId, year, session)

            r = requests.get(rURI)

            root = ET.fromstring(r.content)

            key = decode_key(root.find('{http://www.w3.org/2005/Atom}title').text)
            title = root.find('{http://www.w3.org/2005/Atom}content')[0].find(
                '{http://schemas.microsoft.com/ado/2007/08/dataservices}SmText').text

            key['title'] = title
            key['held_in'] = key['PiqSession']

            if key['SmObjId'] == '00000000':
                return None
            else:
                return key
        except AttributeError as err:
            return None

    # get most recent module from odata-api, and set class-variables
    # return false if not available
    def update(self):
        previous = self.module_exists(previous_session()['year'], previous_session()['session'])
        current = self.module_exists(current_session()['year'], current_session()['session'])
        next = self.module_exists(next_session()['year'], next_session()['session'])

        if previous:
            self.set_module(previous)
        if current:
            self.set_module(current)
        if next:
            self.set_module(next)
        if not (next or current or previous):
            return False
        else:
            return True

    # sets module to provided values and sets 'held_in' properly
    def set_module(self, values):
        self.SmObjId = values['SmObjId']
        self.PiqSession = values['PiqSession']
        self.PiqYear = values['PiqYear']
        self.title = values['title']

        if self.held_in != 0 and values['held_in'] != 0 and self.held_in != values['held_in']:
            self.held_in = 999
        else:
            self.held_in = values['held_in']

    # returns dict of this module's variables if module exits, else None
    def get_module(self):
        if self.PiqSession != 0:
            return {
                'SmObjId': self.SmObjId,
                'PiqSession': self.PiqSession,
                'PiqYear': self.PiqYear,
                'held_in': self.held_in,
                'title': self.title
            }
        else:
            return None
