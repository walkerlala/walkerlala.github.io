## Locking-Interrupts issues

Last time I write an [essay](./A-Few-Words-About-Concurrency-I.html) talking about some locking issues. Basically that is all about locking inside an OS kernel. As a result, user of those kind of lock should be cautious about interrrupts happenning during locking, which would probably cause deadlock. The reason why it may cause deadlock need some explanations, and I will add a few notes here:

#### \#, 1 locks used in an interrupt handler

If a thread A holding a spinlock T get interrupted and the interrupt handler responsible for this interrupt try to acquire T, then we may have deadlock.

```C
lock(&somelock);
...
  <- interrupt comes in
     lock(&somelock);    <- lock in interrupt handler
```

If the interrupt handler is run on a different CPU, it OK. But it is not OK if the interrupt handler run on the same CPU (which is the case for UP systems), because A would never have chances to run before the interrupt handler return (*i.e* before the interrupt has been processed), while at the same time the interrupt handler, unfortunately, fail to acquire the lock and spin/get blocked.

For this reason,  one should disable interrupt before locking in the kernel code. As far as I know, in Linux, they provide two kinds of spinlocks:

```
spin_lock(..);   /* spinlock that does not disable interrupts */
spin_lock_irqsave(...); /* spinlock that disable local interrupt */
```

FreeBSD's spinlock donnot allow interrupt.

#### \#, The priority inversion problem

This is for spinlock.

If thread B with a higher priority get in and try to acquire the lock that thread A currently holds, then thread B would spin, while at the same time  thread A has no chance to run because it has lower priority, thus not being able to release the lock.

For this reson, disabing interrupts is desirable.