import os
import math
from array import array
from optparse import OptionParser
import ROOT
import sys
sys.path.append(os.path.expandvars("$CMSSW_BASE/src/DAZSLE/ZPrimePlusJet/analysis"))

from sampleContainerPhibbCa15 import *


##----##----##----##----##----##----##
def main(options, args):
    idir_old = "/eos/uscms/store/user/lpchbb/zprimebits-v12.03/cvernier"
    idir = "/eos/uscms/store/user/lpchbb/zprimebits-v12.04/norm2/cvernier/"
    idir_data = '/eos/uscms/store/user/lpchbb/zprimebits-v12.05/'
    #idir = options.idir   
    odir = options.odir
    lumi = options.lumi
    muonCR = options.muonCR
    dbtagmin = options.dbtagmin

    #fileName = 'hist_1DZbb_pt_scalesmear_CA15.root'
    fileName = 'hist_1DZbb_pt_scalesmear_CA15_newsamples.root'
    if options.bb:
        fileName = 'hist_1DZbb_sortByBB.root'
    elif muonCR:
        fileName = 'hist_1DZbb_muonCR.root'

    outfile = ROOT.TFile(options.odir + "/" + fileName, "recreate")

    tfiles = {
        'hqq125': [idir_old+'/GluGluHToBB_M125_13TeV_powheg_pythia8_all_1000pb_weighted.root'],
        'vbfhqq125': [idir_old+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root'],
        'zhqq125': [idir_old+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir_old+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir_old+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir_old+'/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir_old+'/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir_old+'/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root'],
        'whqq125': [idir_old + '/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir_old + '/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
        'tthqq125': [idir_old + '/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
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
        'zll': [idir_old + '/DYJetsToLL_M_50_13TeV_ext_1000pb_weighted.root'],
        'wlnu': [idir_old + 'WJetsToLNu_HT_100To200_13TeV_1000pb_weighted.root',
                 idir_old + '/WJetsToLNu_HT_200To400_13TeV_1000pb_weighted.root',
                 idir_old + '/WJetsToLNu_HT_400To600_13TeV_1000pb_weighted.root',
                 idir_old + '/WJetsToLNu_HT_600To800_13TeV_1000pb_weighted.root',
                 idir_old + '/WJetsToLNu_HT_800To1200_13TeV_1000pb_weighted.root',
                 idir_old + '/WJetsToLNu_HT_1200To2500_13TeV_1000pb_weighted.root'],
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
        tfiles['data_obs'] = [idir_old + '/SingleMuonRun2016B_03Feb2017_ver1_v1_fixtrig.root',
                              idir_old + '/SingleMuonRun2016B_03Feb2017_ver2_v2_fixtrig.root',
                              idir_old + '/SingleMuonRun2016C_03Feb2017_v1_fixtrig.root',
                              idir_old + '/SingleMuonRun2016D_03Feb2017_v1_fixtrig.root',
                              idir_old + '/SingleMuonRun2016E_03Feb2017_v1_fixtrig.root',
                              idir_old + '/SingleMuonRun2016F_03Feb2017_v1_fixtrig.root',
                              idir_old + '/SingleMuonRun2016G_03Feb2017_v1_fixtrig.root',
                              idir_old + '/SingleMuonRun2016H_03Feb2017_ver2_v1_fixtrig.root',
                              idir_old + '/SingleMuonRun2016H_03Feb2017_ver3_v1_fixtrig.root']

    print "Signals... "
    sigSamples = {}
#No    sigSamples['hqq125'] = sampleContainerPhibbCa15('hqq125', tfiles['hqq125'], 1, dbtagmin, lumi, False, False, '1', False)
#No    sigSamples['tthqq125'] = sampleContainerPhibbCa15('tthqq125', tfiles['tthqq125'], 1, dbtagmin, lumi, False, False, '1', False)
#No    sigSamples['vbfhqq125'] = sampleContainerPhibbCa15('vbfhqq125', tfiles['vbfhqq125'], 1, dbtagmin, lumi, False, False, '1', False)
#No    sigSamples['whqq125'] = sampleContainerPhibbCa15('whqq125', tfiles['whqq125'], 1, dbtagmin, lumi, False, False, '1', False)
#No    sigSamples['zhqq125'] = sampleContainerPhibbCa15('zhqq125', tfiles['zhqq125'], 1, dbtagmin, lumi, False, False, '1', False)
    sigSamples['DMSbb50'] = sampleContainerPhibbCa15('DMSbb50',tfiles['DMSbb50'], 1, dbtagmin, lumi, False, False, '1', False)
    sigSamples['DMSbb100'] = sampleContainerPhibbCa15('DMSbb100',tfiles['DMSbb100'], 1, dbtagmin, lumi, False, False, '1', False)
    sigSamples['DMSbb125'] = sampleContainerPhibbCa15('DMSbb125',tfiles['DMSbb125'], 1, dbtagmin, lumi, False, False, '1', False)
    sigSamples['DMSbb200'] = sampleContainerPhibbCa15('DMSbb200',tfiles['DMSbb200'], 1, dbtagmin, lumi, False, False, '1', False)
    sigSamples['DMSbb300'] = sampleContainerPhibbCa15('DMSbb300',tfiles['DMSbb300'], 1, dbtagmin, lumi, False, False, '1', False)
    sigSamples['DMSbb350'] = sampleContainerPhibbCa15('DMSbb350',tfiles['DMSbb350'], 1, dbtagmin, lumi, False, False, '1', False)
    sigSamples['DMSbb400'] = sampleContainerPhibbCa15('DMSbb400',tfiles['DMSbb400'], 1, dbtagmin, lumi, False, False, '1', False)
    sigSamples['DMSbb500'] = sampleContainerPhibbCa15('DMSbb500',tfiles['DMSbb500'], 1, dbtagmin, lumi, False, False, '1', False)

    print "Backgrounds..."
    bkgSamples = {}
    bkgSamples['wqq'] = sampleContainerPhibbCa15('wqq', tfiles['wqq'], 1, dbtagmin, lumi, False, False, '1', False)
    bkgSamples['zqq'] = sampleContainerPhibbCa15('zqq', tfiles['zqq'], 1, dbtagmin, lumi, False, False, '1', False)
    if not options.skipQCD:
        bkgSamples['qcd'] = sampleContainerPhibbCa15('qcd', tfiles['qcd'], 1, dbtagmin, lumi, False, False, '1', False)
    bkgSamples['tqq'] = sampleContainerPhibbCa15('tqq', tfiles['tqq'], 1, dbtagmin, lumi, False, False, '1', False)
    bkgSamples['stqq'] = sampleContainerPhibbCa15('stqq', tfiles['stqq'], 1, dbtagmin, lumi, False, False, '1', False)
#No    bkgSamples['wlnu'] = sampleContainerPhibbCa15('wlnu', tfiles['wlnu'], 1, dbtagmin, lumi, False, False, '1', False)
#No    bkgSamples['zll'] = sampleContainerPhibbCa15('zll', tfiles['zll'], 1, dbtagmin, lumi, False, False, '1', False)
    bkgSamples['vvqq'] = sampleContainerPhibbCa15('vvqq', tfiles['vvqq'], 1, dbtagmin, lumi, False, False, '1', False)
    print "Data..."
    if not options.skipData:
        if muonCR:
            dataSample = sampleContainerPhibbCa15('data_obs', tfiles['data_obs'], 1, dbtagmin, lumi, True, False,
                                     '((triggerBits&4)&&passJson)', True)
        else:
            dataSample = sampleContainerPhibbCa15('data_obs', tfiles['data_obs'], 1, dbtagmin, lumi, True, False,
                                     '((triggerBits&2)&&passJson)', False)

    hall = {}


    plots = [
             'h_msd_v_pt_ca15_topR6_p7_pass', 'h_msd_v_pt_ca15_topR6_p7_fail',
             'h_msd_v_pt_ca15_topR6_p7_pass_matched', 'h_msd_v_pt_ca15_topR6_p7_fail_matched',
             'h_msd_v_pt_ca15_topR6_p7_pass_unmatched', 'h_msd_v_pt_ca15_topR6_p7_fail_unmatched',
             'h_msd_v_pt_ca15_topR6_p7_pass_JESUp', 'h_msd_v_pt_ca15_topR6_p7_fail_JESUp',
             'h_msd_v_pt_ca15_topR6_p7_pass_JESDown', 'h_msd_v_pt_ca15_topR6_p7_fail_JESDown',
             'h_msd_v_pt_ca15_topR6_p7_pass_JERUp', 'h_msd_v_pt_ca15_topR6_p7_fail_JERUp',
             'h_msd_v_pt_ca15_topR6_p7_pass_JERDown', 'h_msd_v_pt_ca15_topR6_p7_fail_JERDown',
             'h_msd_v_pt_ca15_topR6_p7_pass_triggerUp', 'h_msd_v_pt_ca15_topR6_p7_fail_triggerUp',
             'h_msd_v_pt_ca15_topR6_p7_pass_triggerDown', 'h_msd_v_pt_ca15_topR6_p7_fail_triggerDown',
             'h_msd_v_pt_ca15_topR6_p7_pass_PuUp', 'h_msd_v_pt_ca15_topR6_p7_fail_PuUp',
             'h_msd_v_pt_ca15_topR6_p7_pass_PuDown', 'h_msd_v_pt_ca15_topR6_p7_fail_PuDown',
             'h_msd_v_pt_ca15_topR6_p75_pass', 'h_msd_v_pt_ca15_topR6_p75_fail',
             'h_msd_v_pt_ca15_topR6_p75_pass_matched', 'h_msd_v_pt_ca15_topR6_p75_pass_unmatched',
             'h_msd_v_pt_ca15_topR6_p75_fail_matched', 'h_msd_v_pt_ca15_topR6_p75_fail_unmatched',
             'h_msd_v_pt_ca15_topR6_p75_pass_JESUp', 'h_msd_v_pt_ca15_topR6_p75_fail_JESUp',
             'h_msd_v_pt_ca15_topR6_p75_pass_JESDown', 'h_msd_v_pt_ca15_topR6_p75_fail_JESDown',
             'h_msd_v_pt_ca15_topR6_p75_pass_JERUp', 'h_msd_v_pt_ca15_topR6_p75_fail_JERUp',
             'h_msd_v_pt_ca15_topR6_p75_pass_JERDown', 'h_msd_v_pt_ca15_topR6_p75_fail_JERDown',
             'h_msd_v_pt_ca15_topR6_p75_pass_triggerUp', 'h_msd_v_pt_ca15_topR6_p75_fail_triggerUp',
             'h_msd_v_pt_ca15_topR6_p75_pass_triggerDown', 'h_msd_v_pt_ca15_topR6_p75_fail_triggerDown',
             'h_msd_v_pt_ca15_topR6_p75_pass_PuUp', 'h_msd_v_pt_ca15_topR6_p75_fail_PuUp',
             'h_msd_v_pt_ca15_topR6_p75_pass_PuDown', 'h_msd_v_pt_ca15_topR6_p75_fail_PuDown',
             'h_msd_v_pt_ca15_topR6_p8_pass', 'h_msd_v_pt_ca15_topR6_p8_fail',
             'h_msd_v_pt_ca15_topR6_p8_pass_matched', 'h_msd_v_pt_ca15_topR6_p8_pass_unmatched',
             'h_msd_v_pt_ca15_topR6_p8_fail_matched', 'h_msd_v_pt_ca15_topR6_p8_fail_unmatched',
             'h_msd_v_pt_ca15_topR6_p8_pass_JESUp', 'h_msd_v_pt_ca15_topR6_p8_fail_JESUp',
             'h_msd_v_pt_ca15_topR6_p8_pass_JESDown', 'h_msd_v_pt_ca15_topR6_p8_fail_JESDown',
             'h_msd_v_pt_ca15_topR6_p8_pass_JERUp', 'h_msd_v_pt_ca15_topR6_p8_fail_JERUp',
             'h_msd_v_pt_ca15_topR6_p8_pass_JERDown', 'h_msd_v_pt_ca15_topR6_p8_fail_JERDown',
             'h_msd_v_pt_ca15_topR6_p8_pass_triggerUp', 'h_msd_v_pt_ca15_topR6_p8_fail_triggerUp',
             'h_msd_v_pt_ca15_topR6_p8_pass_triggerDown', 'h_msd_v_pt_ca15_topR6_p8_fail_triggerDown',
             'h_msd_v_pt_ca15_topR6_p8_pass_PuUp', 'h_msd_v_pt_ca15_topR6_p8_fail_PuUp',
             'h_msd_v_pt_ca15_topR6_p8_pass_PuDown', 'h_msd_v_pt_ca15_topR6_p8_fail_PuDown',
             'h_msd_v_pt_ca15_topR6_p85_pass', 'h_msd_v_pt_ca15_topR6_p85_fail',
             'h_msd_v_pt_ca15_topR6_p85_pass_matched', 'h_msd_v_pt_ca15_topR6_p85_pass_unmatched',
             'h_msd_v_pt_ca15_topR6_p85_fail_matched', 'h_msd_v_pt_ca15_topR6_p85_fail_unmatched',
             'h_msd_v_pt_ca15_topR6_p85_pass_JESUp', 'h_msd_v_pt_ca15_topR6_p85_fail_JESUp',
             'h_msd_v_pt_ca15_topR6_p85_pass_JESDown', 'h_msd_v_pt_ca15_topR6_p85_fail_JESDown',
             'h_msd_v_pt_ca15_topR6_p85_pass_JERUp', 'h_msd_v_pt_ca15_topR6_p85_fail_JERUp',
             'h_msd_v_pt_ca15_topR6_p85_pass_JERDown', 'h_msd_v_pt_ca15_topR6_p85_fail_JERDown',
             'h_msd_v_pt_ca15_topR6_p85_pass_triggerUp', 'h_msd_v_pt_ca15_topR6_p85_fail_triggerUp',
             'h_msd_v_pt_ca15_topR6_p85_pass_triggerDown', 'h_msd_v_pt_ca15_topR6_p85_fail_triggerDown',
             'h_msd_v_pt_ca15_topR6_p85_pass_PuUp', 'h_msd_v_pt_ca15_topR6_p85_fail_PuUp',
             'h_msd_v_pt_ca15_topR6_p85_pass_PuDown', 'h_msd_v_pt_ca15_topR6_p85_fail_PuDown',
             'h_msd_v_pt_ca15_topR6_p9_pass', 'h_msd_v_pt_ca15_topR6_p9_fail',
             'h_msd_v_pt_ca15_topR6_p9_pass_matched', 'h_msd_v_pt_ca15_topR6_p9_pass_unmatched',
             'h_msd_v_pt_ca15_topR6_p9_fail_matched', 'h_msd_v_pt_ca15_topR6_p9_fail_unmatched',
             'h_msd_v_pt_ca15_topR6_p9_pass_JESUp', 'h_msd_v_pt_ca15_topR6_p9_fail_JESUp',
             'h_msd_v_pt_ca15_topR6_p9_pass_JESDown', 'h_msd_v_pt_ca15_topR6_p9_fail_JESDown',
             'h_msd_v_pt_ca15_topR6_p9_pass_JERUp', 'h_msd_v_pt_ca15_topR6_p9_fail_JERUp',
             'h_msd_v_pt_ca15_topR6_p9_pass_JERDown', 'h_msd_v_pt_ca15_topR6_p9_fail_JERDown',
             'h_msd_v_pt_ca15_topR6_p9_pass_triggerUp', 'h_msd_v_pt_ca15_topR6_p9_fail_triggerUp',
             'h_msd_v_pt_ca15_topR6_p9_pass_triggerDown', 'h_msd_v_pt_ca15_topR6_p9_fail_triggerDown',
             'h_msd_v_pt_ca15_topR6_p9_pass_PuUp', 'h_msd_v_pt_ca15_topR6_p9_fail_PuUp',
             'h_msd_v_pt_ca15_topR6_p9_pass_PuDown', 'h_msd_v_pt_ca15_topR6_p9_fail_PuDown',
             'h_msd_v_pt_ca15_topR6_p95_pass', 'h_msd_v_pt_ca15_topR6_p95_fail',
             'h_msd_v_pt_ca15_topR6_p95_pass_matched', 'h_msd_v_pt_ca15_topR6_p95_pass_unmatched',
             'h_msd_v_pt_ca15_topR6_p95_fail_matched', 'h_msd_v_pt_ca15_topR6_p95_fail_unmatched',
             'h_msd_v_pt_ca15_topR6_p95_pass_JESUp', 'h_msd_v_pt_ca15_topR6_p95_fail_JESUp',
             'h_msd_v_pt_ca15_topR6_p95_pass_JESDown', 'h_msd_v_pt_ca15_topR6_p95_fail_JESDown',
             'h_msd_v_pt_ca15_topR6_p95_pass_JERUp', 'h_msd_v_pt_ca15_topR6_p95_fail_JERUp',
             'h_msd_v_pt_ca15_topR6_p95_pass_JERDown', 'h_msd_v_pt_ca15_topR6_p95_fail_JERDown',
             'h_msd_v_pt_ca15_topR6_p95_pass_triggerUp', 'h_msd_v_pt_ca15_topR6_p95_fail_triggerUp',
             'h_msd_v_pt_ca15_topR6_p95_pass_triggerDown', 'h_msd_v_pt_ca15_topR6_p95_fail_triggerDown',
             'h_msd_v_pt_ca15_topR6_p95_pass_PuUp', 'h_msd_v_pt_ca15_topR6_p95_fail_PuUp',
             'h_msd_v_pt_ca15_topR6_p95_pass_PuDown', 'h_msd_v_pt_ca15_topR6_p95_fail_PuDown',
             ]


#    plots = ['h_msd_v_pt_ca15_topR6_N2_pass', 'h_msd_v_pt_ca15_topR6_N2_fail',
#             # SR with N2DDT @ 26% && db > 0.9, msd corrected
#             'h_msd_v_pt_ca15_topR6_N2_pass_matched', 'h_msd_v_pt_ca15_topR6_N2_pass_unmatched',
#             # matched and unmatached for mass up/down
#             'h_msd_v_pt_ca15_topR6_N2_fail_matched', 'h_msd_v_pt_ca15_topR6_N2_fail_unmatched',
#             # matched and unmatached for mass up/down
#             'h_msd_v_pt_ca15_topR6_N2_pass_JESUp', 'h_msd_v_pt_ca15_topR6_N2_pass_JESDown',  # JES up/down
#             'h_msd_v_pt_ca15_topR6_N2_fail_JESUp', 'h_msd_v_pt_ca15_topR6_N2_fail_JESDown',  # JES up/down
#             'h_msd_v_pt_ca15_topR6_N2_pass_JERUp', 'h_msd_v_pt_ca15_topR6_N2_pass_JERDown',  # JER up/down
#             'h_msd_v_pt_ca15_topR6_N2_fail_JERUp', 'h_msd_v_pt_ca15_topR6_N2_fail_JERDown',  # JER up/down
#             'h_msd_v_pt_ca15_topR6_N2_pass_triggerUp', 'h_msd_v_pt_ca15_topR6_N2_pass_triggerDown',  # trigger up/down
#             'h_msd_v_pt_ca15_topR6_N2_fail_triggerUp', 'h_msd_v_pt_ca15_topR6_N2_fail_triggerDown',  # trigger up/down
#             'h_msd_v_pt_ca15_topR6_N2_pass_PuUp', 'h_msd_v_pt_ca15_topR6_N2_pass_PuDown',  # Pu up/downxf
#             'h_msd_v_pt_ca15_topR6_N2_fail_PuUp', 'h_msd_v_pt_ca15_topR6_N2_fail_PuDown',  # trigger up/down
#             ]

    if options.bb:
        plots = ['h_msd_v_pt_ca15_bbleading_topR6_pass', 'h_msd_v_pt_ca15_bbleading_topR6_fail']
    elif muonCR:
        plots = ['h_msd_ca15_muCR4_N2_pass', 'h_msd_ca15_muCR4_N2_fail',
                 'h_msd_ca15_muCR4_N2_pass_JESUp', 'h_msd_ca15_muCR4_N2_pass_JESDown',
                 'h_msd_ca15_muCR4_N2_fail_JESUp', 'h_msd_ca15_muCR4_N2_fail_JESDown',
                 'h_msd_ca15_muCR4_N2_pass_JERUp', 'h_msd_ca15_muCR4_N2_pass_JERDown',
                 'h_msd_ca15_muCR4_N2_fail_JERUp', 'h_msd_ca15_muCR4_N2_fail_JERDown',
                 'h_msd_ca15_muCR4_N2_pass_mutriggerUp', 'h_msd_ca15_muCR4_N2_pass_mutriggerDown',
                 'h_msd_ca15_muCR4_N2_fail_mutriggerUp', 'h_msd_ca15_muCR4_N2_fail_mutriggerDown',
                 'h_msd_ca15_muCR4_N2_pass_muidUp', 'h_msd_ca15_muCR4_N2_pass_muidDown',
                 'h_msd_ca15_muCR4_N2_fail_muidUp', 'h_msd_ca15_muCR4_N2_fail_muidDown',
                 'h_msd_ca15_muCR4_N2_pass_muisoUp', 'h_msd_ca15_muCR4_N2_pass_muisoDown',
                 'h_msd_ca15_muCR4_N2_fail_muisoUp', 'h_msd_ca15_muCR4_N2_fail_muisoDown',
                 'h_msd_ca15_muCR4_N2_pass_PuUp', 'h_msd_ca15_muCR4_N2_pass_PuDown',
                 'h_msd_ca15_muCR4_N2_fail_PuUp', 'h_msd_ca15_muCR4_N2_fail_PuDown',
                 ]

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
            hall['%s_%s' % ('data_obs', tag2)] = getattr(dataSample, plot)
            hall['%s_%s' % ('data_obs', tag2)].SetName('%s_%s' % ('data_obs', tag2))
            print 'data_obs' + '_' + tag2
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
    

    (options, args) = parser.parse_args()

    main(options, args)

    print "All done."
