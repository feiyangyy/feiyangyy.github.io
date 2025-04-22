## 基础知识
### HLS
HLS 全称 Http Live Stream, 是苹果公司开发的一种**流协议**，其通过把音视频文件切分成mpeg-ts(ts) 文件，并且生成一个播放列表文件(mu38),让客户端下载这些小文件，并实现播放

其复用了HTTP协议的基础设施（如防护墙、CDN内容分发）

### TS
TS  全称Transport stream, 是mpeg-2 的一种**封装格式**，其特征是包大小固定位188B，支持多路复用

### RTSP 
RTSP 全称实时传输流协议 (Real time streaming protocol) ，是一种实时流传输控制协议，用于建立对象之间的媒体传输对话，适合低延迟场景

## HLS 详解

工作原理：
1. 内容切割： HLS需现将文件切分成多个小片段，并封装为TS格式，片段时长一般6-10S
2. 列表指引: 提供MU38列表文件，作为播放列表， 播放列表内包含各个文件的顺序和URL，客户端需先请求这个mu38文件，然后依次解析、播放

### 优点
1. 复用HTTP基础设施
### 缺点
1. 启动延迟高，原因是先要对文件或者流做切分

### TS 解析
一个视频容器通常包含三种流：
1. 视频流
2. 音频流
3. 字幕流

TS(Transport stream) 是为了应对传输较差的情况设计的，TS上述三种以及额外的信息合成**一个流**

### TS 包结构
TS 采用**固定包**大小(188B)

1. 包分解字节，包的第一个字节 0x47 **固定值**，用于区分边界
2. **PID**，13b, 用于区分子流，区分是**Video,Audio,Subtitle** 以及其他流等
3. **自适应字段控制**：指示有没有自适应控制字段，以及有无有效载荷（数据）
4. **自适应字段**: 关键是可能会包含一个**PCR （Program Lock reference）** **OPCR (Original Program ...)**
    * **PCR （Program Lock reference）**: 提供一个高精度时钟基准，用于音视频同步
4. **连续计数器**:4b, 用于检测是否丢包，正常不丢报的流，这个计数器是1-16 循环变化，如果发生了不连续，说明存在丢包
4. **TEI**: 传输错误标志位，一旦此bit=1, 说明存在传输错误，客户端可以根据此丢包
5. 载荷(Payload): 实际数据
    * 如果数据，会用stuffing 字节补充，以控制包长度固定
  


TS流就是由连续多个的TS包组成，因此站在全局看，一个TS流，就是完成了 AVS 等多路流的合并

因此，整体上看,TS只负责错误检测，检测方法有两种：一个是连续计数器的连续性检测，还有一个是TEI标志位。错误处理要靠传输协议或者业务层面处理，如解码器的错误隐蔽或者协议上的重传等


### 直播场景下，HLS如何与TS配合运作
1. 采集端做encode，并不断生成小文件（即小的TS流）
2. 采集端将编码好的文件推送到CDN服务器上
3. CDN 服务器生成mu38 列表文件，并进行分发（这里mu38 也可能是源服务器生成的）
4. 客户端拉去mu38，并不断解析、播放

这里的**mu38**会定期刷新，移除已播放片段，添加新片段

采集端生成小文件就会引入初级延迟，源服务器刷新mu38会引入二级延迟，因此HLS整体会有一定的延迟，近些年有新协议LHLS （低延迟HLS），以改进延迟问题。

### 点播场景下，HLS如何运作?
理解点播和直播的重要区别之一是，**点播可以做seek，快进快退，而直播不可以**

点播场景下，文件通常是录制好的。进行点播时:
1. 服务器将文件切分成多个小片段，并生成mu38文件
2. 客户端请求mu38, 并拉取这些小文件
3. 完成播放

Q: 是否可以像直播那样，对于以及播放的片段，动态的将其删除，并添加新的片段，这样可以减轻存储压力?

