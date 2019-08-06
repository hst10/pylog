#include <iostream>
#include <cstdio>
#include <ctime>
#include <cstdlib> 
#include <chrono>

using namespace std; 

int main(int argc, char * argv[])
{
    if (argc < 2) exit(1); 

    const int order = std::atoi(argv[1]);
    const int length = 1 << order; 
    float* a = new float[length]; 
    float* b = new float[length]; 
    float* w = new float[3]; 

    for (int i = 0; i < 3; i++)
        w[i] = static_cast <float> (rand()) / static_cast <float> (RAND_MAX);

    for (int i = 0; i < length; i++)
        a[i] = static_cast <float> (rand()) / static_cast <float> (RAND_MAX);

    auto start = std::chrono::system_clock::now();

#ifdef OMP
    #pragma omp parallel for
#endif
    for (int i = 1; i < length - 1; i++)
    {
        b[i-1] = a[i-1]*w[0] + a[i]*w[1] + a[i+1]*w[2];
    }
    auto end = std::chrono::system_clock::now();
    std::chrono::duration<double> elapsed_seconds = end-start;
#ifdef OMP
    std::cout<< "test4, omp, " << order << ", " << elapsed_seconds.count() << std::endl;
#else
    std::cout<< "test4, noomp, " << order << ", " << elapsed_seconds.count() << std::endl;
#endif

    return 0;
}
