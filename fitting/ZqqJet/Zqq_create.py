import os
import math
from array import array
import optparse
import ROOT
from ROOT import *
import sys

def createHist(trans_h2ddt,tag,filename,sf,lumi,mass,isdata=False):

	massbins = 100;
	masslo   = 0;
	masshi   = 500;

	h_pass_ak8 = TH2F(tag+"_pass","; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)",massbins,masslo,masshi,5,500,1000)
	h_fail_ak8 = TH2F(tag+"_fail","; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)",massbins,masslo,masshi,5,500,1000)
	h_pass_matched_ak8 = TH2F(tag+"_pass_matched","; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)",massbins,masslo,masshi,5,500,1000)
	h_pass_unmatched_ak8 = TH2F(tag+"_pass_unmatched","; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)",massbins,masslo,masshi,5,500,1000)
	h_fail_matched_ak8 = TH2F(tag+"_fail_matched","; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)",massbins,masslo,masshi,5,500,1000)
	h_fail_unmatched_ak8 = TH2F(tag+"_fail_unmatched","; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)",massbins,masslo,masshi,5,500,1000)
	
	# validation
	h_pass_msd_ak8 = TH1F(tag+"pass_msd", "; AK8 m_{SD}^{PUPPI}; N", 40, 0, 200)
	h_fail_msd_ak8 = TH1F(tag+"fail_msd", "; AK8 m_{SD}^{PUPPI}; N", 40, 0, 200)
	h_pass_msd_matched_ak8 = TH1F(tag+"pass_msd_matched", "; AK8 m_{SD}^{PUPPI}; N", 40, 0, 200)
	h_pass_msd_unmatched_ak8 = TH1F(tag+"pass_msd_unmatched", "; AK8 m_{SD}^{PUPPI}; N", 40, 0, 200)
	h_fail_msd_matched_ak8 = TH1F(tag+"fail_msd_matched", "; AK8 m_{SD}^{PUPPI}; N", 40, 0, 200)
	h_fail_msd_unmatched_ak8 = TH1F(tag+"fail_msd_unmatched", "; AK8 m_{SD}^{PUPPI}; N", 40, 0, 200)

	# sklimpath="root://cmsxrootd.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v11.05/sklim-Nov7/"
	# sklimpath="root://cmsxrootd.fnal.gov//eos/uscms/store/user/lpchbb/sklim-Nov7/"
	sklimpath="/uscms_data/d3/cmantill/CMSSW_8_0_20/src/zprime/ZPrimePlusJet/sklimming/skim/"
	infile=ROOT.TFile(sklimpath+filename+".root")	
	print(sklimpath+filename+".root")
	tree= infile.Get("otree")
	nent = tree.GetEntries();
	finfo = ROOT.TFile("../../sklimming/signalXS/sig_vectordijet_xspt.root");
	h_rw = None
	hinfo = None
	htmp = None;
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

	for i in range(tree.GetEntries()):

		if i % sf != 0: continue
		
		tree.GetEntry(i)
		if(i % (1 * nent/100) == 0):
			sys.stdout.write("\r[" + "="*int(20*i/nent) + " " + str(round(100.*i/nent,0)) + "% done")
			sys.stdout.flush()

		puweight = tree.puWeight
		fbweight = tree.scale1fb * lumi
		weight = puweight*fbweight*sf
		if isdata: weight = puweight*fbweight
		if 'VectorDiJet1Jet' in filename and mass>0: 
			ptToWeightFrom = tree.genVPt;
			if ptToWeightFrom < 500: ptToWeightFrom = 500.; # protection
			weight = weight*h_rw.GetBinContent( h_rw.FindBin(ptToWeightFrom) )

		jmsd_8 = tree.AK8Puppijet0_msd
		jpt_8  = tree.AK8Puppijet0_pt
		if jmsd_8 <= 0: jmsd_8 = 0.01

		rh_8 = math.log(jmsd_8*jmsd_8/jpt_8/jpt_8)

		if rh_8 < -6 or rh_8 > -1.5: continue;

		jtN2b1sd_8 = tree.AK8Puppijet0_N2sdb1
		cur_rho_index = trans_h2ddt.GetXaxis().FindBin(rh_8);
		cur_pt_index  = trans_h2ddt.GetYaxis().FindBin(jpt_8);
		if rh_8 > trans_h2ddt.GetXaxis().GetBinUpEdge( trans_h2ddt.GetXaxis().GetNbins() ): cur_rho_index = trans_h2ddt.GetXaxis().GetNbins();
		if rh_8 < trans_h2ddt.GetXaxis().GetBinLowEdge( 1 ): cur_rho_index = 1;
		if jpt_8 > trans_h2ddt.GetYaxis().GetBinUpEdge( trans_h2ddt.GetYaxis().GetNbins() ): cur_pt_index = trans_h2ddt.GetYaxis().GetNbins();
		if jpt_8 < trans_h2ddt.GetYaxis().GetBinLowEdge( 1 ): cur_pt_index = 1;

		jtN2b1sdddt_8 = jtN2b1sd_8 - trans_h2ddt.GetBinContent(cur_rho_index,cur_pt_index);

		# non resonant case
		jphi  = 9999;
		dphi  = 9999;
		dpt   = 9999;
		dmass = 9999;
		if mass > 0:
			jphi = getattr(tree,"AK8Puppijet0_phi");
			dphi = math.fabs(tree.genVPhi - jphi)
			dpt = math.fabs(tree.genVPt - jpt_8)/tree.genVPt
			dmass = math.fabs(mass - jmsd_8)/mass
		
		# Lepton, photon veto and tight jets
		if tree.neleLoose == 0 and tree.nmuLoose == 0 and tree.ntau==0 and tree.nphoLoose==0 and tree.AK8Puppijet0_isTightVJet ==1:
			
			# pass category
			if tree.AK8Puppijet0_pt > 500 and jtN2b1sdddt_8 < 0:
				h_pass_ak8.Fill( jmsd_8, jpt_8, weight )
				## for signal morphing
				h_pass_msd_ak8.Fill( jmsd_8, weight );
				if dphi < 0.8 and dpt < 0.5 and dmass < 0.3:
					h_pass_msd_matched_ak8.Fill( jmsd_8, weight );
					h_pass_matched_ak8.Fill( jmsd_8, jpt_8, weight );
				else:
					h_pass_msd_unmatched_ak8.Fill( jmsd_8, weight );
					h_pass_unmatched_ak8.Fill( jmsd_8, jpt_8, weight );
			# fail category
			if tree.AK8Puppijet0_pt > 500 and jtN2b1sdddt_8 > 0:
				h_fail_ak8.Fill( jmsd_8, jpt_8, weight )
				## for signal morphing
				h_fail_msd_ak8.Fill( jmsd_8, weight );
				if dphi < 0.8 and dpt < 0.5 and dmass < 0.3:
					h_fail_msd_matched_ak8.Fill( jmsd_8, weight );
					h_fail_matched_ak8.Fill( jmsd_8, jpt_8, weight );
				else:
					h_fail_msd_unmatched_ak8.Fill( jmsd_8, weight );	
					h_fail_unmatched_ak8.Fill( jmsd_8, jpt_8, weight );

	hists_out = [];
	#2d histograms
	hists_out.append( h_pass_ak8 );
	hists_out.append( h_fail_ak8 );
	hists_out.append( h_pass_matched_ak8 );
	hists_out.append( h_pass_unmatched_ak8 );
	hists_out.append( h_fail_matched_ak8 );
	hists_out.append( h_fail_unmatched_ak8 );
	#1d validation histograms
	hists_out.append( h_pass_msd_ak8 );
	hists_out.append( h_pass_msd_matched_ak8 );
	hists_out.append( h_pass_msd_unmatched_ak8 );
	hists_out.append( h_fail_msd_ak8 );
	hists_out.append( h_fail_msd_matched_ak8 );
	hists_out.append( h_fail_msd_unmatched_ak8 );

	return hists_out

