# -*- coding: utf-8 -*-

import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
from time import clock
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from libSFS import *

t1 = clock()

nx = 64
ny = 64
N = nx * ny

theta = np.pi / 5
phi = np.pi / 3
alpha = np.sin(theta) * np.cos(phi)
beta = np.sin(theta) * np.sin(phi)
gamma = np.cos(theta)
lV = np.array([alpha, beta, gamma])

eps = 0.1

dx = 1
dy = 1

x = np.linspace(-nx / 2, nx / 2 - 1, nx)
y = np.linspace(-ny / 2, ny / 2 - 1, ny)
X, Y = np.meshgrid(y, x)

# Z,E,V = generer_surface(Nx=nx, Ny=ny, forme=('volcan',20,20,0.5,0.2,0.5), reg = 0, lV=(theta,phi),obV=(0,0))
# Z,E,V = generer_surface(Nx=nx, Ny=ny, forme=('trap',80,80,1,0.5), reg=0, lV=(theta,phi),obV=(0,0))
Z, E, V = generer_surface(Nx=nx, Ny=ny, forme=('cone', 20,1), reg=0, lV=(theta, phi), obV=(0, 0))
# Z,E,V = generer_surface(Nx=nx, Ny=ny, forme=('plateau',20,20,1), reg = 0, lV=(theta,phi),obV=(0,0))

E_cp = E.copy()

t2 = clock()

print("surface generee")
print(t2 - t1)

t1 = clock()

# gradient decentre

# Matrice du gradient selon x

M_ii_dx = sp.lil_matrix((ny, ny))
M_ii_dx.setdiag(-1)
M_ii_dx[0, 0] = 1
M_ii_dx[-1, -1] = 1
M_ii_dx = M_ii_dx.tocsr()

M_ij_dx = sp.lil_matrix((ny, ny))
M_ij_dx.setdiag(1)
M_ij_dx[0, 0] = 0
M_ij_dx[-1, -1] = 0
M_ij_dx = M_ij_dx.tocsr()

K_ii_dx = sp.lil_matrix((nx, nx))
K_ii_dx.setdiag(1)
K_ii_dx[0, 0] = 0
K_ii_dx[-1, -1] = 0
K_ii_dx = K_ii_dx.tocsr()

K_ij_dx = sp.lil_matrix((nx, nx))
K_ij_dx.setdiag(1, 1)
K_ij_dx[0, 1] = 0
K_ij_dx = K_ij_dx.tocsr()

K_id = sp.lil_matrix((nx, nx))
K_id[0, 0] = 1
K_id[-1, -1] = 1

M_dx = (sp.kron(K_id, sp.eye(ny)) + sp.kron(K_ii_dx, M_ii_dx) + sp.kron(K_ij_dx, M_ij_dx)) / dx

# Matrice du gradient selon y

M_ii_dy = sp.lil_matrix((ny, ny))
M_ii_dy.setdiag(1, 1)
M_ii_dy.setdiag(-1)
M_ii_dy[0, 0] = 1
M_ii_dy[0, 1] = 0
M_ii_dy[1, 0] = 0
M_ii_dy[-1, -1] = 1
M_ii_dy[-1, -2] = 0
M_ii_dy[-2, -1] = 0
M_ii_dy = M_ii_dy.tocsr()

K_ii_dy = sp.lil_matrix((nx, nx))
K_ii_dy.setdiag(1)
K_ii_dy[0, 0] = 0
K_ii_dy[-1, -1] = 0
K_ii_dy = K_ii_dy.tocsr()

M_dy = (sp.kron(K_id, sp.eye(ny)) + sp.kron(K_ii_dy, M_ii_dy)) / dy

# Matrice du laplacien

M_lap = M_dx.transpose().dot(M_dx) + M_dy.T.dot(M_dy)

# Matrice finale

M = eps * M_lap + alpha * M_dx + beta * M_dy


t2 = clock()

print("matrice formee")
print(t2 - t1)

t1 = clock()

nb_it = 1

compt = 0

Z_appr = np.zeros((nx, ny))

plt.figure(-5)
plt.imshow(E_cp, cmap='gray')

while compt < nb_it:

	compt += 1

	Z_gradx, Z_grady = np.gradient(Z_appr)
	corr = np.sqrt(1 + Z_gradx**2 + Z_grady**2)
	E = E_cp * corr - gamma
	    
	F = np.reshape(E, N)

	F[:ny] = [0] * ny
	F[-ny:] = [0] * ny

	for i in range(1, nx - 1):
	    F[ny * i] = 0
	    F[ny * (i + 1) - 1] = 0

	Z_appr_vect = spsolve(M,F)

	Z_appr_n = np.reshape(Z_appr_vect, (nx, ny))

	E_appr = eclairement(Z_appr_n, lV)

	fig = plt.figure()
	ax = fig.gca(projection='3d')
	ax.plot_surface(X,Y,Z_appr_n,rstride=2,cstride=2,linewidth=1)
	ax.plot_wireframe(X,Y,Z,rstride=2,cstride=2,linewidth=1,color='r')
	plt.title(compt)

	# fig = plt.figure()
	# ax = fig.gca(projection='3d')
	# ax.plot_surface(X,Y,Z_appr_n - Z_appr,rstride=2,cstride=2,linewidth=1)
	# plt.title(10*compt +1)
	
	E_appr = (E_appr - np.min(E_appr))/(np.max(E_appr)-np.min(E_appr))

	plt.figure(100*compt)
	plt.imshow(E_appr,cmap='gray')

	print(comparer_eclairement(E_cp,E_appr))
	Z_appr = Z_appr_n
	V_appr = np.sum(Z_appr)
	print(V, V_appr, np.abs(V - V_appr) / V)

t2 = clock()

print("affichage ok")
print(t2 - t1)

plt.show()
