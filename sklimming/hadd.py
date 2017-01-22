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
    samplesDict = {}    
    
    samplesDict['JetHT'] = {
        'JetHTRun2016B_23Sep2016_v1': 'rereco', 
        'JetHTRun2016B_23Sep2016_v2': 'rereco', 
        'JetHTRun2016B_23Sep2016_v3': 'rereco', 
        'JetHTRun2016C_23Sep2016_v1': 'rereco', 
        'JetHTRun2016D_23Sep2016_v1': 'rereco', 
        'JetHTRun2016E_23Sep2016_v1': 'rereco', 
        'JetHTRun2016F_23Sep2016_v1': 'rereco', 
        'JetHTRun2016G_23Sep2016_v1': 'rereco', 
        'JetHTRun2016H_PromptReco_v1': 'data', 
        'JetHTRun2016H_PromptReco_v2': 'data', 
        'JetHTRun2016H_PromptReco_v3': 'data',
        }
    samplesDict['SingleMuon'] = {
        'SingleMuonRun2016B_23Sep2016_v1': 'rereco', 
        'SingleMuonRun2016B_23Sep2016_v3': 'rereco', 
        'SingleMuonRun2016C_23Sep2016_v1': 'rereco', 
        'SingleMuonRun2016D_23Sep2016_v1': 'rereco', 
        'SingleMuonRun2016E_23Sep2016_v1': 'rereco', 
        'SingleMuonRun2016F_23Sep2016_v1': 'rereco', 
        'SingleMuonRun2016G_23Sep2016_v1': 'rereco', 
        'SingleMuonRun2016H_PromptReco_v1': 'data', 
        'SingleMuonRun2016H_PromptReco_v2': 'data', 
        'SingleMuonRun2016H_PromptReco_v3': 'data', 
        }
    samplesDict['Hbb'] = {
        'GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8': 'mc', 
        'GluGluHToBB_M125_13TeV_powheg_pythia8': 'mc', 
        'VBFHToBB_M125_13TeV_amcatnlo_pythia8': 'mc', 
        'VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix': 'mc', 
        'VBFHToBB_M_130_13TeV_powheg_pythia8': 'mc', 
        'WminusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8': 'mc', 
        'WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8': 'mc', 
        'WplusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8': 'mc', 
        'WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8': 'mc', 
        'ZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8': 'mc', 
        'ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8': 'mc', 
        'ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8': 'mc', 
        'bbHToBB_M_125_4FS_yb2_13TeV_amcatnlo': 'mc', 
        'bbHToBB_M_125_4FS_ybyt_13TeV_amcatnlo': 'mc', 
        'ggZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8': 'mc', 
        'ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8': 'mc', 
        'ttHTobb_M125_TuneCUETP8M2_ttHtranche3_13TeV_powheg_pythia8': 'mc', 
        }
    samplesDict['QCD'] = {       
        'QCD_HT1000to1500_13TeV': 'mc',
        'QCD_HT1000to1500_13TeV_ext': 'mc',
        'QCD_HT100to200_13TeV': 'mc', 
        'QCD_HT1500to2000_13TeV': 'mc',
        'QCD_HT1500to2000_13TeV_ext': 'mc',
        'QCD_HT2000toInf_13TeV': 'mc',
        'QCD_HT2000toInf_13TeV_ext': 'mc',
        'QCD_HT200to300_13TeV': 'mc',
        'QCD_HT200to300_13TeV_ext': 'mc',
        'QCD_HT300to500_13TeV': 'mc',
        'QCD_HT300to500_13TeV_ext': 'mc',
        'QCD_HT500to700_13TeV': 'mc',
        'QCD_HT500to700_13TeV_ext': 'mc',
        'QCD_HT50to100_13TeV': 'mc',
        'QCD_HT700to1000_13TeV': 'mc',
        'QCD_HT700to1000_13TeV_ext': 'mc'
        }
    samplesDict['SingleTop'] = {
        'ST_t_channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin': 'mc',
        'ST_t_channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin': 'mc',
        'ST_tW_antitop_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4': 'mc',
        'ST_tW_top_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4': 'mc'
        }
    samplesDict['W'] = {
        'WJetsToQQ_HT180_13TeV': 'mc',
        #'WJetsToQQ_HT_600ToInf_13TeV': 'mc',
        'WJetsToLNu_HT_100To200_13TeV': 'mc',
        'WJetsToLNu_HT_200To400_13TeV': 'mc',
        'WJetsToLNu_HT_400To600_13TeV': 'mc',
        'WJetsToLNu_HT_600To800_13TeV': 'mc',
        'WJetsToLNu_HT_800To1200_13TeV': 'mc',
        'WJetsToLNu_HT_1200To2500_13TeV': 'mc',
        'WJetsToLNu_HT_2500ToInf_13TeV': 'mc',
        }
    samplesDict['DY'] = {
        'DYJetsToLL_M_50_13TeV_ext': 'mc',
        'DYJetsToQQ_HT180_13TeV': 'mc',
        #'ZJetsToQQ_HT600toInf_13TeV_madgraph': 'mc',
        }
    samplesDict['TT'] = {
        #'TTJets_13TeV':'mc',
        'TT_powheg':'mc'
        }
    samplesDict['Diboson'] = {
        #'WWTo4Q_13TeV_amcatnlo': 'mc',
        'WWTo4Q_13TeV_powheg': 'mc',
        #'ZZTo4Q_13TeV_amcatnlo':'mc',
        'WZ_13TeV_pythia8': 'mc'
        }
    samplesDict['Triboson'] = {
        #'TTWJetsToQQ_13TeV': 'mc',
        #'TTGJets_13TeV': 'mc',
        #'TTZToQQ_13TeV': 'mc',
        'WWW_4F_13TeV_amcatnlo_pythia8': 'mc',
        'WWZ_13TeV_amcatnlo_pythia8': 'mc',
        'ZZZ_13TeV_amcatnlo_pythia8': 'mc'
        }
    samplesDict['VectorDiJet1Jet'] = {
        'VectorDiJet1Jet_100_13TeV_madgraph': 'mc', 
        'VectorDiJet1Jet_150_13TeV_madgraph': 'mc', 
        'VectorDiJet1Jet_200_13TeV_madgraph': 'mc', 
        'VectorDiJet1Jet_25_13TeV_madgraph': 'mc', 
        'VectorDiJet1Jet_300_13TeV_madgraph': 'mc', 
        'VectorDiJet1Jet_400_13TeV_madgraph': 'mc', 
        'VectorDiJet1Jet_500_13TeV_madgraph': 'mc', 
        'VectorDiJet1Jet_50_13TeV_madgraph': 'mc', 
        'VectorDiJet1Jet_600_13TeV_madgraph': 'mc', 
        'VectorDiJet1Jet_800_13TeV_madgraph': 'mc', 
        }
    samplesDict['VectorDiJet1Gamma'] = {
        'VectorDiJet1Gamma_1000_13TeV_madgraph': 'mc', 
        'VectorDiJet1Gamma_100_13TeV_madgraph': 'mc', 
        'VectorDiJet1Gamma_10_13TeV_madgraph': 'mc', 
        'VectorDiJet1Gamma_125_13TeV_madgraph': 'mc', 
        'VectorDiJet1Gamma_200_13TeV_madgraph': 'mc', 
        'VectorDiJet1Gamma_25_13TeV_madgraph': 'mc', 
        'VectorDiJet1Gamma_300_13TeV_madgraph': 'mc', 
        'VectorDiJet1Gamma_400_13TeV_madgraph': 'mc', 
        'VectorDiJet1Gamma_500_13TeV_madgraph': 'mc', 
        'VectorDiJet1Gamma_50_13TeV_madgraph': 'mc', 
        'VectorDiJet1Gamma_600_13TeV_madgraph': 'mc', 
        'VectorDiJet1Gamma_75_13TeV_madgraph': 'mc', 
        'VectorDiJet1Gamma_800_13TeV_madgraph': 'mc', 
        }
    samplesDict['DMSpin0'] = {
        'Spin0_ggPhi12j_g1_1000_PseudoScalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_1000_Scalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_100_Scalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_125_PseudoScalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_125_Scalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_150_PseudoScalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_150_Scalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_200_PseudoScalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_200_Scalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_250_PseudoScalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_250_Scalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_25_PseudoScalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_25_Scalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_300_PseudoScalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_300_Scalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_350_PseudoScalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_350_Scalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_400_Scalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_500_PseudoScalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_500_Scalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_50_PseudoScalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_50_Scalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_5_PseudoScalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_5_Scalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_600_PseudoScalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_600_Scalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_75_PseudoScalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_75_Scalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_800_PseudoScalar_13TeV_madgraph': 'mc', 
        'Spin0_ggPhi12j_g1_800_Scalar_13TeV_madgraph': 'mc', 
        }
    
    samplesDict['MC'] = dict(samplesDict['Hbb'].items() +
                             samplesDict['QCD'].items() +
                             samplesDict['SingleTop'].items() +
                             samplesDict['W'].items() +
                             samplesDict['DY'].items() +
                             samplesDict['TT'].items() +
                             samplesDict['Diboson'].items() +
                             samplesDict['Triboson'].items() +
                             samplesDict['VectorDiJet1Jet'].items() +
                             samplesDict['VectorDiJet1Gamma'].items() +
                             samplesDict['DMSpin0'].items())
    
    samplesDict['Data'] = dict(samplesDict['JetHT'].items() +
                               samplesDict['SingleMuon'].items())
                              
    samplesDict['All'] = dict(samplesDict['MC'].items() + samplesDict['Data'].items())

    samples = samplesDict[options.sample]
    
    EOS = '/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select'
    postfix = ''
    for label, isMc in samples.iteritems():
        basename = label + '.root'
        filesToConvert, badFiles = getFilesRecursively(DataDir,label+'/',None,None)
        print "files To Convert = ",filesToConvert
        print "bad files = ", badFiles
        cwd = os.getcwd()
        for i in range(0,len(filesToConvert)/500+1):         
            haddCommand = '#!/bin/bash\n'
            haddCommand += 'pwd\n'
            haddCommand += 'cd %s\n'%cwd   
            haddCommand += 'pwd\n'
            haddCommand += 'eval `scramv1 runtime -sh`\n'
            haddCommand += 'cd -\n'
            haddCommand += 'hadd -f %s %s\n'%(basename.replace('.root','_%i.root'%i),(' '.join(filesToConvert[i*500:(i+1)*500])).replace('eos','root://eoscms.cern.ch//eos'))
            haddCommand += '%s cp %s /%s/%s\n'%(EOS,basename.replace('.root','_%i.root'%i),OutDir,basename.replace('.root','_%i.root'%i))        
            haddCommand += 'rm %s'%(basename.replace('.root','_%i.root'%i))
            with open('hadd_command_%s.sh'%(basename.replace('.root','_%i.root'%i)),'w') as f:
                f.write(haddCommand)

            os.system('bsub -q 8nh -o $PWD/hadd_command_%s.log source $PWD/hadd_command_%s.sh'%(basename.replace('.root','_%i.root'%i),basename.replace('.root','_%i.root'%i)))

        with open('bad_files_%s.txt'%basename,'w') as f:
            for badFile in badFiles:
                f.write(badFile+'\n')


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
                #f = ROOT.TFile.Open((os.path.join(root, file)).replace('eos','root://eoscms.cern.ch//eos'))
                f = ROOT.TFile.Open((os.path.join(root, file)))
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
    parser.add_option('-s','--sample',dest="sample", default="All",
                      choices=['All','Hbb','QCD','JetHT','SingleMuon','DMSpin0','TT','DY','W','Diboson','Triboson','SingleTop','VectorDiJet1Jet','VectorDiJet1Gamma','MC','Data'],
                      help="samples to produces")

    (options, args) = parser.parse_args()

    main(options,args)
