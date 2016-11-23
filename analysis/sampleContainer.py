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
        self._isData = isData
        #print lumi 
        #print self._NEv.GetBinContent(1)
        if isData:
            self._lumi = 1
        self._fillCA15 = fillCA15

        # define histograms
        self.h_n_ak4              = ROOT.TH1F("h_n_ak4","; AK4 n_{jets};", 20, 0, 20)
        self.h_n_ak4_fwd          = ROOT.TH1F("h_n_ak4fwd","; AK4 n_{jets}, 2.5<|#eta|<4.5;", 20, 0, 20)
        self.h_n_ak4L             = ROOT.TH1F("h_n_ak4L","; AK4 n_{L b-tags}, #DeltaR > 0.8;", 20, 0, 20)
        self.h_n_ak4M             = ROOT.TH1F("h_n_ak4M","; AK4 n_{M b-tags}, #DeltaR > 0.8;", 20, 0, 20)
        self.h_n_ak4T             = ROOT.TH1F("h_n_ak4T","; AK4 n_{T b-tags}, #DeltaR > 0.8;", 20, 0, 20)
        self.h_n_ak4_dR0p8        = ROOT.TH1F("h_n_ak4_dR0p8","; AK4 n_{jets}, #DeltaR > 0.8;", 20, 0, 20)
        self.h_isolationCA15      = ROOT.TH1F("h_isolationCA15","; AK8/CA15 p_{T} ratio ;", 50, 0.5, 1.5) 
        self.h_met                = ROOT.TH1F("h_met","; E_{T}^{miss} [GeV] ;", 50, 0, 500)

        self.h_pt_ak8             = ROOT.TH1F("h_pt_ak8","; AK8 p_{T} [GeV];", 50, 300, 2100)
        self.h_pt_ak8_dbtagCut    = ROOT.TH1F("h_pt_ak8_dbtagCut","; AK8 p_{T} [GeV];", 45, 300, 2100)
        self.h_msd_ak8            = ROOT.TH1F("h_msd_ak8","; AK8 m_{SD}^{PUPPI} [GeV];", 35,50,400)
        self.h_msd_ak8_dbtagCut   = ROOT.TH1F("h_msd_ak8_dbtagCut","; AK8 m_{SD}^{PUPPI} [GeV];", 35,50,400)
        self.h_msd_ak8_t21ddtCut  = ROOT.TH1F("h_msd_ak8_t21ddtCut","; m_{SD}^{PUPPI} [GeV];", 35,50,400)
        self.h_msd_ak8_N2Cut      = ROOT.TH1F("h_msd_ak8_N2Cut","; m_{SD}^{PUPPI} [GeV];", 35,50,400)
        self.h_dbtag_ak8          = ROOT.TH1F("h_dbtag_ak8","; double b-tag;", 40, -1, 1)
        self.h_t21_ak8            = ROOT.TH1F("h_t21_ak8","; AK8 #tau_{21};", 25, 0, 1.5)
        self.h_t21ddt_ak8         = ROOT.TH1F("h_t21ddt_ak8","; AK8 #tau_{21};", 25, 0, 1.5)
        self.h_rhop_v_t21_ak8     = ROOT.TH2F("h_rhop_v_t21_ak8","; AK8 rho^{DDT}; AK8 <#tau_{21}>",15,-5,10,25,0,1.5)
        self.h_t32_ak8            = ROOT.TH1F("h_t32_ak8","; AK8 #tau_{32};", 25, 0, 1.5)
        self.h_t32_ak8_t21ddtCut  = ROOT.TH1F("h_t32_ak8_t21ddtCut","; AK8 #tau_{32};", 20, 0, 1.5)
        self.h_n2b1sd_ak8         = ROOT.TH1F("h_n2b1sd_ak8","; AK8 N_{2}^{1} (SD);", 25, 0, 0.5)
        self.h_n2b1sdddt_ak8      = ROOT.TH1F("h_n2b1sdddt_ak8","; AK8 N_{2}^{1,DDT} (SD);", 25, 0, 1)
        self.h_msd_ak8_topR1      = ROOT.TH1F("h_msd_ak8_topR1","; AK8 m_{SD}^{PUPPI} [GeV];", 35,50,400)
        self.h_msd_ak8_topR2      = ROOT.TH1F("h_msd_ak8_topR2","; AK8 m_{SD}^{PUPPI} [GeV];", 35,50,400)
        self.h_msd_ak8_topR3      = ROOT.TH1F("h_msd_ak8_topR3","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400)
        self.h_msd_ak8_topR4      = ROOT.TH1F("h_msd_ak8_topR4","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400)
        self.h_msd_ak8_topR5      = ROOT.TH1F("h_msd_ak8_topR5","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400)
        self.h_msd_ak8_topR6      = ROOT.TH1F("h_msd_ak8_topR6","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400)

        self.h_pt_ca15            = ROOT.TH1F("h_pt_ca15","; CA15 p{T} [GeV];", 100, 300, 3000)
        self.h_msd_ca15           = ROOT.TH1F("h_msd_ca15","; CA15 m_{SD}^{PUPPI} [GeV];", 35,50,400)
        self.h_msd_ca15_t21ddtCut = ROOT.TH1F("h_msd_ca15_t21ddtCut","; CA15 m_{SD}^{PUPPI} [GeV];", 35,50,400)
        self.h_t21_ca15           = ROOT.TH1F("h_t21_ca15","; CA15 #tau_{21};", 25, 0, 1.5)
        self.h_t21ddt_ca15        = ROOT.TH1F("h_t21ddt_ca15","; CA15 #tau_{21};", 25, 0, 1.5)
        self.h_rhop_v_t21_ca15    = ROOT.TH2F("h_rhop_v_t21_ca15","; CA15 rho^{DDT}; CA15 <#tau_{21}>",15,-5,10,25,0,1.5)
        self.h_msd_ak8_N2Cut.Sumw2()
        self.h_t32_ak8_t21ddtCut.Sumw2()
        self.h_n_ak4_fwd.Sumw2()    
        self.h_n_ak4L.Sumw2()       
        self.h_n_ak4M.Sumw2()
        self.h_n_ak4T.Sumw2()       
        self.h_isolationCA15.Sumw2()
        self.h_msd_ak8_topR1.Sumw2()
        self.h_msd_ak8_topR2.Sumw2()
        self.h_msd_ak8_topR3.Sumw2()
        self.h_msd_ak8_topR4.Sumw2()
        self.h_msd_ak8_topR5.Sumw2()
        self.h_msd_ak8_topR6.Sumw2()

        self.h_pt_ak8.Sumw2(); self.h_msd_ak8.Sumw2(); self.h_t21_ak8.Sumw2()
        self.h_pt_ca15.Sumw2(); self.h_msd_ca15.Sumw2(); self.h_t21_ca15.Sumw2()
        self.h_msd_ak8_t21ddtCut.Sumw2(); self.h_t21ddt_ak8.Sumw2(); self.h_rhop_v_t21_ak8.Sumw2()
        self.h_msd_ca15_t21ddtCut.Sumw2(); self.h_t21ddt_ca15.Sumw2(); self.h_rhop_v_t21_ca15.Sumw2()
        self.h_dbtag_ak8.Sumw2(); self.h_msd_ak8_dbtagCut.Sumw2(); self.h_pt_ak8_dbtagCut.Sumw2()
        self.h_n_ak4.Sumw2(); self.h_n_ak4_dR0p8.Sumw2()
        self.h_met.Sumw2()

        # loop
        self.loop()

    def loop( self ):
        # looping
        nent = self._tt.GetEntries()
        print nent
        for i in range(self._tt.GetEntries()):
            if i % self._sf != 0: continue
                        
            self._tt.GetEntry(i)
            
            if(i % (1 * nent/100) == 0):
                sys.stdout.write("\r[" + "="*int(20*i/nent) + " " + str(round(100.*i/nent,0)) + "% done")
                sys.stdout.flush()


            puweight = self._tt.puWeight
            fbweight = self._tt.scale1fb * self._lumi
            weight = puweight*fbweight*self._sf

            # Trigger (for JetHT triggerBits& 2 or in this case triggerBits!=1 )
            #if self._isData and self._tt.triggerBits !=1: continue

            # Lepton and photon veto
            if self._tt.neleLoose != 0 or self._tt.nmuLoose != 0 or self._tt.ntau != 0 or self._tt.nphoLoose != 0:  continue

            ##### AK8 info
            jmsd_8 = self._tt.AK8Puppijet0_msd
            jpt_8  = self._tt.AK8Puppijet0_pt
            if jmsd_8 <= 0: jmsd_8 = 0.01
            rh_8 = math.log(jmsd_8*jmsd_8/jpt_8/jpt_8)
            rhP_8 = math.log(jmsd_8*jmsd_8/jpt_8)
            jt21_8 = self._tt.AK8Puppijet0_tau21
            jt32_8 = self._tt.AK8Puppijet0_tau32
            jt21P_8 = jt21_8 + 0.063*rhP_8
            jtN2b1sd_8 = self._tt.AK8Puppijet0_N2sdb1

            # N2DDT transformation
            f_h2ddt = ROOT.TFile("analysis/ZqqJet/h3_n2ddt.root");
            trans_h2ddt = f_h2ddt.Get("h2ddt");
            trans_h2ddt.SetDirectory(0);
            f_h2ddt.Close()
            cur_rho_index = trans_h2ddt.GetXaxis().FindBin(rh_8);
            cur_pt_index  = trans_h2ddt.GetYaxis().FindBin(jpt_8);
            if rh_8 > trans_h2ddt.GetXaxis().GetBinUpEdge( trans_h2ddt.GetXaxis().GetNbins() ): cur_rho_index = trans_h2ddt.GetXaxis().GetNbins();
            if rh_8 < trans_h2ddt.GetXaxis().GetBinLowEdge( 1 ): cur_rho_index = 1;
            if jpt_8 > trans_h2ddt.GetYaxis().GetBinUpEdge( trans_h2ddt.GetYaxis().GetNbins() ): cur_pt_index = trans_h2ddt.GetYaxis().GetNbins();
            if jpt_8 < trans_h2ddt.GetYaxis().GetBinLowEdge( 1 ): cur_pt_index = 1;
            jtN2b1sdddt_8 = jtN2b1sd_8 - trans_h2ddt.GetBinContent(cur_rho_index,cur_pt_index);

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
                self.h_n2b1sdddt_ak8.Fill(jtN2b1sdddt_8,weight)
                self.h_n_ak4.Fill( (n_4-self._tt.nAK4Puppijetsfwd), weight )
                self.h_n_ak4_dR0p8.Fill( n_dR0p8_4, weight )
                self.h_n_ak4_fwd.Fill( self._tt.nAK4Puppijetsfwd  , weight )
                self.h_n_ak4L.Fill(    self._tt.nAK4PuppijetsLdR08, weight )
                self.h_n_ak4M.Fill(    self._tt.nAK4PuppijetsMdR08    , weight )
                self.h_n_ak4T.Fill(    self._tt.nAK4PuppijetsTdR08 , weight )
                self.h_isolationCA15.Fill(    self._tt.AK8Puppijet0_ratioCA15_04 , weight )
                self.h_met.Fill(self._tt.pfmet, weight)

            if self._tt.AK8Puppijet0_pt > 500 and jt21P_8 < 0.4 and self._tt.AK8Puppijet0_msd >50:
                self.h_msd_ak8_t21ddtCut.Fill( jmsd_8, weight )
	        self.h_t32_ak8_t21ddtCut.Fill( jt32_8, weight )

            if self._tt.AK8Puppijet0_pt > 500 and jtN2b1sdddt_8 < 0 and self._tt.AK8Puppijet0_msd >50:
                self.h_msd_ak8_N2Cut.Fill( jmsd_8, weight )

            if self._tt.AK8Puppijet0_pt > 500  and self._tt.AK8Puppijet0_msd >50 and self._tt.pfmet < 180 and self._tt.nAK4PuppijetsdR08 <5 and self._tt.nAK4PuppijetsTdR08 < 3:
                self.h_msd_ak8_topR1.Fill( jmsd_8, weight )
            if self._tt.AK8Puppijet0_pt > 500  and self._tt.AK8Puppijet0_msd >50 and self._tt.pfmet < 180 and self._tt.nAK4PuppijetsdR08 <5 and self._tt.nAK4PuppijetsTdR08 < 3 and  jdb_8 > 0.9 :
                self.h_msd_ak8_topR2.Fill( jmsd_8, weight )
            if self._tt.AK8Puppijet0_pt > 500  and self._tt.AK8Puppijet0_msd >40 and self._tt.pfmet < 180 and self._tt.nAK4PuppijetsdR08 <5 and self._tt.nAK4PuppijetsTdR08 < 3 and  jdb_8 > 0.9  and jt21P_8 < 0.4 :
                self.h_msd_ak8_topR3.Fill( jmsd_8, weight )
            if self._tt.AK8Puppijet0_pt > 500  and self._tt.AK8Puppijet0_msd >40  and  jdb_8 > 0.9  and jt21P_8 < 0.4 and jt32_8 > 0.7:
                self.h_msd_ak8_topR4.Fill( jmsd_8, weight )
            if self._tt.AK8Puppijet0_pt > 500  and self._tt.AK8Puppijet0_msd >40 and self._tt.pfmet < 180 and self._tt.nAK4PuppijetsdR08 <5 and self._tt.nAK4PuppijetsTdR08 < 3 and  jdb_8 > 0.9  and jt21P_8 < 0.55 :
                self.h_msd_ak8_topR5.Fill( jmsd_8, weight )
            if self._tt.AK8Puppijet0_pt > 500  and self._tt.AK8Puppijet0_msd >40 and self._tt.pfmet < 180 and self._tt.nAK4PuppijetsdR08 <5 and self._tt.nAK4PuppijetsTdR08 < 3 and  jdb_8 > 0.95  and jt21P_8 < 0.55 :
                self.h_msd_ak8_topR6.Fill( jmsd_8, weight )

            if self._tt.AK8Puppijet0_pt > 500 and jdb_8 > 0.9 and self._tt.AK8Puppijet0_msd >50:
                self.h_msd_ak8_dbtagCut.Fill( jmsd_8, weight )
                self.h_pt_ak8_dbtagCut.Fill( jpt_8, weight )

            ##### CA15 info
            if not self._fillCA15: continue

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



