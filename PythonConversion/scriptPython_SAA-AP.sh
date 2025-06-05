#!/bin/bash
#<5min
#N30: 1 2 5 6 7 8 9 10 11 12
#N40: 1 3 5 6 7 9 19 11 12 13
#N50: 2 6 7 10 13 14 15 16 17 21

#5-60min
#N30: 4 20 83 89 107 166 172 174 200 241
#N40: 4 8 16 20 27 28 33 36 37 48
#N50: 18 26 30 46 73 93 98 110 113

#>60min
#N30: 3 35 36 37 52 63 64 150 282 319
#N40: 2 14 18 22 24 38 39 40 56 76
#N50: 1 3 4 5 8 9 11 12 19 20

for density in 15;
do
    for N in 30;
    do
        for i in {1 2 5 6 7 8 9 10 11 12 4 20 83 89 107 166 172 174 200 241 3 35 36 37 52 63 64 150 282 319}; 
        do
            for num_cases in 5000;
            do
                echo "Running N=$N density=$density i=$i "
                gtimeout -k 5 3600 python SAA-AP.py $N $i $density $num_cases
                # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
                echo "End of 3600 seconds"
            done
        done
    done
    for N in 40;
    do
        for i in {1 3 5 6 7 9 19 11 12 13 4 8 16 20 27 28 33 36 37 48 2 14 18 22 24 38 39 40 56 76}; 
        do
            for num_cases in 5000;
            do
                echo "Running N=$N density=$density i=$i "
                gtimeout -k 5 3600 python SAA-AP.py $N $i $density $num_cases
                # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
                echo "End of 3600 seconds"
            done
        done
    done
    for N in 50;
    do
        for i in {2 6 7 10 13 14 15 16 17 21 18 26 30 46 73 93 98 110 113 1 3 4 5 8 9 11 12 19 20}; 
        do
            for num_cases in 5000;
            do
                echo "Running N=$N density=$density i=$i "
                gtimeout -k 5 3600 python SAA-AP.py $N $i $density $num_cases
                # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
                echo "End of 3600 seconds"
            done
        done
    done
done
