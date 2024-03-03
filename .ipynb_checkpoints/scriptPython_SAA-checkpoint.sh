#!/bin/bash
for N in 10 100;
do
    for i in {1..5};
    do
        for num_cases in 1000 10000 20000 50000;
        do
            echo "Running N=$N d=$d i=$i "
            gtimeout -k 5 300 python ./PythonConversion/SAA.py $N $i $num_cases
            # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
            echo "End of 2 seconds"
        done
    done
done