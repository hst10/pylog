#include "insertion_sort_itself.h"
#include "insertion_sort_parallel.h"
#include "merge_sort_itself.h"
#include <iostream>
#include "stdio.h"
int main(){
	int fail = 0;
	DTYPE A[SIZE];
	for (int i=0; i<SIZE; i++){
		A[i] = 2000-i;
	}
	DTYPE B[SIZE];	

	insertion_sort_itself(A);
	//merge_sort_itself(A);
	for (int i=0; i<SIZE; i++){
		B[i] = A[i] ; 
	}

	//insertion_sort_parallel(A,B);

    for(int i = 0; i < SIZE; i++)
        std::cout << B[i] << " ";
    std::cout << "\n";

    for(int i = 1; i < SIZE; i++) {
        if(B[i] < B[i-1]) {
            std::cout << i << " " << B[i-1] << ">" << B[i] <<
                "\n";
            fail = 1;
        }
    }

	if(fail == 1)
		printf("FAILED\n");
	else
		printf("PASS\n");

	return fail;
}