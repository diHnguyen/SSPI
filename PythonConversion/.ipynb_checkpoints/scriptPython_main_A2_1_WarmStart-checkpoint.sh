#!/bin/bash

for N in 30;
do
    for i in {11..30};
    do
        echo "Running N=$N d=$d i=$i "
        gtimeout -k 5 3600 python main_A2_1_WarmStart.py $N $i
        # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
        echo "End of 3600 seconds"
    done
done
