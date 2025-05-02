## 引入
我们的日常业务中，对于某一个类型的子类，如animal:
```C++
// 过于classic，以至于能直接推导出来，难绷
class Animal {
public:
  // 这种样板代码我一直认为应当做到语言中
    virtual ~Animal() {}
    virtual void speak() = 0;
};

class Dog : public Animal {
public:
    void speak() override { std::cout << "Woof!" << std::endl; } 
}

class Cat : public Animal {
public:
    void speak() override { std::cout << "Meow!" << std::endl; } 
}

class Bird : public Animal {
public:
    void speak() override { std::cout << "Chirp!" << std::endl; } 
}

class Fish : public Animal {
public:
    void speak() override { std::cout << "Blub!" << std::endl; } 
}

enum AnimalType {
    Dog_,
    Cat_,
    Bird_,
    Fish_, 
}

Animal* CreateAnimal(int animalType) {
  if(animalType == Dog_) {
    return new Dog();
  }
  // ...
}
```

这种方法称作简单工厂方法，新增一个Animal的子类，需要增加CreateAnimal的判断分支，以及增加枚举。 调用端需要知道这些枚举值，这是一种静态的绑定（意味着要改代码）。

更有甚者，会将CreateAnimal 散落在各处。这对于有一定编程经验的人来说是不可原谅的。

## 工厂模式
工厂模式是不使用静态的CreateAnimal， 而使用抽象工厂类型、具体工厂类型来消除CreateAnimal的分支。 具体而言:
```C++
class AnimalFactory {
public:
    virtual Animal* createAnimal() = 0;
    virtual ~AnimalFactory() {}
};

class DogFactory : public AnimalFactory {
public:
    Animal* createAnimal() override { return new Dog(); } 
}

class Dog : public Animal {
public:
    void speak() override { std::cout << "Woof!" << std::endl; } 
}

//... 其他Animal的工厂

```
这样，我们消除了的CreateAnimal修改，但是客户端侧，仍然需要具体使用哪个工厂，如:
```C++
// 使用dog
AnamalFactory* factory = new DogFactory();
factory->createAnimal()->speak();

// 使用cat
AnamalFactory* factory = new CatFactory();
factory->createAnimal()->speak();
```
这实际上仍然包含静态代码的修改，并且，这种代码人手动来写的话，比较臃肿（现在是AI时代，这个命题已经不成立了） 

## 抽象工厂
抽象工厂模式是聚合了产品族，如:
```C++
class DevicesFactory {
public:
    virtual AbstractPhone* getPhone() = 0;
    virtual AbstractTablet* getTablet() = 0;
    virtual AbstractLaptop* getLaptop() = 0;
    virtual ~DevicesFactory() {}
};

class AppleDevicesFactory : public DevicesFactory {
public:
    AbstractPhone* getPhone() override { return new Phone(); }
    AbstractTablet* getTablet() override { return new IPAD(); }
    AbstractLaptop* getLaptop() override { return new MAC(); } 
}

class SamsungDevicesFactory : public DevicesFactory {
public:
    AbstractPhone* getPhone() override { return new Galaxy(); }
    AbstractTablet* getTablet() override { return new Tablet(); }
    AbstractLaptop* getLaptop() override { return new Laptop(); } 
}
// 以下是具体的设备声明...
```
此处，一个抽象工厂能够负责多个产品的创建，如AppleDevicesFactory可以负责创建Apple的所有设备，而SamsungDevicesFactory可以负责创建Samsung的所有设备。 但是同样的，客户端侧仍然需要根据扩展**修改**。

## 反射
真正能解决这个问题的，我认为还是通过类似反射的动态注册机制，客户端可以通过稳定的、可以在运行时确定参数的接口来动态的创建对象。

