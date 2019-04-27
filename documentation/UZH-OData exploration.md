    for a search of courses instead of modules ESearchSet (vs SmSerachSet):
    prefix= https://studentservices.uzh.ch/sap/opu/odata/uzh/vvz_data_srv/
ESearchSet?$skip=0&$top=20&$orderby=EStext%20asc&$filter=substringof(%27i%20wer%27,Seark)%20and%20PiqYear%20eq%20%272018%27%20and%20PiqSession%20eq%20%27004%27&$expand=Persons&$inlinecount=allpages
    /Persons:
    PSearchSet?$skip=0&$top=20&$orderby=LastName%20asc&$filter=PiqYear%20eq%20%272018%27%20and%20PiqSession%20eq%20%27004%27&$inlinecount=allpages 
    
    clicking on course (detail page, containing info about containing modules, persons, rooms etc.): 
EDetailsSet(EObjId='50934874',PiqYear='2018',PiqSession='004')?$expand=Rooms%2cPersons%2cSchedule%2cSchedule%2fRooms%2cSchedule%2fPersons%2cModules%2cLinks
    CANNOT CALL INDIVIDUALLY?, because not implemented
        /Rooms, GListSet
        /Links, WebLinkSet
        /Modules, Module! SmListSet !!!!!!
            SmListSet(ObligCore4Cg='',SmObjId='50934872',PiqYear='2018',PiqSession='004')
            ?$expand=Modules
        /Schedule, EScheduleSet
        /Persons, PListSet
    
    from there, following a link to a containing module:
    clicking on module (detail page, containing Partof information of Sc (studienprogramme)):
SmDetailsSet(SmObjId='50934872',PiqYear='2018',PiqSession='004')?$expand=Partof%2cOrganizations%2cResponsible%2cEvents%2cEvents%2fPersons%2cOfferPeriods
    /OfferPeriods
    /Partof, Studienprogramme!
    /Responsible
    /Organizations
    /Events
    #
    clicking on details for first studienprogramm:
CgDetailsSet(CgObjId='50437275',PiqYear='2018',PiqSession='004')?$expand=Organizations%2cHead%2cCoordination%2cScs%2cCgs 
    /Cgs, seemingly empty?
    /Organizations
    /Head
    /Coordination
    /Scs, Studiengänge!
    just finding containing studienprogramms:
    CgSearchSet?$skip=0&$top=20&$orderby=CgStext%20asc&$filter=PiqYear%20eq%20%272018%27%20and%20PiqSession%20eq%20%27004%27&$inlinecount=allpages
    from there, following a link to a studienprogramm:

    when clicking on details, odd GET (not sure if necessary): 
    DetailPageConfigSet?$filter=OType%20eq%20%27E%27%20and%20ObjectId%20eq%20%2750934874%27
    again, odd GET:
    DetailPageConfigSet?$filter=OType%20eq%20%27SM%27%20and%20ObjectId%20eq%20%2750934872%27
    
```
    # # ET.dump(course_details_root)
    # course_details_root_modules = course_details_root.find("{http://www.w3.org/2005/Atom}link[@title='Modules']")
    # print()
    # for e in course_details_root_modules.findall(".//{http://www.w3.org/2005/Atom}entry"):
    #     print(e)
    #     for ee in course_details_root.findall("{http://www.w3.org/2005/Atom}link[@title='Modules'].//{http://www.w3.org/2005/Atom}content/*"):
    #         print(ee)
    #         for eee in ee.findall('*'):
    #             print(eee)
    #         # for eee in ee.findall('*'):
    #     #         print(eee)
    # print()

```