- Getting a **shared_ptr** for **this** object

  $$\blacksquare$$ Motivation

  Imagine the following scenario

  ```cpp
  class Thing {
  public:
  	void foo();
  	void defrangulate();
  };
  void transmogrify(Thing *);
  int main()
  {
  	Thing * t1 = new Thing;
  	t1->foo();
  	...
  	delete t1; // done with the object
  }
  ...
  void Thing::foo()
  {
  	// we need to transmogrify this object
  	transmogrify(this);
  }
  ...
  void transmogrify(Thing * ptr)
  {
  	ptr->defrangulate();
  	/* etc. */
  }
  ```

  How do we transform it to use **shared_ptr** so that it's more c++11-ish ?

  Maybe this:

  ```cpp
  class Thing {
  public:
  	void foo();
  	void defrangulate();
  };
  void transmogrify(shared_ptr<Thing>);
  int main()
  {
  	shared_ptr<Thing> t1(new Thing); // start a manager object for the Thing
  	t1->foo();
  	...
  	// Thing is supposed to get deleted when t1 goes out of scope
  }
  ...
  void Thing::foo()
  {
  	// we need to transmogrify this object
  	shared_ptr<Thing> sp_for_this(this); // danger! a second manager object!
  	transmogrify(sp_for_this);
  }
  ```

  However, we would end up deleting an object twice, which is a severe error.

  $$\blacksquare$$ Solution

  To solve this, we can:

  > The **Thing** class must be modified to inherit from **enabled_shared_from_this\<Thing\>**, so that **Thing** now has a **weak_ptr\<Thing\>** as a member variable. When the first shared_ptr to a Thing object is created, the shared_ptr constructor uses template magic to detect that the enable_shared_from_this base class is present, and then initializes the weak_ptr member variable from the first shared_ptr. Once this has been done, the weak_ptr in Thing points to the same manager object as the first shared_ptr. Then when you need a shared_ptr pointing to this Thing, you call the shared_from_this() member function, which returns a shared_ptr obtained by construction from the weak_ptr, which in turn will use the same manager object as the
  > first shared_ptr.

  So the solution is:

  ```cpp
  class Thing : public enable_shared_from_this<Thing> {
  public:
  	void foo();
  	void defrangulate();
  };
  int main()
  {
  	// The following starts a manager object for the Thing and also
  	// initializes the weak_ptr member that is now part of the Thing.
  	shared_ptr<Thing> t1(new Thing);
  	t1->foo();
  	...
  }
  ...
  void Thing::foo()
  {
  	// we need to transmogrify this object
  	// get a shared_ptr from the weak_ptr in this object
  	shared_ptr<Thing> sp_this = shared_from_this();
  	transmogrify(sp_this);
  }
  ...
  void transmogrify(shared_ptr<Thing> ptr)
  {
  	ptr->defrangulate();
  	/* etc. */
  }
  ```

  One caveat about this is that you can't use **shared_from_this()** in the constructor of the **Thing** class. The **weak_ptr** member variable has to be set to point to the manager object by the shared_ptr constructor, and this can't run until the Thing constructor has completed.

  $$\blacksquare$$ About linkage

- *Non-const* global variables have *external* linkage by default

- *Const* global variables have *internal* linkage by default

- Functions have *external* linkage by default



数组在一般情况下会转换成首元素指针右值，除了：

- sizeof 运算的时候
- 取地址的时候（得到的是指向数组的指针而不是指向首元素的指针）
- C11的_Alignof运算符



In computer science and object oriented programming, a **passive data structure** (**PDS**, which is also termed a **plain old data structure**, or **POD**), is a term for a record, to contrast with objects. It is a data structure that is represented only as passive collections of field values (instance variables) without using object-oriented features.

A PDS type in C++, or Plain Old C++ Object, is defined as either a scalar type or a PDS class. A PDS class has

- no user-defined copy assignment operator
- no user-define destructor
- no non-static members that are not themselves PDS
- an aggregate, which means that it has no user-declared constructors, no private nor protected non-static data, no virtual base class and no virtual functions

(the `type_traits`library in the STL provides a function name `is_pod`that can be used to determined whether a given type is a POD)

