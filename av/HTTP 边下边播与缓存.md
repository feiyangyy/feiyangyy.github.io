## 什么是边下边播
边下边播是指：一边下载、一边播放; 用过QVOD的朋友应该都知道...

这里的下载是指存储到缓存文件中，最终此缓存文件是否持久化具体取决于业务设计。 比如，某些无盘系统做VOD，cache可能是在内存中做的，那么就没有持久化的必要。而像QVOD那种，就很有必要性了。

我们可以简单搭建一个http文件服务器来模拟这个边下边播的事情，同时了解下不同播放器的行为

## 搭建服务器
这里我们用nginx来搭建一个简单的http文件服务器，具体步骤如下：
1. 安装nginx
```bash
sudo apt-get install nginx
```
2. 配置nginx
```bash
sudo vim /etc/nginx/sites-available/default
```
在server块中添加以下内容, 注意这里要配置支持获取文件的chunk：
```nginx
location / {
                root /some/path;
                autoindex on;
                autoindex_exact_size off;
                autoindex_localtime on;
                charset utf-8;
                add_header Accept-Ranges bytes;
                add_header Access-Control-Allow-Origin *;
                sendfile on;
                tcp_nopush on;
                tcp_nodelay on;
}
```
3. 重启nginx
```bash
sudo nginx -t
sudo service nginx restart
```

将视频文件拷贝到/some/path 下，通过浏览器访问`ip/` 即可看到文件列表了，选择对应的文件即可下载

## 验证ffplay的播放行为

## 验证vlc的播放行为

## 使用HTTP代理+cache服务，优化ffplay 播放

我该如何在linux上搭建http proxy + cache  结合ffplay 验证边下边播的方案?
