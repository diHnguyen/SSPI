#!/bin/bash
for N in 50 30;
do
    for d in 30 20;
    do
        for i in {1..20};
        do
            echo "Running N=$N d=$d i=$i "
            gtimeout -k 5 900 julia /Users/dinguyen/Desktop/Paper5/MainAlg.jl $N $d $i
            # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
            echo "End of 2 seconds"
        done
    done
done