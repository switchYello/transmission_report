import base64
import datetime
import socket
import sys
from textwrap import fill

import prettytable as pt
import requests
import socks
from prettytable import SINGLE_BORDER


class Torrent:
    def __init__(self, name, size, downloadDir):
        self._name = name
        self._size = size
        self._download_dir = downloadDir
        self._track_list = []

    def append_track(self, t, last_update):
        self._track_list.append({'track': t, 'last_update': last_update})

    def get_name(self):
        return self._name

    def get_size(self):
        return self._size

    def get_track_list(self):
        return list(map(lambda t: t['track'], self._track_list))

    def get_download_dir(self):
        return self._download_dir

    def get_track_len(self):
        return len(self._track_list)

    def contain_track(self, search_track: str) -> bool:
        if search_track is None or search_track.strip() == '':
            return True
        for tra in self._track_list:
            if search_track in tra['track']:
                return True
        return False

    # size对象是B，获取文件的MB大小用于比较
    def get_mb_size(self):
        return float(self._size) / 1024 / 1024

    def pretty_size(self):
        return byte_format(self._size)

    def pretty_track(self):
        self._track_list.sort(key=lambda t: t['track'])
        return "\n".join(map(lambda t: '{} ({})'.format(t['track'], t['last_update']), self._track_list))


# 参数接收
args = sys.argv
_tr_host = args[1]
_username = args[2]
_password = args[3]
_show_min_size_mb = int(args[4])
_show_count = int(args[5])
_search_track = args[6]


# debug
# socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1086)
# socket.socket = socks.socksocket

def byte_format(bytes):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
    s = float(bytes)
    for unit in units:
        if s < 1024:
            return "%.2f %s" % (s, unit)
        else:
            s = s / 1024
    return '有这么大吗'


def fetch_data():
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
    "arguments": {"fields": ["id","name","totalSize","trackerStats","activityDate","downloadDir"]},
    "tag": ""
    }'''

    # 调用接口获取全量种子信息
    resp = requests.post(_tr_host + '/transmission/rpc', data=data_, headers=heads_)
    # 如果是409则添加请求头后重新请求重新请求
    if resp.status_code == 409:
        sessionId = resp.headers['x-transmission-session-id']
        heads_.update({'X-Transmission-Session-Id': sessionId})
        resp = requests.post(_tr_host + '/transmission/rpc', data=data_, headers=heads_)
    if resp.status_code == 401:
        raise Exception('username or password is incorrect')
    # 解析响应报文
    if not resp.status_code == 200:
        raise Exception("请求tr失败:", resp.text)
    torrent_list: list = resp.json()['arguments']['torrents']
    return torrent_list


def parse_data(torrent_list: list):
    # 预处理生成track关系映射
    # 有的种子有一个track，有个种子有多个track，如果同一个种子有多个track的则应该只计算一次
    # 比如有个种子有hkd.org,hkd.in两个track，其实这两个track都属于hkd这个站点的，则只统计一次到hkd.org上。并且后续的所有hkd.in都计算时当成hkd.org
    # 将种子列表按照track数量排序，数量多个排前面，一次插入映射表
    torrent_list.sort(key=lambda torrent: len(torrent['trackerStats']), reverse=True)
    track_mapper = {}  # 维护一张映射表，将hkd.org映射为hkd.org，hkd.in也映射为hkd.in
    for torrent in torrent_list:
        tracks = torrent['trackerStats']
        tracks.sort(key=lambda torrent: torrent['sitename'])  # track名字按照自然顺序排序
        first_track = tracks[0]  # 取排序后的第一个
        for track in tracks:
            track_mapper.setdefault(track['sitename'], first_track['sitename'])  # 全部映射到第一个track的名字上

    #
    # 遍历种子列表开始统计，如果一个种子有多个track则只统计一次，并且名称按照上面的映射表统一映射
    table = {}
    for torrent in torrent_list:
        file_name = torrent['name']
        file_size = torrent['totalSize']
        download_dir = torrent['downloadDir']
        key = "{}-{}".format(file_name, file_size)
        torrent_item = table.get(key, Torrent(file_name, file_size, download_dir))  # 获取指定种子的track列表
        first_tracker = torrent['trackerStats'][0]  # 取第一个track
        torrent_item.append_track(track_mapper[first_tracker['sitename']], datetime.datetime.fromtimestamp(torrent['activityDate']).strftime('%Y-%m-%d %H:%M:%S'))
        table[key] = torrent_item
    # 将整理好的种子转移到result中，进行筛选个过滤
    result = []
    result.extend(table.values())
    return result


# 按照站点统计每个种子的大小和计数，生成总览报表
def print_all_report(result):
    size_table = {}  # 按站点统计数量和大小
    for torr in result:
        for sitename in torr.get_track_list():
            exist = size_table.get(sitename, {'site': sitename, 'size': 0, 'count': 0})
            exist['size'] += torr.get_size()
            exist['count'] += 1
            size_table.update({sitename: exist})
    t1 = pt.PrettyTable(['站点', '做种个数', '做种大小'])
    values = list(size_table.values())
    values.sort(key=lambda a: a['size'], reverse=True)
    for v in values:
        t1.add_row([v['site'], v['count'], byte_format(v['size'])], divider=True)
    t1.set_style(SINGLE_BORDER)
    t1.title = '数据总览'
    t1.add_autoindex('序号')
    return t1


# 生成明细报表
def print_detail_report(result):
    # 各种过滤
    result = list(filter(lambda torr: torr.get_mb_size() > _show_min_size_mb, result))  # 过滤掉小于指定大小的种子
    result = list(filter(lambda torr: torr.contain_track(_search_track), result))  # 筛选包含需要搜索的track字符的种子
    result.sort(key=lambda torr: torr.get_size(), reverse=True)  # 从大到小排序排序
    result = result[0:_show_count]  # 已经按大排序了，切片指定数量
    # 构建表格打印
    t = pt.PrettyTable(['文件名', '下载路径', '站点数量', '文件大小', '站点名称(最后活跃时间)'])
    for it in result:
        t.add_row([fill(it.get_name(), width=90), it.get_download_dir(), it.get_track_len(), it.pretty_size(), it.pretty_track()], divider=True)
    t.align['站点名称(最后活跃时间)'] = 'l'
    t.set_style(SINGLE_BORDER)
    t.add_autoindex('序号')
    return t


data = fetch_data()
result = parse_data(data)
print(print_detail_report(result))
print(print_all_report(result))
