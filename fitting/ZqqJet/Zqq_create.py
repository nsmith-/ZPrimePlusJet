import os
import math
import array
import optparse
import ROOT
import warnings
from ROOT import *
import sys

massbins = 100;
masslo   = 0;
masshi   = 500;
DY_SF    = 1.35;
def createHist(trans_h2ddt,puw,trig_eff,tag,filename,sf,lumi,mass,isdata=False,cutFormula='1'):
	
	massbins = 100;
	masslo   = 0;
	masshi   = 500;

	pt_binBoundaries = [500,600,700,800,900,1000]
	h_pass_ak8 = TH2F(tag+"_pass","; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)",massbins,masslo,masshi,len(pt_binBoundaries)-1, array.array('d',pt_binBoundaries))
	h_fail_ak8 = TH2F(tag+"_fail","; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)",massbins,masslo,masshi,len(pt_binBoundaries)-1, array.array('d',pt_binBoundaries))
	h_pass_matched_ak8 = TH2F(tag+"_pass_matched","; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)",massbins,masslo,masshi,len(pt_binBoundaries)-1, array.array('d',pt_binBoundaries))
	h_pass_unmatched_ak8 = TH2F(tag+"_pass_unmatched","; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)",massbins,masslo,masshi,len(pt_binBoundaries)-1, array.array('d',pt_binBoundaries))
	h_fail_matched_ak8 = TH2F(tag+"_fail_matched","; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)",massbins,masslo,masshi,len(pt_binBoundaries)-1, array.array('d',pt_binBoundaries))
	h_fail_unmatched_ak8 = TH2F(tag+"_fail_unmatched","; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)",massbins,masslo,masshi,len(pt_binBoundaries)-1, array.array('d',pt_binBoundaries))
	
	 # validation
	h_pass_msd_ak8 = TH1F(tag+"pass_msd", "; AK8 m_{SD}^{PUPPI}; N", 40, 0, 200)
	h_fail_msd_ak8 = TH1F(tag+"fail_msd", "; AK8 m_{SD}^{PUPPI}; N", 40, 0, 200)
	h_pass_msd_matched_ak8 = TH1F(tag+"pass_msd_matched", "; AK8 m_{SD}^{PUPPI}; N", 40, 0, 200)
	h_pass_msd_unmatched_ak8 = TH1F(tag+"pass_msd_unmatched", "; AK8 m_{SD}^{PUPPI}; N", 40, 0, 200)
	h_fail_msd_matched_ak8 = TH1F(tag+"fail_msd_matched", "; AK8 m_{SD}^{PUPPI}; N", 40, 0, 200)
	h_fail_msd_unmatched_ak8 = TH1F(tag+"fail_msd_unmatched", "; AK8 m_{SD}^{PUPPI}; N", 40, 0, 200)
	
	 # msd corr
	corrGEN = ROOT.TF1("corrGEN","[0]+[1]*pow(x*[2],-[3])",200,3500)
	corrGEN.SetParameter(0,1.00626)
	corrGEN.SetParameter(1, -1.06161)
	corrGEN.SetParameter(2,0.0799900)
	corrGEN.SetParameter(3,1.20454)
	
	corrRECO_cen = ROOT.TF1("corrRECO_cen","[0]+[1]*x+[2]*pow(x,2)+[3]*pow(x,3)+[4]*pow(x,4)+[5]*pow(x,5)",200,3500)
	corrRECO_cen.SetParameter(0,1.09302)
	corrRECO_cen.SetParameter(1,-0.000150068)
	corrRECO_cen.SetParameter(2,3.44866e-07)
	corrRECO_cen.SetParameter(3,-2.68100e-10)
	corrRECO_cen.SetParameter(4,8.67440e-14)
	corrRECO_cen.SetParameter(5,-1.00114e-17)
	
	corrRECO_for = ROOT.TF1("corrRECO_for","[0]+[1]*x+[2]*pow(x,2)+[3]*pow(x,3)+[4]*pow(x,4)+[5]*pow(x,5)",200,3500)
	corrRECO_for.SetParameter(0,1.27212)
	corrRECO_for.SetParameter(1,-0.000571640)
	corrRECO_for.SetParameter(2,8.37289e-07)
	corrRECO_for.SetParameter(3,-5.20433e-10)
	corrRECO_for.SetParameter(4,1.45375e-13)
	corrRECO_for.SetParameter(5,-1.50389e-17)
	 
	 # open files
	if 'VectorDiJet' in filename:
		sklimpath="/afs/cern.ch/user/c/cmantill/work/public/Bacon/CMSSW_7_4_7/src/inputs/ZPrimePlusJet/sklimming/signals0213/"
		infile=ROOT.TFile(sklimpath+filename+".root")
		print(sklimpath+filename+".root")
		tree= infile.Get("otree")
	else:
		sklimpath="/eos/cms/store/group/phys_exotica/dijet/dazsle/zprimebits-v12.03/sklimZqq/"
		infile=ROOT.TFile(sklimpath+filename+".root")	
		print(sklimpath+filename+".root")
		tree= infile.Get("otree2")
	nent = tree.GetEntries();
	
	warnings.filterwarnings( action='ignore', category=RuntimeWarning, message='creating converter.*' )
	cutFormula = ROOT.TTreeFormula("cutFormula",cutFormula,tree)
	tree.SetNotify(cutFormula)
	for i in range(tree.GetEntries()):
		
		if i % sf != 0: continue
		
		tree.LoadTree(i)
		selected = False
		for j in range(cutFormula.GetNdata()):
			if (cutFormula.EvalInstance(j)):
				selected = True
				break
		if not selected: continue 		
		
		tree.GetEntry(i)
		if(i % (1 * nent/100) == 0):
			sys.stdout.write("\r[" + "="*int(20*i/nent) + " " + str(round(100.*i/nent,0)) + "% done")
			sys.stdout.flush()

		puweight = puw.GetBinContent(puw.FindBin(tree.npu));
		fbweight = tree.scale1fb * lumi
		vjetsKF = 1

		# NLO corrections and k-factors
		genBosonPtMin=150; genBosonPtMax=1000;
		bosonpt = tree.genVPt
		f_kfactors = ROOT.TFile.Open("data/kfactors.root")
		hQCD_Z = f_kfactors.Get('ZJets_012j_NLO/nominal')
		hQCD_W = f_kfactors.Get('WJets_012j_NLO/nominal')
		hLO_Z = f_kfactors.Get('ZJets_LO/inv_pt')
		hLO_W = f_kfactors.Get('WJets_LO/inv_pt')
		hEWK_Z = f_kfactors.Get('EWKcorr/Z')
		hEWK_W = f_kfactors.Get('EWKcorr/W')
		hQCD_Z.SetDirectory(0)
		hQCD_W.SetDirectory(0)
		hLO_Z.SetDirectory(0)
		hLO_W.SetDirectory(0)
		hEWK_Z.SetDirectory(0)
                hEWK_W.SetDirectory(0)
		genBosonPtMin = hQCD_Z.GetBinCenter(1);
		genBosonPtMax = hQCD_Z.GetBinCenter(hQCD_Z.GetNbinsX())
		if bosonpt < genBosonPtMin: bosonpt = genBosonPtMin
		if bosonpt > genBosonPtMax: bosonpt = genBosonPtMax
		hEWK_Z.Divide(hQCD_Z);
		hEWK_W.Divide(hQCD_W);
		hQCD_Z.Divide(hLO_Z);
		hQCD_W.Divide(hLO_W);
		if 'VectorDiJet' in filename:
			qcdKF = hQCD_Z.GetBinContent(hQCD_Z.FindBin(bosonpt));
			vjetsKF = qcdKF
		elif 'WJets' in filename:
			qcdKF = hQCD_W.GetBinContent(hQCD_W.FindBin(bosonpt));
			ewkKF = hEWK_W.GetBinContent(hEWK_W.FindBin(bosonpt));
			vjetsKF = qcdKF*ewkKF
		elif 'DYJets' in filename:
			qcdKF = hQCD_Z.GetBinContent(hQCD_Z.FindBin(bosonpt));
			ewkKF = hEWK_Z.GetBinContent(hEWK_Z.FindBin(bosonpt));
			vjetsKF = DY_SF*ewkKF
		else:
			vjetsKF = 1
			 
		 # Trigger weight
		massForTrig =  min(tree.AK8Puppijet0_msd, 300. )
		ptForTrig =  max(200., min(tree.AK8Puppijet0_pt  , 1000. ))
		trigweight = trig_eff.GetEfficiency(trig_eff.FindFixBin(massForTrig,ptForTrig))
		if trigweight<=0:
			trigweight = 1
			
		weight = puweight*fbweight*sf*vjetsKF*trigweight
		
		if isdata: 
			weight = 1
			
		jeta_8 = tree.AK8Puppijet0_eta
		jpt_8  = tree.AK8Puppijet0_pt
		
		genCorr  = 1.
		recoCorr = 1.
		totalWeight = 1.
		 
		genCorr =  corrGEN.Eval( jpt_8 )
		if( abs(jeta_8)  < 1.3 ):
			recoCorr = corrRECO_cen.Eval( jpt_8 );
		else:
			recoCorr = corrRECO_for.Eval( jpt_8 );
		totalWeight = genCorr*recoCorr
		
		jmsd_8_raw = tree.AK8Puppijet0_msd
		jmsd_8 = tree.AK8Puppijet0_msd*totalWeight
		if jmsd_8 <= 0: jmsd_8 = 0.01
		if jmsd_8_raw <= 0: jmsd_8_raw = 0.01
		 
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
		if tree.neleLoose == 0 and tree.nmuLoose == 0 and tree.ntau==0 and tree.AK8Puppijet0_isTightVJet ==1:
				
			cutN2 = 0.

			# pass category
			if tree.AK8Puppijet0_pt > 500 and jtN2b1sdddt_8 < cutN2:
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
			if tree.AK8Puppijet0_pt > 500 and jtN2b1sdddt_8 > cutN2:
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

