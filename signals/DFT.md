#### 离散时间傅里叶变换(DTFT)
设离散序列x(n)的采样周期是$T_s$， 那么$x(n)$ 可表示为$x(nTs)\delta(t-nTs)$，整个信号可看做采样而得的$x_s(t)$;求这个东西的傅里叶变换就是:

$$
\mathcal{F}[x_s(t)] = \int \sum x(nT_s)\delta(t-nTs)exp(-j\Omega t)dt = \\
\sum[ x(nT_s)\int\delta(t-nTs)exp(-j\Omega t)dt ]=\\
\sum [x(nT_s)exp(-j\Omega nT_s)] = \sum [x[n]exp(-jn\omega)] \\
\omega=\Omega T_s = \frac{\Omega}{f_s}
$$

在离散域时，一般把$\omega$ 叫做数字角频率，在不涉及到和模拟相关的转换时，一般把采样周期都认为是1，方便操作
前文说过，模拟信号的采样，对应于频域是信号的周期延拓，并且，我们通常认为原信号是带限的，否则因为出现混叠，我们做离散的变换分析也没有意义
观察 DTFT的表达式，可以发现：
1. DTFT一定是周期的，且$2\pi$一定是DTFT的周期（数字角频率计）
2. DTFT仍然是连续的
#### 离散傅里叶变换 （DFT）
DTFT得到的结果是在频率域上仍然是连续的，这个不能用于实际应用。但DTFT表明了 离散序列的频域基本情况。
一般，计算机中的序列长度都是有限的，假设某序列$x(n)$长度为N，时域描述为$x_s(t)$,采样间隔为$T_s$, 其DTFT为:

$$
x(j\omega) = \sum_{0}^{N-1}x(n)exp(-jn\omega)
$$

现在我们对其周期化，令周期为$NT_s$  则周期化的信号为：

$$
\widetilde{x_s}_N(t) =  x_s(t)*\sum\delta(t-nT_s)
$$

当站在离散域角度看上面这个公式，相当于对序列 x(n) 按照 N进行周期延拓。在连续时间域上，其傅里叶变换相当于两者变换的乘积，即:

$$
\mathcal{F}(\widetilde{x_s}_N(t)) = \mathcal{F}(x_s(t)) \mathcal{F}(\sum\delta(t-nT_N))] =\\
x(j\omega) [K\sum{\delta(w-nw_N)}] = \\
K\sum x(jnw_N)\delta(w-nw_N)  \quad （1）
$$ 

其中:

$$
T_N = NT_s \quad w_N = \frac{2\pi}{T_N}  T_s= \frac{2\pi}{N}
$$

即，序列周期化后，等价于在频域上对其采样，采样间隔是$\frac{2\pi}{N}$
前文说过，DTFT一定是周期化且$2\pi$一定是其周期, 考察(1)在$[-\pi, \pi]$区间内，刚好采了N个点，自此，我们可以引入DFT了.
因为$x(jw) = x(j(w+2\pi))$ 则:

$$
x(jnw_N) = x(jn\frac{2\pi}{N}) \\
x(j(n+N)(w_N)) = x(j(nw_N + Nw_N)) = x(j(nw_N + 2\pi)) = x(jnw_N)
$$

因此频域的序列也是以N为周期的，我们考虑（1）其在一个周期内的展开结果

$$
\sum_{k=0}^{N-1}{x(jkw_N)} \delta(w-kw_N) \\
x(jkw_N) = \sum_{n=0}^{N-1}{x(n)exp(-jnkw_N)} = \sum_{n=0}^{N-1}{x(n)exp(-jnk\frac{2\pi}{N})}
$$

忽略$\delta(w-kw_N)$, 我们把上式称作序列的DFT，正式定义如下：

$$
X[k] =\sum_{n=0}^{N-1}{x[n]exp(-jkn\frac{2\pi}{N}})
$$
