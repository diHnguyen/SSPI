import numpy as np

print("Running testInstance")
edge = np.array([[0, 1], [0, 2], [1, 2], [1, 3], [2, 3]])
cL_orig = np.array([0.0, 8, 11, 4, 0])
cU_orig = np.array([0.0, 12, 11, 20, 0])
d = np.array([0.0, 1, 0, 8, 0])
Len = len(cL_orig)
c_orig = 0.5 * (cL_orig + cU_orig)
yy = np.zeros(Len)
yy = [1, 0, 0, 1, 0]
SP_init = sum(yy[i] * c_orig[i] for i in range(0, Len))
p = [1.0]
g = [SP_init]
h = [0.0]
origin = 0
destination = 3
last_node = np.max(edge)
all_nodes = list(range(1, last_node + 1))
M_orig = np.zeros(Len)
for i in range(Len):
    M_orig[i] = cU_orig[i] - cL_orig[i]
delta1 = 1.0
delta2 = 1.0
b = 1
last_node = np.max(edge)
β = 0.253
print(c_orig)
