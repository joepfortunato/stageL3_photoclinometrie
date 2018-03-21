import numpy as np
import pylab as plt
import scipy.misc as imageio
from libSFS import *
from scipy.signal import convolve2d
from mpl_toolkits.mplot3d import Axes3D
from numpy.fft import fftshift,fft2,ifft2
#from fonctions_utiles import *
from scipy.fftpack import dct,dst,idct,idst

plt.rcParams["image.cmap"]="gray"
plt.ion()
plt.show()

def build_centered_indices(M,N):
    i = M//2 - (M//2 - np.arange(0,M)) % M  # (0, 1, ..., M/2, -M/2, ..., -1)
    j = N//2 - (N//2 - np.arange(0,N)) % N  # (0, 1, ..., M/2, -M/2, ..., -1)
    return np.meshgrid(i, j)

def inv_cl2(u,alpha,beta,gamma,epsilon):
    u=np.array(u)
    M,N = u.shape
    U = fft2(u)
    U[0,0]=U[0,0]-gamma
    (ii, jj) = build_centered_indices(N,M)
    D = (2*1j*np.pi)*((ii/N)*alpha + (jj/M)*beta) + epsilon*(-4*(np.pi)**2*((ii/N)**2+(jj/M)**2))
    D[0,0]=1
    for h in range(N):
        for k in range(N):
            if D[h,k]==0:
                D[h,k]=1
    X = U/D
    #X=np.real(X)
    
    return np.real(ifft2(X))

def inv_cl_real(u,alpha,beta,gamma):
    u=np.array(u)
    M,N = u.shape
    U = fft2(u)
    U[0,0]=U[0,0]-gamma
    (ii, jj) = build_centered_indices(N,M)
    D = (2*1j*np.pi)*((ii/N)*alpha + (jj/M)*beta)
    D[0,0]=1
    for h in range(N):
        for k in range(N):
            if D[h,k]==0:
                D[h,k]=1
    X = U/D
    X=np.real(X)
    return np.real(ifft2(X))
    
def inv_cl_imag(u,alpha,beta,gamma):
    u=np.array(u)
    M,N = u.shape
    U = fft2(u)
    U[0,0]=U[0,0]-gamma
    (ii, jj) = build_centered_indices(N,M)
    D = (2*1j*np.pi)*((ii/N)*alpha + (jj/M)*beta)
    D[0,0]=1
    for h in range(N):
        for k in range(N):
            if D[h,k]==0:
                D[h,k]=1
    X = U/D
    X=1j*np.imag(X)
    return np.real(ifft2(X))
    
    
def laplacien_per_dft2(u):
    M,N = u.shape
    U = fft2(u);
    (ii, jj) = build_centered_indices(N,M)
    dx = (2j * np.pi / N) * ii
    dy = (2j * np.pi / M) * jj
    dxU = dx**2 * U
    dyU = dy**2 * U
    Du = np.real(ifft2(dxU+dyU))
    return Du
    
# def estimation_volume(I,z,alpha,beta,gamma):
#     V=-gamma*(alpha+beta)/(2*(alpha**2+beta**2))
#     L=laplacien_per_dft2(z)
#     for k in range(N):
#         for m in range(N):
#             V+=((alpha*(1-k/N)+beta*(1-m/N))*I[k,m]-(1-k/N)*(1-m/N)*L[k,m])/(alpha**2+beta**2)
#     return V

## Paramètres de la simulation

nx=128
ny=128
# Paramètres du rayon incident
theta=np.pi/4 # Angle avec la normale -pi/2 < theta < pi/2
phi=np.pi/4
lV=direction_eclairement((theta,phi),(0,0))
(alpha,beta,gamma)=lV
delta=alpha/beta
epsilon=0

Z=generer_surface(Nx=nx, Ny=ny, forme=('cone',50,5), reg = 0)
V=sum(sum(Z))
I=eclairement(Z,lV,np.gradient)
N=I.shape[0]

