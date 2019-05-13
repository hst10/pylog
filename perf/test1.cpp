#include <iostream>
#include <cstdio>
#include <ctime>

int main()
{
    std::clock_t start;
    double duration;

    const int length = 1 << 20; 
    float a = new float[length]; 
    float b = new float[length]; 
    float c = new float[length]; 

    for (int i = 0; i < length; i++)
    {
        a[i] = static_cast <float> (rand()) / static_cast <float> (RAND_MAX);
        b[i] = static_cast <float> (rand()) / static_cast <float> (RAND_MAX);
    }

    start = std::clock();
    #pragma omp parallel for
    for (int i = 0; i < length; i++)
    {
        c[i] = a[i] + b[i];
    }
    duration = ( std::clock() - start ) / (double) CLOCKS_PER_SEC;
    std::cout<<"printf: "<< duration <<'\n';

    return 0;
}
