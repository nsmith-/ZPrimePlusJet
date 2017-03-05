import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import array
import scipy
import pdb
import sys
import time
import warnings
PTCUT = 300.
T21DDTCUT = 0.55
#########################################################################################################
class printEff:

    def __init__( self ,name, fn, cutFormula='1'):
        self._name = name
        self._fn = fn
        if len(fn)>0:
            self._tf = ROOT.TFile.Open(self._fn[0])
        self._tt = ROOT.TChain('Events')
        for fn in self._fn: self._tt.Add(fn)
        self.corrGEN = ROOT.TF1("corrGEN","[0]+[1]*pow(x*[2],-[3])",200,3500)
        self.corrGEN.SetParameter(0,1.00626)
        self.corrGEN.SetParameter(1, -1.06161)
        self.corrGEN.SetParameter(2,0.0799900)
        self.corrGEN.SetParameter(3,1.20454)

        self.corrRECO_cen = ROOT.TF1("corrRECO_cen","[0]+[1]*x+[2]*pow(x,2)+[3]*pow(x,3)+[4]*pow(x,4)+[5]*pow(x,5)",200,3500)
        self.corrRECO_cen.SetParameter(0,1.09302)
        self.corrRECO_cen.SetParameter(1,-0.000150068)
        self.corrRECO_cen.SetParameter(2,3.44866e-07)
        self.corrRECO_cen.SetParameter(3,-2.68100e-10)
        self.corrRECO_cen.SetParameter(4,8.67440e-14)
        self.corrRECO_cen.SetParameter(5,-1.00114e-17)

        self.corrRECO_for = ROOT.TF1("corrRECO_for","[0]+[1]*x+[2]*pow(x,2)+[3]*pow(x,3)+[4]*pow(x,4)+[5]*pow(x,5)",200,3500)
        self.corrRECO_for.SetParameter(0,1.27212)
        self.corrRECO_for.SetParameter(1,-0.000571640)
        self.corrRECO_for.SetParameter(2,8.37289e-07)
        self.corrRECO_for.SetParameter(3,-5.20433e-10)
        self.corrRECO_for.SetParameter(4,1.45375e-13)
        self.corrRECO_for.SetParameter(5,-1.50389e-17)	

	
        f_pu= ROOT.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ggH/puWeights_All.root","read")
        self._puw      = f_pu.Get("puw")
        self._puw_up   = f_pu.Get("puw_p")
        self._puw_down   = f_pu.Get("puw_m")


        # get histogram for transform
        f_h2ddt = ROOT.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/GridOutput_v13.root","read")
        self._trans_h2ddt = f_h2ddt.Get("Rho2D")
        self._trans_h2ddt.SetDirectory(0)
        f_h2ddt.Close()
	

        # set branch statuses and addresses
        self._branches = [('AK8Puppijet0_msd','d',-999),('AK8Puppijet0_pt','d',-999),
                          ('AK8Puppijet0_pt_JERUp','d',-999),('AK8Puppijet0_pt_JERDown','d',-999),
                          ('AK8Puppijet0_pt_JESUp','d',-999),('AK8Puppijet0_pt_JESDown','d',-999),
                          ('AK8Puppijet0_eta','d',-999),('AK8Puppijet0_phi','d',-999),('AK8Puppijet0_tau21','d',-999),('AK8Puppijet0_tau32','d',-999),
                          ('AK8Puppijet0_N2sdb1','d',-999),('puWeight','f',0),('scale1fb','f',0),
			  ('AK8CHSjet0_doublecsv','d',-999),
                          ('AK8Puppijet0_doublecsv','d',-999),('AK8Puppijet1_doublecsv','d',-999),
                          ('kfactor','f',0),('AK8Puppijet2_doublecsv','i',-999),('nAK4PuppijetsPt30','i',-999),
                          ('nAK4PuppijetsPt30dR08_0','i',-999),
                          ('nAK4PuppijetsPt30dR08jesUp_0','i',-999),('nAK4PuppijetsPt30dR08jesDown_0','i',-999),
                          ('nAK4PuppijetsPt30dR08jerUp_0','i',-999),('nAK4PuppijetsPt30dR08jerDown_0','i',-999),
                          ('nAK4PuppijetsfwdPt30','i',-999),
                          ('AK8Puppijet1_pt','d',-999),('AK8Puppijet2_pt','d',-999),('AK8Puppijet1_tau21','d',-999),('AK8Puppijet2_tau21','d',-999),                        
                          ('AK8Puppijet0_ratioCA15_04','d',-999),
                          ('pfmet','f',-999),('pfmetphi','f',-999),('puppet','f',-999),('puppetphi','f',-999),
                          ('MetXCorrjesUp','d',-999),('MetXCorrjesDown','d',-999),('MetYCorrjesUp','d',-999),('MetYCorrjesDown','d',-999),
                          ('MetXCorrjerUp','d',-999),('MetXCorrjerDown','d',-999),('MetYCorrjerUp','d',-999),('MetYCorrjerDown','d',-999),
                          ('neleLoose','i',-999),('nmuLoose','i',-999),('ntau','i',-999),('nphoLoose','i',-999),
                          ('AK8Puppijet1_msd','d',-999),('AK8Puppijet2_msd','d',-999),('npv','i',1),('npu','i',1), 
                          ('nAK4PuppijetsLPt150dR08_0','i',-999),('nAK4PuppijetsMPt150dR08_0','i',-999),('nAK4PuppijetsTPt150dR08_0','i',-999),
                          ('AK8Puppijet0_isTightVJet','i',0),
                          ('AK8Puppijet2_isTightVJet','i',0),('AK4Puppijet3_pt','f',0),('AK4Puppijet2_pt','f',0),('AK4Puppijet1_pt','f',0),('AK4Puppijet0_pt','f',0),
                          ('AK4Puppijet3_eta','f',0),('AK4Puppijet2_eta','f',0),('AK4Puppijet1_eta','f',0),('AK4Puppijet0_eta','f',0)
                          ]

        self._tt.SetBranchStatus("*",0)
        for branch in self._branches:
            self._tt.SetBranchStatus(branch[0],1)
        for branch in self._branches:
            setattr(self, branch[0].replace(' ', ''), array.array(branch[1],[branch[2]]))
            self._tt.SetBranchAddress( branch[0], getattr(self, branch[0].replace(' ', '')) )

        #x = array.array('d',[0])
        #self._tt.SetBranchAddress( "h_n_ak4", n_ak4  )

        # loop
        if len(fn)>0:
            self.loop()

    

    def loop( self ):
        # looping
        nent = self._tt.GetEntries()
        print nent
	cut=[]
        cut = [0.,0.,0.,0.,0.]


        for i in xrange(nent):
	
            #self._tt.LoadEntry(i)
            self._tt.LoadTree(i)
            
            self._tt.GetEntry(i)
            
            
            nPuForWeight = min(self.npu[0],49.5)
            puweight = self._puw.GetBinContent(self._puw.FindBin(nPuForWeight))
                    
            weight = puweight


            ##### AK8 info
            jmsd_8_raw = self.AK8Puppijet0_msd[0]
            jpt_8  = self.AK8Puppijet0_pt[0]            
            jeta_8  = self.AK8Puppijet0_eta[0]
            jmsd_8 = jmsd_8_raw;#self.AK8Puppijet0_msd[0]*self.PUPPIweight(jpt_8,jeta_8)
            jphi_8  = self.AK8Puppijet0_phi[0]
            if jmsd_8 <= 0: jmsd_8 = 0.01
            rh_8 = math.log(jmsd_8*jmsd_8/jpt_8/jpt_8)  #tocheck here
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
            
               
            if jpt_8 > PTCUT :
                cut[0]=cut[0]+1
            if jpt_8 > PTCUT and jmsd_8 > 65  and jmsd_8< 105 and jtN2b1sdddt_8 <0. :
                cut[1]=cut[1]+1
	    if jpt_8 > PTCUT and jmsd_8 > 105  and jmsd_8< 135 and jtN2b1sdddt_8 <0. :
                cut[2]=cut[2]+1
                        
        print "\n"
	print self._name
	print(cut[0],cut[1],cut[2])
	print(cut[1]/cut[0],cut[2]/cut[0])
                    
		


    def PUPPIweight(self,puppipt=30., puppieta=0. ):

        genCorr  = 1.
        recoCorr = 1.
        totalWeight = 1.


        genCorr =  self.corrGEN.Eval( puppipt )
        if( abs(puppieta)  < 1.3 ):
    		recoCorr = self.corrRECO_cen.Eval( puppipt )
    	else: 
            recoCorr = self.corrRECO_for.Eval( puppipt )
        totalWeight = genCorr*recoCorr
        return totalWeight

##########################################################################################



