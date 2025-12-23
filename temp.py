import numpy as np


"""
Populations
x_i: 1, 2, 3
p_i: 1/3, 1/3, 1/3
mean: 2.0
var: 2/3, 0.6666



"""
rng = np.random.default_rng()
biased_vars = []
vars = []
for i in range(100000):
    samples = rng.integers(low=1, high=3, endpoint=True, size=2)
    biased_vars.append(np.var(samples))
    vars.append(np.var(samples, ddof=1))

print(np.mean(biased_vars))
print(np.mean(vars))