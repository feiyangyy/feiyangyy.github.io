#include <stdio.h>
#include <stdint.h>
#include <vector>
#include <numeric>
#include <cmath>
#include <string>
#include <string.h>

#define _USE_MATH_DEFINES

struct Complex
{
  // 实部
  double a;
  // 虚部
  double b;
  Complex(double a, double b) : a(a), b(b) {}
  Complex(double a) : a(a), b(0) {}
  std::string ToString()
  {
    std::vector<char> buffer(64, 0);
    sprintf(buffer.data(), "(%.4lf + j%.4lf)", a, b);
    return buffer.data();
  }
};

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

using DisSequnce = std::vector<Complex>;

int main()
{
  DisSequnce values = {{1}, {2}, {3}};
  auto res = dft(values);
  std::string str_res;
  for (auto &r : res)
  {
    str_res += r.ToString() + " ";
  }
  printf("dft result:%s\n", str_res.c_str());
  return 0;
}