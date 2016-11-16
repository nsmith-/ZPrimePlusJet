import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array
import numpy
##############################################################################

def main(options,args):
    
    idir = options.idir
    odir = options.odir
    lumi = options.lumi
    sf = 5;

    #tf = ROOT.TFile("/uscms_data/d2/ntran/physics/dijets/DAZSLE/go3/ZPrimePlusJet/sklimming/sklim-v0-Nov2/QCD.root");
    tf = ROOT.TFile("/eos/uscms/store/user/lpchbb/zprimebits-v11.05/sklim-Nov7/QCD.root");
    tt = tf.Get("otree");
    nent = int(tt.GetEntries())

    # n2Vrho in ptbins
    ptbinsLo = [500,600,700,800];
    ptbinsHi = [600,700,800,900];

    h2s_n2Vrhos = []
    quantiles = []
    for j,pt in enumerate(ptbinsLo):
        h2s_n2Vrhos.append(ROOT.TH2F("h2s_n2Vrhos"+str(j),"; #rho; N2", 18, -6.0, -1.5, 50, 0, 0.5))

    for i in range(int(tt.GetEntries())):

        #if i % sf != 0: continue;
        tt.GetEntry(i)
        # if i > 500000: break;

        if(i % (1 * nent/100) == 0):
            sys.stdout.write("\r[" + "="*int(20*i/nent) + " " + str(round(100.*i/nent,0)) + "% done")
            sys.stdout.flush()

        puweight = tt.puWeight
        fbweight = tt.scale1fb
        weight = puweight*fbweight*sf
        jmsd_8 = tt.AK8Puppijet0_msd
        jpt_8  = tt.AK8Puppijet0_pt
        if jmsd_8 <= 0: jmsd_8 = 0.01
        if jmsd_8 < 30.: continue;
        rh_8 = math.log(jmsd_8*jmsd_8/jpt_8/jpt_8)
        jtN2b1sd_8 = tt.AK8Puppijet0_N2sdb1

        #if jpt_8 < 500 or jpt_8 > 600: continue;

        rh_8 = math.log(jmsd_8*jmsd_8/jpt_8/jpt_8)
        jtN2b1sd_8 = tt.AK8Puppijet0_N2sdb1
        for j,pt in enumerate(ptbinsLo):
            if jpt_8 > ptbinsLo[j] and jpt_8 < ptbinsHi[j]:
                h2s_n2Vrhos[j].Fill(rh_8,jtN2b1sd_8);
    
    #quantile = makeProfile(h2s_n2Vrho_inc);
    for j,pt in enumerate(ptbinsLo):
        quantiles.append(makeProfile(h2s_n2Vrhos[j],str(j)));
    print quantiles

    h_rho = ROOT.TH1F("h_rho","; #rho; N", 50, -10, 0);
    h2_rhoVpt_fail = ROOT.TH2F("h2_rhoVpt_fail","; #rho; pT", 18, -6.0, -1.5, 8, 500, 900);
    h2_rhoVpt_pass = ROOT.TH2F("h2_rhoVpt_pass","; #rho; pT", 18, -6.0, -1.5, 8, 500, 900);
    h2_rhoVpt_pafa = ROOT.TH2F("h2_rhoVpt_pafa","; #rho; pT", 18, -6.0, -1.5, 8, 500, 900);
    h2_rhoVpt_pafa_v2 = ROOT.TH2F("h2_rhoVpt_pafa_v2","; #rho; pT", 18, -6.0, -1.5, 8, 500, 900);
    h_jtN2b1sd = ROOT.TH1F("h_jtN2b1sd","; N2; N", 25, -0.2, 0.6);
    h_jtN2b1sdddt = ROOT.TH1F("h_jtN2b1sdddt","; N2DDT; N", 25, -0.2, 0.6);

    h_rhos = [];
    h_rhos_fail = [];
    h_rhos_pass = [];
    h_rhos_pafa = [];
    h_rhos_fail_v2 = [];
    h_rhos_pafa_v2 = [];
    h2s_n2Vrho = [];
    h2s_n2ddtVrho = [];
    h2s_n2ddtVrho_v2 = [];

    for j,pt in enumerate(ptbinsLo):
        h_rhos.append( ROOT.TH1F("h_rho"+str(j),"; #rho; N", 50, -10, 0) );
        h_rhos_fail.append( ROOT.TH1F("h_rhos_fail"+str(j),"; #rho; N", 50, -10, 0) );
        h_rhos_fail_v2.append( ROOT.TH1F("h_rhos_fail_v2"+str(j),"; #rho; N", 50, -10, 0) );
        h_rhos_pass.append( ROOT.TH1F("h_rhos_pass"+str(j),"; #rho; N", 50, -10, 0) );
        h_rhos_pafa.append( ROOT.TH1F("h_rhos_pafa"+str(j),"; #rho; N", 50, -10, 0) );
        h_rhos_pafa_v2.append( ROOT.TH1F("h_rhos_pafa_v2"+str(j),"; #rho; N", 50, -10, 0) );
        h2s_n2Vrho.append( ROOT.TH2F("h2s_n2Vrho"+str(j),"; #rho; N2", 18, -6.0, -1.5, 50, -0.25, 0.5) );
        h2s_n2ddtVrho.append( ROOT.TH2F("h2s_n2ddtVrho"+str(j),"; #rho; N2DDT", 18, -6.0, -1.5, 50, -0.25, 0.5) );
        h2s_n2ddtVrho_v2.append( ROOT.TH2F("h2s_n2ddtVrho_v2"+str(j),"; #rho; N2DDT", 18, -6.0, -1.5, 50, -0.25, 0.5) );

    for i in range(int(tt.GetEntries())):

        if i % sf != 0: continue
        
        tt.GetEntry(i)
        
        if(i % (1 * nent/100) == 0):
            sys.stdout.write("\r[" + "="*int(20*i/nent) + " " + str(round(100.*i/nent,0)) + "% done")
            sys.stdout.flush()

        puweight = tt.puWeight
        fbweight = tt.scale1fb
        weight = puweight*fbweight*sf

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

        #jtN2b1sdddt_8 = jtN2b1sd_8 - (9.00067e-05)*jpt_8 - (0.0778)*(rh_8) - 0.0265*rh_8*rh_8 - 0.0024*rh_8*rh_8*rh_8;

        jtN2b1sdddt_8 = 0 
        rho_index = h2s_n2ddtVrho[0].GetXaxis().FindBin(rh_8) - 1;
        if rh_8 > h2s_n2ddtVrho[0].GetXaxis().GetBinUpEdge( h2s_n2ddtVrho[0].GetXaxis().GetNbins() ): rho_index = h2s_n2ddtVrho[0].GetXaxis().GetNbins()-1;
        if rh_8 < h2s_n2ddtVrho[0].GetXaxis().GetBinLowEdge( 1 ): rho_index = 0;
        for j,pt in enumerate(ptbinsLo):
            if jpt_8 > ptbinsLo[j] and jpt_8 < ptbinsHi[j]:
                jtN2b1sdddt_8 = jtN2b1sd_8 - quantiles[j][rho_index]; #+ (9.00067e-05)*(jpt_8-500.);
        
        # rhofunc = -2.42531e-06 - 1.47639e-01*rh_8 - 3.27902e-02*rh_8*rh_8 - 2.43034e-03*rh_8*rh_8*rh_8; 
        rhofunc = -2.72547e-02 - 1.34663e-01*rh_8 - 2.40669e-02*rh_8*rh_8 - 1.44548e-03*rh_8*rh_8*rh_8 ; 
        jtN2b1sdddt_8_v2 = jtN2b1sd_8 - rhofunc + (9.00067e-05)*(jpt_8-500.);
        # print jtN2b1sdddt_8_v2, rhofunc

        h_rho.Fill(rh_8);
        h_jtN2b1sd.Fill(jtN2b1sd_8);
        h_jtN2b1sdddt.Fill(jtN2b1sdddt_8);
        if jtN2b1sdddt_8 < 0:
            h2_rhoVpt_pafa.Fill(rh_8,jpt_8);
            h2_rhoVpt_pafa_v2.Fill(rh_8,jpt_8);
            h2_rhoVpt_pass.Fill(rh_8,jpt_8);
        if jtN2b1sdddt_8 > 0:
            h2_rhoVpt_fail.Fill(rh_8,jpt_8);

        for j,pt in enumerate(ptbinsLo):
            if jpt_8 > ptbinsLo[j] and jpt_8 < ptbinsHi[j]: 
                h_rhos[j].Fill(rh_8); 
                h2s_n2Vrho[j].Fill(rh_8,jtN2b1sd_8);
                h2s_n2ddtVrho[j].Fill(rh_8,jtN2b1sdddt_8);
                h2s_n2ddtVrho_v2[j].Fill(rh_8,jtN2b1sdddt_8_v2);
                if jtN2b1sdddt_8 < 0: 
                    h_rhos_pass[j].Fill(rh_8);
                    h_rhos_pafa[j].Fill(rh_8);
                if jtN2b1sdddt_8 > 0: 
                    h_rhos_fail[j].Fill(rh_8);

                if jtN2b1sdddt_8_v2 < 0: 
                    h_rhos_pafa_v2[j].Fill(rh_8);
                if jtN2b1sdddt_8_v2 > 0: 
                    h_rhos_fail_v2[j].Fill(rh_8);

                break;

    h2_rhoVpt_pafa.Sumw2();
    h2_rhoVpt_pafa_v2.Sumw2();
    h2_rhoVpt_fail.Sumw2();
    # h2_rhoVpt_fail_v2.Sumw2();
    h2_rhoVpt_pafa.Divide(h2_rhoVpt_fail);
    # h2_rhoVpt_pafa_v2.Divide(h2_rhoVpt_fail_v2);
    for j,pt in enumerate(ptbinsLo):
        h_rhos_pafa[j].Sumw2();
        h_rhos_pafa_v2[j].Sumw2();
        h_rhos_fail[j].Sumw2();
        h_rhos_fail_v2[j].Sumw2();
        h_rhos_pafa[j].Divide(h_rhos_fail[j]);
        h_rhos_pafa_v2[j].Divide(h_rhos_fail_v2[j]);

    makeCanvas(h_rho);
    makeCanvas(h_jtN2b1sd);
    makeCanvas(h_jtN2b1sdddt);
    makeCanvases(h_rhos);
    makeCanvases(h_rhos_fail);
    makeCanvases(h_rhos_pass);
    makeCanvases(h_rhos_pafa);
    makeCanvases(h_rhos_pafa_v2);
    for h2 in h2s_n2Vrho: makeCanvasViolin(h2);
    for h2 in h2s_n2ddtVrho: makeCanvasViolin(h2);
    for h2 in h2s_n2ddtVrho_v2: makeCanvasViolin(h2);
    makeCanvas2D(h2_rhoVpt_pafa);


