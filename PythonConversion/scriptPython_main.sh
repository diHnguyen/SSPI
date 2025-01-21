#!/bin/bash

#A = (4 8 16 20 28 37 55 64 70 74)
for density in 15;
do
    for N in 50;
    do
        for i in {101..150};#{51..54} {56..63} {65..69};
        do
            echo "Running N=$N density=$density i=$i "
            gtimeout -k 5 3600 python main.py $N $i $density
            # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
            echo "End of 3600 seconds"
        done
    done
done