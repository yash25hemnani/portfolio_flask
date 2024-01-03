#include <stdio.h>

void update(int *a,int *b) {
    int temp1 = *a;
    int temp2 = *b;
    *a = *a + *b;
    if (*a>*b){
        *b = temp1 - temp2;
    } 
    else{
        *b = temp2 - temp1;
    }
}

int main() {
    int a, b;
    int *pa = &a, *pb = &b;
    
    scanf("%d %d", &a, &b);
    update(pa, pb);
    printf("%d\n%d", a, b);

    return 0;
}