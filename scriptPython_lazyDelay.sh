#!/bin/bash
for N in 10 100;
do
    for i in {1..5};
    do
        echo "Running N=$N d=$d i=$i "
        gtimeout -k 5 3600 python ./PythonConversion/LazyConstraintModel_DelaySP.py $N $i $num_cases
        # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
        echo "End of 3600 seconds"
    done
done