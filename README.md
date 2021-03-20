# McAfee ESM Python API

This module allows to get a simple python API
wrapper around the McAfee ESM REST API principal components.

# Main features

- Incident Management
- Watchlist
- Get Devices


# Usage

Initialize a session. By default, verify is disabled:

    from .py_esm import Session
    
    url = 'https://mcafee_esm_host
    username = 'username'
    password = 'password'
    session = Session(username, password, url)
    session.login()

If you want use CA cert:
    
    import py_esm

    url = 'https://mcafee_esm_host
    username = 'username'
    password = 'password'
    cert = '/path/to/your/CA/cert'
    session = py_esm.Session(username, password, url, verify=cert)
    session.login()

**Incident Management**:

If you want to get case detail:

    case_id = 1
    management = py_esm.IncidentManagement(session)
    case = management.get_case_detail(case_id)
    print(case)

_result:_
    
    {
        'id': 49526,
        'summary': 'CASE MESSAGE',
        'assignedTo': 999,
        'severity': 99,
        'orgId': 9,
        'statusId': 9,
        'openTime': '01/01/2021 00:00:01',
        'closeTime': '01/01/2021 01:01:01',
        'deviceList': None,
        'dataSourceList': ['111'],
        'eventList': 
            [
                {  
                    'id': '144159490847064022|3746639',
                    'lastTime': '01/01/2021 00:00:01',
                    'message': 'CASE MESSAGE'
                }
            ],
        'notes': 'CASE NOTES,
        'history':
        '
        \n------- Viewed: 01/01/2021 00:00:02(GMT)    user1 -------\n
        \n------- Viewed: 01/01/2021 02:00:01(GMT)    user2 -------\n
        \n------- Viewed: 01/01/2021 03:00:01(GMT)    user1 -------\n
        \n------- Viewed: 01/01/2021 04:04:01(GMT)    user1 -------\n
        '
    }

**Watchlists**

All fields in **Watchlists**:
   
    watchlist = py_esm.WatchList(session)
    all_fileds = watchlist.get_fields)
    print(all_fields)

_result:_
    
    [{'id': 6, 'name': 'UserIDDst'}, {'id': 7, 'name': 'UserIDSrc'}, {'id': 4259841, 'name': 'URL'},
    {'id': 8, 'name': 'Database_Name'}, {'id': 4259842, 'name': 'Message_Text'}]


This fields you get a filters when get watchlist:
        
    filter = [{'id': 6, 'name': 'UserIDDst'}]
    filtered_wl = watchlist.get_watchlists(filter)

To get a list of all watchlists:

    all_watchlists = watchlist.get_watchlists()
    print(all_watchlists)

_result:_ 

    {
        'id': 11,
        'active': True,
        'customType': 
            {
                'id': 0,
                'name': '7'
            },
        'dynamic': False,
        'scored': False,
        'valueCount': 1,
        'errorMsg': '',
        'hidden': False, 
        'type':
            {
                'id': 0,
                'name': 'MANUAL'
            },
        'source': 5,
        'name': 'WATCHLIST_1'
    }


The next function user watchlist_id. To replace the name Watchlist to id (if name is none return None):

    name = 'my_watchlist'
    name_to_id = watchlist.name_to_id(name)

More information about watchlist:

    watchlist_id = 11
    watchlist_detail = watchlist.get_details(watchlist_id)

_result:_ 

    {
        'ipsid': '0',
        'id': 11,
        'age': 0,
        'groups': '',
        'valueFile':
            {
                'fileToken': 'U2FsdGVkX1/ziTvmSbCRLh8WZPDHo3YJXCi/m1p8qjblaikjd1Sh+LNmqKhwfWL8CnGJouHX0KeudNM4LiMDwg..'
            },
        'values': None,
        'lineSkip': 0,
        'dbUrl': '',
        'postArgs': '',
        'ignoreRegex': '',
        'search': '', 
        'updateType': 'MANUAL',
        'updateDay': 0,
        'updateMin': 0,
        'recordCount': 7,
        'mountPoint': '',
        'jobTrackerURL': '',
        'jobTrackerPort': '12',
        'sslcheck': 'F',
        'matchRegex': '',
        'delimitRegex': '',
        'enabled': True,
        'lookup': '',
        'method': 0,
        'port': '12',
        'path': '',
        'username': '',
        'password': '',
        'query': '',
        'active': False,
        'customType': 
            {
                'id': 0,
                'name': 'MANUAL'
            },
        'dynamic': False,
        'scored': False,
        'valueCount': 0,
        'errorMsg': None,
        'hidden': False,
        'type': 
            {
                'id': 0,
                'name': 'MANUAL'
            },
        'source': 5,
        'name': 'WATCHLIST_1'
    }

Get values on watchlist:

    watchlist_id = 11
    watchlist_valies = watchlist.get_values(watchlist_id)

_result:_

    ('value1', 'value2', 'value3', 'value4')



    
    
