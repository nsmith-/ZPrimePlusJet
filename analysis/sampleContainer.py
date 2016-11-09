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

    def __init__( self , fn, sf = 1, lumi = 1, isData = False, fillCA15=False ):

        self._fn = fn
        self._tf = ROOT.TFile.Open(self._fn[0])
        self._tt = ROOT.TChain('otree')
        for fn in self._fn: self._tt.Add(fn)
        self._sf = sf
        self._lumi = lumi
	print lumi 
	#print self._NEv.GetBinContent(1)
        if isData:
            self._lumi = 1
        self._fillCA15 = fillCA15;

        # define histograms
        self.h_n_ak4             = ROOT.TH1F("h_n_ak4","; AK4 n_{jets};", 20, 0, 20)
	self.h_n_ak4_fwd             = ROOT.TH1F("h_n_ak4fwd","; AK4 n_{jets} fwd;", 20, 0, 20)
	self.h_n_ak4L             = ROOT.TH1F("h_n_ak4L","; AK4 n_{jets} CSV>CSVL;", 20, 0, 20)
	self.h_n_ak4M             = ROOT.TH1F("h_n_ak4M","; AK4 n_{jets} CSV>CSVM;", 20, 0, 20)
	self.h_n_ak4T             = ROOT.TH1F("h_n_ak4T","; AK4 n_{jets} CSV>CSVT;", 20, 0, 20)
        self.h_n_ak4_dR0p8       = ROOT.TH1F("h_n_ak4_dR0p8","; AK4 n_{jets} #Delta R > 0.8;", 20, 0, 20)
	self.h_isolationCA15     = ROOT.TH1F("h_isolationCA15","; AK8/CA15 p_{T} ;", 50, 0.5, 1.5) 
        
        self.h_pt_ak8            = ROOT.TH1F("h_pt_ak8","; AK8 p_{T} [GeV];", 100, 300, 3000)
        self.h_pt_ak8_dbtagCut   = ROOT.TH1F("h_pt_ak8_dbtagCut","; AK8 p_{T} [GeV];", 100, 300, 3000)
        self.h_msd_ak8           = ROOT.TH1F("h_msd_ak8","; AK8 m_{SD}^{PUPPI} [GeV];", 60, 0, 600)
        self.h_msd_ak8_dbtagCut  = ROOT.TH1F("h_msd_ak8_dbtagCut","; AK8 m_{SD}^{PUPPI} [GeV];", 60, 0, 600)
        self.h_msd_ak8_t21ddtCut = ROOT.TH1F("h_msd_ak8_t21ddtCut","; m_{SD}^{PUPPI} [GeV];", 57, 30, 600)
	self.h_msd_ak8_N2Cut = ROOT.TH1F("h_msd_ak8_N2Cut","; m_{SD}^{PUPPI} [GeV];", 57, 30, 600)
        self.h_dbtag_ak8         = ROOT.TH1F("h_dbtag_ak8","; double b-tag;", 40, -1, 1)
        self.h_t21_ak8           = ROOT.TH1F("h_t21_ak8","; AK8 #tau_{21};", 25, 0, 1.5)
        self.h_t21ddt_ak8        = ROOT.TH1F("h_t21ddt_ak8","; AK8 #tau_{21};", 25, 0, 1.5)
        self.h_rhop_v_t21_ak8    = ROOT.TH2F("h_rhop_v_t21_ak8","; AK8 rho^{DDT}; AK8 <#tau_{21}>",15,-5,10,25,0,1.5)
        self.h_t32_ak8           = ROOT.TH1F("h_t32_ak8","; AK8 #tau_{32};", 25, 0, 1.5)
        self.h_n2b1sd_ak8        = ROOT.TH1F("h_n2b1sd_ak8","; AK8 N_{2}^{1}(SD);", 25, 0, 0.5)
        self.h_n2b1sdddt_ak8     = ROOT.TH1F("h_n2b1sdddt_ak8","; AK8 N_{2}^{1}(SD);", 25, 0, 1)

        self.h_pt_ca15            = ROOT.TH1F("h_pt_ca15","; CA15 p{T} [GeV];", 100, 300, 3000)
        self.h_msd_ca15           = ROOT.TH1F("h_msd_ca15","; CA15 m_{SD}^{PUPPI} [GeV];", 60, 0, 600)
        self.h_msd_ca15_t21ddtCut = ROOT.TH1F("h_msd_ca15_t21ddtCut","; CA15 m_{SD}^{PUPPI} [GeV];", 57, 30, 600)
        self.h_t21_ca15           = ROOT.TH1F("h_t21_ca15","; CA15 #tau_{21};", 25, 0, 1.5)
        self.h_t21ddt_ca15        = ROOT.TH1F("h_t21ddt_ca15","; CA15 #tau_{21};", 25, 0, 1.5)
        self.h_rhop_v_t21_ca15    = ROOT.TH2F("h_rhop_v_t21_ca15","; CA15 rho^{DDT}; CA15 <#tau_{21}>",15,-5,10,25,0,1.5)
	self.h_msd_ak8_N2Cut.Sumw2()
	self.h_n_ak4_fwd.Sumw2();    
 	self.h_n_ak4L.Sumw2();       
 	self.h_n_ak4M.Sumw2();
 	self.h_n_ak4T.Sumw2();       
	self.h_isolationCA15.Sumw2();

        self.h_pt_ak8.Sumw2(); self.h_msd_ak8.Sumw2(); self.h_t21_ak8.Sumw2()
        self.h_pt_ca15.Sumw2(); self.h_msd_ca15.Sumw2(); self.h_t21_ca15.Sumw2()
        self.h_msd_ak8_t21ddtCut.Sumw2(); self.h_t21ddt_ak8.Sumw2(); self.h_rhop_v_t21_ak8.Sumw2()
        self.h_msd_ca15_t21ddtCut.Sumw2(); self.h_t21ddt_ca15.Sumw2(); self.h_rhop_v_t21_ca15.Sumw2()
        self.h_dbtag_ak8.Sumw2(); self.h_msd_ak8_dbtagCut.Sumw2(); self.h_pt_ak8_dbtagCut.Sumw2()
        self.h_n_ak4.Sumw2(); self.h_n_ak4_dR0p8.Sumw2()
        
        # loop
        self.loop()
        
    def loop( self ):
        # looping
        nent = self._tt.GetEntries()
        for i in range(self._tt.GetEntries()):

            if i % self._sf != 0: continue
            # if i > 100000: break
            
            self._tt.GetEntry(i)
            
            if(i % (1 * nent/100) == 0):
                sys.stdout.write("\r[" + "="*int(20*i/nent) + " " + str(round(100.*i/nent,0)) + "% done")
                sys.stdout.flush()


            puweight = self._tt.puWeight
            fbweight = self._tt.scale1fb * self._lumi
            weight = puweight*fbweight*self._sf

            jmsd_8 = self._tt.AK8Puppijet0_msd
            jpt_8  = self._tt.AK8Puppijet0_pt
            if jmsd_8 <= 0: jmsd_8 = 0.01
            rh_8 = math.log(jmsd_8*jmsd_8/jpt_8/jpt_8)
            rhP_8 = math.log(jmsd_8*jmsd_8/jpt_8)
            jt21_8 = self._tt.AK8Puppijet0_tau21
            jt32_8 = self._tt.AK8Puppijet0_tau32
            jt21P_8 = jt21_8 + 0.063*rhP_8
            jtN2b1sd_8 = self._tt.AK8Puppijet0_N2sdb1
            n2slope = 0.025;
            jtN2b1sdddt_8 = jtN2b1sd_8 + (9.00067e-05)*jpt_8 + n2slope*rh_8;
            if rh_8 < -3: jtN2b1sdddt_8 = jtN2b1sd_8 + (9.00067e-05)*jpt_8;

            jdb_8 = self._tt.AK8CHSjet0_doublecsv
            
            n_4 = self._tt.nAK4Puppijets
            n_dR0p8_4 = self._tt.nAK4PuppijetsdR08
            
            if self._tt.AK8Puppijet0_pt > 500 and self._tt.AK8Puppijet0_msd >50: 
                self.h_pt_ak8.Fill( jpt_8, weight )
                self.h_msd_ak8.Fill( jmsd_8, weight )
                self.h_dbtag_ak8.Fill( jdb_8, weight )
                self.h_t21_ak8.Fill( jt21_8, weight )		
                self.h_t32_ak8.Fill( jt32_8, weight )		
                self.h_t21ddt_ak8.Fill( jt21P_8, weight )										
                self.h_rhop_v_t21_ak8.Fill( rhP_8, jt21_8, weight )
                self.h_n2b1sd_ak8.Fill(jtN2b1sd_8,weight);
                self.h_n2b1sdddt_ak8.Fill(jtN2b1sdddt_8,weight);
                self.h_n_ak4.Fill( n_4, weight )
                self.h_n_ak4_dR0p8.Fill( n_dR0p8_4, weight )
		self.h_n_ak4_fwd.Fill( self._tt.nAK4Puppijetsfwd  , weight )
		self.h_n_ak4L.Fill(    self._tt.nAK4PuppijetsLdR08, weight )
		self.h_n_ak4M.Fill(    self._tt.nAK4PuppijetsMdR08    , weight )
		self.h_n_ak4T.Fill(    self._tt.nAK4PuppijetsTdR08 , weight )     
		self.h_isolationCA15.Fill(    self._tt.AK8Puppijet0_ratioCA15_04 , weight )
	

            if self._tt.AK8Puppijet0_pt > 500 and jt21P_8 < 0.4 and self._tt.AK8Puppijet0_msd >50:
                self.h_msd_ak8_t21ddtCut.Fill( jmsd_8, weight )
	
	    if self._tt.AK8Puppijet0_pt > 500 and jtN2b1sdddt_8 < 0.45 and self._tt.AK8Puppijet0_msd >50:
                self.h_msd_ak8_N2Cut.Fill( jmsd_8, weight )

            if self._tt.AK8Puppijet0_pt > 500 and jdb_8 > 0.9 and self._tt.AK8Puppijet0_msd >50:
                self.h_msd_ak8_dbtagCut.Fill( jmsd_8, weight )
                self.h_pt_ak8_dbtagCut.Fill( jpt_8, weight )

            ##### CA15 info
            if not self._fillCA15: continue;

            jmsd_15 = self._tt.CA15Puppijet0_msd
            jpt_15  = self._tt.CA15Puppijet0_pt
            if jmsd_15 <= 0: jmsd_15 = 0.01
            rhP_15  = math.log(jmsd_15*jmsd_15/jpt_15)   
            jt21_15 = self._tt.CA15Puppijet0_tau21               
            jt21P_15 = jt21_15 + 0.075*rhP_15

            if self._tt.CA15Puppijet0_pt > 500: 
                self.h_pt_ca15.Fill( jpt_15, weight )               
                self.h_msd_ca15.Fill( jmsd_15, weight )
                self.h_t21_ca15.Fill(jt21_15, weight )          
                self.h_t21ddt_ca15.Fill(jt21P_15, weight )          
                self.h_rhop_v_t21_ca15.Fill( rhP_15, jt21_15, weight )

            if self._tt.CA15Puppijet0_pt > 500 and jt21P_15 < 0.4:
                self.h_msd_ca15_t21ddtCut.Fill( jmsd_15, weight )
            #####

        print "\n"
        self.h_rhop_v_t21_ak8_Px = self.h_rhop_v_t21_ak8.ProfileX()
        self.h_rhop_v_t21_ca15_Px = self.h_rhop_v_t21_ca15.ProfileX()
        self.h_rhop_v_t21_ak8_Px.SetTitle("; rho^{DDT}; <#tau_{21}>")
        self.h_rhop_v_t21_ca15_Px.SetTitle("; rho^{DDT}; <#tau_{21}>")


##########################################################################################



