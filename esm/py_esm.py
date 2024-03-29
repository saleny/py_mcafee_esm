from .special_requets import EsmRequest
from base64 import b64encode
from time import sleep
from re import split, search


class User:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def username(self) -> str:
        return str(b64encode(bytes(self.username, 'utf-8')), 'utf-8')

    def password(self) -> str:
        return str(b64encode(bytes(self.password, 'utf-8')), 'utf-8')


class Session(User, EsmRequest):
    def __init__(self, username: str, password: str, url: str, verify: bool = False):
        User.__init__(self, username, password)
        self.verify = verify
        self.url = url

    def login(self) -> dict:
        params = {"username": super().username(), "password": super().password(), "locale": "en_US"}
        headers = {'Content-Type': 'application/json'}
        EsmRequest.__init__(self, self.url, headers=headers, verify=self.verify)
        request = super().esm_post('login', params)
        headers['Cookie'], headers['X-Xsrf-Token'] = request.headers['Set-Cookie'], request.headers['Xsrf-Token']
        EsmRequest.__init__(self, self.url, headers=headers, verify=self.verify)
        return headers

    def logout(self):
        return super().esm_delete('logout')


class GetDevice(EsmRequest):
    def __init__(self, active_session: User):
        super().__init__(active_session.url, headers=active_session.headers, verify=active_session.verify)

    def get_receivers(self, types) -> tuple:
        return tuple(super().esm_post('devGetDeviceList?filterByRights=false', {'types': [types]}).json())

    def get_device(self, device_type):
        # device type may be
        # "IPS"
        # "POLICY"
        # "RECEIVER"
        # "THIRD_PARTY"
        # "DBM"
        # "DBM_DB"
        # "DBM_AGENT"
        # "VA"
        # "IPSVIPS"
        # "ESM"
        # "APM"
        # "APMVIPS"
        # "ELM"
        # "ELMREC"
        # "LOCALESM"
        # "RISK"
        # "ASSET"
        # "RISKMANAGER"
        # "RISKAGENT"
        # "EPO"
        # "EPO_APP"
        # "NSM"
        # "NSM_SENSOR"
        # "NSM_INTERFACE"
        # "MVM"
        # "SEARCH_ELASTIC"
        # "KID_CLUSTER"
        # "KID_NODE"
        # "SYSTEM"
        # "BUCKET"
        # "UNKNOWN
        try:
            device = super().esm_post('devGetDeviceList?filterByRights=false', {'types': [device_type]})
            device_json = device.json()
        except ValueError:
            return tuple('Error or Not Found', device)
        return device_json

    def get_data_sources(self, receiver_list: tuple = None) -> dict:
        data_sources = list()
        if not receiver_list:
            receiver_list = self.get_receivers('RECEIVER')
        for rec in receiver_list:
            data_sources.append(super().esm_post('dsGetDataSourceList', {'receiverId': rec['id']}).json())
        return data_sources[0]

    def get_data_source_detail(self, data_sources: list):
        data_source_dict = dict()
        for ds in data_sources:
            data_source_detail = super().esm_post('dsGetDataSourceDetail', {'datasourceId': ds['id']})
            # print(data_source_detail.text)
            try:
                data_source_dict.update({data_source_detail['ipAddress']: data_source_detail['name']})
            except TypeError:
                continue
        return data_source_dict


