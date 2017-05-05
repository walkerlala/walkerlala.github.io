#include <stdio.h>
#include <pthread.h>
#include <assert.h>
#include <unistd.h>

#define NUM_T2 1000

int a=0;
int b=0;

void* T1(void* dummy)
{
    b = 0;
    sleep(1);

    a = 1;
    b = 1;
    return NULL;
}

void* T2(void* dummy)
{
    a = 0;
    sleep(1);

    while(0 == b)
        ;
    assert(1 == a);
    return NULL;
}

int main()
{
    pthread_t threads[NUM_T2+1];
    for(int i=0; i<NUM_T2+1; i++){
        threads[i] = PTHREAD_ONCE_INIT;
    }

    for(int i=0; i< 500; i++){
        a = b = 1;
        pthread_create(&threads[0], NULL, T1, NULL);
        for(int i=1; i<NUM_T2+1; i++){
            pthread_create(&threads[i], NULL, T2, NULL);
        }

        for(int i=0; i<NUM_T2+1; i++){
            pthread_join(threads[i], NULL);
        }
    }

    return 0;
}
