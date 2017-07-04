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

PTCUT = 450.
PTCUTMUCR = 400.
DBTAGCUT = 0.9
T21DDTCUT = 0.55
MUONPTCUT = 55
METCUT = 140
MASSCUT = 40
NJETCUT = 100

def delta_phi(phi1, phi2):
  PI = 3.14159265359
  x = phi1 - phi2
  while x >=  PI:
      x -= ( 2*PI )
  while x <  -PI:
      x += ( 2*PI )
  return x

def delta_phi_david(phi1, phi2):
    return math.acos(math.cos(phi1 - phi2))

#########################################################################################################
class sampleContainerPhibbAK8:
    def __init__(self, name, fn, sf=1, DBTAGCUTMIN=-99., lumi=1, isData=False, fillCA15=False, cutFormula='1',
                 minBranches=False):
        self._name = name
        self.DBTAGCUTMIN = DBTAGCUTMIN
        self._fn = fn
        if len(fn) > 0:
            self._tf = ROOT.TFile.Open(self._fn[0])
        self._tt = ROOT.TChain('otree')
        for fn in self._fn: self._tt.Add(fn)
        self._sf = sf
        self._lumi = lumi
        warnings.filterwarnings(action='ignore', category=RuntimeWarning, message='creating converter.*')
        self._cutFormula = ROOT.TTreeFormula("cutFormula",
                                             "(" + cutFormula + ")&&(AK8Puppijet0_pt>%f||AK8Puppijet0_pt_JESDown>%f||AK8Puppijet0_pt_JESUp>%f||AK8Puppijet0_pt_JERUp>%f||AK8Puppijet0_pt_JERDown>%f)" % (
                                                 PTCUTMUCR, PTCUTMUCR, PTCUTMUCR, PTCUTMUCR, PTCUTMUCR), self._tt)
        self._isData = isData
        # print lumi
        # print self._NEv.GetBinContent(1)
        if isData:
            self._lumi = 1
        self._fillCA15 = fillCA15
        # based on https://github.com/thaarres/PuppiSoftdropMassCorr Summer16
        self.corrGEN = ROOT.TF1("corrGEN", "[0]+[1]*pow(x*[2],-[3])", 200, 3500)
        self.corrGEN.SetParameter(0, 1.00626)
        self.corrGEN.SetParameter(1, -1.06161)
        self.corrGEN.SetParameter(2, 0.0799900)
        self.corrGEN.SetParameter(3, 1.20454)

        self.corrRECO_cen = ROOT.TF1("corrRECO_cen", "[0]+[1]*x+[2]*pow(x,2)+[3]*pow(x,3)+[4]*pow(x,4)+[5]*pow(x,5)",
                                     200, 3500)
        self.corrRECO_cen.SetParameter(0, 1.09302)
        self.corrRECO_cen.SetParameter(1, -0.000150068)
        self.corrRECO_cen.SetParameter(2, 3.44866e-07)
        self.corrRECO_cen.SetParameter(3, -2.68100e-10)
        self.corrRECO_cen.SetParameter(4, 8.67440e-14)
        self.corrRECO_cen.SetParameter(5, -1.00114e-17)

        self.corrRECO_for = ROOT.TF1("corrRECO_for", "[0]+[1]*x+[2]*pow(x,2)+[3]*pow(x,3)+[4]*pow(x,4)+[5]*pow(x,5)",
                                     200, 3500)
        self.corrRECO_for.SetParameter(0, 1.27212)
        self.corrRECO_for.SetParameter(1, -0.000571640)
        self.corrRECO_for.SetParameter(2, 8.37289e-07)
        self.corrRECO_for.SetParameter(3, -5.20433e-10)
        self.corrRECO_for.SetParameter(4, 1.45375e-13)
        self.corrRECO_for.SetParameter(5, -1.50389e-17)

        # f_puppi= ROOT.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ZqqJet/puppiCorr.root","read")
        # self._puppisd_corrGEN      = f_puppi.Get("puppiJECcorr_gen")
        # self._puppisd_corrRECO_cen = f_puppi.Get("puppiJECcorr_reco_0eta1v3")
        # self._puppisd_corrRECO_for = f_puppi.Get("puppiJECcorr_reco_1v3eta2v5")

        f_pu = ROOT.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ggH/puWeights_All.root", "read")
        self._puw = f_pu.Get("puw")
        self._puw_up = f_pu.Get("puw_p")
        self._puw_down = f_pu.Get("puw_m")

        # get histogram for transform
        f_h2ddt = ROOT.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ZqqJet/h3_n2ddt_26eff_36binrho11pt_Spring16.root",
                                  "read")  # GridOutput_v13_WP026.root # smooth version of the ddt ; exp is 4.45 vs 4.32 (3% worse)
        self._trans_h2ddt = f_h2ddt.Get("h2ddt")
        self._trans_h2ddt.SetDirectory(0)
        f_h2ddt.Close()

        # get trigger efficiency object

        f_trig = ROOT.TFile.Open(
            "$ZPRIMEPLUSJET_BASE/analysis/ggH/RUNTriggerEfficiencies_SingleMuon_Run2016_V2p1_v03.root", "read")
        self._trig_denom = f_trig.Get("DijetTriggerEfficiencySeveralTriggers/jet1SoftDropMassjet1PtDenom_cutJet")
        self._trig_numer = f_trig.Get("DijetTriggerEfficiencySeveralTriggers/jet1SoftDropMassjet1PtPassing_cutJet")
        self._trig_denom.SetDirectory(0)
        self._trig_numer.SetDirectory(0)
        self._trig_denom.RebinX(2)
        self._trig_numer.RebinX(2)
        self._trig_denom.RebinY(5)
        self._trig_numer.RebinY(5)
        self._trig_eff = ROOT.TEfficiency()
        if (ROOT.TEfficiency.CheckConsistency(self._trig_numer, self._trig_denom)):
            self._trig_eff = ROOT.TEfficiency(self._trig_numer, self._trig_denom)
            self._trig_eff.SetDirectory(0)
        f_trig.Close()

        # get muon trigger efficiency object

        lumi_GH = 16.146
        lumi_BCDEF = 19.721
        lumi_total = lumi_GH + lumi_BCDEF

        f_mutrig_GH = ROOT.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ggH/EfficienciesAndSF_Period4.root", "read")
        self._mutrig_eff_GH = f_mutrig_GH.Get("Mu50_OR_TkMu50_PtEtaBins/efficienciesDATA/pt_abseta_DATA")
        self._mutrig_eff_GH.Sumw2()
        self._mutrig_eff_GH.SetDirectory(0)
        f_mutrig_GH.Close()

        f_mutrig_BCDEF = ROOT.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ggH/EfficienciesAndSF_RunBtoF.root", "read")
        self._mutrig_eff_BCDEF = f_mutrig_BCDEF.Get("Mu50_OR_TkMu50_PtEtaBins/efficienciesDATA/pt_abseta_DATA")
        self._mutrig_eff_BCDEF.Sumw2()
        self._mutrig_eff_BCDEF.SetDirectory(0)
        f_mutrig_BCDEF.Close()

        self._mutrig_eff = self._mutrig_eff_GH.Clone('pt_abseta_DATA_mutrig_ave')
        self._mutrig_eff.Scale(lumi_GH / lumi_total)
        self._mutrig_eff.Add(self._mutrig_eff_BCDEF, lumi_BCDEF / lumi_total)

        # get muon ID efficiency object

        f_muid_GH = ROOT.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ggH/EfficienciesAndSF_GH.root", "read")
        self._muid_eff_GH = f_muid_GH.Get("MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta/efficienciesDATA/pt_abseta_DATA")
        self._muid_eff_GH.Sumw2()
        self._muid_eff_GH.SetDirectory(0)
        f_muid_GH.Close()

        f_muid_BCDEF = ROOT.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ggH/EfficienciesAndSF_BCDEF.root", "read")
        self._muid_eff_BCDEF = f_muid_BCDEF.Get(
            "MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta/efficienciesDATA/pt_abseta_DATA")
        self._muid_eff_BCDEF.Sumw2()
        self._muid_eff_BCDEF.SetDirectory(0)
        f_muid_BCDEF.Close()

        self._muid_eff = self._muid_eff_GH.Clone('pt_abseta_DATA_muid_ave')
        self._muid_eff.Scale(lumi_GH / lumi_total)
        self._muid_eff.Add(self._muid_eff_BCDEF, lumi_BCDEF / lumi_total)

        # get muon ISO efficiency object

        f_muiso_GH = ROOT.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ggH/EfficienciesAndSF_ISO_GH.root", "read")
        self._muiso_eff_GH = f_muiso_GH.Get("LooseISO_LooseID_pt_eta/efficienciesDATA/pt_abseta_DATA")
        self._muiso_eff_GH.Sumw2()
        self._muiso_eff_GH.SetDirectory(0)
        f_muiso_GH.Close()

        f_muiso_BCDEF = ROOT.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ggH/EfficienciesAndSF_ISO_BCDEF.root", "read")
        self._muiso_eff_BCDEF = f_muiso_BCDEF.Get("LooseISO_LooseID_pt_eta/efficienciesDATA/pt_abseta_DATA")
        self._muiso_eff_BCDEF.Sumw2()
        self._muiso_eff_BCDEF.SetDirectory(0)
        f_muiso_BCDEF.Close()

        self._muiso_eff = self._muiso_eff_GH.Clone('pt_abseta_DATA_muiso_ave')
        self._muiso_eff.Scale(lumi_GH / lumi_total)
        self._muiso_eff.Add(self._muiso_eff_BCDEF, lumi_BCDEF / lumi_total)

        self._minBranches = minBranches
        # set branch statuses and addresses
        self._branches = [('AK8Puppijet0_msd', 'd', -999), ('AK8Puppijet0_pt', 'd', -999),
                          ('AK8Puppijet0_pt_JERUp', 'd', -999), ('AK8Puppijet0_pt_JERDown', 'd', -999),
                          ('AK8Puppijet0_pt_JESUp', 'd', -999), ('AK8Puppijet0_pt_JESDown', 'd', -999),
                          ('AK8Puppijet0_eta', 'd', -999), ('AK8Puppijet0_phi', 'd', -999),
                          ('AK8Puppijet0_tau21', 'd', -999), ('AK8Puppijet0_tau32', 'd', -999),
                          ('AK8Puppijet0_N2sdb1', 'd', -999), ('puWeight', 'f', 0), ('scale1fb', 'f', 0),
                          ('AK8Puppijet0_doublecsv', 'd', -999),
                          ('kfactor', 'f', 0), ('kfactorNLO', 'f', 0), ('nAK4PuppijetsPt30', 'i', -999),
                          ('nAK4PuppijetsPt30dR08_0', 'i', -999),
                          ('nAK4PuppijetsPt30dR08jesUp_0', 'i', -999), ('nAK4PuppijetsPt30dR08jesDown_0', 'i', -999),
                          ('nAK4PuppijetsPt30dR08jerUp_0', 'i', -999), ('nAK4PuppijetsPt30dR08jerDown_0', 'i', -999),
                          ('nAK4PuppijetsMPt50dR08_0', 'i', -999),
                          ('AK8Puppijet0_ratioCA15_04', 'd', -999),
                          ('pfmet', 'f', -999), ('pfmetphi', 'f', -999), ('puppet', 'f', -999),
                          ('puppetphi', 'f', -999),
                          ('MetXCorrjesUp', 'd', -999), ('MetXCorrjesDown', 'd', -999), ('MetYCorrjesUp', 'd', -999),
                          ('MetYCorrjesDown', 'd', -999),
                          ('MetXCorrjerUp', 'd', -999), ('MetXCorrjerDown', 'd', -999), ('MetYCorrjerUp', 'd', -999),
                          ('MetYCorrjerDown', 'd', -999),
                          ('neleLoose', 'i', -999), ('nmuLoose', 'i', -999), ('ntau', 'i', -999),
                          ('nphoLoose', 'i', -999),
                          ('triggerBits', 'i', 1), ('passJson', 'i', 1), ('vmuoLoose0_pt', 'd', -999),
                          ('vmuoLoose0_eta', 'd', -999), ('vmuoLoose0_phi', 'd', -999),
                          ('npv', 'i', 1), ('npu', 'i', 1),
                          ('AK8Puppijet0_isTightVJet', 'i', 0)
                          ]
        if not self._minBranches:
            self._branches.extend([('nAK4PuppijetsfwdPt30', 'i', -999), ('nAK4PuppijetsLPt50dR08_0', 'i', -999),
                                   ('nAK4PuppijetsTPt50dR08_0', 'i', -999),
                                   ('nAK4PuppijetsLPt100dR08_0', 'i', -999), ('nAK4PuppijetsMPt100dR08_0', 'i', -999),
                                   ('nAK4PuppijetsTPt100dR08_ 0', 'i', -999),
                                   ('nAK4PuppijetsLPt150dR08_0', 'i', -999), ('nAK4PuppijetsMPt150dR08_0', 'i', -999),
                                   ('nAK4PuppijetsTPt150dR08_0', 'i', -999),
                                   ('nAK4PuppijetsLPt50dR08_1', 'i', -999), ('nAK4PuppijetsMPt50dR08_1', 'i', -999),
                                   ('nAK4PuppijetsTPt50dR08_1', 'i', -999),
                                   ('nAK4PuppijetsLPt100dR08_1', 'i', -999), ('nAK4PuppijetsMPt100dR08_1', 'i', -999),
                                   ('nAK4PuppijetsTPt100dR08_ 1', 'i', -999),
                                   ('nAK4PuppijetsLPt150dR08_1', 'i', -999), ('nAK4PuppijetsMPt150dR08_1', 'i', -999),
                                   ('nAK4PuppijetsTPt150dR08_1', 'i', -999),
                                   ('nAK4PuppijetsLPt50dR08_2', 'i', -999), ('nAK4PuppijetsMPt50dR08_2', 'i', -999),
                                   ('nAK4PuppijetsTPt50dR08_2', 'i', -999),
                                   ('nAK4PuppijetsLPt100dR08_2', 'i', -999), ('nAK4PuppijetsMPt100dR08_2', 'i', -999),
                                   ('nAK4PuppijetsTPt100dR08_ 1', 'i', -999),
                                   ('nAK4PuppijetsLPt150dR08_2', 'i', -999), ('nAK4PuppijetsMPt150dR08_2', 'i', -999),
                                   ('nAK4PuppijetsTPt150dR08_2', 'i', -999),
                                   ('nAK4PuppijetsLPt150dR08_0', 'i', -999), ('nAK4PuppijetsMPt150dR08_0', 'i', -999),
                                   ('nAK4PuppijetsTPt150dR08_0', 'i', -999),
                                   ('AK8Puppijet1_pt', 'd', -999), ('AK8Puppijet2_pt', 'd', -999),
                                   ('AK8Puppijet1_tau21', 'd', -999), ('AK8Puppijet2_tau21', 'd', -999),
                                   ('AK8Puppijet1_msd', 'd', -999), ('AK8Puppijet2_msd', 'd', -999),
                                   ('AK8Puppijet1_doublecsv', 'd', -999), ('AK8Puppijet2_doublecsv', 'i', -999),
                                   ('AK8Puppijet1_isTightVJet', 'i', 0),
                                   ('AK8Puppijet2_isTightVJet', 'i', 0), ('AK4Puppijet3_pt', 'f', 0),
                                   ('AK4Puppijet2_pt', 'f', 0), ('AK4Puppijet1_pt', 'f', 0),
                                   ('AK4Puppijet0_pt', 'f', 0),
                                   ('AK4Puppijet3_eta', 'f', 0), ('AK4Puppijet2_eta', 'f', 0),
                                   ('AK4Puppijet1_eta', 'f', 0), ('AK4Puppijet0_eta', 'f', 0)
                                   ])
        if not self._isData:
            self._branches.extend([('genMuFromW', 'i', -999), ('genEleFromW', 'i', -999), ('genTauFromW', 'i', -999)])
            self._branches.extend(
                [('genVPt', 'f', -999), ('genVEta', 'f', -999), ('genVPhi', 'f', -999), ('genVMass', 'f', -999),
                 ('topPtWeight', 'f', -999), ('topPt', 'f', -999), ('antitopPt', 'f', -999)])

        if self._fillCA15:
            self._branches.extend(
                [('CA15Puppijet0_msd', 'd', -999), ('CA15Puppijet0_pt', 'd', -999), ('CA15Puppijet0_tau21', 'd', -999)])

        self._tt.SetBranchStatus("*", 0)
        for branch in self._branches:
            self._tt.SetBranchStatus(branch[0], 1)
        for branch in self._branches:
            setattr(self, branch[0].replace(' ', ''), array.array(branch[1], [branch[2]]))
            self._tt.SetBranchAddress(branch[0], getattr(self, branch[0].replace(' ', '')))

        # x = array.array('d',[0])
        # self._tt.SetBranchAddress( "h_n_ak4", n_ak4  )

        # define histograms
        histos1d = {            
            'h_npv': ["h_" + self._name + "_npv", "; number of PV;;", 100, 0, 100],
            'h_msd_ak8_topR6_N2_pass': ["h_" + self._name + "_msd_ak8_topR6_N2_pass", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_topR6_N2_pass_JESUp': ["h_" + self._name + "_msd_ak8_topR6_N2_pass_JESUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_topR6_N2_pass_JESDown': ["h_" + self._name + "_msd_ak8_topR6_N2_pass_JESDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_topR6_N2_pass_JERUp': ["h_" + self._name + "_msd_ak8_topR6_N2_pass_JERUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_topR6_N2_pass_JERDown': ["h_" + self._name + "_msd_ak8_topR6_N2_pass_JERDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_topR6_N2_fail': ["h_" + self._name + "_msd_ak8_topR6_N2_fail", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_topR6_N2_fail_JESUp': ["h_" + self._name + "_msd_ak8_topR6_N2_fail_JESUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_topR6_N2_fail_JESDown': ["h_" + self._name + "_msd_ak8_topR6_N2_fail_JESDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_topR6_N2_fail_JERUp': ["h_" + self._name + "_msd_ak8_topR6_N2_fail_JERUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_topR6_N2_fail_JERDown': ["h_" + self._name + "_msd_ak8_topR6_N2_fail_JERDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_pt_mu_muCR4_N2': ["h_" + self._name + "_pt_mu_muCR4_N2", "; leading muon p_{T} (GeV);", 50, 30, 500],
            'h_eta_mu_muCR4_N2': ["h_" + self._name + "_eta_mu_muCR4_N2", "; leading muon #eta;", 50, -2.5, 2.5],
            'h_pt_ak8_muCR4_N2': ["h_" + self._name + "_pt_ak8_muCR4_N2", "; AK8 leading p_{T} (GeV);", 50, 300, 2100],
            'h_eta_ak8_muCR4_N2': ["h_" + self._name + "_eta_ak8_muCR4_N2", "; AK8 leading #eta;", 50, -3, 3],
            'h_dbtag_ak8_muCR4_N2': ["h_" + self._name + "_dbtag_ak8_muCR4_N2", "; p_{T}-leading double b-tag;", 40, -1, 1],
            'h_t21ddt_ak8_muCR4_N2': ["h_" + self._name + "_t21ddt_ak8_muCR4_N2", "; AK8 #tau_{21}^{DDT};", 25, 0, 1.5],
            'h_msd_ak8_muCR4_N2': ["h_" + self._name + "_msd_ak8_muCR4_N2", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_pass': ["h_" + self._name + "_msd_ak8_muCR4_N2_pass", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_pass_JESUp': ["h_" + self._name + "_msd_ak8_muCR4_N2_pass_JESUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_pass_JESDown': ["h_" + self._name + "_msd_ak8_muCR4_N2_pass_JESDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_pass_JERUp': ["h_" + self._name + "_msd_ak8_muCR4_N2_pass_JERUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_pass_JERDown': ["h_" + self._name + "_msd_ak8_muCR4_N2_pass_JERDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_pass_mutriggerUp': ["h_" + self._name + "_msd_ak8_muCR4_N2_pass_mutriggerUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_pass_mutriggerDown': ["h_" + self._name + "_msd_ak8_muCR4_N2_pass_mutriggerDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_pass_muidUp': ["h_" + self._name + "_msd_ak8_muCR4_N2_pass_muidUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_pass_muidDown': ["h_" + self._name + "_msd_ak8_muCR4_N2_pass_muidDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_pass_muisoUp': ["h_" + self._name + "_msd_ak8_muCR4_N2_pass_muisoUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_pass_muisoDown': ["h_" + self._name + "_msd_ak8_muCR4_N2_pass_muisoDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_pass_PuUp': ["h_" + self._name + "_msd_ak8_muCR4_N2_pass_PuUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_pass_PuDown': ["h_" + self._name + "_msd_ak8_muCR4_N2_pass_PuDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_fail': ["h_" + self._name + "_msd_ak8_muCR4_N2_fail", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_fail_JESUp': ["h_" + self._name + "_msd_ak8_muCR4_N2_fail_JESUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_fail_JESDown': ["h_" + self._name + "_msd_ak8_muCR4_N2_fail_JESDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_fail_JERUp': ["h_" + self._name + "_msd_ak8_muCR4_N2_fail_JERUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_fail_JERDown': ["h_" + self._name + "_msd_ak8_muCR4_N2_fail_JERDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_fail_mutriggerUp': ["h_" + self._name + "_msd_ak8_muCR4_N2_fail_mutriggerUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_fail_mutriggerDown': ["h_" + self._name + "_msd_ak8_muCR4_N2_fail_mutriggerDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_fail_muidUp': ["h_" + self._name + "_msd_ak8_muCR4_N2_fail_muidUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_fail_muidDown': ["h_" + self._name + "_msd_ak8_muCR4_N2_fail_muidDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_fail_muisoUp': ["h_" + self._name + "_msd_ak8_muCR4_N2_fail_muisoUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_fail_muisoDown': ["h_" + self._name + "_msd_ak8_muCR4_N2_fail_muisoDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_fail_PuUp': ["h_" + self._name + "_msd_ak8_muCR4_N2_fail_PuUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
            'h_msd_ak8_muCR4_N2_fail_PuDown': ["h_" + self._name + "_msd_ak8_muCR4_N2_fail_PuDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
        }
        if not self._minBranches:
            histos1d_ext = {
                'h_Cuts': ["h_" + self._name + "_Cuts", "; Cut ", 8, 0, 8],
                'h_n_ak4': ["h_" + self._name + "_n_ak4", "; AK4 n_{jets}, p_{T} > 30 GeV;", 20, 0, 20],
                'h_ht': ["h_" + self._name + "_ht", "; HT (GeV);;", 50, 300, 2100],
                'h_pt_bbleading': ["h_" + self._name + "_pt_bbleading", "; AK8 leading p_{T} (GeV);", 50, 300, 2100],
                'h_bb_bbleading': ["h_" + self._name + "_bb_bbleading", "; double b-tag ;", 40, -1, 1],
                'h_msd_bbleading': ["h_" + self._name + "_msd_bbleading", "AK8 m_{SD}^{PUPPI} (GeV);", 30, 40, 250],
                'h_n_ak4fwd': ["h_" + self._name + "_n_ak4fwd", "; AK4 n_{jets}, p_{T} > 30 GeV, 2.5<|#eta|<4.5;", 20, 0, 20],
                'h_n_ak4L': ["h_" + self._name + "_n_ak4L", "; AK4 n_{L b-tags}, #DeltaR > 0.8, p_{T} > 40 GeV;", 20, 0, 20],
                'h_n_ak4M': ["h_" + self._name + "_n_ak4M", "; AK4 n_{M b-tags}, #DeltaR > 0.8, p_{T} > 40 GeV;", 20, 0, 20],
                'h_n_ak4T': ["h_" + self._name + "_n_ak4T", "; AK4 n_{T b-tags}, #DeltaR > 0.8, p_{T} > 40 GeV;", 20, 0, 20],
                'h_n_ak4_dR0p8': ["h_" + self._name + "_n_ak4_dR0p8", "; AK4 n_{jets}, #DeltaR > 0.8, p_{T} > 30 GeV;", 20, 0, 20],
                'h_isolationCA15': ["h_" + self._name + "_isolationCA15", "; AK8/CA15 p_{T} ratio ;", 50, 0.5, 1.5],
                'h_met': ["h_" + self._name + "_met", "; E_{T}^{miss} (GeV) ;", 50, 0, 500],
                'h_pt_ak8': ["h_" + self._name + "_pt_ak8", "; AK8 leading p_{T} (GeV);", 50, 300, 2100],
                'h_eta_ak8': ["h_" + self._name + "_eta_ak8", "; AK8 leading #eta;", 50, -3, 3],
                'h_pt_ak8_sub1': ["h_" + self._name + "_pt_ak8_sub1", "; AK8 subleading p_{T} (GeV);", 50, 300, 2100],
                'h_pt_ak8_sub2': ["h_" + self._name + "_pt_ak8_sub2", "; AK8 3rd leading p_{T} (GeV);", 50, 300, 2100],
                'h_pt_ak8_dbtagCut': ["h_" + self._name + "_pt_ak8_dbtagCut", "; AK8 leading p_{T} (GeV);", 45, 300, 2100],
                'h_msd_ak8': ["h_" + self._name + "_msd_ak8", "; p_{T}-leading m_{SD} (GeV);", 80, 40, 600],
                'h_msd_ak8_nocut': ["h_" + self._name + "_msd_ak8_nocut", "; p_{T}-leading m_{SD} (GeV);", 86, 0, 602],
                'h_rho_ak8': ["h_" + self._name + "_rho_ak8", "; p_{T}-leading  #rho=log(m_{SD}^{2}/p_{T}^{2}) ;", 50, -7, -1], 
                'h_rho_ak8_nocut': ["h_" + self._name + "_rho_ak8_nocut", "; p_{T}-leading  #rho=log(m_{SD}^{2}/p_{T}^{2}) ;", 50, -7, -1], 
                'h_msd_ak8_raw': ["h_" + self._name + "_msd_ak8_raw", "; AK8 m_{SD}^{PUPPI} no correction (GeV);", 80, 40, 600],
                'h_msd_ak8_raw_nocut': ["h_" + self._name + "_msd_ak8_raw_nocut", "; AK8 m_{SD}^{PUPPI} no correction (GeV);", 86, 0, 602],
                'h_msd_ak8_inc': ["h_" + self._name + "_msd_ak8_inc", "; AK8 m_{SD}^{PUPPI} (GeV);", 100, 0, 500],
                'h_msd_ak8_dbtagCut': ["h_" + self._name + "_msd_ak8_dbtagCut", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_t21ddtCut': ["h_" + self._name + "_msd_ak8_t21ddtCut", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_t21ddtCut_inc': ["h_" + self._name + "_msd_ak8_t21ddtCut_inc", "; AK8 m_{SD}^{PUPPI} (GeV);", 100, 0, 500],
                'h_msd_ak8_N2Cut': ["h_" + self._name + "_msd_ak8_N2Cut", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_dbtag_ak8': ["h_" + self._name + "_dbtag_ak8", "; p_{T}-leading double b-tag;", 40, -1, 1],
                'h_dbtag_ak8_sub1': ["h_" + self._name + "_dbtag_ak8_sub1", "; 2nd p_{T}-leading double b-tag;", 40, -1, 1],
                'h_dbtag_ak8_sub2': ["h_" + self._name + "_dbtag_ak8_sub2", "; 3rd p_{T}-leading double b-tag;", 40, -1, 1],
                'h_t21_ak8': ["h_" + self._name + "_t21_ak8", "; AK8 #tau_{21};", 25, 0, 1.5],
                'h_t21ddt_ak8': ["h_" + self._name + "_t21ddt_ak8", "; AK8 #tau_{21}^{DDT};", 25, 0, 1.5],
                'h_t32_ak8': ["h_" + self._name + "_t32_ak8", "; AK8 #tau_{32};", 25, 0, 1.5],
                'h_t32_ak8_t21ddtCut': ["h_" + self._name + "_t32_ak8_t21ddtCut", "; AK8 #tau_{32};", 20, 0, 1.5],
                'h_n2b1sd_ak8': ["h_" + self._name + "_n2b1sd_ak8", "; AK8 N_{2}^{1} (SD);", 25, -0.5, 0.5],
                'h_n2b1sdddt_ak8': ["h_" + self._name + "_n2b1sdddt_ak8", "; AK8 N_{2}^{1,DDT} (SD);", 25, -0.5, 0.5],
                'h_n2b1sdddt_ak8_aftercut': ["h_" + self._name + "_n2b1sdddt_ak8_aftercut", "; p_{T}-leading N_{2}^{1,DDT};", 25, -0.5, 0.5],
		'h_dbtag_ak8_aftercut': ["h_" + self._name + "_dbtag_ak8_aftercut", "; p_{T}-leading double-b tagger;", 33, -1, 1],
                'h_msd_ak8_raw_SR_fail': ["h_" + self._name + "_msd_ak8_raw_SR_fail", "; AK8 m_{SD}^{PUPPI} no corr (GeV);", 80, 40, 600],
                'h_msd_ak8_raw_SR_pass': ["h_" + self._name + "_msd_ak8_raw_SR_pass", "; AK8 m_{SD}^{PUPPI} no corr (GeV);", 80, 40, 600],
                'h_msd_ak8_topR6_pass': ["h_" + self._name + "_msd_ak8_topR6_pass", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR6_pass_JESUp': ["h_" + self._name + "_msd_ak8_topR6_pass_JESUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR6_pass_JESDown': ["h_" + self._name + "_msd_ak8_topR6_pass_JESDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR6_pass_JERUp': ["h_" + self._name + "_msd_ak8_topR6_pass_JERUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR6_pass_JERDown': ["h_" + self._name + "_msd_ak8_topR6_pass_JERDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR6_fail': ["h_" + self._name + "_msd_ak8_topR6_fail", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR6_fail_JESUp': ["h_" + self._name + "_msd_ak8_topR6_fail_JESUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR6_fail_JESDown': ["h_" + self._name + "_msd_ak8_topR6_fail_JESDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR6_fail_JERUp': ["h_" + self._name + "_msd_ak8_topR6_fail_JERUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR6_fail_JERDown': ["h_" + self._name + "_msd_ak8_topR6_fail_JERDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_n_ak4L100': ["h_" + self._name + "_n_ak4L100", "; AK4 n_{L b-tags}, #DeltaR > 0.8, p_{T} > 100 GeV;", 10, 0, 10],
                'h_n_ak4L150': ["h_" + self._name + "_n_ak4L150", "; AK4 n_{L b-tags}, #DeltaR > 0.8, p_{T} > 150 GeV;", 10, 0, 10],
                'h_n_ak4M100': ["h_" + self._name + "_n_ak4M100", "; AK4 n_{M b-tags}, #DeltaR > 0.8, p_{T} > 100 GeV;", 10, 0, 10],
                'h_n_ak4M150': ["h_" + self._name + "_n_ak4M150", "; AK4 n_{M b-tags}, #DeltaR > 0.8, p_{T} > 150 GeV;", 10, 0, 10],
                'h_n_ak4T100': ["h_" + self._name + "_n_ak4T100", "; AK4 n_{T b-tags}, #DeltaR > 0.8, p_{T} > 100 GeV;", 10, 0, 10],
                'h_n_ak4T150': ["h_" + self._name + "_n_ak4T150", "; AK4 n_{T b-tags}, #DeltaR > 0.8, p_{T} > 150 GeV;", 10, 0, 10],
                'h_msd_ak8_muCR1': ["h_" + self._name + "_msd_ak8_muCR1", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR2': ["h_" + self._name + "_msd_ak8_muCR2", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR3': ["h_" + self._name + "_msd_ak8_muCR3", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_pt_mu_muCR4': ["h_" + self._name + "_pt_mu_muCR4", "; leading muon p_{T} (GeV);", 50, 30, 500],
                'h_eta_mu_muCR4': ["h_" + self._name + "_eta_mu_muCR4", "; leading muon #eta;", 50, -2.5, 2.5],
                'h_pt_ak8_muCR4': ["h_" + self._name + "_pt_ak8_muCR4", "; AK8 leading p_{T} (GeV);", 50, 300, 2100],
                'h_eta_ak8_muCR4': ["h_" + self._name + "_eta_ak8_muCR4", "; AK8 leading #eta;", 50, -3, 3],
                'h_dbtag_ak8_muCR4': ["h_" + self._name + "_dbtag_ak8_muCR4", "; p_{T}-leading double b-tag;", 40, -1, 1],
                'h_t21ddt_ak8_muCR4': ["h_" + self._name + "_t21ddt_ak8_muCR4", "; AK8 #tau_{21}^{DDT};", 25, 0, 1.5],
                'h_msd_ak8_muCR4': ["h_" + self._name + "_msd_ak8_muCR4", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_pass': ["h_" + self._name + "_msd_ak8_muCR4_pass", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_pass_JESUp': ["h_" + self._name + "_msd_ak8_muCR4_pass_JESUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_pass_JESDown': ["h_" + self._name + "_msd_ak8_muCR4_pass_JESDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_pass_JERUp': ["h_" + self._name + "_msd_ak8_muCR4_pass_JERUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_pass_JERDown': ["h_" + self._name + "_msd_ak8_muCR4_pass_JERDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_pass_mutriggerUp': ["h_" + self._name + "_msd_ak8_muCR4_pass_mutriggerUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_pass_mutriggerDown': ["h_" + self._name + "_msd_ak8_muCR4_pass_mutriggerDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_pass_muidUp': ["h_" + self._name + "_msd_ak8_muCR4_pass_muidUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_pass_muidDown': ["h_" + self._name + "_msd_ak8_muCR4_pass_muidDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_pass_muisoUp': ["h_" + self._name + "_msd_ak8_muCR4_pass_muisoUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_pass_muisoDown': ["h_" + self._name + "_msd_ak8_muCR4_pass_muisoDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_pass_PuUp': ["h_" + self._name + "_msd_ak8_muCR4_pass_PuUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_pass_PuDown': ["h_" + self._name + "_msd_ak8_muCR4_pass_PuDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_fail': ["h_" + self._name + "_msd_ak8_muCR4_fail", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_fail_JESUp': ["h_" + self._name + "_msd_ak8_muCR4_fail_JESUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_fail_JESDown': ["h_" + self._name + "_msd_ak8_muCR4_fail_JESDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_fail_JERUp': ["h_" + self._name + "_msd_ak8_muCR4_fail_JERUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_fail_JERDown': ["h_" + self._name + "_msd_ak8_muCR4_fail_JERDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_fail_mutriggerUp': ["h_" + self._name + "_msd_ak8_muCR4_fail_mutriggerUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_fail_mutriggerDown': ["h_" + self._name + "_msd_ak8_muCR4_fail_mutriggerDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_fail_muidUp': ["h_" + self._name + "_msd_ak8_muCR4_fail_muidUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_fail_muidDown': ["h_" + self._name + "_msd_ak8_muCR4_fail_muidDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_fail_muisoUp': ["h_" + self._name + "_msd_ak8_muCR4_fail_muisoUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_fail_muisoDown': ["h_" + self._name + "_msd_ak8_muCR4_fail_muisoDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_fail_PuUp': ["h_" + self._name + "_msd_ak8_muCR4_fail_PuUp", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_fail_PuDown': ["h_" + self._name + "_msd_ak8_muCR4_fail_PuDown", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR5': ["h_" + self._name + "_msd_ak8_muCR5", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR6': ["h_" + self._name + "_msd_ak8_muCR6", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_bbleading_muCR4_pass': ["h_" + self._name + "_msd_ak8_bbleading_muCR4_pass", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_bbleading_muCR4_fail': ["h_" + self._name + "_msd_ak8_bbleading_muCR4_fail", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR1': ["h_" + self._name + "_msd_ak8_topR1", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR2_pass': ["h_" + self._name + "_msd_ak8_topR2_pass", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR3_pass': ["h_" + self._name + "_msd_ak8_topR3_pass", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR4_pass': ["h_" + self._name + "_msd_ak8_topR4_pass", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR5_pass': ["h_" + self._name + "_msd_ak8_topR5_pass", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR2_fail': ["h_" + self._name + "_msd_ak8_topR2_fail", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR3_fail': ["h_" + self._name + "_msd_ak8_topR3_fail", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR5_fail': ["h_" + self._name + "_msd_ak8_topR5_fail", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR7_pass': ["h_" + self._name + "_msd_ak8_topR7_pass", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR7_fail': ["h_" + self._name + "_msd_ak8_topR7_fail", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR4_fail': ["h_" + self._name + "_msd_ak8_topR4_fail", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_bbleading_topR6_pass': ["h_" + self._name + "_msd_ak8_bbleading_topR6_pass", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_bbleading_topR6_fail': ["h_" + self._name + "_msd_ak8_bbleading_topR6_fail", "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_pt_ca15': ["h_" + self._name + "_pt_ca15", "; CA15 p{T} (GeV);", 100, 300, 3000],
                'h_msd_ca15': ["h_" + self._name + "_msd_ca15", "; CA15 m_{SD}^{PUPPI} (GeV);", 35, 50, 400],
                'h_msd_ca15_t21ddtCut': ["h_" + self._name + "_msd_ca15_t21ddtCut", "; CA15 m_{SD}^{PUPPI} (GeV);", 35, 50, 400],
                'h_t21_ca15': ["h_" + self._name + "_t21_ca15", "; CA15 #tau_{21};", 25, 0, 1.5],
                'h_t21ddt_ca15': ["h_" + self._name + "_t21ddt_ca15", "; CA15 #tau_{21};", 25, 0, 1.5]
            }                
            dbcuts = [0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
            for dbcut in dbcuts:
                dbcutstring = str(dbcut).replace('0.','p')
                histos1d_ext.update({
                'h_msd_ak8_topR6_%s_pass'%dbcutstring: ["h_" + self._name + "_msd_ak8_topR6_%s_pass"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR6_%s_fail'%dbcutstring: ["h_" + self._name + "_msd_ak8_topR6_%s_fail"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR6_N2_%s_pass'%dbcutstring: ["h_" + self._name + "_msd_ak8_topR6_N2_%s_pass"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_topR6_N2_%s_fail'%dbcutstring: ["h_" + self._name + "_msd_ak8_topR6_N2_%s_fail"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_pass'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_pass"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_pass_JESUp'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_pass_JESUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_pass_JESDown'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_pass_JESDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_pass_JERUp'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_pass_JERUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_pass_JERDown'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_pass_JERDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_pass_mutriggerUp'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_pass_mutriggerUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_pass_mutriggerDown'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_pass_mutriggerDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_pass_muidUp'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_pass_muidUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_pass_muidDown'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_pass_muidDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_pass_muisoUp'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_pass_muisoUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_pass_muisoDown'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_pass_muisoDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_pass_PuUp'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_pass_PuUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_pass_PuDown'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_pass_PuDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_fail'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_fail"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_fail_JESUp'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_fail_JESUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_fail_JESDown'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_fail_JESDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_fail_JERUp'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_fail_JERUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_fail_JERDown'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_fail_JERDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_fail_mutriggerUp'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_fail_mutriggerUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_fail_mutriggerDown'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_fail_mutriggerDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_fail_muidUp'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_fail_muidUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_fail_muidDown'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_fail_muidDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_fail_muisoUp'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_fail_muisoUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_fail_muisoDown'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_fail_muisoDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_fail_PuUp'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_fail_PuUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                'h_msd_ak8_muCR4_N2_%s_fail_PuDown'%dbcutstring: ["h_" + self._name + "_msd_ak8_muCR4_N2_%s_fail_PuDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV);", 80, 40, 600],
                })
            histos1d = dict(histos1d.items() + histos1d_ext.items())

        msd_binBoundaries = []
        for i in range(0, 81):
            msd_binBoundaries.append(40. + i * 7)
        print(msd_binBoundaries)
        pt_binBoundaries = [450, 500, 550, 600, 675, 800, 1000]
        #pt_binBoundaries = [300, 350, 400, 450, 500, 550, 600, 675, 800, 1000]

        histos2d_fix = {
            'h_rhop_v_t21_ak8': ["h_" + self._name + "_rhop_v_t21_ak8", "; AK8 rho^{DDT}; AK8 <#tau_{21}>", 15, -5, 10,
                                 25, 0, 1.5],
            'h_rhop_v_t21_ca15': ["h_" + self._name + "_rhop_v_t21_ca15", "; CA15 rho^{DDT}; CA15 <#tau_{21}>", 15, -5,
                                  10, 25, 0, 1.5]
        }

        histos2d = {
            'h_msd_v_pt_ak8_topR6_N2_pass': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_pass", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_pass_JESUp': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_pass_JESUp", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_pass_JESDown': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_pass_JESDown", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_pass_JERUp': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_pass_JERUp", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_pass_JERDown': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_pass_JERDown", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_pass_triggerUp': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_pass_triggerUp", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_pass_triggerDown': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_pass_triggerDown", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_pass_PuUp': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_pass_PuUp", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_pass_PuDown': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_pass_PuDown", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_pass_matched': ["h_" + self._name + "_msd_v_pt_ak8_N2_topR6_pass_matched", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_pass_unmatched': ["h_" + self._name + "_msd_v_pt_ak8_N2_topR6_pass_unmatched", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_fail': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_fail", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_fail_JESUp': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_fail_JESUp", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_fail_JESDown': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_fail_JESDown", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_fail_JERUp': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_fail_JERUp", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_fail_JERDown': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_fail_JERDown", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_fail_triggerUp': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_fail_triggerUp", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_fail_triggerDown': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_fail_triggerDown", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_fail_PuUp': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_fail_PuUp", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_fail_PuDown': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_fail_PuDown", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_fail_matched': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_fail_matched", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_topR6_N2_fail_unmatched': ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_fail_unmatched", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_muCR4_N2_pass': ["h_" + self._name + "_msd_v_pt_ak8_muCR4_N2_pass", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
            'h_msd_v_pt_ak8_muCR4_N2_fail': ["h_" + self._name + "_msd_v_pt_ak8_muCR4_N2_fail", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"]
        }

        if not self._minBranches:
            histos2d_ext = {
                'h_msd_v_pt_ak8_topR1': ["h_" + self._name + "_msd_v_pt_ak8_topR1", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR2_pass': ["h_" + self._name + "_msd_v_pt_ak8_topR2_pass", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR3_pass': ["h_" + self._name + "_msd_v_pt_ak8_topR3_pass", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR4_pass': ["h_" + self._name + "_msd_v_pt_ak8_topR4_pass", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR5_pass': ["h_" + self._name + "_msd_v_pt_ak8_topR5_pass", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_pass': ["h_" + self._name + "_msd_v_pt_ak8_topR6_pass", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_pass_JESUp': ["h_" + self._name + "_msd_v_pt_ak8_topR6_pass_JESUp", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_pass_JESDown': ["h_" + self._name + "_msd_v_pt_ak8_topR6_pass_JESDown", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_pass_JERUp': ["h_" + self._name + "_msd_v_pt_ak8_topR6_pass_JERUp", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_pass_JERDown': ["h_" + self._name + "_msd_v_pt_ak8_topR6_pass_JERDown", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_pass_matched': ["h_" + self._name + "_msd_v_pt_ak8_topR6_pass_matched", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_pass_unmatched': ["h_" + self._name + "_msd_v_pt_ak8_topR6_pass_unmatched", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_fail_matched': ["h_" + self._name + "_msd_v_pt_ak8_topR6_fail_matched", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_fail_unmatched': ["h_" + self._name + "_msd_v_pt_ak8_topR6_fail_unmatched", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR7_pass': ["h_" + self._name + "_msd_v_pt_ak8_topR7_pass", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR2_fail': ["h_" + self._name + "_msd_v_pt_ak8_topR2_fail", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR3_fail': ["h_" + self._name + "_msd_v_pt_ak8_topR3_fail", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR4_fail': ["h_" + self._name + "_msd_v_pt_ak8_topR4_fail", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR5_fail': ["h_" + self._name + "_msd_v_pt_ak8_topR5_fail", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_fail': ["h_" + self._name + "_msd_v_pt_ak8_topR6_fail", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_fail_JESUp': ["h_" + self._name + "_msd_v_pt_ak8_topR6_fail_JESUp", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_fail_JESDown': ["h_" + self._name + "_msd_v_pt_ak8_topR6_fail_JESDown", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_fail_JERUp': ["h_" + self._name + "_msd_v_pt_ak8_topR6_fail_JERUp", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_fail_JERDown': ["h_" + self._name + "_msd_v_pt_ak8_topR6_fail_JERDown", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_raw_fail': ["h_" + self._name + "_msd_v_pt_ak8_topR6_raw_fail", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_raw_pass': ["h_" + self._name + "_msd_v_pt_ak8_topR6_raw_pass", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR7_fail': ["h_" + self._name + "_msd_v_pt_ak8_topR7_fail", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_bbleading_topR6_pass': ["h_" + self._name + "_msd_v_pt_ak8_bbleading_topR6_pass", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_bbleading_topR6_fail': ["h_" + self._name + "_msd_v_pt_ak8_bbleading_topR6_fail", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_muCR4_pass': ["h_" + self._name + "_msd_v_pt_ak8_muCR4_pass", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_muCR4_fail': ["h_" + self._name + "_msd_v_pt_ak8_muCR4_fail", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_bbleading_muCR4_pass': ["h_" + self._name + "_msd_v_pt_ak8_bbleading_muCR4_pass", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_bbleading_muCR4_fail': ["h_" + self._name + "_msd_v_pt_ak8_bbleading_muCR4_fail", "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"]
            }
            dbcuts = [0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
            for dbcut in dbcuts:
                dbcutstring = str(dbcut).replace('0.','p')
                histos2d_ext.update({
                'h_msd_v_pt_ak8_topR6_%s_fail'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_fail"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_fail_matched'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_fail_matched"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_fail_unmatched'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_fail_unmatched"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_fail_JERUp'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_fail_JERUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_fail_JERDown'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_fail_JERDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_fail_JESUp'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_fail_JESUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_fail_JESDown'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_fail_JESDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_fail_triggerUp'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_fail_triggerUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_fail_triggerDown'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_fail_triggerDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_fail_PuUp'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_fail_PuUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_fail_PuDown'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_fail_PuDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_pass'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_pass"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_pass_matched'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_pass_matched"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_pass_unmatched'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_pass_unmatched"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_pass_JERUp'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_pass_JERUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_pass_JERDown'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_pass_JERDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_pass_JESUp'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_pass_JESUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_pass_JESDown'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_pass_JESDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_pass_triggerUp'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_pass_triggerUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_pass_triggerDown'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_pass_triggerDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_pass_PuUp'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_pass_PuUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_%s_pass_PuDown'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_%s_pass_PuDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_fail'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_fail"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_fail_matched'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_fail_matched"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_fail_unmatched'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_fail_unmatched"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_fail_JERUp'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_fail_JERUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_fail_JERDown'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_fail_JERDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_fail_JESUp'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_fail_JESUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_fail_JESDown'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_fail_JESDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_fail_triggerUp'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_fail_triggerUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_fail_triggerDown'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_fail_triggerDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_fail_PuUp'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_fail_PuUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_fail_PuDown'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_fail_PuDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_pass'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_pass"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_pass_matched'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_pass_matched"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_pass_unmatched'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_pass_unmatched"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_pass_JERUp'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_pass_JERUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_pass_JERDown'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_pass_JERDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_pass_JESUp'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_pass_JESUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_pass_JESDown'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_pass_JESDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_pass_triggerUp'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_pass_triggerUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_pass_triggerDown'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_pass_triggerDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_pass_PuUp'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_pass_PuUp"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"],
                'h_msd_v_pt_ak8_topR6_N2_%s_pass_PuDown'%dbcutstring: ["h_" + self._name + "_msd_v_pt_ak8_topR6_N2_%s_pass_PuDown"%dbcutstring, "; AK8 m_{SD}^{PUPPI} (GeV); AK8 p_{T} (GeV)"]
            })

            histos2d = dict(histos2d.items() + histos2d_ext.items())

        for key, val in histos1d.iteritems():
            setattr(self, key, ROOT.TH1F(val[0], val[1], val[2], val[3], val[4]))
            (getattr(self, key)).Sumw2()
        for key, val in histos2d_fix.iteritems():
            setattr(self, key, ROOT.TH2F(val[0], val[1], val[2], val[3], val[4], val[5], val[6], val[7]))
            (getattr(self, key)).Sumw2()
        for key, val in histos2d.iteritems():
            tmp = ROOT.TH2F(val[0], val[1], len(msd_binBoundaries) - 1, array.array('d', msd_binBoundaries),
                            len(pt_binBoundaries) - 1, array.array('d', pt_binBoundaries))
            setattr(self, key, tmp)
            (getattr(self, key)).Sumw2()

        # loop
        if len(fn) > 0:
            self.loop()

    def loop(self):
        # looping
        nent = self._tt.GetEntries()
        print "\n", "***********************************************************************************************************************************"
        print self._name
        print "***********************************************************************************************************************************", "\n"
        print nent , "\n"        
        cut = []
        cut = [0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0.]

        self._tt.SetNotify(self._cutFormula)
        for i in xrange(nent):
            if i % self._sf != 0: continue

            # self._tt.LoadEntry(i)
            self._tt.LoadTree(i)
            selected = False
            for j in range(self._cutFormula.GetNdata()):
                if (self._cutFormula.EvalInstance(j)):
                    selected = True
                    break
            if not selected: continue

            self._tt.GetEntry(i)

            if (nent / 100 > 0 and i % (1 * nent / 100) == 0):
                sys.stdout.write("\r[" + "=" * int(20 * i / nent) + " " + str(round(100. * i / nent, 0)) + "% done")
                sys.stdout.flush()

            puweight = self.puWeight[0] #corrected
            nPuForWeight = min(self.npu[0], 49.5)
	    #$print(puweight,self._puw.GetBinContent(self._puw.FindBin(nPuForWeight)))
            #puweight = self._puw.GetBinContent(self._puw.FindBin(nPuForWeight))
            puweight_up = self._puw_up.GetBinContent(self._puw_up.FindBin(nPuForWeight))
            puweight_down = self._puw_down.GetBinContent(self._puw_down.FindBin(nPuForWeight))
            # print(self.puWeight[0],puweight,puweight_up,puweight_down)
            fbweight = self.scale1fb[0] * self._lumi
            # if self._name=='tqq' or 'TTbar' in self._name:
            #    fbweight = fbweight/self.topPtWeight[0] # remove top pt reweighting (assuming average weight is ~ 1)
            vjetsKF = 1.
	    wscale=[1.0,1.0,1.0,1.20,1.25,1.25,1.0]
	    ptscale=[0, 500, 600, 700, 800, 900, 1000,3000]
	    ptKF=1.
            if self._name == 'wqq' or self._name == 'W':
                # print self._name
		for i in range(0, len(ptscale)):
			if self.genVPt[0] > ptscale[i] and self.genVPt[0]<ptscale[i+1]:  ptKF=wscale[i]
                vjetsKF = self.kfactor[0] * 1.35 * ptKF  # ==1 for not V+jets events
            elif self._name == 'zqq' or self._name == 'DY':
                # print self._name
                vjetsKF = self.kfactor[0] * 1.45  # ==1 for not V+jets events
            # trigger weight
            massForTrig = min(self.AK8Puppijet0_msd[0], 300.)
            ptForTrig = max(200., min(self.AK8Puppijet0_pt[0], 1000.))
            trigweight = self._trig_eff.GetEfficiency(self._trig_eff.FindFixBin(massForTrig, ptForTrig))
            trigweightUp = trigweight + self._trig_eff.GetEfficiencyErrorUp(
                self._trig_eff.FindFixBin(massForTrig, ptForTrig))
            trigweightDown = trigweight - self._trig_eff.GetEfficiencyErrorLow(
                self._trig_eff.FindFixBin(massForTrig, ptForTrig))
            if trigweight <= 0 or trigweightDown <= 0 or trigweightUp <= 0:
                print 'trigweights are %f, %f, %f, setting all to 1' % (trigweight, trigweightUp, trigweightDown)
                trigweight = 1
                trigweightDown = 1
                trigweightUp = 1

            weight = puweight * fbweight * self._sf * vjetsKF * trigweight
            weight_triggerUp = puweight * fbweight * self._sf * vjetsKF * trigweightUp
            weight_triggerDown = puweight * fbweight * self._sf * vjetsKF * trigweightDown
            weight_pu_up = puweight_up * fbweight * self._sf * vjetsKF * trigweight
            weight_pu_down = puweight_down * fbweight * self._sf * vjetsKF * trigweight

            mutrigweight = 1
            mutrigweightDown = 1
            mutrigweightUp = 1
            if self.nmuLoose[0] > 0:
                muPtForTrig = max(52., min(self.vmuoLoose0_pt[0], 700.))
                muEtaForTrig = min(abs(self.vmuoLoose0_eta[0]), 2.3)
                mutrigweight = self._mutrig_eff.GetBinContent(self._mutrig_eff.FindBin(muPtForTrig, muEtaForTrig))
                mutrigweightUp = mutrigweight + self._mutrig_eff.GetBinError(
                    self._mutrig_eff.FindBin(muPtForTrig, muEtaForTrig))
                mutrigweightDown = mutrigweight - self._mutrig_eff.GetBinError(
                    self._mutrig_eff.FindBin(muPtForTrig, muEtaForTrig))
                if mutrigweight <= 0 or mutrigweightDown <= 0 or mutrigweightUp <= 0:
                    print 'mutrigweights are %f, %f, %f, setting all to 1' % (
                    mutrigweight, mutrigweightUp, mutrigweightDown)
                    mutrigweight = 1
                    mutrigweightDown = 1
                    mutrigweightUp = 1

            muidweight = 1
            muidweightDown = 1
            muidweightUp = 1
            if self.nmuLoose[0] > 0:
                muPtForId = max(20., min(self.vmuoLoose0_pt[0], 100.))
                muEtaForId = min(abs(self.vmuoLoose0_eta[0]), 2.3)
                muidweight = self._muid_eff.GetBinContent(self._muid_eff.FindBin(muPtForId, muEtaForId))
                muidweightUp = muidweight + self._muid_eff.GetBinError(self._muid_eff.FindBin(muPtForId, muEtaForId))
                muidweightDown = muidweight - self._muid_eff.GetBinError(self._muid_eff.FindBin(muPtForId, muEtaForId))
                if muidweight <= 0 or muidweightDown <= 0 or muidweightUp <= 0:
                    print 'muidweights are %f, %f, %f, setting all to 1' % (muidweight, muidweightUp, muidweightDown)
                    muidweight = 1
                    muidweightDown = 1
                    muidweightUp = 1

            muisoweight = 1
            muisoweightDown = 1
            muisoweightUp = 1
            if self.nmuLoose[0] > 0:
                muPtForIso = max(20., min(self.vmuoLoose0_pt[0], 100.))
                muEtaForIso = min(abs(self.vmuoLoose0_eta[0]), 2.3)
                muisoweight = self._muiso_eff.GetBinContent(self._muiso_eff.FindBin(muPtForIso, muEtaForIso))
                muisoweightUp = muisoweight + self._muiso_eff.GetBinError(
                    self._muiso_eff.FindBin(muPtForIso, muEtaForIso))
                muisoweightDown = muisoweight - self._muiso_eff.GetBinError(
                    self._muiso_eff.FindBin(muPtForIso, muEtaForIso))
                if muisoweight <= 0 or muisoweightDown <= 0 or muisoweightUp <= 0:
                    print 'muisoweights are %f, %f, %f, setting all to 1' % (
                    muisoweight, muisoweightUp, muisoweightDown)
                    muisoweight = 1
                    muisoweightDown = 1
                    muisoweightUp = 1

            weight_mu = puweight * fbweight * self._sf * vjetsKF * mutrigweight * muidweight * muisoweight
            weight_mutriggerUp = puweight * fbweight * self._sf * vjetsKF * mutrigweightUp * muidweight * muisoweight
            weight_mutriggerDown = puweight * fbweight * self._sf * vjetsKF * mutrigweightDown * muidweight * muisoweight
            weight_muidUp = puweight * fbweight * self._sf * vjetsKF * mutrigweight * muidweightUp * muisoweight
            weight_muidDown = puweight * fbweight * self._sf * vjetsKF * mutrigweight * muidweightDown * muisoweight
            weight_muisoUp = puweight * fbweight * self._sf * vjetsKF * mutrigweight * muidweight * muisoweightUp
            weight_muisoDown = puweight * fbweight * self._sf * vjetsKF * mutrigweight * muidweight * muisoweightDown
            weight_mu_pu_up = puweight_up * fbweight * self._sf * vjetsKF * mutrigweight * muidweight * muisoweight
            weight_mu_pu_down = puweight_down * fbweight * self._sf * vjetsKF * mutrigweight * muidweight * muisoweight

            if self._isData:
                weight = 1
                weight_triggerUp = 1
                weight_triggerDown = 1
                weight_pu_up = 1
                weight_pu_down = 1
                weight_mu = 1
                weight_mutriggerUp = 1
                weight_mutriggerDown = 1
                weight_muidUp = 1
                weight_muidDown = 1
                weight_muisoUp = 1
                weight_muisoDown = 1
                weight_mu_pu_up = 1
                weight_mu_pu_down = 1

            ##### AK8 info
            #print "Anter Weight : ", weight
            jmsd_8_raw = self.AK8Puppijet0_msd[0]
            jpt_8 = self.AK8Puppijet0_pt[0]
            jpt_8_JERUp = self.AK8Puppijet0_pt_JERUp[0]
            jpt_8_JERDown = self.AK8Puppijet0_pt_JERDown[0]
            jpt_8_JESUp = self.AK8Puppijet0_pt_JESUp[0]
            jpt_8_JESDown = self.AK8Puppijet0_pt_JESDown[0]
            jeta_8 = self.AK8Puppijet0_eta[0]
            jmsd_8 = self.AK8Puppijet0_msd[0] * self.PUPPIweight(jpt_8, jeta_8)
            jphi_8 = self.AK8Puppijet0_phi[0]
            if not self._minBranches:
                jpt_8_sub1 = self.AK8Puppijet1_pt[0]
                jpt_8_sub2 = self.AK8Puppijet2_pt[0]
            if jmsd_8 <= 0: jmsd_8 = 0.01
            rh_8 = math.log(jmsd_8 * jmsd_8 / jpt_8 / jpt_8)  # tocheck here
            rhP_8 = math.log(jmsd_8 * jmsd_8 / jpt_8)
            jt21_8 = self.AK8Puppijet0_tau21[0]
            jt32_8 = self.AK8Puppijet0_tau32[0]
            jt21P_8 = jt21_8 + 0.063 * rhP_8
            jtN2b1sd_8 = self.AK8Puppijet0_N2sdb1[0]

            # N2DDT transformation
            cur_rho_index = self._trans_h2ddt.GetXaxis().FindBin(rh_8)
            cur_pt_index = self._trans_h2ddt.GetYaxis().FindBin(jpt_8)
            if rh_8 > self._trans_h2ddt.GetXaxis().GetBinUpEdge(
                self._trans_h2ddt.GetXaxis().GetNbins()): cur_rho_index = self._trans_h2ddt.GetXaxis().GetNbins()
            if rh_8 < self._trans_h2ddt.GetXaxis().GetBinLowEdge(1): cur_rho_index = 1
            if jpt_8 > self._trans_h2ddt.GetYaxis().GetBinUpEdge(
                self._trans_h2ddt.GetYaxis().GetNbins()): cur_pt_index = self._trans_h2ddt.GetYaxis().GetNbins()
            if jpt_8 < self._trans_h2ddt.GetYaxis().GetBinLowEdge(1): cur_pt_index = 1
            jtN2b1sdddt_8 = jtN2b1sd_8 - self._trans_h2ddt.GetBinContent(cur_rho_index, cur_pt_index)

            jdb_8 = self.AK8Puppijet0_doublecsv[0]
            if not self._minBranches:
                if self.AK8Puppijet1_doublecsv[0] > 1:
                    jdb_8_sub1 = -99
                else:
                    jdb_8_sub1 = self.AK8Puppijet1_doublecsv[0]
                if self.AK8Puppijet2_doublecsv[0] > 1:
                    jdb_8_sub2 = -99
                else:
                    jdb_8_sub2 = self.AK8Puppijet2_doublecsv[0]

            n_4 = self.nAK4PuppijetsPt30[0]
            if not self._minBranches:
                n_fwd_4 = self.nAK4PuppijetsfwdPt30[0]
            n_dR0p8_4 = self.nAK4PuppijetsPt30dR08_0[0]
            # due to bug, don't use jet counting JER/JES Up/Down for now
            # n_dR0p8_4_JERUp = self.nAK4PuppijetsPt30dR08jerUp_0[0]
            # n_dR0p8_4_JERDown = self.nAK4PuppijetsPt30dR08jerDown_0[0]
            # n_dR0p8_4_JESUp = self.nAK4PuppijetsPt30dR08jesUp_0[0]
            # n_dR0p8_4_JESDown = self.nAK4PuppijetsPt30dR08jesDown_0[0]
            n_dR0p8_4_JERUp = n_dR0p8_4
            n_dR0p8_4_JERDown = n_dR0p8_4
            n_dR0p8_4_JESUp = n_dR0p8_4
            n_dR0p8_4_JESDown = n_dR0p8_4
            
            n_MdR0p8_4 = self.nAK4PuppijetsMPt50dR08_0[0]
            if not self._minBranches:
                n_LdR0p8_4 = self.nAK4PuppijetsLPt50dR08_0[0]
                n_TdR0p8_4 = self.nAK4PuppijetsTPt50dR08_0[0]
                n_LPt100dR0p8_4 = self.nAK4PuppijetsLPt100dR08_0[0]
                n_MPt100dR0p8_4 = self.nAK4PuppijetsMPt100dR08_0[0]
                n_TPt100dR0p8_4 = self.nAK4PuppijetsTPt100dR08_0[0]
                n_LPt150dR0p8_4 = self.nAK4PuppijetsLPt150dR08_0[0]
                n_MPt150dR0p8_4 = self.nAK4PuppijetsMPt150dR08_0[0]
                n_TPt150dR0p8_4 = self.nAK4PuppijetsTPt150dR08_0[0]

            met = self.pfmet[0]#puppet[0]
            metphi = self.pfmetphi[0]#puppetphi[0]
            met_x = met * ROOT.TMath.Cos(metphi)
            met_y = met * ROOT.TMath.Sin(metphi)
            met_JESUp = ROOT.TMath.Sqrt(
                (met_x + self.MetXCorrjesUp[0]) * (met_x + self.MetXCorrjesUp[0]) + (met_y + self.MetYCorrjesUp[0]) * (
                met_y + self.MetYCorrjesUp[0]))
            met_JESDown = ROOT.TMath.Sqrt((met_x + self.MetXCorrjesDown[0]) * (met_x + self.MetXCorrjesDown[0]) + (
            met_y + self.MetYCorrjesDown[0]) * (met_y + self.MetYCorrjesDown[0]))
            met_JERUp = ROOT.TMath.Sqrt(
                (met_x + self.MetXCorrjerUp[0]) * (met_x + self.MetXCorrjerUp[0]) + (met_y + self.MetYCorrjerUp[0]) * (
                met_y + self.MetYCorrjerUp[0]))
            met_JERDown = ROOT.TMath.Sqrt((met_x + self.MetXCorrjerDown[0]) * (met_x + self.MetXCorrjerDown[0]) + (
            met_y + self.MetYCorrjerDown[0]) * (met_y + self.MetYCorrjerDown[0]))

            ratioCA15_04 = self.AK8Puppijet0_ratioCA15_04[0]

            ntau = self.ntau[0]
            nmuLoose = self.nmuLoose[0]
            neleLoose = self.neleLoose[0]
            nphoLoose = self.nphoLoose[0]
            isTightVJet = self.AK8Puppijet0_isTightVJet[0]

            # muon info
            vmuoLoose0_pt = self.vmuoLoose0_pt[0]
            vmuoLoose0_eta = self.vmuoLoose0_eta[0]
            vmuoLoose0_phi = self.vmuoLoose0_phi[0]

            self.h_npv.Fill(self.npv[0], weight)

            # gen-matching for scale/smear systematic
            dphi = 9999.
            dpt = 9999.
            dmass = 9999.
            if (not self._isData):
                genVPt = self.genVPt[0]
                genVEta = self.genVEta[0]
                genVPhi = self.genVPhi[0]
                genVMass = self.genVMass[0]
                if genVPt > 0 and genVMass > 0:
                    dphi = math.fabs(delta_phi(genVPhi, jphi_8))
                    dpt = math.fabs(genVPt - jpt_8) / genVPt
                    dmass = math.fabs(genVMass - jmsd_8) / genVMass

            # Single Muon Control Regions
            if jpt_8 > PTCUTMUCR and jmsd_8 > MASSCUT and nmuLoose == 1 and neleLoose == 0 and ntau == 0 and vmuoLoose0_pt > MUONPTCUT and abs(
                    vmuoLoose0_eta) < 2.1 and isTightVJet and abs(
                            math.acos(math.cos(vmuoLoose0_phi - jphi_8))) > 2. * ROOT.TMath.Pi() / 3. and n_MdR0p8_4 >= 1:
                if not self._minBranches:
                    ht_ = 0.
                    if (abs(self.AK4Puppijet0_eta[0]) < 2.4 and self.AK4Puppijet0_pt[0] > 30): ht_ = ht_ + \
                                                                                                     self.AK4Puppijet0_pt[
                                                                                                         0]
                    if (abs(self.AK4Puppijet1_eta[0]) < 2.4 and self.AK4Puppijet1_pt[0] > 30): ht_ = ht_ + \
                                                                                                     self.AK4Puppijet1_pt[
                                                                                                         0]
                    if (abs(self.AK4Puppijet2_eta[0]) < 2.4 and self.AK4Puppijet2_pt[0] > 30): ht_ = ht_ + \
                                                                                                     self.AK4Puppijet2_pt[
                                                                                                         0]
                    if (abs(self.AK4Puppijet3_eta[0]) < 2.4 and self.AK4Puppijet3_pt[0] > 30): ht_ = ht_ + \
                                                                                                     self.AK4Puppijet3_pt[
                                                                                                         0]
                    self.h_ht.Fill(ht_, weight)

                    self.h_msd_ak8_muCR1.Fill(jmsd_8, weight_mu)
                    if jdb_8 > DBTAGCUT:
                        self.h_msd_ak8_muCR2.Fill(jmsd_8, weight_mu)
                    if jt21P_8 < 0.4:
                        self.h_msd_ak8_muCR3.Fill(jmsd_8, weight_mu)

                    self.h_t21ddt_ak8_muCR4.Fill(jt21P_8, weight_mu)
                    if jt21P_8 < T21DDTCUT:
                        self.h_dbtag_ak8_muCR4.Fill(jdb_8, weight_mu)
                        self.h_msd_ak8_muCR4.Fill(jmsd_8, weight_mu)
                        self.h_pt_ak8_muCR4.Fill(jpt_8, weight_mu)
                        self.h_eta_ak8_muCR4.Fill(jeta_8, weight_mu)
                        self.h_pt_mu_muCR4.Fill(vmuoLoose0_pt, weight_mu)
                        self.h_eta_mu_muCR4.Fill(vmuoLoose0_eta, weight_mu)
                        if jdb_8 > DBTAGCUT:
                            self.h_msd_ak8_muCR4_pass.Fill(jmsd_8, weight_mu)
                            self.h_msd_v_pt_ak8_muCR4_pass.Fill(jmsd_8, jpt_8, weight_mu)
                        elif jdb_8 > self.DBTAGCUTMIN:
                            self.h_msd_ak8_muCR4_fail.Fill(jmsd_8, weight_mu)
                            self.h_msd_v_pt_ak8_muCR4_fail.Fill(jmsd_8, jpt_8, weight_mu)

                    if jdb_8 > 0.7 and jt21P_8 < 0.4:
                        self.h_msd_ak8_muCR5.Fill(jmsd_8, weight_mu)
                    if jdb_8 > 0.7 and jt21P_8 < T21DDTCUT:
                        self.h_msd_ak8_muCR6.Fill(jmsd_8, weight_mu)

                if jtN2b1sdddt_8 < 0:
                    self.h_dbtag_ak8_muCR4_N2.Fill(jdb_8, weight_mu)
                    self.h_msd_ak8_muCR4_N2.Fill(jmsd_8, weight_mu)
                    self.h_pt_ak8_muCR4_N2.Fill(jpt_8, weight_mu)
                    self.h_eta_ak8_muCR4_N2.Fill(jeta_8, weight_mu)
                    self.h_pt_mu_muCR4_N2.Fill(vmuoLoose0_pt, weight_mu)
                    self.h_eta_mu_muCR4_N2.Fill(vmuoLoose0_eta, weight_mu)
                    if jdb_8 > DBTAGCUT:
                        self.h_msd_ak8_muCR4_N2_pass.Fill(jmsd_8, weight_mu)
                        self.h_msd_v_pt_ak8_muCR4_N2_pass.Fill(jmsd_8, jpt_8, weight_mu)
                        self.h_msd_ak8_muCR4_N2_pass_mutriggerUp.Fill(jmsd_8, weight_mutriggerUp)
                        self.h_msd_ak8_muCR4_N2_pass_mutriggerDown.Fill(jmsd_8, weight_mutriggerDown)
                        self.h_msd_ak8_muCR4_N2_pass_muidUp.Fill(jmsd_8, weight_muidUp)
                        self.h_msd_ak8_muCR4_N2_pass_muidDown.Fill(jmsd_8, weight_muidDown)
                        self.h_msd_ak8_muCR4_N2_pass_muisoUp.Fill(jmsd_8, weight_muisoUp)
                        self.h_msd_ak8_muCR4_N2_pass_muisoDown.Fill(jmsd_8, weight_muisoDown)
                        self.h_msd_ak8_muCR4_N2_pass_PuUp.Fill(jmsd_8, weight_mu_pu_up)
                        self.h_msd_ak8_muCR4_N2_pass_PuDown.Fill(jmsd_8, weight_mu_pu_down)
                    elif jdb_8 > self.DBTAGCUTMIN:
                        self.h_msd_ak8_muCR4_N2_fail.Fill(jmsd_8, weight_mu)
                        self.h_msd_v_pt_ak8_muCR4_N2_fail.Fill(jmsd_8, jpt_8, weight_mu)
                        self.h_msd_ak8_muCR4_N2_fail_mutriggerUp.Fill(jmsd_8, weight_mutriggerUp)
                        self.h_msd_ak8_muCR4_N2_fail_mutriggerDown.Fill(jmsd_8, weight_mutriggerDown)
                        self.h_msd_ak8_muCR4_N2_fail_muidUp.Fill(jmsd_8, weight_muidUp)
                        self.h_msd_ak8_muCR4_N2_fail_muidDown.Fill(jmsd_8, weight_muidDown)
                        self.h_msd_ak8_muCR4_N2_fail_muisoUp.Fill(jmsd_8, weight_muisoUp)
                        self.h_msd_ak8_muCR4_N2_fail_muisoDown.Fill(jmsd_8, weight_muisoDown)
                        self.h_msd_ak8_muCR4_N2_fail_PuUp.Fill(jmsd_8, weight_mu_pu_up)
                        self.h_msd_ak8_muCR4_N2_fail_PuDown.Fill(jmsd_8, weight_mu_pu_down)
                        
                    if not self._minBranches:
                        dbcuts = [0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
                        for dbcut in dbcuts:
                            if jdb_8 > dbcut:                                
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_pass' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_mu)
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_pass_mutriggerUp' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_mutriggerUp)
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_pass_mutriggerDown' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_mutriggerDown)
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_pass_muidUp' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_muidUp)
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_pass_muidDown' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_muidDown)
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_pass_muisoUp' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_muisoUp)
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_pass_muisoDown' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_muisoDown)
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_pass_PuUp' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_mu_pu_up)
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_pass_PuDown' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_mu_pu_down)
                            elif jdb_8 > self.DBTAGCUTMIN:                                
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_fail' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_mu)
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_fail_mutriggerUp' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_mutriggerUp)
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_fail_mutriggerDown' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_mutriggerDown)
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_fail_muidUp' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_muidUp)
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_fail_muidDown' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_muidDown)
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_fail_muisoUp' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_muisoUp)
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_fail_muisoDown' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_muisoDown)
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_fail_PuUp' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_mu_pu_up)
                                getattr(self, 'h_msd_ak8_muCR4_N2_%s_fail_PuDown' % str(dbcut).replace('0.','p')).Fill(jmsd_8, weight_mu_pu_down)


            for syst in ['JESUp', 'JESDown', 'JERUp', 'JERDown']:
                if eval('jpt_8_%s' % syst) > PTCUTMUCR and jmsd_8 > MASSCUT and nmuLoose == 1 and neleLoose == 0 and ntau == 0 and vmuoLoose0_pt > MUONPTCUT and abs(vmuoLoose0_eta) < 2.1 and isTightVJet and jtN2b1sdddt_8 < 0 and abs(math.acos(math.cos(vmuoLoose0_phi - jphi_8))) > 2. * ROOT.TMath.Pi() / 3. and n_MdR0p8_4 >= 1:
                    if jdb_8 > DBTAGCUT:
                        (getattr(self, 'h_msd_ak8_muCR4_N2_pass_%s' % syst)).Fill(jmsd_8, weight)
                    elif jdb_8 > self.DBTAGCUTMIN:
                        (getattr(self, 'h_msd_ak8_muCR4_N2_fail_%s' % syst)).Fill(jmsd_8, weight)

            if not self._minBranches:
                jmsd_8_sub1 = self.AK8Puppijet1_msd[0]
                jmsd_8_sub2 = self.AK8Puppijet2_msd[0]
                n_MPt100dR0p8_4_sub1 = self.nAK4PuppijetsMPt100dR08_1[0]
                n_MPt100dR0p8_4_sub2 = self.nAK4PuppijetsMPt100dR08_2[0]

                jt21_8_sub1 = self.AK8Puppijet1_tau21[0]
                rhP_8_sub1 = -999
                jt21P_8_sub1 = -999
                if jpt_8_sub1 > 0 and jmsd_8_sub1 > 0:
                    rhP_8_sub1 = math.log(jmsd_8_sub1 * jmsd_8_sub1 / jpt_8_sub1)
                    jt21P_8_sub1 = jt21_8_sub1 + 0.063 * rhP_8_sub1

                jt21_8_sub2 = self.AK8Puppijet2_tau21[0]
                rhP_8_sub2 = -999
                jt21P_8_sub2 = -999
                if jpt_8_sub2 > 0 and jmsd_8_sub2 > 0:
                    rhP_8_sub2 = math.log(jmsd_8_sub2 * jmsd_8_sub2 / jpt_8_sub2)
                    jt21P_8_sub2 = jt21_8_sub2 + 0.063 * rhP_8_sub2

                isTightVJet_sub1 = self.AK8Puppijet1_isTightVJet
                isTightVJet_sub2 = self.AK8Puppijet2_isTightVJet

                bb_idx = [[jmsd_8, jpt_8, jdb_8, n_MPt100dR0p8_4, jt21P_8, isTightVJet],
                          [jmsd_8_sub1, jpt_8_sub1, jdb_8_sub1, n_MPt100dR0p8_4_sub1, jt21P_8_sub1, isTightVJet_sub1],
                          [jmsd_8_sub2, jpt_8_sub2, jdb_8_sub2, n_MPt100dR0p8_4_sub2, jt21P_8_sub2, isTightVJet_sub2]
                          ]

                a = 0
                for i in sorted(bb_idx, key=lambda bbtag: bbtag[2], reverse=True):
                    if a > 0: continue
                    a = a + 1
                    if i[1] > PTCUTMUCR and i[
                        0] > MASSCUT and nmuLoose == 1 and neleLoose == 0 and ntau == 0 and vmuoLoose0_pt > MUONPTCUT and abs(
                            vmuoLoose0_eta) < 2.1 and i[4] < T21DDTCUT and i[5]:
                        if i[2] > DBTAGCUT:
                            self.h_msd_ak8_bbleading_muCR4_pass.Fill(i[0], weight_mu)
                            self.h_msd_v_pt_ak8_bbleading_muCR4_pass.Fill(i[0], i[1], weight_mu)
                        else:
                            self.h_msd_ak8_bbleading_muCR4_fail.Fill(i[0], weight_mu)
                            self.h_msd_v_pt_ak8_bbleading_muCR4_fail.Fill(i[0], i[1], weight_mu)
                if jpt_8 > PTCUT:
                    cut[3] = cut[3] + 1
                if jpt_8 > PTCUT and jmsd_8 > MASSCUT:
                    cut[4] = cut[4] + 1
                if jpt_8 > PTCUT and jmsd_8 > MASSCUT and isTightVJet:
                    cut[5] = cut[5] + 1
                if jpt_8 > PTCUT and jmsd_8 > MASSCUT and isTightVJet and neleLoose == 0 and nmuLoose == 0:
                    cut[0] = cut[0] + 1
                if jpt_8 > PTCUT and jmsd_8 > MASSCUT and isTightVJet and neleLoose == 0 and nmuLoose == 0 and ntau == 0:
                    cut[1] = cut[1] + 1
                if jpt_8 > PTCUT and jmsd_8 > MASSCUT and isTightVJet and neleLoose == 0 and nmuLoose == 0 and ntau == 0 and nphoLoose == 0:
                    cut[2] = cut[2] + 1

                if jpt_8 > PTCUT:
                    self.h_msd_ak8_inc.Fill(jmsd_8, weight)
                    if jt21P_8 < T21DDTCUT:
                        self.h_msd_ak8_t21ddtCut_inc.Fill(jmsd_8, weight)

            # Lepton and photon veto
            if neleLoose != 0 or nmuLoose != 0 or ntau != 0: continue  # or nphoLoose != 0:  continue

            if not self._minBranches:
                a = 0
                for i in sorted(bb_idx, key=lambda bbtag: bbtag[2], reverse=True):
                    if a > 0: continue
                    a = a + 1
                    if i[2] > DBTAGCUT and i[0] > MASSCUT and i[1] > PTCUT:
                        self.h_msd_bbleading.Fill(i[0], weight)
                        # print sorted(bb_idx, key=lambda bbtag: bbtag[2],reverse=True)
                        self.h_pt_bbleading.Fill(i[1], weight)
                        # print(i[0],i[1],i[2])
                        self.h_bb_bbleading.Fill(i[2], weight)
                    if i[1] > PTCUT and i[0] > MASSCUT and met < METCUT and n_dR0p8_4 < NJETCUT and i[3] < 2 and i[
                        4] < T21DDTCUT and n_fwd_4 < 3 and i[5]:
                        if i[2] > DBTAGCUT:
                            self.h_msd_ak8_bbleading_topR6_pass.Fill(i[0], weight)
                            self.h_msd_v_pt_ak8_bbleading_topR6_pass.Fill(i[0], i[1], weight)
                        else:
                            self.h_msd_ak8_bbleading_topR6_fail.Fill(i[0], weight)
                            self.h_msd_v_pt_ak8_bbleading_topR6_fail.Fill(i[0], i[1], weight)

		if jpt_8 > PTCUT and jmsd_8 > MASSCUT:
	            self.h_rho_ak8_nocut.Fill(rh_8, weight)

                if jpt_8 > PTCUT:
                    self.h_msd_ak8_nocut.Fill(jmsd_8, weight)
                    self.h_msd_ak8_raw_nocut.Fill(jmsd_8_raw, weight) 

                if jpt_8 > PTCUT and jmsd_8 > MASSCUT and rh_8<-2.1 and rh_8>-6.:
                    self.h_pt_ak8.Fill(jpt_8, weight)
                    self.h_eta_ak8.Fill(jeta_8, weight)
                    self.h_pt_ak8_sub1.Fill(jpt_8_sub1, weight)
                    self.h_pt_ak8_sub2.Fill(jpt_8_sub2, weight)
                    self.h_msd_ak8.Fill(jmsd_8, weight)
		    self.h_rho_ak8.Fill(rh_8, weight)
                    self.h_msd_ak8_raw.Fill(jmsd_8_raw, weight)
                    self.h_dbtag_ak8.Fill(jdb_8, weight)
                    self.h_dbtag_ak8_sub1.Fill(jdb_8_sub1, weight)
                    self.h_dbtag_ak8_sub2.Fill(jdb_8_sub2, weight)
                    self.h_t21_ak8.Fill(jt21_8, weight)
                    self.h_t32_ak8.Fill(jt32_8, weight)
                    self.h_t21ddt_ak8.Fill(jt21P_8, weight)
                    self.h_rhop_v_t21_ak8.Fill(rhP_8, jt21_8, weight)
                    self.h_n2b1sd_ak8.Fill(jtN2b1sd_8, weight)
                    self.h_n2b1sdddt_ak8.Fill(jtN2b1sdddt_8, weight)
		
                    self.h_n_ak4.Fill(n_4, weight)
                    self.h_n_ak4_dR0p8.Fill(n_dR0p8_4, weight)
                    self.h_n_ak4fwd.Fill(n_fwd_4, weight)
                    self.h_n_ak4L.Fill(n_LdR0p8_4, weight)
                    self.h_n_ak4L100.Fill(n_LPt100dR0p8_4, weight)
                    self.h_n_ak4M.Fill(n_MdR0p8_4, weight)
                    self.h_n_ak4M100.Fill(n_MPt100dR0p8_4, weight)
                    self.h_n_ak4T.Fill(n_TdR0p8_4, weight)
                    self.h_n_ak4T100.Fill(n_TPt100dR0p8_4, weight)
                    self.h_n_ak4L150.Fill(n_LPt150dR0p8_4, weight)
                    self.h_n_ak4M150.Fill(n_MPt150dR0p8_4, weight)
                    self.h_n_ak4T150.Fill(n_TPt150dR0p8_4, weight)
                    self.h_isolationCA15.Fill(ratioCA15_04, weight)
                    self.h_met.Fill(met, weight)

                if jpt_8 > PTCUT and jt21P_8 < T21DDTCUT and jmsd_8 > MASSCUT:
                    self.h_msd_ak8_t21ddtCut.Fill(jmsd_8, weight)
                    self.h_t32_ak8_t21ddtCut.Fill(jt32_8, weight)

                if jpt_8 > PTCUT and jtN2b1sdddt_8 < 0 and jmsd_8 > MASSCUT:
                    self.h_msd_ak8_N2Cut.Fill(jmsd_8, weight)

                if jpt_8 > PTCUT and jmsd_8 > MASSCUT and met < METCUT and n_dR0p8_4 < NJETCUT and n_TdR0p8_4 < 3 and isTightVJet:
                    self.h_msd_ak8_topR1.Fill(jmsd_8, weight)
                    self.h_msd_v_pt_ak8_topR1.Fill(jmsd_8, jpt_8, weight)
                if jpt_8 > PTCUT and jmsd_8 > MASSCUT and met < METCUT and n_dR0p8_4 < NJETCUT and n_TdR0p8_4 < 3 and isTightVJet:
                    if jdb_8 > DBTAGCUT:
                        self.h_msd_ak8_topR2_pass.Fill(jmsd_8, weight)
                        self.h_msd_v_pt_ak8_topR2_pass.Fill(jmsd_8, jpt_8, weight)
                    elif jdb_8 > self.DBTAGCUTMIN:
                        self.h_msd_ak8_topR2_fail.Fill(jmsd_8, weight)
                        self.h_msd_v_pt_ak8_topR2_fail.Fill(jmsd_8, jpt_8, weight)
                if jpt_8 > PTCUT and jmsd_8 > MASSCUT and met < METCUT and n_dR0p8_4 < NJETCUT and n_TdR0p8_4 < 3 and jt21P_8 < 0.4 and isTightVJet:
                    if jdb_8 > DBTAGCUT:
                        self.h_msd_ak8_topR3_pass.Fill(jmsd_8, weight)
                        self.h_msd_v_pt_ak8_topR3_pass.Fill(jmsd_8, jpt_8, weight)
                    elif jdb_8 > self.DBTAGCUTMIN:
                        self.h_msd_ak8_topR3_fail.Fill(jmsd_8, weight)
                        self.h_msd_v_pt_ak8_topR3_fail.Fill(jmsd_8, jpt_8, weight)
                if jpt_8 > PTCUT and jmsd_8 > MASSCUT and jt21P_8 < 0.4 and jt32_8 > 0.7 and isTightVJet:
                    if jdb_8 > DBTAGCUT:
                        self.h_msd_ak8_topR4_pass.Fill(jmsd_8, weight)
                        self.h_msd_v_pt_ak8_topR4_pass.Fill(jmsd_8, jpt_8, weight)
                    elif jdb_8 > self.DBTAGCUTMIN:
                        self.h_msd_ak8_topR4_fail.Fill(jmsd_8, weight)
                        self.h_msd_v_pt_ak8_topR4_fail.Fill(jmsd_8, jpt_8, weight)
                if jpt_8 > PTCUT and jmsd_8 > MASSCUT and met < METCUT and n_dR0p8_4 < NJETCUT and n_MPt100dR0p8_4 < 2 and jt21P_8 < T21DDTCUT and n_fwd_4 < 3 and isTightVJet:
                    if jdb_8 > DBTAGCUT:
                        self.h_msd_ak8_topR5_pass.Fill(jmsd_8, weight)
                        self.h_msd_v_pt_ak8_topR5_pass.Fill(jmsd_8, jpt_8, weight)
                    elif jdb_8 > self.DBTAGCUTMIN:
                        self.h_msd_ak8_topR5_fail.Fill(jmsd_8, weight)
                        self.h_msd_v_pt_ak8_topR5_fail.Fill(jmsd_8, jpt_8, weight)

            if jpt_8 > PTCUT and jmsd_8 > MASSCUT and met < METCUT and isTightVJet:
                cut[6] = cut[6] + 1
            #if jpt_8 > PTCUT and jmsd_8 > MASSCUT and met < METCUT and n_dR0p8_4 < NJETCUT and isTightVJet:
                #cut[7] = cut[7] + 1
            if (not self._minBranches) and jpt_8 > PTCUT and jmsd_8 > MASSCUT and met < METCUT and n_dR0p8_4 < NJETCUT and jt21P_8 < T21DDTCUT and isTightVJet:
                if jdb_8 > DBTAGCUT:
                    # cut[9]=cut[9]+1
                    self.h_msd_ak8_topR6_pass.Fill(jmsd_8, weight)
                    self.h_msd_ak8_raw_SR_pass.Fill(jmsd_8_raw, weight)
                    self.h_msd_v_pt_ak8_topR6_pass.Fill(jmsd_8, jpt_8, weight)
                    self.h_msd_v_pt_ak8_topR6_raw_pass.Fill(jmsd_8_raw, jpt_8, weight)
                    # for signal morphing
                    if dphi < 0.8 and dpt < 0.5 and dmass < 0.3:
                        self.h_msd_v_pt_ak8_topR6_pass_matched.Fill(jmsd_8, jpt_8, weight)
                    else:
                        self.h_msd_v_pt_ak8_topR6_pass_unmatched.Fill(jmsd_8, jpt_8, weight)
                elif jdb_8 > self.DBTAGCUTMIN:
                    self.h_msd_ak8_topR6_fail.Fill(jmsd_8, weight)
                    self.h_msd_v_pt_ak8_topR6_fail.Fill(jmsd_8, jpt_8, weight)
                    self.h_msd_ak8_raw_SR_fail.Fill(jmsd_8_raw, weight)
                    self.h_msd_v_pt_ak8_topR6_raw_fail.Fill(jmsd_8, jpt_8, weight)
                    # for signal morphing
                    if dphi < 0.8 and dpt < 0.5 and dmass < 0.3:
                        self.h_msd_v_pt_ak8_topR6_fail_matched.Fill(jmsd_8, jpt_8, weight)
                    else:
                        self.h_msd_v_pt_ak8_topR6_fail_unmatched.Fill(jmsd_8, jpt_8, weight)
	    if jpt_8 > PTCUT and jmsd_8 > MASSCUT and met < METCUT and n_dR0p8_4 < NJETCUT and isTightVJet and jdb_8 > DBTAGCUT and rh_8<-2.1 and rh_8>-6.: 	
		if (not self._minBranches): self.h_n2b1sdddt_ak8_aftercut.Fill(jtN2b1sdddt_8,weight)
            if jpt_8 > PTCUT and jmsd_8 > MASSCUT and met < METCUT and n_dR0p8_4 < NJETCUT and jtN2b1sdddt_8 < 0 and isTightVJet:
                cut[8] = cut[8] + 1
		if  rh_8<-2.1 and rh_8>-6.:
		    cut[7] = cut[7] + 1
		    if (not self._minBranches): self.h_dbtag_ak8_aftercut.Fill(jdb_8,weight)
                if jdb_8 > DBTAGCUT:
                    cut[9] = cut[9] + 1
                    self.h_msd_ak8_topR6_N2_pass.Fill(jmsd_8, weight)
                    self.h_msd_v_pt_ak8_topR6_N2_pass.Fill(jmsd_8, jpt_8, weight)
                    self.h_msd_v_pt_ak8_topR6_N2_pass_triggerUp.Fill(jmsd_8, jpt_8, weight_triggerUp)
                    self.h_msd_v_pt_ak8_topR6_N2_pass_triggerDown.Fill(jmsd_8, jpt_8, weight_triggerDown)
                    self.h_msd_v_pt_ak8_topR6_N2_pass_PuUp.Fill(jmsd_8, jpt_8, weight_pu_up)
                    self.h_msd_v_pt_ak8_topR6_N2_pass_PuDown.Fill(jmsd_8, jpt_8, weight_pu_down)

                    # for signal morphing
                    if dphi < 0.8 and dpt < 0.5 and dmass < 0.3:
                        self.h_msd_v_pt_ak8_topR6_N2_pass_matched.Fill(jmsd_8, jpt_8, weight)
                    else:
                        self.h_msd_v_pt_ak8_topR6_N2_pass_unmatched.Fill(jmsd_8, jpt_8, weight)
                elif jdb_8 > self.DBTAGCUTMIN:
                    self.h_msd_ak8_topR6_N2_fail.Fill(jmsd_8, weight)
                    self.h_msd_v_pt_ak8_topR6_N2_fail.Fill(jmsd_8, jpt_8, weight)
                    self.h_msd_v_pt_ak8_topR6_N2_fail_triggerUp.Fill(jmsd_8, jpt_8, weight_triggerUp)
                    self.h_msd_v_pt_ak8_topR6_N2_fail_triggerDown.Fill(jmsd_8, jpt_8, weight_triggerDown)
                    self.h_msd_v_pt_ak8_topR6_N2_fail_PuUp.Fill(jmsd_8, jpt_8, weight_pu_up)
                    self.h_msd_v_pt_ak8_topR6_N2_fail_PuDown.Fill(jmsd_8, jpt_8, weight_pu_down)

                    # for signal morphing
                    if dphi < 0.8 and dpt < 0.5 and dmass < 0.3:
                        self.h_msd_v_pt_ak8_topR6_N2_fail_matched.Fill(jmsd_8, jpt_8, weight)
                    else:
                        self.h_msd_v_pt_ak8_topR6_N2_fail_unmatched.Fill(jmsd_8, jpt_8, weight)

            for syst in ['JESUp', 'JESDown', 'JERUp', 'JERDown']:
                if (not self._minBranches) and eval('jpt_8_%s' % syst) > PTCUT and jmsd_8 > MASSCUT and eval('met_%s' % syst) < METCUT and eval(
                                'n_dR0p8_4_%s' % syst) < NJETCUT and jt21P_8 < T21DDTCUT and isTightVJet:
                    if jdb_8 > DBTAGCUT:
                        (getattr(self, 'h_msd_ak8_topR6_pass_%s' % syst)).Fill(jmsd_8, weight)
                        (getattr(self, 'h_msd_v_pt_ak8_topR6_pass_%s' % syst)).Fill(jmsd_8, eval('jpt_8_%s' % syst),
                                                                                    weight)
                    elif jdb_8 > self.DBTAGCUTMIN:
                        (getattr(self, 'h_msd_ak8_topR6_fail_%s' % syst)).Fill(jmsd_8, weight)
                        (getattr(self, 'h_msd_v_pt_ak8_topR6_fail_%s' % syst)).Fill(jmsd_8, eval('jpt_8_%s' % syst),
                                                                                    weight)
                if eval('jpt_8_%s' % syst) > PTCUT and jmsd_8 > MASSCUT and eval('met_%s' % syst) < METCUT and eval(
                                'n_dR0p8_4_%s' % syst) < NJETCUT and jtN2b1sdddt_8 < 0 and isTightVJet:
                    if jdb_8 > DBTAGCUT:
                        (getattr(self, 'h_msd_ak8_topR6_N2_pass_%s' % syst)).Fill(jmsd_8, weight)
                        (getattr(self, 'h_msd_v_pt_ak8_topR6_N2_pass_%s' % syst)).Fill(jmsd_8, eval('jpt_8_%s' % syst),
                                                                                       weight)
                    elif jdb_8 > self.DBTAGCUTMIN:
                        (getattr(self, 'h_msd_ak8_topR6_N2_fail_%s' % syst)).Fill(jmsd_8, weight)
                        (getattr(self, 'h_msd_v_pt_ak8_topR6_N2_fail_%s' % syst)).Fill(jmsd_8, eval('jpt_8_%s' % syst),
                                                                                       weight)

            ###Double-b optimization for ggH
            if not self._minBranches:
                dbcuts = [0.7, 0.75, 0.8, 0.85, 0.9, 0.95]
                for dbcut in dbcuts:
                    # using tau21DDT
                    if jpt_8 > PTCUT and jmsd_8 > MASSCUT and met < METCUT and n_dR0p8_4 < NJETCUT and jt21P_8 < T21DDTCUT and isTightVJet:
                        if jdb_8 > dbcut:
                            getattr(self,'h_msd_ak8_topR6_%s_pass'%str(dbcut).replace('0.','p')).Fill(jmsd_8, weight)
                            getattr(self,'h_msd_v_pt_ak8_topR6_%s_pass'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight)
                            getattr(self,'h_msd_v_pt_ak8_topR6_%s_pass_PuUp'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight_pu_up)
                            getattr(self,'h_msd_v_pt_ak8_topR6_%s_pass_PuDown'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight_pu_down)
                            getattr(self,'h_msd_v_pt_ak8_topR6_%s_pass_triggerUp'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight_triggerUp)
                            getattr(self,'h_msd_v_pt_ak8_topR6_%s_pass_triggerDown'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight_triggerDown)
                            # for signal morphing
                            if dphi < 0.8 and dpt < 0.5 and dmass < 0.3:
                                getattr(self,'h_msd_v_pt_ak8_topR6_%s_pass_matched'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight)
                            else: 
                                getattr(self,'h_msd_v_pt_ak8_topR6_%s_pass_unmatched'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight)
                        else:
                            getattr(self,'h_msd_ak8_topR6_%s_fail'%str(dbcut).replace('0.','p')).Fill(jmsd_8, weight)
                            getattr(self,'h_msd_v_pt_ak8_topR6_%s_fail'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight)
                            getattr(self,'h_msd_v_pt_ak8_topR6_%s_fail_PuUp'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight_pu_up)
                            getattr(self,'h_msd_v_pt_ak8_topR6_%s_fail_PuDown'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight_pu_down)
                            getattr(self,'h_msd_v_pt_ak8_topR6_%s_fail_triggerUp'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight_triggerUp)
                            getattr(self,'h_msd_v_pt_ak8_topR6_%s_fail_triggerDown'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight_triggerDown)
                            # for signal morphing
                            if dphi < 0.8 and dpt < 0.5 and dmass < 0.3:
                                getattr(self,'h_msd_v_pt_ak8_topR6_%s_fail_matched'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight)
                            else: 
                                getattr(self,'h_msd_v_pt_ak8_topR6_%s_fail_unmatched'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight)
                    for syst in ['JESUp', 'JESDown', 'JERUp', 'JERDown']:
                        if eval('jpt_8_%s' % syst) > PTCUT and jmsd_8 > MASSCUT and eval('met_%s' % syst) < METCUT and eval('n_dR0p8_4_%s' % syst) < NJETCUT and jt21P_8 < T21DDTCUT and isTightVJet:
                            if jdb_8 > dbcut:
                                getattr(self, 'h_msd_v_pt_ak8_topR6_%s_pass_%s' % (str(dbcut).replace('0.','p'),syst)).Fill(jmsd_8, eval('jpt_8_%s' % syst),weight)
                            else:
                                getattr(self, 'h_msd_v_pt_ak8_topR6_%s_fail_%s' % (str(dbcut).replace('0.','p'),syst)).Fill(jmsd_8, eval('jpt_8_%s' % syst),weight)
                    # using N2DDT
                    if jpt_8 > PTCUT and jmsd_8 > MASSCUT and met < METCUT and n_dR0p8_4 < NJETCUT and jtN2b1sdddt_8 < 0 and isTightVJet:
                        if jdb_8 > dbcut:
                            getattr(self,'h_msd_ak8_topR6_N2_%s_pass'%str(dbcut).replace('0.','p')).Fill(jmsd_8, weight)
                            getattr(self,'h_msd_v_pt_ak8_topR6_N2_%s_pass'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight)
                            getattr(self,'h_msd_v_pt_ak8_topR6_N2_%s_pass_PuUp'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight_pu_up)
                            getattr(self,'h_msd_v_pt_ak8_topR6_N2_%s_pass_PuDown'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight_pu_down)
                            getattr(self,'h_msd_v_pt_ak8_topR6_N2_%s_pass_triggerUp'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight_triggerUp)
                            getattr(self,'h_msd_v_pt_ak8_topR6_N2_%s_pass_triggerDown'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight_triggerDown)
                            # for signal morphing
                            if dphi < 0.8 and dpt < 0.5 and dmass < 0.3:
                                getattr(self,'h_msd_v_pt_ak8_topR6_N2_%s_pass_matched'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight)
                            else: 
                                getattr(self,'h_msd_v_pt_ak8_topR6_N2_%s_pass_unmatched'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight)
                        else:
                            getattr(self,'h_msd_ak8_topR6_N2_%s_fail'%str(dbcut).replace('0.','p')).Fill(jmsd_8, weight)
                            getattr(self,'h_msd_v_pt_ak8_topR6_N2_%s_fail'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight)
                            getattr(self,'h_msd_v_pt_ak8_topR6_N2_%s_fail_PuUp'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight_pu_up)
                            getattr(self,'h_msd_v_pt_ak8_topR6_N2_%s_fail_PuDown'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight_pu_down)
                            getattr(self,'h_msd_v_pt_ak8_topR6_N2_%s_fail_triggerUp'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight_triggerUp)
                            getattr(self,'h_msd_v_pt_ak8_topR6_N2_%s_fail_triggerDown'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight_triggerDown)
                            # for signal morphing
                            if dphi < 0.8 and dpt < 0.5 and dmass < 0.3:
                                getattr(self,'h_msd_v_pt_ak8_topR6_N2_%s_fail_matched'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight)
                            else: 
                                getattr(self,'h_msd_v_pt_ak8_topR6_N2_%s_fail_unmatched'%str(dbcut).replace('0.','p')).Fill(jmsd_8, jpt_8, weight)
                    for syst in ['JESUp', 'JESDown', 'JERUp', 'JERDown']:
                        if eval('jpt_8_%s' % syst) > PTCUT and jmsd_8 > MASSCUT and eval('met_%s' % syst) < METCUT and eval('n_dR0p8_4_%s' % syst) < NJETCUT and jtN2b1sdddt_8 < 0 and isTightVJet:
                            if jdb_8 > dbcut:
                                getattr(self, 'h_msd_v_pt_ak8_topR6_N2_%s_pass_%s' % (str(dbcut).replace('0.','p'),syst)).Fill(jmsd_8, eval('jpt_8_%s' % syst),weight)
                            else:
                                getattr(self, 'h_msd_v_pt_ak8_topR6_N2_%s_fail_%s' % (str(dbcut).replace('0.','p'),syst)).Fill(jmsd_8, eval('jpt_8_%s' % syst),weight)


#
                ################################
                if jpt_8 > PTCUT and jmsd_8 > MASSCUT and jpt_8_sub1 < 300 and met < METCUT and n_dR0p8_4 < NJETCUT and n_TdR0p8_4 < 3 and jt21P_8 < 0.4 and isTightVJet:
                    if jdb_8 > DBTAGCUT:
                        self.h_msd_ak8_topR7_pass.Fill(jmsd_8, weight)
                        self.h_msd_v_pt_ak8_topR7_pass.Fill(jmsd_8, jpt_8, weight)
                    elif jdb_8 > self.DBTAGCUTMIN:
                        self.h_msd_ak8_topR7_fail.Fill(jmsd_8, weight)
                        self.h_msd_v_pt_ak8_topR7_fail.Fill(jmsd_8, jpt_8, weight)

                if jpt_8 > PTCUT and jdb_8 > DBTAGCUT and jmsd_8 > MASSCUT:
                    self.h_msd_ak8_dbtagCut.Fill(jmsd_8, weight)
                    self.h_pt_ak8_dbtagCut.Fill(jpt_8, weight)

            ##### CA15 info
            if not self._fillCA15: continue

            jmsd_15 = self.CA15Puppijet0_msd[0]
            jpt_15 = self.CA15Puppijet0_pt[0]
            if jmsd_15 <= 0: jmsd_15 = 0.01
            rhP_15 = math.log(jmsd_15 * jmsd_15 / jpt_15)
            jt21_15 = self.CA15Puppijet0_tau21[0]
            jt21P_15 = jt21_15 + 0.075 * rhP_15

            if jpt_15 > PTCUT:
                self.h_pt_ca15.Fill(jpt_15, weight)
                self.h_msd_ca15.Fill(jmsd_15, weight)
                self.h_t21_ca15.Fill(jt21_15, weight)
                self.h_t21ddt_ca15.Fill(jt21P_15, weight)
                self.h_rhop_v_t21_ca15.Fill(rhP_15, jt21_15, weight)

            if jpt_15 > PTCUT and jt21P_15 < 0.4:
                self.h_msd_ca15_t21ddtCut.Fill(jmsd_15, weight)
                #####
        print "\n"
        
        if not self._minBranches and cut[3] > 0.:
            self.h_Cuts.SetBinContent(4, float(cut[0] / cut[3] * 100.))
            self.h_Cuts.SetBinContent(5, float(cut[1] / cut[3] * 100.))
            # self.h_Cuts.SetBinContent(6,float(cut[2]/nent*100.))
            self.h_Cuts.SetBinContent(1, float(cut[3] / cut[3] * 100.))
            self.h_Cuts.SetBinContent(2, float(cut[4] / cut[3] * 100.))
            self.h_Cuts.SetBinContent(3, float(cut[5] / cut[3] * 100.))
            self.h_Cuts.SetBinContent(6, float(cut[6] / cut[3] * 100.))
            #self.h_Cuts.SetBinContent(7, float(cut[7] / cut[3] * 100.))
            #self.h_Cuts.SetBinContent(9,float(cut[8]/nent*100.))
            self.h_Cuts.SetBinContent(8,float(cut[7]/ cut[3]  *100.))
            self.h_Cuts.SetBinContent(7, float(cut[8]) / cut[3] * 100.)
            print(cut[0] / nent * 100., cut[7], cut[8], cut[9])
            a_Cuts = self.h_Cuts.GetXaxis()
            a_Cuts.SetBinLabel(4, "lep veto")
            a_Cuts.SetBinLabel(5, "#tau veto")
            # a_Cuts.SetBinLabel(6, "#gamma veto")
            a_Cuts.SetBinLabel(1, "p_{T}>450 GeV")
            a_Cuts.SetBinLabel(2, "m_{SD}>40 GeV")
            a_Cuts.SetBinLabel(3, "tight ID")
            a_Cuts.SetBinLabel(6, "MET<140")
#            a_Cuts.SetBinLabel(7, "njet<5")
            a_Cuts.SetBinLabel(7, "N2^{DDT}<0")
	    a_Cuts.SetBinLabel(8, "-6<#rho<-2.1")

            self.h_rhop_v_t21_ak8_Px = self.h_rhop_v_t21_ak8.ProfileX()
            self.h_rhop_v_t21_ca15_Px = self.h_rhop_v_t21_ca15.ProfileX()
            self.h_rhop_v_t21_ak8_Px.SetTitle("; rho^{DDT}; <#tau_{21}>")
            self.h_rhop_v_t21_ca15_Px.SetTitle("; rho^{DDT}; <#tau_{21}>")

    def PUPPIweight(self, puppipt=30., puppieta=0.):

        genCorr = 1.
        recoCorr = 1.
        totalWeight = 1.

        genCorr = self.corrGEN.Eval(puppipt)
        if (abs(puppieta) < 1.3):
            recoCorr = self.corrRECO_cen.Eval(puppipt)
        else:
            recoCorr = self.corrRECO_for.Eval(puppipt)
        totalWeight = genCorr * recoCorr
        return totalWeight

##########################################################################################