def makeCanvas(h):

    c = ROOT.TCanvas("c","c",1000,800);
    h.Draw('hist');
    c.SaveAs("plots/"+h.GetName()+".pdf");
    c.SaveAs("plots/"+h.GetName()+".png");

def makeCanvasViolin(h):

    h1 = {}
    q5 = []
    bins = []

    nbinsx = h.GetXaxis().GetNbins();
    for i in range(nbinsx):
        h1[i] = h.ProjectionY("From %s to %s+1"%(str(i),str(i)), i, i+1);
        probSum = array.array('d', [0.05])
        q = array.array('d', [0.0]*len(probSum))
        h1[i].GetQuantiles(len(probSum), q, probSum)
        q5.append(q[0])

    xlo = h.GetXaxis().GetBinLowEdge(1);
    xhi = h.GetXaxis().GetBinUpEdge( h.GetXaxis().GetNbins() );
    hprof = ROOT.TH1F("hv_N2sdb1",";#rho = log(m^{2}/p_{T}^{2});N_{2}^{DDT}",nbinsx,xlo,xhi)
    numpy.round(q5,3)

    for i in range(nbinsx):
        hprof.SetBinContent(i+1,q5[i])

    c = ROOT.TCanvas("c","c",1000,800);
    h.Draw('VIOLIN');
    hprof.SetMarkerColor(ROOT.kBlue)
    hprof.SetMarkerStyle(20)
    hprof.Draw("psames");    
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