回到简单工厂方法:
```C++
Animal* CreateAnimal(int animalType) {
  if(animalType == Dog_) {
    return new Dog();
  }
  // ...
}
/// 我们可以修改成
class AnimalFactory {
  static std::unordered_map<int, AnimalFactory*> animalFactories;
public:
  static Animal* CreateAnimal(int animalType) {
    if(animalFactories.find(animalType) == animalFactories.end()) {
      return nullptr; 
    }
    return animalFactories[animalType]->createAnimal();
  }
  static void RegisterAnimalFactory(int animalType, AnimalFactory* factory) {
    animalFactories[animalType] = factory;
  }
  virtual Animal* createAnimal() = 0;
}

// 其他各工厂的实现...

// 提供类似于宏的接口，用于注册
#define REGISTER_ANIMAL_FACTORY(animalType, factory) \
  AnimalFactory::RegisterAnimalFactory(animalType, new factory());

void RegisterAll(){
  REGISTER_ANIMAL_FACTORY(Dog_, DogFactory);
  // ... 其他动物
}

// 客户端侧的参数，可以来自于配置文件，或者别的什么地方， 全局的，一开始的RegisterAll()的函数的变化，我认为是可以容忍的（把他当做语言的一种固定机制）
// 只是因为我们没有，所以我们要手动编写并调用

int  main() {
  RegisterAll();
  int animalType;
  // 这里指明动态确认类型
  std::cin >> animalType;
  
  Animal* animal = AnimalFactory::CreateAnimal(animalType);
}
```
此处的animalType 甚至可以在运行时加载，而不必因为简单工厂模式的限制导致无法扩展。 我们可以在动态加载插件(or sth)初始化的时候，把自己的类型注册进去。具体就要根据实际业务和框架确定了。


## 原型模式
1. 在客户端代码使用前，预先提供一些样板实例，这些实例就是prototype
2. 在客户端需要构造一个对象时，通过clone方法构造某个原型的一个副本（**注意不是引用**），从而简化复杂对象的创建工作
    - C++中就是拷贝构造，某些语言可能需要借助一些序列化的方法

## 构造器(Builder)
Builder 模式要点可以分为两部分，一是将**对象表示和创建分离**， 二是将分离出来的创建步骤抽象成一个独立的builder类。builder 类可以根据类的复杂情况设计

就表示和创建分离而言，我们实际上用的很多了，比如，对于一个复杂对象:
```C++
class ComplexObject {
public:
// default construct
    ComplexObject() {
        // 复杂的初始化逻辑
    }

    static ComplexObject *create() {
       auto c = new ComplexObject();
       c->InitPart1();
       c->InitPart2();
       // ....
       // 成功返回对象，否则nullptr
    }
    // ... 具体的构造逻辑
}
```
这个是一个常用的技法，原因在于
1. 构造函数如果抛异常，或者发生某些失败情况，需要**业务代码销毁这个对象**, 样板代码
2. 要提供一些额外的flag 判断创建情况
3. 创建工作拆分到一个独立的static 方法中，就可以解决1,2的问题

分离成builder 类，要看具体的情况，如果只是为了分离复杂的创建动作， builder 用static 提供足够。但是以下情况是需要分离的
1. builder 创建对象的过程，某些步骤是可选的，并且对业务代码可控
2. builder 直接根据业务需要动态控制构建步骤，例如就像java的builder一样:
```java
StringBuilder sb = new StringBuilder();
// 这里比使用 += 构造更为高校
sb.append("Hello").append(" ").append("World").append("!");
sb.toString();
```
上面的代码中， append的字符串列表可能是运行时才能获知的，这里通过Builder 维持一个对象ctx, 并且在构造完毕时提供一个完整对象时一个绝佳选择。

这里可能会问：

不能通过类似于C++ std::vector<std::string> 这类的东西来构造吗？然后内部不断拼接？
    - 在构造这个用于初始化的vector 同时已经可以把对象构造好，何必多次一句呢

当然了，builder可以像工厂模式那样，每一个类型对应一个builder，再抽象一个builder 基类，对应也提供这些类型的基类。这个可以根据业务需求敲定

## 创建型模式总结

### 简单工厂

提供一个总的工厂类和创建方法，依据类型描述（如枚举、字符串），通过switch-case 或者if-else 创建

改进：允许派生类进行动态注册，从而实现类似于反射的功能，以消除工厂类方法中的if-else 分支

**不涉及类的创建的具体工作**

### 工厂方法
1. 提供一个工厂基类和类型基类
2. 每个类型对应一个工厂类，工厂类继承自工厂基类
3. 工厂类提供一个创建方法，返回类型基类的指针

这里的工厂类本身，仍然需要类似于动态注册机制一样的东西，以消除客户端对具体工厂类的感知（换句话说，如果没有，则客户端仍然能感知到这些具体的工厂类）

### 抽象工厂

和工厂方法类似，只是一个工厂类型可以产生一组相关联的产品

### 原型模式

事先提供复杂对象的原型，以供业务代码copy。提供clone 接口

### 构造器模式
1. 将对象的构造过程与表示分离，提供一个builder 类，用于构建对象。
2. 每个类型可以对应一个builder类，并且在动态创建的场景下，可以根据需要动态控制构建过程，而免除生成配置文件
    - 配置文件的事情，其实我当前项目中的一个问题，比如ME和Stab的Init，完全可以使用Builder（改进）
