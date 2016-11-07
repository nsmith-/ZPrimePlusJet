import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array

###############################
# Creates violin/profile plots
###############################

def doProfile(h2,pt,ptbin,hprofile,odir):

    h1 = {}
    qs = []
    q2 = []

    for i in range(0,11):
        h1[i] = h2.ProjectionY("From %s to %s+1"%(str(i),str(i)), i, i+1);

        areaFractions = [0.05,0.1,0.5,1]
        probSum = array.array('d', areaFractions)
        q = array.array('d', [0.0]*len(probSum))
        h1[i].GetQuantiles(len(probSum), q, probSum)
        qs.append(q[0])
        q2.append(q[2])

    hprof = ROOT.TH1F("h2_N2sdb1",";#rho = log(m^{2}/p_{T}^{2});N_{2}^{DDT}",10,-6,-1)
    for i in range(0,11):
        hprof.SetBinContent(i,qs[i])

    c = ROOT.TCanvas("cprof","cprof",1000,800)

    txta = ROOT.TLatex(0.16,0.95,"CMS");
    txta.SetNDC();
    txtb = ROOT.TLatex(0.22,0.95,"Simulation Preliminary");
    txtb.SetNDC(); txtb.SetTextFont(52);
    txta.SetTextSize(0.035);
    txtb.SetTextSize(0.035);

    txtc = ROOT.TLatex(0.19,0.85,"%s"%ptbin);
    txtc.SetNDC();
    txtc.SetTextSize(0.030);
    txtc.SetTextFont(42);

    leg = ROOT.TLegend(0.5,0.65,0.9,0.9);
    leg.SetBorderSize(0);
    leg.SetFillStyle(0)
    leg.AddEntry(hprof,"5% eff",'pl')
    leg.AddEntry(hprofile,'50% eff','pl')

    hprofile.GetXaxis().SetTitle("#rho = log(m^{2}/p_{T}^{2})")
    hprofile.GetYaxis().SetTitle('N_{2}^{#beta = 1.0}_{SD} DDT')
    hprofile.SetMarkerColor(ROOT.kBlack)
    hprofile.SetMarkerStyle(20)
    hprofile.SetFillColor(ROOT.kGray)
    hprofile.SetLineColor(ROOT.kGray)
    hprofile.SetMarkerSize(1.5)
    hprofile.SetMaximum(hprof.GetMaximum()*2);
    hprofile.Draw("violinx")

    hprof.SetMarkerColor(ROOT.kBlue)
    hprof.SetMarkerStyle(20)
    hprof.SetLineColor(ROOT.kBlue)
    hprof.SetMarkerSize(1.5)
    hprof.SetMaximum(hprof.GetMaximum()*2);

    hprof.Draw("psames")

    txta.Draw();
    txtb.Draw();
    txtc.Draw();
    leg.SetTextSize(0.045);
    leg.Draw();

    c.SaveAs("%s/profile005N2sdb1_ptbin%s.png"%(odir,str(pt)))

def main(options,args):

    f = {}
    t = {}

    files = [('QCD','QCD')]
    histos = {};

    h2_N2sdb1 = {}
    hrho_N2sdb1 = {}

    for tag,sample in files:

        hrho_N2sdb1[tag] = []
        h2_N2sdb1[tag] = []

        f[tag] = ROOT.TFile("%s_%s.root"%(options.idir,sample));
        t[tag] = f[tag].Get("tree");

        n_ptbins = 5;
        ptlo = 350;
        ptwidth = 100;
        pthi = 850;

        for i in range(n_ptbins):
            h2_N2sdb1[tag].append( ROOT.TH2F("h2_N2sdb1_"+str(i)+tag,"#rho = log(m^{2}/p_{T}^{2});N2sdb1;Events",10,-6,-1,10,0,1));
            hrho_N2sdb1[tag].append(ROOT.TH2F("hrho_N2sdb1_"+str(i)+tag,"#rho = log(m^{2}/p_{T}^{2});N2sdb1;Events",10,-6,-1,10,0,1));

        nent = int(t[tag].GetEntries());
        for i in range(int(t[tag].GetEntries())):
            if(i % (1 * nent/100) == 0):
                sys.stdout.write("\r[" + "="*int(20*i/nent) + " " + str(round(100.*i/nent,0)) + "% done");
                sys.stdout.flush();
            if i % 100 != 0: continue;
                
            t[tag].GetEntry(i);
            
            jpt = getattr(t[tag],"AK8Puppijet0_pt");
            jmsd = getattr(t[tag],"AK8Puppijet0_msd");
            jrho2 = ROOT.TMath.Log((jmsd*jmsd)/(jpt*jpt))

            if jpt > 0 and (jmsd > 0):
                jN2sdb1 = getattr(t[tag],"AK8Puppijet0_N2sdb1")

                for j in range(n_ptbins):
                    if jpt > (ptlo + j*float(ptwidth)) and jpt < (ptlo + (j+1)*float(ptwidth)):
                        hrho_N2sdb1[tag][j].Fill( jrho2, jN2sdb1);
                        h2_N2sdb1[tag][j].Fill( jrho2, jN2sdb1);

        for j in range(n_ptbins):
            hrho_N2sdb1[tag][j].SetDirectory(0);
            h2_N2sdb1[tag][j].SetDirectory(0);

        for j in range(n_ptbins):
            if j == 0: ptbin = 'pT = 350-450 GeV'
            if j == 1: ptbin = 'pT = 450-550 GeV'
            if j == 2: ptbin = 'pT = 550-650 GeV'
            if j == 3: ptbin = 'pT = 650-750 GeV'
            if j == 4: ptbin = 'pT = 750-850 GeV'

            doProfile(h2_N2sdb1[tag][j],j,ptbin,hrho_N2sdb1[tag][j],options.odir);

        f[tag].Close()

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('-i','--idir', dest='idir', default = '/afs/cern.ch/work/c/cmantill/public/Bacon/CMSSW_8_0_20/src/BaconAnalyzer/Analyzer/training/validation_2',help='input directory', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = '~cmantill/www/Zprime/05Nov/',help='directory to write plots', metavar='odir')

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
