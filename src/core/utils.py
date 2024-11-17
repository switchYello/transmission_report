import tldextract
from urllib.parse import urlparse


# www.baidu.com ->baidu.com
def extract_root_domain(url):
    extracted = tldextract.extract(url)
    root_domain = extracted.registered_domain
    return root_domain


# www.baidu.com ->baidu
def extract_domain(url):
    extracted = tldextract.extract(url)
    domain = extracted.domain
    return domain


# 格式化域名
def format_domain(url):
    if not url[:4] == 'http':
        url = 'http://' + url
    extracted = urlparse(url)
    return extracted.scheme + "://" + extracted.netloc


def byte_format(bytes):
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
    s = float(bytes)
    for unit in units:
        if s < 1024:
            return "%.2f %s" % (s, unit)
        else:
            s = s / 1024
    return '有这么大吗'


def safe_get(arr, index, default):
    if 0 <= index < len(arr):
        return arr[index]
    else:
        return default
