#!/bin/bash

#移除虚拟环境
rm -rf .venv
python3 -m venv .venv
#激活venv环境
source .venv/bin/activate
#venv环境下安装必要的组件
python3 -m pip install -r requirements.txt
#退出虚拟环境
deactivate
#加执行权限
chmod u+x start.sh
