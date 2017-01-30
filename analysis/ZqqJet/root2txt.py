import numpy as np
import ROOT as r
import math

lFile = r.TFile("QCDShort.root")
lTree = lFile.Get("otree")

for i0 in range(lTree.GetEntriesFast()):
    lTree.GetEntry(i0)
    if np.isnan(lTree.AK8Puppijet0_N2sdb1):
        continue
    print lTree.AK8Puppijet0_pt,2*math.log(lTree.AK8Puppijet0_msd/lTree.AK8Puppijet0_pt),lTree.AK8Puppijet0_N2sdb1,lTree.scale1fb*lTree.puWeight
    #if i0 > 1000000: 
    #    break