直播采用的是类似于TCP sliding window 那样的机制，保留一段时间内的视频切片。客户端可以请求的最早的视频片段由窗口决定。窗口的移动和客户端的播放进度是无关的，**而是和采集端推送进度有关**， 属于业务层面的事情

点播也是如此，业务层面可以维持一个窗口，并且在seek时，动态刷新这个窗口从而达到类似目的，这仍然属于业务层面的事情

### Let's do sth fun.
1. How to generate a HLS stream with ffmpeg?
```bash
ffmpeg -i foo.mp4 -codec:copy -start_number 0 -hls_time 5 -hls_list_size 0 -f hls stream.m3u8
```
1. `start_number`:  it controls the way of generating HLS-sengments, like: `seg0.ts, seg1.ts ...`
2. `-f hls ` output format is HSL
3. `hls_time 5`: the duration of each ts file 5 sec
4. `hsl_list_size 0`: no sliding window.

after the operation, we can see the outputs:
```
├── streams0.ts
├── streams10.ts
├── streams11.ts
├── streams12.ts
├── streams13.ts
├── streams14.ts
├── streams15.ts
├── streams16.ts
├── streams17.ts
├── streams18.ts
├── streams19.ts
├── streams1.ts
├── streams20.ts
├── streams21.ts
├── streams22.ts
├── streams23.ts
├── streams24.ts
├── streams25.ts
├── streams26.ts
├── streams27.ts
├── streams28.ts
├── streams2.ts
├── streams3.ts
├── streams4.ts
├── streams5.ts
├── streams6.ts
├── streams7.ts
├── streams8.ts
├── streams9.ts
```


### 查看ts的二进制文件:
```bash
head -c 188 streams1.ts | hexdump -C
```
*文件尾部自然想到tail, 文件头部自然想到head*

结果:
```
00000000  47 40 11 11 00 42 f0 25  00 01 c1 00 00 ff 01 ff  |G@...B.%........|
00000010  00 01 fc 80 14 48 12 01  06 46 46 6d 70 65 67 09  |.....H...FFmpeg.|
00000020  53 65 72 76 69 63 65 30  31 77 7c 43 ca ff ff ff  |Service01w|C....|
00000030  ff ff ff ff ff ff ff ff  ff ff ff ff ff ff ff ff  |................|
*
000000bc
```
可以看到，包开头是0x47, 尾部用stuffing 字节填充,这个包可能是没有数据的

### 查看m3u8文件
```
vim `ls | grep m3`
```
内容如下:
```
#EXTM3U <---------- 文件头部 
#EXT-X-VERSION:3 <---版本号--->
#EXT-X-TARGETDURATION:8 <---TS片段的最大持续时间-->
#EXT-X-MEDIA-SEQUENCE:0 <---当前列表中，第一个切片的序号--->
#EXTINF:8.341667, <--下一个分辨的持续时间，这里第一个持续8.34 sec--->
streams0.ts
#EXTINF:4.170833,
streams1.ts
#EXTINF:4.170833,
streams2.ts
#EXTINF:4.170833,
streams3.ts
...
streams25.ts
#EXTINF:4.170833,
streams26.ts
#EXTINF:3.370033,
streams27.ts
#EXTINF:2.653533,
streams28.ts
#EXT-X-ENDLIST <----- 文件尾部
```

### 使用ffplay 测试播放
```bash
ffplay -i `ls | grep m3`
```
可见ffplay 再动态的打开ts文件
![avatar](pics/hls.png)

### 使用ffmpeg + 滑动窗口，模拟推直播流
```
ffmpeg -i input.mp4 \
    -c:v libx264 -c:a aac \
    -f hls -hls_time 4 -hls_list_size 6 \
    -hls_flags delete_segments+append_list \
    output.m3u8
```
这个输出的太快了，不好确认这个m3u8文件的变化情况, 不过在分割结束时，我们能看到文件中只有部分TS文件