def makeProfile(h2,ptbin):

    h1 = {}
    q5 = []
    bins = []

    nbinsx = h2.GetXaxis().GetNbins();
    for i in range(nbinsx):
        h1[i] = h2.ProjectionY("From %s to %s+1"%(str(i),str(i)), i, i+1);

        probSum = array.array('d', [0.05])
        q = array.array('d', [0.0]*len(probSum))
        h1[i].GetQuantiles(len(probSum), q, probSum)
        q5.append(q[0])
    
    xlo = h2.GetXaxis().GetBinLowEdge(1);
    xhi = h2.GetXaxis().GetBinUpEdge( h2.GetXaxis().GetNbins() );
    hprof = ROOT.TH1F("h2_N2sdb1",";#rho = log(m^{2}/p_{T}^{2});N_{2}^{DDT}",nbinsx,xlo,xhi)
    numpy.round(q5,3)

    for i in range(0,nbinsx):
        hprof.SetBinContent(i+1,q5[i])

    g1 = ROOT.TF1("m2","pol3",-6,-2);
    hprof.Fit(g1,"RL");

    print "check the fit..."
    print "evaluating function...", g1.Eval(-2.);
    byhand = -2.42531e-06 + 1.47639e-01*2. - 3.27902e-02*4 + 2.43034e-03*8 
    print "now by hand...",byhand

    print q5

    c = ROOT.TCanvas("c","c",1000,800);
    txta = ROOT.TLatex(0.16,0.95,"CMS");
    txta.SetNDC();
    txtb = ROOT.TLatex(0.22,0.95,"Simulation Preliminary");
    txtb.SetNDC(); txtb.SetTextFont(52);
    txta.SetTextSize(0.035);
    txtb.SetTextSize(0.035);

    leg = ROOT.TLegend(0.5,0.65,0.9,0.9);
    leg.SetBorderSize(0);
    leg.SetFillStyle(0)
    leg.AddEntry(hprof,"5% eff",'pl')
    leg.AddEntry(h2,'50% eff','pl')

    h2.Draw('VIOLIN');
    hprof.SetMarkerColor(ROOT.kBlue)
    hprof.SetMarkerStyle(20)
    hprof.SetLineColor(ROOT.kBlue)
    hprof.SetMarkerSize(1)
    hprof.SetMaximum(0.4);
    hprof.SetMinimum(0.1);
    hprof.Draw("psames");
    txta.Draw();
    txtb.Draw();
    leg.SetTextSize(0.045);
    leg.Draw();

    c.SaveAs("plots/"+h2.GetName()+"_5eff.pdf");
    c.SaveAs("plots/"+h2.GetName()+"_5eff.png");

    fout = ROOT.TFile("n2ddt_%s.root"%ptbin,"RECREATE");
    hprof.SetName("h_n2ddt_transformation_%s"%ptbin);
    hprof.Write();
    fout.Close();

    return q5

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




