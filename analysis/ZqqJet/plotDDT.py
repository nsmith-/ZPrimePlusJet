import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
from array import array
import math
import sys
import time

##############################################################################
def main(options,args):
    
    
    c_ptH = ROOT.TCanvas("c_ptH","c_ptH",800,600)
    file_in = ROOT.TFile.Open("h3_n2ddt_26eff_36binrho11pt_Spring16.root")
    file_in.cd()
    
    tt = file_in.Get('h2ddt').Clone()
    
    tt.Draw('COLZ')
    tt.SetContour(999)
    ROOT.gPad.Update()
    #c_ptH.cd()
    #tt.GetXaxis().SetTitle('#rho = ln(m_{SD}^{2}/p_{T}^{2})')
    tt.GetXaxis().SetTitle('#rho')
    tt.GetYaxis().SetTitle('p_{T} (GeV)')
    tt.GetXaxis().SetTitleSize(0.05)
    tt.GetYaxis().SetTitleSize(0.05)
    tt.GetXaxis().SetTitleOffset(1)
    tt.GetYaxis().SetTitleOffset(1.2)
    tt.GetXaxis().SetLabelSize(0.045)
    tt.GetYaxis().SetLabelSize(0.045)
    tt.GetZaxis().SetLabelSize(0.045)
    tt.GetZaxis().SetTitleSize(0.05)
    tt.GetZaxis().SetTitleOffset(1.2)
    tt.GetZaxis().SetTitle('N_{2}^{1} cut at 26% QCD eff')
    palette = ROOT.TPaletteAxis(-1.45,450,-1.1,1000,tt)
    tt.Draw('COL')
    palette.Draw()
    tag1 = ROOT.TLatex(0.67, 0.92, "35.9 fb^{-1} (13 TeV)")
    tag1.SetNDC()
    tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag2 = ROOT.TLatex(0.17, 0.92, "CMS")
    tag2.SetTextSize(0.055)
    tag2.SetNDC()
    tag2.SetTextFont(62)
    tag3 = ROOT.TLatex(0.27, 0.92, "Simulation Preliminary")
    tag3.SetNDC()
    tag3.SetTextFont(52)
    tag2.SetTextSize(0.055)
    tag3.SetTextSize(0.045)
    #tag1.Draw()
    tag2.Draw()
    tag3.Draw()

    c_ptH.SaveAs("DDT.pdf");
    c_ptH.SaveAs("DDT.C");
    c_ptH.SaveAs("DDT.png");

##----##----##----##----##----##----##
if __name__ == '__main__':
    parser = OptionParser()

    (options, args) = parser.parse_args()

    import tdrstyle
    tdrstyle.setTDRStyle()
    ROOT.gStyle.SetPadTopMargin(0.10)
    ROOT.gStyle.SetPadLeftMargin(0.16)
    ROOT.gStyle.SetPadRightMargin(0.18)
    ROOT.gStyle.SetPaintTextFormat("1.1f")
    ROOT.gStyle.SetOptStat(0000)
    ROOT.gStyle.SetOptFit(0000)
    ROOT.gROOT.SetBatch()
    #ROOT.gStyle.SetPalette(ROOT.kBlackBody)
    #ROOT.gStyle.SetPalette(ROOT.kBird)    
    stops = [ 0.0, 1.0]
    red =   [ 1.0, 0.3]
    green = [ 1.0, 0.3]
    blue =  [ 1.0, 1.0]

    s = array('d', stops)
    r = array('d', red)
    g = array('d', green)
    b = array('d', blue)

    npoints = len(s)
    ROOT.TColor.CreateGradientColorTable(npoints, s, r, g, b, 999)

    ROOT.gStyle.SetNumberContours(999)

    main(options,args)
##----##----##----##----##----##----##