mass=[50,75,100,125,150,200,250,300]

outfile=TFile("histInputs/hist_1DZqq-dataReRecoSpring165eff-3481-Gridv13-sig-pt5006007008009001000_msd_all_newk.root", "recreate");

lumi =34.81

# puweights
f_pu= ROOT.TFile.Open("data/puWeights_All.root","read")
puw      = f_pu.Get("puw")

# trigger efficiency
f_trig = ROOT.TFile.Open("data/RUNTriggerEfficiencies_SingleMuon_Run2016_V2p1_v03.root","read")
trig_denom = f_trig.Get("DijetTriggerEfficiencySeveralTriggers/jet1SoftDropMassjet1PtDenom_cutJet")
trig_numer = f_trig.Get("DijetTriggerEfficiencySeveralTriggers/jet1SoftDropMassjet1PtPassing_cutJet")
trig_denom.SetDirectory(0)
trig_numer.SetDirectory(0)
trig_denom.RebinX(2)
trig_numer.RebinX(2)
trig_denom.RebinY(5)
trig_numer.RebinY(5)        
trig_eff = ROOT.TEfficiency()
if (ROOT.TEfficiency.CheckConsistency(trig_numer,trig_denom)):
	trig_eff = ROOT.TEfficiency(trig_numer,trig_denom)
	trig_eff.SetDirectory(0)
