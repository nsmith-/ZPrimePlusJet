import os
import math
from array import array
from optparse import OptionParser
import ROOT
import sys
sys.path.append(os.path.expandvars("$CMSSW_BASE/src/DAZSLE/ZPrimePlusJet/analysis"))

from sampleContainerPhibb import *

def getFiles(muonCR=False):
    #idir_old = "root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.03/cvernier/"
    idir = "root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/norm2/cvernier/"
    idir_muon = "root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier/"
    idir_data = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.05/'
    tfiles = {
        'hqq125': [idir_data+'/GluGluHToBB_M125_13TeV_powheg_pythia8_CKKW_1000pb_weighted.root'],
        'vbfhqq125': [idir+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root'],
        'zhqq125': [idir+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir+'/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir+'/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir+'/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root'],
        'whqq125': [idir + '/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir + '/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
        'tthqq125': [idir + '/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
############### Signals
        'DMSbb50': [idir_data + '/Spin0_ggPhibb1j_g1_50_Scalar_1000pb_weighted.root'],
        'DMSbb100': [idir_data + '/Spin0_ggPhibb1j_g1_100_Scalar_1000pb_weighted.root'],
        'DMSbb125': [idir_data + '/Spin0_ggPhibb1j_g1_125_Scalar_1000pb_weighted.root'],
        'DMSbb200': [idir_data + '/Spin0_ggPhibb1j_g1_200_Scalar_1000pb_weighted.root'],
        'DMSbb300': [idir_data + '/Spin0_ggPhibb1j_g1_300_Scalar_1000pb_weighted.root'],
        'DMSbb350': [idir_data + '/Spin0_ggPhibb1j_g1_350_Scalar_1000pb_weighted.root'],
        'DMSbb400': [idir_data + '/Spin0_ggPhibb1j_g1_400_Scalar_1000pb_weighted.root'],
        'DMSbb500': [idir_data + '/Spin0_ggPhibb1j_g1_500_Scalar_1000pb_weighted.root'],

############### Backgrounds
        'qcd': [
                idir_data+'/QCD_HT100to200_13TeV_1000pb_weighted.root',
                idir_data+'/QCD_HT200to300_13TeV_1000pb_weighted.root',
                idir_data+'/QCD_HT300to500_13TeV_all_1000pb_weighted.root',
                idir_data+'/QCD_HT500to700_13TeV_1000pb_weighted.root',
                idir_data+'/QCD_HT700to1000_13TeV_1000pb_weighted.root',
                idir_data+'/QCD_HT1000to1500_13TeV_1000pb_weighted.root',
                idir_data+'/QCD_HT1500to2000_13TeV_all_1000pb_weighted.root',
                idir_data+'/QCD_HT2000toInf_13TeV_all_1000pb_weighted.root'],
        'wqq': [idir_data+'/WJetsToQQ_HT180_13TeV_1000pb_weighted.root'],
        'tqq': [idir+'/TT_powheg_1000pb_weighted.root'],
        'zqq': [idir_data+'/DYJetsToQQ_HT180_13TeV_1000pb_weighted.root'],
        'stqq': [idir+'/ST_t_channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
                 idir+'/ST_t_channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
                 idir+'/ST_tW_antitop_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root',
                 idir+'/ST_tW_top_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root'],
        'vvqq': [idir+'/WWTo4Q_13TeV_powheg_1000pb_weighted.root',
                 idir+'/ZZ_13TeV_pythia8_1000pb_weighted.root',#ZZTo4Q_13TeV_amcatnloFXFX_madspin_pythia8_1000pb_weighted.root',
                 idir+'/WZ_13TeV_pythia8_1000pb_weighted.root'],
################
        'zll': [idir + '/DYJetsToLL_M_50_13TeV_ext_1000pb_weighted.root'],
        'wlnu': [idir + 'WJetsToLNu_HT_100To200_13TeV_1000pb_weighted.root',
                 idir + '/WJetsToLNu_HT_200To400_13TeV_1000pb_weighted.root',
                 idir + '/WJetsToLNu_HT_400To600_13TeV_1000pb_weighted.root',
                 idir + '/WJetsToLNu_HT_600To800_13TeV_1000pb_weighted.root',
                 idir + '/WJetsToLNu_HT_800To1200_13TeV_1000pb_weighted.root',
                 idir + '/WJetsToLNu_HT_1200To2500_13TeV_1000pb_weighted.root'],
################
        'data_obs': [idir_data+'JetHTRun2016B_03Feb2017_ver2_v2_v3.root',
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
                     idir_data + 'JetHTRun2016H_03Feb2017_ver3_v1_v3.root']
    }

    if muonCR:
        tfiles['data_obs'] = [idir_muon + '/SingleMuonRun2016B_03Feb2017_ver1_v1_fixtrig.root',
                              idir_muon + '/SingleMuonRun2016B_03Feb2017_ver2_v2_fixtrig.root',
                              idir_muon + '/SingleMuonRun2016C_03Feb2017_v1_fixtrig.root',
                              idir_muon + '/SingleMuonRun2016D_03Feb2017_v1_fixtrig.root',
                              idir_muon + '/SingleMuonRun2016E_03Feb2017_v1_fixtrig.root',
                              idir_muon + '/SingleMuonRun2016F_03Feb2017_v1_fixtrig.root',
                              idir_muon + '/SingleMuonRun2016G_03Feb2017_v1_fixtrig.root',
                              idir_muon + '/SingleMuonRun2016H_03Feb2017_ver2_v1_fixtrig.root',
                              idir_muon + '/SingleMuonRun2016H_03Feb2017_ver3_v1_fixtrig.root']

    return tfiles

##----##----##----##----##----##----##
def main(options, args):

    #idir = options.idir   
    odir = options.odir
    lumi = options.lumi
    muonCR = options.muonCR
    dbtagmin = options.dbtagmin
    fillCA15 = options.fillCA15

    if not fillCA15: jet_type = "AK8"
    else: jet_type = "CA15" 
    fileName = 'hist_1DZbb_pt_scalesmear_' +jet_type + '_check.root'
    if options.bb:
        fileName = 'hist_1DZbb_sortByBB_' + jet_type + '_check.root'
    elif muonCR:
        fileName = 'hist_1DZbb_muonCR_' + jet_type + '_check.root'

    outfile = ROOT.TFile.Open(options.odir + "/" + fileName, "recreate")

    tfiles = getFiles(muonCR)

    
    all_plots = []
    testSample = sampleContainerPhibb('test',[], 1, dbtagmin,lumi)
    for attr in dir(testSample):
        try:
            if 'h_' in attr and getattr(testSample,attr).InheritsFrom('TH1') or getattr(testSample,attr).InheritsFrom('TH2'):
                all_plots.append(attr)
        except:
            pass

        
    dbcuts = [0.7,0.75,0.8,0.85,0.9,0.95]
    plots = []
    for dbcut in dbcuts:
        plots.extend([
             'h_msd_v_pt_topR6_N2_%s_pass'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_topR6_N2_%s_fail'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_topR6_N2_%s_pass_matched'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_topR6_N2_%s_fail_matched'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_topR6_N2_%s_pass_unmatched'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_topR6_N2_%s_fail_unmatched'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_topR6_N2_%s_pass_JESUp'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_topR6_N2_%s_fail_JESUp'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_topR6_N2_%s_pass_JESDown'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_topR6_N2_%s_fail_JESDown'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_topR6_N2_%s_pass_JERUp'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_topR6_N2_%s_fail_JERUp'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_topR6_N2_%s_pass_JERDown'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_topR6_N2_%s_fail_JERDown'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_topR6_N2_%s_pass_triggerUp'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_topR6_N2_%s_fail_triggerUp'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_topR6_N2_%s_pass_triggerDown'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_topR6_N2_%s_fail_triggerDown'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_topR6_N2_%s_pass_PuUp'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_topR6_N2_%s_fail_PuUp'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_topR6_N2_%s_pass_PuDown'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_topR6_N2_%s_fail_PuDown'%str(dbcut).replace('0.','p')
             ])

    if options.bb:
        plots = ['h_msd_v_pt_bbleading_topR6_pass', 'h_msd_v_pt_bbleading_topR6_fail']
    elif muonCR:
        for dbcut in dbcuts:
            plots.extend([
                 'h_msd_muCR4_N2_%s_pass'%str(dbcut).replace('0.','p'), 'h_msd_muCR4_N2_%s_fail'%str(dbcut).replace('0.','p'),
                 'h_msd_muCR4_N2_%s_pass_JESUp'%str(dbcut).replace('0.','p'), 'h_msd_muCR4_N2_%s_pass_JESDown'%str(dbcut).replace('0.','p'),
                 'h_msd_muCR4_N2_%s_fail_JESUp'%str(dbcut).replace('0.','p'), 'h_msd_muCR4_N2_%s_fail_JESDown'%str(dbcut).replace('0.','p'),
                 'h_msd_muCR4_N2_%s_pass_JERUp'%str(dbcut).replace('0.','p'), 'h_msd_muCR4_N2_%s_pass_JERDown'%str(dbcut).replace('0.','p'),
                 'h_msd_muCR4_N2_%s_fail_JERUp'%str(dbcut).replace('0.','p'), 'h_msd_muCR4_N2_%s_fail_JERDown'%str(dbcut).replace('0.','p'),
                 'h_msd_muCR4_N2_%s_pass_mutriggerUp'%str(dbcut).replace('0.','p'), 'h_msd_muCR4_N2_%s_pass_mutriggerDown'%str(dbcut).replace('0.','p'),
                 'h_msd_muCR4_N2_%s_fail_mutriggerUp'%str(dbcut).replace('0.','p'), 'h_msd_muCR4_N2_%s_fail_mutriggerDown'%str(dbcut).replace('0.','p'),
                 'h_msd_muCR4_N2_%s_pass_muidUp'%str(dbcut).replace('0.','p'), 'h_msd_muCR4_N2_%s_pass_muidDown'%str(dbcut).replace('0.','p'),
                 'h_msd_muCR4_N2_%s_fail_muidUp'%str(dbcut).replace('0.','p'), 'h_msd_muCR4_N2_%s_fail_muidDown'%str(dbcut).replace('0.','p'),
                 'h_msd_muCR4_N2_%s_pass_muisoUp'%str(dbcut).replace('0.','p'), 'h_msd_muCR4_N2_%s_pass_muisoDown'%str(dbcut).replace('0.','p'),
                 'h_msd_muCR4_N2_%s_fail_muisoUp'%str(dbcut).replace('0.','p'), 'h_msd_muCR4_N2_%s_fail_muisoDown'%str(dbcut).replace('0.','p'),
                 'h_msd_muCR4_N2_%s_pass_PuUp'%str(dbcut).replace('0.','p'), 'h_msd_muCR4_N2_%s_pass_PuDown'%str(dbcut).replace('0.','p'),
                 'h_msd_muCR4_N2_%s_fail_PuUp'%str(dbcut).replace('0.','p'), 'h_msd_muCR4_N2_%s_fail_PuDown'%str(dbcut).replace('0.','p'),
                 ])
    for plot in plots:
        if plot not in all_plots:
            print "%s does not exist in sample container: are you sure about the name?!"% plot
            sys.exit()
    print "all plots exist"
    

    print "Signals... "
    sigSamples = {}
    sigSamples['DMSbb50'] = sampleContainerPhibb('DMSbb50',tfiles['DMSbb50'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    sigSamples['DMSbb100'] = sampleContainerPhibb('DMSbb100',tfiles['DMSbb100'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    sigSamples['DMSbb125'] = sampleContainerPhibb('DMSbb125',tfiles['DMSbb125'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    sigSamples['DMSbb200'] = sampleContainerPhibb('DMSbb200',tfiles['DMSbb200'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    sigSamples['DMSbb300'] = sampleContainerPhibb('DMSbb300',tfiles['DMSbb300'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    sigSamples['DMSbb350'] = sampleContainerPhibb('DMSbb350',tfiles['DMSbb350'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    sigSamples['DMSbb400'] = sampleContainerPhibb('DMSbb400',tfiles['DMSbb400'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    sigSamples['DMSbb500'] = sampleContainerPhibb('DMSbb500',tfiles['DMSbb500'], 1, dbtagmin, lumi, False, fillCA15, '1', False)

    print "Backgrounds..."
    bkgSamples = {}
    bkgSamples['wqq'] = sampleContainerPhibb('wqq', tfiles['wqq'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    bkgSamples['zqq'] = sampleContainerPhibb('zqq', tfiles['zqq'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    if not options.skipQCD:
        bkgSamples['qcd'] = sampleContainerPhibb('qcd', tfiles['qcd'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    bkgSamples['tqq'] = sampleContainerPhibb('tqq', tfiles['tqq'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    bkgSamples['stqq'] = sampleContainerPhibb('stqq', tfiles['stqq'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    bkgSamples['wlnu'] = sampleContainerPhibb('wlnu', tfiles['wlnu'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    bkgSamples['zll'] = sampleContainerPhibb('zll', tfiles['zll'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    bkgSamples['vvqq'] = sampleContainerPhibb('vvqq', tfiles['vvqq'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    bkgSamples['hqq125'] = sampleContainerPhibb('hqq125', tfiles['hqq125'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    bkgSamples['tthqq125'] = sampleContainerPhibb('tthqq125', tfiles['tthqq125'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    bkgSamples['vbfhqq125'] = sampleContainerPhibb('vbfhqq125', tfiles['vbfhqq125'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    bkgSamples['whqq125'] = sampleContainerPhibb('whqq125', tfiles['whqq125'], 1, dbtagmin, lumi, False, fillCA15, '1', False)
    bkgSamples['zhqq125'] = sampleContainerPhibb('zhqq125', tfiles['zhqq125'], 1, dbtagmin, lumi, False, fillCA15, '1', False)


    print "Data..."
    if not options.skipData:
        if muonCR:
            dataSample = sampleContainerPhibb('data_obs', tfiles['data_obs'], 1, dbtagmin, lumi, True, fillCA15, '((triggerBits&4)&&passJson)', False)
        else:
            dataSample = sampleContainerPhibb('data_obs', tfiles['data_obs'], 1, dbtagmin, lumi, True, fillCA15, '((triggerBits&2)&&passJson)', False)

    hall = {}

    for plot in plots:
        tag = plot.split('_')[-2] + '_' + plot.split('_')[-1]   # 'pass' or 'fail' or systematicName
        tag2 = plot.split('_')[-1]   # 'pass' or 'fail' or systematicName
        if (plot.split('_')[-1] != 'pass' and plot.split('_')[-1] != 'fail'):
            tag = plot.split('_')[-3] + '_' + plot.split('_')[-2] + '_' + plot.split('_')[-1]  # 'pass_systematicName', 'pass_systmaticName', etc.
        #print tag
        if tag2 not in ['pass', 'fail']:
            tag2 = plot.split('_')[-2] + '_' + plot.split('_')[-1]  # 'pass_systematicName', 'pass_systmaticName', etc.

        for process, s in sigSamples.iteritems():
            hall['%s_%s' % (process, tag)] = getattr(s, plot)
            hall['%s_%s' % (process, tag)].SetName('%s_%s' % (process, tag))
            print process + '_' + tag
        for process, s in bkgSamples.iteritems():
            hall['%s_%s' % (process, tag)] = getattr(s, plot)
            hall['%s_%s' % (process, tag)].SetName('%s_%s' % (process, tag))
            print process + '_' + tag
        if not options.skipData:
            hall['%s_%s' % ('data_obs', tag)] = getattr(dataSample, plot)
            hall['%s_%s' % ('data_obs', tag)].SetName('%s_%s' % ('data_obs', tag))
            print 'data_obs' + '_' + tag
    outfile.cd()

    for key, h in hall.iteritems():
       print h.GetName() , "\n"
       h.Write()

    outfile.Write()
    outfile.Close()


##----##----##----##----##----##----##
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", default=35.9, type="float", help="luminosity", metavar="lumi")
    parser.add_option("--bb", action='store_true', dest="bb", default=False, help="sort by double b-tag")
    parser.add_option('-i', '--idir', dest='idir', default='data/', help='directory with data', metavar='idir')
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write histograms', metavar='odir')
    parser.add_option('-m', '--muonCR', action='store_true', dest='muonCR', default=False, help='for muon CR',
                      metavar='muonCR')
    parser.add_option('-d', '--dbtagmin', dest='dbtagmin', default=-99., type="float",
                      help='left bound to btag selection', metavar='dbtagmin')
    parser.add_option('--skip-qcd', action='store_true', dest='skipQCD', default=False, help='skip QCD', metavar='skipQCD')
    parser.add_option('--skip-data', action='store_true', dest='skipData', default=False, help='skip Data', metavar='skipData')
    parser.add_option('-c','--fillCA15', action='store_true', dest='fillCA15', default =False,help='for CA15', metavar='fillCA15')
 

    (options, args) = parser.parse_args()

    main(options, args)

    print "All done."
