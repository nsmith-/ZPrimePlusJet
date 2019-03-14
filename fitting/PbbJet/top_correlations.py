from __future__ import print_function
import ROOT
import sys
import math

def _RooAbsCollection__iter__(self):
    it = self.iterator()
    obj = it.Next()
    while obj != None:
        yield obj
        obj = it.Next()

ROOT.RooAbsCollection.__iter__ = _RooAbsCollection__iter__

fin = ROOT.TFile.Open(sys.argv[-1])
fit_s = fin.Get("fit_s")

chist = fit_s.correlationHist()

corrs = []
for i in range(1, chist.GetNbinsX()+1):
    for j in range(1, chist.GetNbinsY()+1-i):
        xlbl = chist.GetXaxis().GetBinLabel(i)
        ylbl = chist.GetYaxis().GetBinLabel(j)
        cval = chist.GetBinContent(i, j)
        corrs.append((cval, xlbl, ylbl))

corrs.sort(key=lambda x: abs(x[0]), reverse=True)

for c in corrs[:10]:
    print("Corr %.2f %s %s" % c)

magnitude = {}
for param in fit_s.floatParsFinal():
    oom = int(math.log10(abs(param.getError())))
    magnitude[oom] = magnitude.get(oom, 0) + 1

for oom in sorted(magnitude.keys()):
    print("Parameter errors of order 1e%d: %d" % (oom, magnitude[oom]))
