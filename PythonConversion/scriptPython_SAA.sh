#!/bin/bash
for N in 30;
do
    for i in {11..150};
    do
        for num_cases in 5000;
        do
            echo "Running N=$N d=$d i=$i "
            gtimeout -k 5 3600 python SAA.py $N $i $num_cases
            # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
            echo "End of 3600 seconds"
        done
    done
done