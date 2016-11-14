import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array

##############################################################################
def main(options,args):

    h_lo_ptH = makeHistFromTextInput("dat_vbfn3lo/LO_ptH.dat","h_lo_ptH");
    h_nlo_ptH = makeHistFromTextInput("dat_vbfn3lo/NLO_ptH.dat","h_nlo_ptH");
    h_nnlo_ptH = makeHistFromTextInput("dat_vbfn3lo/NNLO_ptH.dat","h_nnlo_ptH");
    h_nnnlo_ptH = makeHistFromTextInput("dat_vbfn3lo/NNNLO_ptH.dat","h_nnnlo_ptH");

    # h_lo_yH = makeHistFromTextInput("dat_vbfn3lo/LO_yH.dat","h_lo_yH");
    # h_nlo_yH = makeHistFromTextInput("dat_vbfn3lo/NLO_yH.dat","h_nlo_yH");
    # h_nnlo_yH = makeHistFromTextInput("dat_vbfn3lo/NNLO_yH.dat","h_nnlo_yH");
    # h_nnnlo_yH = makeHistFromTextInput("dat_vbfn3lo/NNNLO_yH.dat","h_nnnlo_yH");

    h_lo_ptH.SetLineColor(ROOT.kBlack);
    h_nlo_ptH.SetLineColor(ROOT.kGreen+3);
    h_nnlo_ptH.SetLineColor(ROOT.kBlue);
    h_nnnlo_ptH.SetLineColor(ROOT.kRed);   

    leg = ROOT.TLegend(0.5,0.6,0.8,0.8);
    leg.SetBorderSize(0);
    leg.SetFillStyle(0);
    leg.SetTextSize(0.035);
    leg.AddEntry(h_lo_ptH,"LO","l");
    leg.AddEntry(h_nlo_ptH,"NLO","l");
    leg.AddEntry(h_nnlo_ptH,"NNLO","l");
    leg.AddEntry(h_nnnlo_ptH,"NNNLO","l");

    c_ptH = ROOT.TCanvas("c_ptH","c_ptH",1000,800);
    p1 = ROOT.TPad("p1","p1",0.0,0.3,1.0,1.0);
    p2 = ROOT.TPad("p2","p2",0.0,0.0,1.0,0.3);
    p1.SetBottomMargin(0.05);
    p2.SetTopMargin(0.05);
    p2.SetBottomMargin(0.3);

    c_ptH.cd();
    p1.Draw(); p1.cd();

    h_lo_ptH.Draw('histe');
    h_nlo_ptH.Draw('histesames');
    h_nnlo_ptH.Draw('histesames');
    h_nnnlo_ptH.Draw('histesames');
    leg.Draw();

    c_ptH.cd();
    p2.Draw(); p2.cd();

    h_nlo_ptH_ratio = h_nlo_ptH.Clone();
    h_nlo_ptH_ratio.SetTitle(";pT(GeV);ratio to LO")
    h_nlo_ptH_ratio.Divide(h_lo_ptH);    
    h_nnlo_ptH_ratio = h_nnlo_ptH.Clone();
    h_nnlo_ptH_ratio.SetTitle(";pT(GeV);ratio to LO")
    h_nnlo_ptH_ratio.Divide(h_lo_ptH);    
    h_nnnlo_ptH_ratio = h_nnnlo_ptH.Clone();
    h_nnnlo_ptH_ratio.SetTitle(";pT(GeV);ratio to LO")
    h_nnnlo_ptH_ratio.Divide(h_lo_ptH);  

    fixRatioErrors(h_nlo_ptH_ratio,h_nlo_ptH);
    fixRatioErrors(h_nnlo_ptH_ratio,h_nnlo_ptH);
    fixRatioErrors(h_nnnlo_ptH_ratio,h_nnnlo_ptH);


    h_nlo_ptH_ratio.SetMaximum(1.1);
    h_nlo_ptH_ratio.SetMinimum(0.9);
    h_nlo_ptH_ratio.Draw("histe");
    h_nnlo_ptH_ratio.Draw("histesames");
    h_nnnlo_ptH_ratio.Draw("histesames");

    c_ptH.SaveAs("plots/ptH.pdf");
    c_ptH.SaveAs("plots/ptH.png");
    p1.SetLogy();
    c_ptH.SaveAs("plots/ptH-log.pdf");
    c_ptH.SaveAs("plots/ptH-log.png");

    fout = ROOT.TFile("vbf_ptH_n3lo.root","RECREATE");
    fout.cd();
    h_lo_ptH.Write();
    h_nlo_ptH.Write();
    h_nnlo_ptH.Write();
    h_nnnlo_ptH.Write();
    fout.Close();

