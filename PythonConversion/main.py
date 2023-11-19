#Flow:
import gurobipy as gp

# #Load instance given parameters
# A1 = 0  # 1=Select arc having the largest uncertainty , 0=Select arc using Lemma2
# A2 = 1  # 1=Partition once per cell , 0=Partition multiple per cell
# A3 = 1  # 1=Split at mean base cost , 0=Split using SA if possible
# A4 = 1  # 1=Frequent solve MP
# # If running A5 = 0, do not use this file, use LazyAlg.jl instead
# # FIXED IN THIS FILE
A5 = 1  # 1=Regular opt model
# set_var = str(A1) + str(A2) + str(A3) + str(A4) + str(A5)
# # Assuming you have a file "functionLoadSharedFiles.py" with the required functions
# exec(open("functionLoadSharedFiles.py").read())

if A5==1: #Solve a regular optimization model
    exec(open("RegOptModel.py").read())
else: #Solve a lazy model
    exec(open("LazyConstraintModel.py").read())