class IncidentManagement(EsmRequest):
    def __init__(self, active_session: User):
        super().__init__(active_session.url, headers=active_session.headers, verify=active_session.verify)

    def get_incidents(self, fields, filters, sort, sort_field, limit) -> tuple:
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

    def get_case_detail(self, case_id: int) -> dict:
        return super().esm_post('caseGetCaseDetail', {'id': case_id}).json()

    def get_case_events_detail(self, events_ids: list):
        data = \
            {
                "eventIds":
                    {
                        "list": events_ids
                    }
            }
        return super().esm_post('caseGetCaseEventsDetail', data).json()

    def parsing_notes_in_case(self, case_id: int):  # специально для интеграции. На вход case_detail на выход
        # {'date_time': ['09/02/2021 22:34:53'], 'author': ['admin@ff.so'],
        # 'comments': 'this is comment in case'}
        case = self.get_case_detail()
        notes_split = split(r'(------- .*)', case['notes'], maxsplit=10)
        comments = []
        date_time = []
        author = []
        comments_in_incident = {}
        for comment in notes_split:
            if '------- Comment Added' in comment:
                date_time.append(search('(\d{2}/\d{2}/\d{4}.)(([0-1]\d|2[0-3]):[0-5]\d:[0-5]\d)', comment).group(0))
                author.append(search('\S{3,}@\w{3,}.so', comment).group(0))
                comments.append(notes_split[notes_split.index(comment) + 1])
        comments_in_incident.update({'date_time': date_time, 'author': author, 'comments': comment})
        return comments_in_incident


class GetDetail(EsmRequest):
    def __init__(self, active_session: User):
        super().__init__(active_session.url, headers=active_session.headers, verify=active_session.verify)

    def status(self, resId: int) -> None:
        data = {"resultID": resId}
        post = super().esm_post('qryGetStatus', data)
        while 1:
            post = super().esm_post('qryGetStatus', data)
            if post.json()['percentComplete'] != 100:
                sleep(2)
                continue
            else:
                break

    def request(self, time_range: str, sigID: int, limit=30000) -> dict:
        data = {
            "config": {
                "timeRange": time_range,
                "includeTotal": True,
                "fields": [
                    {
                        "typeBits": 17,
                        "id": None,
                        "name": "IPSID"
                    },
                    {
                        "typeBits": 3,
                        "id": "7",
                        "name": "UserIDSrc"
                    },
                ],
                "filters": [
                    {
                        "type": "EsmFieldFilter",
                        "field": {
                            "name": "DSIDSigID"
                        },
                        "operator": "EQUALS",
                        "values": [{
                            "type": "EsmBasicValue",
                            "value": sigID
                        }]
                    }
                ],
                "limit": limit,
                "offset": 0
            }
        }
        response = super().esm_post('qryExecuteDetail?type=EVENT&reverse=false', data).json()
        return response

    def result(self, time_range: str, sigID: int) -> str:
        response = self.request(time_range, sigID)
        resId = response['resultID']
        self.status(resId)
        data = {"resultID": resId}
        esm_post = super().esm_post('qryGetResults?startPos=0&numRows=9999999', data)
        return esm_post.json()['rows']


class WatchList(EsmRequest):
    def __init__(self, active_session: User):
        super().__init__(active_session.url, headers=active_session.headers, verify=active_session.verify)

    def add_watchlist_values(self, values: list, watchlist_id: int) -> None:
        return super().esm_post('sysAddWatchlistValues', {'watchlist': watchlist_id, 'values': [values]}).text

    def get_fields(self) -> dict:
        return super().esm_post('sysGetWatchlistFields', {}).json()

    def get_watchlists(self, filters: list = None) -> tuple:
        if filters is None:
            filters = list()
        return tuple(
            super().esm_post('sysGetWatchlists?hidden=false&dynamic=false&writeOnly=false&indexedOnly=false',
                             {'filters': filters}).json())

    def get_details(self, watchlist_id: int) -> dict:
        return super().esm_post('sysGetWatchlistDetails', {'id': watchlist_id}).json()

    def get_values(self, watchlist_id: int) -> tuple:
        file_token = self.get_details(watchlist_id)['valueFile']['fileToken']
        return tuple(super().default_post('rs/watchlists/getValues', {'fileToken': file_token}).json()['data'])

    def remove_values(self, watchlist_id: int, values: list) -> str:
        return super().esm_post('sysRemoveWatchlistValues', {'watchlist': watchlist_id, 'values': values}).text

    def name_to_id(self, watchlist_name: str) -> str:
        watchlists = self.get_watchlists()
        for watchlist in watchlists:
            if watchlist['name'] == watchlist_name:
                return watchlist['id']
