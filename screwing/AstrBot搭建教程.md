# AStrBot 搭建流程

## 安装

1. 注册一个QQ号，最好是小号
2. 找一台服务器，可以是云服务器
3. clone napcat QQ的docker 仓库:
```bash
git clone https://github.com/NapNeko/NapCat-Docker.git
cd NapCat-Dokcer
mv compose/astrbot.yml compose.yml
NAPCAT_UID=$(id -u) NAPCAT_GID=$(id -g) docker-compose up -d
```

一切就绪后，进入napcat webui(http://<宿主机ip>:6099/webui), 做一些配置，默认登录Token napcat

## 配置napcat
1. 登录你的QQ小号，这个用手机扫一下即可

## 配置AstrBot
默认AstrBot和napcat 是部署在一台机器上的，访问AstrBot的webui 只是端口不同 （http://<宿主机ip>:6185）

webui 3.5.5 下:

选择 配置→消息平台→平台适配器→aiocqhttp(OneBotV11), 按照平台文档操作即可

## 接入DeepSeek
配置->服务提供商->新增服务提供商 按提示填写即可