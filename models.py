# coding=utf8
import requests

import helpers

class Globals():
    URI_prefix = "https://studentservices.uzh.ch/sap/opu/odata/uzh/vvz_data_srv/"

class Module:
    # constructor
    def __init__(self, SmObjId):
        self.SmObjId = SmObjId
        self.PiqSession = 0
        self.PiqYear = 0
        self.title = ''
        self.whitelisted=0

    # check if a module exists in specified year and session and return dict with SmObjId, PiqYear, PiqSession, and title
    # return None if module doesn't exist
    def find_module(self, year, session):
        rURI = "https://studentservices.uzh.ch/sap/opu/odata/uzh/vvz_data_srv/SmDetailsSet(SmObjId='{0}',PiqYear='{1}'," \
               "PiqSession='{2}')?$expand=Partof%2cOrganizations%2cResponsible%2cEvents%2cEvents%2fPersons%2cOfferPeriods".format(
            self.SmObjId, year, session)

        r = requests.get(rURI)
        try:
            # if the module does not exist, raise HTTP error 404
            r.raise_for_status()

            module = {
                'title':        r.json()['d']['SmText'],
                'SmObjId':      r.json()['d']['SmObjId'],
                'PiqSession':   r.json()['d']['PiqSession'],
                'PiqYear':      r.json()['d']['PiqYear'],
            }

            if module['SmObjId'] == '00000000':
                return None
            else:
                return module

        except requests.exceptions.HTTPError as err:
            print(err)
            return None
        except AttributeError as err:
            print(err)
            return None

    # get most recent module from odata-api, and set class-variables
    # return false if not available
    def update(self):
        previous = self.find_module(helpers.previous_session()['year'], helpers.previous_session()['session'])
        current = self.find_module(helpers.current_session()['year'], helpers.current_session()['session'])
        next = self.find_module(helpers.next_session()['year'], helpers.next_session()['session'])

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

    # sets module to provided values
    def set_module(self, values):
        self.SmObjId = values['SmObjId']
        self.PiqSession = values['PiqSession']
        self.PiqYear = values['PiqYear']
        self.title = values['title']

    # returns dict of this module's variables if module exits, else None
    def get_module(self):
        if self.PiqSession != 0:
            return {
                'SmObjId': self.SmObjId,
                'PiqSession': self.PiqSession,
                'PiqYear': self.PiqYear,
                'title': self.title,
                'whitelisted': self.whitelisted
            }
        else:
            return None
