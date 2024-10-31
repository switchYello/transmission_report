#!/bin/bash

#移除虚拟环境
echo '移除旧环境'
rm -rf .venv

echo '初始化虚拟环境'
python3 -m venv .venv
source .venv/bin/activate

echo 'venv环境下安装必要的组件'
python3 -m pip install -r requirements.txt

echo '安装完成'
deactivate
chmod u+x start.sh