mass=[50,75,100,125,150,200,250,300]#,400,500]
# mass=[100]#,400,500]

outfile=TFile("hist_1DZqq-matchtest.root", "recreate");
# outfile=TFile("test.root", "recreate");

#lumi =34.100
lumi = 2.27
SF_tau21 =1

f_h2ddt = TFile("../../analysis/ZqqJet/h3_n2ddt.root");
print("Opened file ... ")
trans_h2ddt = f_h2ddt.Get("h2ddt");
trans_h2ddt.SetDirectory(0)
f_h2ddt.Close()

data_hists = createHist(trans_h2ddt,'data_obs','JetHTReReco_B',15,1,0,True)
qcd_hists = createHist(trans_h2ddt,'qcd','QCD',1,lumi,0)
tqq_hists = createHist(trans_h2ddt,'tqq','TTJets_13TeV_1000pb_weighted',1,lumi,0)
wqq_hists = createHist(trans_h2ddt,'wqq','WJetsToQQ_HT_600ToInf_13TeV_1000pb_weighted',1,lumi,80.)
zqq_hists = createHist(trans_h2ddt,'zqq','DYJetsToQQ_HT180_13TeV_1000pb_weighted',1,lumi,91.)


for m in mass:
	hs_hists = createHist(trans_h2ddt,'zqq%s'%(m),'VectorDiJet1Jet_M%s_1000pb_weighted'%(m),1,lumi,m)
	outfile.cd()
	for h in hs_hists: h.Write();

print("Building pass/fail")	
outfile.cd()
for h in data_hists: h.Write();
for h in qcd_hists: h.Write();
for h in tqq_hists: h.Write();
for h in wqq_hists: h.Write();
for h in zqq_hists: h.Write();
outfile.Write()
outfile.Close()

