# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from libSFS import direction_eclairement, generer_surface, eclairement, points_critiques, height, comp_connexes, rearrange
from time import clock
from copy import deepcopy

plt.ion()
plt.show()
plt.rcParams["image.cmap"]="gray"

## Fonctions utiles

def g(a,b,c,d): # gradient
    return np.sqrt(max(a,b,0)**2+max(c,d,0)**2)

def f(U,n,dx,dy): # on cherche z(x,y) tel que le gradient obtenu (par rapport à l'ancienne surface) convienne
    v=min(U)
    c=g((v-U[0])/dx,(v-U[1])/dx,(v-U[2])/dy,(v-U[3])/dy)-n
    while abs(c)>delta :
        v=v-c
        c=g((v-U[0])/dx,(v-U[1])/dx,(v-U[2])/dy,(v-U[3])/dy)-n
    return v
    
def reg(Z):
    r=0
    (Zx,Zy)=np.gradient(Z)
    Zxx=np.gradient(Zx)[0]
    Zyy=np.gradient(Zy)[0]
    for x in range(nx):
        for y in range(ny):
            r = r + Zxx[x,y]**2 + Zyy[x,y]**2
    return r
    
def FMM(I,z0,dx,dy,masque):
    delta=0.0001
    (nx,ny)=I.shape
    n=np.zeros((nx,ny)) # n(x,y) est la fonction qui est égale à la norme du gradient
    z=deepcopy(z0)
    CB=[z0[:,0],z0[:,ny-1],z0[0,:],z0[nx-1,:]]
    for x in range(1,nx-1):
        for y in range(1,ny-1):
            n[x,y]=np.sqrt(1/I[x,y]**2-1)
    Q=points_critiques(I)
    Q_bis=deepcopy(Q)
    Q_bis=(Q_bis+masque)>0
    Q_bis[:,0]=np.ones(nx)
    Q_bis[:,ny-1]=np.ones(nx)
    Q_bis[0,:]=np.ones(ny)
    Q_bis[nx-1,:]=np.ones(ny)
    CC=comp_connexes(Q)
    P=np.ones(len(CC))
    V=np.zeros(len(CC))
    CC=rearrange(CC)
    for i in range(len(CC)): # on calcule la hauteur sur chaque plateau
        V[i]=height(i,Q,V,CC,n,CB,P)
    for i in range(len(CC)): # on impose la hauteur sur chaque plateau
        for x in range(nx):
            for y in range(ny):
                if CC[i,x,y]==1:
                    z0[x,y]=V[i]
                    z[x,y]=z0[x,y]
    T=deepcopy(Q_bis)
    i=0
    while (T!=1).any(): # génération de la solution
        for x in range(1,nx-1):
            for y in range(1,ny-1):
                if T[x,y]==0:
                    U=[z0[x-1,y],z0[x+1,y],z0[x,y-1],z0[x,y+1]]
                    z[x,y]=f(U,n[x,y],dx,dy)
                if z[x,y]==z0[x,y]:
                    T[x,y]=1
        for x in range(1,nx-1):
            for y in range(1,ny-1):
                if T[x,y]==0:
                    z0[x,y]=z[x,y]
        i=i+1
    return z

def rotation_Z(Z, theta):
    Z_rot = np.zeros((3,nx,ny))
    for i in range(nx):
        for j in range(ny):
            Z_rot[0][i,j] = Z[0][i,j] * np.cos(theta) - Z[2][i,j] * np.sin(theta)
            Z_rot[1][i,j] = Z[1][i,j]
            Z_rot[2][i,j] = Z[0][i,j] * np.sin(theta) + Z[2][i,j] * np.cos(theta)
    return Z_rot

def regularisation_maillage(X,Y,Z):
    minMeshX = np.min(X)
    maxMeshX = np.max(X)
    minMeshY = np.min(Y)
    maxMeshY = np.max(Y)
    x_mesh_reg = np.linspace(minMeshX, maxMeshX, nx)
    y_mesh_reg = np.linspace(minMeshY, maxMeshY, ny)
    X_reg,Y_reg = np.meshgrid(y_mesh_reg, x_mesh_reg)

    Z_reg = np.zeros((nx, ny))

    for i in range(nx):
        for j in range(ny):
            distArray = (X_reg[i,j] - X) ** 2 + (Y_reg[i,j] - Y) ** 2
            indX, indY = np.unravel_index(np.argsort(distArray, axis=None), (nx,ny))
            Z_reg[i,j] = np.sum(Z[indX[:4], indY[:4]])/ 4
    return Z_reg

