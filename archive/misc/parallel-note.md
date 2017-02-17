- **live lock** , Too busy to respond to others to resume work. They are not blocking. *e.g.*, two people meet in corridor:  1) A left B left -> A right B right -> A left B left .... infinite loop

- **dead lock**, 

- Philosopher dinning problem solutions

  - Resource Hierarchy
  - Semaphores / Arbistrator
  - Chandy / Misra (use dirty / clean fork to indicate priority )

- priority inversion solution (assume priority of **H**, **M**, **L**)

  * locking with interrupts disabled

    So that **M** cannot pre-empt **L** because pre-emption require interrupt

  * priority ceiling

    the mutex give his *high* priority to **L**

  * priority inheritance

    **L** inherits **H**'s priority so that **M** cannot pre-empt 

  * Random boosting

    ready task holding lock are randomly boosted in priority until they exit the critical region

  * Avoid blocking by using **Non-blocking synchronization** or **Read-copy-update** 

- producer-consumer problem

  - bonus: why this snippet is wrong?

    ```c
    int itemCount = 0;

    procedure producer() {
        while (true) {
            item = produceItem();

            if (itemCount == BUFFER_SIZE) {
                sleep();               // <- sleep with nothing waken up
            }

            putItemIntoBuffer(item);
            itemCount = itemCount + 1;

            if (itemCount == 1) {
                wakeup(consumer);      // <- can't wake up before haven't sleep
            }
        }
    }

    procedure consumer() {
        while (true) {

            if (itemCount == 0) {
                sleep();            // <-- preempted before sleep
            }

            item = removeItemFromBuffer();
            itemCount = itemCount - 1;

            if (itemCount == BUFFER_SIZE - 1) {
                wakeup(producer);
            }

            consumeItem(item);
        }
    }
    ```

    this would cause dead-lock

  - A refined one using semaphore:

    ```c
    semaphore fillCount = 0; // items produced
    semaphore emptyCount = BUFFER_SIZE; // remaining space

    procedure producer() {
        while (true) {
            item = produceItem();
            down(emptyCount);
            putItemIntoBuffer(item);
            up(fillCount);
        }
    }

    procedure consumer() {
        while (true) {
            down(fillCount);
            item = removeItemFromBuffer();
            up(emptyCount);
            consumeItem(item);
        }
    }
    ```

    This work fine with only on producer and consumer.(when there are more than one producer, they would possibly write to the same slot at the same time )

  - final solution using semaphor with a mutex

    ```c
    mutex buffer_mutex; // similar to "semaphore buffer_mutex = 1", but different (see notes below)
    semaphore fillCount = 0;
    semaphore emptyCount = BUFFER_SIZE;

    procedure producer() {
        while (true) {
            item = produceItem();
            down(emptyCount);
                down(buffer_mutex);    // <- lock the buffer first
                    putItemIntoBuffer(item);
                up(buffer_mutex);
            up(fillCount);
        }
    }

    procedure consumer() {
        while (true) {
            down(fillCount);
                down(buffer_mutex);
                    item = removeItemFromBuffer();
                up(buffer_mutex);
            up(emptyCount);
            consumeItem(item);
        }
    }
    ```

    ​

- Reader-writer problem

  - The first readers-writers problem:  The writer may starve (*reader preference*)
  - The second readers-writers problem: The reader may starve (*writer preference*)
  - The third readers-writers problem:  With a FIFO semaphores, neither readers nor writers will starve

- seqlock -- a improved version of reader-writer-lock(rwlock)

  - writer increment sequence number after acquiring lock and before releasing lock

  - readers check the sequence number before and after reading the shared data

    (If the sequence number is odd on either occasion, a writer had taken the lock while the data was being read and it **may or may not** have changed. If the sequence numbers are different, a writer has changed the data while it was being read. In either case readers simply retry (using a loop, or in Linux, `read_seqretry()`) until they read the same even sequence number before and after)

  *Features*:

  - In Linux, it use spin lock to implement
  - readers would not be blocked
  - suitable for situation where write is rare but read is frequent

  *References*

  - https://en.wikipedia.org/wiki/Seqlock
  - https://lwn.net/Articles/22818/

- RCU

  **read-copy-update** (**RCU**) is a synchronization mechanism implementing a kind of mutual exclusion that can sometimes be used as an alternative to a [readers-writer lock](https://en.wikipedia.org/wiki/Readers-writer_lock). It allows extremely low overhead, [wait-free](https://en.wikipedia.org/wiki/Non-blocking_synchronization) reads(allow read to occur concurrently with update). However, RCU updates can be expensive, as they must leave the old versions of the data structure in place to accommodate pre-existing readers. These old versions are reclaimed after all pre-existing readers finish their accesses.

  In contrast with conventional locking primitives that ensure mutual exclusion among concurrent threads **regardless of whether they be readers or updaters**, or with reader-writer locks that **allow concurrent reads but not in the presence of updates**, **RCU supports concurrency between a single updater and multiple readers**. RCU ensures that reads are coherent by maintaining multiple versions of objects and ensuring that they are not freed up until all pre-existing read-side critical sections complete. RCU defines and uses efficient and scalable mechanisms for publishing and reading new versions of an object, and also for deferring the collection of old versions. These mechanisms distribute the work among read and update paths in such a way as to make read paths extremely fast. In some cases (non-preemptable kernels), RCU's read-side primitives have zero overhead.

  At its core, RCU is nothing more or less than an API that provide:

  1. a publish-subscribe mechanism for adding new data (`rcu_assign_pointer()`, `rcu_dereference()`)
  2. a way of waiting for pre-existing RCU readers to finish, (*e.g,* `synchronize_rcu()`)
  3. a discipline of maintaining multiple version to permit change without harming or unduly delay concurrent RCU readers

  $$\blacksquare$$ **Advantage**

  - extremely low overhead of read
  - Immunity to read-side deadlock (because read-size do not involve any spin, block, and backwark branches )
  - Immunity to priority inversion (because low-priority RCU readers cannot prevent a high-priority RCU updater from acquiring the update-side lock. Similarly, a low-priority RCU updater cannot prevent high-priority RCU readers from entering an RCU read-side critical section)
  - small real-time latency
  - RCU readers and updaters run concurrently

  $$\blacksquare$$  **reference**

  [1] : https://lwn.net/Articles/262464/

  [2] : https://lwn.net/Articles/263130/

  [3] : https://lwn.net/Articles/264090/

- TODO: Linux file concurrent access

- TODO: Try this simple program using parallel C/C++ (and compiler optimization) W/O `volatile` or *memory barrier* to see the difference 

- TODO: smp_rmb ->  read : read

  ​             smp_wmb -> write : write

  ​             smp_mb   ->   r/w  :  r/w

   then  what could be    read  :  read /write ? and similarily write : read/write ?

- Memory barier transitivity

  - Although memory barier only guarantee to have effect on **current** CPU, all mainstream CPU provide a feature called **memory barier transitivity**: 

    > If **B** saw the effects of **A**'s accesses, and **C** saw the effects of **B**'s accesses, then **C** must also see the effects of **A**'s accesses.

    All CPUs I am aware of claim to provide transitivity.

- TODO: quick quiz B.13

- A good elaboration of memory ordering on modern processors [by Paul McKenney](./mem-ordering-Paul-McKenney.pdf)
