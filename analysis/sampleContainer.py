import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array
import warnings

#########################################################################################################
class sampleContainer:

    def __init__( self ,name, fn, sf = 1, lumi = 1, isData = False, fillCA15=False, cutFormula='1'):
        self._name = name
        self._fn = fn
        self._tf = ROOT.TFile.Open(self._fn[0])
        self._tt = ROOT.TChain('otree')
        for fn in self._fn: self._tt.Add(fn)
        self._sf = sf
        self._lumi = lumi        
        warnings.filterwarnings( action='ignore', category=RuntimeWarning, message='creating converter.*' )
        self._cutFormula = ROOT.TTreeFormula("cutFormula",cutFormula,self._tt)
        self._isData = isData
        #print lumi 
        #print self._NEv.GetBinContent(1)
        if isData:
            self._lumi = 1
        self._fillCA15 = fillCA15

        # get histogram for transform
        f_h2ddt = ROOT.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ZqqJet/h3_n2ddt.root","read")
        self._trans_h2ddt = f_h2ddt.Get("h2ddt")
        self._trans_h2ddt.SetDirectory(0)
        f_h2ddt.Close()

        # set branch statuses and addresses
        self._branches = [('AK8Puppijet0_msd','d',-999),('AK8Puppijet0_pt','d',-999),('AK8Puppijet0_tau21','d',-999),('AK8Puppijet0_tau32','d',-999),
                          ('AK8Puppijet0_N2sdb1','d',-999),('puWeight','f',0),('scale1fb','f',0),('AK8CHSjet0_doublecsv','d',-999),('AK8CHSjet1_doublecsv','d',-999),
                          ('AK8CHSjet2_doublecsv','i',-999),('nAK4Puppijets','i',-999),('nAK4PuppijetsdR08','i',-999),('nAK4Puppijetsfwd','i',-999),
                          ('nAK4PuppijetsLdR08','i',-999),('nAK4PuppijetsMdR08','i',-999),('nAK4PuppijetsTdR08','i',-999),('nAK4PuppijetsLPt100dR08','i',-999),
                          ('nAK4PuppijetsMPt100dR08','i',-999),('nAK4PuppijetsTPt100dR08','i',-999),('AK8Puppijet1_pt','d',-999),('AK8Puppijet2_pt','d',-999),
                          ('AK8Puppijet0_ratioCA15_04','d',-999),('pfmet','f',-999),('neleLoose','i',-999),('nmuLoose','i',-999),('ntau','i',-999),('nphoLoose','i',-999),
                          ('triggerBits','i',1),('passJson','i',1),('vmuoLoose0_pt','d',-999),('AK8Puppijet1_msd','d',-999),('AK8Puppijet2_msd','d',-999),
                          ('nAK4PuppijetsLPt150dR08','i',-999),('nAK4PuppijetsMPt150dR08','i',-999),('nAK4PuppijetsTPt150dR08','i',-999),('AK8Puppijet0_isTightVJet','i',0)
                          ]
        if not self._isData:
            self._branches.extend( [ ('genMuFromW','i',-999),('genEleFromW','i',-999),('genTauFromW','i',-999) ] )
            
        if self._fillCA15:
            self._branches.extend( [ ('CA15Puppijet0_msd','d',-999),('CA15Puppijet0_pt','d',-999),('CA15Puppijet0_tau21','d',-999) ] )

        self._tt.SetBranchStatus("*",0)
        for branch in self._branches:
            self._tt.SetBranchStatus(branch[0],1)
        for branch in self._branches:
            setattr(self, branch[0], array.array(branch[1],[branch[2]]))
            self._tt.SetBranchAddress( branch[0], getattr(self, branch[0]) )

        #x = array.array('d',[0])
        #self._tt.SetBranchAddress( "h_n_ak4", n_ak4  )

        # define histograms        
        histos1d = {
        'h_n_ak4'              :["h_"+self._name+"_n_ak4","; AK4 n_{jets}, p_{T} > 30 GeV;", 20, 0, 20],     
        'h_pt_bbleading'       :["h_"+self._name+"_pt_bbleading","; AK8 leading p_{T} [GeV];", 50, 300, 2100],
        'h_bb_bbleading'       :["h_"+self._name+"_bb_bbleading","; bb ;", 40, -1, 1],
        'h_msd_bbleading'      :["h_"+self._name+"_msd_bbleading","AK8 m_{SD}^{PUPPI} [GeV];", 48,40,400],
        'h_n_ak4_fwd'          :["h_"+self._name+"_n_ak4fwd","; AK4 n_{jets}, p_{T} > 30 GeV, 2.5<|#eta|<4.5;", 20, 0, 20],
        'h_n_ak4L'             :["h_"+self._name+"_n_ak4L","; AK4 n_{L b-tags}, #DeltaR > 0.8, p_{T} > 40 GeV;", 20, 0, 20],
        'h_n_ak4L100'          :["h_"+self._name+"_n_ak4L100","; AK4 n_{L b-tags}, #DeltaR > 0.8, p_{T} > 100 GeV;", 10, 0, 10],
        'h_n_ak4L150'          :["h_"+self._name+"_n_ak4L150","; AK4 n_{L b-tags}, #DeltaR > 0.8, p_{T} > 150 GeV;", 10, 0, 10],
        'h_n_ak4M'             :["h_"+self._name+"_n_ak4M","; AK4 n_{M b-tags}, #DeltaR > 0.8, p_{T} > 40 GeV;", 20, 0, 20],
        'h_n_ak4M100'          :["h_"+self._name+"_n_ak4M100","; AK4 n_{M b-tags}, #DeltaR > 0.8, p_{T} > 100 GeV;", 10, 0, 10],
        'h_n_ak4M150'          :["h_"+self._name+"_n_ak4M150","; AK4 n_{M b-tags}, #DeltaR > 0.8, p_{T} > 150 GeV;", 10, 0, 10],
        'h_n_ak4T'             :["h_"+self._name+"_n_ak4T","; AK4 n_{T b-tags}, #DeltaR > 0.8, p_{T} > 40 GeV;", 20, 0, 20],
        'h_n_ak4T100'          :["h_"+self._name+"_n_ak4T100","; AK4 n_{T b-tags}, #DeltaR > 0.8, p_{T} > 100 GeV;", 10, 0, 10],
        'h_n_ak4T150'          :["h_"+self._name+"_n_ak4T150","; AK4 n_{T b-tags}, #DeltaR > 0.8, p_{T} > 150 GeV;", 10, 0, 10],
        'h_n_ak4_dR0p8'        :["h_"+self._name+"_n_ak4_dR0p8","; AK4 n_{jets}, #DeltaR > 0.8, p_{T} > 30 GeV;", 20, 0, 20],
        'h_isolationCA15'      :["h_"+self._name+"_isolationCA15","; AK8/CA15 p_{T} ratio ;", 50, 0.5, 1.5], 
        'h_met'                :["h_"+self._name+"_met","; E_{T}^{miss} [GeV] ;", 50, 0, 500],
        'h_pt_ak8'             :["h_"+self._name+"_pt_ak8","; AK8 leading p_{T} [GeV];", 50, 300, 2100],
        'h_pt_ak8_sub1'        :["h_"+self._name+"_pt_ak8_sub1","; AK8 subleading p_{T} [GeV];", 50, 300, 2100],
        'h_pt_ak8_sub2'        :["h_"+self._name+"_pt_ak8_sub2","; AK8 3rd leading p_{T} [GeV];", 50, 300, 2100],
        'h_pt_ak8_dbtagCut'    :["h_"+self._name+"_pt_ak8_dbtagCut","; AK8 leading p_{T} [GeV];", 45, 300, 2100],
        'h_msd_ak8'            :["h_"+self._name+"_msd_ak8","; AK8 m_{SD}^{PUPPI} [GeV];", 48,40,400],
        'h_msd_ak8_dbtagCut'   :["h_"+self._name+"_msd_ak8_dbtagCut","; AK8 m_{SD}^{PUPPI} [GeV];", 30,40,400],
        'h_msd_ak8_t21ddtCut'  :["h_"+self._name+"_msd_ak8_t21ddtCut","; m_{SD}^{PUPPI} [GeV];", 30,40,400],
        'h_msd_ak8_N2Cut'      :["h_"+self._name+"_msd_ak8_N2Cut","; m_{SD}^{PUPPI} [GeV];", 30,40,400],
        'h_dbtag_ak8'          :["h_"+self._name+"_dbtag_ak8","; leading double b-tag;", 40, -1, 1],
        'h_dbtag_ak8_sub1'     :["h_"+self._name+"_dbtag_ak8_sub1","; subleading double b-tag;", 40, -1, 1],
        'h_dbtag_ak8_sub2'     :["h_"+self._name+"_dbtag_ak8_sub2","; 3rd leading double b-tag;", 40, -1, 1],
        'h_t21_ak8'            :["h_"+self._name+"_t21_ak8","; AK8 #tau_{21};", 25, 0, 1.5],
        'h_t21ddt_ak8'         :["h_"+self._name+"_t21ddt_ak8","; AK8 #tau_{21}^{DDT};", 25, 0, 1.5],
        'h_t32_ak8'            :["h_"+self._name+"_t32_ak8","; AK8 #tau_{32};", 25, 0, 1.5],
        'h_t32_ak8_t21ddtCut'  :["h_"+self._name+"_t32_ak8_t21ddtCut","; AK8 #tau_{32};", 20, 0, 1.5],
        'h_n2b1sd_ak8'         :["h_"+self._name+"_n2b1sd_ak8","; AK8 N_{2}^{1} (SD);", 25, 0, 0.5],
        'h_n2b1sdddt_ak8'      :["h_"+self._name+"_n2b1sdddt_ak8","; AK8 N_{2}^{1,DDT} (SD);", 25, 0, 1],
        'h_msd_ak8_topR1'      :["h_"+self._name+"_msd_ak8_topR1","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_topR2_pass' :["h_"+self._name+"_msd_ak8_topR2_pass","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_topR3_pass' :["h_"+self._name+"_msd_ak8_topR3_pass","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_topR4_pass' :["h_"+self._name+"_msd_ak8_topR4_pass","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_topR5_pass' :["h_"+self._name+"_msd_ak8_topR5_pass","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_topR6_pass' :["h_"+self._name+"_msd_ak8_topR6_pass","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_topR7_pass' :["h_"+self._name+"_msd_ak8_topR7_pass","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_topR2_fail' :["h_"+self._name+"_msd_ak8_topR2_fail","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_topR3_fail' :["h_"+self._name+"_msd_ak8_topR3_fail","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_topR4_fail' :["h_"+self._name+"_msd_ak8_topR4_fail","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_topR5_fail' :["h_"+self._name+"_msd_ak8_topR5_fail","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_topR6_fail' :["h_"+self._name+"_msd_ak8_topR6_fail","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_topR7_fail' :["h_"+self._name+"_msd_ak8_topR7_fail","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_muCR1'      :["h_"+self._name+"_msd_ak8_muCR1","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_muCR2'      :["h_"+self._name+"_msd_ak8_muCR2","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_muCR3'      :["h_"+self._name+"_msd_ak8_muCR3","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_muCR4'      :["h_"+self._name+"_msd_ak8_muCR4","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_muCR5'      :["h_"+self._name+"_msd_ak8_muCR5","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_msd_ak8_muCR6'      :["h_"+self._name+"_msd_ak8_muCR6","; AK8 m_{SD}^{PUPPI} [GeV];", 24,40,400],
        'h_pt_ca15'            :["h_"+self._name+"_pt_ca15","; CA15 p{T} [GeV];", 100, 300, 3000],
        'h_msd_ca15'           :["h_"+self._name+"_msd_ca15","; CA15 m_{SD}^{PUPPI} [GeV];", 35,50,400],
        'h_msd_ca15_t21ddtCut' :["h_"+self._name+"_msd_ca15_t21ddtCut","; CA15 m_{SD}^{PUPPI} [GeV];", 35,50,400],
        'h_t21_ca15'           :["h_"+self._name+"_t21_ca15","; CA15 #tau_{21};", 25, 0, 1.5],
        'h_t21ddt_ca15'        :["h_"+self._name+"_t21ddt_ca15","; CA15 #tau_{21};", 25, 0, 1.5]
        }
        histos2d = {
        'h_rhop_v_t21_ak8'          :["h_"+self._name+"_rhop_v_t21_ak8","; AK8 rho^{DDT}; AK8 <#tau_{21}>",15,-5,10,25,0,1.5],
        'h_rhop_v_t21_ca15'         :["h_"+self._name+"_rhop_v_t21_ca15","; CA15 rho^{DDT}; CA15 <#tau_{21}>",15,-5,10,25,0,1.5],
        'h_msd_v_pt_ak8_topR1'      :["h_"+self._name+"_msd_v_pt_ak8_topR1","; AK8 m_{SD}^{PUPPI} [GeV]; AK8 p_{T} [GeV]", 75,0,500,5,500,1000],
        'h_msd_v_pt_ak8_topR2_pass' :["h_"+self._name+"_msd_v_pt_ak8_topR2_pass","; AK8 m_{SD}^{PUPPI} [GeV]; AK8 p_{T} [GeV]", 75,0,500,5,500,1000],
        'h_msd_v_pt_ak8_topR3_pass' :["h_"+self._name+"_msd_v_pt_ak8_topR3_pass","; AK8 m_{SD}^{PUPPI} [GeV]; AK8 p_{T} [GeV]", 75,0,500,5,500,1000],
        'h_msd_v_pt_ak8_topR4_pass' :["h_"+self._name+"_msd_v_pt_ak8_topR4_pass","; AK8 m_{SD}^{PUPPI} [GeV]; AK8 p_{T} [GeV]", 75,0,500,5,500,1000],
        'h_msd_v_pt_ak8_topR5_pass' :["h_"+self._name+"_msd_v_pt_ak8_topR5_pass","; AK8 m_{SD}^{PUPPI} [GeV]; AK8 p_{T} [GeV]", 75,0,500,5,500,1000],
        'h_msd_v_pt_ak8_topR6_pass' :["h_"+self._name+"_msd_v_pt_ak8_topR6_pass","; AK8 m_{SD}^{PUPPI} [GeV]; AK8 p_{T} [GeV]", 75,0,500,5,500,1000],
        'h_msd_v_pt_ak8_topR7_pass' :["h_"+self._name+"_msd_v_pt_ak8_topR7_pass","; AK8 m_{SD}^{PUPPI} [GeV]; AK8 p_{T} [GeV]", 75,0,500,5,500,1000],
        'h_msd_v_pt_ak8_topR2_fail' :["h_"+self._name+"_msd_v_pt_ak8_topR2_fail","; AK8 m_{SD}^{PUPPI} [GeV]; AK8 p_{T} [GeV]", 75,0,500,5,500,1000],
        'h_msd_v_pt_ak8_topR3_fail' :["h_"+self._name+"_msd_v_pt_ak8_topR3_fail","; AK8 m_{SD}^{PUPPI} [GeV]; AK8 p_{T} [GeV]", 75,0,500,5,500,1000],
        'h_msd_v_pt_ak8_topR4_fail' :["h_"+self._name+"_msd_v_pt_ak8_topR4_fail","; AK8 m_{SD}^{PUPPI} [GeV]; AK8 p_{T} [GeV]", 75,0,500,5,500,1000],
        'h_msd_v_pt_ak8_topR5_fail' :["h_"+self._name+"_msd_v_pt_ak8_topR5_fail","; AK8 m_{SD}^{PUPPI} [GeV]; AK8 p_{T} [GeV]", 75,0,500,5,500,1000],
        'h_msd_v_pt_ak8_topR6_fail' :["h_"+self._name+"_msd_v_pt_ak8_topR6_fail","; AK8 m_{SD}^{PUPPI} [GeV]; AK8 p_{T} [GeV]", 75,0,500,5,500,1000],
        'h_msd_v_pt_ak8_topR7_fail' :["h_"+self._name+"_msd_v_pt_ak8_topR7_fail","; AK8 m_{SD}^{PUPPI} [GeV]; AK8 p_{T} [GeV]", 75,0,500,5,500,1000]
        }
            
        for key, val in histos1d.iteritems():
            setattr( self, key, ROOT.TH1F(val[0], val[1], val[2] ,val[3], val[4]) )
            (getattr(self, key)).Sumw2()
        for key, val in histos2d.iteritems():
            setattr( self, key, ROOT.TH2F(val[0], val[1], val[2] ,val[3], val[4], val[5], val[6], val[7]) )
            (getattr(self, key)).Sumw2()

        # loop
        self.loop()

    def loop( self ):
        # looping
        nent = self._tt.GetEntries()
        print nent

        self._tt.SetNotify(self._cutFormula)
        for i in xrange(nent):
            if i % self._sf != 0: continue

            #self._tt.LoadEntry(i)
            self._tt.LoadTree(i)
            selected = False
            for j in range(self._cutFormula.GetNdata()):
                if (self._cutFormula.EvalInstance(j)):
                    selected = True
                    break
            if not selected: continue 
            
            self._tt.GetEntry(i)
            
            if(i % (1 * nent/100) == 0):
                sys.stdout.write("\r[" + "="*int(20*i/nent) + " " + str(round(100.*i/nent,0)) + "% done")
                sys.stdout.flush()

            
            puweight = self.puWeight[0]
            fbweight = self.scale1fb[0] * self._lumi
            weight = puweight*fbweight*self._sf

            # Trigger (for JetHT triggerBits& 2 or in this case triggerBits!=1 )
            #if self._isData and self._tt.triggerBits !=1: continue


            ##### AK8 info
            jmsd_8 = self.AK8Puppijet0_msd[0]
            jpt_8  = self.AK8Puppijet0_pt[0]
            jpt_8_sub1  = self.AK8Puppijet1_pt[0]
            jpt_8_sub2  = self.AK8Puppijet2_pt[0]
            if jmsd_8 <= 0: jmsd_8 = 0.01
            rh_8 = math.log(jmsd_8*jmsd_8/jpt_8/jpt_8)
            rhP_8 = math.log(jmsd_8*jmsd_8/jpt_8)
            jt21_8 = self.AK8Puppijet0_tau21[0]
            jt32_8 = self.AK8Puppijet0_tau32[0]
            jt21P_8 = jt21_8 + 0.063*rhP_8
            jtN2b1sd_8 = self.AK8Puppijet0_N2sdb1[0]

            # N2DDT transformation
            cur_rho_index = self._trans_h2ddt.GetXaxis().FindBin(rh_8)
            cur_pt_index  = self._trans_h2ddt.GetYaxis().FindBin(jpt_8)
            if rh_8 > self._trans_h2ddt.GetXaxis().GetBinUpEdge( self._trans_h2ddt.GetXaxis().GetNbins() ): cur_rho_index = self._trans_h2ddt.GetXaxis().GetNbins()
            if rh_8 < self._trans_h2ddt.GetXaxis().GetBinLowEdge( 1 ): cur_rho_index = 1
            if jpt_8 > self._trans_h2ddt.GetYaxis().GetBinUpEdge( self._trans_h2ddt.GetYaxis().GetNbins() ): cur_pt_index = self._trans_h2ddt.GetYaxis().GetNbins()
            if jpt_8 < self._trans_h2ddt.GetYaxis().GetBinLowEdge( 1 ): cur_pt_index = 1
            jtN2b1sdddt_8 = jtN2b1sd_8 - self._trans_h2ddt.GetBinContent(cur_rho_index,cur_pt_index)

            jdb_8 = self.AK8CHSjet0_doublecsv[0]
            if self.AK8CHSjet1_doublecsv[0] > 1:
                jdb_8_sub1=-99
            else:
                jdb_8_sub1 = self.AK8CHSjet1_doublecsv[0]
            if self.AK8CHSjet2_doublecsv[0] > 1:
                jdb_8_sub2=-99
            else:
                jdb_8_sub2 = self.AK8CHSjet2_doublecsv[0]
            
            n_4 = self.nAK4Puppijets[0]
            n_fwd_4 =  self.nAK4Puppijetsfwd[0]
            n_dR0p8_4 = self.nAK4PuppijetsdR08[0]
            n_LdR0p8_4 = self.nAK4PuppijetsLdR08[0]
            n_MdR0p8_4 = self.nAK4PuppijetsMdR08[0]
            n_TdR0p8_4 = self.nAK4PuppijetsTdR08[0]
            n_LPt100dR0p8_4 = self.nAK4PuppijetsLPt100dR08[0]
            n_MPt100dR0p8_4 = self.nAK4PuppijetsMPt100dR08[0]
            n_TPt100dR0p8_4 = self.nAK4PuppijetsTPt100dR08[0]
            n_LPt150dR0p8_4 = self.nAK4PuppijetsLPt150dR08[0]
            n_MPt150dR0p8_4 = self.nAK4PuppijetsMPt150dR08[0]
            n_TPt150dR0p8_4 = self.nAK4PuppijetsTPt150dR08[0]

            met = self.pfmet[0]
            ratioCA15_04 = self.AK8Puppijet0_ratioCA15_04[0]

            ntau = self.ntau[0]
            nmuLoose = self.nmuLoose[0]
            neleLoose = self.neleLoose[0]
            nphoLoose = self.nphoLoose[0]
            isTightVJet = self.AK8Puppijet0_isTightVJet[0]

            vmuoLoose0_pt = self.vmuoLoose0_pt[0]
            # Single Muon Control Region 1 (inclusive)
            if jpt_8 > 500 and jmsd_8 >40 and nmuLoose>=1 and neleLoose==0 and nphoLoose==0 and ntau==0 and vmuoLoose0_pt>50 :
                self.h_msd_ak8_muCR1.Fill( jmsd_8, weight )
                if jdb_8 > 0.9:
                    self.h_msd_ak8_muCR2.Fill( jmsd_8, weight )
                if jt21P_8 < 0.4:
                    self.h_msd_ak8_muCR3.Fill( jmsd_8, weight )
                if jdb_8 > 0.9 and jt21P_8 < 0.4:
                    self.h_msd_ak8_muCR4.Fill( jmsd_8, weight )
                if jdb_8 > 0.7 and jt21P_8 < 0.4:
                    self.h_msd_ak8_muCR5.Fill( jmsd_8, weight )
                if jdb_8 > 0.7 and jt21P_8 < 0.55:
                    self.h_msd_ak8_muCR6.Fill( jmsd_8, weight )

            # Lepton and photon veto
            if neleLoose != 0 or nmuLoose != 0 or ntau != 0 or nphoLoose != 0:  continue
            bb_idx = [[jmsd_8,jpt_8,jdb_8],[self.AK8Puppijet1_msd[0],jpt_8_sub1,jdb_8_sub1],[self.AK8Puppijet2_msd[0],jpt_8_sub2,jdb_8_sub2]]
            a = 0
            for i in sorted(bb_idx, key=lambda bbtag: bbtag[2], reverse=True):
                if a > 0 : continue
                a = a+1
                if  i[2] > 0.9   and i[0]> 40 and i[1]>500:
                    self.h_msd_bbleading.Fill( i[0], weight )
                    #print sorted(bb_idx, key=lambda bbtag: bbtag[2],reverse=True)
                    self.h_pt_bbleading.Fill( i[1], weight )
                    #print(i[0],i[1],i[2])
                    self.h_bb_bbleading.Fill( i[2], weight )
	
 
            if jpt_8 > 500 and jmsd_8 > 40: 
                self.h_pt_ak8.Fill( jpt_8, weight )
                self.h_pt_ak8_sub1.Fill( jpt_8_sub1, weight )
                self.h_pt_ak8_sub2.Fill( jpt_8_sub2, weight )
                self.h_msd_ak8.Fill( jmsd_8, weight )
                self.h_dbtag_ak8.Fill( jdb_8, weight )
                self.h_dbtag_ak8_sub1.Fill( jdb_8_sub1, weight )
                self.h_dbtag_ak8_sub2.Fill( jdb_8_sub2, weight )
                self.h_t21_ak8.Fill( jt21_8, weight )		
                self.h_t32_ak8.Fill( jt32_8, weight )		
                self.h_t21ddt_ak8.Fill( jt21P_8, weight )									
                self.h_rhop_v_t21_ak8.Fill( rhP_8, jt21_8, weight )
                self.h_n2b1sd_ak8.Fill(jtN2b1sd_8,weight)
                self.h_n2b1sdddt_ak8.Fill(jtN2b1sdddt_8,weight)
                self.h_n_ak4.Fill( n_4 , weight )
                self.h_n_ak4_dR0p8.Fill( n_dR0p8_4, weight )
                self.h_n_ak4_fwd.Fill( n_fwd_4  , weight )
                self.h_n_ak4L.Fill(    n_LdR0p8_4, weight )
                self.h_n_ak4L100.Fill(    n_LPt100dR0p8_4, weight )
                self.h_n_ak4M.Fill(    n_MdR0p8_4    , weight )
                self.h_n_ak4M100.Fill(   n_MPt100dR0p8_4, weight )
                self.h_n_ak4T.Fill(    n_TdR0p8_4 , weight )
                self.h_n_ak4T100.Fill(    n_TPt100dR0p8_4, weight )
                self.h_n_ak4L150.Fill(    n_LPt150dR0p8_4, weight )
                self.h_n_ak4M150.Fill(   n_MPt150dR0p8_4, weight )
                self.h_n_ak4T150.Fill(    n_TPt150dR0p8_4, weight )
                self.h_isolationCA15.Fill(    ratioCA15_04 , weight )
                self.h_met.Fill(met, weight)

            if jpt_8 > 500 and jt21P_8 < 0.4 and jmsd_8 > 40:
                self.h_msd_ak8_t21ddtCut.Fill( jmsd_8, weight )
	        self.h_t32_ak8_t21ddtCut.Fill( jt32_8, weight )

            if jpt_8 > 500 and jtN2b1sdddt_8 < 0 and jmsd_8 > 40:
                self.h_msd_ak8_N2Cut.Fill( jmsd_8, weight )

            if jpt_8 > 500 and jmsd_8 > 40 and met < 180 and n_dR0p8_4 <5 and n_TdR0p8_4 < 3 and isTightVJet:
                self.h_msd_ak8_topR1.Fill( jmsd_8, weight )
                self.h_msd_v_pt_ak8_topR1.Fill( jmsd_8, jpt_8, weight )
            if jpt_8 > 500 and jmsd_8 > 40 and met < 180 and n_dR0p8_4 <5 and n_TdR0p8_4 < 3 and isTightVJet:
                if jdb_8 > 0.9:
                    self.h_msd_ak8_topR2_pass.Fill( jmsd_8, weight )
                    self.h_msd_v_pt_ak8_topR2_pass.Fill( jmsd_8, jpt_8, weight )
                else:
                    self.h_msd_ak8_topR2_fail.Fill( jmsd_8, weight )
                    self.h_msd_v_pt_ak8_topR2_fail.Fill( jmsd_8, jpt_8, weight )
            if jpt_8 > 500 and jmsd_8 > 40 and met < 180 and n_dR0p8_4 <5 and n_TdR0p8_4 < 3 and jt21P_8 < 0.4 and isTightVJet:
                if jdb_8 > 0.9:
                    self.h_msd_ak8_topR3_pass.Fill( jmsd_8, weight )
                    self.h_msd_v_pt_ak8_topR3_pass.Fill( jmsd_8, jpt_8, weight )
                else:
                    self.h_msd_ak8_topR3_fail.Fill( jmsd_8, weight )
                    self.h_msd_v_pt_ak8_topR3_fail.Fill( jmsd_8, jpt_8, weight )
            if jpt_8 > 500 and jmsd_8 > 40 and jt21P_8 < 0.4 and jt32_8 > 0.7 and isTightVJet:
                if jdb_8 > 0.9:
                    self.h_msd_ak8_topR4_pass.Fill( jmsd_8, weight )
                    self.h_msd_v_pt_ak8_topR4_pass.Fill( jmsd_8, jpt_8, weight )
                else:
                    self.h_msd_ak8_topR4_fail.Fill( jmsd_8, weight )
                    self.h_msd_v_pt_ak8_topR4_fail.Fill( jmsd_8, jpt_8, weight )                    
            if jpt_8 > 500 and jmsd_8 > 40 and met < 180 and n_dR0p8_4 < 5 and n_TdR0p8_4 < 3 and jt21P_8 < 0.55 and isTightVJet:
                if jdb_8 > 0.9:
                    self.h_msd_ak8_topR5_pass.Fill( jmsd_8, weight )
                    self.h_msd_v_pt_ak8_topR5_pass.Fill( jmsd_8, jpt_8, weight ) 
                else:                    
                    self.h_msd_ak8_topR5_fail.Fill( jmsd_8, weight )
                    self.h_msd_v_pt_ak8_topR5_fail.Fill( jmsd_8, jpt_8, weight ) 
            if jpt_8 > 500 and jmsd_8 > 40 and met < 180 and n_dR0p8_4 < 5 and n_MPt100dR0p8_4 < 2 and jt21P_8 < 0.55 and n_fwd_4 < 3 and isTightVJet:
                if jdb_8 > 0.9:
                    self.h_msd_ak8_topR6_pass.Fill( jmsd_8, weight )
                    self.h_msd_v_pt_ak8_topR6_pass.Fill( jmsd_8, jpt_8, weight ) 
                else:
                    self.h_msd_ak8_topR6_fail.Fill( jmsd_8, weight )
                    self.h_msd_v_pt_ak8_topR6_fail.Fill( jmsd_8, jpt_8, weight )                     
            if jpt_8 > 500 and jmsd_8 > 40 and jpt_8_sub1 < 300 and met < 180 and n_dR0p8_4 < 5 and n_TdR0p8_4 < 3 and jt21P_8 < 0.4 and isTightVJet:
                if jdb_8 > 0.9:
                    self.h_msd_ak8_topR7_pass.Fill( jmsd_8, weight )
                    self.h_msd_v_pt_ak8_topR7_pass.Fill( jmsd_8, jpt_8, weight ) 
                else:
                    self.h_msd_ak8_topR7_fail.Fill( jmsd_8, weight )
                    self.h_msd_v_pt_ak8_topR7_fail.Fill( jmsd_8, jpt_8, weight ) 

            if jpt_8 > 500 and jdb_8 > 0.9 and jmsd_8 > 40:
                self.h_msd_ak8_dbtagCut.Fill( jmsd_8, weight )
                self.h_pt_ak8_dbtagCut.Fill( jpt_8, weight )

            ##### CA15 info
            if not self._fillCA15: continue

            jmsd_15 = self.CA15Puppijet0_msd[0]
            jpt_15  = self.CA15Puppijet0_pt[0]
            if jmsd_15 <= 0: jmsd_15 = 0.01
            rhP_15  = math.log(jmsd_15*jmsd_15/jpt_15)   
            jt21_15 = self.CA15Puppijet0_tau21[0]               
            jt21P_15 = jt21_15 + 0.075*rhP_15

            if jpt_15 > 500: 
                self.h_pt_ca15.Fill( jpt_15, weight )               
                self.h_msd_ca15.Fill( jmsd_15, weight )
                self.h_t21_ca15.Fill(jt21_15, weight )          
                self.h_t21ddt_ca15.Fill(jt21P_15, weight )          
                self.h_rhop_v_t21_ca15.Fill( rhP_15, jt21_15, weight )

            if jpt_15 > 500 and jt21P_15 < 0.4:
                self.h_msd_ca15_t21ddtCut.Fill( jmsd_15, weight )
            #####
        print "\n"
        self.h_rhop_v_t21_ak8_Px = self.h_rhop_v_t21_ak8.ProfileX()
        self.h_rhop_v_t21_ca15_Px = self.h_rhop_v_t21_ca15.ProfileX()
        self.h_rhop_v_t21_ak8_Px.SetTitle("; rho^{DDT}; <#tau_{21}>")
        self.h_rhop_v_t21_ca15_Px.SetTitle("; rho^{DDT}; <#tau_{21}>")


##########################################################################################



