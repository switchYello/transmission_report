#!/bin/bash

host=http://127.0.0.1:9091
username=
password=
show_min_size_mb=0
show_count=500
search_track=

while getopts 'h:u:p:m:c:t:' opt; do
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
  t)
    search_track="$OPTARG"
    ;;
  '?')
    echo "-h 指定tr地址，默认http://127.0.0.1:9091"
    echo "-u 指定用户名 默认无"
    echo "-p 指定密码 默认无"
    echo "-m 小于该大小的种子不显示,单位为MB 默认0"
    echo "-c 展示前多少个种子 1000"
    echo "-t 搜索的track名称,模糊搜索"
    exit 1
    ;;
  esac
done

workdir=$(
  cd "$(dirname "${BASH_SOURCE[0]}")" || exit
  pwd
)

source "${workdir}"/.venv/bin/activate
python3 "${workdir}"/main.py "$host" "$username" "$password" "$show_min_size_mb" "$show_count" "$search_track"
deactivate
