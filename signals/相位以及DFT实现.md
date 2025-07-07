#### 傅里叶变换的相位
在最开始的傅里叶级数中，我们把一个周期函数展开成一系列余弦函数的和，这些余弦函数包含三个部分：
1. 频率 余弦函数的频率
2. 幅度 余弦函数前的系数
3. 相位 余弦函数的开始位置

回忆整个傅里叶级数的展开过程，总结可以如下：
4.  因为余弦函数的相位，展开，得到了正弦项和余弦项
5.  实数域中，将相位产生的系数会被合并到余弦项系数$a_n$ 和正弦项系数$b_n$中
6. 通过欧拉公式，将傅里叶级数转换为频域的复数域的级数形式

几乎所有的信号与系统课程都会说：时域的时移等于频域的相移，那么频域的相移究竟是什么意思呢？调相因子$e^{-jnw_0t_0}$究竟产生了什么作用呢?
以傅里叶级数为例:
$$
A_ne^{-jnw_0t_0}= f_0\int_T f(t)exp(-jnw_0(t+t_0))dt \\
exp(-j(nw_0t - nw_0t_0)) = exp(-j(nw_0t-\phi)) \\
\phi = nw_0t_0
$$
因此，这个相移，**指的是分量信号在时域的相移**，周期信号在时域的移相，其实也是时移
另外，这个相移和频率有关，我们的傅里叶变换（级数）中的结果可以分为两部分看：
7. 幅度-频率特性: 在前述傅里叶级数中的$c_n$项的模
8. 相位-频率特性: 前述傅里叶级数中的$\phi$,  此处的相位，仍然值得是分量信号在时域的相位

#### DFT 的实现
DFT实现层面，需要对计算过程展开，并做一些合并:
$$
X(k) = \sum_{n=0}^{N-1}[x[n]e^{-j2\frac{\pi}{N}nk}] 
$$
令$Q=2\frac{\pi}{N}$, 设$x(n) = a_n + jb_n, X(k) = A_k + jB_k$, 则:
$$
x[n]e^{-j2\frac{\pi}{N}nk} = (a_n + jb_n)(cos(Qnk) -jsin(Qnk)) \\
= [a_ncos(Qnk) + b_nsin(Qnk)] + j[b_ncos(Qnk) - a_nsin(Qnk)] \\
X(k) = \sum\lbrace [a_ncos(Qnk) + b_nsin(Qnk)] + j[b_ncos(Qnk) - a_nsin(Qnk)] \rbrace = \\
\sum\lbrace [a_ncos(Qnk) + b_nsin(Qnk)] \rbrace + j\sum\lbrace [b_ncos(Qnk) - a_nsin(Qnk)]\rbrace = \\
A_k + jB_k
$$
因此
$$
A_k=\sum_{n=0}^{N-1}\lbrace [a_ncos(Qnk) + b_nsin(Qnk)] \rbrace \\
B_k = \sum_{n=0}^{N-1}\lbrace [b_ncos(Qnk) - a_nsin(Qnk)]\rbrace 
$$
参考C++实现:
```C++

// 离散傅里叶变换
std::vector<Complex> dft(const std::vector<Complex> &value)
{
  int N = value.size();
  double Q = M_PI / N;
  Complex def_value(0, 0);
  std::vector<Complex> result(N, {0, 0});
  for (int k = 0; k < N; ++k)
  {
    auto &cpl = result[k];
    for (int n = 0; n < N; ++n)
    {
      // 蝶形运算 呼之欲出!
      cpl.a += (value[n].a * cos(n * Q * k) + value[n].b * sin(n * Q * k));
      cpl.b += (value[n].b * cos(n * Q * k) - value[n].a * sin(n * Q * k));
    }
  }
  return result;
}
```
#### 使用DFT来分析实际序列
我们使用DFT和来分析实际序列[1,2,3]以及对应的IDFT，观察其特性 未完待续