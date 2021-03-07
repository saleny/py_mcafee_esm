from .special_requets import EsmRequest
from base64 import b64encode
from time import sleep


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def username(self):
        return str(b64encode(bytes(self.username, 'utf-8')), 'utf-8')

    def password(self):
        return str(b64encode(bytes(self.password, 'utf-8')), 'utf-8')


class Session(User, EsmRequest):
    def __init__(self, username, password, url, verify=False):
        User.__init__(self, username, password)
        self.verify = verify
        self.url = url

    def login(self):
        params = {"username": super().username(), "password": super().password(), "locale": "en_US"}
        headers = {'Content-Type': 'application/json'}
        EsmRequest.__init__(self, self.url, headers=headers, verify=self.verify)
        request = super().esm_post('login', params)
        headers['Cookie'], headers['X-Xsrf-Token'] = request.headers['Set-Cookie'], request.headers['Xsrf-Token']
        EsmRequest.__init__(self, self.url, headers=headers, verify=self.verify)
        return headers

    def logout(self):
        pass


class GetDevice(EsmRequest):
    def __init__(self, active_session):
        super().__init__(active_session.url, headers=active_session.headers, verify=active_session.verify)

    def receivers(self):
        return super().esm_post('devGetDeviceList?filterByRights=false', {'types': ['RECEIVER']}).json()

    def data_sources(self, receiver_list=None):
        data_source_dict = dict()
        if not receiver_list:
            receiver_list = self.receivers()
        for rec in receiver_list:
            data_sources = super().esm_post('dsGetDataSourceList', {'receiverId': rec['id']}).json()
            for ds in data_sources:
                data_source_detail = super().esm_post('dsGetDataSourceDetail', {'datasourceId': ds['id']}).json()
                data_source_dict.update({data_source_detail['ipAddress']: data_source_detail['name']})
        return data_source_dict


class IncidentManagement(EsmRequest):
    def __init__(self, active_session):
        super().__init__(active_session.url, headers=active_session.headers, verify=active_session.verify)

    def get_incidents(self, fields, filters, sort, sort_field, limit):
        data = {"query": {"fields": {"opt": "SELECT", "opr": fields, "exp": None},
                          "sources": {"opt": "SOURCE", "opr": [],
                                      "exp": [{"opt": "EQUALS", "opr": ["QUERYID", "25876"], "exp": []},
                                              {"opt": "EQUALS", "opr": ["ESMQUERYTYPE", "CASE_QUERY"], "exp": []}]},
                          "filters": {"opt": "EQUALS", "opr": filters, "exp": None}, "groups": {},
                          "orders": {"opt": "ORDER", "opr": None,
                                     "exp": [{"opt": sort, "opr": [sort_field], "exp": None}]}},
                "customOptions": {"requireTimeFrame": False}, "queryParameters": [], "limit": limit, "offset": 0,
                "reverse": False, "getTotal": False}
        request = super().esm_int_post(data)
        result_id = request.json()['location'].split('/')[4]
        while True:
            sleep(1)
            request_result = super().esm_int_get(f'{result_id}?offset=0&page_size={limit}&reverse=false')
            if request_result:
                break
        super().qry_close(result_id)
        return tuple(request_result.json()['data'])

    def get_case_detail(self, case_id):
        return super().esm_post('caseGetCaseDetail', {'id': case_id}).json()


class WatchList(EsmRequest):
    def __init__(self, active_session):
        super().__init__(active_session.url, headers=active_session.headers, verify=active_session.verify)

    def get_fields(self):
        return super().esm_post('sysGetWatchlistFields', {}).json()

    def get_watchlists(self, filters=None):
        if filters is None:
            filters = list()
        return tuple(
            super().esm_post('sysGetWatchlists?hidden=false&dynamic=false&writeOnly=false&indexedOnly=false',
                             {'filters': filters}).json())

    def get_details(self, watchlist_id):
        return super().esm_post('sysGetWatchlistDetails', {'id': watchlist_id}).json()

    def get_values(self, watchlist_id):
        file_token = self.get_details(watchlist_id)['valueFile']['fileToken']
        return tuple(super().default_post('rs/watchlists/getValues', {'fileToken': file_token}).json()['data'])

    def remove_values(self, watchlist_id, values):
        return super().esm_post('sysRemoveWatchlistValues', {'watchlist': watchlist_id, 'values': values}).text

    def name_to_id(self, watchlist_name):
        watchlists = self.get_watchlists()
        for watchlist in watchlists:
            if watchlist['name'] == watchlist_name:
                return watchlist['id']

