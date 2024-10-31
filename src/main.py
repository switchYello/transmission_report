import datetime
import json
import re
import sys
from textwrap import fill

import prettytable as pt
import requests
import tldextract
from prettytable import SINGLE_BORDER
from requests.auth import HTTPBasicAuth


class Torrent:
    def __init__(self, filename, size, downloadDir):
        self._filename = filename
        self._size = size
        self._download_dir = downloadDir
        self._site_list = []
        self._track_list = []

    # 站点视角，每个种子记录只会属于一个站点
    def append_site(self, site, is_group, last_update):
        self._site_list.append({'site': site, 'is_group': is_group, 'last_update': last_update})

    # track视角，每个种子可以有多个站点、每个站点有多个track
    def append_track(self, site, host, announce):
        self._track_list.append({"site": site, "host": host, "announce": announce})

    def get_name(self):
        return self._filename

    def get_size(self):
        return self._size

    def get_download_dir(self):
        return self._download_dir

    def get_site_list(self):
        return list(self._site_list)

    def get_track_list(self):
        return list(self._track_list)

    def contain_track(self, search_track: str) -> bool:
        if search_track is None or search_track.strip() == '':
            return True
        for tra in self._site_list:
            if search_track in tra['site']:
                return True
        return False

    # size对象是B，获取文件的MB大小用于比较
    def get_mb_size(self):
        return float(self._size) / 1024 / 1024

    def pretty_size(self):
        return _byte_format(self._size)

    def pretty_track(self):
        self._site_list.sort(key=lambda t: t['site'])
        return "\n".join(map(lambda t: '{}{} ({})'.format(t['site'], '(官种)' if t['is_group'] else '', t['last_update']), self._site_list))


# 参数接收
args = sys.argv
_tr_host = args[1]
_username = args[2]
_password = args[3]
_show_min_size_mb = int(args[4])
_show_count = int(args[5])
_search_track = args[6]


#
# # debug
# socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1086)
# socket.socket = socks.socksocket

def fetch_data() -> list:
    data_ = '''{
        "method": "torrent-get",
        "arguments": {"fields": ["id","name","totalSize","trackerStats","activityDate","downloadDir","host","announce"]},
        "tag": ""
    }'''
    session = requests.Session()
    session.headers.update({"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"})
    # base验证
    if len(_username) > 0 and len(_password) > 0:
        session.auth = HTTPBasicAuth(_username, _password)
    resp = session.post(_tr_host + '/transmission/rpc', data=data_)
    if resp.status_code == 409:  # 如果是409则添加请求头后重新请求重新请求
        sessionId = resp.headers['x-transmission-session-id']
        session.headers.update({'X-Transmission-Session-Id': sessionId})
        resp = session.post(_tr_host + '/transmission/rpc', data=data_)
    if resp.status_code == 401:
        raise Exception('username or password is incorrect')
    # 解析响应报文
    if not resp.status_code == 200:
        raise Exception("请求tr失败:", resp.text)
    torrent_list: list = resp.json()['arguments']['torrents']
    return torrent_list


def parse_data(torrent_list: list) -> list:
    with open('group_config.json', 'r') as file:
        configs: list = json.load(file)
    # 预处理生成track关系映射
    # 有的种子有一个track，有个种子有多个track，如果同一个种子有多个track的则应该只计算一次
    # 比如有个种子有hkd.org,hkd.in两个track，其实这两个track都属于hkd这个站点的，则只统计一次到hkd.org上。并且后续的所有hkd.in都计算时当成hkd.org
    # 将种子列表按照track数量排序，数量多个排前面，一次插入映射表
    torrent_list.sort(key=lambda torrent: len(torrent['trackerStats']), reverse=True)
    track_mapper = {}  # 维护一张映射表，将hkd.org映射为hkd.org，hkd.in也映射为hkd.in
    for torrent_json in torrent_list:
        tracks = torrent_json['trackerStats']
        tracks.sort(key=lambda torrent: torrent['sitename'])  # track名字按照自然顺序排序
        first_track = tracks[0]  # 取排序后的第一个
        for track in tracks:
            track_mapper.setdefault(track['sitename'], first_track['sitename'])  # 全部映射到第一个track的名字上

    #
    # 遍历种子列表开始统计，如果一个种子有多个track则只统计一次，并且名称按照上面的映射表统一映射
    table = {}
    for torrent_json in torrent_list:
        file_name = torrent_json['name']
        file_size = torrent_json['totalSize']
        download_dir = torrent_json['downloadDir']
        key = "{}-{}".format(file_name, file_size)
        torrent_item = table.get(key, Torrent(file_name, file_size, download_dir))  # 获取指定种子的track列表
        first_tracker = torrent_json['trackerStats'][0]  # 取第一个track
        sitename = track_mapper[first_tracker['sitename']]  # 第一个track的站点名称作为整个种子的站点名称
        for track in torrent_json['trackerStats']:
            torrent_item.append_track(sitename, track['host'], track['announce'])
        # 筛选官种配置
        _filter_config, _filter_site = _search_config(configs, torrent_item)
        torrent_item.append_site(sitename, _filter_config is not None and _filter_site == sitename, datetime.datetime.fromtimestamp(torrent_json['activityDate']).strftime('%Y-%m-%d %H:%M:%S'))
        table.setdefault(key, torrent_item)
    # 将整理好的种子转移到result中，进行筛选个过滤
    result = []
    result.extend(table.values())
    return result


