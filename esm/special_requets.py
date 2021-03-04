from requests import post, get
from json import dumps


class EsmRequest:
    def __init__(self, url, headers=None, verify=False):
        self.url = url
        self.headers = headers
        self.verify = verify

    def esm_post(self, method, data):
        return post(f'{self.url}/rs/esm/v2/{method}',
                    data=dumps(data), headers=self.headers, verify=self.verify)

    def esm_get(self, method):
        return get(f'{self.url}/rs/esm/v2/{method}', headers=self.headers, verify=self.verify)

    def esm_int_post(self, data):
        return post(f'{self.url}/rs/v1/runningQuery', data=dumps(data), headers=self.headers, verify=self.verify)

    def esm_int_get(self, method):
        return get(f'{self.url}/rs/v1/runningQuery/{method}', headers=self.headers, verify=self.verify)

    def qry_close(self, result_id):
        return self.esm_post('qryClose', {'resultID': result_id})
