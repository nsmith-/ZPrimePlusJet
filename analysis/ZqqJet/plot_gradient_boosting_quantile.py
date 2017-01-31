import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingRegressor
#from root_numpy import root2array, rec2array

np.random.seed(1)
f = open("jets.txt")
f.readline()  # skip the header
data = np.loadtxt(f)
lX = np.atleast_2d(data[:, 0:2])
lY = data[:, 2]#np.atleast_2d(data[:, 1]).T
lW = data[:, 3]#np.atleast_2d(data[:, 1]).T
lX = lX.astype(np.float32)
lY = lY.astype(np.float32)
lW = lW.astype(np.float32)
lTX = np.column_stack((np.linspace(500,1000., 1000),np.linspace(-1.5,-6, 1000)))
#lTX = np.atleast_2d(np.linspace(500,1000., 1000)).T
print "Running High",len(lX),len(lY)
alpha = 0.95
clf = GradientBoostingRegressor(loss='quantile', alpha=alpha,n_estimators=250, max_depth=5,learning_rate=.1, min_samples_leaf=9,min_samples_split=9)
clf.fit(lX, lY,lW)

# Make the prediction on the meshed x-axis
lYUp = clf.predict(lTX)

print "Running Low"
clf.set_params(alpha=1.0 - alpha)
clf.fit(lX, lY,lW)
lYLow = clf.predict(lTX)

print "Running Central"
clf.set_params(loss='ls')
clf.fit(lX, lY,lW)
lYPred = clf.predict(lTX)

fig1 = plt.figure()
plt.plot(lX[:,0], lY, 'b.', markersize=10, label=u'Observations')
plt.plot(lTX[:,0],lYPred, 'r-', label=u'Prediction')
plt.plot(lTX[:,0],lYUp  , 'k-')
plt.plot(lTX[:,0],lYLow , 'k-')
plt.fill(np.concatenate([lTX[:,0],lTX[:,0]]),np.concatenate([lYUp, lYLow[::-1]]),alpha=.5, fc='b', ec='None', label='90% prediction interval')
plt.xlabel('$p_{T}$')
plt.ylabel('$n_{2}$')
plt.ylim(0, 1)
plt.legend(loc='upper left')
plt.show()


fig2 = plt.figure()
plt.plot(lX[:,1], lY, 'b.', markersize=10, label=u'Observations')
plt.plot(lTX[:,1],lYPred, 'r-', label=u'Prediction')
plt.plot(lTX[:,1],lYUp  , 'k-')
plt.plot(lTX[:,1],lYLow , 'k-')
plt.fill(np.concatenate([lTX[:,1],lTX[:,1]]),np.concatenate([lYUp, lYLow[::-1]]),alpha=.5, fc='b', ec='None', label='90% prediction interval')
plt.xlabel('$m$')
plt.ylabel('$n_{2}$')
plt.ylim(0, 1)
plt.legend(loc='upper left')
plt.show()