i=fft2(I)
plt.figure(17)
i=fftshift(i)
plt.imshow(np.log(1+abs(i)))

#(Ix,Iy)=gradient_tfd2(I)
#C=1 #Albedo du matériau, à ajuster avec un exemple réel

## Résolution du problème

z1=inv_cl2(I,alpha,beta,gamma,epsilon) #solution brute
z2=inv_cl2(I,alpha,beta,gamma,epsilon) #solution corrigée (voir plus bas)

for y0 in range(1,N):
    i=0
    debut=z2[0,y0]
    if int(y0+delta*(N-1))<N:
        fin=z2[N-1,int(y0+delta*(N-1))]
        while i<N :
            z2[i,int(y0+delta*i)]=z2[i,int(y0+delta*i)]-(debut+(fin-debut)*(i/(N-1)))
            i=i+1
    else :
        n=int((N-y0)/delta)
        fin=z2[n,N-1]
        while int(y0+delta*i)<N :
            z2[i,int(y0+delta*i)]=z2[i,int(y0+delta*i)]-(debut+(fin-debut)*(i/n))
            i=i+1

for x0 in range(1,N):
    i=0
    debut=z2[x0,0]
    if int(x0+(N-1)/delta)<N:
        fin=z2[N-1,int(x0+(N-1)/delta)]
        while i<N :
            z2[int(x0+i/delta),i]=z2[int(x0+i/delta),i]-(debut+(fin-debut)*(i/(N-1)))
            i=i+1
    else :
        n=int(delta*(N-x0))
        fin=z2[N-1,n]
        if n>0 :
            while int(x0+i/delta)<N :
                z2[int(x0+i/delta),i]=z2[int(x0+i/delta),i]-(debut+(fin-debut)*(i/n))
                i=i+1
                
z2[0:N,0]=0
z2[0:N,N-1]=0
z2[0,0:N]=0
z2[N-1,0:N]=0        

E1=eclairement(z1,[alpha,beta,gamma],np.gradient)
E2=eclairement(z2,[alpha,beta,gamma],np.gradient)
L=laplacien_per_dft2(Z)
L1=laplacien_per_dft2(z1)
L2=laplacien_per_dft2(z2)

V1=np.sum(z1)
V2=np.sum(z2)
# V2p=estimation_volume(I,z2,alpha,beta,gamma)
# Vp=estimation_volume(I,Z,alpha,beta,gamma)
# V1p=estimation_volume(I,z1,alpha,beta,gamma)

print(V)
print(V1)
print(V2)
# print(Vp)
# print(V1p)
# print(V2p)
print(np.abs((V1-V)/V))
print(np.abs((V2-V)/V))
# print(np.abs((Vp-V)/V))
# print(np.abs((V1p-V)/V))
# print(np.abs((V2p-V)/V))

    
## Affichage des résultats

x = np.linspace(-nx/2,nx/2-1,nx)
y = np.linspace(-ny/2,ny/2-1,ny)
X,Y = np.meshgrid(y,x)

fig = plt.figure(1)
ax = fig.gca(projection='3d')
ax.plot_surface(X,Y,z1,rstride=2,cstride=2,linewidth=1)

fig = plt.figure(2)
ax = fig.gca(projection='3d')
ax.plot_surface(X,Y,z2,rstride=2,cstride=2,linewidth=1)

fig = plt.figure(17)
ax = fig.gca(projection='3d')
ax.plot_surface(X,Y,Z,rstride=2,cstride=2,linewidth=1)

plt.figure(5)
plt.imshow(E1)

plt.figure(6)
plt.imshow(E2)

# plt.figure(7)
# plt.imshow(E3)

plt.figure(8)
plt.imshow(I)

# fig = plt.figure(5)
# ax = fig.gca(projection='3d')
# ax.plot_surface(X,Y,Iy,rstride=2,cstride=2,linewidth=1)