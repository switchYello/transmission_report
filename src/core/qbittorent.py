import requests

import utils


class Qbittorent:

    def __init__(self, host, username, password):
        self._host = host
        self._username = username
        self._password = password
        session = requests.Session()
        session.headers.update({"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                                "referer": self._host})
        self._session = session
        self._login()

    def _login(self):
        _params = {
            "username": self._username,
            "password": self._password
        }
        login_result = self._session.post(self._host + '/api/v2/auth/login', params=_params, timeout=10)
        if login_result.status_code != 200:
            raise Exception("登陆失败:{} {}".format(login_result.status_code, login_result.text))

    def fetch_data(self) -> list:
        data_ = 'rid=0&m32sv6ju'
        resp = self._session.get(self._host + '/api/v2/sync/maindata', data=data_)
        # 解析响应报文
        if resp.status_code != 200:
            raise Exception("请求qb失败:{},{}:".format(resp.status_code, resp.text))
        resp = resp.json()
        torrents: dict = resp['torrents']
        trackers: dict = resp['trackers']
        result = []
        for k, v in torrents.items():
            item = {}
            item.update({'name': v['name']})
            item.update({'totalSize': v['size']})
            item.update({'activityDate': v['last_activity']})
            item.update({'downloadDir': v['save_path']})
            item.update({'infohash_v1': v['infohash_v1']})
            item.update({'trackerStats': list()})
            result.append(item)
        for track, hashs in trackers.items():
            for hash in hashs:
                find = filter(lambda a: a['infohash_v1'] == hash, result)
                for torr in find:
                    torr['trackerStats'].append({'announce': track, 'sitename': utils.extract_domain(track)})
        return result
