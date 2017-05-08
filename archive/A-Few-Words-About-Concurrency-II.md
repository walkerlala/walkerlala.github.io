## ![alt text](../img/icons/png/microphone-1.png) A Few Words About Concurrency (part II)

In the first one of this series I wrote about [locking](./A-Few-Words-About-Concurrency-I.html). In this essay, I would like to talk about *memory model*. 

I have been reading about concurrency these days and wish to be able to write concurrency programs as fluently as sequential ones. But it is very difficult. There are many intimidating concepts in the literature I read, which feel non-understandable and usually cannot be applied directly to real world programming (most of them are mathematical concepts). Among all the things involved, I found that *memory model* is a big topic, and once you know something of it, you open the door of concurrent programming.

### \#1, Introduction

By [definition](https://en.wikipedia.org/wiki/Memory_model_(programming)), a **memory model** describes the interactions of threads through memory and their shared use of the data. In a world, it is a *contract* between programmers and systems, which specific whether some kinds of memory operation are allowed or not. For example:

```C
int X, Y;
int r1, r2;

//thread 1          //thread 2
void T1(){          void T2(){
  X = 1;              Y = 1;
  r1 = Y;             r2 = X;
}                   }
```

it is natural to expect either `r1 == 1`, `r2 == 1` or perhaps both, but never `r1 == 0 && r2 == 0`, because no matter which processor writes 1 to memory first, it’s natural to expect the *other* processor to read that value back. However, this is not the case. We CAN end up with a `r1 == 0 && r2 == 0`, at least on x86, because in many multiprocessor/multicores systems, CPUs are allowed to re-order instruction for optimization. For example, on x86, the specification states that **Loads may be reordered with older stores to different locations**, which means that the above program can be effectively re-ordered to something like this:

```C
int X, Y;
int r1, r2;

//thread 1          //thread 2
void T1(){          void T2(){
  r1 = Y;             r2 = X;
  X = 1;              Y = 1;
}                   }
```

and the final result would be `r1 == 0 && r2 == 0`. You can download a testing program from [here](../code/reorder.zip) to test yourself.

As a contrast to the above example, the following example will work as expected on x86 (the assertion will never fail) because x86's manual specifies that **stores are not reordered with other stores**:

```C
int a=0;
int b=0;

//thread 1                     //thread 2
void T1()                      void T2()
{                              {
    a = 1;                         while(0 == b)
    b = 1;                               ;
                                   assert(1 == a);
}                              }     
```

You see, sometimes CPUs might re-order our program for optimization reason. Besides from re-ordering, CPUs might also perform *pipelining*, *read speculation* and *memory prefetching* to speed up our programs. Therefore, the order where your programs are executed might not be the same with the order you wrote them. In order to enable programmers to reason about their program and be sure what their programs would behave as expected, there must be a *contract* between CPU and programmers, which specifying what CPUs would do on a multiprocessors/multicores platform. That *contract* is called *memory model*, formally.

 ### \#2, Memory Model at the Hardware Level

Actually, there are both memory models on the hardware level and compilers level. Let's start with the hardware level first and take x86 as an example. Note that, for the topic *memory model*, I would mainly talk about memory re-ordering and memory barrier, which you may find different from some text book in you university courses

##### ![alt text](../img/icons/svg/zap.svg) **Implication for the Single-thread World**

That kind of re-ordering might scare you and make you worry about whether you have written a correct program ![alt text](../img/icons/png/happy-4.png)So before we start, let's be clear with the following:

There is a context for all the words I have: **This is all for multi-threads programs**.

The cardinal rule of memory reordering, which is universally followed by compiler developers and CPU vendors, could be phrased as follows^[2]^:

> It should not modify the behavior of a single-threaded program.

Note that this is also true for the programming languages/compilers level.

Therefore, you NEVER have to worry about these things while writing single-threaded program.

![alt text](../img/icons/svg/zap.svg) **X86's Memory Model**

There is a informal memory model for x86^[1]^:

- Loads are *not* reordered with other loads.
- Stores are *not* reordered with other stores.
- Stores are *not* reordered with older loads.
- In a multiprocessor system, memory ordering *obeys causality* (memory ordering respects transitive visibility).
- In a multiprocessor system, stores to the same location have a *total order*.
- In a multiprocessor system, locked instructions have a *total order*.
- Loads and stores are *not* reordered with locked instructions.
- Loads **may** be reordered with older stores to different locations

x86's memory model is a [strong memory model](http://preshing.com/20120930/weak-vs-strong-memory-models/), but it is not [sequential consistent](https://en.wikipedia.org/wiki/Sequential_consistency), which simply means that there are still lots of instruction re-ordering in the x86 world, as illustrated in the first example above. Worse, [Intel's x86 reference](http://www.intel.com/content/www/us/en/processors/architectures-software-developer-manuals.html) doesn't give any formal model for its CPUs, with only some set of rules stating "under what condition what instructions would do what". This make reasoning and automatic-proving difficult. Some prof. in the Cambridge University have proposed a well-proved memory model call [TSO](https://www.cl.cam.ac.uk/~pes20/weakmemory/cacm.pdf) for x86. You might find there [researches](https://www.cl.cam.ac.uk/~pes20/weakmemory/) interesting.

(more things to be added here...linux-kernel's memory model, etc)

![alt text](../img/icons/svg/zap.svg) **Memory Barrier to Rescue**

What can we do in the cases of memory re-ordering? How to make our programs executed as we wrote it? Turns out that every architecture provides explicit [memory barrier](https://en.wikipedia.org/wiki/Memory_barrier) instructions to force CPUs to execute instructions in the order as we wrote it.

For example, to make our first example work correctly, we can insert two lines of memory barrier instructions:

```C
int X, Y;
int r1, r2;

//thread 1              //thread 2
void T1(){              void T2(){
  X = 1;                  Y = 1;
  memory_barrier();       memory_barrier();
  r1 = Y;                 r2 = X;
}                       }
```

What memory barrier means is that every instruction before the memory barrier have to finish and be seen by other processors^[3]^ before instructions after the memory barrier can be executed.

For example, x86 provide three memory barrier (memory fence) instructions^[4]^: `SFENCE`, `LFENCE` and `MFENCE`, which stand for *write memory barrier*(store fence), *read memory barrier*(read fence) and *full memory barrier*(memory fence) respectively. Their differences are listed below:

- Write Memory Barrier

  Any write before the write memory barrier is flush out to the main memory before execution of instructions after the write memory barrier.

- Read Memory Barrier

  When we go past the read memory barrier, it is as if the local memory has been invalidated, and we must fetch from main memory  any variables that will be referenced after the read memory barrier. 

- Full Memory Barrier

  A full memory barrier does both the job of a write memory barrier and read memory bar

Simply put, read memory barrier acts only on instructions that read from memory while write memory barrier acts only on instructions that write to memory.

With memory barrier, we can **explicitly** force CPUs to execute our program in the order as we wrote it and don't have to worry about the reordering issue anymore.

![alt text](../img/icons/svg/zap.svg) **Locks Already Have Memory Barrier Built-in**

I just want to tell you that every kinds of lock I have ever since already have memory barrier built-in. That says, in many cases, you don't have to use memory barrier. A simple lock is sufficient. And that is also why many people can write multi-threads code without caring/knowing memory re-ordering -- their use of locks already perform memory barrier for them.

### \#3, Memory Model at Programming Languages/Compilers Level



### \#4, Memory Consistency Model



### Memory consistency model to ensure safety

- quiescent consistency
- sequential consistency
- linearizability

### Memory model in hardware

- memory barrier
- locking

### Memory model in programming languages

- the java memory model
- the c++ memory model




###### ![alt text](../img/icons/svg/search.svg) Notes

-------

1. I quote it from [here](https://bartoszmilewski.com/2008/11/05/who-ordered-memory-fences-on-an-x86/). You can also find it in [Intel's x86 manual](http://www.intel.com/content/www/us/en/processors/architectures-software-developer-manuals.html).
2. The quote was a tradition English saying from [here](http://preshing.com/20120625/memory-ordering-at-compile-time/).
3. Some argue that memory barrier do **nothing** with data propogation from one part of the system to other part. That is quite true, because [the Alpha processor is an exception for this rule](https://www.cs.umd.edu/~pugh/java/memoryModel/AlphaReordering.html). But for other processor, data propogation can be forced by memory barriers.
4. You can see full semantics of these instruction in these page: [lfence](http://x86.renejeschke.de/html/file_module_x86_id_155.html), [sfence](http://x86.renejeschke.de/html/file_module_x86_id_289.html), [mfence.](http://x86.renejeschke.de/html/file_module_x86_id_170.html)