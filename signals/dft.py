#coding:utf-8
import numpy as np

def dft(signal):
    N = len(signal)
    n = np.arange(N)
    k = n.reshape((N, 1))
    e = np.exp(-2j * np.pi * k * n / N)
    return np.dot(e, signal)

def idft(spectrum):
    N = len(spectrum)
    n = np.arange(N)
    k = n.reshape((N, 1))
    e = np.exp(2j * np.pi * k * n / N)
    return np.dot(e, spectrum) / N

# 输入信号
x = np.array([1, 2, 3, 4, 5])

# 计算DFT
X = dft(x)
print("DFT结果：", X)

# 计算IDFT
reconstructed_x = idft(X)
print("IDFT结果：", reconstructed_x)