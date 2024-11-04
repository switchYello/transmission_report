import json
import os

import utils


class Config:
    def __init__(self):
        _group_config_path = os.path.dirname(__file__) + '/../config/group_config.json'
        with open(_group_config_path, 'r') as file:
            configs: list = json.load(file)
            self.group_config = configs

        _alias_config_path = os.path.dirname(__file__) + '/../config/site_alias_config.json'
        with open(_alias_config_path, 'r') as file:
            alias_configs: dict = json.load(file)
            # 扩展配置文件为根域名形式
            for k, v in dict(alias_configs).items():
                domain = utils.extract_root_domain(k)
                if domain != k:
                    alias_configs.setdefault(domain, v)
            self.alias_config = alias_configs

        _downloader_config_path = os.path.dirname(__file__) + '/../config/downloade_config.json'
        with open(_downloader_config_path, 'r') as file:
            configs: list = json.load(file)
            self.downloader_config = configs

    # 下载器
    def get_downloader_config(self):
        return self.downloader_config

    # 别名
    def get_alias_config(self):
        return self.alias_config

    # 官组
    def get_group_config(self):
        return self.group_config
