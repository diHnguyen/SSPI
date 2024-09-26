#!/bin/bash
for N in 30 40 50;
do
    for i in {1..10};
    do
        for num_cases in 500 5000 50000;
        do
            echo "Running N=$N d=$d i=$i "
            gtimeout -k 5 3600 python SAA-AP.py $N $i $num_cases
            # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
            echo "End of 3600 seconds"
        done
    done
done