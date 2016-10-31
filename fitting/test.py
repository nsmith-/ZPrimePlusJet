#! /usr/bin/env python
import ROOT as r,sys,math,array
from optparse import OptionParser
from hist import hist

fCut="2.2*scale1fb*(bst8_PUPPIjet0_pt > 500 && bst8_PUPPIjet0_msd > 20)*(bst8_PUPPIjet0_tau21+0.063*bst8_PUPPIjet0_rho < 0.38)"
fVar="bst8_PUPPIjet0_msd"

def parser():
    parser = OptionParser()
    parser.add_option('--input',action='store',type='string',dest='input',default='hists.root',help='input file')
    parser.add_option('--morph',action='store_true',         dest='morph',default=False,       help='morph')
    parser.add_option('--shift',action='store_true',         dest='shift',default=False,       help='shift')
    parser.add_option('--smear',action='store_true',         dest='smear',default=False,       help='smear')
            
    (options,args) = parser.parse_args()
    return options

def end():
    if __name__ == '__main__':
        rep = ''
        while not rep in [ 'q', 'Q','a',' ' ]:
            rep = raw_input( 'enter "q" to quit: ' )
            if 1 < len(rep):
                rep = rep[0]

def makehist(iLabel,iFile):
    lFile = r.TFile(iFile)
    lTree = lFile.Get("otree")
    lH    = r.TH1F(iLabel,iLabel,40,40,240)
    lTree.Draw(fVar+">>"+iLabel,fCut)
    lH.SetDirectory(0)
    return lH

def draw(iLabel,iHists):
    lC0 = r.TCanvas(iLabel,iLabel,800,600)
    iColor=50
    lLegend = r.TLegend(0.7,0.7,0.9,0.9)
    iHists[0].Draw("hist")
    for pHist in iHists:
        pHist.SetLineColor(iColor)
        pHist.Draw("hist sames")
        lLegend.AddEntry(pHist,pHist.GetName(),"l")
        iColor+=10
    lLegend.Draw()
    lC0.Modified()
    lC0.Update()
    end()
    
def load(dir='signals/'):
    lH0 = makehist( 'z50',dir+'ZPrimeToQQ_50GeV_v4_mc.root')
    lH1 = makehist('z100',dir+'ZPrimeToQQ_100GeV_v4_mc.root')
    lH2 = makehist('z150',dir+'ZPrimeToQQ_150GeV_v4_mc.root')
    lH3 = makehist('z200',dir+'ZPrimeToQQ_200GeV_v4_mc.root')
    lH4 = makehist('z250',dir+'ZPrimeToQQ_250GeV_v4_mc.root')
    lH5 = makehist('z300',dir+'ZPrimeToQQ_300GeV_v4_mc.root')
    lH   = [lH0,lH1,lH2,lH3,lH4,lH5]
    lVar = [ 50,100,150,200,250,300]
    return (lVar,lH)

if __name__ == "__main__":
    options = parser()
    #print options
    lVars,lHists = load()
    lHist = hist(lVars,lHists)
    if options.morph:
        lMorph = lHist.morph(150)
        lMorphA = [lHists[1],lMorph,lHists[2]]
        draw("morph",lMorphA)

    if options.shift:
        lShifts = lHist.shift(lHists[2],5.)
        lShiftA = [lHists[2],lShifts[0],lShifts[1]]
        draw("shift",lShiftA)

    if options.smear:
        lSmears = lHist.smear(lHists[2],0.1)
        lSmearA = [lHists[2],lSmears[0],lSmears[1]]
        lHists[2].Fit("gaus")
        lSmears[0].Fit("gaus")
        lSmears[1].Fit("gaus")
        draw("smear",lSmearA)
 

    
