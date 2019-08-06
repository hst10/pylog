#!/bin/bash

for i in {1..4}
do
    for order in {16..22}
    do
        for time in {1..5}
        do
            python test$i.py $order >> results_test$i.csv
            echo "python test$i.py $order >> results_test$i.csv"
        done

        for time in {1..5}
        do
            ./test$i $order >> results_test$i.csv
            echo "./test$i $order >> results_test$i.csv"
        done

        for time in {1..5}
        do
            ./test$i\_omp $order >> results_test$i.csv
            echo "./test$i\_omp $order >> results_test$i.csv"
        done
    done
done
