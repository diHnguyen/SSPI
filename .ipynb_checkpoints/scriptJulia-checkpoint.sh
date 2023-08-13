#!/bin/bash
for i in {1..2}
do
    echo "Welcome $i times"
    gtimeout -k 5 10s julia /Users/dinguyen/Library/CloudStorage/GoogleDrive-di.hoai.nguyen@gmail.com/Other\ computers/My\ Laptop/Documents/GitHub/Paper5/LazyAlg.jl 30 30 $i
    # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
    echo "End of 2 seconds"
done