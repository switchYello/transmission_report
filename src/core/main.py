import datetime
import re
import sys
from textwrap import fill

import prettytable as pt
from prettytable import SINGLE_BORDER

import utils
from config import Config
from qbittorent import Qbittorent
from transmission import Transmission
from utils import byte_format
from utils import safe_get


class Torrent:
    def __init__(self, filename, size, downloadDir):
        self._filename = filename
        self._size = size
        self._download_dir = downloadDir
        self._site_list = []
        self._track_list = []

    # 站点视角，每个种子记录只会属于一个站点
    def append_site(self, site, alias, is_group, last_update):
        self._site_list.append({'site': site, 'alias': alias, 'is_group': is_group, 'last_update': last_update})

    # track视角，每个种子可以有多个站点、每个站点有多个track
    def append_track(self, site, alias, announce):
        self._track_list.append({"site": site, 'alias': alias, "announce": announce})

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
            if search_track in tra['site'] or search_track in tra['alias']:
                return True
        return False

    def contain_path(self, search_path: str) -> bool:
        if search_path is None or search_path.strip() == '':
            return True
        return search_path.strip() in self._download_dir

    # size对象是B，获取文件的MB大小用于比较
    def get_mb_size(self):
        return float(self._size) / 1024 / 1024

    def pretty_size(self):
        return byte_format(self._size)

    def pretty_track(self):
        self._site_list.sort(key=lambda t: t['site'])
        return "\n".join(map(lambda t: '{}({}){} ({})'.format(t['site'], t['alias'], '(官种)' if t['is_group'] else '', t['last_update']), self._site_list))


# 参数接收
args = sys.argv
_show_min_size_mb = int(safe_get(args, 1, 0))
_show_count = int(safe_get(args, 2, 500))
_search_track = safe_get(args, 3, '')
_search_path = safe_get(args, 4, '')
_search_seed_count = int(safe_get(args, 5, -1))


#
# # debug
# socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1086)
# socket.socket = socks.socksocket

def parse_data(torrent_list: list, alias_configs, group_config) -> list:
    # 预处理生成track关系映射
    # 有的种子有一个track，有个种子有多个track，如果同一个种子有多个track的则应该只计算一次
    # 比如有个种子有hkd.org,hkd.in两个track，其实这两个track都属于hkd这个站点的，则只统计一次到hkd.org上。并且后续的所有hkd.in都计算时当成hkd.org
    # 将种子列表按照track数量排序，数量多个排前面，一次插入映射表
    torrent_list.sort(key=lambda torrent: len(torrent['trackerStats']), reverse=True)
    sitename_mapper = {}
    for torrent_json in torrent_list:
        _track_list = torrent_json['trackerStats']
        _track_list.sort(key=lambda torrent: torrent['announce'])  # track名字按照自然顺序排序
        first_track = _track_list[0]  # 取排序后的第一个
        # 决策别名,优先使用domain查找，查不到使用host查找，否则直接使用host
        target_alias = None
        for track in _track_list:
            track['root_domain'] = utils.extract_root_domain(track['announce'])  # 提取根域名
            if target_alias is None:
                target_alias = alias_configs.get(track['root_domain'])
        if target_alias is None:
            target_alias = first_track['root_domain']
        # 填充alias
        for track in _track_list:
            sitename_mapper.setdefault(track['sitename'], first_track['sitename'])
            track['sitename'] = sitename_mapper[track['sitename']]
            alias_configs.setdefault(track['root_domain'], target_alias)  # 后续都用查找到的alias
            track['alias'] = alias_configs[track['root_domain']]  # 根据配置设置别名，如果没有配置则使用host当别名

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
        alias = first_tracker['alias']  # 前面统一设置过alias
        sitename = first_tracker['sitename']  # 前面统一设置过sitename，第一个track的站点名称作为整个种子的站点名称
        for track in torrent_json['trackerStats']:
            torrent_item.append_track(sitename, alias, track['announce'])
        # 筛选官种配置
        _filter_config, _filter_site = _search_config(group_config, torrent_item)
        torrent_item.append_site(sitename
                                 , alias
                                 , _filter_config is not None and _filter_site == sitename
                                 , datetime.datetime.fromtimestamp(torrent_json['activityDate']).strftime('%Y-%m-%d %H:%M:%S'))
        table.setdefault(key, torrent_item)
    # 将整理好的种子转移到result中，进行筛选个过滤
    result = []
    result.extend(table.values())
    return result


