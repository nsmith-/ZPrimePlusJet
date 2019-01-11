import os
import math
from array import array
from optparse import OptionParser
import ROOT
import sys
sys.path.append(os.path.expandvars("$CMSSW_BASE/src/DAZSLE/ZPrimePlusJet/analysis"))

from sampleContainer import *
from normSampleContainer import *

    

##----##----##----##----##----##----##
def main(options, args):
#    idir = options.idir
    odir = options.odir
    lumi = options.lumi
    muonCR = options.muonCR
    dbtagmin = options.dbtagmin
    DBTMIN = dbtagmin
    dbtagcut = options.dbtagcut
    is2017   = options.is2017
    sfData   = options.sfData

    fileName = 'hist_1DZbb_pt_scalesmear_%s.root'%options.iSplit
    if options.skipQCD:
    	fileName = 'hist_1DZbb_pt_scalesmear_looserWZ_%s.root'%options.iSplit
    if options.bb:
        fileName = 'hist_1DZbb_sortByBB_%s.root'%options.iSplit
    elif muonCR:
        fileName = 'hist_1DZbb_muonCR_%s.root'%options.iSplit

    outfile = ROOT.TFile(options.odir + "/" + fileName, "recreate")
    
    if is2017:
        samplefiles   = open(os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/samples_v15.01.json"),"r")
        tfiles  = json.load(samplefiles)['Hxx_2017']
    # Load older when missing
        # backup_samplefiles   = open(os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/samplefiles.json"),"r")
        # b_tfiles  = json.load(backup_samplefiles)['controlPlotsGGH_2017']
        # for key in b_tfiles.keys():
        #     if key not in tfiles.keys():
        #         tfiles[key] = b_tfiles[key]
        #         print "Adding old/backup files:", key 
        puOpt  = "2017"
    else:
        tfiles = get2016files(muonCR)
        puOpt  = "2016"

    passfail    = ['pass','fail']
    systematics = ['JESUp','JESDown','JERUp','JERDown','triggerUp','triggerDown','PuUp','PuDown','matched','unmatched']
    plots = []
    region  = options.region
    region = 'Hcc1'
    print "Selecting doubleB pass/fail plots for this region   =  %s"% region
    for pf in passfail:
        hname  ="h_msd_v_pt_ak8_%s_%s"%(region,pf)
        plots.append(hname)
        for sys in systematics:
            hname_sys  = "h_msd_v_pt_ak8_%s_%s_%s"%(region,pf,sys)
            plots.append(hname_sys)

    #plots = ['h_msd_v_pt_ak8_topR6_N2_pass', 'h_msd_v_pt_ak8_topR6_N2_fail',
    #         # SR with N2DDT @ 26% && db > 0.9, msd corrected
    #         'h_msd_v_pt_ak8_topR6_N2_pass_matched', 'h_msd_v_pt_ak8_topR6_N2_pass_unmatched',
    #         # matched and unmatached for mass up/down
    #         'h_msd_v_pt_ak8_topR6_N2_fail_matched', 'h_msd_v_pt_ak8_topR6_N2_fail_unmatched',
    #         # matched and unmatached for mass up/down
    #         'h_msd_v_pt_ak8_topR6_N2_pass_JESUp', 'h_msd_v_pt_ak8_topR6_N2_pass_JESDown',  # JES up/down
    #         'h_msd_v_pt_ak8_topR6_N2_fail_JESUp', 'h_msd_v_pt_ak8_topR6_N2_fail_JESDown',  # JES up/down
    #         'h_msd_v_pt_ak8_topR6_N2_pass_JERUp', 'h_msd_v_pt_ak8_topR6_N2_pass_JERDown',  # JER up/down
    #         'h_msd_v_pt_ak8_topR6_N2_fail_JERUp', 'h_msd_v_pt_ak8_topR6_N2_fail_JERDown',  # JER up/down
    #         'h_msd_v_pt_ak8_topR6_N2_pass_triggerUp', 'h_msd_v_pt_ak8_topR6_N2_pass_triggerDown',  # trigger up/down
    #         'h_msd_v_pt_ak8_topR6_N2_fail_triggerUp', 'h_msd_v_pt_ak8_topR6_N2_fail_triggerDown',  # trigger up/down
    #         'h_msd_v_pt_ak8_topR6_N2_pass_PuUp', 'h_msd_v_pt_ak8_topR6_N2_pass_PuDown',  # Pu up/downxf
    #         'h_msd_v_pt_ak8_topR6_N2_fail_PuUp', 'h_msd_v_pt_ak8_topR6_N2_fail_PuDown',  # trigger up/down
    #         ]
    print "N plots = %s "%(len(plots))
    print "plots =  ",plots

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

   
    sigSamples = {}
    bkgSamples = {}
    def_treeName = 'Events'
    def_DDB = 'AK8Puppijet0_deepdoubleb'

    
    if options.is2017:
        pass 
        print "Signals... "
        sigSamples['hqq125'] = normSampleContainer('hqq125', tfiles['ggHbb'], 1, DBTMIN, lumi, False, False, '1', True, 
                iSplit = options.iSplit, maxSplit = options.maxSplit, treeName=def_treeName, doublebName=def_DDB, puOpt='default').addPlots(plots) 
        sigSamples['hcc125'] = normSampleContainer('hcc125' ,tfiles['ggHcc']  , 1, DBTMIN,lumi,False,False,'1',True, 
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, puOpt='default').addPlots(plots) 
        sigSamples['tthqq125'] = normSampleContainer('tthqq125',tfiles['ttHbb']  , 1, DBTMIN,lumi,False,False,'1',True, 
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, puOpt='default').addPlots(plots)
        sigSamples['whqq125'] = normSampleContainer('whqq125',tfiles['WHbb']  , 1, DBTMIN,lumi,False,False,'1',True, 
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, puOpt='default').addPlots(plots)
        sigSamples['zhqq125'] = normSampleContainer('zhqq125',tfiles['ZHbb']  , 1, DBTMIN,lumi,False,False,'1',True, 
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, puOpt='default').addPlots(plots)
        sigSamples['vbfhqq125'] = normSampleContainer('vbfhqq125',tfiles['VBFHbb']  , 1, DBTMIN,lumi,False,False,'1',True, 
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, puOpt='default').addPlots(plots)
    
        print "Backgrounds..." 
        bkgSamples['wqq']   = normSampleContainer('wqq',tfiles['W'], 1, DBTMIN,lumi,False,False,'1',True, 
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, puOpt="default").addPlots(plots)
        bkgSamples['zqq']  = normSampleContainer('zqq', tfiles['Z'], 1, DBTMIN,lumi,False,False,'1', True, 
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, puOpt="default").addPlots(plots) 
        if not options.skipQCD:  
            bkgSamples['qcd']  = normSampleContainer('qcd',tfiles['qcd'], 1, dbtagmin,lumi,False,False,'1',True, 
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, puOpt="default").addPlots(plots)   
        bkgSamples['tqq']  = normSampleContainer('tqq',tfiles['TTbar'], 1, DBTMIN,lumi,False,False,'1',True,
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, puOpt='default').addPlots(plots)
        bkgSamples['stqq']  = normSampleContainer('stqq',tfiles['SingleTop'], 1, DBTMIN,lumi,False,False,'1',True,
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, puOpt='default').addPlots(plots)
        bkgSamples['vvqq']  = normSampleContainer('vvqq',tfiles['Diboson'], 1, DBTMIN,lumi,False,False,'1',True,
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, puOpt='default').addPlots(plots)
        
    else:
        bkgSamples['wqq']  = sampleContainer('wqq',tfiles['wqq'], 1, dbtagmin,lumi,False,False,'1',True, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt="2016")
        bkgSamples['zqq']  = sampleContainer('zqq',tfiles['zqq'], 1, dbtagmin,lumi,False,False,'1',True, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt="2016")
        bkgSamples['wlnu'] = sampleContainer('wlnu', tfiles['wlnu'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt="2016")
        bkgSamples['tqq'] = sampleContainer('tqq', tfiles['tqq'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt=puOpt)
        bkgSamples['stqq'] = sampleContainer('stqq', tfiles['stqq'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt=puOpt)
        bkgSamples['zll'] = sampleContainer('zll', tfiles['zll'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt="2016")
        bkgSamples['vvqq'] = sampleContainer('vvqq', tfiles['vvqq'], 1, dbtagmin, lumi, False, False, '1', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt=puOpt)

    print "Data..."
    if not options.skipData:
        if muonCR:
            dataSample = normSampleContainer('data_obs', tfiles['muon'], sfData, DBTMIN, lumi, True, False, '((triggerBits&4)&&passJson)', True,
                    iSplit = options.iSplit, maxSplit = options.maxSplit, treeName=def_treeName, doublebCut=dbtagcut).addPlots(plots)
        else:
            # 2017 triggerBits
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
            if options.is2017:
                dataSample = normSampleContainer('data_obs', tfiles['data'], sfData, DBTMIN, lumi, True, False, "passJson", True,
                    iSplit = options.iSplit, maxSplit = options.maxSplit, triggerNames=triggerNames, treeName=def_treeName).addPlots(plots)
            else:
                dataSample = sampleContainer('data_obs', tfiles['data_obs'], sfData, dbtagmin, lumi, True, False,
                                       '((triggerBits&2)&&passJson)', True, iSplit = options.iSplit, maxSplit = options.maxSplit,doublebCut=dbtagcut,puOpt=puOpt)

    hall = {}

    normSamples =['wqq','zqq','wlnu','hqq125','hcc125', 'tthqq125', 'vbfhqq125', 'whqq125', 'zhqq125' 'qcd','tqq', 'stqq', 'vvqq']
    for plot in plots:
        tag = plot.split('_')[-1]  # 'pass' or 'fail' or systematicName
        if tag not in ['pass', 'fail']:
            tag = plot.split('_')[-2] + '_' + plot.split('_')[-1]  # 'pass_systematicName', 'pass_systmaticName', etc.

        for process, s in sigSamples.iteritems():
            #if process in normSamples:
            if type(s) == dict:
                hall['%s_%s' % (process, tag)] = sigSamples[process][plot]   #get plot from normSampleContainer
            else:
                hall['%s_%s' % (process, tag)] = getattr(s, plot)           #get plot from SampleContainer
            hall['%s_%s' % (process, tag)].SetName('%s_%s' % (process, tag))

        for process, s in bkgSamples.iteritems():
            #if options.is2017 and process in normSamples:
            if type(s) == dict:
                hall['%s_%s' % (process, tag)] = bkgSamples[process][plot]     #get plot from normSampleContainer
            else:
                hall['%s_%s' % (process, tag)] = getattr(s, plot)           #get plot from SampleContainer
            hall['%s_%s' % (process, tag)].SetName('%s_%s' % (process, tag))

        if not options.skipData:
            #if options.is2017:
            if type(s) == dict:
                hall['%s_%s' % ('data_obs', tag)] = dataSample[plot]
            else:
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
    parser.add_option("--lumi", dest="lumi", default=41.3, type="float", help="luminosity", metavar="lumi")
    parser.add_option("--bb", action='store_true', dest="bb", default=False, help="sort by double b-tag")
    parser.add_option('-i', '--idir', dest='idir', default='data/', help='directory with data', metavar='idir')
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write histograms', metavar='odir')
    parser.add_option('-m', '--muonCR', action='store_true', dest='muonCR', default=False, help='for muon CR',
                      metavar='muonCR')
    parser.add_option('--dbtagmin', dest='dbtagmin', default=-99., type="float",
                      help='left bound to btag selection(fail region lower bound)', metavar='dbtagmin')
    parser.add_option('--dbtagcut', dest='dbtagcut', default=0.9, type="float",
                      help='btag selection for cut value(pass region lower bound)', metavar='dbtagcut')
    parser.add_option('--skip-qcd', action='store_true', dest='skipQCD', default=False, help='skip QCD', metavar='skipQCD')
    parser.add_option('--skip-data', action='store_true', dest='skipData', default=False, help='skip Data', metavar='skipData')
    parser.add_option("--max-split", dest="maxSplit", default=1, type="int", help="max number of jobs", metavar="maxSplit")
    parser.add_option("--i-split"  , dest="iSplit", default=0, type="int", help="job number", metavar="iSplit")
    parser.add_option("--is2017"  , dest="is2017", action='store_true', default=False, help="use 2017 files", metavar="is2017")
    parser.add_option("--sfData" , dest="sfData", default=1, type="int", help="process 1/sf of data", metavar="sfData")
    parser.add_option("--region" , dest="region", default='topR6_N2',choices=['topR6_N2','QGquark','QGgluon'], help="region for pass/fail doubleB tag", metavar="region")

    (options, args) = parser.parse_args()

    main(options, args)

    print "All done."
