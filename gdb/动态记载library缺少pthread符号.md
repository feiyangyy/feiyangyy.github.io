#### 1. 问题现象
通过dlopen 动态加载的so，使用std::thread 创建线程，会crash。

加载该so的程序，如果链接了pthread, 即可解决该问题。

问题：

1. 即便是so链接了pthread, dlopen也不会为其加载pthread, 也就是说,dlopen时，加载哪些依赖库，是怎么确认的?
    * 问题也可能是，**pthread 加载了，但是其中的函数地址被可执行程序中的弱符号替代了。**

2. 为什么是crash，而不是报什么找不到符号或者别的问题：
    * 这是因为，libstdc++ 包含pthread 相关的weak符号，而so 中的代码很有可能调到了这些weak符号对应的函数

3. 附加问题：如果可执行程序A 和 B，都依赖动态库C，C中的库暴露了一个类的static 方法`Foo::SetUp(int x);` 假设A 设置的为`Foo::Setup(1)`, B 设置的是`Foo::Setup(2)`, 他们的设置会有冲突吗?
解答:
```
当多个可执行程序（如 A 和 B）都依赖于同一个动态库（如 C）时，它们共享该库的全局状态。
```

#### 2. 问题基本分析
dlopen的加载过程:

1. 动态段（Dynamic Section）
在 ELF 文件的动态段中，有一个名为 DT_NEEDED 的条目，它列出了该库所依赖的其他动态库。这些依赖库在库被加载时会被解析并加载。

2. 加载过程
```
当调用 dlopen 加载一个动态库时：

查找依赖：系统会检查该库的动态段，查找所有的 DT_NEEDED 条目，确定需要加载的其他库。

递归加载：如果所依赖的库也有其他依赖，系统会递归地加载这些库，直到所有依赖都被满足。
```
按照这个逻辑，pthread 应当是会被加载的，我们需要有方法确认pthread是否加载，如果被加载了，那么问题可能就是符号查找方面的

```
cat /proc/${PID}/maps 
```
以上命令可以查看哪些库被加载

测试代码参考testing_code
```C++
  std::string lib = "./libfoo.so";
  printf("Before \n");
  Pause();
  void *handler = dlopen(lib.c_str(), RTLD_NOW);
  // ...
  printf("After\n");
  Pause();
  return 0;
```
Before阶段没有加载pthread

查看dlopen 后（After阶段），程序加载的动态库:
```
7f7cac0ad000-7f7cac0b3000 r--p 00000000 00:00 381312             /usr/lib/x86_64-linux-gnu/libpthread-2.31.so
7f7cac0b3000-7f7cac0c4000 r-xp 00006000 00:00 381312             /usr/lib/x86_64-linux-gnu/libpthread-2.31.so
7f7cac0c4000-7f7cac0ca000 r--p 00017000 00:00 381312             /usr/lib/x86_64-linux-gnu/libpthread-2.31.so
7f7cac0ca000-7f7cac0cb000 r--p 0001c000 00:00 381312             /usr/lib/x86_64-linux-gnu/libpthread-2.31.so
7f7cac0cb000-7f7cac0cc000 rw-p 0001d000 00:00 381312             /usr/lib/x86_64-linux-gnu/libpthread-2.31.so
```
可见此时pthread 是加载了的

因此，dlopen 为我们的libfoo 加载了 pthread。那么问题就是符号匹配的问题了；也就是so中调用的pthread相关的函数为什么没有匹配到libpthread中的实现呢

#### 3. 动态库链接

通过readelf 解析程序的依赖 `readelf -s > foo.log`，
动态段输出信息:

dynsym 段，保存依赖符号信息
Bind  绑定属性，确认作用域和可见性:
1. LOCAL: 局部的，意味着外部不可访问
2. GLOBAL: 可被外部访问的，意思即可被寻址的
3. WEAK: 弱符号，允许其他同名的全局符号覆盖，如果没有则使用该WEAK的

Type
1. NOTYPE 没有信息
2. FUNC 函数
3. OBJECT 对象或者变量

Vis 可见性 == 和 Bind 不是重复？
DEFUALT 默认
HIDDEN 隐藏 外部不可访问
PROTECTED 保护，外部可访问，不可覆盖

NDX 符号?节区?索引 **节区即section, 直接记英文即可**
1. UND 未定义，通常由外部符号给定

NAME 符号名称

*不过g++11(not c++11) 似乎解决了pthread的连接问题*

#### 4. 符号重定位
将一个符号绑定到具体的地址的过程，称为重定位。 在重定位过程中，可能会有名称重复，此时就需要有一个优先级确认优先在哪里查找。

ld.so 使用了类似于C++中的名字空间的机制，也叫做namespace来管理加载的库，这个很有可能是为了避免符号污染。

当被加载的库需要查找一个符号时，他查找的顺序是：

