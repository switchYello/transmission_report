import json
import os

import utils


class Config:
    def __init__(self):
        _downloader_user_config_path = os.path.dirname(__file__) + '/../config/downloade_config.json'
        _group__base_config_path = os.path.dirname(__file__) + '/../base_config/group_config.json'
        _group_user_config_path = os.path.dirname(__file__) + '/../config/group_config.json'
        _alias_base_config_path = os.path.dirname(__file__) + '/../base_config/site_alias_config.json'
        _alias_user_config_path = os.path.dirname(__file__) + '/../config/site_alias_config.json'

        self.downloader_config = []
        self.group_config = []
        self.alias_config = {}

        # 加载下载器配置
        if os.path.exists(_downloader_user_config_path):
            with open(_downloader_user_config_path, 'r') as file:
                configs: list = json.load(file)
                self.downloader_config = configs

        # 加载官组配置（优先加载用户的，内置的排后面）
        if os.path.exists(_group_user_config_path):
            with open(_group_user_config_path, 'r') as file:
                configs: list = json.load(file)
                self.group_config.extend(configs)
        if os.path.exists(_group__base_config_path):
            with open(_group__base_config_path, 'r') as file:
                configs: list = json.load(file)
                self.group_config.extend(configs)

        # 加载别名配置 (使用update方式，优先加载内置的)
        if os.path.exists(_alias_base_config_path):
            with open(_alias_base_config_path, 'r') as file:
                alias_configs: dict = json.load(file)
                # 扩展配置文件为根域名形式后再存一份
                for k, v in dict(alias_configs).items():
                    domain = utils.extract_root_domain(k)
                    if domain != k:
                        alias_configs.setdefault(domain, v)
                self.alias_config.update(alias_configs)
        if os.path.exists(_alias_user_config_path):
            with open(_alias_user_config_path, 'r') as file:
                alias_configs: dict = json.load(file)
                # 扩展配置文件为根域名形式
                for k, v in dict(alias_configs).items():
                    domain = utils.extract_root_domain(k)
                    if domain != k:
                        alias_configs.setdefault(domain, v)
                self.alias_config.update(alias_configs)

    # 下载器
    def get_downloader_config(self):
        return self.downloader_config

    # 别名
    def get_alias_config(self):
        return self.alias_config

    # 官组
    def get_group_config(self):
        return self.group_config
