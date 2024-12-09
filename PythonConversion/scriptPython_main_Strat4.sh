#!/bin/bash

for N in 30;
do
    for i in 13 14 17 18 19 21 22 25 26 28 29;
    do
        echo "Running N=$N d=$d i=$i "
        gtimeout -k 5 3600 python main_Strat4.py $N $i
        # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
        echo "End of 3600 seconds"
    done
done
