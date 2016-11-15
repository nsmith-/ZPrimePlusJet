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
    #idir = "/eos/uscms/store/user/lpchbb/ggHsample_V11/sklim-v0-28Oct/"
    #odir = "plots_2016_10_31/"
    idir = options.idir
    odir = options.odir
    lumi = options.lumi
    sf = 1;

    tf = ROOT.TFile("/eos/uscms/store/user/lpchbb/zprimebits-v11.05/sklim-Nov7/QCD.root");
    tt = tf.Get("otree");

    ptbinsLo = [500,600,700,800];
    ptbinsHi = [600,700,800,900];
    h_msd = ROOT.TH1F("h_msd","; m_{SD} (GeV); N", 50, 50, 300);
    h2_massVpt_fail = ROOT.TH2F("h2_rhoVpt_fail","; m_{SD} (GeV); p_{T}", 50, 7, 50, 300, 500, 900);
    h2_massVpt_pass = ROOT.TH2F("h2_rhoVpt_pass","; m_{SD} (GeV); p_{T}", 50, 7, 50, 300, 500, 900);
    h2_massVpt_pafa = ROOT.TH2F("h2_rhoVpt_pafa","; m_{SD} (GeV); p_{T}", 50, 7, 50, 300, 500, 900);
    h_doubleb= ROOT.TH1F("h_double-b","; double-b; N", 40, -1, 1);
    h_mass = [];
    h_mass_fail = [];
    h_mass_pass = [];
    h_mass_pafa = [];
    h2s_doublebVmass = [];
    for j,pt in enumerate(ptbinsLo):
        h_mass.append( ROOT.TH1F("h_mass"+str(j),"; m_{SD} (GeV); N", 50, -10, 0) );
        h_mass_fail.append( ROOT.TH1F("h_mass_fail"+str(j),"; m_{SD} (GeV); N", 50, 50, 300) );
        h_mass_pass.append( ROOT.TH1F("h_mass_pass"+str(j),"; m_{SD} (GeV); N", 50, 50, 300) );
        h_mass_pafa.append( ROOT.TH1F("h_mass_pafa"+str(j),"; m_{SD} (GeV); N", 50, 50, 300) );
        h2s_doublebVmass.append( ROOT.TH2F("h2s_doublebVmass"+str(j),"; m_{SD} (GeV); double-b", 10, 50, 300, 40, -1, 1) );

    nent = tt.GetEntries()
    for i in range(tt.GetEntries()):

        if i % sf != 0: continue
        # if i > 5000000: break
        
        tt.GetEntry(i)
        
        if(i % (1 * nent/100) == 0):
            sys.stdout.write("\r[" + "="*int(20*i/nent) + " " + str(round(100.*i/nent,0)) + "% done")
            sys.stdout.flush()

        puweight = tt.puWeight
        fbweight = tt.scale1fb
        weight = puweight*fbweight*sf

        jmsd_8 = tt.AK8Puppijet0_msd
        jpt_8  = tt.AK8Puppijet0_pt
	jbb =	tt.AK8CHSjet0_doublecsv

        if jmsd_8 < 50.: continue;


        h_msd.Fill(jmsd_8);
        h_doubleb.Fill(jbb);
        if jbb > 0.8:
            h2_massVpt_pafa.Fill(jmsd_8,jpt_8);
            h2_massVpt_pass.Fill(jmsd_8,jpt_8);
        if jbb < 0.8:
            h2_massVpt_fail.Fill(jmsd_8,jpt_8);

        for j,pt in enumerate(ptbinsLo):
            if jpt_8 > ptbinsLo[j] and jpt_8 < ptbinsHi[j]: 
                h_mass[j].Fill(jmsd_8); 
                h2s_doublebVmass[j].Fill(jbb,jmsd_8);
                if jbb > 0.8: 
                    h_mass_pass[j].Fill(jmsd_8);
                    h_mass_pafa[j].Fill(jmsd_8);
                if jbb < 0.8: h_mass_fail[j].Fill(jmsd_8);
                break;

    h2_massVpt_pafa.Sumw2();
    h2_massVpt_fail.Sumw2();
    h2_massVpt_pafa.Divide(h2_massVpt_fail);
    for j,pt in enumerate(ptbinsLo):
        h_mass_pafa[j].Sumw2();
        h_mass_fail[j].Sumw2();
        h_mass_pafa[j].Divide(h_mass_fail[j]);

    makeCanvas(h_msd);
    makeCanvas(h_doubleb);
    makeCanvases(h_mass);
    makeCanvases(h_mass_fail);
    makeCanvases(h_mass_pass);
    makeCanvases(h_mass_pafa);
    for h2 in h2s_doublebVmass: makeCanvasViolin(h2);
    makeCanvas2D(h2_massVpt_pafa);

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




