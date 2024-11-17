import requests
from requests.auth import HTTPBasicAuth


class Transmission:

    def __init__(self, host, username, password):
        self._host = host
        self._username = username
        self._password = password

    def fetch_data(self) -> list:
        data_ = '''{
            "method": "torrent-get",
            "arguments": {"fields": ["name","totalSize","trackerStats","activityDate","downloadDir"]},
            "tag": ""
        }'''
        session = requests.Session()
        session.headers.update({"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"})
        # base验证
        if len(self._username) > 0 and len(self._password) > 0:
            session.auth = HTTPBasicAuth(self._username, self._password)
        resp = session.post(self._host + '/transmission/rpc', data=data_, timeout=20)
        if resp.status_code == 409:  # 如果是409则添加请求头后重新请求重新请求
            sessionId = resp.headers['x-transmission-session-id']
            session.headers.update({'X-Transmission-Session-Id': sessionId})
            resp = session.post(self._host + '/transmission/rpc', data=data_)
        if resp.status_code == 401:
            raise Exception('username or password is incorrect')
        # 解析响应报文,若果响应头不是200 或者包含特定的字符，说明失败了
        if not resp.status_code == 200 or "<!DOCTYPE HTML>" in resp.text:
            raise Exception("transmission返回结果不正确:", resp.text)
        torrent_list: list = resp.json().get('arguments', {}).get('torrents', [])
        return torrent_list
