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

    tf = ROOT.TFile("/uscms_data/d2/ntran/physics/dijets/DAZSLE/go3/ZPrimePlusJet/sklimming/sklim-v0-Nov2/QCD.root");
    tt = tf.Get("otree");

    ptbinsLo = [500,600,700,800];
    ptbinsHi = [600,700,800,900];
    h_rho = ROOT.TH1F("h_rho","; #rho; N", 50, -10, 0);
    h2_rhoVpt_fail = ROOT.TH2F("h2_rhoVpt_fail","; #rho; pT", 14, -7, 0, 8, 500, 900);
    h2_rhoVpt_pass = ROOT.TH2F("h2_rhoVpt_pass","; #rho; pT", 14, -7, 0, 8, 500, 900);
    h2_rhoVpt_pafa = ROOT.TH2F("h2_rhoVpt_pafa","; #rho; pT", 14, -7, 0, 8, 500, 900);
    h_jtN2b1sd = ROOT.TH1F("h_jtN2b1sd","; N2; N", 25, 0, 0.6);
    h_jtN2b1sdddt = ROOT.TH1F("h_jtN2b1sdddt","; N2DDT; N", 25, 0, 0.6);
    h_rhos = [];
    h_rhos_fail = [];
    h_rhos_pass = [];
    h_rhos_pafa = [];
    h2s_n2Vrho = [];
    h2s_n2ddtVrho = [];
    for j,pt in enumerate(ptbinsLo):
        h_rhos.append( ROOT.TH1F("h_rho"+str(j),"; #rho; N", 50, -10, 0) );
        h_rhos_fail.append( ROOT.TH1F("h_rhos_fail"+str(j),"; #rho; N", 50, -10, 0) );
        h_rhos_pass.append( ROOT.TH1F("h_rhos_pass"+str(j),"; #rho; N", 50, -10, 0) );
        h_rhos_pafa.append( ROOT.TH1F("h_rhos_pafa"+str(j),"; #rho; N", 50, -10, 0) );
        h2s_n2Vrho.append( ROOT.TH2F("h2s_n2Vrho"+str(j),"; #rho; N2", 14, -7, 0, 25, 0, 0.6) );
        h2s_n2ddtVrho.append( ROOT.TH2F("h2s_n2ddtVrho"+str(j),"; #rho; N2DDT", 14, -7, 0, 25, 0, 0.6) );

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
        weight = puweight+fbweight*sf

        jmsd_8 = tt.AK8Puppijet0_msd
        jpt_8  = tt.AK8Puppijet0_pt
        if jmsd_8 <= 0: jmsd_8 = 0.01

        if jmsd_8 < 30.: continue;

        rh_8 = math.log(jmsd_8*jmsd_8/jpt_8/jpt_8)
        rhP_8 = math.log(jmsd_8*jmsd_8/jpt_8)
        jt21_8 = tt.AK8Puppijet0_tau21
        jt32_8 = tt.AK8Puppijet0_tau32
        jt21P_8 = jt21_8 + 0.063*rhP_8
        jtN2b1sd_8 = tt.AK8Puppijet0_N2sdb1
        n2slope = 0.025;
        if rh_8 < -3.5: n2slope = 0;
        #jtN2b1sdddt_8 = jtN2b1sd_8 - (9.00067e-05)*jpt_8 + n2slope*(rh_8 + 3.5);
        jtN2b1sdddt_8 = jtN2b1sd_8 - (9.00067e-05)*jpt_8 - (0.0778)*(rh_8) - 0.0265*rh_8*rh_8 - 0.0024*rh_8*rh_8*rh_8;

        h_rho.Fill(rh_8);
        h_jtN2b1sd.Fill(jtN2b1sd_8);
        h_jtN2b1sdddt.Fill(jtN2b1sdddt_8);
        if jtN2b1sdddt_8 < 0.2:
            h2_rhoVpt_pafa.Fill(rh_8,jpt_8);
            h2_rhoVpt_pass.Fill(rh_8,jpt_8);
        if jtN2b1sdddt_8 > 0.2:
            h2_rhoVpt_fail.Fill(rh_8,jpt_8);

        for j,pt in enumerate(ptbinsLo):
            if jpt_8 > ptbinsLo[j] and jpt_8 < ptbinsHi[j]: 
                h_rhos[j].Fill(rh_8); 
                h2s_n2Vrho[j].Fill(rh_8,jtN2b1sd_8);
                h2s_n2ddtVrho[j].Fill(rh_8,jtN2b1sdddt_8);
                if jtN2b1sdddt_8 < 0.2: 
                    h_rhos_pass[j].Fill(rh_8);
                    h_rhos_pafa[j].Fill(rh_8);
                if jtN2b1sdddt_8 > 0.2: h_rhos_fail[j].Fill(rh_8);
                break;

    h2_rhoVpt_pafa.Sumw2();
    h2_rhoVpt_fail.Sumw2();
    h2_rhoVpt_pafa.Divide(h2_rhoVpt_fail);
    for j,pt in enumerate(ptbinsLo):
        h_rhos_pafa[j].Sumw2();
        h_rhos_fail[j].Sumw2();
        h_rhos_pafa[j].Divide(h_rhos_fail[j]);

    makeCanvas(h_rho);
    makeCanvas(h_jtN2b1sd);
    makeCanvas(h_jtN2b1sdddt);
    makeCanvases(h_rhos);
    makeCanvases(h_rhos_fail);
    makeCanvases(h_rhos_pass);
    makeCanvases(h_rhos_pafa);
    for h2 in h2s_n2Vrho: makeCanvasViolin(h2);
    for h2 in h2s_n2ddtVrho: makeCanvasViolin(h2);
    makeCanvas2D(h2_rhoVpt_pafa);

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