def fixRatioErrors(hrat,h):

    nxbins = h.GetXaxis().GetNbins();
    for i in range(nxbins):
        fracerr = h.GetBinError(i+1)/h.GetBinContent(i+1);
        hrat.SetBinError(i+1, fracerr*hrat.GetBinContent(i+1));

def makeHistFromTextInput(fn,name):

    results = [];
    f = open(fn,'r');
    for line in f: 
        if "#" in line: continue;
        lline = line.strip().split();
        yerrhi = float(lline[4]) - float(lline[2]);
        yerrlo = float(lline[2]) - float(lline[3]);
        # yerr = (yerrhi+yerrlo)/2;
        yerr = max(yerrhi,yerrlo);
        # print lline
        # print lline[2], (float(lline[0]) + float(lline[1]))/2,yerrhi, yerrlo, yerr, float(lline[5])
        # results.append( [ (float(lline[0]) + float(lline[1]))/2, float(lline[2]), float(lline[5]) ]  );
        results.append( [ (float(lline[0]) + float(lline[1]))/2, float(lline[2]), yerr ]  );
    
    binwidth = (results[1][0] - results[0][0])/2.;
    h = ROOT.TH1F(name,";pT(GeV);pb/10GeV",len(results),results[0][0]-binwidth,results[len(results)-1][0]+binwidth);
    for i,r in enumerate(results):
        h.SetBinContent(i+1,results[i][1]);
        h.SetBinError(i+1,results[i][2]);
    
    h.SetMarkerSize(0);
    h.SetLineWidth(2);
    h.Sumw2();
    return h;

def makeCanvas(h):

    c = ROOT.TCanvas("c","c",1000,800);
    h.Draw('hist');
    c.SaveAs("plots/"+h.GetName()+".pdf");
    c.SaveAs("plots/"+h.GetName()+".png");

def makeCanvasViolin(h):

    c = ROOT.TCanvas("c","c",1000,800);
    h.Draw('VIOLIN');
    c.SaveAs("plots/"+h.GetName()+".pdf");
    c.SaveAs("plots/"+h.GetName()+".png");

def makeCanvas2D(h):

    c = ROOT.TCanvas("c","c",1000,800);
    h.Draw('COLZ');
    c.SaveAs("plots/"+h.GetName()+".pdf");
    c.SaveAs("plots/"+h.GetName()+".png");


def makeCanvases(hs):

    colors = [1,2,4,6,7,3];
    for i,h in enumerate(hs): h.SetLineColor(colors[i]);
    for i,h in enumerate(hs): 
        if h.Integral() > 0: h.Scale( 1/h.Integral() );
    hmax = -99;
    for i,h in enumerate(hs): 
        if hmax < h.GetMaximum(): hs[0].SetMaximum(h.GetMaximum()*1.2);

    c = ROOT.TCanvas("c","c",1000,800);
    for i,h in enumerate(hs):
        option = 'hist';
        if i > 0: option = 'histsames';
        h.Draw(option);
    c.SaveAs("plots/"+hs[0].GetName()+"s.pdf");
    c.SaveAs("plots/"+hs[0].GetName()+"s.png");


##----##----##----##----##----##----##
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", type=float, default = 30,help="luminosity", metavar="lumi")
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')

    (options, args) = parser.parse_args()

     
    import tdrstyle
    tdrstyle.setTDRStyle()
    ROOT.gStyle.SetPadTopMargin(0.10)
    ROOT.gStyle.SetPadLeftMargin(0.16)
    ROOT.gStyle.SetPadRightMargin(0.10)
    ROOT.gStyle.SetPalette(1)
    ROOT.gStyle.SetPaintTextFormat("1.1f")
    ROOT.gStyle.SetOptFit(0000)
    ROOT.gROOT.SetBatch()
    
    main(options,args)
##----##----##----##----##----##----##




