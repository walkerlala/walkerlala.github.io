## 关于Reliable Data Transimission(RDT): GBN、SR、TCP

### (GBN)Go-Back-N 回退N步

- GBN receiver无须暂存任何顺序步正确的packet，因为sender会重新发送所有未经确认的packet
- GBN的单一packet错误(比如没有在timeout之前接收到ack)将导致重送大量无须重送的packet

##### \#, GBN发送端

- 累积式确认：收到接收端回传的ACK(n)，即表示序号小于n的packet都已经正确收到了。
- 使用一个 Timer：绑定最早发出且未经确认的packet (base)
- 超时行为：Timeout 前都还没收到最早发送出的packet所回传的ACK，则重新发送所有未经确认的packet (base ~ nextseqnum-1)
- 收到顺序不正确的ACK：不做任何事情
- **收到顺序不正确的ACK：不做任何事情**(这个我怀疑。我觉得收到顺序不正确的ACK分为两种情况：如果这个ACK以前就收到了，那么就不处理；但是如果这个ACK是对一个比较靠后的n进行的确认，那么这个n以前的packet都获得了确认)
- 收到顺序正确的ACK：
  - 将base设为ACK序号+1，造成窗口滑动(因此这个协议又称为**窗口滑动协议**)
  - 若还有packet可传送，重新启动Timer，并传送新的packet

##### \#, GBN接收端

- 收到正确顺序的packet：回传该packet序号的ACK给传送端
- 收到错误顺序的packet：回传最后一次收到正确序号的ACK给传送端

### SR(Selective Repeat) 选择重传

- SR传送端只重新发送接收端未正确收到的packet

- SR会将失序的packet缓存

- SR的传送端、接收端双方的window位置各不相同

- SR窗口的大小不许等于有限序号大小的一半

  $$\blacksquare$$ *为什么窗口大小必须是序号大小的一半呢*

  - 假设有限序号０、１、２、３，窗口大小为３。如果此时接收端收到0, 1, 2，则接收端窗口观点会从[0, 1, 2] , 3 , 0, 1, 2, 3...变成0, 1, 2, [3, 0, 1], 2, 3, 假设这时候接收端回传给传送端的ACK遗失从而造成传送端Timeout而重发第一批的0, 1, 2，而此时接收端想要的却是第一批的0, 1....这就尴尬了
  - 同样的情境，将窗口大小改为2, 接收端收到0, 1, 则接收端窗口会从[0, 1], 2, 3, 0, 1, 2, 3 变成 0, 1, [2, 3], 0, 1, 2, 如果同样发生接收端回传的ACK遗失，传送端等待超时从而重传第一批的0, 1，这时候接收端就不会有错乱的问题了。

##### \#, SR 传送端

- 超时事件：每个packet都已自己的Timer，当各个packet的ACK都超时时，则重新发送该packet
- 收到ACK：
  1. 标记对应序号的packet为已经确认
  2. 若收到的ACK序号是base，则将base移动到下一个最小未经确的packet上
  3. 若窗口移动到了尚未传送的packet上，则同时传送这些未被传送的packet

##### \#, SR 接收端

- 接收到目前window内任何一个packet：
  1. 回传收到的序号的ACK给传送端
  2. 若收到的序号不是base，则将packet缓存
  3. 若收到的序号是base，从base与其后连续已收到的packet交给上层，并将window移动到最小预期收到的位置上。例如：接收端窗口为0, 1, 2, 3, 4, 此时收到1, 2, 3, 将他们缓存起来，之后收到base, 则将0, 1, 2, 3交给上层，并将window移动到 4
- 收到window之前的packet：立刻回传（如果不传，传送端的窗口可能无法移动）
- 收到其他packet：忽略

### TCP (Transmission Control Protocol)

- TCP 传送端只需要维护「最小已经发出未经确认的packet的序号」以及「下一个要传送的packet的序号」
- TCP对一次 Timeout 最多只重发一个packet
- TCP的ACK与GBN、SR的ACK不同，TCP传送端所发出的ACK，表示期待下一次要收到的packet的序号，而GBN、SR是用了确认已经收到的packet的序号
- TCP同SR一样会将失序的packet缓存（其实TCP的RFC里面并没有要求这个行为，但是大多数的TCP实现都是这样做的）
- TCP为累积式确认（也有某种TCP修正称为选择性确认）

##### \#, TCP 传送端

- 超时：重发packet
- 定时地在某些特定的时刻对网络状态做估计，得到估计时延（EstimatedRTT），用来设置定时器的TimerInterval
- 加倍时间间隔：每次TCP重传都会将下一次的超时间隔设为先前的两倍
- 收到重复三次的ACK（Duplicate ACK）：重发packet，又称**快速重传**

##### \#, TCP 接收端

- 预期packet抵达：回传下一次期望收到的packet的ACK
- 非预期的packet抵达：暂存packet，送出期望收到的packet的序号的ACK