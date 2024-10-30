#!/bin/bash

host=http://127.0.0.1:9091
username=
password=
show_min_size_mb=0
show_count=2000

while getopts 'h:u:p:m:c:' opt; do
  case "$opt" in
  h)
    host="$OPTARG"
    ;;
  u)
    username="$OPTARG"
    ;;
  p)
    password="$OPTARG"
    ;;
  m)
    show_min_size_mb="$OPTARG"
    ;;
  c)
    show_count="$OPTARG"
    ;;
  '?')
    echo "-h 指定tr地址，默认http://127.0.0.1:9091"
    echo "-u 指定用户名 默认tr"
    echo "-p指定密码 默认tr"
    echo "-m小于该大小的种子不显示,单位为MB 默认0"
    echo "-c展示前多少个种子 2000"
    exit 1
    ;;
  esac
done

workdir=$(
  cd "$(dirname "${BASH_SOURCE[0]}")" || exit
  pwd
)

source "${workdir}"/.venv/bin/activate
python3 "${workdir}"/main.py "$host" "$username" "$password" "$show_min_size_mb" "$show_count"
deactivate
