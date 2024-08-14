#!/bin/bash
for N in 10 100;
do
    for i in {1..5};
    do
        echo "Running N=$N d=$d i=$i "
        gtimeout -k 5 3600 python ./PythonConversion/VerifySolQual_V2.py $N $i 50000
        # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
        # echo "End of 2 seconds"
    done
done