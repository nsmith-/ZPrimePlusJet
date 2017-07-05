import os
import math
from array import array
from optparse import OptionParser
import ROOT
import sys
sys.path.append(os.path.expandvars("$CMSSW_BASE/src/DAZSLE/ZPrimePlusJet/analysis"))

from sampleContainerPhibbCA15 import *
from Hbb_create_AK8 import getFiles

##----##----##----##----##----##----##
def main(options, args):

    #idir = options.idir   
    odir = options.odir
    lumi = options.lumi
    muonCR = options.muonCR
    dbtagmin = options.dbtagmin

    #fileName = 'hist_1DZbb_pt_scalesmear_CA15.root'
    #fileName = 'hist_1DZbb_pt_scalesmear_CA15_newsamples.root'
    fileName = 'hist_1DZbb_pt_scalesmear_CA15_pre.root'
    if options.bb:
        fileName = 'hist_1DZbb_sortByBB.root'
    elif muonCR:
        fileName = 'hist_1DZbb_muonCR_CA15_newsamples_300.root'

    outfile = ROOT.TFile.Open(options.odir + "/" + fileName, "recreate")

    tfiles = getFiles(muonCR)

    print "Signals... "
    sigSamples = {}
    sigSamples['DMSbb50'] = sampleContainerPhibbCA15('DMSbb50',tfiles['DMSbb50'], 1, dbtagmin, lumi, False, False, '1', False)
    sigSamples['DMSbb100'] = sampleContainerPhibbCA15('DMSbb100',tfiles['DMSbb100'], 1, dbtagmin, lumi, False, False, '1', False)
    sigSamples['DMSbb125'] = sampleContainerPhibbCA15('DMSbb125',tfiles['DMSbb125'], 1, dbtagmin, lumi, False, False, '1', False)
    sigSamples['DMSbb200'] = sampleContainerPhibbCA15('DMSbb200',tfiles['DMSbb200'], 1, dbtagmin, lumi, False, False, '1', False)
    sigSamples['DMSbb300'] = sampleContainerPhibbCA15('DMSbb300',tfiles['DMSbb300'], 1, dbtagmin, lumi, False, False, '1', False)
    sigSamples['DMSbb350'] = sampleContainerPhibbCA15('DMSbb350',tfiles['DMSbb350'], 1, dbtagmin, lumi, False, False, '1', False)
    sigSamples['DMSbb400'] = sampleContainerPhibbCA15('DMSbb400',tfiles['DMSbb400'], 1, dbtagmin, lumi, False, False, '1', False)
    sigSamples['DMSbb500'] = sampleContainerPhibbCA15('DMSbb500',tfiles['DMSbb500'], 1, dbtagmin, lumi, False, False, '1', False)

    print "Backgrounds..."
    bkgSamples = {}
    bkgSamples['wqq'] = sampleContainerPhibbCA15('wqq', tfiles['wqq'], 1, dbtagmin, lumi, False, False, '1', False)
    bkgSamples['zqq'] = sampleContainerPhibbCA15('zqq', tfiles['zqq'], 1, dbtagmin, lumi, False, False, '1', False)
    if not options.skipQCD:
        bkgSamples['qcd'] = sampleContainerPhibbCA15('qcd', tfiles['qcd'], 1, dbtagmin, lumi, False, False, '1', False)
    bkgSamples['tqq'] = sampleContainerPhibbCA15('tqq', tfiles['tqq'], 1, dbtagmin, lumi, False, False, '1', False)
    bkgSamples['stqq'] = sampleContainerPhibbCA15('stqq', tfiles['stqq'], 1, dbtagmin, lumi, False, False, '1', False)
    bkgSamples['wlnu'] = sampleContainerPhibbCA15('wlnu', tfiles['wlnu'], 1, dbtagmin, lumi, False, False, '1', False)
    bkgSamples['zll'] = sampleContainerPhibbCA15('zll', tfiles['zll'], 1, dbtagmin, lumi, False, False, '1', False)
    bkgSamples['vvqq'] = sampleContainerPhibbCA15('vvqq', tfiles['vvqq'], 1, dbtagmin, lumi, False, False, '1', False)
    bkgSamples['hqq125'] = sampleContainerPhibbCA15('hqq125', tfiles['hqq125'], 1, dbtagmin, lumi, False, False, '1', False)
    bkgSamples['tthqq125'] = sampleContainerPhibbCA15('tthqq125', tfiles['tthqq125'], 1, dbtagmin, lumi, False, False, '1', False)
    bkgSamples['vbfhqq125'] = sampleContainerPhibbCA15('vbfhqq125', tfiles['vbfhqq125'], 1, dbtagmin, lumi, False, False, '1', False)
    bkgSamples['whqq125'] = sampleContainerPhibbCA15('whqq125', tfiles['whqq125'], 1, dbtagmin, lumi, False, False, '1', False)
    bkgSamples['zhqq125'] = sampleContainerPhibbCA15('zhqq125', tfiles['zhqq125'], 1, dbtagmin, lumi, False, False, '1', False)


    print "Data..."
    if not options.skipData:
        if muonCR:
            dataSample = sampleContainerPhibbCA15('data_obs', tfiles['data_obs'], 1, dbtagmin, lumi, False, False,'((triggerBits&4)&&passJson)', False)
        else:
            dataSample = sampleContainerPhibbCA15('data_obs', tfiles['data_obs'], 1, dbtagmin, lumi, False, False,'((triggerBits&2)&&passJson)', False)

    hall = {}

    dbcuts = [0.7,0.75,0.8,0.85,0.9,0.95]
    plots = []
    for dbcut in dbcuts:
        plots.extend([
             'h_msd_v_pt_ca15_topR6_N2_%s_pass'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_ca15_topR6_N2_%s_fail'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_ca15_topR6_N2_%s_pass_matched'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_ca15_topR6_N2_%s_fail_matched'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_ca15_topR6_N2_%s_pass_unmatched'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_ca15_topR6_N2_%s_fail_unmatched'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_ca15_topR6_N2_%s_pass_JESUp'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_ca15_topR6_N2_%s_fail_JESUp'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_ca15_topR6_N2_%s_pass_JESDown'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_ca15_topR6_N2_%s_fail_JESDown'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_ca15_topR6_N2_%s_pass_JERUp'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_ca15_topR6_N2_%s_fail_JERUp'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_ca15_topR6_N2_%s_pass_JERDown'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_ca15_topR6_N2_%s_fail_JERDown'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_ca15_topR6_N2_%s_pass_triggerUp'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_ca15_topR6_N2_%s_fail_triggerUp'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_ca15_topR6_N2_%s_pass_triggerDown'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_ca15_topR6_N2_%s_fail_triggerDown'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_ca15_topR6_N2_%s_pass_PuUp'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_ca15_topR6_N2_%s_fail_PuUp'%str(dbcut).replace('0.','p'),
             'h_msd_v_pt_ca15_topR6_N2_%s_pass_PuDown'%str(dbcut).replace('0.','p'), 'h_msd_v_pt_ca15_topR6_N2_%s_fail_PuDown'%str(dbcut).replace('0.','p')
             ])

    if options.bb:
        plots = ['h_msd_v_pt_ca15_bbleading_topR6_pass', 'h_msd_v_pt_ca15_bbleading_topR6_fail']
    elif muonCR:
        for dbcut in dbcuts:
            plots.extend([
                 'h_msd_ca15_muCR4_N2_%s_pass'%str(dbcut).replace('0.','p'), 'h_msd_ca15_muCR4_N2_%s_fail'%str(dbcut).replace('0.','p'),
                 'h_msd_ca15_muCR4_N2_%s_pass_JESUp'%str(dbcut).replace('0.','p'), 'h_msd_ca15_muCR4_N2_%s_pass_JESDown'%str(dbcut).replace('0.','p'),
                 'h_msd_ca15_muCR4_N2_%s_fail_JESUp'%str(dbcut).replace('0.','p'), 'h_msd_ca15_muCR4_N2_%s_fail_JESDown'%str(dbcut).replace('0.','p'),
                 'h_msd_ca15_muCR4_N2_%s_pass_JERUp'%str(dbcut).replace('0.','p'), 'h_msd_ca15_muCR4_N2_%s_pass_JERDown'%str(dbcut).replace('0.','p'),
                 'h_msd_ca15_muCR4_N2_%s_fail_JERUp'%str(dbcut).replace('0.','p'), 'h_msd_ca15_muCR4_N2_%s_fail_JERDown'%str(dbcut).replace('0.','p'),
                 'h_msd_ca15_muCR4_N2_%s_pass_mutriggerUp'%str(dbcut).replace('0.','p'), 'h_msd_ca15_muCR4_N2_%s_pass_mutriggerDown'%str(dbcut).replace('0.','p'),
                 'h_msd_ca15_muCR4_N2_%s_fail_mutriggerUp'%str(dbcut).replace('0.','p'), 'h_msd_ca15_muCR4_N2_%s_fail_mutriggerDown'%str(dbcut).replace('0.','p'),
                 'h_msd_ca15_muCR4_N2_%s_pass_muidUp'%str(dbcut).replace('0.','p'), 'h_msd_ca15_muCR4_N2_%s_pass_muidDown'%str(dbcut).replace('0.','p'),
                 'h_msd_ca15_muCR4_N2_%s_fail_muidUp'%str(dbcut).replace('0.','p'), 'h_msd_ca15_muCR4_N2_%s_fail_muidDown'%str(dbcut).replace('0.','p'),
                 'h_msd_ca15_muCR4_N2_%s_pass_muisoUp'%str(dbcut).replace('0.','p'), 'h_msd_ca15_muCR4_N2_%s_pass_muisoDown'%str(dbcut).replace('0.','p'),
                 'h_msd_ca15_muCR4_N2_%s_fail_muisoUp'%str(dbcut).replace('0.','p'), 'h_msd_ca15_muCR4_N2_%s_fail_muisoDown'%str(dbcut).replace('0.','p'),
                 'h_msd_ca15_muCR4_N2_%s_pass_PuUp'%str(dbcut).replace('0.','p'), 'h_msd_ca15_muCR4_N2_%s_pass_PuDown'%str(dbcut).replace('0.','p'),
                 'h_msd_ca15_muCR4_N2_%s_fail_PuUp'%str(dbcut).replace('0.','p'), 'h_msd_ca15_muCR4_N2_%s_fail_PuDown'%str(dbcut).replace('0.','p'),
                 ])

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
