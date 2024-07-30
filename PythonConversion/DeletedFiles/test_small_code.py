import numpy as np

a = np.array([])

for i in range(2):
    for j in range(2):
        a = np.append(a,[i,j])
a = np.reshape(a,(4,2))
print(a)
b = [0,1]
print((b == a).all(1).any())