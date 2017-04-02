#include <iostream>
#include <exception>
using namespace std;

int partition(int *arr, int lhs, int rhs){
    int ind = lhs - 1;
    int pivot = arr[rhs-1];
    while(lhs < rhs-1){
        if(arr[lhs] < pivot){
            std::swap(arr[++ind], arr[lhs]);
        }
        lhs++;
    }
    std::swap(arr[ind+1], arr[rhs-1]);
    return ind+1;
}

void myqsort(int *arr, int lhs, int rhs){
    if(lhs < rhs){
        int m = partition(arr, lhs, rhs);
        myqsort(arr, lhs, m);
        myqsort(arr, m+1, rhs);
    }
}

int main()
{
    //int arr[10] = {2,3,4,5,6,1,1,3,10,6};
    int arr[10] = {0,0,0,0,0,0,0,0,0,1};
    for(auto i : arr){
        cout<<i<<endl;
    }
    myqsort(arr, 0, 10);
    for(auto i : arr){
        cout<<i<<endl;
    }
}
