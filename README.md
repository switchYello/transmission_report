# transmission_report辅种情况分析脚本

----

> 2024-10-30 新建:  
1、脚本会调用transmission的接口，获取当前所有种子，按照文件名称大小进行分组，以表格形式展示    
2、从输出能够看出每个种子在每个站点的做种情况，可以辅助决策删种，执行脚本后在控制台中输出如下效果  

> 2024-10-31 更新：  
1、新增官种视图，已站点维度展示官种分布和辅种分布  
2、支持站点多track合并，类似麒麟这种存在两个track（hdkyl、hdkylin）合并成一个，统计时只统计一份  
3、明细试图中，会在站点后面标注这个文件在当前网站上是否是官种   
>

> 2024-11-01 更新：  
1、新增站点别名展示

> 2024-11-04 更新：  
1、支持 qbittorent了 🎉🎉🎉  
2、地址、账密配置提取到单独的配置文件中，不再通过参数传递  
3、增加过滤条: -p按照存储路径过滤 -f按照辅种数量过滤  
4、-t参数支持使用别名搜索  
4、明细展示美化  
 

>2024-11-15 更新：  
1、支持docker模式运行  
2、优化qb登陆问题  

>2024-12-10 更新：  
1、增加：咖啡、高清视界的别名

---- 

