import numpy as np
import ROOT as r
import math
from array import array

def val(iX,fX):
    lDist=10
    lI0=0
    for i0 in range(len(fX)):
        pDist=abs(iX-fX[i0])
        if lDist > pDist:
            lDist=pDist
            lI0=i0
    return lI0

lFile = r.TFile("N2DDT_v2.root")
fX = []
fGraphs = []
lX = []
lY = []
lZ = []
for pGraph in lFile.GetListOfKeys():
    pX = pGraph.GetName().split("_")[1]
    print pX,pGraph.GetName()
    fX.append(float(pX)*-1.)
    pXs = pGraph.ReadObj().GetX()
    pYs = pGraph.ReadObj().GetY()
    pG = pGraph.ReadObj()
    pG.Fit("pol5","Q","R",300,1200)
    pF = pG.GetFunction("pol5")
    pY = []
    pZ = []
    for i0 in range(pGraph.ReadObj().GetN()):
        #print pX,pXs[i0],pYs[i0]
        lX.append(float(pX)*-1.)
        lY.append(pXs[i0])
        lZ.append(pF.Eval(pXs[i0]))
        pY.append(pXs[i0])
        pZ.append(pF.Eval(pXs[i0]))
    pGraph = r.TGraph(len(pY),array('d',pY),array('d',pZ))
    fGraphs.append(pGraph)

lOFile = r.TFile("Output.root","RECREATE")
lGraph2D = r.TGraph2D(len(lX),array('d',lX),array('d',lY),array('d',lZ))
lGraph2D.SetTitle("DDT_rho_pt")
lGraph2D.SetName ("DDT_rho_pt")
lGraph2D.Write()

lN=180
lH2D = r.TH2F("Rho2D","Rho2D",lN,-7,-1.5,lN,200,1200)
lH2D.GetXaxis().SetTitle("#rho")
lH2D.GetYaxis().SetTitle("p_{T} (GeV)")
for i0 in range(lN+1):
    for i1 in range(lN+1):
        print "Interpol:",i0,i1
        lX = lH2D.GetXaxis().GetBinCenter(i0)
        lY = lH2D.GetYaxis().GetBinCenter(i1)
        if lY > 1180:
            lY=1180
        #lH2D.SetBinContent(i0,i1,lGraph2D.Interpolate(lX,lY))
        lH2D.SetBinContent(i0,i1,fGraphs[val(lX,fX)].Eval(lY))

lH2D.Write()
lH2D.Draw("colz")
def end():
    if __name__ == '__main__':
        rep = ''
        while not rep in [ 'q', 'Q','a',' ' ]:
            rep = raw_input( 'enter "q" to quit: ' )
            if 1 < len(rep):
                rep = rep[0]

end()