## Parametres du probleme

# nx = 32
# ny = 32

delta=0.01
theta = np.pi/10
phi = np.pi/2
theta_obs = 0
phi_obs = 0
lV = direction_eclairement((theta, phi), (theta_obs, phi_obs))
(alpha, beta, gamma) = lV
CB=np.array([np.zeros(nx),np.zeros(nx),np.zeros(ny),np.zeros(ny)]) # Conditions de bord du problème
dx=1
dy=1
dx_rot=1/np.cos(theta)

x_mesh = np.linspace(-(nx-1)/2, (nx-1)/2, nx)
y_mesh = np.linspace(-(ny-1)/2, (ny-1)/2, ny)
X,Y = np.meshgrid(y_mesh,x_mesh)

Z = generer_surface(Nx=nx, Ny=ny, forme=('cone',30,15), reg=0)
# Z = generer_surface(Nx=nx, Ny=ny, forme=('trap',10,20,5,10), reg = 0)
# Z = generer_surface(Nx=nx, Ny=ny, forme=('plateau',20,20,5), reg = 1)

V=np.sum(Z)
I=eclairement(Z,lV,np.gradient)

##

cond=(I < (alpha ** 2 + beta ** 2)**.5)

if cond.any():
    print("Peut-être pas possible")
else :
    print("OK")

plt.figure(9)
plt.imshow(cond)

masque = np.zeros((nx,ny)) 
for i in range(nx): 
    for j in range(ny): 
        if np.sqrt((nx/2-i)**2+(ny/2-j)**2)>30: 
            masque[i,j]=1

plt.figure(7)
plt.imshow(masque)

Z1=np.zeros((nx,ny))

Z_mesh = np.array([X,Y,Z1])
Z_rot = rotation_Z(Z_mesh, -theta)

x_mesh_reg = np.linspace(np.min(Z_rot[1]), np.max(Z_rot[1]), nx)
y_mesh_reg = np.linspace(np.min(Z_rot[0]), np.max(Z_rot[0]), ny)
X_reg,Y_reg = np.meshgrid(y_mesh_reg, x_mesh_reg)

for i in range(6):
    
    # Z1  ->  Z_n    
    Z_mesh = np.array([X,Y,Z1])
    Z_rot = rotation_Z(Z_mesh, -theta)
    Z_reg = regularisation_maillage(Z_rot[0],Z_rot[1],Z_rot[2])
    # Z_reg  ->  Z_n_tilde
    Z0 = np.zeros((nx,ny))
    
    Z0_mesh = np.array([X,Y,Z0])
    Z0_rot = rotation_Z([X,Y,Z0], -theta)
    Z0_reg = regularisation_maillage(Z0_rot[0],Z0_rot[1],Z0_rot[2])
    
    
    masque_rot_reg = regularisation_maillage(Z_rot[0],Z_rot[1],masque)
    I_rot_reg = regularisation_maillage(Z_rot[0],Z_rot[1],I)
    
    z = FMM(I_rot_reg,Z0_reg,dx_rot,dy,masque_rot_reg)

    # z  ->  Z_n+1_tilde

    
    Z_mesh = np.array([X_reg,Y_reg,z])
    Z_rot = rotation_Z(Z_mesh, theta)
    Z1 = regularisation_maillage(Z_rot[0],Z_rot[1],Z_rot[2])
    print(i)
    

I_sim = eclairement(Z1,lV,np.gradient)

fig = plt.figure(1)
ax = fig.gca(projection='3d')
plt.axis('off')
ax.plot_surface(X, Y, Z1, rstride=1, cstride=1, linewidth=0, color='#acc2d9')
ax.plot_wireframe(X, Y, Z, rstride=5, cstride=5, linewidth=1, color='r')

plt.figure(2)
plt.imshow(I)

plt.figure(4)
plt.imshow(I_rot_reg)

plt.figure(5)
plt.imshow(I_sim)

plt.show()

v=np.sum(Z1)
print(abs(v-V)/V)

print(comparer_eclairement(I, I_sim))
