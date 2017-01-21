#! /usr/bin/env python
import os
import glob
import math
from array import array
import sys
import time
from optparse import OptionParser

import ROOT

# ROOT.gROOT.ProcessLine(".L ~/tdrstyle.C")
# ROOT.setTDRStyle()
# ROOT.gStyle.SetPadTopMargin(0.06)
# ROOT.gStyle.SetPadLeftMargin(0.16)
# ROOT.gStyle.SetPadRightMargin(0.10)
# ROOT.gStyle.SetPalette(1)
# ROOT.gStyle.SetPaintTextFormat("1.1f")


############################################################

# observableTraining takes in 2 root files, list of observables, spectator observables ... launches a CONDOR job
# TMVAhelper.py is used by observableTraining
# analysis.py defines the list of trainings, the signal and background process

########################################################################################################################
########################################################################################################################

def main(options,args):

    DataDir = options.idir
    OutDir = options.odir

    tags = []
    #tags.append([ 'DYJetsToLL_M_50_13TeV_ext/', 0] )
    #tags.append([ 'DYJetsToQQ_HT180_13TeV/', 0] )
    #tags.append([ 'GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8/', 0] )
    #tags.append([ 'GluGluHToBB_M125_13TeV_powheg_pythia8/', 0] )
    tags.append([ 'QCD_HT1000to1500_13TeV/', 0] )
    tags.append([ 'QCD_HT1000to1500_13TeV_ext/', 0] )
    tags.append([ 'QCD_HT100to200_13TeV/', 0] )
    tags.append([ 'QCD_HT1500to2000_13TeV/', 0] )
    tags.append([ 'QCD_HT1500to2000_13TeV_ext/', 0] )
    tags.append([ 'QCD_HT2000toInf_13TeV/', 0] )
    tags.append([ 'QCD_HT2000toInf_13TeV_ext/', 0] )
    tags.append([ 'QCD_HT200to300_13TeV/', 0] )
    tags.append([ 'QCD_HT200to300_13TeV_ext/', 0] )
    tags.append([ 'QCD_HT300to500_13TeV/', 0] )
    tags.append([ 'QCD_HT300to500_13TeV_ext/', 0] )
    tags.append([ 'QCD_HT500to700_13TeV/', 0] )
    tags.append([ 'QCD_HT500to700_13TeV_ext/', 0] )
    tags.append([ 'QCD_HT50to100_13TeV/', 0] )
    tags.append([ 'QCD_HT700to1000_13TeV/', 0] )
    tags.append([ 'QCD_HT700to1000_13TeV_ext/', 0] )
    tags.append([ 'ST_t-channel_antitop_4f_inclusiveDecays_13TeV_powheg/', 0] )
    tags.append([ 'ST_t-channel_top_4f_inclusiveDecays_13TeV_powheg/', 0] )
    tags.append([ 'ST_tW_antitop_5f_inclusiveDecays_13TeV/', 0] )
    tags.append([ 'ST_tW_antitop_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M1/', 0] )
    tags.append([ 'ST_tW_antitop_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4/', 0] )
    tags.append([ 'ST_tW_top_5f_inclusiveDecays_13TeV/', 0] )
    tags.append([ 'ST_tW_top_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M1/', 0] )
    tags.append([ 'ST_tW_top_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4/', 0] )
    tags.append([ 'ST_t_channel_antitop_4f_inclusiveDecays_13TeV_powhegV2_madspin_pythia8_TuneCUETP8M1/', 0] )
    tags.append([ 'ST_t_channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin/', 0] )
    tags.append([ 'ST_t_channel_top_4f_inclusiveDecays_13TeV_powhegV2_madspin_pythia8_TuneCUETP8M1/', 0] )
    tags.append([ 'ST_t_channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_1000_PseudoScalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_1000_Scalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_100_Scalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_125_PseudoScalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_125_Scalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_150_PseudoScalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_150_Scalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_200_PseudoScalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_200_Scalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_250_PseudoScalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_250_Scalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_25_PseudoScalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_25_Scalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_300_PseudoScalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_300_Scalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_350_PseudoScalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_350_Scalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_400_Scalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_500_PseudoScalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_500_Scalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_50_PseudoScalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_50_Scalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_5_PseudoScalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_5_Scalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_600_PseudoScalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_600_Scalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_75_PseudoScalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_75_Scalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_800_PseudoScalar_13TeV_madgraph/', 0] )
    tags.append([ 'Spin0_ggPhi12j_g1_800_Scalar_13TeV_madgraph/', 0] )
    tags.append([ 'TT_powheg/', 0] )
    tags.append([ 'VBFHToBB_M125_13TeV_amcatnlo_pythia8/', 0] )
    tags.append([ 'VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix/', 0] )
    tags.append([ 'VBFHToBB_M_130_13TeV_powheg_pythia8/', 0] )
    tags.append([ 'VectorDiJet1Jet_100_13TeV_madgraph/', 0] )
    tags.append([ 'VectorDiJet1Jet_150_13TeV_madgraph/', 0] )
    tags.append([ 'VectorDiJet1Jet_200_13TeV_madgraph/', 0] )
    tags.append([ 'VectorDiJet1Jet_25_13TeV_madgraph/', 0] )
    tags.append([ 'VectorDiJet1Jet_300_13TeV_madgraph/', 0] )
    tags.append([ 'VectorDiJet1Jet_400_13TeV_madgraph/', 0] )
    tags.append([ 'VectorDiJet1Jet_500_13TeV_madgraph/', 0] )
    tags.append([ 'VectorDiJet1Jet_50_13TeV_madgraph/', 0] )
    tags.append([ 'VectorDiJet1Jet_600_13TeV_madgraph/', 0] )
    tags.append([ 'VectorDiJet1Jet_800_13TeV_madgraph/', 0] )
    tags.append([ 'WJetsToLNu_HT_100To200_13TeV/', 0] )
    tags.append([ 'WJetsToLNu_HT_1200To2500_13TeV/', 0] )
    tags.append([ 'WJetsToLNu_HT_200To400_13TeV/', 0] )
    tags.append([ 'WJetsToLNu_HT_2500ToInf_13TeV/', 0] )
    tags.append([ 'WJetsToLNu_HT_400To600_13TeV/', 0] )
    tags.append([ 'WJetsToLNu_HT_600To800_13TeV/', 0] )
    tags.append([ 'WJetsToLNu_HT_800To1200_13TeV/', 0] )
    tags.append([ 'WJetsToQQ_HT180_13TeV/', 0] )
    tags.append([ 'WWTo4Q_13TeV-powheg/', 0] )
    tags.append([ 'WWTo4Q_13TeV_amcatnlo/', 0] )
    tags.append([ 'WWTo4Q_13TeV_powheg/', 0] )
    tags.append([ 'WWTo4Q_4f_13TeV_amcatnloFXFX_madspin_pythia8/', 0] )
    tags.append([ 'WZ_13TeV/', 0] )
    tags.append([ 'WZ_13TeV_pythia8/', 0] )
    tags.append([ 'WminusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8/', 0] )
    tags.append([ 'WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8/', 0] )
    tags.append([ 'WplusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8/', 0] )
    tags.append([ 'WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8/', 0] )
    tags.append([ 'ZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8/', 0] )
    tags.append([ 'ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8/', 0] )
    tags.append([ 'ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8/', 0] )
    tags.append([ 'ZZTo4Q_13TeV_amcatnlo/', 0] )
    tags.append([ 'ZZTo4Q_13TeV_amcatnloFXFX_madspin_pythia8/', 0] )
    tags.append([ 'bbHToBB_M_125_4FS_yb2_13TeV_amcatnlo/', 0] )
    tags.append([ 'bbHToBB_M_125_4FS_ybyt_13TeV_amcatnlo/', 0] )
    tags.append([ 'ggZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8/', 0] )
    tags.append([ 'ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8/', 0] )
    tags.append([ 'ttHTobb_M125_TuneCUETP8M2_ttHtranche3_13TeV_powheg_pythia8/', 0] )
    #tags = []
    ##tags.append([ 'JetHTRun2016B_23Sep2016_v1/', 0] )
    ##tags.append([ 'JetHTRun2016B_23Sep2016_v2/', 0] )
    #tags.append([ 'JetHTRun2016B_23Sep2016_v3/', 0] )
    #tags.append([ 'JetHTRun2016C_23Sep2016_v1/', 0] )
    #tags.append([ 'JetHTRun2016D_23Sep2016_v1/', 0] )
    #tags.append([ 'JetHTRun2016E_23Sep2016_v1/', 0] )
    #tags.append([ 'JetHTRun2016F_23Sep2016_v1/', 0] )
    #tags.append([ 'JetHTRun2016G_23Sep2016_v1/', 0] )
    #tags.append([ 'JetHTRun2016H_PromptReco_v1/', 0] )
    #tags.append([ 'JetHTRun2016H_PromptReco_v2/', 0] )
    #tags.append([ 'JetHTRun2016H_PromptReco_v3/', 0] )
    #tags.append([ 'SingleMuonRun2016B_23Sep2016_v1/', 0] )
    #tags.append([ 'SingleMuonRun2016B_23Sep2016_v3/', 0] )
    #tags.append([ 'SingleMuonRun2016C_23Sep2016_v1/', 0] )
    #tags.append([ 'SingleMuonRun2016D_23Sep2016_v1/', 0] )
    #tags.append([ 'SingleMuonRun2016E_23Sep2016_v1/', 0] )
    #tags.append([ 'SingleMuonRun2016F_23Sep2016_v1/', 0] )
    #tags.append([ 'SingleMuonRun2016G_23Sep2016_v1/', 0] )
    #tags.append([ 'SingleMuonRun2016H_PromptReco_v1/', 0] )
    #tags.append([ 'SingleMuonRun2016H_PromptReco_v2/', 0] )
    #tags.append([ 'SingleMuonRun2016H_PromptReco_v3/', 0] )


    
    EOS = '/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select'
    postfix = ''
    for i in range(len(tags)):
        basename = tags[i][0].replace('/','') + '.root'
        filesToConvert, badFiles = getFilesRecursively(DataDir,tags[i][0],None,'sklim')
        print "files To Convert = ",filesToConvert
        print "bad files = ", badFiles
        haddCommand = 'hadd -f /tmp/woodson/%s %s\n'%(basename,(' '.join(filesToConvert)).replace('eos','root://eoscms.cern.ch//eos'))
        haddCommand += '%s cp /tmp/woodson/%s /%s/%s'%(EOS,basename,OutDir,basename)
        print haddCommand
        with open('hadd_command_%s.sh'%basename,'w') as f:
            f.write(haddCommand)
        with open('bad_files_%s.txt'%basename,'w') as f:
            for badFile in badFiles:
                f.write(badFile+'\n')

        os.system('source $PWD/hadd_command_%s.sh'%basename)




