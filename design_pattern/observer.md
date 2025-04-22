## 观察者模式
Observer 模式我认为是异步编程中经常使用的模式，几乎和单例一样普遍。

一个直接的原因是，几乎没有人会在系统或者某个内部模块发生某些事情的时候直接去调用外部的细节实现，除非是出于极端的性能需求。

首先我们写出与观察者对立的代码:
```C++
// 假设是某个内部模块，如文件下载的实现
class NoObserver {
public:
    void SthHappened(void* arg) {
      // 丑陋且死板，并且极难扩展
      ProgressBar * bar = static_cast<ProgressBar*>(arg);
      bar->Update(100);
    }
}
```

但凡有一点编程常识的人都会意识到这么写代码带来的灾难性问题：模块和业务的紧耦合。

很简单的，我们可以通过Observer 模式来解决这个事情

```C++
class Observer {
public:
  virtual void OnSthHappened(void* arg) = 0;
  virtual ~Observer() = default; 
};

class MyObserver : public Observer {
public:
  virtual void OnSthHappened(void* arg) override {
    // 带有一些细节处理
    ProgressBar * bar = static_cast<ProgressBar*>(arg);
    bar->Update(100);
  } 
};

class Subject {
public:
  void AddObserver(Observer* observer) {
    observers_.push_back(observer);
  }
  void RemoveObserver(Observer* observer) {
    // 省略
  }
  void NotifyObservers(void* arg) {
    // 广播
    for (auto& observer : observers_) {
      observer->OnSthHappened(arg);
    }
  } 
};
```

当然了，我们可以通过std::function 来代替Observer 的类型集成关系和声明，但要留意多线程场景下， 函数对象的有效性观察可能不及Observer 来的方便。