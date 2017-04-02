/*
 * atomic-increment-balance.c  
 *
 *    This program show how concurrently updating the same variable
 *    with atomic operation would produce the correct result
 *
 * By walkerlala. No warranty provided. 2017-03-23
 *
 * On Linux, compile with:
 *    gcc -Wall atomic-increment-balance.c -o atomic-increment-balance -lpthread
 * and then run as:
 *    ./atomic-increment-balance
 */

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

int balance;

/* you can change this by providing a integer as program argument */
int rnd = 100000;

void *p1(void *ptr)
{
    for(int i=0; i<rnd; i++){
        __sync_fetch_and_add(&balance, 1);
    }
    return NULL;
}

void *p2(void *ptr)
{
    for(int i=0;i<rnd; i++){
        __sync_fetch_and_sub(&balance, 1);
    }
    return NULL;
}

int main(int argc, char *argv[])
{
    if(argc >= 2){
        int tmp = atoi(argv[1]);
        if(tmp > 100000){
            rnd = tmp;
        }
    }
    printf("Setting round to: %d\n", rnd);

    printf("Before two threads running, balance = %d\n", balance);

    pthread_t threads[2] = {PTHREAD_ONCE_INIT, PTHREAD_ONCE_INIT};

    pthread_create(&threads[0], NULL, p1, NULL);
    pthread_create(&threads[1], NULL, p2, NULL);

    pthread_join(threads[0], NULL);
    pthread_join(threads[1], NULL);

    printf("After two threads running, balance = %d\n", balance);
}
