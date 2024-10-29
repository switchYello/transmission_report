import base64
import json
import socket
import sys
from textwrap import fill

import prettytable as pt
import requests
import socks
from prettytable import SINGLE_BORDER


class Torrent:
    def __init__(self, name, size):
        self._name = name
        self._size = size
        self._track_list = []

    def append_track(self, t):
        self._track_list.append(t)

    def get_name(self):
        return self._name

    def get_size(self):
        return self._size

    def get_track_len(self):
        return len(self._track_list)

    # size对象是B，获取文件的MB大小用于比较
    def get_mb_size(self):
        return float(self._size) / 1024 / 1024

    def pretty_size(self):
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
        s = float(self._size)
        for unit in units:
            if s < 1024:
                return "%.2f %s" % (s, unit)
            else:
                s = s / 1024
        return '有这么大吗'

    def pretty_track(self):
        self._track_list.sort()
        return "\n".join(self._track_list)


# 参数接收
args = sys.argv
_tr_host = args[1]
_username = args[2]
_password = args[3]
_show_min_size_mb = int(args[4])
_show_count = int(args[5])

# debug
# socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1086)
# socket.socket = socks.socksocket

heads_: dict = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}
# base验证
if len(_username) > 0 and len(_password) > 0:
    encoded = base64.b64encode((_username + ':' + _password).encode('utf-8'))
    encodestring = encoded.decode('utf-8')
    heads_.update({"Authorization": "Basic " + encodestring})

data_ = '''{
"method": "torrent-get",
"arguments": {"fields": ["id","name","totalSize","trackerStats"]},
"tag": ""
}'''
# 获取全量种子信息
resp = requests.post(_tr_host + '/transmission/rpc', data=data_, headers=heads_)
# 如果是409则添加请求头后重新请求重新请求
if resp.status_code == 409:
    sessionId = resp.headers['x-transmission-session-id']
    heads_.update({'X-Transmission-Session-Id': sessionId})
    resp = requests.post(_tr_host + '/transmission/rpc', data=data_, headers=heads_)
# 解析响应报文
if not resp.status_code == 200:
    print("请求tr失败:", resp.text)
    exit(-1)
torrent_list = json.loads(resp.text)['arguments']['torrents']

# 创建一个dict，键是种子名拼大小确定唯一值，值为种子对象
table = {}
for torrent in torrent_list:
    name = torrent['name']
    totalSize = torrent['totalSize']
    key = "{}-{}".format(name, totalSize)
    for track in torrent['trackerStats']:
        torrent = table.get(key, Torrent(name, totalSize))  # 获取指定种子的track列表
        torrent.append_track(track['sitename'])
        table[key] = torrent

# 过滤
result = []
result.extend(table.values())
result = list(filter(lambda torr: torr.get_mb_size() > _show_min_size_mb, result))  # 过滤掉小于指定大小的种子
result.sort(key=lambda torr: torr.get_size(), reverse=True)  # 从大到小排序排序
result = result[0:_show_count]  # 已经按大排序了，切片指定数量

# 构建表格打印
t = pt.PrettyTable(['index', 'name', 'trackCount', 'size', 'sitename'])
for index, it in enumerate(result):
    t.add_row([index, fill(it.get_name(), width=100), it.get_track_len(), it.pretty_size(), it.pretty_track()], divider=True)
t.align['sitename'] = 'l'
t.set_style(SINGLE_BORDER)
print(t)
