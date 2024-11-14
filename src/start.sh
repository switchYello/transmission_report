#!/bin/bash

#docker固定src，非docker动态获取
if [ "$_RUN_IN_DOCKER" == 'true' ]; then
  WORKDIR="/src"
else
  WORKDIR=$(
    cd "$(dirname "${BASH_SOURCE[0]}")" || exit
    pwd
  )
fi

BASE_CONFIG="${WORKDIR}/base_config"
USER_CONFIG="${WORKDIR}/config"

if [ ! -d "$USER_CONFIG" ]; then
  mkdir "$USER_CONFIG"
fi
if [ ! -f "$USER_CONFIG/downloade_config.json" ]; then
  cp "${BASE_CONFIG}/downloade_config.json" "$USER_CONFIG/downloade_config.json"
fi
if [ ! -f "$USER_CONFIG/group_config.json" ]; then
  cp "${BASE_CONFIG}/group_config.json" "$USER_CONFIG/group_config.json"
fi
if [ ! -f "$USER_CONFIG/site_alias_config.json" ]; then
  cp "${BASE_CONFIG}/site_alias_config.json" "$USER_CONFIG/site_alias_config.json"
fi



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

#docker不走虚拟环境，非docker走虚拟环境
if [ "$_RUN_IN_DOCKER" == 'true' ]; then
  python3 "${WORKDIR}"/core/main.py "$filter_size" "$filter_count" "$filter_track" "$filter_path" "$filter_mult_seed_count"
else
  source "${WORKDIR}"/.venv/bin/activate
  python3 "${WORKDIR}"/core/main.py "$filter_size" "$filter_count" "$filter_track" "$filter_path" "$filter_mult_seed_count"
  deactivate
fi
