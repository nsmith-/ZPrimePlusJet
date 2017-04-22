

import ROOT as rt
from tools import *
from array import array

def exec_me(command,dryRun=True):
    print command
    if not dryRun: os.system(command)
##-------------------------------------------------------------------------------------
if __name__ == '__main__':

    import tdrstyle
    tdrstyle.setTDRStyle()
    rt.gStyle.SetPadTopMargin(0.10)
    rt.gStyle.SetPadLeftMargin(0.16)
    rt.gStyle.SetPadRightMargin(0.18)
    rt.gStyle.SetPalette(1)
    rt.gStyle.SetPaintTextFormat("1.1f")
    rt.gStyle.SetOptFit(0000)
    rt.gROOT.SetBatch()
    rt.gStyle.SetOptTitle(0)
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetPalette(rt.kBird)
    rt.gStyle.SetNumberContours(999)

    exec_me('combine -M MultiDimFit --minimizerTolerance 0.001 --minimizerStrategy 2  --setPhysicsModelParameterRanges r=0,5:r_z=0,2 --algo grid --points 100 -d card_rhalphabet_muonCR_floatZ.root -n 2D --saveWorkspace',True)
    c = rt.TCanvas('c','c',500,400)
    
    tfile = rt.TFile.Open('higgsCombine2D.MultiDimFit.mH120.root')
    limit = tfile.Get('limit')
    limit.Draw("r_z:r>>htemp(10,0,8,10,0,2)","deltaNLL*(quantileExpected>-1)","colz")
    contours = array('d',[2.3,5.99])
    htemp = rt.gPad.GetPrimitive('htemp')
    htemp.GetXaxis().SetTitle('#mu')
    htemp.GetYaxis().SetTitle('#mu_{Z}')
    dataTag = 'data'
    htemp.GetZaxis().SetTitle('-2 #Delta log L(%s)'%dataTag)
    htemp.SetMinimum(0.)
    htemp.SetMaximum(16.)
    htemp.DrawCopy("colz")
    htemp.SetContour(1,contours)
    htemp.Draw("cont3 same")
    htemp.SetLineColor(rt.kRed)

    lumi = 35.9
    tag1 = rt.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.04)
    tag2 = rt.TLatex(0.17,0.92,"CMS")
    tag2.SetNDC(); tag2.SetTextFont(62)
    tag3 = rt.TLatex(0.27,0.92,"Preliminary")
    tag3.SetNDC(); tag3.SetTextFont(52)
    tag2.SetTextSize(0.05); tag3.SetTextSize(0.04); tag1.Draw(); tag2.Draw(); tag3.Draw()

    
    c.Print('deltaLL2D.pdf')
    c.Print('deltaLL2D.C')
