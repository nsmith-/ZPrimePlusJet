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
from plotHelpers import *
from sampleContainer import *
DBTMIN=-99
#
def makePlots(plot,hs,hb,hd,hall,legname,color,style,isData,odir,lumi,ofile,canvases):
    if isData:
        c = makeCanvasComparisonStackWData(hd,hs,hb,legname,color,style,plot.replace('h_','stack_'),odir,lumi,ofile)
        canvases.append(c)	
    else:
        c = makeCanvasComparisonStack(hs,hb,legname,color,style,'ggHbb',plot.replace('h_','stack_'),odir,lumi,False,ofile)
        c1 = makeCanvasComparison(hall,legname,color,style,plot.replace('h_','signalcomparison_'),odir,lumi,ofile,True)
#        canvases.append(c)	
        canvases.append(c1)

def get2016files():
    #from  commit: ed54500
    idir     = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier'
    idirData = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.05/'
    
    tfiles = {
        'Hbb'   :    [idirData + '/GluGluHToBB_M125_13TeV_powheg_pythia8_CKKW_1000pb_weighted.root',
                      idir + '/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root',
                      idir + '/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                      idir + '/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                      idir + '/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root',
                      idir + '/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                      idir + '/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                      idir + '/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                      idir + '/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
        'ggHbb'  :  [idirData + '/GluGluHToBB_M125_13TeV_powheg_pythia8_CKKW_1000pb_weighted.root'],
        'VBFHbb' :  [idir + '/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root'],
        'VHbb':     [idir + '/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir + '/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir + '/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root',
                    idir + '/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir + '/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir + '/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
        'ttHbb'  : [idir + '/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],

        'Diboson': [idir + '/WWTo4Q_13TeV_powheg_1000pb_weighted.root',
                    idir + '/ZZ_13TeV_pythia8_1000pb_weighted.root',
                    idir + '/WZ_13TeV_pythia8_1000pb_weighted.root'],
        'DY':      [idir + '/DYJetsToQQ_HT180_13TeV_1000pb_weighted_v1204.root'],
        'DYll':    [idir + '/DYJetsToLL_M_50_13TeV_ext_1000pb_weighted.root'],
        'SingleTop': [
                    idir + '/ST_t_channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
                    idir + '/ST_t_channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
                    idir + '/ST_tW_antitop_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root',
                    idir + '/ST_tW_top_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root'],
        'W'      : [idir + '/WJetsToQQ_HT180_13TeV_1000pb_weighted_v1204.root'],
        'Wlnu'   : [idir + '/WJetsToLNu_HT_100To200_13TeV_1000pb_weighted.root',
                    idir + '/WJetsToLNu_HT_200To400_13TeV_1000pb_weighted.root',
                    idir + '/WJetsToLNu_HT_400To600_13TeV_1000pb_weighted.root',
                    idir + '/WJetsToLNu_HT_600To800_13TeV_1000pb_weighted.root',
                    idir + '/WJetsToLNu_HT_800To1200_13TeV_1000pb_weighted.root',
                    idir + '/WJetsToLNu_HT_1200To2500_13TeV_1000pb_weighted.root'],
        'TTbar'  : [idir + '/TT_powheg_1000pb_weighted_v1204.root'],  # Powheg is the new default
        'QCD': [    idir + '/QCD_HT100to200_13TeV_1000pb_weighted.root',
                    idir + '/QCD_HT200to300_13TeV_all_1000pb_weighted.root',
                    idir + '/QCD_HT300to500_13TeV_all_1000pb_weighted.root',
                    idir + '/QCD_HT500to700_13TeV_ext_1000pb_weighted.root',
                    idir + '/QCD_HT700to1000_13TeV_ext_1000pb_weighted.root',
                    idir + '/QCD_HT1000to1500_13TeV_all_1000pb_weighted.root',
                    idir + '/QCD_HT1500to2000_13TeV_all_1000pb_weighted.root',
                    idir + '/QCD_HT2000toInf_13TeV_1000pb_weighted.root'],
        'Phibb50': [idir + '/Spin0_ggPhi12j_g1_50_Scalar_13TeV_madgraph_1000pb_weighted.root'],
        'Phibb75': [idir + '/Spin0_ggPhi12j_g1_75_Scalar_13TeV_madgraph_1000pb_weighted.root'],
        'Phibb150': [idir + '/Spin0_ggPhi12j_g1_150_Scalar_13TeV_madgraph_1000pb_weighted.root'],
        'Phibb250': [idir + '/Spin0_ggPhi12j_g1_250_Scalar_13TeV_madgraph_1000pb_weighted.root'],
        'data_obs': [idirData+'JetHTRun2016B_03Feb2017_ver2_v2_v3.root',
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

        'muon':     [idir + '/SingleMuonRun2016B_03Feb2017_ver1_v1_fixtrig.root',
                     idir + '/SingleMuonRun2016B_03Feb2017_ver2_v2_fixtrig.root',
                     idir + '/SingleMuonRun2016C_03Feb2017_v1_fixtrig.root',
                     idir + '/SingleMuonRun2016D_03Feb2017_v1_fixtrig.root',
                     idir + '/SingleMuonRun2016E_03Feb2017_v1_fixtrig.root',
                     idir + '/SingleMuonRun2016F_03Feb2017_v1_fixtrig.root',
                     idir + '/SingleMuonRun2016G_03Feb2017_v1_fixtrig.root',
                     idir + '/SingleMuonRun2016H_03Feb2017_ver2_v1_fixtrig.root',
                     idir + '/SingleMuonRun2016H_03Feb2017_ver3_v1_fixtrig.root']
        }
    return tfiles


def get2017files():
    idir_temp = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier/'
    idir = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.07-puWeight/norm/'
    idir_1208 = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.08/norm'
    idirData = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.07/sklim/'

    tfiles = {'Hbb':        [idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8_all_1000pb_weighted.root',
			                idir+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root',
			                idir+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			                idir+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			                idir+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',  
			                idir+'/ttHTobb_M125_TuneCP5_13TeV_powheg_pythia8_1000pb_weighted.root',
			                idir+'/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_herwigpp_1000pb_weighted.root',
			                idir+'/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			                idir+'/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],	
	          'ggHbb' :     [idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
                            # idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root'],
              'VBFHbb':     [idir+'VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_1000pb_weighted.root'],
              'VHbb'  :     [idir+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
              	            idir+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                            idir+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
		                    idir+'/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_herwigpp_1000pb_weighted.root',
		                    idir+'/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
		                    idir+'/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
              'ttHbb':      [idir+'/ttHTobb_M125_TuneCP5_13TeV_powheg_pythia8_1000pb_weighted.root'],#ttHTobb_M125_TuneCUETP8M2_ttHtranche3_13TeV_powheg_pythia8_1000pb_weighted.root'],
              'Diboson':    [idir+'/WW_TuneCP5_13TeV_pythia8_1000pb_weighted.root',
                             idir+'/WZ_TuneCP5_13TeV_pythia8_1000pb_weighted.root',#ZZTo4Q_13TeV_amcatnloFXFX_madspin_pythia8_1000pb_weighted.root',
                             idir+'/ZZ_TuneCP5_13TeV_pythia8_1000pb_weighted.root'],
              #'DY':         [idir_temp+'/DYJetsToQQ_HT180_13TeV_1000pb_weighted_v1204.root'],
              'DY':         [idir+'/DYJetsToQQ_HT180_13TeV_1000pb_weighted_v1204.root'],
              'zqq400to600': [idir_1208 + '/ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV_1000pb_weighted.root'],
              'zqq600to800': [idir_1208 + '/ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV_1000pb_weighted.root'],
              'zqq800toInf': [idir_1208 + '/ZJetsToQQ_HT_800toInf_qc19_4j_TuneCP5_13TeV_1000pb_weighted.root'],
 
              'DYll':       [idir_temp+'/DYJetsToLL_M_50_13TeV_ext_1000pb_weighted.root'],
              'SingleTop':  [idir+'/ST_t_channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV_powhegV2_madspin_pythia8_1000pb_weighted.root',
                             idir+'/ST_t_channel_top_4f_inclusiveDecays_TuneCP5_13TeV_powhegV2_madspin_pythia8_1000pb_weighted.root',
                             idir+'/ST_s_channel_4f_leptonDecays_TuneCP5_13TeV_amcatnlo_pythia8_noPF_1000pb_weighted.root',
                             idir+'/ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV_powheg_pythia8_1000pb_weighted.root',
                             idir+'/ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV_powheg_pythia8_1000pb_weighted.root'],
              #'W':          [idir_temp+'/WJetsToQQ_HT180_13TeV_1000pb_weighted_v1204.root'],
              'wqq400to600': [idir_1208 + '/WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV_1000pb_weighted.root'],
              'wqq600to800': [idir_1208 + '/WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV_1000pb_weighted.root'],
              'wqq800toInf': [idir_1208 + '/WJetsToQQ_HT_800toInf_qc19_3j_TuneCP5_13TeV_1000pb_weighted.root'],
              'Wlnu':       [idir_temp+'WJetsToLNu_HT_100To200_13TeV_1000pb_weighted.root',
                             idir_temp+'/WJetsToLNu_HT_200To400_13TeV_1000pb_weighted.root',
                             idir_temp+'/WJetsToLNu_HT_400To600_13TeV_1000pb_weighted.root',
                             idir_temp+'/WJetsToLNu_HT_600To800_13TeV_1000pb_weighted.root',
                             idir_temp+'/WJetsToLNu_HT_800To1200_13TeV_1000pb_weighted.root',
                             idir_temp+'/WJetsToLNu_HT_1200To2500_13TeV_1000pb_weighted.root',
                             idir_temp+'/WJetsToLNu_HT_2500ToInf_13TeV_1000pb_weighted.root'],
              'TTbar':      [idir+'/TTToHadronic_TuneCP5_13TeV_powheg_pythia8_byLumi_1000pb_weighted.root',
                		     idir+'TTToSemiLeptonic_TuneCP5_13TeV_powheg_pythia8_byLumi_1000pb_weighted.root'], #Powheg is the new default
              'QCD':        [idir+'/QCD_HT100to200_TuneCP5_13TeV_madgraph_pythia8_1000pb_weighted.root',
                             idir+'/QCD_HT200to300_TuneCP5_13TeV_madgraph_pythia8_1000pb_weighted.root',
                             idir+'/QCD_HT300to500_TuneCP5_13TeV_madgraph_pythia8_noPF_byLumi_1000pb_weighted.root',
                             idir+'/QCD_HT500to700_TuneCP5_13TeV_madgraph_pythia8_noPF_byLumi_1000pb_weighted.root',
                             idir+'/QCD_HT700to1000_TuneCP5_13TeV_madgraph_pythia8_noPF_byLumi_1000pb_weighted.root',
                             idir+'/QCD_HT1000to1500_TuneCP5_13TeV_madgraph_pythia8_1000pb_weighted.root',
                             idir+'/QCD_HT1500to2000_TuneCP5_13TeV_madgraph_pythia8_1000pb_weighted.root',
                             idir+'/QCD_HT2000toInf_TuneCP5_13TeV_madgraph_pythia8_1000pb_weighted.root'],
              'Phibb50':    [idir+'/Spin0_ggPhi12j_g1_50_Scalar_13TeV_madgraph_1000pb_weighted.root'],
              'Phibb75':    [idir+'/Spin0_ggPhi12j_g1_75_Scalar_13TeV_madgraph_1000pb_weighted.root'],
              'Phibb150':   [idir+'/Spin0_ggPhi12j_g1_150_Scalar_13TeV_madgraph_1000pb_weighted.root'],
              'Phibb250':   [idir+'/Spin0_ggPhi12j_g1_250_Scalar_13TeV_madgraph_1000pb_weighted.root'],
              'data': [
#                     idirData + 'JetHTRun2017C_17Nov2017_v1_noPF_294927-299380.root',
#                     idirData + 'JetHTRun2017C_17Nov2017_v1_noPF_299381-300155.root',
#                     idirData + 'JetHTRun2017C_17Nov2017_v1_noPF_300156-300575.root',
#                     idirData + 'JetHTRun2017C_17Nov2017_v1_noPF_300576-301391.root',
#                     idirData + 'JetHTRun2017C_17Nov2017_v1_noPF_301392-302343.root',
#                     idirData + 'JetHTRun2017D_17Nov2017_v1_noPF_294927-302392.root',
#                     idirData + 'JetHTRun2017D_17Nov2017_v1_noPF_302393-302664.root',
#                     idirData + 'JetHTRun2017E_17Nov2017_v1_noPF_303825-304119.root',
#                     idirData + 'JetHTRun2017E_17Nov2017_v1_noPF_304120-304507.root',
#                     idirData + 'JetHTRun2017E_17Nov2017_v1_noPF_304508-305185.root',
#                     idirData + 'JetHTRun2017F_17Nov2017_v1_noPF_304508-305185.root',
#		     idirData + 'JetHTRun2017F_17Nov2017_v1_noPF_305186-305248.root',
#                     idirData + 'JetHTRun2017F_17Nov2017_v1_noPF_305249-305364.root',
#                     idirData + 'JetHTRun2017F_17Nov2017_v1_noPF_305365-305636.root',
#                     idirData + 'JetHTRun2017F_17Nov2017_v1_noPF_305637-306029.root',
#                     idirData + 'JetHTRun2017F_17Nov2017_v1_noPF_306030-306126.root'],
#                     idirData + 'JetHTRun2017B_PromptReco_v1_noPF.root',
        		     idirData + 'JetHTRun2017C_17Nov2017_v1_noPF.root',
                     idirData + 'JetHTRun2017D_17Nov2017_v1_noPF.root',
                     idirData + 'JetHTRun2017E_17Nov2017_v1_noPF.root',
                     idirData + 'JetHTRun2017F_17Nov2017_v1_noPF.root'],


              'muon': [
                       #idirData+'/SingleMuonRun2017B_17Nov2017_v1_noPF.root',
                       idirData+'/SingleMuonRun2017C_17Nov2017_v1_noPF.root',
                       idirData+'/SingleMuonRun2017D_17Nov2017_v1_noPF.root',
                       idirData+'/SingleMuonRun2017E_17Nov2017_v1_noPF.root',
                       idirData+'/SingleMuonRun2017F_17Nov2017_v1_noPF.root']
            }
    return tfiles

##############################################################################
def main(options,args,outputExists):
    #idir = "/eos/uscms/store/user/lpchbb/ggHsample_V11/sklim-v0-28Oct/"
    #odir = "plots_2016_10_31/"
#    idir = options.idir

    #TODO: update to new samples
    odir = options.odir
    lumi = options.lumi
    isData = options.isData
    muonCR = options.muonCR
    is2017 = options.is2017
    
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
               'Phibb75': '#Phi(b#bar{b}), 75 GeV',
               'Phibb150': '#Phi(b#bar{b}), 150 GeV',
               'Phibb250': '#Phi(b#bar{b}), 250 GeV'               
               }


    if isData and muonCR:
        legname['data'] = 'SingleMuon data'

    if is2017:
        tfiles = get2017files()
        puOpt  = "2017"
    else:
        tfiles = get2016files()
        puOpt  = "2016"       

    color = {'ggHbb': ROOT.kAzure+1,
             'Hbb': ROOT.kRed,
             'VHbb': ROOT.kTeal+1,
             'VBFHbb': ROOT.kBlue-10,
		     'Phibb50': ROOT.kBlue-1,
             'Phibb75': ROOT.kAzure+1,
		     'Phibb150': ROOT.kTeal+1,
		     'Phibb250': ROOT.kMagenta+1,
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
		     'Phibb50': 2,
             'Phibb75': 3,
		     'Phibb150': 4,
		     'Phibb250': 5,
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
        testSample = sampleContainer('test',[], 1, DBTMIN,lumi)
        for attr in dir(testSample):
            try:
                if 'h_' in attr and getattr(testSample,attr).InheritsFrom('TH1') and not getattr(testSample,attr).InheritsFrom('TH2'):
                    plots.append(attr)
            except:
                pass
    elif isData:
        plots = ['h_pt_ak8','h_msd_ak8','h_dbtag_ak8','h_n_ak4','h_n_ak4_dR0p8','h_t21_ak8','h_t32_ak8','h_n2b1sdddt_ak8','h_t21ddt_ak8','h_met','h_npv','h_eta_ak8','h_ht','h_dbtag_ak8_aftercut','h_n2b1sdddt_ak8_aftercut','h_rho_ak8','h_Cuts']
    else:
        plots = []
        testSample = sampleContainer('test',[], 1, DBTMIN,lumi)
        for attr in dir(testSample):
            try:
                if 'h_' in attr and getattr(testSample,attr).InheritsFrom('TH1') and not getattr(testSample,attr).InheritsFrom('TH2'):
                    plots.append(attr)
            except:
                pass
    if not outputExists: 
        samples = ['ggHbb','VBFHbb','VHbb','ttHbb','QCD','SingleTop','Diboson','TTbar']                      
        #samples = ['ggHbb','VBFHbb','VHbb','ttHbb','QCD','SingleTop','Diboson','W','DY','TTbar']                      
        for s in samples:
            for tfile in tfiles[s]:
                if not "root://" in tfile and not os.path.isfile(tfile):
                    print 'error: %s does not exist'%tfile                 
                    sys.exit()
        print "Signals... "
        sigSamples = {}
        sigSamples['ggHbb']  = sampleContainer('ggHbb',tfiles['ggHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt) 
        sigSamples['VBFHbb'] = sampleContainer('VBFHbb',tfiles['VBFHbb'], 1, DBTMIN,lumi ,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt) 
        sigSamples['VHbb'] = sampleContainer('VHbb',tfiles['VHbb'], 1, DBTMIN,lumi ,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt) 	
        sigSamples['ttHbb'] = sampleContainer('ttHbb',tfiles['ttHbb'], 1, DBTMIN,lumi ,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)    
        print "Backgrounds..."
        bkgSamples = {}    
        subwqqSamples={}
        subzqqSamples={}
        if not options.is2017:
            bkgSamples['W']  = sampleContainer('W',tfiles['W'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
            bkgSamples['DY']  = sampleContainer('DY',tfiles['DY'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
        else:
            pudir="root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.08-Pu/hadd/"
            subwqqSamples['wqq400to600'] = sampleContainer('wqq400to600', tfiles['wqq400to600'], 1, DBTMIN, lumi, False, False, '1', False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=pudir+"WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV.root")
            subwqqSamples['wqq600to800'] = sampleContainer('wqq600to800', tfiles['wqq600to800'], 1, DBTMIN, lumi, False, False, '1', False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=pudir+"WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV.root")
            subwqqSamples['wqq800toInf'] = sampleContainer('wqq800toInf', tfiles['wqq800toInf'], 1, DBTMIN, lumi, False, False, '1', False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=pudir+"WJetsToQQ_HT_800toInf_qc19_3j_TuneCP5_13TeV.root")
            subzqqSamples['zqq400to600'] = sampleContainer('zqq400to600', tfiles['zqq400to600'], 1, DBTMIN, lumi, False, False, '1', False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=pudir+"ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV.root")
            subzqqSamples['zqq600to800'] = sampleContainer('zqq600to800', tfiles['zqq600to800'], 1, DBTMIN, lumi, False, False, '1', False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=pudir+"ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV.root")
            subzqqSamples['zqq800toInf'] = sampleContainer('zqq800toInf', tfiles['zqq800toInf'], 1, DBTMIN, lumi, False, False, '1', False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=pudir+"ZJetsToQQ_HT_800toInf_qc19_4j_TuneCP5_13TeV.root")

            bkgSamples['wqq400to600'] = sampleContainer('wqq400to600', tfiles['wqq400to600'], 1, DBTMIN, lumi, False, False, '1', False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=pudir+"WJetsToQQ_HT400to600_qc19_3j_TuneCP5_13TeV.root")
            bkgSamples['wqq600to800'] = sampleContainer('wqq600to800', tfiles['wqq600to800'], 1, DBTMIN, lumi, False, False, '1', False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=pudir+"WJetsToQQ_HT600to800_qc19_3j_TuneCP5_13TeV.root")
            bkgSamples['wqq800toInf'] = sampleContainer('wqq800toInf', tfiles['wqq800toInf'], 1, DBTMIN, lumi, False, False, '1', False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=pudir+"WJetsToQQ_HT_800toInf_qc19_3j_TuneCP5_13TeV.root")
            bkgSamples['zqq400to600'] = sampleContainer('zqq400to600', tfiles['zqq400to600'], 1, DBTMIN, lumi, False, False, '1', False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=pudir+"ZJetsToQQ_HT400to600_qc19_4j_TuneCP5_13TeV.root")
            bkgSamples['zqq600to800'] = sampleContainer('zqq600to800', tfiles['zqq600to800'], 1, DBTMIN, lumi, False, False, '1', False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=pudir+"ZJetsToQQ_HT600to800_qc19_4j_TuneCP5_13TeV.root")
            bkgSamples['zqq800toInf'] = sampleContainer('zqq800toInf', tfiles['zqq800toInf'], 1, DBTMIN, lumi, False, False, '1', False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=pudir+"ZJetsToQQ_HT_800toInf_qc19_4j_TuneCP5_13TeV.root")


        bkgSamples['QCD'] = sampleContainer('QCD',tfiles['QCD'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
        if isData and muonCR:
            bkgSamples['Wlnu']  = sampleContainer('Wlnu',tfiles['Wlnu'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt='2016')
            bkgSamples['DYll']  = sampleContainer('DYll',tfiles['DYll'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt='2016')
            #bkgSamples['TTbar1Mu']  = sampleContainer('TTbar1Mu',tfiles['TTbar'], 1, DBTMIN,lumi, False, False, 'genMuFromW==1&&genEleFromW+genTauFromW==0',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
            #bkgSamples['TTbar1Ele']  = sampleContainer('TTbar1Ele',tfiles['TTbar'], 1, DBTMIN,lumi, False, False, 'genEleFromW==1&&genMuFromW+genTauFromW==0',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
            #bkgSamples['TTbar1Tau']  = sampleContainer('TTbar1Tau',tfiles['TTbar'], 1, DBTMIN,lumi, False, False, 'genTauFromW==1&&genEleFromW+genMuFromW==0',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
            #bkgSamples['TTbar0Lep']  = sampleContainer('TTbar0Lep',tfiles['TTbar'], 1, DBTMIN,lumi, False, False, 'genMuFromW+genEleFromW+genTauFromW==0',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
            #bkgSamples['TTbar2Lep']  = sampleContainer('TTbar2Lep',tfiles['TTbar'], 1, DBTMIN,lumi, False, False, 'genMuFromW+genEleFromW+genTauFromW==2',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
            bkgSamples['TTbar']  = sampleContainer('TTbar',tfiles['TTbar'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
        else:        
            bkgSamples['TTbar']  = sampleContainer('TTbar',tfiles['TTbar'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
        bkgSamples['SingleTop'] = sampleContainer('SingleTop',tfiles['SingleTop'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
        bkgSamples['Diboson'] = sampleContainer('Diboson',tfiles['Diboson'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
        #bkgSamples['Hbb'] = sampleContainer('Hbb',tfiles['Hbb'], 1, lumi ) 	

        if isData:
            print "Data..."
        if isData and muonCR:
            dataSample = sampleContainer('muon',tfiles['muon'], 1, DBTMIN,lumi, isData, False, '((triggerBits&4)&&passJson)',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
        elif isData:
            # For production  zprimebits-v12.07
            #HLT_AK8PFJet330_PFAK8BTagCSV_p17_v =32768
            #HLT_PFHT1050_v                     =134217728
            #HLT_AK8PFJet400_TrimMass30_v       =4096
            #HLT_AK8PFHT800_TrimMass50_v        =8192
            #HLT_PFJet500_v                     =16384
            #HLT_AK8PFJet360_TrimMass30_v       =16
            #HLT_AK8PFJet380_TrimMass30_v       =16777216
            #HLT_AK8PFJet500_v                  =2097152
            triggerNames={"version":"zprimebit-12.07-triggerBits","branchName":"triggerBits",
                          "names":[
                               "HLT_AK8PFJet330_PFAK8BTagCSV_p17_v*",
                               "HLT_PFHT1050_v*",
                               "HLT_AK8PFJet400_TrimMass30_v*",
                               "HLT_AK8PFHT800_TrimMass50_v*",
                               "HLT_PFJet500_v*",
                               "HLT_AK8PFJet360_TrimMass30_v*",
                               "HLT_AK8PFJet380_TrimMass30_v*",
                               "HLT_AK8PFJet500_v*"]
                      }
            #selectTriggerBitsAndJson = "((triggerBits&32768 || triggerBits&134217728 || triggerBits&4096 || triggerBits&8192 || triggerBits&16384 || triggerBits&16 || triggerBits&16777216 || triggerBits&2097152)&&passJson)"
            dataSample = sampleContainer('data',tfiles['data'], 1, DBTMIN,lumi, isData, False, "passJson", False, iSplit = options.iSplit, maxSplit = options.maxSplit, triggerNames=triggerNames)
        
        ofile = ROOT.TFile.Open(odir+'/Plots_1000pb_weighted_%s.root '%options.iSplit,'recreate')

        if options.is2017:
            wqqplots={}
            wqq_sc = subwqqSamples[subwqqSamples.keys()[0]]  # first subsample
            for plot in plots:
                wqqplots[plot] = getattr(wqq_sc,plot).Clone()
                wqqplots[plot].SetName(plot.replace("h_","h_W_"))
                for subS_key in subwqqSamples.keys()[1:]:
                    subS = subwqqSamples[subS_key]
                    wqqplots[plot].Add(getattr(subS,plot))
            zqqplots={}
            zqq_sc = subzqqSamples[subzqqSamples.keys()[0]]  # first subsample
            for plot in plots:
                zqqplots[plot] = getattr(zqq_sc,plot).Clone()
                zqqplots[plot].SetName(plot.replace("h_","h_DY_"))
                for subS_key in subzqqSamples.keys()[1:]:
                    subS = subzqqSamples[subS_key]
                    zqqplots[plot].Add(getattr(subS,plot))

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

        if options.is2017:
            hall_byproc['DY']= zqqplots  
            hall_byproc['W'] = wqqplots   
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
                print proc, plot
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
            #makePlots(plot,hs,hb,hd,hall,legname,color,style,isData,odir,lumi,ofile,canvases)
    
        ofile.Close()
    else:        
        sigSamples = ['ggHbb','VBFHbb','VHbb','ttHbb']        
        bkgSamples = ['QCD','SingleTop','Diboson','W','DY']                      
        if isData and muonCR:
#            bkgSamples.extend(['Wlnu','DYll','TTbar1Mu','TTbar1Ele','TTbar1Tau','TTbar0Lep','TTbar2Lep'])
            bkgSamples.extend(['Wlnu','DYll','TTbar'])
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
    parser.add_option('--is2017', action='store_true', dest='is2017', default =False,help='for using 2017 files', metavar='is2017')
    parser.add_option("--max-split", dest="maxSplit", default=1, type="int", help="max number of jobs", metavar="maxSplit")
    parser.add_option("--i-split"  , dest="iSplit", default=0, type="int", help="job number", metavar="iSplit")
    parser.add_option("--puOpt"  , dest="puOpt", default="2017", help="select pu weight source", metavar="puOpt")

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




