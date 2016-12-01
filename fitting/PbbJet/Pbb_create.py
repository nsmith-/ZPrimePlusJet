import os
import math
from array import array
import optparse
import ROOT
from ROOT import *
import sys

def createHist(trans_h2ddt,tag,filename,sf,lumi,mass):
	h_pass_ak8 = TH2F(tag+"_pass","; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)",75,0,500,5,500,1000)
	h_fail_ak8 = TH2F(tag+"_fail","; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)",75,0,500,5,500,1000)

	sklimpath="root://cmsxrootd.fnal.gov//eos/uscms/store/user/lpchbb/sklim-Nov7/"
	infile=ROOT.TFile(sklimpath+filename+".root")	
	print(sklimpath+filename+".root")
	tree= infile.Get("otree")
        nent = tree.GetEntries();
	'''
        finfo = ROOT.TFile("../../sklimming/signalXS/sig_vectordijet_xspt.root");
        h_rw = None
        if 'VectorDiJet1Jet' in filename and mass > 0:
                hname = "med_"+str(mass)+"_0.1_proc_800";
                if '75' in filename: hname = "med_"+str(mass)+"_0.1_proc_801";
                hinfo = finfo.Get(hname)
                hinfo.Scale(100*1000.); # 100. for coupling, 1000. for conversion to pb is the cross-section 
                hinfo_nbins = hinfo.GetNbinsX();
                hinfo_xlo = hinfo.GetXaxis().GetBinLowEdge(1);
                hinfo_xhi = hinfo.GetXaxis().GetBinUpEdge(hinfo_nbins);
                htmp = ROOT.TH1F("htmp","htmp",hinfo_nbins,hinfo_xlo,hinfo_xhi)
                for i in range(nent):
                        tree.GetEntry(i);
                        htmp.Fill(tree.genVPt,tree.scale1fb)

                h_rw = ROOT.TH1F( hinfo.Clone() );
                h_rw.Divide(htmp);
	'''
        for i in range(tree.GetEntries()):

            if i % sf != 0: continue
            tree.GetEntry(i)
            if(i % (1 * nent/100) == 0):
                sys.stdout.write("\r[" + "="*int(20*i/nent) + " " + str(round(100.*i/nent,0)) + "% done")
                sys.stdout.flush()

            puweight = tree.puWeight
            fbweight = tree.scale1fb * lumi
            weight = puweight*fbweight*sf
	    #if 'VectorDiJet1Jet' in filename and mass>0: weight = weight*h_rw.GetBinContent( h_rw.FindBin(tree.genVPt) )

	    jmsd_8 = tree.AK8Puppijet0_msd
	    jpt_8  = tree.AK8Puppijet0_pt
	    if jmsd_8 <= 0: jmsd_8 = 0.01

	    rh_8 = math.log(jmsd_8*jmsd_8/jpt_8/jpt_8)
	    jtN2b1sd_8 = tree.AK8Puppijet0_N2sdb1

            rhP_8 = math.log(jmsd_8*jmsd_8/jpt_8)
            jt21_8 = tree.AK8Puppijet0_tau21
            jt21P_8 = jt21_8 + 0.063*rhP_8
	

	    cur_rho_index = trans_h2ddt.GetXaxis().FindBin(rh_8);
	    cur_pt_index  = trans_h2ddt.GetYaxis().FindBin(jpt_8);
	    if rh_8 > trans_h2ddt.GetXaxis().GetBinUpEdge( trans_h2ddt.GetXaxis().GetNbins() ): cur_rho_index = trans_h2ddt.GetXaxis().GetNbins();
	    if rh_8 < trans_h2ddt.GetXaxis().GetBinLowEdge( 1 ): cur_rho_index = 1;
	    if jpt_8 > trans_h2ddt.GetYaxis().GetBinUpEdge( trans_h2ddt.GetYaxis().GetNbins() ): cur_pt_index = trans_h2ddt.GetYaxis().GetNbins();
	    if jpt_8 < trans_h2ddt.GetYaxis().GetBinLowEdge( 1 ): cur_pt_index = 1;

	    jtN2b1sdddt_8 = jtN2b1sd_8 - trans_h2ddt.GetBinContent(cur_rho_index,cur_pt_index);
	    jdb_8 = tree.AK8CHSjet0_doublecsv

	    # Lepton, photon veto and tight jets
	    if tree.neleLoose == 0 and tree.nmuLoose == 0 and tree.ntau==0 and tree.nphoLoose==0 and tree.AK8Puppijet0_isTightVJet ==1 and jt21P_8 < 0.4  and tree.AK8Puppijet0_msd >40 and tree.pfmet < 180 and tree.nAK4PuppijetsdR08 <5 and tree.nAK4PuppijetsTdR08 < 3 :
		    if tree.AK8Puppijet0_pt > 500 and jdb_8 >0.9:
			    h_pass_ak8.Fill( jmsd_8, jpt_8, weight )
		    if tree.AK8Puppijet0_pt > 500 and jdb_8 <0.9:
			    h_fail_ak8.Fill( jmsd_8, jpt_8, weight )

	return h_pass_ak8,h_fail_ak8


mass=[50,75,100,125,150,250,300,400,500]

outfile=TFile("hist_1DPbb.root", "recreate");

lumi =30.
SF_tau21 =1

f_h2ddt = TFile("../../analysis/ZqqJet/h3_n2ddt.root");
print("Opened file ... ")
trans_h2ddt = f_h2ddt.Get("h2ddt");
trans_h2ddt.SetDirectory(0)
f_h2ddt.Close()

data_obs_pass, data_obs_fail = createHist(trans_h2ddt,'data_obs','JetHTICHEP',1,1,0)
qcd_pass, qcd_fail = createHist(trans_h2ddt,'qcd','QCD',1,30.,0)
tqq_pass, tqq_fail = createHist(trans_h2ddt,'tqq','TTbar_madgraphMLM_1000pb_weighted',1,30.,0)
wqq_pass, wqq_fail = createHist(trans_h2ddt,'wqq','WJets_1000pb_weighted',1,30.,0)
zqq_pass, zqq_fail = createHist(trans_h2ddt,'zqq','DY_1000pb_weighted',1,30.,0)

for m in mass:
	hs_pass, hs_fail = createHist(trans_h2ddt,'pqq%s'%(m),'DMSpin0_ggPhibb1j_%s_1000pb_weighted'%(m),1,30.,m)
	outfile.cd()
	hs_pass.Write()
	hs_fail.Write()

print("Building pass/fail")	
outfile.cd()
qcd_pass.Write()
qcd_fail.Write()
data_obs_pass.Write()
data_obs_fail.Write()
wqq_pass.Write()
wqq_fail.Write()
zqq_pass.Write()
zqq_fail.Write()
tqq_pass.Write()
tqq_fail.Write()
outfile.Write()
outfile.Close()

