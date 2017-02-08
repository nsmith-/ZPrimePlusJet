import numpy as np
import ROOT as r
import math
from array import array

lFile = r.TFile("N2DDT.root")
lX = []
lY = []
lZ = []
for pGraph in lFile.GetListOfKeys():
    pX = pGraph.GetName().split("_")[1]
    print pX,pGraph.GetName()
    pXs = pGraph.ReadObj().GetX()
    pYs = pGraph.ReadObj().GetY()
    for i0 in range(pGraph.ReadObj().GetN()):
        #print pX,pXs[i0],pYs[i0]
        lX.append(float(pX)*-1.)
        lY.append(pXs[i0])
        lZ.append(pYs[i0])

lOFile = r.TFile("Output2.root","RECREATE")
lGraph2D = r.TGraph2D(len(lX),array('d',lX),array('d',lY),array('d',lZ))
lGraph2D.SetTitle("DDT_rho_pt")
lGraph2D.SetName ("DDT_rho_pt")
lGraph2D.Write()

lN=100
lH2D = r.TH2F("Rho2D","Rho2D",lN,-7,-1.0,lN,450,1200)
lH2D.GetXaxis().SetTitle("#rho")
lH2D.GetYaxis().SetTitle("p_{T} (GeV)")
for i0 in range(lN+1):
    for i1 in range(lN+1):
        print "Interpol:",i0,i1
        lX = lH2D.GetXaxis().GetBinCenter(i0)
        lY = lH2D.GetYaxis().GetBinCenter(i1)
        lH2D.SetBinContent(i0,i1,lGraph2D.Interpolate(lX,lY))

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
