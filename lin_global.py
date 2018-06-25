# -*- coding: utf-8 -*-

import scipy.sparse as sp
from scipy.sparse.linalg import spsolve, eigs, norm
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from libSFS import *
import scipy.misc as io
from numpy.linalg import solve

nx = 126
ny = 200

# nx = 128
# ny = 128
N = nx * ny

theta = np.pi / 3
phi = np.pi / 2.7

# theta = np.pi / 8
# phi = np.pi / 4

theta_obs = 0
phi_obs = 0
lV = direction_eclairement((theta, phi), (theta_obs, phi_obs))
alpha, beta, gamma = lV

eps = 0.1

dx = 1
dy = 1

nb_it = 10


x = np.linspace(0, np.pi, nx)
y = np.linspace(0, np.pi, ny)
X, Y = np.meshgrid(y, x)

Dx_ii = sp.lil_matrix((ny, ny))
Dx_ii.setdiag(-1.0 / dx)
Dx_ii.setdiag(1.0 / dx, 1)
Dx_ii = Dx_ii.tocsr()

Kx_ii = sp.eye(nx)
Kx_ii = Kx_ii.tocsr()

Dx = sp.kron(Kx_ii, Dx_ii)
Dx = Dx.tocsr()

Dy_ii = sp.eye(ny) * (-1 / dy)
Dy_ii = Dy_ii.tocsr()

Ky_ii = sp.eye(nx)
Ky_ii = Ky_ii.tocsr()

Dy_ij = sp.eye(ny) / dy
Dy_ij = Dy_ij.tocsr()

Ky_ij = sp.lil_matrix((nx, nx))
Ky_ij.setdiag(1, 1)
Ky_ij = Ky_ij.tocsr()

Dy = sp.kron(Ky_ii, Dy_ii) + sp.kron(Ky_ij, Dy_ij)
Dy = Dy.tocsr()

Lap = -(Dx.T.dot(Dx) + Dy.T.dot(Dy))
Lap = Lap.tocsr()

M = alpha * Dx + beta * Dy + eps * Lap
M = M.tocsr()


def grad(U): return (Dx.dot(U), Dy.dot(U))

# Z_mat = generer_surface(Nx=nx, Ny=ny, forme=('volcan',50,50,0.5,0.2,0.5), reg = 0)
# Z_mat = generer_surface(Nx=nx, Ny=ny, forme=('trap',30,100,1,0.5), reg=0)
# Z_mat = generer_surface(Nx=nx, Ny=ny, forme=('cone', 50, 10), reg=0)
# Z_mat = generer_surface(Nx=nx, Ny=ny, forme=('plateau',20,20,1), reg = 0)

# Z = np.reshape(Z_mat, N)
# E = eclairement(Z, lV, grad)
# E_cp = E.copy()
# E_cp_mat = np.reshape(E_cp, (nx, ny))

# V = np.sum(Z)

E_cp_mat = io.imread('img/1/non_sym.png', 'L')
E_cp_mat = (E_cp_mat - np.min(E_cp_mat))/(np.max(E_cp_mat) - np.min(E_cp_mat))

mask = io.imread('img/1/non_sym_mask.png', 'L')
mask = 1 - (mask - np.min(mask))/(np.max(mask) - np.min(mask))

E_cp_mat = E_cp_mat * mask

E_cp_mat[np.where(E_cp_mat == 0)] = 0.5
E = np.reshape(E_cp_mat, N)
E_cp = E.copy()

compt = 0

Z_appr = np.zeros(N)

while compt < nb_it:
	compt += 1

	Z_gradx, Z_grady = grad(Z_appr)
	corr = np.sqrt(1 + Z_gradx**2 + Z_grady**2)
	E = E_cp * corr - gamma

	Z_appr = spsolve(M.T.dot(M), M.T.dot(E).T)

	E_appr = eclairement(Z_appr, lV, grad)
	Z_appr_mat = np.reshape(Z_appr, (nx, ny))
	E_appr_mat = np.reshape(E_appr, (nx, ny))

	Z_appr_mat = mask * Z_appr_mat
	Z_appr = np.reshape(Z_appr_mat, N)

fig = plt.figure(10 * compt)
ax = fig.gca(projection='3d')
ax.axis('off')
ax.set_zlim3d(-2,30)
ax.plot_wireframe(X, Y, Z_mat, rstride=5, cstride=5, linewidth=1, color='r')
ax.plot_surface(X, Y, (Z_appr_mat * (Z_appr_mat >= 0))[::-1,:], rstride=1, cstride=1, linewidth=0, color='#acc2d9')

plt.show()