import os
import math
from array import array
from optparse import OptionParser
import ROOT
import sys
from sampleContainer import *


##----##----##----##----##----##----##
def main(options,args):    
    idir = options.idir
    odir = options.odir
    lumi = options.lumi

    fileName = 'hist_1DZbb.root'
    if options.bb:
        fileName = 'hist_1DZbb_sortByBB.root'
    
    outfile=ROOT.TFile(options.odir+"/"+fileName, "recreate")
    
    tfiles = {'hqq125': [idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
              #'vbfhqq125': [idir+'/VBFHToBB_M125_13TeV_amcatnlo_pythia8_1000pb_weighted.root'],
              'vbfhqq125': [idir+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root'],
              'zhqq125': [idir+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
              'whqq125':[idir+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                         idir+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
              'tthqq125':  [idir+'/ttHTobb_M125_TuneCUETP8M2_ttHtranche3_13TeV_powheg_pythia8_1000pb_weighted.root'],
              #'zqq': [idir+'/ZJetsToQQ_HT600toInf_13TeV_madgraph_1000pb_weighted.root'],
              'zqq': [idir+'/DYJetsToQQ_HT180_13TeV_1000pb_weighted.root '],
              #'wqq':  [idir+'/WJetsToQQ_HT_600ToInf_13TeV_1000pb_weighted.root'],
              'wqq':  [idir+'/WJetsToQQ_HT180_13TeV_1000pb_weighted.root'],
              #'tqq':  [idir+'/TTJets_13TeV_1000pb_weighted.root'],
              'tqq':  [idir+'/TT_13TeV_powheg_pythia8_ext_1000pb_weighted.root'],
              'stqq': [idir+'/ST_t-channel_antitop_4f_inclusiveDecays_13TeV_powheg_1000pb_weighted.root',
		                     idir+'/ST_t-channel_top_4f_inclusiveDecays_13TeV_powheg_1000pb_weighted.root',
		                     idir+'/ST_tW_antitop_5f_inclusiveDecays_13TeV_1000pb_weighted.root',
		                     idir+'/ST_tW_top_5f_inclusiveDecays_13TeV_1000pb_weighted.root'],
              'vvqq':[idir+'/WWTo4Q_13TeV_amcatnlo_1000pb_weighted.root',
                          idir+'/ZZTo4Q_13TeV_amcatnlo_1000pb_weighted.root',
                          idir+'/WZ_13TeV_1000pb_weighted.root'],
              'qcd': [idir+'/QCD_HT200to300_13TeV_ext_1000pb_weighted.root',
                      idir+'/QCD_HT300to500_13TeV_ext_1000pb_weighted.root',
                      idir+'/QCD_HT500to700_13TeV_ext_1000pb_weighted.root',
                      idir+'/QCD_HT700to1000_13TeV_ext_1000pb_weighted.root',
                      idir+'/QCD_HT1000to1500_13TeV_ext_1000pb_weighted.root',
                      idir+'/QCD_HT1500to2000_13TeV_ext_1000pb_weighted.root',
                      idir+'/QCD_HT2000toInf_13TeV_ext_1000pb_weighted.root',],     
              'data_obs': [idir+'/JetHTRun2016B_PromptReco_v2_resub.root',
                       idir+'/JetHTRun2016C_PromptReco_v2.root',
                       idir+'/JetHTRun2016D_PromptReco_v2.root',
                       idir+'/JetHTRun2016E_PromptReco_v2.root',
                       idir+'/JetHTRun2016F_PromptReco_v1.root',
                       idir+'/JetHTRun2016G_PromptReco_v1.root',
                       idir+'/JetHTRun2016H_PromptReco_v2.root']
            }
    
    print "Signals... "
    sigSamples = {}
    sigSamples['hqq125']  = sampleContainer('hqq125',tfiles['hqq125']  , 1, lumi)
    sigSamples['tthqq125']  = sampleContainer('tthqq125',tfiles['tthqq125']  , 1, lumi)
    sigSamples['vbfhqq125']  = sampleContainer('vbfhqq125',tfiles['vbfhqq125']  , 1, lumi)
    sigSamples['whqq125']  = sampleContainer('whqq125',tfiles['whqq125']  , 1, lumi)
    sigSamples['zhqq125']  = sampleContainer('zhqq125',tfiles['zhqq125']  , 1, lumi)
    print "Backgrounds..."
    bkgSamples = {}    
    bkgSamples['qcd'] = sampleContainer('qcd',tfiles['qcd'], 1, lumi)
    bkgSamples['tqq'] = sampleContainer('tqq',tfiles['tqq'], 1, lumi)
    bkgSamples['stqq'] = sampleContainer('stqq',tfiles['stqq'], 1, lumi)
    bkgSamples['wqq'] = sampleContainer('wqq',tfiles['wqq'], 1, lumi)
    bkgSamples['zqq'] = sampleContainer('zqq',tfiles['zqq'], 1, lumi)
    bkgSamples['vvqq'] = sampleContainer('vvqq',tfiles['vvqq'], 1, lumi)
    print "Data..."
    dataSample = sampleContainer('data_obs',tfiles['data_obs'], 100, lumi, True , False, '((triggerBits&2)&&passJson)')

    hall={}
    plots =  ['h_msd_v_pt_ak8_topR6_pass','h_msd_v_pt_ak8_topR6_fail']
    if options.bb:
        plots =  ['h_msd_v_pt_ak8_bbleading_topR6_pass','h_msd_v_pt_ak8_bbleading_topR6_fail']
        
    for plot in plots:
        tag = plot.split('_')[-1] # 'pass' or 'fail'            
        
        for process, s in sigSamples.iteritems():
            hall['%s_%s'%(process,tag)] = getattr(s,plot)
            hall['%s_%s'%(process,tag)].SetName('%s_%s'%(process,tag))
        for process, s in bkgSamples.iteritems():
            hall['%s_%s'%(process,tag)] = getattr(s,plot)
            hall['%s_%s'%(process,tag)].SetName('%s_%s'%(process,tag))
        hall['%s_%s'%('data_obs',tag)] = getattr(dataSample,plot)
        hall['%s_%s'%('data_obs',tag)].SetName('%s_%s'%('data_obs',tag))

    outfile.cd()

    for key, h in hall.iteritems():
        h.Write()
        
    outfile.Write()
    outfile.Close()


##----##----##----##----##----##----##
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", default = 30,type=float,help="luminosity", metavar="lumi")
    parser.add_option("--bb", action='store_true', dest="bb", default = False,help="sort by double b-tag")
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = './',help='directory to write histograms', metavar='odir')

    (options, args) = parser.parse_args()

    main(options,args)
