#!/bin/bash

for i in $(seq 2006 2013);
do
    echo $i
    echo $(date '+%Y-%m-%d %H:%M:%S')
done