f_trig.Close()

# n2ddt
f_h2ddt = TFile("data/GridOutput_v13.root");
print("Opened file ... ")
trans_h2ddt = f_h2ddt.Get("Rho2D");
trans_h2ddt.SetDirectory(0)
f_h2ddt.Close()

wqq_hists = createHist(trans_h2ddt,puw,trig_eff,'wqq','WJetsToQQ_HT180_13TeV_1000pb_weighted',1,lumi,80.)
zqq_hists = createHist(trans_h2ddt,puw,trig_eff,'zqq','DYJetsToQQ_HT180_13TeV_1000pb_weighted',1,lumi,91.)
#qcd_hists = createHist(trans_h2ddt,puw,trig_eff,'qcd','QCD',1,lumi,0)
#tqq_hists = createHist(trans_h2ddt,puw,trig_eff,'tqq','TT_powheg_1000pb_weighted',1,lumi,0)
stqq_hists = createHist(trans_h2ddt,puw,trig_eff,'stqq','ST',1,lumi,0)
#data_hists = createHist(trans_h2ddt,puw,trig_eff,'data_obs','JetHT',1,1,0,True,'((triggerBits&2)&&passJson)')

hs_hists = {}
for m in mass:
	hs_hists[m]= []
	hs_hists[m] = createHist(trans_h2ddt,puw,trig_eff,'zqq%s'%str(m),'VectorDiJet1Jet_M%s_1000pb_weighted'%str(m),1,lumi,m)
	'''
	f2   = TFile("hist_1DZqq-dataReRecoSpring165eff-3481-Gridv13-sig-pt5006007008009001000_msd_all.root");
	hs_hists[m].append(f2.Get("zqq%s_pass"%m))
        hs_hists[m].append(f2.Get("zqq%s_pass_matched"%m))
        hs_hists[m].append(f2.Get("zqq%s_pass_unmatched"%m))
        hs_hists[m].append(f2.Get("zqq%s_fail"%m))
        hs_hists[m].append(f2.Get("zqq%s_fail_matched"%m))
        hs_hists[m].append(f2.Get("zqq%s_fail_unmatched"%m))
        hs_hists[m].append(f2.Get("zqq%s_fail_unmatched"%m))
	for h in hs_hists[m]: h.SetDirectory(0)
	f2.Close()
	'''

