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