In [Java](https://en.wikipedia.org/wiki/Java_(programming_language)), some developers consider that the PDS concept corresponds to a class with public data members and no methods (Java Code Conventions 10.1),[[6\]](https://en.wikipedia.org/wiki/Passive_data_structure#cite_note-Oracle-7) i.e., a [data transfer object](https://en.wikipedia.org/wiki/Data_transfer_object).[[7\]](https://en.wikipedia.org/wiki/Passive_data_structure#cite_note-8) Others would also include [Plain Old Java Objects](https://en.wikipedia.org/wiki/Plain_Old_Java_Object) (POJOs), a class that has methods but only getters and setters, with no logic, and [Java Beans](https://en.wikipedia.org/wiki/Java_Beans) to fall under the PDS concept if they do not use event handling and do not implement added methods beyond getters and setters.[*citation needed*] However, POJOs and Java Beans have [encapsulation](https://en.wikipedia.org/wiki/Encapsulation_(computer_programming)), and so violate the fundamental definition of PDS.

- some note

  ```cpp
  class A {
  public:
      A() {}
      A(int i){
          cout << "contructing with int"<<endl;
      }
    
      //去掉const之后，下面的 A a =1; 会在GCC下编译错误
      //VC++例外，因为VC++允许非常量引用绑定临时值
      A(const A& a) {
          cout<<"copy constructor"<<endl;
      }
  };

  int main(){
      A a = 1;    //先隐式构造，然后拷贝构造(但是GCC一般会吧copy-ctor优化掉，如果要看到copy-ctor的话，加 -fno-elide-constructors)
      return 0;
  }
  ```

- name hidding in C++

  consider this code:

  ```cpp
  #include <stdio.h>

  class Base {
  public: 
      virtual void gogo(int a){
          printf(" Base :: gogo (int) \n");
      };

      virtual void gogo(int* a){
          printf(" Base :: gogo (int*) \n");
      };
  };

  class Derived : public Base{
  public:
      virtual void gogo(int* a){
          printf(" Derived :: gogo (int*) \n");
      };
  };

  int main(){
      Derived obj;
      obj.gogo(7);
  }
  ```

  will compile with this errror:

  ```
  > g++ -pedantic -Os test.cpp -o test
  test.cpp: In function `int main()':
  test.cpp:31: error: no matching function for call to `Derived::gogo(int)'
  test.cpp:21: note: candidates are: virtual void Derived::gogo(int*) 
  test.cpp:33:2: warning: no newline at end of file
  ```

  This is know as the **name hiding rule** of C++

  The rationale behind it:

  > The decision, the rationale behind the name hiding, i.e. *why* it actually was designed into C++, is to avoid certain counterintuitive, unforeseen and potentially dangerous behavior that might take place if the inherited set of overloaded functions were allowed to mix with the current set of overloads in the given class. You probably know that in C++ overload resolution works by choosing the best function from the set of candidates. This is done by matching the types of arguments to the types of parameters. The matching rules could be complicated at times, and often lead to results that might be perceived as illogical by an unprepared user. Adding new functions to a set of previously existing ones might result in a rather drastic shift in overload resolution results.

  > For example, let's say the base class `B` has a member function `foo` that takes a parameter of type `void *`, and all calls to `foo(NULL)` are resolved to `B::foo(void *)`. Let's say there's no name hiding and this `B::foo(void *)` is visible in many different classes descending from `B`. However, let's say in some [indirect, remote] descendant `D` of class `B` a function `foo(int)` is defined. Now, without name hiding `D` has both `foo(void *)` and `foo(int)` visible and participating in overload resolution. Which function will the calls to `foo(NULL)` resolve to, if made through an object of type `D`? They will resolve to `D::foo(int)`, since `int` is a better match for integral zero (i.e. `NULL`) than any pointer type. So, throughout the hierarchy calls to `foo(NULL)`resolve to one function, while in `D` (and under) they suddenly resolve to another.

  > This behavior was deemed undesirable when the language was designed. As a better approach, it was decided to follow the "name hiding" specification, meaning that each class starts with a "clean sheet" with respect to each method name it declares. In order to override this behavior, an explicit action is required from the user: originally a redeclaration of inherited method(s) (currently deprecated), now an explicit use of using-declaration.

  ref: [SO-answer](https://stackoverflow.com/questions/1628768/why-does-an-overridden-function-in-the-derived-class-hide-other-overloads-of-the)
