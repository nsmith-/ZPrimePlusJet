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
    file_in = ROOT.TFile.Open("h3_n2ddt_26eff_36binrho11pt_Spring16.root");
    file_in.cd()
    tt = file_in.Get('h2ddt')


    c_ptH = ROOT.TCanvas("c_ptH","c_ptH",800,800);

    c_ptH.cd();
    ROOT.gStyle.SetPalette(ROOT.kBlackBody);
    tt.GetXaxis().SetTitle('#rho = ln(m_{SD}^{2}/p_{T}^{2})')
    tt.GetYaxis().SetTitle('p_{T} (GeV)')
    tt.GetXaxis().SetTitleSize(0.043)
    tt.GetYaxis().SetTitleSize(0.043)
    tt.GetXaxis().SetTitleOffset(1)
    tt.GetYaxis().SetTitleOffset(1.2)
    tt.GetXaxis().SetLabelSize(0.03)
    tt.GetYaxis().SetLabelSize(0.03)
    tt.GetZaxis().SetLabelSize(0.025)
    tt.GetZaxis().SetTitleSize(0.04)
    tt.GetZaxis().SetTitleOffset(1.2)
    tt.GetZaxis().SetTitle('N_{2}^{1} cut at 26% QCD eff')
    ROOT.gStyle.SetNumberContours(999)
    palette = ROOT.TPaletteAxis(-1.74753,450.4435,-1.501524,1000.444,tt);
    tt.Draw('COL')
    palette.Draw()
    tag1 = ROOT.TLatex(0.67, 0.92, "35.9 fb^{-1} (13 TeV)")
    tag1.SetNDC();
    tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag2 = ROOT.TLatex(0.17, 0.92, "CMS")
    tag2.SetNDC()
    tag2.SetTextFont(62)
    tag3 = ROOT.TLatex(0.3, 0.92, "Simulation Preliminary")
    tag3.SetNDC()
    tag3.SetTextFont(52)
    tag2.SetTextSize(0.05)
    tag3.SetTextSize(0.04)
#    tag1.Draw()
    tag2.Draw()
    tag3.Draw()

    c_ptH.SaveAs("DDT.pdf");
    c_ptH.SaveAs("DDT.png");

##----##----##----##----##----##----##
if __name__ == '__main__':
    parser = OptionParser()

    (options, args) = parser.parse_args()

    #import tdrstyle
    #tdrstyle.setTDRStyle()
    ROOT.gStyle.SetPadTopMargin(0.10)
    ROOT.gStyle.SetPadLeftMargin(0.16)
    ROOT.gStyle.SetPadRightMargin(0.10)
    ROOT.gStyle.SetPalette(1)
    ROOT.gStyle.SetPaintTextFormat("1.1f")
    ROOT.gStyle.SetOptStat(0000)
    ROOT.gStyle.SetOptFit(0000)
    ROOT.gROOT.SetBatch()

    main(options,args)
##----##----##----##----##----##----##

