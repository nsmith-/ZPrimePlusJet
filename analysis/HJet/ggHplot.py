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
    binBoundaries=[300,310,320,330,340,350,360,370,380,390,400,410,420,430,440,450,460,470,480,490,500,510,520,530,540,540+20*1, 540+20*2, 540+20*3, 540+20*4, 540+20*5, 540+20*6, 540+20*7, 540+20*8, 540+20*9, 540+20*10, 540+20*10+30,540+20*10 + 60, 540+20*10 +90,540+20*10+120,540+20*10+150,540+20*10+180,540+20*10+210,540+20*10+240,540+20*10+270,540+20*10+470]
    file_in = ROOT.TFile.Open("GluGluHToBB_M125_13TeV_powheg_pythia8_all_1000pb_weighted.root")
    file_corr = ROOT.TFile.Open("GluGluHToBB_M125_13TeV_powheg_pythia8_all_1000pb_weighted_corrected.root")
    file_phil = ROOT.TFile.Open("ggH_corrections.root")
    file_in.cd()	
    tt = file_in.Get('otree')
    h_lo_ptH=ROOT.TH1F("h_lo_ptH","h_lo_ptH",len(binBoundaries)-1, array('d',binBoundaries)) 
    tt.Draw("genVPt>>h_lo_ptH","1*scale1fb") #(AK8Puppijet0_pt>450.)
    file_corr.cd()
    tt2 = file_corr.Get('otree')
    h_nnnlo_ptH=ROOT.TH1F("h_nnnlo_ptH","h_nnnlo_ptH",len(binBoundaries)-1, array('d',binBoundaries))
    tt2.Draw("genVPt>>h_nnnlo_ptH","(1.)*scale1fb")
    	
    
    
    #h_lo_ptH = makeHistFromTextInput("dat_vbfn3lo/LO_ptH.dat","h_lo_ptH");
    #h_nlo_ptH = makeHistFromTextInput("dat_vbfn3lo/NLO_ptH.dat","h_nlo_ptH");
    #h_nnlo_ptH = makeHistFromTextInput("dat_vbfn3lo/NNLO_ptH.dat","h_nnlo_ptH");
    #h_nnnlo_ptH = makeHistFromTextInput("dat_vbfn3lo/NNNLO_ptH.dat","h_nnnlo_ptH");
    
    # h_lo_yH = makeHistFromTextInput("dat_vbfn3lo/LO_yH.dat","h_lo_yH");
    # h_nlo_yH = makeHistFromTextInput("dat_vbfn3lo/NLO_yH.dat","h_nlo_yH");
    # h_nnlo_yH = makeHistFromTextInput("dat_vbfn3lo/NNLO_yH.dat","h_nnlo_yH");
    # h_nnnlo_yH = makeHistFromTextInput("dat_vbfn3lo/NNNLO_yH.dat","h_nnnlo_yH");

    h_lo_ptH.SetLineColor(ROOT.kBlack);
    h_lo_ptH.SetTitle("");
    h_lo_ptH.GetYaxis().SetTitle("d#sigma/dp_{T} (fb/GeV)")
    h_lo_ptH.GetYaxis().SetTitleSize(0.05)
    h_lo_ptH.GetYaxis().SetTitleOffset(1.1)
    #h_nlo_ptH.SetLineColor(ROOT.kGreen+3);
    #h_nnlo_ptH.SetLineColor(ROOT.kBlue);
    h_nnnlo_ptH.SetLineColor(ROOT.kAzure-8);   
    h_nnnlo_ptH.SetMarkerColor(ROOT.kAzure-8);
    h_lo_ptH.SetMarkerColor(ROOT.kBlack);
    h_nnnlo_ptH.SetMarkerStyle(20);
    h_lo_ptH.SetMarkerStyle(20);
    h_nnnlo_ptH.SetMarkerSize(0.5)
    h_lo_ptH.SetMarkerSize(0.5)	

    leg = ROOT.TLegend(0.7,0.7,0.9,0.9);
    leg.SetBorderSize(0);
    leg.SetFillStyle(0);
    leg.SetTextSize(0.035);
    leg.AddEntry(h_lo_ptH,"CMS Powheg","lp");
    #leg.AddEntry(h_nlo_ptH,"NLO","l");
    #leg.AddEntry(h_nnlo_ptH,"NNLO","l");
    leg.AddEntry(h_nnnlo_ptH,"NNLO + m_{t}","lp");

    c_ptH = ROOT.TCanvas("c_ptH","c_ptH",800,800);
    p1 = ROOT.TPad("p1","p1",0.0,0.3,1.0,1.0);
    p2 = ROOT.TPad("p2","p2",0.0,0.0,1.0,0.329);
    p1.SetBottomMargin(0.05);
    p2.SetTopMargin(0.05);
    p2.SetBottomMargin(0.3);

    c_ptH.cd();
    p1.Draw(); p1.cd();
    h_lo_ptH = divideBinWidth(h_lo_ptH)
    h_nnnlo_ptH = divideBinWidth(h_nnnlo_ptH)	
    h_lo_ptH.SetMaximum(50.)
    h_lo_ptH.Draw('e');
    #h_nlo_ptH.Draw('esames');
    #h_nnlo_ptH.Draw('histesames');
    h_nnnlo_ptH.Draw('e sames');
    #file_phil.cd()   #sanity check with files from phil we used to derive the ratio
    #h3 = file_phil.Get('MG_NNLO_FT_binWdith')
  
    #h4 = file_phil.Get('Powheg_binWidth')
    #h3.Draw('sames')
    #h4.Draw('sames')
    leg.Draw();

    c_ptH.cd();
    p2.Draw(); p2.cd();

    #h_nlo_ptH_ratio = h_nlo_ptH.Clone();
    #h_nlo_ptH_ratio.SetTitle(";pT(GeV);ratio to POWHEG")
    #h_nlo_ptH_ratio.Divide(h_lo_ptH);    
    #h_nnlo_ptH_ratio = h_nnlo_ptH.Clone();
    #h_nnlo_ptH_ratio.SetTitle(";pT(GeV);ratio to POWHEG")
    #h_nnlo_ptH_ratio.Divide(h_lo_ptH);    
    h_nnnlo_ptH_ratio = h_nnnlo_ptH.Clone();
    h_nnnlo_ptH_ratio.SetTitle(";H p_{T} (GeV);ratio to POWHEG")
    h_nnnlo_ptH_ratio.GetXaxis().SetLabelSize(0.07)
    h_nnnlo_ptH_ratio.GetYaxis().SetLabelSize(0.07)
    h_nnnlo_ptH_ratio.GetXaxis().SetTitleSize(0.09)
    h_nnnlo_ptH_ratio.GetYaxis().SetTitleSize(0.09)
    h_nnnlo_ptH_ratio.GetXaxis().SetTitleOffset(1.1)
    h_nnnlo_ptH_ratio.GetYaxis().SetTitleOffset(0.6)
    h_nnnlo_ptH_ratio.GetXaxis().SetLabelOffset(0.03)
    
    h_nnnlo_ptH_ratio.Divide(h_lo_ptH);  
    #h3_ratio = h3.Clone() 
    #h3_ratio.Divide(h4)

    #fixRatioErrors(h_nlo_ptH_ratio,h_nlo_ptH);
    #fixRatioErrors(h_nnlo_ptH_ratio,h_nnlo_ptH);
    fixRatioErrors(h_nnnlo_ptH_ratio,h_nnnlo_ptH);
    h_nnnlo_ptH_ratio.SetMarkerColor(ROOT.kAzure-8);
    h_nnnlo_ptH_ratio.SetLineColor(ROOT.kAzure-8);
    NLO_= ROOT.TF1("NLO_", "pol2", 200, 1220)
    
    NLO_.SetParameter(0, 2.70299e+00)
    NLO_.SetParameter(1, -2.18233e-03)
    NLO_.SetParameter(2,5.22287e-07 )
    NLO_.SetLineColor(ROOT.kGray+2)
    NLO_.SetLineWidth(1)
    a = ROOT.TLine(300,1,1200,1)
    a.SetLineWidth(1)
    a.SetLineStyle(2)
    a.SetLineColor(ROOT.kBlack)
    

    


    h_nnnlo_ptH_ratio.SetMaximum(3.);
    h_nnnlo_ptH_ratio.SetMinimum(0.);
    #h_nlo_ptH_ratio.Draw("histe");
    #h_nnlo_ptH_ratio.Draw("histesames");
    h_nnnlo_ptH_ratio.Draw("histesames");
    NLO_.Draw("sames")
    a.Draw("sames")

    #h3_ratio.Draw("histesames");

    c_ptH.SaveAs("ptH.pdf");
    c_ptH.SaveAs("ptH.png");
    p1.SetLogy();
    c_ptH.SaveAs("ptH-log.pdf");
    c_ptH.SaveAs("ptH-log.png");

    fout = ROOT.TFile("ggh_ptH_n3lo.root","RECREATE");
    fout.cd();
    h_lo_ptH.Write();
#    h_nlo_ptH.Write();
#    h_nnlo_ptH.Write();
    h_nnnlo_ptH.Write();
    fout.Close();

def fixRatioErrors(hrat,h):

    nxbins = h.GetXaxis().GetNbins();
    for i in range(nxbins):
        if h.GetBinContent(i+1) ==0 : 
		fracerr =1 
	else:
            fracerr = h.GetBinError(i+1)/h.GetBinContent(i+1);
        hrat.SetBinError(i+1, 0.3*hrat.GetBinContent(i+1));

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

def divideBinWidth(h):

    for iB in range(1, h.GetNbinsX()+1):
      currentVal = h.GetBinContent(iB);
      currentErr = h.GetBinError(iB);
      binWidth = h.GetBinWidth(iB);
      h.SetBinContent(iB,currentVal/binWidth);
      h.SetBinError(iB,currentErr/binWidth);
    return h

##----##----##----##----##----##----##
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=True, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", type=float, default = 30,help="luminosity", metavar="lumi")
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')

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




