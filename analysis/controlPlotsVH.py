import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array
import glob
import os
from plotHelpers1lep import *
from sampleContainer1lep import *

DBTMIN = -99


#
def makePlots(plot, hs, hb, hd, hall, legname, color, style, isData, odir, lumi, ofile, canvases):
    if isData:
        c = makeCanvasComparisonStackWData(hd, hs, hb, legname, color, style, plot.replace('h_', 'stack_'), odir, lumi,
                                           ofile)
        canvases.append(c)
    else:
        c = makeCanvasComparisonStack(hs, hb, legname, color, style, 'WHbb', plot.replace('h_', 'stack_'), odir, lumi,
                                      True, ofile)
    #    c1 = makeCanvasComparison(hall, legname, color, style, plot.replace('h_', 'signalcomparison_'), odir, lumi,
    #                              ofile, True)
        canvases.append(c)
        #canvases.append(c1)


##############################################################################
def main(options, args, outputExists):
    # idir = "/eos/uscms/store/user/lpchbb/ggHsample_V11/sklim-v0-28Oct/"
    # odir = "plots_2016_10_31/"
    # idir = options.idir
    idir = "root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/norm2/cvernier/"
    idirWH = "root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier/" 	
    idirMuon = "root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier/"
    idirData = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.05/'
    odir = options.odir
    lumi = options.lumi
    fillCA15 = options.fillCA15
    isData = options.isData
    muonCR = options.muonCR

    legname = {'ggHbb': 'ggH(b#bar{b})',
               'Hbb': 'H(b#bar{b})',
               'VBFHbb': 'VBF H(b#bar{b})',
               'ZHbb': 'ZH(b#bar{b})',
               'WHbb': ' WH(b#bar{b})',
               'ttHbb': 't#bar{t}H(b#bar{b})',
               'Diboson': 'WW+WZ+ZZ',
               'SingleTop': 'single-t',
               'DY': 'Z(qq)+jets',
               'W': 'W(qq)+jets',
               'DYll': 'Z(ll)+jets',
               'Wlnu': 'W(l#nu)+jets',
               'TTbar': 't#bar{t}+jets',
               'TTbar1Mu': 't#bar{t}+jets, 1#mu',
               'TTbar1Ele': 't#bar{t}+jets, 1e',
               'TTbar1Tau': 't#bar{t}+jets, 1#tau',
               'TTbar1Lep': 't#bar{t}+jets, 1l',
               'TTbar0Lep': 't#bar{t}+jets, 0l',
               'TTbar2Lep': 't#bar{t}+jets, 2l',
               'QCD': 'QCD',
               'data': 'JetHT data',
               'muon': 'SingleMuon data',
               'Phibb50': '#Phi(b#bar{b}), 50 GeV',
               'Phibb75': '#Phi(b#bar{b}), 75 GeV',
               'Phibb150': '#Phi(b#bar{b}), 150 GeV',
               'Phibb250': '#Phi(b#bar{b}), 250 GeV'
               }

    if isData and muonCR:
        legname['data'] = 'SingleMuon data'

    tfiles = {'Hbb': [idirData + '/GluGluHToBB_M125_13TeV_powheg_pythia8_CKKW_1000pb_weighted.root',
                      idir + '/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root',
                      idir + '/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                      idirWH + '/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                      idirWH + '/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                      idir + '/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                      idir + '/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                      idir + '/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                      idirWH + '/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root'],
              'ggHbb': [idirData + '/GluGluHToBB_M125_13TeV_powheg_pythia8_CKKW_1000pb_weighted.root'],
              # idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root'],
              'VBFHbb': [idir + '/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root'],
              'ZHbb': [idirWH + '/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idirWH + '/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root',
                       idirWH + '/ZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idirWH + '/ggZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
              'WHbb': [idirWH + '/WminusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idirWH + 'WplusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
              'Diboson': [idir + '/WW_13TeV_pythia8_1000pb_weighted.root',
                          idir + '/ZZ_13TeV_pythia8_1000pb_weighted.root',
                          idir + 'WZ_13TeV_pythia8_1000pb_weighted.root'],
              'ttHbb': [idir + '/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
              # ttHTobb_M125_TuneCUETP8M2_ttHtranche3_13TeV_powheg_pythia8_1000pb_weighted.root'],
              'DY': [idirData + '/DYJetsToQQ_HT180_13TeV_1000pb_weighted.root'],
              'DYll': [idir + '/DYJetsToLL_M_50_13TeV_ext_1000pb_weighted.root'],
              'SingleTop': [
                  idir + '/ST_t_channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
                  idir + '/ST_t_channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
                  idir + '/ST_tW_antitop_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root',
                  idir + '/ST_tW_top_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root'],
              'W': [idirData + '/WJetsToQQ_HT180_13TeV_1000pb_weighted.root'],
              'Wlnu': [idir + 'WJetsToLNu_HT_100To200_13TeV_1000pb_weighted.root',
                       idir + '/WJetsToLNu_HT_200To400_13TeV_1000pb_weighted.root',
                       idir + '/WJetsToLNu_HT_400To600_13TeV_1000pb_weighted.root',
                       idir + '/WJetsToLNu_HT_600To800_13TeV_1000pb_weighted.root',
                       idir + '/WJetsToLNu_HT_800To1200_13TeV_1000pb_weighted.root',
                       idir + '/WJetsToLNu_HT_1200To2500_13TeV_1000pb_weighted.root',
                       idir + '/WJetsToLNu_HT_2500ToInf_13TeV_1000pb_weighted.root'],
              'TTbar': [idir + '/TT_powheg_1000pb_weighted.root'],  # Powheg is the new default
              'QCD': [idirData + '/QCD_HT100to200_13TeV_1000pb_weighted.root',
                      idirData + '/QCD_HT200to300_13TeV_1000pb_weighted.root',
                      idirData + '/QCD_HT300to500_13TeV_all_1000pb_weighted.root',
                      idirData + '/QCD_HT500to700_13TeV_1000pb_weighted.root',
                      idirData + '/QCD_HT700to1000_13TeV_1000pb_weighted.root',
                      idirData + '/QCD_HT1000to1500_13TeV_1000pb_weighted.root',
                      idirData + '/QCD_HT1500to2000_13TeV_all_1000pb_weighted.root',
                      idirData + '/QCD_HT2000toInf_13TeV_all_1000pb_weighted.root'],
              'Phibb50': [idirData + '/Spin0_ggPhibb1j_g1_50_Scalar_1000pb_weighted.root'],
              'Phibb75': [idirData + '/Spin0_ggPhibb1j_g1_75_Scalar_1000pb_weighted.root'],
              'Phibb150': [idirData + '/Spin0_ggPhibb1j_g1_150_Scalar_1000pb_weighted.root'],
              'Phibb250': [idirData + '/Spin0_ggPhibb1j_g1_250_Scalar_1000pb_weighted.root'],
              'data': [
                  idirData + 'JetHTRun2016B_03Feb2017_ver2_v2_v3.root',
                  idirData + 'JetHTRun2016B_03Feb2017_ver1_v1_v3.root',
                  idirData + 'JetHTRun2016C_03Feb2017_v1_v3_0.root',
                  idirData + 'JetHTRun2016C_03Feb2017_v1_v3_1.root',
                  idirData + 'JetHTRun2016C_03Feb2017_v1_v3_2.root',
                  idirData + 'JetHTRun2016C_03Feb2017_v1_v3_3.root',
                  idirData + 'JetHTRun2016C_03Feb2017_v1_v3_4.root',
                  idirData + 'JetHTRun2016C_03Feb2017_v1_v3_5.root',
                  idirData + 'JetHTRun2016C_03Feb2017_v1_v3_6.root',
                  idirData + 'JetHTRun2016C_03Feb2017_v1_v3_7.root',
                  idirData + 'JetHTRun2016C_03Feb2017_v1_v3_8.root',
                  idirData + 'JetHTRun2016C_03Feb2017_v1_v3_9.root',
                  idirData + 'JetHTRun2016D_03Feb2017_v1_v3_0.root',
                  idirData + 'JetHTRun2016D_03Feb2017_v1_v3_1.root',
                  idirData + 'JetHTRun2016D_03Feb2017_v1_v3_10.root',
                  idirData + 'JetHTRun2016D_03Feb2017_v1_v3_11.root',
                  idirData + 'JetHTRun2016D_03Feb2017_v1_v3_12.root',
                  idirData + 'JetHTRun2016D_03Feb2017_v1_v3_13.root',
                  idirData + 'JetHTRun2016D_03Feb2017_v1_v3_14.root',
                  idirData + 'JetHTRun2016D_03Feb2017_v1_v3_2.root',
                  idirData + 'JetHTRun2016D_03Feb2017_v1_v3_3.root',
                  idirData + 'JetHTRun2016D_03Feb2017_v1_v3_4.root',
                  idirData + 'JetHTRun2016D_03Feb2017_v1_v3_5.root',
                  idirData + 'JetHTRun2016D_03Feb2017_v1_v3_6.root',
                  idirData + 'JetHTRun2016D_03Feb2017_v1_v3_7.root',
                  idirData + 'JetHTRun2016D_03Feb2017_v1_v3_8.root',
                  idirData + 'JetHTRun2016D_03Feb2017_v1_v3_9.root',
                  idirData + 'JetHTRun2016E_03Feb2017_v1_v3_0.root',
                  idirData + 'JetHTRun2016E_03Feb2017_v1_v3_1.root',
                  idirData + 'JetHTRun2016E_03Feb2017_v1_v3_2.root',
                  idirData + 'JetHTRun2016E_03Feb2017_v1_v3_3.root',
                  idirData + 'JetHTRun2016E_03Feb2017_v1_v3_4.root',
                  idirData + 'JetHTRun2016E_03Feb2017_v1_v3_5.root',
                  idirData + 'JetHTRun2016E_03Feb2017_v1_v3_6.root',
                  idirData + 'JetHTRun2016E_03Feb2017_v1_v3_7.root',
                  idirData + 'JetHTRun2016E_03Feb2017_v1_v3_8.root',
                  idirData + 'JetHTRun2016E_03Feb2017_v1_v3_9.root',
                  idirData + 'JetHTRun2016E_03Feb2017_v1_v3_10.root',
                  idirData + 'JetHTRun2016E_03Feb2017_v1_v3_11.root',
                  idirData + 'JetHTRun2016E_03Feb2017_v1_v3_12.root',
                  idirData + 'JetHTRun2016E_03Feb2017_v1_v3_13.root',
                  idirData + 'JetHTRun2016E_03Feb2017_v1_v3_14.root',
                  idirData + 'JetHTRun2016F_03Feb2017_v1_v3_0.root',
                  idirData + 'JetHTRun2016F_03Feb2017_v1_v3_1.root',
                  idirData + 'JetHTRun2016F_03Feb2017_v1_v3_2.root',
                  idirData + 'JetHTRun2016F_03Feb2017_v1_v3_3.root',
                  idirData + 'JetHTRun2016F_03Feb2017_v1_v3_4.root',
                  idirData + 'JetHTRun2016F_03Feb2017_v1_v3_5.root',
                  idirData + 'JetHTRun2016F_03Feb2017_v1_v3_6.root',
                  idirData + 'JetHTRun2016F_03Feb2017_v1_v3_7.root',
                  idirData + 'JetHTRun2016F_03Feb2017_v1_v3_8.root',
                  idirData + 'JetHTRun2016F_03Feb2017_v1_v3_9.root',
                  idirData + 'JetHTRun2016F_03Feb2017_v1_v3_10.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_0.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_1.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_2.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_3.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_4.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_5.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_6.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_7.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_8.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_9.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_10.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_11.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_12.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_13.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_14.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_15.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_16.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_17.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_18.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_19.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_20.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_21.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_22.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_23.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_24.root',
                  idirData + 'JetHTRun2016G_03Feb2017_v1_v3_25.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_0.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_1.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_2.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_3.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_4.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_5.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_6.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_7.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_8.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_9.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_10.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_11.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_12.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_13.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_14.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_15.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_16.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_17.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_18.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_19.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_20.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_21.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_22.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_23.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_24.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_25.root',
                  idirData + 'JetHTRun2016H_03Feb2017_ver3_v1_v3.root'],
              'muon': [idirMuon + '/SingleMuonRun2016B_03Feb2017_ver1_v1_fixtrig.root',
                       idirMuon + '/SingleMuonRun2016B_03Feb2017_ver2_v2_fixtrig.root',
                       idirMuon + '/SingleMuonRun2016C_03Feb2017_v1_fixtrig.root',
                       idirMuon + '/SingleMuonRun2016D_03Feb2017_v1_fixtrig.root',
                       idirMuon + '/SingleMuonRun2016E_03Feb2017_v1_fixtrig.root',
                       idirMuon + '/SingleMuonRun2016F_03Feb2017_v1_fixtrig.root',
                       idirMuon + '/SingleMuonRun2016G_03Feb2017_v1_fixtrig.root',
                       idirMuon + '/SingleMuonRun2016H_03Feb2017_ver2_v1_fixtrig.root',
                       idirMuon + '/SingleMuonRun2016H_03Feb2017_ver3_v1_fixtrig.root']

              }

    color = {'ggHbb': ROOT.kAzure + 1,
             'Hbb': ROOT.kRed,
             'ZHbb': ROOT.kTeal + 1,
             'WHbb': ROOT.kTeal + 2,
             'VBFHbb': ROOT.kBlue - 10,
             'Phibb50': ROOT.kBlue - 1,
             'Phibb75': ROOT.kAzure + 1,
             'Phibb150': ROOT.kTeal + 1,
             'Phibb250': ROOT.kMagenta + 1,
             'ttHbb': ROOT.kBlue - 1,
             'Diboson': ROOT.kOrange,
             'SingleTop': ROOT.kRed - 2,
             'DY': ROOT.kRed,
             'DYll': ROOT.kRed - 3,
             'W': ROOT.kGreen + 3,
             'Wlnu': ROOT.kGreen + 2,
             'TTbar': ROOT.kGray,
             'TTbar1Mu': ROOT.kViolet,
             'TTbar1Lep': ROOT.kViolet,
             'TTbar1Ele': ROOT.kSpring,
             'TTbar1Tau': ROOT.kOrange + 2,
             'TTbar0Lep': ROOT.kGray,
             'TTbar2Lep': ROOT.kMagenta - 9,
             'QCD': ROOT.kAzure + 6,
             'data': ROOT.kBlack,
             'muon': ROOT.kBlack
             }

    style = {'Hbb': 1,
             'ggHbb': 2,
             'Phibb50': 2,
             'Phibb75': 3,
             'Phibb150': 4,
             'Phibb250': 5,
             'VBFHbb': 3,
             'ZHbb': 4,
             'WHbb': 4,
             'ttHbb': 5,
             'Diboson': 1,
             'SingleTop': 1,
             'DY': 1,
             'DYll': 1,
             'W': 1,
             'Wlnu': 1,
             'TTbar': 1,
             'TTbar1Mu': 1,
             'TTbar1Lep': 1,
             'TTbar1Ele': 1,
             'TTbar1Tau': 1,
             'TTbar0Lep': 1,
             'TTbar2Lep': 1,
             'QCD': 1,
             'data': 1,
             'muon': 1
             }

    canvases = []
    if isData and muonCR:
        plots = []
        testSample = sampleContainer('test', [], 1, DBTMIN, lumi)
        for attr in dir(testSample):
            try:
                if 'h_' in attr and getattr(testSample, attr).InheritsFrom('TH1') and not getattr(testSample,
                                                                                                  attr).InheritsFrom(
                        'TH2'):
                    plots.append(attr)
            except:
                pass
    elif isData:
        plots = ['h_pt_ak8', 'h_msd_ak8', 'h_dbtag_ak8', 'h_n_ak4', 'h_n_ak4_dR0p8', 'h_t21_ak8', 'h_t32_ak8',
                 'h_n2b1sdddt_ak8', 'h_t21ddt_ak8', 'h_met', 'h_npv', 'h_eta_ak8', 'h_ht', 'h_dbtag_ak8_aftercut',
                 'h_n2b1sdddt_ak8_aftercut', 'h_rho_ak8']
    else:
        plots = []
        testSample = sampleContainer('test', [], 1, DBTMIN, lumi)
        for attr in dir(testSample):
            try:
                if 'h_' in attr and getattr(testSample, attr).InheritsFrom('TH1') and not getattr(testSample,
                                                                                                  attr).InheritsFrom(
                        'TH2'):
                    plots.append(attr)
            except:
                pass

    if not outputExists:
        samples = ['ggHbb', 'VBFHbb', 'ZHbb', 'WHbb', 'QCD', 'SingleTop', 'Diboson', 'W', 'DY', 'TTbar']
        # for s in samples:
        #    for tfile in tfiles[s]:
        #        if not os.path.isfile(tfile):
        #            print 'error: %s does not exist'%tfile                 
        #            sys.exit()
        print "Signals... "
        sigSamples = {}
        # sigSamples['ggHbb']  = sampleContainer('ggHbb',tfiles['ggHbb']  , 1, DBTMIN, lumi, False, fillCA15)
        # sigSamples['VBFHbb'] = sampleContainer('VBFHbb',tfiles['VBFHbb'], 1, DBTMIN, lumi, False, fillCA15)
        # sigSamples['VHbb'] = sampleContainer('VHbb',tfiles['VHbb'], 1, DBTMIN, lumi, False, fillCA15)
        # sigSamples['ttHbb'] = sampleContainer('ttHbb',tfiles['ttHbb'], 1, DBTMIN, lumi, False, fillCA15)
        # sigSamples['Phibb50']  = sampleContainer('Phibb50',tfiles['Phibb50']  , 1, 0.2480*lumi, False, fillCA15)
        # sigSamples['Phibb75'] = sampleContainer('Phibb75',tfiles['Phibb75'], 1, 0.2080*lumi, False, fillCA15)
        # sigSamples['Phibb150'] = sampleContainer('Phibb150',tfiles['Phibb150'], 1, 0.2764*lumi, False, fillCA15)
        # sigSamples['Phibb250'] = sampleContainer('Phibb250',tfiles['Phibb250'], 1, 0.6699*lumi, False, fillCA15)
	sigSamples['WHbb'] = sampleContainer('WHbb', tfiles['WHbb'], 1, DBTMIN, lumi, False, fillCA15)
        sigSamples['ZHbb'] = sampleContainer('ZHbb', tfiles['ZHbb'], 1, DBTMIN, lumi, False, fillCA15)
        print "Backgrounds..."
        bkgSamples = {}
        # bkgSamples['W']  = sampleContainer('W',tfiles['W'], 1, DBTMIN, lumi, False, fillCA15)
        # bkgSamples['DY']  = sampleContainer('DY',tfiles['DY'], 1, DBTMIN, lumi, False, fillCA15)

        bkgSamples['QCD'] = sampleContainer('QCD', tfiles['QCD'], 1000, DBTMIN, lumi, False, fillCA15)
        if muonCR:
            bkgSamples['Wlnu'] = sampleContainer('Wlnu', tfiles['Wlnu'], 1, DBTMIN, lumi, False, fillCA15)
            bkgSamples['DYll'] = sampleContainer('DYll', tfiles['DYll'], 1, DBTMIN, lumi, False, fillCA15)
            #    bkgSamples['TTbar1Mu']  = sampleContainer('TTbar1Mu',tfiles['TTbar'], 1, DBTMIN, lumi, False, fillCA15, 'genMuFromW==1&&genEleFromW+genTauFromW==0')
            #    bkgSamples['TTbar1Ele']  = sampleContainer('TTbar1Ele',tfiles['TTbar'], 1, DBTMIN, lumi, False, fillCA15, 'genEleFromW==1&&genMuFromW+genTauFromW==0')
            #    bkgSamples['TTbar1Tau']  = sampleContainer('TTbar1Tau',tfiles['TTbar'], 1, DBTMIN, lumi, False, fillCA15, 'genTauFromW==1&&genEleFromW+genMuFromW==0')
            bkgSamples['TTbar1Lep'] = sampleContainer('TTbar1Lep', tfiles['TTbar'], 1, DBTMIN, lumi, False, fillCA15,
                                                      'genMuFromW+genEleFromW+genTauFromW==1')
            bkgSamples['TTbar0Lep'] = sampleContainer('TTbar0Lep', tfiles['TTbar'], 1, DBTMIN, lumi, False, fillCA15,
                                                      'genMuFromW+genEleFromW+genTauFromW==0')
            bkgSamples['TTbar2Lep'] = sampleContainer('TTbar2Lep', tfiles['TTbar'], 1, DBTMIN, lumi, False, fillCA15,
                                                      'genMuFromW+genEleFromW+genTauFromW==2')
        else:
            bkgSamples['TTbar'] = sampleContainer('TTbar', tfiles['TTbar'], 1, DBTMIN, lumi, False, fillCA15)
        bkgSamples['SingleTop'] = sampleContainer('SingleTop', tfiles['SingleTop'], 1, DBTMIN, lumi, False, fillCA15)
        bkgSamples['Diboson'] = sampleContainer('Diboson', tfiles['Diboson'], 1, DBTMIN, lumi, False, fillCA15)
        # bkgSamples['Hbb'] = sampleContainer('Hbb',tfiles['Hbb'], 1, lumi )

        if isData:
            print "Data..."
        if isData and muonCR:
            dataSample = sampleContainer('muon', tfiles['muon'], 1, DBTMIN, lumi, isData, fillCA15,
                                         '((triggerBits&4)&&passJson)')
        elif isData:
            dataSample = sampleContainer('data', tfiles['data'], 1, DBTMIN, lumi, isData, fillCA15,
                                         '((triggerBits&2)&&passJson)')

        ofile = ROOT.TFile.Open(odir + '/Plots_1000pb_weighted.root ', 'recreate')

        hall_byproc = {}
        for process, s in sigSamples.iteritems():
            hall_byproc[process] = {}
        for process, s in bkgSamples.iteritems():
            hall_byproc[process] = {}
        if isData:
            if muonCR:
                hall_byproc['muon'] = {}
            else:
                hall_byproc['data'] = {}

        for plot in plots:
            for process, s in sigSamples.iteritems():
                hall_byproc[process][plot] = getattr(s, plot)
            for process, s in bkgSamples.iteritems():
                hall_byproc[process][plot] = getattr(s, plot)
            if isData:
                if muonCR:
                    hall_byproc['muon'][plot] = getattr(dataSample, plot)
                else:
                    hall_byproc['data'][plot] = getattr(dataSample, plot)

        ofile.cd()
        for proc, hDict in hall_byproc.iteritems():
            for plot, h in hDict.iteritems():
                h.Write()

        for plot in plots:
            hs = {}
            hb = {}
            hall = {}
            hd = None
            for process, s in sigSamples.iteritems():
                hs[process] = getattr(s, plot)
                hall[process] = getattr(s, plot)
            for process, s in bkgSamples.iteritems():
                hb[process] = getattr(s, plot)
                hall[process] = getattr(s, plot)
            if isData:
                hd = getattr(dataSample, plot)
            makePlots(plot, hs, hb, hd, hall, legname, color, style, isData, odir, lumi, ofile, canvases)

        ofile.Close()
    else:
        sigSamples = ['ggHbb', 'VBFHbb', 'WHbb', 'ZHbb']
        bkgSamples = ['QCD', 'SingleTop', 'Diboson', 'W', 'DY']
        if muonCR:
            bkgSamples.extend(['Wlnu', 'DYll', 'TTbar1Lep', 'TTbar0Lep', 'TTbar2Lep'])
        else:
            bkgSamples.extend(['TTbar'])

        ofile = ROOT.TFile.Open(odir + '/Plots_1000pb_weighted.root', 'read')
        for plot in plots:
            hb = {}
            hs = {}
            hall = {}
            hd = None
            for process in bkgSamples:
                hb[process] = ofile.Get(plot.replace('h_', 'h_%s_' % process))
                hall[process] = ofile.Get(plot.replace('h_', 'h_%s_' % process))
            for process in sigSamples:
                hs[process] = ofile.Get(plot.replace('h_', 'h_%s_' % process))
                hall[process] = ofile.Get(plot.replace('h_', 'h_%s_' % process))
            if isData and muonCR:
                hd = ofile.Get(plot.replace('h_', 'h_muon_'))
            elif isData:
                hd = ofile.Get(plot.replace('h_', 'h_data_'))
            print plot
            makePlots(plot, hs, hb, hd, hall, legname, color, style, isData, odir, lumi, ofile, canvases)


##----##----##----##----##----##----##
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", default=35.9, type=float, help="luminosity", metavar="lumi")
    parser.add_option('-i', '--idir', dest='idir', default='data/', help='directory with data', metavar='idir')
    parser.add_option('-o', '--odir', dest='odir', default='plots/', help='directory to write plots', metavar='odir')
    parser.add_option('-s', '--isData', action='store_true', dest='isData', default=False, help='signal comparison',
                      metavar='isData')
    parser.add_option('-m', '--muonCR', action='store_true', dest='muonCR', default=False, help='for muon CR',
                      metavar='muonCR')
    parser.add_option('-c','--fillCA15', action='store_true', dest='fillCA15', default =False,help='for CA15', metavar='fillCA15')

    (options, args) = parser.parse_args()

    import tdrstyle

    tdrstyle.setTDRStyle()
    ROOT.gStyle.SetPadTopMargin(0.10)
    ROOT.gStyle.SetPadLeftMargin(0.16)
    ROOT.gStyle.SetPadRightMargin(0.10)
    # ROOT.gStyle.SetPalette(1)
    ROOT.gStyle.SetPaintTextFormat("1.1f")
    ROOT.gStyle.SetOptFit(0000)
    ROOT.gROOT.SetBatch()

    outputExists = False
    if glob.glob(options.odir + '/Plots_1000pb_weighted.root'):
        outputExists = True

    main(options, args, outputExists)
##----##----##----##----##----##----##
