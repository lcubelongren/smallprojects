
# https://math.stackexchange.com/questions/4373805/solving-the-two-body-problem-numerically-in-python

import numpy as np
from scipy.integrate import solve_ivp, odeint
import matplotlib.pyplot as plt


G = 6.674e-11

time = np.arange(0, 1e2, 1)

M = 1e24  # mass (kg)
r0 = np.array([0, 1e5, 0])  # initial position (m)
v0 = np.array([0, 0, 0])  # initial velocity (m/s)

r_mag = np.linalg.norm(r0)  # magnitude of position vector from r1 to r2

# initial conditions
a0 = np.concatenate((r0, v0))

def two_body_eqm(t, a, G, M):
    x, y, z = a[:3]
    u, v, w = a[3:]
    x += 0
    print(x, y, z, u, v, w)
    r_mag = np.linalg.norm([x, y, z])
    c = G * M * np.array([x, y, z]) / np.power(r_mag, 3)
    return np.concatenate(([u, v, w], c))


A = np.zeros((len(time)+1, 6))
A[0] = a0
for i,t in enumerate(time):
    A[i+1] = two_body_eqm(t+1, A[i], G, M)


plt.figure()
plt.plot(A[:,0])
plt.plot(A[:,1])
plt.show()

plt.figure()
#lim = np.max(y[:,:6]) * 1.1
lim = 1e9
plt.xlim([-lim, lim])
plt.ylim([-lim, lim])
plt.scatter(0, 0, c='k', s=100)
plt.scatter(r0[0], r0[1], c='b', s=1)
plt.plot(A[:,0], A[:,1], c='r')
plt.show()