# pick from existent hists
data_hists = []
qcd_hists = []
tqq_hists = []
f2   = TFile("hist_1DZqq-dataReRecoSpring165eff-3481-Gridv13-sig-pt5006007008009001000_msd.root");
data_hists.append(f2.Get("data_obs_pass"))
data_hists.append(f2.Get("data_obs_pass_matched"))
data_hists.append(f2.Get("data_obs_pass_unmatched"))
data_hists.append(f2.Get("data_obs_fail"))
data_hists.append(f2.Get("data_obs_fail_matched"))
data_hists.append(f2.Get("data_obs_fail_unmatched"))
qcd_hists.append(f2.Get("qcd_pass"))
qcd_hists.append(f2.Get("qcd_pass_matched"))
qcd_hists.append(f2.Get("qcd_pass_unmatched"))
qcd_hists.append(f2.Get("qcd_fail"))
qcd_hists.append(f2.Get("qcd_fail_matched"))
qcd_hists.append(f2.Get("qcd_fail_unmatched"))
tqq_hists.append(f2.Get("tqq_pass"))
tqq_hists.append(f2.Get("tqq_pass_matched"))
tqq_hists.append(f2.Get("tqq_pass_unmatched"))
tqq_hists.append(f2.Get("tqq_fail"))
tqq_hists.append(f2.Get("tqq_fail_matched"))
tqq_hists.append(f2.Get("tqq_fail_unmatched"))
for h in data_hists: h.SetDirectory(0)
for h in qcd_hists: h.SetDirectory(0)
for h in tqq_hists: h.SetDirectory(0)
f2.Close()

print("Building pass/fail")	
outfile.cd()
for hs in hs_hists: 
	for h in hs_hists[hs]:
		h.Write()
for h in data_hists: h.Write();
for h in qcd_hists: h.Write();
for h in tqq_hists: h.Write();
for h in wqq_hists: h.Write();
for h in zqq_hists: h.Write();
for h in stqq_hists: h.Write();
outfile.Write()
outfile.Close()

