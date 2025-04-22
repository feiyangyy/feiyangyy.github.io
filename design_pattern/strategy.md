## 概述
前面说过，设计模式的核心是变与不变，我们可以给一个更为精炼详实的描述：
```
设计模式的核心是变与不变，主要任务是用动态的方法隔离出变化的部分
```

## 引入
在业务开发中，我们经常遇到
```C++
enum AlgType {
    ALG_A,
    ALG_B,
    ALG_C,
    // ...
};

void DoAlg() {
  if(alg_type == ALG_A) {
    //... 
  } else if(alg_type == ALG_B) {
    //... 
  } else if(alg_type == ALG_C) {
    //... 
  }
  // ...
}
```
上面的代码中，我们可以看到，DoAlg 这个函数的实现中，如果我们要增加一个新的算法ALG_D, 我们需要修改enum AlgType 以及给DoAlg 函数增加一个分支。 这是一种常见的以静态的代码修改方式支撑业务变化的方法。此处的修改，往往意味着联动修改DoAlg的测试用例，或者调用此函数的代码要做联动修改。

## 策略模式
策略模式是将ALG_A、ALG_B、ALG_C的具体算法封装成类型，并且在创建处由工厂模式创建，然后在DoAlg 中，只需要调用具体类型的接口即可。这样，DoAlg 这个高层调用者就可以维持不变。新增的算法类型，则实现一个策略类型即可。
```C++
class AlgObject {
  public:
  virtual void Do() = 0;
  virtual ~AlgObject() = default; 
protected:
  std::string alg_type_;
}

class AlgA : public AlgObject {
  public:
  virtual void Do() override {
    //...
  } 
}
class AlgB : public AlgObject {
  public:
  virtual void Do() override {
    //...
  } 
}

class AlgC : public AlgObject {
  public:
  virtual void Do() override {
    //...
  } 
}

class AlgD : public AlgObject {
  virtual void Do() override {
    //...
   } 
}

// 此处factory 仅供示例
class AlgFactory {
  public:
  static AlgObject* CreateAlg(AlgType alg_type) {
    // 或者通过register的方式，消除这个switch-case
    switch(alg_type) {
      case ALG_A: return new AlgA();
      case ALG_B: return new AlgB();
      case ALG_C: return new AlgC();
      case ALG_D: return new AlgD();
      default: return nullptr;
    }  
  } 
}

void DoAlg(AlgObject *alg) {
// 复杂代码
alg->Do();
// 复杂代码
}

void Foo(){
  // 总归是需要一个创建的过程，其中如果用一些绑定方法，或许可以消除调用者对创建的感知
  AlgObject *alg = AlgFactory::CreateAlg(ALG_A);
  // DoAlg 稳定了，其中可能包含复杂代码
  DoAlg(alg);
}
```
不需要策略模式的情况:
1. DoAlg 中的分支确定不会增长
2. 原型阶段，尚未摸清楚此部分有无增长的可能性

**软件开发和维护** 是一个动态的实践过程，并不能一蹴而就。