# 生成明细报表
def generate_detail_report(result):
    result = result[:]
    result = list(filter(lambda torr: torr.get_mb_size() > _show_min_size_mb, result))  # 过滤掉小于指定大小的种子
    result = list(filter(lambda torr: torr.contain_track(_search_track), result))  # 筛选包含需要搜索track字符的种子 _search_track
    result = list(filter(lambda torr: torr.contain_path(_search_path), result))  # 筛选路径 _search_path
    if _search_seed_count != -1:
        result = list(filter(lambda torr: len(torr.get_site_list()) == _search_seed_count, result))  # 筛选 _search_seed_count
    result.sort(key=lambda torr: torr.get_size(), reverse=True)  # 从大到小排序排序
    result = result[0:_show_count]  # 已经按大排序了，切片指定数量  _show_count
    # 构建表格打印
    t = pt.PrettyTable(['文件名', '下载路径', '站点数量', '文件大小', '站点名称(最后活跃时间)'])
    for it in result:
        # 明细子表
        subTable = pt.PrettyTable(["站点", "官种", "最后活跃"])
        for site in it.get_site_list():
            subTable.add_row([site['alias'], '❤️' if site['is_group'] else '', site['last_update']])
            subTable.sortby = '最后活跃'
            subTable.reversesort = True
        # 主表
        t.add_row([fill(it.get_name(), width=80), it.get_download_dir(), len(it.get_site_list()), it.pretty_size(), subTable], divider=True)
    t.title = '文件明细视图'
    t.align['站点名称(最后活跃时间)'] = 'l'
    t.set_style(SINGLE_BORDER)
    t.add_autoindex('序号')
    return t


#
# 统计官种，生成总览报表
def generate_group_report(result):
    group_table = {}
    all_count = 0  # 种子总数，一个种子多个站点只计算一次
    all_size = 0  # 种子总占用，一个种子多个站点只计算一次
    for torr in result:
        all_count += 1
        all_size += torr.get_size()
        # 统计官种和非官种
        for site in torr.get_site_list():
            _group_detail = group_table.setdefault(site['alias'],
                                                   {"site": site['site'], "alias": site['alias'], "g_count": 0, "g_size": 0, "o_count": 0, "o_size": 0, 'multSeedCount': 0, 'multSeedSize': 0})  # 站点
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
    # 排序后将别名一致的向前提取
    # for i in range(0, len(values)):
    #     for j in range(0, i):
    #         if values[i]['alias'] == values[j]['alias']:
    #             pop = values.pop(i)
    #             values.insert(j + 1, pop)
    #             break
    t = pt.PrettyTable(['站点', '别名', '官种数', '官种大小', '非官种数', '非官种大小', '做种总数', '做种总大小', '辅种数', '辅种总大小', '辅种比例'])
    for v in values:
        t.add_row([
            v['site'],
            v['alias'],
            v['g_count'],
            byte_format(v['g_size']),
            v['o_count'],
            byte_format(v['o_size']),
            v['g_count'] + v['o_count'],
            byte_format(v['g_size'] + v['o_size']),
            v['multSeedCount'],
            byte_format(v['multSeedSize']),
            '%.2f%%' % (v['multSeedSize'] / (v['g_size'] + v['o_size']) * 100)
        ], divider=True)
    t.title = '辅种视图,去重种子总数:%d 实际磁盘占用:%s' % (all_count, byte_format(all_size))
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
            if utils.extract_root_domain(_track['announce']) in _config_host and re.search(_siteRegex, torr.get_name(), re.I):  # 站点符合配置且官组符合配置
                _filter_config = _config
                _filter_site = _track['site']
                break
        if _filter_config:
            break
    return _filter_config, _filter_site


config = Config()
downloaders = config.get_downloader_config()

# 获取数据
data = []
for downloader in downloaders:
    if downloader['type'] == 'transmission':
        tr = Transmission(downloader['url'], downloader['username'], downloader['password'])
        data.extend(tr.fetch_data())
    if downloader['type'] == 'qbittorent':
        qb = Qbittorent(downloader['url'], downloader['username'], downloader['password'])
        data.extend(qb.fetch_data())

# 配置
alias_configs = config.get_alias_config()
configs = config.get_group_config()
# 处理数据
_parsed_data = parse_data(data, alias_configs, configs)
print(generate_detail_report(_parsed_data))
print(generate_group_report(_parsed_data))
