#!/bin/bash
# For <5 minutes:

# N30: 1 2 5 6 7 8 9 10 11 12 xxx 
# N30: 4 20 37 64 83 107 150 174 258 277 xxx
# N30: 3 35 36 52 63 282 319 334 546 549 

# N40: 1 3 5 6 7 9 10 11 12 13 xxx 
# N40: 4 8 24 27 37 48 64 68 77 82 xxx
# N40: 2 14 18 22 29 38 39 40 56 76

# N50: 2 6 7 10 12 13 14 15 16 17 xxx
# N50: 3 8 26 27 28 39 41 46 54 73 xxx
# N50: 1 4 5 9 11 20 23 32 34 38 

#Use this: 
# N30   
# 1 2 5 6 7 8 9 10 11 12  
# 4 20 83 99 107 166 172 174 200 241  
# 3 35 36 37 52 63 64 150 282 319

# N40   
# 1 3 5 6 7 9 10 11 12 13  
# 4 8 16 27 33 36 37 48 64 68  
# 2 14 18 22 24 38 39 40 56 76

# N50   
# 2 6 7 10 13 14 15 16 17 21  
# 18 26 46 73 93 98 110 113 122 124  
# 1 3 4 5 8 9 11 12 19 20


for density in 15;
do
    for N in 30;
    do
        for i in 99 166 172 200 241;
        do
            for num_cases in 1000 10000 100000;
            do
                echo "Running N=$N density=$density i=$i "
                gtimeout -k 5 3600 python SAA.py $N $i $density $num_cases
                # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
                echo "End of 3600 seconds"
            done
        done
    done
done
for density in 15;
do
    for N in 40;
    do
        for i in 16 33 36 ;
        do
            for num_cases in 1000 10000 100000;
            do
                echo "Running N=$N density=$density i=$i "
                gtimeout -k 5 3600 python SAA.py $N $i $density $num_cases
                # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
                echo "End of 3600 seconds"
            done
        done
    done
done
for density in 15;
do
    for N in 50;
    do
        for i in 21 18 93 98 110 113 122 124 19;
        do
            for num_cases in 1000 10000 100000;
            do
                echo "Running N=$N density=$density i=$i "
                gtimeout -k 5 3600 python SAA.py $N $i $density $num_cases
                # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
                echo "End of 3600 seconds"
            done
        done
    done
done