😀😀 想要使用docker方式运行可以看这个[docker方式使用](https://github.com/switchYello/transmission_report/blob/main/DOCKER%E6%96%B9%E5%BC%8F%E4%BD%BF%E7%94%A8.md)，推荐用docker 😀😀

😀😀 想要使用源码方式运行，可以继续向下看 😀😀

---- 


## 1、功能介绍
```shell
user@debian:/opt/transmission_report/src$ bash start.sh -utr -ptr -c10
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                  文件明细视图                                                                                                    │
├──────┬───────────────────────────────────────────────────────────────────────────────────────────────────────┬─────────────────────────┬──────────┬───────────┬────────────────────────────────────────────────┤
│ 序号 │                                                 文件名                                                  │         下载路径         │ 站点数量   │  文件大小   │ 站点名称(最后活跃时间)                            │
├──────┼───────────────────────────────────────────────────────────────────────────────────────────────────────┼─────────────────────────┼──────────┼───────────┼────────────────────────────────────────────────┤
│  1   │                          MKMP-581.2024.2160p.DMM.WEB-DL.AAC2.0.H.264-CTRL.mkv                         │   /downloads/complete   │    1     │  11.58 GB │ +------+------+---------------------+          │
│      │                                                                                                       │                         │          │           │ | 站点 | 官种 |       最后活跃      |            │
│      │                                                                                                       │                         │          │           │ +------+------+---------------------+          │
│      │                                                                                                       │                         │          │           │ | 馒头 |      | 2024-11-03 23:14:04 |           │
│      │                                                                                                       │                         │          │           │ +------+------+---------------------+          │
└──────┴───────────────────────────────────────────────────────────────────────────────────────────────────────┴─────────────────────────┴──────────┴───────────┴────────────────────────────────────────────────┘
│  2   │         剑网3·侠肝义胆沈剑心.第三季.jian.wang.xia.gan.yi.dan.shen.jian.xin.S03.2022.2160p.WEB-             │   /downloads/complete   │    1     │  11.19 GB │ +------+------+---------------------+          │
│      │                                        DL.H.265.AAC.2.0-FROGWeb                                       │                         │          │           │ | 站点 | 官种 |       最后活跃      |             │
│      │                                                                                                       │                         │          │           │ +------+------+---------------------+          │
│      │                                                                                                       │                         │          │           │ | 肉丝 |      | 2024-11-04 20:18:40 |           │
│      │                                                                                                       │                         │          │           │ +------+------+---------------------+          │
└──────┴───────────────────────────────────────────────────────────────────────────────────────────────────────┴─────────────────────────┴──────────┴───────────┴────────────────────────────────────────────────┘
│  3   │                           狂赌之渊 电影版.2019.1080p.日语.简繁中字￡CMCT陆判                                │   /downloads/complete   │    1     │  11.00 GB │ +------+------+---------------------+          │
│      │                                                                                                       │                         │          │           │ | 站点 | 官种 |       最后活跃      |             │
│      │                                                                                                       │                         │          │           │ +------+------+---------------------+          │
│      │                                                                                                       │                         │          │           │ | 肉丝 |      | 2024-11-04 21:03:24 |          │
│      │                                                                                                       │                         │          │           │ +------+------+---------------------+          │
└──────┴───────────────────────────────────────────────────────────────────────────────────────────────────────┴─────────────────────────┴──────────┴───────────┴────────────────────────────────────────────────┘
│  4   │                         START-203.2024.2160p.DMM.WEB-DL.AAC2.0.H.264-CTRL.mkv                         │   /downloads/complete   │    1     │  10.59 GB │ +------+------+---------------------+          │
│      │                                                                                                       │                         │          │           │ | 站点 | 官种 |       最后活跃      |             │
│      │                                                                                                       │                         │          │           │ +------+------+---------------------+          │
│      │                                                                                                       │                         │          │           │ | 馒头 |      | 2024-11-03 23:16:16 |          │
│      │                                                                                                       │                         │          │           │ +------+------+---------------------+          │
└──────┴───────────────────────────────────────────────────────────────────────────────────────────────────────┴─────────────────────────┴──────────┴───────────┴────────────────────────────────────────────────┘
│  5   │                         START-193.2024.2160p.DMM.WEB-DL.AAC2.0.H.264-CTRL.mkv                         │   /downloads/complete   │    1     │  10.53 GB │ +------+------+---------------------+          │
│      │                                                                                                       │                         │          │           │ | 站点 | 官种 |       最后活跃      |             │
│      │                                                                                                       │                         │          │           │ +------+------+---------------------+          │
│      │                                                                                                       │                         │          │           │ | 馒头 |      | 2024-11-04 21:03:15 |           │
│      │                                                                                                       │                         │          │           │ +------+------+---------------------+          │
└──────┴───────────────────────────────────────────────────────────────────────────────────────────────────────┴─────────────────────────┴──────────┴───────────┴────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                     辅种视图,去重种子总数:316 实际磁盘占用:821.13 GB                                           │
├──────┬──────────────┬────────┬──────────┬──────────┬────────────┬──────────┬────────────┬────────┬────────────┬──────────┤
│ 序号  │     站点      │ 官种数  │ 官种大小  │ 非官种数   │ 非官种大小  │ 做种总数   │ 做种总大小   │ 辅种数  │ 辅种总大小   │ 辅种比例  │
├──────┼──────────────┼────────┼──────────┼──────────┼────────────┼──────────┼────────────┼────────┼────────────┼──────────┤
│  1   │    m-team    │   8    │ 26.13 GB │    96    │ 501.59 GB  │   104    │ 527.72 GB  │   77   │ 405.23 GB  │  76.79%  │
└──────┴──────────────┴────────┴──────────┴──────────┴────────────┴──────────┴────────────┴────────┴────────────┴──────────┘
│  2   │    hdkyl     │   10   │ 91.01 GB │   119    │ 376.89 GB  │   129    │ 467.90 GB  │   81   │ 381.05 GB  │  81.44%  │
└──────┴──────────────┴────────┴──────────┴──────────┴────────────┴──────────┴────────────┴────────┴────────────┴──────────┘
│  3   │   cyanbug    │   0    │  0.00 B  │   104    │ 269.55 GB  │   104    │ 269.55 GB  │   68   │ 267.40 GB  │  99.20%  │
└──────┴──────────────┴────────┴──────────┴──────────┴────────────┴──────────┴────────────┴────────┴────────────┴──────────┘
│  4   │    kufei     │   0    │  0.00 B  │    30    │ 100.39 GB  │    30    │ 100.39 GB  │   1    │  8.18 GB   │  8.15%   │
└──────┴──────────────┴────────┴──────────┴──────────┴────────────┴──────────┴────────────┴────────┴────────────┴──────────┘
│  5   │  dns-verify  │   0    │  0.00 B  │    49    │  31.22 GB  │    49    │  31.22 GB  │   0    │   0.00 B   │  0.00%   │
└──────┴──────────────┴────────┴──────────┴──────────┴────────────┴──────────┴────────────┴────────┴────────────┴──────────┘
│  6   │ ilovelemonhd │   3    │ 23.96 GB │    12    │  4.17 GB   │    15    │  28.13 GB  │   0    │   0.00 B   │  0.00%   │
└──────┴──────────────┴────────┴──────────┴──────────┴────────────┴──────────┴────────────┴────────┴────────────┴──────────┘
│  7   │   connects   │   0    │  0.00 B  │    7     │  21.47 GB  │    7     │  21.47 GB  │   0    │   0.00 B   │  0.00%   │
└──────┴──────────────┴────────┴──────────┴──────────┴────────────┴──────────┴────────────┴────────┴────────────┴──────────┘


```



## 2、安装
> **脚本需要python环境，依赖python的venv组件，如果安装时缺少相关依赖请自行安装好。**

1. 将本项目从github下载到服务器上,放在某个文件夹下
```shell
git clone https://github.com/switchYello/transmission_report.git
```

2. 执行如下命令初始化python venv环境
```shell
#进入src目录
cd src
#创建venv环，此时会创建一个隐藏文件夹.venv
python3 -m venv .venv
#激活venv环境
source .venv/bin/activate
#venv环境下安装必要的组件
python3 -m pip install -r requirements.txt
#退出虚拟环境
deactivate
#加执行权限
chmod u+x start.sh
```

3. 如果后续有更新的话使用git重新拉代码
```shell
git pull -f https://github.com/switchYello/transmission_report.git
```


## 3、使用
修改`config`目录下的`downloade_config.json`配置文件，  
使用时进入到脚本所在的文件夹下，直接执行 `bash start.sh` 即可使用默认参数运行一次，控制台可输出上述报表。

参数：
```text
-m 小于该大小的种子不显示,单位为MB 默认0全部展示
-c 列表展示前多少个种子 默认500
-t 想要搜索的trade或别名，比如只看包含馒头的可以添加参数 -t team，就会过滤出包含馒头的种子 （模糊搜索）
-p 按照存储路径过滤 （模糊搜索）
-f 按照辅种站点数量过滤 （精确搜索）
-? 输出帮助信息
```


示例:  
```text
1、搜索馒头的辅种情况，即track中包含team字符的
bash start.sh -t team

2、展示大于500MB的，从大到小排序的前50个种子
bash start.sh -m500 -c 50

3、搜索大青虫前100个种子
bash start.sh -c 100 -t bug 

4、筛选指定路径下的种子
bash start.sh -p downloads/complete 

5、搜索downloads/complete路径小，辅种数量只有1个的种子
bash start.sh -p downloads/complete -f 1 

```
如果参数和默认值一样可以省略不写，可通过定义alias将参数写好，这样就不用每次输入路径和账号密码了


## 4、配置文件：
- 下载器配置`downloade_config.json`
支持qb和tr，需要配置好路径账号密码，路径中不要填写接口path。

```json 
[
  {
    "name": "qb下载器",
    "type": "qbittorent",
    "url": "http://192.168.1.8:6882",
    "username": "admin",
    "password": "adminadmin"
  },
  {
    "name": "tr下载器",
    "type": "transmission",
    "url": "http://192.168.1.8:9091",
    "username": "tr",
    "password": "tr"
  }
]
```

- 别名配置`site_alias_config.json`
根据track的域名映射成其他可识别的名称，不配置默认展示域名
```json
{
  "agsvpt.trackers.work": "末日种子库",
  "m-team.cc": "馒头",
  "hdkylin.top": "麒麟",
  "cyanbug.net": "大青虫",
  "ilovelemonhd.me": "柠檬",
  "dns-verify.top": "lusthive(9KG)",
  "connects.icu": "fsm(9KG)",
  "nextpt.net": "fsm(9KG)",
  "kufei.org": "库非",
  "hdpt.xyz": "明教",
  "rousi.zip": "肉丝"
}

```

- 官组配置 `group_config.json`
筛选站点track，并使用正则匹配种子名称，符合正则的会标记为官组。
```json
[
  {
    "--": "此配置文件修改自油猴脚本【官种保种统计】并加以改动适配python",
    "host": "audiences.me",
    "abbrev": "Audiences",
    "siteRegex": "[@-]\\s?(Audies|ADE|ADWeb|ADAudio|ADeBook|ADMusic)"
  },
  {
    "host": "hdsky.me",
    "abbrev": "SKY",
    "siteRegex": "[@-]\\s?(HDS)\\b"
  },
  {
    "host": "pterclub.com",
    "abbrev": "PTer",
    "siteRegex": "[@-]\\s?(PTer)\\b"
  },
```




## 5、卸载
因为使用的venv环境，直接将git对应的文件夹全部删除即可。  



## 6、小技巧，使用别名配置默认值
```text
在用户目录下的隐藏文件.baserc文件中增加如下行（参数和路径自行修改）
cd ~
vi .bashrc
alias reporttr='bash /path_to_source/src/start.sh -utr -ptr -c200'
保存后执行 `source .baserc`或者退出ssh重新连接


上面的意思是为引号内的这行脚本定义一个别名，并且会在启动时初始化到环境变量里。
后面无论在哪个目录下，像下面这样直接执行`reporttr`都能调用脚本了,而且可以添加参数覆盖别名中的参数
user@debian:/opt/docker$ reporttr  -c 50
```

