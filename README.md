# transmission_report

## transmission辅种情况分析脚本

脚本会调用transmission的接口，获取当前所有种子，按照文件名称大小进行分组，以表格形式展示。  
从输出能够看出每个种子在每个站点的做种情况，可以辅助我们决策删种，执行脚本后在控制台中输出如下效果。

```shell
user@debian:/opt/script/tr$ bash start.sh
┌───────┬───────────────────────────────────────────────────────────────────────────────────┬────────────┬───────────┬───────────────────────────────┐
│ index │                                        name                                       │ trackCount │ size      │                        tracks │
├───────┼───────────────────────────────────────────────────────────────────────────────────┼────────────┼───────────┼───────────────────────────────┤
│ 0     │          脱口秀大会.Rock.&.Roast.S06.2024.2160p.WEB-DL.H265.DDP2.0-ADWeb          │ 2          │ 56.23 GB  │         tracker.m-team.cc:443 │
│       │                                                                                   │            │           │           www.hdkylin.top:443 │
└───────┴───────────────────────────────────────────────────────────────────────────────────┴────────────┴───────────┴───────────────────────────────┘
│ 1     │           边水往事.Escape.from.the.Trilateral.Slopes.S01.2024.1080p.WEB-          │ 3          │ 48.82 GB  │          tracker.hdkyl.in:443 │
│       │                          DL.HEVC.10bit.HDR.AAC.2.0-HDKWeb                         │            │           │         tracker.m-team.cc:443 │
│       │                                                                                   │            │           │           www.hdkylin.top:443 │
└───────┴───────────────────────────────────────────────────────────────────────────────────┴────────────┴───────────┴───────────────────────────────┘
│ 2     │       异形前传：普罗米修斯 Prometheus 2012 UHD Blu-ray 2160p HDR HEVC DTS-HD      │ 4          │ 47.62 GB  │       tracker.cyanbug.net:443 │
│       │                                 MA 7.1-Pete@HDSky                                 │            │           │          tracker.hdkyl.in:443 │
│       │                                                                                   │            │           │         tracker.m-team.cc:443 │
│       │                                                                                   │            │           │           www.hdkylin.top:443 │
└───────┴───────────────────────────────────────────────────────────────────────────────────┴────────────┴───────────┴───────────────────────────────┘
│ 3     │                    American.Horror.Story.S01.2011.Disney+.WEB-                    │ 2          │ 31.95 GB  │       tracker.cyanbug.net:443 │
│       │                              DL.1080p.H264.DDP-HDCTV                              │            │           │         tracker.m-team.cc:443 │
└───────┴───────────────────────────────────────────────────────────────────────────────────┴────────────┴───────────┴───────────────────────────────┘
│ 4     │            Gambling.Apocalypse.Kaiji.S02.2011.1080p.BluRay.x265.10bit.F           │ 2          │ 29.68 GB  │       tracker.cyanbug.net:443 │
│       │                                    LAC.2.0-ADE                                    │            │           │           www.hdkylin.top:443 │
└───────┴───────────────────────────────────────────────────────────────────────────────────┴────────────┴───────────┴───────────────────────────────┘
│ 5     │            Gambling.Apocalypse.Kaiji.S01.2007.1080p.BluRay.x265.10bit.F           │ 2          │ 27.07 GB  │       tracker.cyanbug.net:443 │
│       │                                    LAC.2.0-ADE                                    │            │           │           www.hdkylin.top:443 │
└───────┴───────────────────────────────────────────────────────────────────────────────────┴────────────┴───────────┴───────────────────────────────┘
│ 6     │            胆小鬼.Nobody.Knows.S01.2022.1080p.NowPlay.WEB-DL.H264.AAC-            │ 4          │ 26.83 GB  │       tracker.cyanbug.net:443 │
│       │                                       HHWEB                                       │            │           │          tracker.hdkyl.in:443 │
│       │                                                                                   │            │           │         tracker.m-team.cc:443 │
│       │                                                                                   │            │           │           www.hdkylin.top:443 │
└───────┴───────────────────────────────────────────────────────────────────────────────────┴────────────┴───────────┴───────────────────────────────┘
│ 7     │          火星救援.The.Martian.2015.BluRay.2160p.x265.10bit.HDR.4Audio.mUH         │ 1          │ 24.96 GB  │                 kufei.org:443 │

```

## 安装

> 需要python环境，依赖python的venv组件，如果安装时缺少相关依赖请自行安装好。使用venv进行环境隔离可以防止不同项目间相互影响。

1. 将本项目从github下载到服务器上,放在某个文件夹下
2. 初次安装执行如下命令

```shell
#进入src目录
cd src
#创建venv环，此时会创建一个隐藏文件夹.venv
python3 -m venv .venv
#激活venv环境
source .venv/bin/activate
#venv环境下安装必要的组件
python3 -m pip install -r requirements.txt
```

3. 安装成功后可将`requirements.txt`文件删除，保留`start.sh`,`main.py`以及隐藏的`.venv`文件夹就可以了

## 使用

使用时进入到脚本所在的文件夹下，直接执行 `bash start.sh` 即可运行一次，控制台可输出上述报表。  
也可将脚本配置在环境变量里，或者创建软连接到你常用的文件夹下方便后续使用。

参数：
全部可指定参数有如下,可以修改start.sh脚本将默认值改掉这样后续就不用输入参数了.
> bash start.sh -h http://127.0.0.1:9091 -u tr -p tr -m 500 -c 10

```text
-h 指定tr地址,需要带前面的http，默认http://127.0.0.1:9091
-u 指定用户名 默认空字符串
-p 指定密码 默认空字符串
-m 小于该大小的种子不显示,单位为MB 默认0全部展示
-c 列表展示前多少个种子 默认2000,种子太多的话一页看不过来
```

## 卸载
因为使用的venv环境，直接将脚本对应的文件夹全部删除即可。
