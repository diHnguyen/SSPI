#!/bin/bash
for N in 30 40 50;
do
    for i in {1..10};
    do
        echo "Running N=$N d=$d i=$i "
        gtimeout -k 5 3600 python SequentialSampling.py $N $i
        # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
        # echo "End of 2 seconds"
    done
done