def getFilesRecursively(dir,searchstring,additionalstring = None, skipString = None):
    
    # thesearchstring = "_"+searchstring+"_"
    thesearchstring = searchstring

    theadditionalstring = None
    if not additionalstring == None: 
        theadditionalstring = additionalstring

    cfiles = []
    badfiles = []
    for root, dirs, files in os.walk(dir+'/'+thesearchstring):
        nfiles = len(files)
        for ifile, file in enumerate(files):
            
            if ifile%100==0:
                print '%i/%i files checked in %s'%(ifile,nfiles,dir+'/'+thesearchstring)
            try:
                f = ROOT.TFile.Open((os.path.join(root, file)).replace('eos','root://eoscms.cern.ch//eos'))
                if f.IsZombie():
                    print 'file is zombie'
                    f.Close()
                    badfiles.append(os.path.join(root, file))                    
                    continue
                elif not f.Get('Events'):
                    print 'tree is false'
                    f.Close()
                    badfiles.append(os.path.join(root, file))                    
                    continue
                elif not f.Get('Events').InheritsFrom('TTree'):
                    print 'tree is not a tree'
                    f.Close()
                    badfiles.append(os.path.join(root, file))                    
                    continue
                else:
                    f.Close()
                    cfiles.append(os.path.join(root, file))                    
            except:
                print 'could not open file or tree'
                badfiles.append(os.path.join(root, file))                    
                continue
                
    return cfiles, badfiles



if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('--train', action='store_true', dest='train', default=False, help='train')
    parser.add_option("--lumi", dest="lumi", default = 30,type=float,help="luminosity", metavar="lumi")
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with bacon bits', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = 'skim/',help='directory to write hadded bits', metavar='odir')

    (options, args) = parser.parse_args()

    main(options,args)
