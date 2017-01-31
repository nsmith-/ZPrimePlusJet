import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor
#from root_numpy import root2array, rec2array

np.random.seed(1)
f = open("jets.txt")
f.readline()  # skip the header
data = np.loadtxt(f)
lX = np.atleast_2d(data[:, 0:2])
lY = data[:, 2]
lW = data[:, 3]
lX = lX.astype(np.float32)
lY = lY.astype(np.float32)
lW = lW.astype(np.float32)
lN=500
lTRho0 =  np.linspace(-1.5,-6, lN)
lTPt   =  np.array(())
lTRho  =  np.array(())
for i0 in range(lN):
    print i0
    pTPt  =  np.linspace(500,1000., lN)
    pTRho =  np.linspace(lTRho0[i0],lTRho0[i0],lN)
    lTPt  = np.append(lTPt, pTPt)
    lTRho = np.append(lTRho,pTRho)
lTX = np.column_stack((lTPt,lTRho))
print "Running High",len(lX),len(lY)
alpha = 0.05
clf = GradientBoostingRegressor(loss='quantile', alpha=alpha,n_estimators=250, max_depth=5,learning_rate=.1, min_samples_leaf=9,min_samples_split=9)
clf.fit(lX, lY,lW)
lYUp = clf.predict(lTX)
for i0 in range(len(lYUp)):
    print lTX[i0,0],lTX[i0,1],lYUp[i0]