1. 本地符号表，我得理解是foo.so 内部定义的符号
2. 全局符号表，全局符号表可以理解为是由可执行程序加载时生成的，要注意加载可执行文件的ld.so 和我们使用的动态加载的dl.so 不是一个东西，两者运作机制不同。
    * 全局符号表是在foo.so 启动之前就已经准备好了
3. 其他顺序

**这个需要通过debug验证，给出直接准确的证据**

这样，我们似乎就能理解为什么，pthread_create被解析成weak的符号了。但是这里还有一个问题: 既然weak符号承担了默认的实现的角色，那么为什么我们的程序调用了std::thread后，不链接pthread依然会报错呢?

#### 5. libstdc++的thread实现
std::thread 起线程的地方:
```C++
#ifdef GTHR_ACTIVE_PROXY
	// Create a reference to pthread_create, not just the gthr weak symbol.
  // 这个地方去找depend
	auto __depend = reinterpret_cast<void(*)()>(&pthread_create);
#else
	auto __depend = nullptr;
#endif
// 真的起线程
        _M_start_thread(_S_make_state(
	      __make_invoker(std::forward<_Callable>(__f),
			     std::forward<_Args>(__args)...)),
	    __depend);

```
可见此处，要产生pthread_create的依赖，需要定义GTHR_ACTIVE_PROXY， `std::thread` 是一个头文件，在引入这个头文件时，相关代码会作为foo.so 的一部分参与编译。那么 GTHR_ACTIVE_PROXY 这个宏是谁定义的呢? 我们的业务代码中有没有默认开启这个宏呢?

我们在library.cc中增加如下代码:
```
#ifdef GTHR_ACTIVE_PROXY
#pragma message(" GTHR_ACTIVE_PROXY is defined! This is a compile-time message.")
#endif
```
其被正常输出，意味着，我们正常定义了`GTHR_ACTIVE_PROXY`, 这个很有可能是thread 依赖的某些头文件引入的(`gthr_posix.h`)

引申问题：
1. weak 机制
2. so 的头文件中的内联函数，如果编译时配置不同而发生变化，会有什么问题

以下是一个阶段性的总结：
```
总结:
1. c++11的<thread> 的create implement是在thread.cc 中实现的，这意味着创建代码在libstdc++.so 中，创建代码需要使用与平台有关的api
2. gcc(g++ is a part of gcc)的预期：
    * 没有调用的thread的代码，不会产生对pthread的依赖，更重要的，不同配置的gcc的线程模型是不同的，依赖库也不同（即不一定是pthread)，如果不去除依赖，这会导致链接的深刻耦合
    * 调用了thread的代码，必须要链接到pthread
3. gcc 内部，通过弱符号机制来达到这个目的，以foo函数举例：
    * 通过一个包装的符号，如gcc_foo, 弱引用到foo
    * 声明foo 是一个弱符号，可以在链接时被强符号替代，弱符号默认是未定义的（可能也不是空指针）
    * g++的thread.cc 通过gcc_foo 包装后的函数，来创建线程，而不是直接使用平台api

通过弱符号，即便是业务代码没有链接pthread，thread.cc 相关的代码也不会产生链接报错。那么，g++ 又是如何完成2.2. 的呢? 答案是g++ 通过一个无用参数强制产生对pthread 的依赖，这部分实现是在<thread> 文件中，会被展开到业务代码里，让业务代码产生对pthread的依赖，注意不是libstdc++。

那么为什么dlopen 又会导致使用了std::thread的库crash呢? 这是因为符号加载顺序的问题，libdl 不是ld，他是glibc的一部分，他通过名字空间等机制支持符号的隔离等。名字空间一般有：local/global 以及其他（可能和加载顺序有关），dlopen 加载一个库时，其查找符号的顺序是：
1. LOCAL
2. GLOBAL
3. 其他

前面说过，因为gcc内部搞了一个弱符号，他是存在应用程序的符号表中的，应用程序的符号表对于dlopen的so而言是全局的。可以明确的是LOCAL肯定没有pthread相关符号，GLOBAL中有gcc定义的弱符号，dl认为找到了，但实际是错误的，从而导致了不能debug的crash
```
其实最后的结论并不正确，因为这是一个推论，并非从代码或者实践得出的结论。其实可以再思考一下，就能发现其中的问题：
1. libstdc++.so 在 业务代码中已经被加载一次了，符号也和业务代码符号合并了，dlopen 并不会再次重新加载libstdc++.so
2. 真正需要可用符号的时stdc++中创建线程的实现代码，而不是我们的so代码

所以这里的问题是：需要刷新 libstdc++.so 中的弱符号，而因为应用先加载了libstdc++.so了，dlopen 加载so时不会刷新其中的符号，同时so使用了stdc++中相关实现，进而导致了使用到了弱符号。

我们验证这个猜想很简单，我们编写一个C的应用来加载这个so，这样，libstdc++的符号就能在 dlopen时刷新了, 那么其就不会crash，详见测试代码main.c

在`After`阶段后，so中的线程正常被创建，一切OK

不过两者从表面来看推测都正确，但是结论完全不同。

进阶:
符号决议、Lazy binding.