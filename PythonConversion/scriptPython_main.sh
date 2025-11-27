#!/bin/bash
# For <5 minutes:

# N30: 1 2 5 6 7 8 9 10 11 12 xxx 
# N40: 1 3 5 6 7 9 10 11 12 13 xxx 
# N50: 2 6 7 10 12 13 14 15 16 17 xxx
# For 5-60 minutes:

# N30: 4 20 37 64 83 107 150 174 258 277 xxx
# N40: 4 8 24 27 37 48 64 68 77 82 xxx
# N50: 3 8 26 27 28 39 41 46 54 73 xxx
# For >60 minutes: 

# N30: 3 35 36 52 63 282 319 334 546 549 
# N40: 2 14 18 22 29 38 39 40 56 76
# N50: 1 4 5 9 11 20 23 32 34 38 

for density in 15;
do
    for N in 30;
    do
        for i in ;
        do
            echo "Running N=$N density=$density i=$i "
            gtimeout -k 5 3600 python main.py $N $i $density
            # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
            echo "End of 3600 seconds"
        done
    done
    for N in 40;
    do
        for i in 39;
        do
            echo "Running N=$N density=$density i=$i "
            gtimeout -k 5 3600 python main_Times.py $N $i $density
            # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
            echo "End of 3600 seconds"
        done
    done
    for N in 50;
    do
        for i in ;
        do
            echo "Running N=$N density=$density i=$i "
            gtimeout -k 5 3600 python main.py $N $i $density
            # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
            echo "End of 3600 seconds"
        done
    done
done