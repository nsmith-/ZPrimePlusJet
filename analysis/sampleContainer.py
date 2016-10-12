import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array

#########################################################################################################
class sampleContainer:
	
	def __init__( self , fn, sf = 1, lumi = 1 ):

		self._fn = fn;
		self._tf = ROOT.TFile(self._fn);
		self._tt = self._tf.Get("otree");
		self._sf = sf;
		self._lumi = lumi;

		# define histograms
		self.h_pt_ak8            = ROOT.TH1F("h_pt_ak8","; pT(GeV), AK8;", 100, 300, 3000);
		self.h_msd_ak8           = ROOT.TH1F("h_msd_ak8","; m_{SD}^{PUPPI} (AK8) (GeV);", 60, 0, 600);
		self.h_msd_ak8_t21ddtCut = ROOT.TH1F("h_msd_ak8_t21ddtCut","; m_{SD}^{PUPPI} (AK8) (GeV);", 57, 30, 600);
		self.h_t21_ak8           = ROOT.TH1F("h_t21_ak8","; #tau_{21}, AK8;", 25, 0, 1.5);
		self.h_t21ddt_ak8        = ROOT.TH1F("h_t21ddt_ak8","; #tau_{21}, AK8;", 25, 0, 1.5);
		self.h_rhop_v_t21_ak8    = ROOT.TH2F("h_rhop_v_t21_ak8","; rho^{DDT}; <#tau_{21}>",15,-5,10,25,0,1.5)

		self.h_pt_ca15            = ROOT.TH1F("h_pt_ca15","; pT(GeV), CA15;", 100, 300, 3000);
		self.h_msd_ca15           = ROOT.TH1F("h_msd_ca15","; m_{SD}^{PUPPI} (CA15) (GeV);", 60, 0, 600);
		self.h_msd_ca15_t21ddtCut = ROOT.TH1F("h_msd_ca15_t21ddtCut","; m_{SD}^{PUPPI} (CA15) (GeV);", 57, 30, 600);
		self.h_t21_ca15           = ROOT.TH1F("h_t21_ca15","; #tau_{21}, CA15;", 25, 0, 1.5);
		self.h_t21ddt_ca15        = ROOT.TH1F("h_t21ddt_ca15","; #tau_{21}, CA15;", 25, 0, 1.5);
		self.h_rhop_v_t21_ca15    = ROOT.TH2F("h_rhop_v_t21_ca15","; rho^{DDT}; <#tau_{21}>",15,-5,10,25,0,1.5)

		self.h_pt_ak8.Sumw2(); self.h_msd_ak8.Sumw2(); self.h_t21_ak8.Sumw2(); 
		self.h_pt_ca15.Sumw2(); self.h_msd_ca15.Sumw2(); self.h_t21_ca15.Sumw2();
		self.h_msd_ak8_t21ddtCut.Sumw2(); self.h_t21ddt_ak8.Sumw2(); self.h_rhop_v_t21_ak8.Sumw2();
		self.h_msd_ca15_t21ddtCut.Sumw2(); self.h_t21ddt_ca15.Sumw2(); self.h_rhop_v_t21_ca15.Sumw2();

		# loop
		self.loop();

	def loop( self ):

		# looping
		nent = self._tt.GetEntries();
		for i in range(self._tt.GetEntries()):
			
			self._tt.GetEntry(i);
			if(i % (1 * nent/100) == 0):
				sys.stdout.write("\r[" + "="*int(20*i/nent) + " " + str(round(100.*i/nent,0)) + "% done");
				sys.stdout.flush();

			if i % self._sf != 0: continue;
			# if i > 100000: break;

			puweight = self._tt.puWeight;
			fbweight = self._tt.scale1fb * self._lumi;
			weight = puweight+fbweight*self._sf;

			jmsd_8 = self._tt.AK8Puppijet0_msd;
			jpt_8  = self._tt.AK8Puppijet0_pt;
			if jmsd_8 <= 0: jmsd_8 = 0.01;
			rhP_8 = math.log(jmsd_8*jmsd_8/jpt_8); 
			jt21_8 = self._tt.AK8Puppijet0_tau21;                 
			jt21P_8 = jt21_8 + 0.063*rhP_8;

			jmsd_15 = self._tt.CA15Puppijet0_msd;
			jpt_15  = self._tt.CA15Puppijet0_pt;
			if jmsd_15 <= 0: jmsd_15 = 0.01;
			rhP_15  = math.log(jmsd_15*jmsd_15/jpt_15);   
			jt21_15 = self._tt.CA15Puppijet0_tau21               
			jt21P_15 = jt21_15 + 0.075*rhP_15;

			if self._tt.AK8Puppijet0_pt > 500: 
				self.h_pt_ak8.Fill( jpt_8, weight );
				self.h_msd_ak8.Fill( jmsd_8, weight );
				self.h_t21_ak8.Fill( jt21_8, weight );		
				self.h_t21ddt_ak8.Fill( jt21P_8, weight );										
				self.h_rhop_v_t21_ak8.Fill( rhP_8, jt21_8, weight );
			
			if self._tt.CA15Puppijet0_pt > 500: 
				self.h_pt_ca15.Fill( jpt_15, weight );				
				self.h_msd_ca15.Fill( jmsd_15, weight );
				self.h_t21_ca15.Fill(jt21_15, weight );			
				self.h_t21ddt_ca15.Fill(jt21P_15, weight );			
				self.h_rhop_v_t21_ca15.Fill( rhP_15, jt21_15, weight );

			if self._tt.AK8Puppijet0_pt > 500 and jt21P_8 < 0.4:
				self.h_msd_ak8_t21ddtCut.Fill( jmsd_8, weight );
			if self._tt.CA15Puppijet0_pt > 500 and jt21P_15 < 0.4:
				self.h_msd_ca15_t21ddtCut.Fill( jmsd_15, weight );

		print "\n";

		self.h_rhop_v_t21_ak8_Px = self.h_rhop_v_t21_ak8.ProfileX();
		self.h_rhop_v_t21_ca15_Px = self.h_rhop_v_t21_ca15.ProfileX();
		self.h_rhop_v_t21_ak8_Px.SetTitle("; rho^{DDT}; <#tau_{21}>");
		self.h_rhop_v_t21_ca15_Px.SetTitle("; rho^{DDT}; <#tau_{21}>");


##########################################################################################



