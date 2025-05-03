#import "base.typ": conf
#show: doc => conf(
  title: [
    Towards Improved Modelling
  ],
  authors: (
    (
      name: "Theresa Tungsten",
      affiliation: "Artos Institute",
      email: "tung@artos.edu",
    ),
    (
      name: "Eugene Deklan",
      affiliation: "Honduras State",
      email: "e.deklan@hstate.hn",
    ),
  ),
  abstract: lorem(80),
  doc,
)

= 基本概念
#let omg =$omega$
#let o0 = $omg_0$
#let pn = $phi_n$
== 傅里叶级数
傅里叶变换是将信号放在复数域中做变换（从实信号扩展到复数域，在复数域下，仍然那是纯实的），分析其特性。
1. 实数域 周期信号的傅里叶级数:
满足一定条件的周期函数，可以展开成傅里叶级数，某周期函数$f(t)$ 的频率为$f_0$，则其角频率为:$omg_0 = 2 pi f_0$. 其可以展开成傅里叶级数:
$
  f(t) = c_0 + sum_(n=1)^(inf) c_n cos(n o0 t + pn)
$
经过适当变换可得:
$
  f(t) = c_0 + sum_(n=1)^(inf)[a_n cos(n o0 t) + b_n sin(n o0 t)];\
  a_n = c_n cos(phi_n), b_n = -c_n sin(phi_n); \
  a_n = 2/T integral_(-T/2)^(T/2) f(t) cos(n o0 t) d t; b_n = 2/T integral_(-T/2)^(T/2) f(t) sin(n o0 t) d t; \
  c_n = sqrt(a_n ^2 + b_n^2); phi_n = arctan(-b_n/a_n)
$<a1>

@a1 表示一个实周期信号可以由无穷多个正弦信号和余弦信号表示，这些正弦信号或余弦信号的频率是 $2 pi f$ 的整数倍 $2 pi f$ 也称作角频率。角频率源自$sin(o0 t)$的频率为:$f = 2pi / o0$

@a1 同时也表达了傅里叶系列变换的基本性质:
1. 幅度: $c_n$ 对应于$n o0 或 n f$下的基信号幅度， 幅度也代表了该频率分量的能量。 注意这个能量是不能从变换结果立刻得出的。
2. 相位: $phi_n$ 对应于 $n o0$ 下的基信号的相位

== 复数域的傅里叶级数
如果将信号$f(t)$ 表为复数域内的纯实信号，利用欧拉公式，可将正弦、余弦展开:
$
cos(n o0 t) = (e^(i n o0 t) + e^(-n o0 t))/2; sin(n o0 t) = (e^(i n o0 t) - e^(-n o0 t)) / 2
$
前述傅里叶级数可以表为：
$
f(t) = sum_(n=-infinity)^(infinity) [(a_n - j b_n)/2 e^(j n o0 t)];
A_n = (a_n - j b_n)/2 = 1/T_0 integral_(-T/2)^(T/2) [f(t) e^(-j n o0 t)] d t;\
f(t) = sum_(n = -infinity)^(infinity) {1/T integral_(-1/T)^(1/T)[f(t) e^(-j n o0 t)] d t}
$<a2>

== 非周期实信号的傅里叶变换
#let bo = $Omega$
非周期实信号的$T -> infinity$, $o0 -> 0$, $n o0 -> bo$
@a2 可表为:
$
f(t) &= lim_(T->infinity){sum_(n = -infinity)^(infinity) {1/T integral_(-1/T)^(1/T)[f(t) e^(-j n o0 t)] d t}} \
&= lim_(T->infinity) {sum_(n=-infinity)^(infinity){o0/(2 pi) integral_(-1/T)^(1/T)[f(t) e^(-j n o0 t)] d t}} \
&= integral_(-infinity)^(infinity) 1/(2 pi) integral_(-infinity)^(infinity) [f(t) e^(-j bo t)] d t d bo \
&= 1/(2 pi) integral_(-infinity)^(infinity) integral_(-infinity)^(infinity) [f(t) e^(-j bo t)] d t d bo
$

== 离散时间傅里叶变换(DTFT)
对实连续信号使用$sum_(-infinity)^(infinity) delta(t -n T_s)$ 冲击串采样可以得到离散信号($T_s$是采样周期）。 对得到的采样信号进行傅里叶变换得到的结果即离散时间傅里叶变换:
$
f_s(t) = sum x_(n T_s)  delta(t - n T_s) \
F(f_s(t)) = 1/(2 pi) integral_(-infinity)^(infinity) {sum x_(n T_s) delta(t - n T_s) exp(-j bo t)}d t = 1/(2 pi) sum_(-infinity)^(infinity) x_(n T_s) exp(-j bo n T_s)
$<a3>
@a3 的DTFT 仍然是频域连续的，不利于计算机分析。 并且实际应用中也没有无限长的信号的序列

DTFT 有一个性质（实际上由奈奎斯特采样定理给出）:

== 离散傅里叶变换
$
  X(k) = sum_(n=0) ^(N-1) x(n) e^(-j 2pi/N k n) = sum [x(n)(cos(2pi/N k n) - j sin(2pi/N k n))]
$
DFT 的结果包含实部、虚部，表示起来更为复杂； 但是，此结果即有能量信息，也有相位信息


== 离散余弦变换:
#let ep = $epsilon$
第二类离散余弦变换：
$
  X(k) = sqrt(2/N) ep_k sum_(n=0)^(N-1) x_n cos[(k(2n + 1) pi)/2N] ;\
  ep_k = cases(1/sqrt(2) \, k = 0, 1 )
$
以序列[0,1] 带入一下:
$
  X(0) = 1 dot 1/sqrt(2) {x(0) cos(0) + x(1) cos(0) } = 1/sqrt(2)(x_0 + x_1); \
  X(1) = 1 dot 1 {[x_0 cos[(1 dot (1) pi)/2 dot 2]] + [x_1 cos[(1 dot (2 + 3) pi)/ 2 dot 2]]} = x_0 cos(pi) + x_1 cos(5 pi)
  
$

 