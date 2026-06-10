#!/bin/bash
# N30: 1 2 5 6 7 8 9 10 11 12
# N30: 4 20 83 89 107 166 172 174 200 241
# N30: 3 35 36 37 52 63 64 150 282 319

# N40: 1 3 5 6 7 9 10 11 12 13 
# N40: 4 8 16 20 27 28 33 36 37 48
# N40: 2 14 18 22 24 38 39 40 56 76

# N50: 2 6 7 10 13 14 15 16 17 21
# N50: 18 26 30 46 73 93 98 110 113 122
# N50: 1 3 4 5 8 9 11 12 19 20

# for num_cases in 1000 10000 ;
# do
#     for density in 15;
#     do
#         for N in 50;
#         do
#             for i in 30;
#             do
#                 for seed in 2024 2025 2006 2007 2008 2009 2010 2011 2012 2013;#$(seq 2006 2013);
#                 do
#                     echo $(date '+%Y-%m-%d %H:%M:%S')
#                     echo "Running N=$N density=$density i=$i seed=$seed num_cases=$num_cases"
#                     gtimeout -k 5 3600 python SAA.py $N $i $density $num_cases $seed
#                     # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
#                     echo "End of 3600 seconds"
#                 done
#             done
#         done
#     done
# done
for seed in 2024 2025 2006 2007 2008 2009 2010 2011 2012 2013; #$(seq 2006 2013);
do
    # for density in 15;
    # do
    #     for N in 30;
    #     do
    #         # for i in 1 2 6 7 8 9 10 20 83 166 172 200 35 37 52 150;
    #         for i in 1 2 5 6 7 8 9 10 11 12 4 20 83 89 107 166 172 174 200 241 3 35 36 37 52 63 64 150 282 319;
    #         #1 2 5 6 7 8 9 10 11 12 4 20 83 89 107 166 172 174 200 241 3 35 36 37 52 63 64 150 282 319;
    #         do
    #             for num_cases in 100;
    #             do
    #                 echo $(date '+%Y-%m-%d %H:%M:%S')
    #                 echo "Running N=$N density=$density i=$i seed=$seed num_cases=$num_cases"
    #                 gtimeout -k 5 3600 python SAA.py $N $i $density $num_cases $seed
    #                 # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
    #                 echo "End of 3600 seconds"
    #             done
    #         done
    #     done
    # done
    for density in 15;
    do
        for N in 40;
        do
            # for i in 1 3 5 7 9 10 11 12 4 2 39 56 76;
            for i in 27 28 33 36 37 48  22 24 38 39 40 56 76
            #1 3 5 6 7 9 10 11 12 13 4 8 16 27 33 36 37 48 64 68 2 14 18 22 24 38 39 40 56 76;
            do
                for num_cases in 100 ;
                do
                    echo $(date '+%Y-%m-%d %H:%M:%S')
                    echo "Running N=$N density=$density i=$i seed=$seed num_cases=$num_cases"
                    gtimeout -k 5 3600 python SAA.py $N $i $density $num_cases $seed
                    # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
                    echo "End of 3600 seconds"
                done
            done
        done
    done
    # for density in 15;
    # do
    #     for N in 50;
    #     do
    #         for i in 2 6 7 10 13 14 15 16 17 21 30 46 93 122 3 12 19;
    #         # for i in 1 4 5 8 9 11 18 20 26 73 98 110 113;
    #         # 2 6 7 10 13 14 15 16 17 21 18 26 46 73 93 98 110 113 122 124 1 3 4 5 8 9 11 12 19 20;
    #         do
    #             for num_cases in 100;
    #             do
    #                 echo $(date '+%Y-%m-%d %H:%M:%S')
    #                 echo "Running N=$N density=$density i=$i seed=$seed"
    #                 gtimeout -k 5 3600 python SAA.py $N $i $density $num_cases $seed
    #                 # gtimeout -k 5 2s sleep $((i*10)) && echo "Hello"
    #                 echo "End of 3600 seconds"
    #             done
    #         done
    #     done
    # done
done
