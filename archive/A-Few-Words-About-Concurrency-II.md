## ![alt text](../img/icons/png/microphone-1.png) A Few Words About Concurrency (part II)

In the first one of this series I wrote about [locking](./A-Few-Words-About-Concurrency-I.html). In this essay, I would like to talk about *memory model*. 

I have been reading about concurrency these days and wish to be able to write concurrency programs as fluently as sequential ones. But it is very difficult. There are many intimidating concepts in the literature I read, which feel non-understandable and usually cannot be applied directly to real world programming (most of them are mathematical concepts). Among all the things involved, I found that *memory model* is a big topic, and once you know something of it, you open the door of concurrent programming.

By [definition](https://en.wikipedia.org/wiki/Memory_model_(programming)), a **memory model** describes the interactions of threads through memory and their shared use of the data. In a world, it is a contract between programmers and systems, which specific whether some kinds of memory operation are allowed or not. For example:

```C
int a = 0;
int b = 0;

//thread 1
void T1(){
}
```





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