# 生成明细报表
def generate_detail_report(result):
    result = result[:]
    result = list(filter(lambda torr: torr.get_mb_size() > _show_min_size_mb, result))  # 过滤掉小于指定大小的种子
    result = list(filter(lambda torr: torr.contain_track(_search_track), result))  # 筛选包含需要搜索的track字符的种子
    result.sort(key=lambda torr: torr.get_size(), reverse=True)  # 从大到小排序排序
    result = result[0:_show_count]  # 已经按大排序了，切片指定数量
    # 构建表格打印
    t = pt.PrettyTable(['文件名', '下载路径', '站点数量', '文件大小', '站点名称(最后活跃时间)'])
    for it in result:
        t.add_row([
            fill(it.get_name(), width=90),
            it.get_download_dir(),
            len(it.get_site_list()),
            it.pretty_size(),
            it.pretty_track()
        ], divider=True)
    t.title = '文件明细视图'
    t.align['站点名称(最后活跃时间)'] = 'l'
    t.set_style(SINGLE_BORDER)
    t.add_autoindex('序号')
    return t


# 统计官种，生成总览报表
#
def generate_group_report(result):
    group_table = {}
    all_count = 0  # 种子总数，一个种子多个站点只计算一次
    all_size = 0  # 种子总占用，一个种子多个站点只计算一次
    for torr in result:
        all_count += 1
        all_size += torr.get_size()
        # 统计官种和非官种
        for site in torr.get_site_list():
            _group_detail = group_table.setdefault(site['site'], {"site": site['site'], "g_count": 0, "g_size": 0, "o_count": 0, "o_size": 0, 'multSeedCount': 0, 'multSeedSize': 0})  # 站点
            if site['is_group']:
                _group_detail['g_count'] += 1
                _group_detail['g_size'] += torr.get_size()
            else:
                _group_detail['o_count'] += 1
                _group_detail['o_size'] += torr.get_size()
            # 统计辅种的数据，站点多余1个表示这份文件在多个站点使用到算做辅种
            if len(torr.get_site_list()) > 1:
                _group_detail['multSeedCount'] += 1
                _group_detail['multSeedSize'] += torr.get_size()
    values = list(group_table.values())
    values.sort(key=lambda d: (d['g_size'] + d['o_size']), reverse=True)
    t = pt.PrettyTable(['站点', '官种数', '官种大小', '非官种数', '非官种大小', '做种总数', '做种总大小', '辅种数', '辅种总大小', '辅种比例'])
    for v in values:
        t.add_row([
            v['site'],
            v['g_count'],
            _byte_format(v['g_size']),
            v['o_count'],
            _byte_format(v['o_size']),
            v['g_count'] + v['o_count'],
            _byte_format(v['g_size'] + v['o_size']),
            v['multSeedCount'],
            _byte_format(v['multSeedSize']),
            '%.2f%%' % (v['multSeedSize'] / (v['g_size'] + v['o_size']) * 100)
        ], divider=True)
    t.title = '辅种视图,去重种子总数:%d 实际磁盘占用:%s' % (all_count, _byte_format(all_size))
    t.set_style(SINGLE_BORDER)
    t.add_autoindex('序号')
    return t


def _search_config(configs: list, torr: Torrent):
    _filter_config = None
    _filter_site = None
    for _config in configs:
        _config_host = _config['host']  # 允许配置中使用逗号分割多个
        _siteRegex = _config['siteRegex']
        for _track in torr.get_track_list():
            if _extract_root_domain(_track['announce']) in _config_host and re.search(_siteRegex, torr.get_name(), re.I):  # 站点符合配置且官组符合配置
                _filter_config = _config
                _filter_site = _track['site']
                break
        if _filter_config:
            break
    return _filter_config, _filter_site


def _extract_root_domain(url):
    extracted = tldextract.extract(url)
    root_domain = extracted.registered_domain
    return root_domain


def _byte_format(bytes):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
    s = float(bytes)
    for unit in units:
        if s < 1024:
            return "%.2f %s" % (s, unit)
        else:
            s = s / 1024
    return '有这么大吗'


data = fetch_data()
_parsed_data = parse_data(data)
print(generate_detail_report(_parsed_data))
print(generate_group_report(_parsed_data))
