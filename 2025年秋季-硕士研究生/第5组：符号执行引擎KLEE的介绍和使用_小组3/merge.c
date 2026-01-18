#include <stdio.h>
#include <stdlib.h>
#include "assert.h"
#include "klee.h"

// 合并两个已排序的子数组
void merge(int arr[], int left, int mid, int right) {
    int i, j, k;
    int n1 = mid - left + 1;
    int n2 = right - mid;
    
    int *L = (int*)malloc(n1 * sizeof(int));
    int *R = (int*)malloc(n2 * sizeof(int));
    
    for (i = 0; i < n1; i++)
        L[i] = arr[left + i];
    for (j = 0; j < n2; j++)
        R[j] = arr[mid + 1 + j];
    
    i = 0;
    j = 0;
    k = left;
    
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k] = L[i];
            i++;
        } else {
            arr[k] = R[j];
            j++;
        }
        k++;
    }
    
    while (i < n1) {
        arr[k] = L[i];
        i++;
        k++;
    }
    
    while (j < n2) {
        arr[k] = R[j];
        j++;
        k++;
    }
    
    free(L);
    free(R);
}

// 归并排序主函数
void mergeSort(int arr[], int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        mergeSort(arr, left, mid);
        mergeSort(arr, mid + 1, right);
        merge(arr, left, mid, right);
    }
}

int main() {
    // 创建符号数组
    int arr[3];
    
    // 让KLEE为数组的每个元素创建符号值
    klee_make_symbolic(arr, sizeof(arr), "arr");
    
    // 约束数组元素的范围
    for (int i = 0; i < 3; i++) {
        klee_assume(arr[i] >= 0);
        klee_assume(arr[i] <= 10);
    }
    
    mergeSort(arr, 0, 2);
    
    // 添加断言来测试排序正确性
    for (int i = 0; i < 2; i++) {
        klee_assert(arr[i] <= arr[i+1]);
    }
    
    return 0;
}
