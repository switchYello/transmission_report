
# docker方式使用

很多小伙伴玩nas都是使用docker的，用起来干净不会污染系统环境。  
虽然这个只是一个python脚本并且使用了虚拟环境并不会污染系统环境。  
使用docker也免去了搭建环境的困扰，所以就按照下面步骤来操作吧。  


## 使用步骤
请准备一个目录用于存放配置文件，比如我放在了 `/opt/docker/transmission_report` 目录下。  

### 🚩 1.下载镜像
```shell
docker pull docker1062/transmission_report
```

### 🚩 2.第一次运行
```shell
# 在某个位置新建一个配置文件夹
mkdir /opt/docker/transmission_report/config

# 执行命令，其中--user=1000:1000为你的用户，不指定就是默认的root用户
docker run --rm --user=1000:1000 -v /opt/docker/transmission_report/config:/src/config --net=host docker1062/transmission_report
```
解释一下这行命令,他是用docker执行上面拉到的镜像，而镜像启动后输出报表然后自动退出。    
--rm 参数表示执行终止后自动清理掉容器  
-v   参数绑定参数路径到容器内部的固定位置  
--net=host 表示使用host模式启动，方便我们使用127.0.0.1访问其他容器  
--user=1000:1000 表示使用哪个用户身份执行  
docker1062/transmission_report 是镜像的名称  



命令执行完成后会在`/opt/docker/transmission_report/config`目录下初始化三份配置文件。
请注意config文件夹的权限，还有确保--user指定的用户能够读写这三份配置文件。  

```shell
root@vm:/opt/docker/transmission_report# ll config/
-rw-r--r-- 1 root root  161 Nov 14 18:54 downloade_config.json   #配置下载器的配置文件，支持qb和tr
-rw-r--r-- 1 root root 3128 Nov 14 18:48 group_config.json       #配置官组的配置文件
-rw-r--r-- 1 root root  329 Nov 14 18:48 site_alias_config.json  #配置站点别名的配置文件
```

👉️👉️👉️  **我们需要修改`downloade_confi.json`为我们系统自己的，默认的地址和账号密码不符合你的设定。**

### 🚩 3. 后续使用
下载器的配置修改好后就可以正常使用了。**添加不同参数输出报表，不添加任何参数时输出帮助信息。**
* -m 小于该大小的种子不显示,单位为MB 默认0
* -c 展示前多少个种子 500
* -t 按照track名称或别名过滤,模糊搜索
* -p 按照存储路径过滤
* -f 按照辅种站点数量过滤
```shell
# 输出前100个
docker run --rm --user=1000:1000 -v /opt/docker/transmission_report/config:/src/config --net=host docker1062/transmission_report -c100

#筛选downloads路径下前100个
docker run --rm --user=1000:1000 -v /opt/docker/transmission_report/config:/src/config --net=host docker1062/transmission_report -c100 -p downloads

#筛选辅种数为1的
docker run --rm --user=1000:1000 -v /opt/docker/transmission_report/config:/src/config --net=host docker1062/transmission_report -f1
```


###  🚩 4. 配置详解
`downloade_config.json`
* name 用于展示，名称随意
* type 支持qbittorent、transmission
* url 以http开头，端口号结尾，不需要写路径，末尾不需要斜杠
* username、password按照实际填写
```json
[
  {
    "name": "qb下载器",
    "type": "qbittorent",
    "url": "http://127.0.0.1:6882",
    "username": "admin",
    "password": "adminadmin"
  },
  {
    "name": "tr下载器",
    "type": "transmission",
    "url": "http://127.0.0:9091",
    "username": "tr",
    "password": "tr"
  }
]
```

`site_alias_config.json` 配置里是站点的别名，根据track地址映射成中文，可自行添加。也可提pr给我。
```json
{
  "agsvpt.trackers.work": "末日种子库",
  "m-team.cc": "馒头",
  "hdkylin.top": "麒麟"
}
```


`group_config.json` 配置种子官组信息，用于识别一个种子在对应站点是不是官种。从油猴脚本中需改而来。
```json
[
  {
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
  }
]
```


### 🚩 命令别名配置
上面的命令很长，难以记住因此配置一个alias方便我们使用
```shell
cd ~
vi .bashrc
# 在最后面添加这行
alias report_tr="docker run --rm --user=1000:1000 -v /opt/docker/transmission_report/config:/src/config --net=host docker1062/transmission_report"
source .bashrc  #使之生效
report_tr -c10 # 已经可以使用report_tr代替了后面一大串命令
```

### 🚩 镜像更新
重新执行 `docker pull docker1062/transmission_report` 即可重新拉取最新镜像，下次运行即是最新的


