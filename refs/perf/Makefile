all: 
	g++ -std=c++11 -fopenmp test1.cpp  -o test1
	g++ -std=c++11 -fopenmp test2.cpp  -o test2
	g++ -std=c++11 -fopenmp test3.cpp  -o test3
	g++ -std=c++11 -fopenmp test4.cpp  -o test4
	g++ -std=c++11 -fopenmp -DOMP test1.cpp  -o test1_omp
	g++ -std=c++11 -fopenmp -DOMP test2.cpp  -o test2_omp
	g++ -std=c++11 -fopenmp -DOMP test3.cpp  -o test3_omp
	g++ -std=c++11 -fopenmp -DOMP test4.cpp  -o test4_omp

clean:
	rm -rf test1 test2 test3 test4 test1_omp test2_omp test3_omp test4_omp
