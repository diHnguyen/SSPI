#!/bin/bash
# For <5 minutes:

# N30: 1 2 5 6 7 8 9 10 11 12 
# N40: 1 3 5 6 7 9 10 11 12 13 
# N50: 2 6 7 10 13 14 15 16 17 21
# For 5-60 minutes:

# N30: 4 20 83 89 107 166 172 174 200 241
# N40: 4 8 16 20 27 28 33 36 37 48
# N50: 18 26 30 46 73 93 98 110 113 122
# For >60 minutes: 

# N30: 3 35 36 37 52 63 64 150 282 319
# N40: 2 14 18 22 24 38 39 40 56 76
# N50: 1 3 4 5 8 9 11 12 19 20

for density in 15;
do
    for N in 30;
    do
        for i in 1 2 5 6 7 8 9 10 11 12 ;
        do
            echo "Running N=$N density=$density i=$i "
            gtimeout -k 5 3600 python main_singleCut_combined_noAltBound_noWarmStart.py $N $i $density
            # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
            echo "End of 3600 seconds"
        done
    done
    for N in 40;
    do
        for i in 1 3 5 6 7 9 10 11 12 13 ;
        do
            echo "Running N=$N density=$density i=$i "
            gtimeout -k 5 3600 python main_singleCut_combined_noAltBound_noWarmStart.py $N $i $density
            # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
            echo "End of 3600 seconds"
        done
    done
    for N in 50;
    do
        for i in 2 6 7 10 13 14 15 16 17 21;
        do
            echo "Running N=$N density=$density i=$i "
            gtimeout -k 5 3600 python main_singleCut_combined_noAltBound_noWarmStart.py $N $i $density
            # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
            echo "End of 3600 seconds"
        done
    done

    for N in 30;
    do
        for i in 4 20 83 89 107 166 172 174 200 241 ;
        do
            echo "Running N=$N density=$density i=$i "
            gtimeout -k 5 3600 python main_singleCut_combined_noAltBound_noWarmStart.py $N $i $density
            # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
            echo "End of 3600 seconds"
        done
    done
    for N in 40;
    do
        for i in 4 8 16 20 27 28 33 36 37 48 ;
        do
            echo "Running N=$N density=$density i=$i "
            gtimeout -k 5 3600 python main_singleCut_combined_noAltBound_noWarmStart.py $N $i $density
            # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
            echo "End of 3600 seconds"
        done
    done
    for N in 50;
    do
        for i in 18 26 30 46 73 93 98 110 113 122;
        do
            echo "Running N=$N density=$density i=$i "
            gtimeout -k 5 3600 python main_singleCut_combined_noAltBound_noWarmStart.py $N $i $density
            # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
            echo "End of 3600 seconds"
        done
    done
done