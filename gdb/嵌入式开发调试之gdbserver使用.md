## 基本步骤
1. 首先要交叉编译目标平台的gdb-server, 比如arm的, 然后把他安装到系统中
2. gdb-server 是基于网络工作的，因此目标平台（板子）必须和调试机有网络连接，最好是直连
    * linux 下不知道为啥RNDIS网络驱动有问题（没有识别），因此建议试用windows的 WSL
3. 把host-gdb，(注意，如果是arm的，则应当是arm-linux-xxx-gdb 这种形式，如果没有，则自己编译一个，参考《正点原子》的教程即可) 放到调试机上
4. 先在板端启动gdbserver, 方法是 gdbserver [HOST_IP]:[端口] example
    * 这里的HOST_IP 是调试电脑的ip, 端口根据实际情况填写，后面电脑连接的时候要匹配
    * 这里的example是待调试的程序
5. 调试机（电脑）gdb example，这里的example与上含义相同，且一定要相同
6. target remote [board_ip]:[端口]，这里的board_ip 就是运行gdbserver的ip， 端口要和上面的端口一直
7. 然后c(continue) 运行即可