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
    float* c = new float[length]; 
    float* d = new float[length]; 

    for (int i = 0; i < length; i++)
    {
        a[i] = static_cast <float> (rand()) / static_cast <float> (RAND_MAX);
        b[i] = static_cast <float> (rand()) / static_cast <float> (RAND_MAX);
        c[i] = static_cast <float> (rand()) / static_cast <float> (RAND_MAX);
    }

    auto start = std::chrono::system_clock::now();
#ifdef OMP
    #pragma omp parallel for
#endif
    for (int i = 0; i < length; i++)
    {
        d[i] = (a[i] + b[i] * c[i]) / (a[i] * b[i] * c[i]);
    }
    auto end = std::chrono::system_clock::now();
    std::chrono::duration<double> elapsed_seconds = end-start;
#ifdef OMP
    std::cout<< "test3, omp, " << order << ", " << elapsed_seconds.count() << std::endl;
#else
    std::cout<< "test3, noomp, " << order << ", " << elapsed_seconds.count() << std::endl;
#endif

    return 0;
}
