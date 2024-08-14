# coding=utf8
import requests

class Globals():
    URI_prefix_details = "https://studentservices.uzh.ch/sap/opu/odata/uzh/vvz_data_srv"
    URI_prefix = "https://studentservices.uzh.ch/sap/opu/zodatav4/sap/zcm_vvz_v4_ui/srvd/sap/zsb_vvz/0001"

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
        # rURI = "https://studentservices.uzh.ch/sap/opu/odata/uzh/vvz_data_srv/SmDetailsSet(SmObjId='{0}',PiqYear='{1}'," \
        #        "PiqSession='{2}')?$expand=Partof,Organizations,Responsible,Events,Events/Persons,OfferPeriods&$format=json".format(
        #     self.SmObjId, self.PiqYear, self.PiqSession)
        # use new URI structure:
        # SmDetailsSet(SmObjId='51223451',PiqYear='2024',PiqSession='003')?sap-client=001&$expand=Partof,Organizations,Responsible,Events,Events/Persons,OfferPeriods
        rURI = f"{Globals.URI_prefix_details}/SmDetailsSet(SmObjId='{self.SmObjId}',PiqYear='{self.PiqYear}',PiqSession='{self.PiqSession}')?sap-client=001&$expand=Partof,Organizations,Responsible,Events,Events/Persons,OfferPeriods&$format=json"
        r = requests.get(rURI)
        try:
            # if the module does not exist, raise HTTP error 404
            r.raise_for_status()
            # if the module exists with 'no content' (204), return None
            if r.status_code == 204:
                return None

            module = {
                'SmObjId':      r.json()['d']['SmObjId'],
                'PiqYear':      r.json()['d']['PiqYear'],
                'PiqSession':   r.json()['d']['PiqSession'],
                'title':        r.json()['d']['SmText'],
                'Partof':       r.json()['d']['Partof']['results'],
            }
            # No module found in course catalogue
            if module['SmObjId'] == '00000000':
                return None
            else:
                self.set_module(module)
                # print("find_module_values retrieved: {}".format(module))  
                return module
        except Exception as err:
            print(f"find_module_values failed for {self.SmObjId}\n", type(err), err)
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
