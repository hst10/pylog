#include <stdio.h>
#include <stdlib.h>
#include "../../../matrix_mul.h" //path to header file

int main()
{
	float a[SIZE];
	float b[SIZE];
	float c[SIZE];
	int i;
	//initializing with simple test
	for(i=0;i<SIZE;i++)
	{
		a[i] = (float)i;
		b[i] = (float)i;
		c[i] = 0.0;
	}
	matrix_add_pipeline(a,b,c);
	for(i=0;i<SIZE;i++)
	{
		printf("%f %f\n%f\n",a[i],b[i],c[i]);
	}
}
