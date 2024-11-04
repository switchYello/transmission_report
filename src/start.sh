#!/bin/bash

filter_size=0
filter_count=500
filter_track=
filter_path=
filter_mult_seed_count=-1

while getopts ':m:c:t:p:f:?:' opt; do
  case "$opt" in
  m)
    filter_size="$OPTARG"
    ;;
  c)
    filter_count="$OPTARG"
    ;;
  t)
    filter_track="$OPTARG"
    ;;
  p)
    filter_path="$OPTARG"
    ;;
  f)
    filter_mult_seed_count="$OPTARG"
    ;;
  ?)
    echo "-m 小于该大小的种子不显示,单位为MB 默认0"
    echo "-c 展示前多少个种子 500"
    echo "-t 按照track名称或别名过滤,模糊搜索"
    echo "-p 按照存储路径过滤"
    echo "-f 按照辅种站点数量过滤"
    exit 1
    ;;
  esac
done

workdir=$(
  cd "$(dirname "${BASH_SOURCE[0]}")" || exit
  pwd
)

source "${workdir}"/.venv/bin/activate
python3 "${workdir}"/core/main.py "$filter_size" "$filter_count" "$filter_track" "$filter_path" "$filter_mult_seed_count"
deactivate
