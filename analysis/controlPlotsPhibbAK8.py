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
from plotHelpersPhibb import *
from sampleContainerPhibbAK8 import *
DBTMIN=-99
#
def makePlots(plot,hs,hb,hd,hall,legname,color,style,isData,odir,lumi,ofile,canvases):
    if isData:
        c = makeCanvasComparisonStackWData(hd,hs,hb,legname,color,style,plot.replace('h_','stack_'),odir,lumi,ofile)
        canvases.append(c)	
    else:
        c = makeCanvasComparisonStack(hs,hb,legname,color,style,'Phibb50',plot.replace('h_','stack_'),odir,lumi,True,ofile)
        #c = makeCanvasComparisonStack(hs,hb,legname,color,style,'Phibb50',plot.replace('h_','stack_'),odir,lumi,False,ofile)
        c1 = makeCanvasComparison(hall,legname,color,style,plot.replace('h_','signalcomparison_'),odir,lumi,ofile,False)
#        canvases.append(c)	
        canvases.append(c1)
##############################################################################
def main(options,args,outputExists):
    idir_old = "root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.03/cvernier"
    idir = "root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/norm2/cvernier/"
    idir_data = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.05/'
    #idir = options.idir   
    odir = options.odir
    lumi = options.lumi
    isData = options.isData
    muonCR = options.muonCR

    
    legname = {'ggHbb': 'ggH(b#bar{b})',
               'Hbb': 'H(b#bar{b})',
               'VBFHbb':'VBF H(b#bar{b})',
               'VHbb': 'VH(b#bar{b})',
	       'ttHbb': 't#bar{t}H(b#bar{b})',
               'Diboson': 'VV(4q)',
               'SingleTop': 'single-t',
               'DY': 'Z(qq)+jets',
               'W': 'W(qq)+jets',
               'DYll': 'Z(ll)+jets',
               'Wlnu': 'W(l#nu)+jets',
               'TTbar': 't#bar{t}+jets',        
               'TTbar1Mu': 't#bar{t}+jets, 1#mu',  
               'TTbar1Ele': 't#bar{t}+jets, 1e',        
               'TTbar1Tau': 't#bar{t}+jets, 1#tau',        
               'TTbar0Lep': 't#bar{t}+jets, 0l',        
               'TTbar2Lep': 't#bar{t}+jets, 2l',        
               'QCD': 'QCD',
	       'data': 'JetHT data',
               'muon': 'SingleMuon data',
               'Phibb50': '#Phi(b#bar{b}), 50 GeV',
               'Phibb100': '#Phi(b#bar{b}), 100 GeV',
               'Phibb125': '#Phi(b#bar{b}), 125 GeV',
               'Phibb200': '#Phi(b#bar{b}), 200 GeV',
               'Phibb300': '#Phi(b#bar{b}), 300 GeV',               
               'Phibb350': '#Phi(b#bar{b}), 350 GeV',               
               'Phibb400': '#Phi(b#bar{b}), 400 GeV',
               'Phibb500': '#Phi(b#bar{b}), 500 GeV',
               }

    if isData and muonCR:
        legname['data'] = 'SingleMuon data'
    print "IDIR old : ", idir_old
    print "IDIR now : ", idir
    print "IDIR new : ", idir_data
    tfiles = {'Hbb':   [idir_old + '/GluGluHToBB_M125_13TeV_powheg_pythia8_all_1000pb_weighted.root',
			idir_old + '/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root',
			idir_old + '/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			idir_old + '/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			idir_old + '/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',  
			idir_old + '/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			idir_old + '/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			idir_old + '/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			idir_old + '/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root'],	
              'ggHbb': [idir_old + '/GluGluHToBB_M125_13TeV_powheg_pythia8_all_1000pb_weighted.root'],
              'VBFHbb': [idir_old + '/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root'],
              'VHbb': [idir_old + '/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir_old + '/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir_old + '/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir_old + '/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir_old + '/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir_old + '/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root'],
              'ttHbb':  [idir_old + '/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],#ttHTobb_M125_TuneCUETP8M2_ttHtranche3_13TeV_powheg_pythia8_1000pb_weighted.root'],
############### Signals
              'Phibb50': [idir_data + '/Spin0_ggPhibb1j_g1_50_Scalar_1000pb_weighted.root'],
              'Phibb100': [idir_data + '/Spin0_ggPhibb1j_g1_100_Scalar_1000pb_weighted.root'],
              'Phibb125': [idir_data + '/Spin0_ggPhibb1j_g1_125_Scalar_1000pb_weighted.root'],
              'Phibb200': [idir_data + '/Spin0_ggPhibb1j_g1_200_Scalar_1000pb_weighted.root'],
              'Phibb300': [idir_data + '/Spin0_ggPhibb1j_g1_300_Scalar_1000pb_weighted.root'],
              'Phibb350': [idir_data + '/Spin0_ggPhibb1j_g1_350_Scalar_1000pb_weighted.root'],
              'Phibb400': [idir_data + '/Spin0_ggPhibb1j_g1_400_Scalar_1000pb_weighted.root'],
              'Phibb500': [idir_data + '/Spin0_ggPhibb1j_g1_500_Scalar_1000pb_weighted.root'],
############### Backgrounds
              'QCD': [idir_data + '/QCD_HT100to200_13TeV_1000pb_weighted.root',
                      idir_data + '/QCD_HT200to300_13TeV_1000pb_weighted.root',
                      idir_data + '/QCD_HT300to500_13TeV_all_1000pb_weighted.root',
                      idir_data + '/QCD_HT500to700_13TeV_1000pb_weighted.root',
                      idir_data + '/QCD_HT700to1000_13TeV_1000pb_weighted.root',
                      idir_data + '/QCD_HT1000to1500_13TeV_1000pb_weighted.root',
                      idir_data + '/QCD_HT1500to2000_13TeV_all_1000pb_weighted.root',
                      idir_data + '/QCD_HT2000toInf_13TeV_all_1000pb_weighted.root'],
              'W':  [idir_data + '/WJetsToQQ_HT180_13TeV_1000pb_weighted.root'],
              'TTbar':  [idir + '/TT_powheg_1000pb_weighted.root'], #Powheg is the new default
              'DY': [idir_data + '/DYJetsToQQ_HT180_13TeV_1000pb_weighted.root'],
              'SingleTop':  [idir + '/ST_t_channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
                             idir + '/ST_t_channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
                             idir + '/ST_tW_antitop_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root',
                             idir + '/ST_tW_top_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root'],
              'Diboson': [idir + '/WWTo4Q_13TeV_powheg_1000pb_weighted.root',
                          idir + '/ZZ_13TeV_pythia8_1000pb_weighted.root',#ZZTo4Q_13TeV_amcatnloFXFX_madspin_pythia8_1000pb_weighted.root',
                          idir + '/WZ_13TeV_pythia8_1000pb_weighted.root'],
################
              'DYll': [idir + '/DYJetsToLL_M_50_13TeV_ext_1000pb_weighted.root'],
              'Wlnu': [idir + '/WJetsToLNu_HT_100To200_13TeV_1000pb_weighted.root',
                     idir + '/WJetsToLNu_HT_200To400_13TeV_1000pb_weighted.root',
                     idir + '/WJetsToLNu_HT_400To600_13TeV_1000pb_weighted.root',
                     idir + '/WJetsToLNu_HT_600To800_13TeV_1000pb_weighted.root',
                     idir + '/WJetsToLNu_HT_800To1200_13TeV_1000pb_weighted.root',
                    idir + '/WJetsToLNu_HT_1200To2500_13TeV_1000pb_weighted.root',
                    idir + '/WJetsToLNu_HT_2500ToInf_13TeV_1000pb_weighted.root'],
################
              'data': [
		     idir_data + 'JetHTRun2016B_03Feb2017_ver2_v2_v3.root',
		     idir_data + 'JetHTRun2016B_03Feb2017_ver1_v1_v3.root',
                     idir_data + 'JetHTRun2016C_03Feb2017_v1_v3_0.root',
                     idir_data + 'JetHTRun2016C_03Feb2017_v1_v3_1.root',
                     idir_data + 'JetHTRun2016C_03Feb2017_v1_v3_2.root',
                     idir_data + 'JetHTRun2016C_03Feb2017_v1_v3_3.root',
                     idir_data + 'JetHTRun2016C_03Feb2017_v1_v3_4.root',
                     idir_data + 'JetHTRun2016C_03Feb2017_v1_v3_5.root',
                     idir_data + 'JetHTRun2016C_03Feb2017_v1_v3_6.root',
                     idir_data + 'JetHTRun2016C_03Feb2017_v1_v3_7.root',
                     idir_data + 'JetHTRun2016C_03Feb2017_v1_v3_8.root',
                     idir_data + 'JetHTRun2016C_03Feb2017_v1_v3_9.root',
                     idir_data + 'JetHTRun2016D_03Feb2017_v1_v3_0.root',
		     idir_data + 'JetHTRun2016D_03Feb2017_v1_v3_1.root',
                     idir_data + 'JetHTRun2016D_03Feb2017_v1_v3_10.root',
                     idir_data + 'JetHTRun2016D_03Feb2017_v1_v3_11.root',
                     idir_data + 'JetHTRun2016D_03Feb2017_v1_v3_12.root',
                     idir_data + 'JetHTRun2016D_03Feb2017_v1_v3_13.root',
                     idir_data + 'JetHTRun2016D_03Feb2017_v1_v3_14.root',
                     idir_data + 'JetHTRun2016D_03Feb2017_v1_v3_2.root',
                     idir_data + 'JetHTRun2016D_03Feb2017_v1_v3_3.root',
                     idir_data + 'JetHTRun2016D_03Feb2017_v1_v3_4.root',
                     idir_data + 'JetHTRun2016D_03Feb2017_v1_v3_5.root',
                     idir_data + 'JetHTRun2016D_03Feb2017_v1_v3_6.root',
                     idir_data + 'JetHTRun2016D_03Feb2017_v1_v3_7.root',
                     idir_data + 'JetHTRun2016D_03Feb2017_v1_v3_8.root',
                     idir_data + 'JetHTRun2016D_03Feb2017_v1_v3_9.root',
                     idir_data + 'JetHTRun2016E_03Feb2017_v1_v3_0.root',
                     idir_data + 'JetHTRun2016E_03Feb2017_v1_v3_1.root',
                     idir_data + 'JetHTRun2016E_03Feb2017_v1_v3_2.root',
                     idir_data + 'JetHTRun2016E_03Feb2017_v1_v3_3.root',
                     idir_data + 'JetHTRun2016E_03Feb2017_v1_v3_4.root',
                     idir_data + 'JetHTRun2016E_03Feb2017_v1_v3_5.root',
                     idir_data + 'JetHTRun2016E_03Feb2017_v1_v3_6.root',
                     idir_data + 'JetHTRun2016E_03Feb2017_v1_v3_7.root',
                     idir_data + 'JetHTRun2016E_03Feb2017_v1_v3_8.root',
                     idir_data + 'JetHTRun2016E_03Feb2017_v1_v3_9.root',
                     idir_data + 'JetHTRun2016E_03Feb2017_v1_v3_10.root',
                     idir_data + 'JetHTRun2016E_03Feb2017_v1_v3_11.root',
                     idir_data + 'JetHTRun2016E_03Feb2017_v1_v3_12.root',
                     idir_data + 'JetHTRun2016E_03Feb2017_v1_v3_13.root',
                     idir_data + 'JetHTRun2016E_03Feb2017_v1_v3_14.root',
                     idir_data + 'JetHTRun2016F_03Feb2017_v1_v3_0.root',
                     idir_data + 'JetHTRun2016F_03Feb2017_v1_v3_1.root',
                     idir_data + 'JetHTRun2016F_03Feb2017_v1_v3_2.root',
                     idir_data + 'JetHTRun2016F_03Feb2017_v1_v3_3.root',
                     idir_data + 'JetHTRun2016F_03Feb2017_v1_v3_4.root',
                     idir_data + 'JetHTRun2016F_03Feb2017_v1_v3_5.root',
                     idir_data + 'JetHTRun2016F_03Feb2017_v1_v3_6.root',
                     idir_data + 'JetHTRun2016F_03Feb2017_v1_v3_7.root',
                     idir_data + 'JetHTRun2016F_03Feb2017_v1_v3_8.root',
                     idir_data + 'JetHTRun2016F_03Feb2017_v1_v3_9.root',
                     idir_data + 'JetHTRun2016F_03Feb2017_v1_v3_10.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_0.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_1.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_2.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_3.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_4.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_5.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_6.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_7.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_8.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_9.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_10.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_11.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_12.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_13.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_14.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_15.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_16.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_17.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_18.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_19.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_20.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_21.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_22.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_23.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_24.root',
                     idir_data + 'JetHTRun2016G_03Feb2017_v1_v3_25.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_0.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_1.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_2.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_3.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_4.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_5.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_6.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_7.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_8.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_9.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_10.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_11.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_12.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_13.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_14.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_15.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_16.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_17.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_18.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_19.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_20.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_21.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_22.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_23.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_24.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver2_v1_v3_25.root',
                     idir_data + 'JetHTRun2016H_03Feb2017_ver3_v1_v3.root'],
              'muon': [idir + '/SingleMuonRun2016B_03Feb2017_ver1_v1_fixtrig.root',
                       idir + '/SingleMuonRun2016B_03Feb2017_ver2_v2_fixtrig.root',
                       idir + '/SingleMuonRun2016C_03Feb2017_v1_fixtrig.root',
                       idir + '/SingleMuonRun2016D_03Feb2017_v1_fixtrig.root',
                       idir + '/SingleMuonRun2016E_03Feb2017_v1_fixtrig.root',
                       idir + '/SingleMuonRun2016F_03Feb2017_v1_fixtrig.root',
                       idir + '/SingleMuonRun2016G_03Feb2017_v1_fixtrig.root',
                       idir + '/SingleMuonRun2016H_03Feb2017_ver2_v1_fixtrig.root',
                       idir + '/SingleMuonRun2016H_03Feb2017_ver3_v1_fixtrig.root']
            }

    color = {'ggHbb': ROOT.kAzure+1,
             'Hbb': ROOT.kRed,
             'VHbb': ROOT.kTeal+1,
             'VBFHbb': ROOT.kBlue-10,
             'Phibb50': ROOT.kAzure+1,
             'Phibb100': ROOT.kRed-2,
	     #'Phibb125': ROOT.kRed,
	     'Phibb125': ROOT.kOrange-9,
             'Phibb200': ROOT.kBlue-1,
             'Phibb300': ROOT.kMagenta+1,
             'Phibb350': ROOT.kBlue,
             'Phibb400': ROOT.kBlue-10,
             'Phibb500': ROOT.kSpring,
	     'ttHbb': ROOT.kBlue-1,
             'Diboson': ROOT.kOrange,
             'SingleTop': ROOT.kRed-2,
             'DY':  ROOT.kRed,
             'DYll':  ROOT.kRed-3,
             'W':  ROOT.kGreen+3,
             'Wlnu':  ROOT.kGreen+2,
             'TTbar':  ROOT.kGray,
             'TTbar1Mu':  ROOT.kViolet,
             'TTbar1Ele':  ROOT.kSpring,
             'TTbar1Tau':  ROOT.kOrange+2,
             'TTbar0Lep':  ROOT.kGray,
             'TTbar2Lep':  ROOT.kMagenta-9,
             'QCD': ROOT.kBlue+2,
	     'data':ROOT.kBlack,
	     'muon':ROOT.kBlack
            }

    style = {'Hbb': 1,
             'ggHbb': 2,             
             'Phibb50': 3,
	     'Phibb100': 4,
	     'Phibb125': 4,
	     'Phibb200': 9,
	     'Phibb300': 5,
	     'Phibb350': 2,
	     'Phibb400': 2,
	     'Phibb500': 2,
             'VBFHbb': 3,
	     'VHbb': 4,
	     'ttHbb': 5,
             'Diboson': 1,
             'SingleTop': 1,
             'DY': 1,
             'DYll': 1,
             'W': 1,
             'Wlnu': 1,
             'TTbar': 1,
             'TTbar1Mu': 1,
             'TTbar1Ele': 1,
             'TTbar1Tau': 1,
             'TTbar0Lep': 1,
             'TTbar2Lep': 1,
             'QCD': 1,
             'data': 1,
	     'muon':1
            }
        


    canvases = []
    if isData and muonCR:
        plots = []
        testSample = sampleContainerPhibbAK8('test',[], 1, DBTMIN,lumi)
        for attr in dir(testSample):
            try:
                if 'h_' in attr and getattr(testSample,attr).InheritsFrom('TH1') and not getattr(testSample,attr).InheritsFrom('TH2'):
                    plots.append(attr)
            except:
                pass
    elif isData:
        plots = ['h_pt_ak8','h_msd_ak8','h_dbtag_ak8','h_n_ak4','h_n_ak4_dR0p8','h_t21_ak8','h_t32_ak8','h_n2b1sdddt_ak8','h_t21ddt_ak8','h_met','h_npv','h_eta_ak8','h_ht','h_dbtag_ak8_aftercut','h_n2b1sdddt_ak8_aftercut','h_rho_ak8', 'h_rho_ak8_nocut', 'h_msd_ak8_nocut','h_Cuts']
    else:
        plots = []
        testSample = sampleContainerPhibbAK8('test',[], 1, DBTMIN,lumi)
        for attr in dir(testSample):
            try:
                if 'h_' in attr and getattr(testSample,attr).InheritsFrom('TH1') and not getattr(testSample,attr).InheritsFrom('TH2'):
                    plots.append(attr)
            except:
                pass
            
    if not outputExists: 
        samples = ['Phibb50','Phibb100','Phibb125','Phibb200','Phibb300','Phibb350','Phibb400','Phibb500','QCD','SingleTop','Diboson','W','DY','TTbar']
#        for s in samples:
#            for tfile in tfiles[s]:
#                if not os.path.isfile(tfile):
#                    print 'error: %s does not exist'%tfile                 
#                    sys.exit()
        print "Signals... "
        sigSamples = {}
#No        sigSamples['ggHbb']  = sampleContainerPhibbAK8('ggHbb',tfiles['ggHbb']  , 1, DBTMIN,lumi) 
#No        sigSamples['VBFHbb'] = sampleContainerPhibbAK8('VBFHbb',tfiles['VBFHbb'], 1, DBTMIN,lumi ) 
#No        sigSamples['VHbb'] = sampleContainerPhibbAK8('VHbb',tfiles['VHbb'], 1, DBTMIN,lumi )        
#No        sigSamples['ttHbb'] = sampleContainerPhibbAK8('ttHbb',tfiles['ttHbb'], 1, DBTMIN,lumi )    
        sigSamples['Phibb50'] = sampleContainerPhibbAK8('Phibb50',tfiles['Phibb50'], 1, DBTMIN, lumi) 
        sigSamples['Phibb100'] = sampleContainerPhibbAK8('Phibb100',tfiles['Phibb100'], 1, DBTMIN, lumi)      
        sigSamples['Phibb125'] = sampleContainerPhibbAK8('Phibb125',tfiles['Phibb125'], 1, DBTMIN, lumi)      
        sigSamples['Phibb200'] = sampleContainerPhibbAK8('Phibb200',tfiles['Phibb200'], 1, DBTMIN, lumi)      
        sigSamples['Phibb300'] = sampleContainerPhibbAK8('Phibb300',tfiles['Phibb300'], 1, DBTMIN, lumi)      
        sigSamples['Phibb350'] = sampleContainerPhibbAK8('Phibb350',tfiles['Phibb350'], 1, DBTMIN, lumi)      
        sigSamples['Phibb400'] = sampleContainerPhibbAK8('Phibb400',tfiles['Phibb400'], 1, DBTMIN, lumi)   
        sigSamples['Phibb500'] = sampleContainerPhibbAK8('Phibb500',tfiles['Phibb500'], 1, DBTMIN, lumi)   
        print "Backgrounds..."
        bkgSamples = {}
        bkgSamples['W']  = sampleContainerPhibbAK8('W',tfiles['W'], 1, DBTMIN,lumi)
        bkgSamples['DY']  = sampleContainerPhibbAK8('DY',tfiles['DY'], 1, DBTMIN,lumi)
        bkgSamples['QCD'] = sampleContainerPhibbAK8('QCD',tfiles['QCD'], 1, DBTMIN,lumi)
        if isData and muonCR:
            bkgSamples['Wlnu']  = sampleContainerPhibbAK8('Wlnu',tfiles['Wlnu'], 1, DBTMIN,lumi)
###No            bkgSamples['DYll']  = sampleContainerPhibbAK8('DYll',tfiles['DYll'], 1, DBTMIN,lumi)
###No            bkgSamples['TTbar1Mu']  = sampleContainerPhibbAK8('TTbar1Mu',tfiles['TTbar'], 1, DBTMIN,lumi, False, False, 'genMuFromW==1&&genEleFromW+genTauFromW==0')
###No            bkgSamples['TTbar1Ele']  = sampleContainerPhibbAK8('TTbar1Ele',tfiles['TTbar'], 1, DBTMIN,lumi, False, False, 'genEleFromW==1&&genMuFromW+genTauFromW==0')
###No            bkgSamples['TTbar1Tau']  = sampleContainerPhibbAK8('TTbar1Tau',tfiles['TTbar'], 1, DBTMIN,lumi, False, False, 'genTauFromW==1&&genEleFromW+genMuFromW==0')
###No            bkgSamples['TTbar0Lep']  = sampleContainerPhibbAK8('TTbar0Lep',tfiles['TTbar'], 1, DBTMIN,lumi, False, False, 'genMuFromW+genEleFromW+genTauFromW==0')
###No            bkgSamples['TTbar2Lep']  = sampleContainerPhibbAK8('TTbar2Lep',tfiles['TTbar'], 1, DBTMIN,lumi, False, False, 'genMuFromW+genEleFromW+genTauFromW==2')
##        else:        
            bkgSamples['TTbar']  = sampleContainerPhibbAK8('TTbar',tfiles['TTbar'], 1, DBTMIN,lumi)
        bkgSamples['SingleTop'] = sampleContainerPhibbAK8('SingleTop',tfiles['SingleTop'], 1, DBTMIN,lumi)
        bkgSamples['Diboson'] = sampleContainerPhibbAK8('Diboson',tfiles['Diboson'], 1, DBTMIN,lumi)
#No        bkgSamples['Hbb'] = sampleContainerPhibbAK8('Hbb',tfiles['Hbb'], 1, lumi )  

        if isData:
            print "Data..."
        if isData and muonCR:
            dataSample = sampleContainerPhibbAK8('muon',tfiles['muon'], 1, DBTMIN,lumi, isData, False, '((triggerBits&4)&&passJson)')
        elif isData:
            dataSample = sampleContainerPhibbAK8('data',tfiles['data'], 1, DBTMIN,lumi, isData, False, '((triggerBits&2)&&passJson)')
        
        ofile = ROOT.TFile.Open(odir+'/Plots_1000pb_weighted.root ','recreate')

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
                hall_byproc[process][plot] = getattr(s,plot)
            for process, s in bkgSamples.iteritems():
                hall_byproc[process][plot] = getattr(s,plot)
            if isData:
                if muonCR:      
                    hall_byproc['muon'][plot] = getattr(dataSample,plot)
                else:
                    hall_byproc['data'][plot] = getattr(dataSample,plot)
            
        ofile.cd()
        for proc, hDict in hall_byproc.iteritems():
            for plot, h in hDict.iteritems():
                h.Write()
        
        for plot in plots:
            hs = {}
            hb = {}
            hall={}
            hd = None
            for process, s in sigSamples.iteritems():
                hs[process] = getattr(s,plot)
                hall[process] = getattr(s,plot)
            for process, s in bkgSamples.iteritems():
                hb[process] = getattr(s,plot)
                hall[process] = getattr(s,plot)
            if isData:
                hd = getattr(dataSample,plot)
            makePlots(plot,hs,hb,hd,hall,legname,color,style,isData,odir,lumi,ofile,canvases)
    
        ofile.Close()
    else:        
        sigSamples = ['Phibb50','Phibb100','Phibb125','Phibb200','Phibb300','Phibb350','Phibb400','Phibb500']        
        bkgSamples = ['QCD','SingleTop','Diboson','W','DY']                      
        if isData and muonCR:
            bkgSamples.extend(['Wlnu','DYll','TTbar1Mu','TTbar1Ele','TTbar1Tau','TTbar0Lep','TTbar2Lep'])
        else:        
            bkgSamples.extend(['TTbar'])
            
        ofile = ROOT.TFile.Open(odir+'/Plots_1000pb_weighted.root','read')
        for plot in plots:
            hb = {}
            hs = {}
            hall = {}
            hd = None
            for process in bkgSamples:
                hb[process] = ofile.Get(plot.replace('h_','h_%s_'%process))
                hall[process] = ofile.Get(plot.replace('h_','h_%s_'%process))
            for process in sigSamples:
                hs[process] = ofile.Get(plot.replace('h_','h_%s_'%process))
                hall[process] = ofile.Get(plot.replace('h_','h_%s_'%process))
            if isData and muonCR:
                hd = ofile.Get(plot.replace('h_','h_muon_'))
            elif isData:
                hd = ofile.Get(plot.replace('h_','h_data_'))
            print plot
            makePlots(plot,hs,hb,hd,hall,legname,color,style,isData,odir,lumi,ofile,canvases)
        


##----##----##----##----##----##----##
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", default = 35.9,type=float,help="luminosity", metavar="lumi")
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
    parser.add_option('-s','--isData', action='store_true', dest='isData', default =False,help='signal comparison', metavar='isData')
    parser.add_option('-m','--muonCR', action='store_true', dest='muonCR', default =False,help='for muon CR', metavar='muonCR')

    (options, args) = parser.parse_args()

     
    import tdrstyle
    tdrstyle.setTDRStyle()
    ROOT.gStyle.SetPadTopMargin(0.10)
    ROOT.gStyle.SetPadLeftMargin(0.16)
    ROOT.gStyle.SetPadRightMargin(0.10)
    #ROOT.gStyle.SetPalette(1)
    ROOT.gStyle.SetPaintTextFormat("1.1f")
    ROOT.gStyle.SetOptFit(0000)
    ROOT.gROOT.SetBatch()

    
    outputExists = False
    if glob.glob(options.odir+'/Plots_1000pb_weighted.root'):
        outputExists = True
        
    main(options,args,outputExists)
##----##----##----##----##----##----##




