# coding=utf8
import requests
from datetime import date
from dateutil.relativedelta import relativedelta

import helpers

class Globals():
    URI_prefix = "https://studentservices.uzh.ch/sap/opu/odata/uzh/vvz_data_srv"

class Module:
    """ Class to hold Module logic and data. Hardly used to full potential, could rework to use more of this."""
    # constructor
    def __init__(self, SmObjId: int, PiqYear: int, PiqSession: int):
        """ Construct with Primary Key: (SmObjId, PiqYear, PiqSession) """
        self.SmObjId = SmObjId
        self.PiqYear = PiqYear
        self.PiqSession = PiqSession
        self.title = ''
        self.whitelisted=None

    # check if a module exists in specified year and session and return dict with SmObjId, PiqYear, PiqSession, and title
    # return None if module doesn't exist
    def find_module_values(self) -> dict:
        """Check if module with given SmObjId and session data exists in course catalogue, get values if it does"""
        # Details page for module
        rURI = "https://studentservices.uzh.ch/sap/opu/odata/uzh/vvz_data_srv/SmDetailsSet(SmObjId='{0}',PiqYear='{1}'," \
               "PiqSession='{2}')?$format=json".format(
            self.SmObjId, self.PiqYear, self.PiqSession)

        r = requests.get(rURI)
        try:
            # if the module does not exist, raise HTTP error 404
            r.raise_for_status()

            module = {
                'SmObjId':      r.json()['d']['SmObjId'],
                'PiqYear':      r.json()['d']['PiqYear'],
                'PiqSession':   r.json()['d']['PiqSession'],
                'title':        r.json()['d']['SmText'],
            }
            # No module found in course catalogue
            if module['SmObjId'] == '00000000':
                return None
            else:
                self.set_module(module)
                # print("find_module_values retrieved: {}".format(module))  
                return module
        except requests.exceptions.HTTPError as err:
            print(type(err), err)
            return None

    def set_module(self, values: dict):
        """ sets module to provided values """
        self.SmObjId = values['SmObjId']
        self.PiqSession = values['PiqSession']
        self.PiqYear = values['PiqYear']
        self.title = values['title']

    def get_module(self) -> dict:
        """ Get this module's variables if module exits, else None """
        if self.PiqSession != 0:
            return {
                'SmObjId': self.SmObjId,
                'PiqYear': self.PiqYear,
                'PiqSession': self.PiqSession,
                'title': self.title,
                'whitelisted': self.whitelisted
            }
        else:
            return None
