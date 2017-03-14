import os
import math
from array import array
from optparse import OptionParser
import ROOT
import sys
sys.path.append(os.path.expandvars("$CMSSW_BASE/src/DAZSLE/ZPrimePlusJet/analysis"))

from sampleContainer import *


##----##----##----##----##----##----##
def main(options, args):
    idir = options.idir
    odir = options.odir
    lumi = options.lumi
    muonCR = options.muonCR
    dbtagmin = options.dbtagmin

    fileName = 'hist_1DZbb_pt_scalesmear.root'
    if options.bb:
        fileName = 'hist_1DZbb_sortByBB.root'
    elif muonCR:
        fileName = 'hist_1DZbb_muonCR.root'

    outfile = ROOT.TFile(options.odir + "/" + fileName, "recreate")

    tfiles = {
        'hqq125': [idir + '/GluGluHToBB_M125_13TeV_powheg_pythia8_all_1000pb_weighted.root'],
        # idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root'],
        # 'VBFHbb': [idir+'/VBFHToBB_M125_13TeV_amcatnlo_pythia8_1000pb_weighted.root'],
        'vbfhqq125': [idir + '/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root'],
        'zhqq125': [idir + '/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir + '/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir + '/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root',
                    idir + '/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
        'whqq125': [idir + '/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                    idir + '/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
        'tthqq125': [idir + '/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
        # ttHTobb_M125_TuneCUETP8M2_ttHtranche3_13TeV_powheg_pythia8_1000pb_weighted.root'],
        'vvqq': [idir + '/WWTo4Q_13TeV_powheg_1000pb_weighted.root',
                 idir + '/ZZ_13TeV_pythia8_1000pb_weighted.root',
                 idir + '/WZ_13TeV_pythia8_1000pb_weighted.root'],
        'zqq': [idir + '/DYJetsToQQ_HT180_13TeV_1000pb_weighted_v1204.root'],
        # ZJetsToQQ_HT600toInf_13TeV_madgraph_1000pb_weighted.root'],#DYJetsToQQ_HT180_13TeV_1000pb_weighted.root '],
        'stqq': [
            idir + '/ST_t_channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
            idir + '/ST_t_channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
            idir + '/ST_tW_antitop_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root',
            idir + '/ST_tW_top_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root'],
        # 'W':  [idir+'/WJetsToQQ_HT_600ToInf_13TeV_1000pb_weighted.root'],
        'wqq': [idir + '/WJetsToQQ_HT180_13TeV_1000pb_weighted_v1204.root'],
        'wlnu': [idir + 'WJetsToLNu_HT_100To200_13TeV_1000pb_weighted.root',
                 idir + '/WJetsToLNu_HT_200To400_13TeV_1000pb_weighted.root',
                 idir + '/WJetsToLNu_HT_400To600_13TeV_1000pb_weighted.root',
                 idir + '/WJetsToLNu_HT_600To800_13TeV_1000pb_weighted.root',
                 idir + '/WJetsToLNu_HT_800To1200_13TeV_1000pb_weighted.root',
                 idir + '/WJetsToLNu_HT_1200To2500_13TeV_1000pb_weighted.root'],
        'zll': [idir + '/DYJetsToLL_M_50_13TeV_ext_1000pb_weighted.root'],
        # 'TTbar':  [idir+'/TTJets_13TeV_1000pb_weighted.root'], #MadGraph is the old default
        'tqq': [idir + '/TT_powheg_1000pb_weighted_v1204.root'],  # Powheg is the new default
        'qcd': [idir + '/QCD_HT100to200_13TeV_1000pb_weighted.root',
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
        'data_obs': [idir + 'JetHTRun2016B_23Sep2016_v1.root',
                     idir + 'JetHTRun2016B_23Sep2016_v3_0.root',
                     idir + 'JetHTRun2016B_23Sep2016_v3_1.root',
                     idir + 'JetHTRun2016B_23Sep2016_v3_2.root',
                     idir + 'JetHTRun2016B_23Sep2016_v3_3.root',
                     idir + 'JetHTRun2016B_23Sep2016_v3_4.root',
                     idir + 'JetHTRun2016B_23Sep2016_v3_5.root',
                     idir + 'JetHTRun2016B_23Sep2016_v3_6.root',
                     idir + 'JetHTRun2016B_23Sep2016_v3_7.root',
                     idir + 'JetHTRun2016B_23Sep2016_v3_8.root',
                     idir + 'JetHTRun2016B_23Sep2016_v3_9.root',
                     idir + 'JetHTRun2016B_23Sep2016_v3_10.root',
                     idir + 'JetHTRun2016B_23Sep2016_v3_11.root',
                     idir + 'JetHTRun2016B_23Sep2016_v3_12.root',
                     idir + 'JetHTRun2016B_23Sep2016_v3_13.root',
                     idir + 'JetHTRun2016B_23Sep2016_v3_14.root',
                     idir + 'JetHTRun2016C_23Sep2016_v1_v2.root',
                     idir + 'JetHTRun2016D_23Sep2016_v1_0.root',
                     idir + 'JetHTRun2016D_23Sep2016_v1_1.root',
                     idir + 'JetHTRun2016D_23Sep2016_v1_2.root',
                     idir + 'JetHTRun2016D_23Sep2016_v1_3.root',
                     idir + 'JetHTRun2016D_23Sep2016_v1_4.root',
                     idir + 'JetHTRun2016D_23Sep2016_v1_5.root',
                     idir + 'JetHTRun2016D_23Sep2016_v1_6.root',
                     idir + 'JetHTRun2016D_23Sep2016_v1_7.root',
                     idir + 'JetHTRun2016E_23Sep2016_v1_0.root',
                     idir + 'JetHTRun2016E_23Sep2016_v1_1.root',
                     idir + 'JetHTRun2016E_23Sep2016_v1_2.root',
                     idir + 'JetHTRun2016E_23Sep2016_v1_3.root',
                     idir + 'JetHTRun2016E_23Sep2016_v1_4.root',
                     idir + 'JetHTRun2016E_23Sep2016_v1_5.root',
                     idir + 'JetHTRun2016E_23Sep2016_v1_6.root',
                     idir + 'JetHTRun2016E_23Sep2016_v1_7.root',
                     idir + 'JetHTRun2016F_23Sep2016_v1.root',
                     idir + 'JetHTRun2016G_23Sep2016_v1_v2.root',
                     idir + 'JetHTRun2016H_PromptReco_v2.root',
                     idir + 'JetHTRun2016H_PromptReco_v3.root']
    }

    if muonCR:
        tfiles['data_obs'] = [idir + '/SingleMuonRun2016B_03Feb2017_ver1_v1.root',
                              idir + '/SingleMuonRun2016B_03Feb2017_ver2_v2.root',
                              idir + '/SingleMuonRun2016C_03Feb2017_v1.root',
                              idir + '/SingleMuonRun2016D_03Feb2017_v1.root',
                              idir + '/SingleMuonRun2016E_03Feb2017_v1.root',
                              idir + '/SingleMuonRun2016F_03Feb2017_v1.root',
                              idir + '/SingleMuonRun2016G_03Feb2017_v1.root',
                              idir + '/SingleMuonRun2016H_03Feb2017_ver2_v1.root',
                              idir + '/SingleMuonRun2016H_03Feb2017_ver3_v1.root']

    print "Signals... "
    sigSamples = {}
    sigSamples['hqq125'] = sampleContainer('hqq125', tfiles['hqq125'], 1, dbtagmin, lumi, False, False, '1', True)
    sigSamples['tthqq125'] = sampleContainer('tthqq125', tfiles['tthqq125'], 1, dbtagmin, lumi, False, False, '1', True)
    sigSamples['vbfhqq125'] = sampleContainer('vbfhqq125', tfiles['vbfhqq125'], 1, dbtagmin, lumi, False, False, '1',
                                              True)
    sigSamples['whqq125'] = sampleContainer('whqq125', tfiles['whqq125'], 1, dbtagmin, lumi, False, False, '1', True)
    sigSamples['zhqq125'] = sampleContainer('zhqq125', tfiles['zhqq125'], 1, dbtagmin, lumi, False, False, '1', True)
    print "Backgrounds..."
    bkgSamples = {}
    bkgSamples['wqq'] = sampleContainer('wqq', tfiles['wqq'], 1, dbtagmin, lumi, False, False, '1', True)
    bkgSamples['zqq'] = sampleContainer('zqq', tfiles['zqq'], 1, dbtagmin, lumi, False, False, '1', True)
    bkgSamples['qcd'] = sampleContainer('qcd', tfiles['qcd'], 1, dbtagmin, lumi, False, False, '1', True)
    bkgSamples['tqq'] = sampleContainer('tqq', tfiles['tqq'], 1, dbtagmin, lumi, False, False, '1', True)
    bkgSamples['stqq'] = sampleContainer('stqq', tfiles['stqq'], 1, dbtagmin, lumi, False, False, '1', True)
    bkgSamples['wlnu'] = sampleContainer('wlnu', tfiles['wlnu'], 1, dbtagmin, lumi, False, False, '1', True)
    bkgSamples['zll'] = sampleContainer('zll', tfiles['zll'], 1, dbtagmin, lumi, False, False, '1', True)
    bkgSamples['vvqq'] = sampleContainer('vvqq', tfiles['vvqq'], 1, dbtagmin, lumi, False, False, '1', True)
    print "Data..."
    if muonCR:
        dataSample = sampleContainer('data_obs', tfiles['data_obs'], 1, dbtagmin, lumi, True, False,
                                     '((triggerBits&4)&&passJson)', True)
    else:
        dataSample = sampleContainer('data_obs', tfiles['data_obs'], 1, dbtagmin, lumi, True, False,
                                     '((triggerBits&2)&&passJson)', True)

    hall = {}

    plots = ['h_msd_v_pt_ak8_topR6_N2_pass', 'h_msd_v_pt_ak8_topR6_N2_fail',
             # SR with N2DDT @ 26% && db > 0.9, msd corrected
             'h_msd_v_pt_ak8_topR6_N2_pass_matched', 'h_msd_v_pt_ak8_topR6_N2_pass_unmatched',
             # matched and unmatached for mass up/down
             'h_msd_v_pt_ak8_topR6_N2_fail_matched', 'h_msd_v_pt_ak8_topR6_N2_fail_unmatched',
             # matched and unmatached for mass up/down
             'h_msd_v_pt_ak8_topR6_N2_pass_JESUp', 'h_msd_v_pt_ak8_topR6_N2_pass_JESDown',  # JES up/down
             'h_msd_v_pt_ak8_topR6_N2_fail_JESUp', 'h_msd_v_pt_ak8_topR6_N2_fail_JESDown',  # JES up/down
             'h_msd_v_pt_ak8_topR6_N2_pass_JERUp', 'h_msd_v_pt_ak8_topR6_N2_pass_JERDown',  # JER up/down
             'h_msd_v_pt_ak8_topR6_N2_fail_JERUp', 'h_msd_v_pt_ak8_topR6_N2_fail_JERDown',  # JER up/down
             'h_msd_v_pt_ak8_topR6_N2_pass_triggerUp', 'h_msd_v_pt_ak8_topR6_N2_pass_triggerDown',  # trigger up/down
             'h_msd_v_pt_ak8_topR6_N2_fail_triggerUp', 'h_msd_v_pt_ak8_topR6_N2_fail_triggerDown',  # trigger up/down
             'h_msd_v_pt_ak8_topR6_N2_pass_PuUp', 'h_msd_v_pt_ak8_topR6_N2_pass_PuDown',  # Pu up/downxf
             'h_msd_v_pt_ak8_topR6_N2_fail_PuUp', 'h_msd_v_pt_ak8_topR6_N2_fail_PuDown',  # trigger up/down
             ]

    if options.bb:
        plots = ['h_msd_v_pt_ak8_bbleading_topR6_pass', 'h_msd_v_pt_ak8_bbleading_topR6_fail']
    elif muonCR:
        plots = ['h_msd_ak8_muCR4_N2_pass', 'h_msd_ak8_muCR4_N2_fail',
                 'h_msd_ak8_muCR4_N2_pass_JESUp', 'h_msd_ak8_muCR4_N2_pass_JESDown',
                 'h_msd_ak8_muCR4_N2_fail_JESUp', 'h_msd_ak8_muCR4_N2_fail_JESDown',
                 'h_msd_ak8_muCR4_N2_pass_JERUp', 'h_msd_ak8_muCR4_N2_pass_JERDown',
                 'h_msd_ak8_muCR4_N2_fail_JERUp', 'h_msd_ak8_muCR4_N2_fail_JERDown',
                 'h_msd_ak8_muCR4_N2_pass_mutriggerUp', 'h_msd_ak8_muCR4_N2_pass_mutriggerDown',
                 'h_msd_ak8_muCR4_N2_fail_mutriggerUp', 'h_msd_ak8_muCR4_N2_fail_mutriggerDown',
                 'h_msd_ak8_muCR4_N2_pass_muidUp', 'h_msd_ak8_muCR4_N2_pass_muidDown',
                 'h_msd_ak8_muCR4_N2_fail_muidUp', 'h_msd_ak8_muCR4_N2_fail_muidDown',
                 'h_msd_ak8_muCR4_N2_pass_muisoUp', 'h_msd_ak8_muCR4_N2_pass_muisoDown',
                 'h_msd_ak8_muCR4_N2_fail_muisoUp', 'h_msd_ak8_muCR4_N2_fail_muisoDown',
                 'h_msd_ak8_muCR4_N2_pass_PuUp', 'h_msd_ak8_muCR4_N2_pass_PuDown',
                 'h_msd_ak8_muCR4_N2_fail_PuUp', 'h_msd_ak8_muCR4_N2_fail_PuDown',
                 ]

    for plot in plots:
        tag = plot.split('_')[-1]  # 'pass' or 'fail' or systematicName
        if tag not in ['pass', 'fail']:
            tag = plot.split('_')[-2] + '_' + plot.split('_')[-1]  # 'pass_systematicName', 'pass_systmaticName', etc.

        for process, s in sigSamples.iteritems():
            hall['%s_%s' % (process, tag)] = getattr(s, plot)
            hall['%s_%s' % (process, tag)].SetName('%s_%s' % (process, tag))
        for process, s in bkgSamples.iteritems():
            hall['%s_%s' % (process, tag)] = getattr(s, plot)
            hall['%s_%s' % (process, tag)].SetName('%s_%s' % (process, tag))
        hall['%s_%s' % ('data_obs', tag)] = getattr(dataSample, plot)
        hall['%s_%s' % ('data_obs', tag)].SetName('%s_%s' % ('data_obs', tag))

    outfile.cd()

    for key, h in hall.iteritems():
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

    (options, args) = parser.parse_args()

    main(options, args)

    print "All done."
