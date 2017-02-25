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