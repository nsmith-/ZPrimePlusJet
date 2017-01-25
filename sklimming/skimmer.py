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

    #DataDir = '/uscmst1b_scratch/lpc1/3DayLifetime/ntran/DAZSLE16/VectorDiJet1Jetv4'
    #DataDir = '/eos/uscms/store/user/lpchbb/hadd-zprime-v11.05/'
    #OutDir = '/eos/uscms/store/user/lpchbb/zprimebits-v11.05/sklim-Nov7/'
    #DataDir = '/eos/uscms/store/user/jduarte1/zprimebits-v11.051/'    
    #OutDir = '/eos/uscms/store/user/jduarte1/zprimebits-v11.051/sklim-v0-Nov18/'
    DataDir = options.idir
    OutDir = options.odir

    tags = []
    tags.append([ 'DYJetsToLL_M_50_13TeV_ext_0.root', 0])
    tags.append([ 'DYJetsToLL_M_50_13TeV_ext_1.root', 0])
    tags.append([ 'DYJetsToLL_M_50_13TeV_ext_2.root', 0])
    tags.append([ 'DYJetsToQQ_HT180_13TeV_0.root', 0])
    tags.append([ 'GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8_0.root', 0])
    tags.append([ 'GluGluHToBB_M125_13TeV_powheg_pythia8_0.root', 0])
    tags.append([ 'QCD_HT1000to1500_13TeV_0.root', 0])
    tags.append([ 'QCD_HT1000to1500_13TeV_ext_0.root', 0])
    tags.append([ 'QCD_HT1000to1500_13TeV_ext_1.root', 0])
    tags.append([ 'QCD_HT100to200_13TeV_0.root', 0])
    tags.append([ 'QCD_HT100to200_13TeV_1.root', 0])
    tags.append([ 'QCD_HT100to200_13TeV_2.root', 0])
    tags.append([ 'QCD_HT100to200_13TeV_3.root', 0])
    tags.append([ 'QCD_HT100to200_13TeV_4.root', 0])
    tags.append([ 'QCD_HT100to200_13TeV_5.root', 0])
    tags.append([ 'QCD_HT1500to2000_13TeV_0.root', 0])
    tags.append([ 'QCD_HT1500to2000_13TeV_ext_0.root', 0])
    tags.append([ 'QCD_HT1500to2000_13TeV_ext_1.root', 0])
    tags.append([ 'QCD_HT2000toInf_13TeV_0.root', 0])
    tags.append([ 'QCD_HT2000toInf_13TeV_ext_0.root', 0])
    tags.append([ 'QCD_HT200to300_13TeV_0.root', 0])
    tags.append([ 'QCD_HT200to300_13TeV_1.root', 0])
    tags.append([ 'QCD_HT200to300_13TeV_ext_0.root', 0])
    tags.append([ 'QCD_HT300to500_13TeV_0.root', 0])
    tags.append([ 'QCD_HT300to500_13TeV_ext_0.root', 0])
    tags.append([ 'QCD_HT300to500_13TeV_ext_1.root', 0])
    tags.append([ 'QCD_HT300to500_13TeV_ext_2.root', 0])
    tags.append([ 'QCD_HT500to700_13TeV_0.root', 0])
    tags.append([ 'QCD_HT500to700_13TeV_ext_0.root', 0])
    tags.append([ 'QCD_HT500to700_13TeV_ext_1.root', 0])
    tags.append([ 'QCD_HT500to700_13TeV_ext_2.root', 0])
    tags.append([ 'QCD_HT500to700_13TeV_ext_3.root', 0])
    tags.append([ 'QCD_HT50to100_13TeV_0.root', 0])
    tags.append([ 'QCD_HT700to1000_13TeV_0.root', 0])
    tags.append([ 'QCD_HT700to1000_13TeV_ext_0.root', 0])
    tags.append([ 'ST_tW_antitop_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_0.root', 0])
    tags.append([ 'ST_tW_top_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_0.root', 0])
    tags.append([ 'ST_t_channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_0.root', 0])
    tags.append([ 'ST_t_channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_1000_PseudoScalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_1000_Scalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_100_Scalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_125_PseudoScalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_125_Scalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_150_PseudoScalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_150_Scalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_200_PseudoScalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_200_Scalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_250_PseudoScalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_250_Scalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_25_PseudoScalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_25_Scalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_300_PseudoScalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_300_Scalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_350_PseudoScalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_350_Scalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_400_Scalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_500_PseudoScalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_500_Scalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_50_PseudoScalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_50_Scalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_5_PseudoScalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_5_Scalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_600_PseudoScalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_600_Scalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_75_PseudoScalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_75_Scalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_800_PseudoScalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'Spin0_ggPhi12j_g1_800_Scalar_13TeV_madgraph_0.root', 0])
    tags.append([ 'TT_powheg_0.root', 0])
    tags.append([ 'VBFHToBB_M125_13TeV_amcatnlo_pythia8_0.root', 0])
    tags.append([ 'VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_0.root', 0])
    tags.append([ 'VBFHToBB_M_130_13TeV_powheg_pythia8_0.root', 0])
    tags.append([ 'VectorDiJet1Gamma_1000_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Gamma_100_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Gamma_10_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Gamma_125_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Gamma_200_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Gamma_25_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Gamma_300_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Gamma_400_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Gamma_500_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Gamma_50_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Gamma_600_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Gamma_75_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Gamma_800_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Jet_100_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Jet_150_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Jet_200_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Jet_25_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Jet_300_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Jet_400_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Jet_500_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Jet_50_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Jet_600_13TeV_madgraph_0.root', 0])
    tags.append([ 'VectorDiJet1Jet_800_13TeV_madgraph_0.root', 0])
    tags.append([ 'WJetsToLNu_HT_100To200_13TeV_0.root', 0])
    tags.append([ 'WJetsToLNu_HT_1200To2500_13TeV_0.root', 0])
    tags.append([ 'WJetsToLNu_HT_200To400_13TeV_0.root', 0])
    tags.append([ 'WJetsToLNu_HT_2500ToInf_13TeV_0.root', 0])
    tags.append([ 'WJetsToLNu_HT_400To600_13TeV_0.root', 0])
    tags.append([ 'WJetsToLNu_HT_600To800_13TeV_0.root', 0])
    tags.append([ 'WJetsToLNu_HT_800To1200_13TeV_0.root', 0])
    tags.append([ 'WJetsToQQ_HT180_13TeV_0.root', 0])
    tags.append([ 'WWTo4Q_13TeV_powheg_0.root', 0])
    tags.append([ 'WWW_4F_13TeV_amcatnlo_pythia8_0.root', 0])
    tags.append([ 'WWZ_13TeV_amcatnlo_pythia8_0.root', 0])
    tags.append([ 'WZ_13TeV_pythia8_0.root', 0])
    tags.append([ 'WminusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8_0.root', 0])
    tags.append([ 'WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_0.root', 0])
    tags.append([ 'WplusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8_0.root', 0])
    tags.append([ 'WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_0.root', 0])
    tags.append([ 'ZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8_0.root', 0])
    tags.append([ 'ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_0.root', 0])
    tags.append([ 'ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_0.root', 0])
    tags.append([ 'ZZZ_13TeV_amcatnlo_pythia8_0.root', 0])
    tags.append([ 'bbHToBB_M_125_4FS_yb2_13TeV_amcatnlo_0.root', 0])
    tags.append([ 'bbHToBB_M_125_4FS_ybyt_13TeV_amcatnlo_0.root', 0])
    tags.append([ 'ggZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8_0.root', 0])
    tags.append([ 'ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_0.root', 0])
    tags.append([ 'ttHTobb_M125_TuneCUETP8M2_ttHtranche3_13TeV_powheg_pythia8_0.root', 0])
    tags.append([ 'JetHTRun2016B_23Sep2016_v1_0.root', 0])
    tags.append([ 'JetHTRun2016B_23Sep2016_v2_0.root', 0])
    tags.append([ 'JetHTRun2016B_23Sep2016_v3_0.root', 0])
    tags.append([ 'JetHTRun2016B_23Sep2016_v3_1.root', 0])
    tags.append([ 'JetHTRun2016B_23Sep2016_v3_10.root', 0])
    tags.append([ 'JetHTRun2016B_23Sep2016_v3_11.root', 0])
    tags.append([ 'JetHTRun2016B_23Sep2016_v3_12.root', 0])
    tags.append([ 'JetHTRun2016B_23Sep2016_v3_2.root', 0])
    tags.append([ 'JetHTRun2016B_23Sep2016_v3_3.root', 0])
    tags.append([ 'JetHTRun2016B_23Sep2016_v3_4.root', 0])
    tags.append([ 'JetHTRun2016B_23Sep2016_v3_5.root', 0])
    tags.append([ 'JetHTRun2016B_23Sep2016_v3_6.root', 0])
    tags.append([ 'JetHTRun2016B_23Sep2016_v3_7.root', 0])
    tags.append([ 'JetHTRun2016B_23Sep2016_v3_8.root', 0])
    tags.append([ 'JetHTRun2016B_23Sep2016_v3_9.root', 0])
    tags.append([ 'JetHTRun2016C_23Sep2016_v1_0.root', 0])
    tags.append([ 'JetHTRun2016C_23Sep2016_v1_1.root', 0])
    tags.append([ 'JetHTRun2016D_23Sep2016_v1_0.root', 0])
    tags.append([ 'JetHTRun2016D_23Sep2016_v1_1.root', 0])
    tags.append([ 'JetHTRun2016D_23Sep2016_v1_2.root', 0])
    tags.append([ 'JetHTRun2016D_23Sep2016_v1_3.root', 0])
    tags.append([ 'JetHTRun2016D_23Sep2016_v1_4.root', 0])
    tags.append([ 'JetHTRun2016D_23Sep2016_v1_5.root', 0])
    tags.append([ 'JetHTRun2016E_23Sep2016_v1_0.root', 0])
    tags.append([ 'JetHTRun2016E_23Sep2016_v1_1.root', 0])
    tags.append([ 'JetHTRun2016E_23Sep2016_v1_2.root', 0])
    tags.append([ 'JetHTRun2016E_23Sep2016_v1_3.root', 0])
    tags.append([ 'JetHTRun2016E_23Sep2016_v1_4.root', 0])
    tags.append([ 'JetHTRun2016F_23Sep2016_v1_0.root', 0])
    tags.append([ 'JetHTRun2016F_23Sep2016_v1_1.root', 0])
    tags.append([ 'JetHTRun2016F_23Sep2016_v1_2.root', 0])
    tags.append([ 'JetHTRun2016F_23Sep2016_v1_3.root', 0])
    tags.append([ 'JetHTRun2016F_23Sep2016_v1_4.root', 0])
    tags.append([ 'JetHTRun2016G_23Sep2016_v1_0.root', 0])
    tags.append([ 'JetHTRun2016H_PromptReco_v1_0.root', 0])
    tags.append([ 'JetHTRun2016H_PromptReco_v2_0.root', 0])
    tags.append([ 'JetHTRun2016H_PromptReco_v2_1.root', 0])
    tags.append([ 'JetHTRun2016H_PromptReco_v2_2.root', 0])
    tags.append([ 'JetHTRun2016H_PromptReco_v2_3.root', 0])
    tags.append([ 'JetHTRun2016H_PromptReco_v2_4.root', 0])
    tags.append([ 'JetHTRun2016H_PromptReco_v2_5.root', 0])
    tags.append([ 'JetHTRun2016H_PromptReco_v2_6.root', 0])
    tags.append([ 'JetHTRun2016H_PromptReco_v2_7.root', 0])
    tags.append([ 'JetHTRun2016H_PromptReco_v3_0.root', 0])
    tags.append([ 'SingleMuonRun2016B_23Sep2016_v1_0.root', 0])
    tags.append([ 'SingleMuonRun2016B_23Sep2016_v3_0.root', 0])
    tags.append([ 'SingleMuonRun2016B_23Sep2016_v3_1.root', 0])
    tags.append([ 'SingleMuonRun2016C_23Sep2016_v1_0.root', 0])
    tags.append([ 'SingleMuonRun2016D_23Sep2016_v1_0.root', 0])
    tags.append([ 'SingleMuonRun2016E_23Sep2016_v1_0.root', 0])
    tags.append([ 'SingleMuonRun2016F_23Sep2016_v1_0.root', 0])
    tags.append([ 'SingleMuonRun2016G_23Sep2016_v1_0.root', 0])
    tags.append([ 'SingleMuonRun2016H_PromptReco_v1_0.root', 0])
    tags.append([ 'SingleMuonRun2016H_PromptReco_v2_0.root', 0])
    tags.append([ 'SingleMuonRun2016H_PromptReco_v3_0.root', 0])


    # make a tmp dir
    #####
    postfix = ''
    for i in range(len(tags)):
        filesToConvert = getFilesRecursively(DataDir,tags[i][0],None,'sklim')
        print "files To Convert = ",filesToConvert
        # curweight = getLHEWeight( filesToConvert )


        for f in filesToConvert:
            status = sklimAdd(f,OutDir,tags[i][1])
            print status
        ## hadd stuff

    # 	oname = OutDir + '/ProcJPM_'+tags[i][0]+"_"+tags[i][1]+"-"+postfix+".root"
    # 	# oname = OutDir + '/ProcJPM_'+tags[i][0]+"_"+tags[i][1]+".root"
    # 	haddCmmd = 'hadd -f '+oname+" "
    # 	for f in filesToConvert:
    # 		ofile = OutDir + "/" + os.path.basename( f )
    # 		haddCmmd += ofile + " "
    # 	print haddCmmd
    # 	os.system(haddCmmd)

    # for files in os.listdir(OutDir):
    # 	if 'slim' in files: os.system('rm '+OutDir+'/'+files)

    # cmmd = 'hadd -f %s/ProcJPM_ttbar-%s.root %s/*ttbar*-%s_0.root' % (OutDir,postfix,OutDir,postfix)
    # os.system(cmmd)
    # cmmd = 'hadd -f %s/ProcJPM_Wjets-%s.root %s/*Wjets*-%s_0.root' % (OutDir,postfix,OutDir,postfix)
    # os.system(cmmd)
    # cmmd = 'hadd -f %s/ProcJPM_QCD-%s.root %s/*QCD*-%s_0.root' % (OutDir,postfix,OutDir,postfix)
    # os.system(cmmd)
    # cmmd = 'hadd -f %s/ProcJPM_znunu-%s.root %s/*znunu*-%s_0.root' % (OutDir,postfix,OutDir,postfix)
    # os.system(cmmd)



def sklimAdd(fn,odir,mass=0):

    basename = os.path.basename( fn )

    f1 = ROOT.TFile.Open(fn,'read')
    tree = f1.Get("Events")
    try:
        if not tree.InheritsFrom("TTree"):
            return -1
    except:
        return -1
    
    ofile = ROOT.TFile.Open(odir+'/'+basename,'RECREATE')
    ofile.cd()
    f1.cd()	
    obj = ROOT.TObject
    for key in ROOT.gDirectory.GetListOfKeys():
        f1.cd()
        obj = key.ReadObj()
        print obj.GetName()
        if obj.GetName() == 'Events':
            continue
        ofile.cd()
        print key.GetName()
        obj.Write(key.GetName())

        
    
    otree = tree.CloneTree(0)
    otree.SetName("otree")

    otree.SetBranchStatus("*Puppijet0_e2*",0)
    otree.SetBranchStatus("*Puppijet0_e3*",0)
    otree.SetBranchStatus("*Puppijet0_e4*",0)
    otree.SetBranchStatus("CA15Puppi*",0)	
    #otree.SetBranchStatus("bst8_PUPPIjet0_pt",1)

    nent = tree.GetEntries()
    print nent
    fto = ROOT.TFile.Open("test"+str(mass)+".root","RECREATE")
    finfo = ROOT.TFile.Open("signalXS/sig_vectordijet_xspt.root")
    fvbf = ROOT.TFile.Open("signalXS/vbf_ptH_n3lo.root")
    fr = ROOT.TFile.Open("signalXS/Higgs_v2.root")
    h_ggh_num = fr.Get('gghpt_amcnlo012jmt')
    h_ggh_den = fr.Get('ggh_hpt')
    h_ggh_den.Scale(28.45024/h_ggh_den.Integral())
    h_vbf_num = fvbf.Get('h_nnnlo_ptH')
    h_vbf_den = fvbf.Get('h_lo_ptH')
    
  

    # # h_rw = ROOT.TH1F()
    h_rw = None
    if 'VectorDiJet' in fn and mass > 0: 	
        hname = "med_"+str(mass)+"_0.1_proc_800"
        if '75' in fn: hname = "med_"+str(mass)+"_0.1_proc_801"
        hinfo = finfo.Get(hname)
        hinfo.Scale(100*1000.) # 100. for coupling, 1000. for conversion to pb is the cross-section
        hinfo_nbins = hinfo.GetNbinsX()
        hinfo_xlo = hinfo.GetXaxis().GetBinLowEdge(1)
        hinfo_xhi = hinfo.GetXaxis().GetBinUpEdge(hinfo_nbins)
        htmp = ROOT.TH1F("htmp","htmp",hinfo_nbins,hinfo_xlo,hinfo_xhi)
        for i in range(nent):
            tree.GetEntry(i)
            htmp.Fill(tree.genVPt,tree.scale1fb) 

        h_rw = ROOT.TH1F( hinfo.Clone() )
        h_rw.Divide(htmp)

    newscale1fb = array( 'f', [ 0. ] ) #rewriting this guy
    # newkfactor  = array( 'f', [ 0. ] ) #rewriting this guy
    tree.SetBranchAddress("scale1fb",newscale1fb)
    # tree.SetBranchAddress("kfactor",newkfactor)

    for i in range(nent):

        if( nent/100 > 0 and i % (1 * nent/100) == 0):
            sys.stdout.write("\r[" + "="*int(20*i/nent) + " " + str(round(100.*i/nent,0)) + "% done")
            sys.stdout.flush()

        tree.GetEntry(i)
        # print tree.HT, tree.mT2, tree.alphaT, tree.dRazor, tree.mRazor, tree.sumJetMass

        if tree.AK8Puppijet0_pt > 500 :
            # throw out NaN values...
            # print tree.HT, tree.mT2, tree.alphaT, tree.dRazor, tree.mRazor, tree.sumJetMass

            # curalphaT = tree.alphaT
            # curdRazor = tree.dRazor
            # if math.isnan(curalphaT) or math.isnan(curdRazor): continue
            # # print tree.HT, tree.mT2, tree.alphaT, tree.dRazor, tree.mRazor, tree.sumJetMass
            # if int(tree.HT) % 2 == modval: continue
            # # print int(tree.HT)
            # lheWeight[0] = float(weight)
            # MHTOvHT[0] = tree.MHT/math.sqrt(tree.HT)
            # print tree.genVPt ,tree.scale1fb,h_rw.GetBinContent( h_rw.FindBin(tree.genVPt) )
	    if 'GluGluHToBB_M125_13TeV_powheg' in fn:  newscale1fb[0] =  h_ggh_num.GetBinContent( h_ggh_num.FindBin(tree.genVPt) )/h_ggh_den.GetBinContent( h_ggh_den.FindBin(tree.genVPt) )
	    if 'VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix' in fn and tree.genVPt<1000. : newscale1fb[0] =  tree.scale1fb*h_vbf_num.GetBinContent( h_vbf_num.FindBin(tree.genVPt) )/h_vbf_den.GetBinContent( h_vbf_den.FindBin(tree.genVPt) )
            if 'VectorDiJet' in fn and mass > 0: newscale1fb[0] = tree.scale1fb*h_rw.GetBinContent( h_rw.FindBin(tree.genVPt) )
            else: newscale1fb[0] = tree.scale1fb
            #newscale1fb[0]= NEvents.GetBinContent(1)	
            # if 'VectorDiJet' in fn and mass > 0: newkfactor[0] = tree.kfactorNLO
            # else: newkfactor[0] = tree.kfactor

            # print tree.kfactorNLO, tree.kfactor
            # print tree.scale1fb
            # print h_rw.FindBin(tree.genVPt)
            # print h_rw.GetBinContent( h_rw.FindBin(tree.genVPt) )

            otree.Fill()   

    # fto.cd()
    # if 'VectorDiJet' in fn and mass > 0: h_rw.Write()
    # fto.Close()

    print "\n"
    #otree.Print()
    otree.AutoSave()
    ofile.cd()
    otree.Write()
    ofile.Close()
    return 0

def getFilesRecursively(dir,searchstring,additionalstring = None, skipString = None):
	
    # thesearchstring = "_"+searchstring+"_"
    thesearchstring = searchstring

    theadditionalstring = None
    if not additionalstring == None: 
        theadditionalstring = additionalstring

    cfiles = []
    for root, dirs, files in os.walk(dir):
        for file in files:
            # print file	
            if thesearchstring in file:
                if skipString != None and (skipString in file or skipString in dir or skipString in root):
                    print "already skimmed"
                    return []
                if theadditionalstring == None or theadditionalstring in file:
                    cfiles.append(os.path.join(root, file))
    return cfiles

if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('--train', action='store_true', dest='train', default=False, help='train')
    parser.add_option("--lumi", dest="lumi", default = 30,type=float,help="luminosity", metavar="lumi")
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with bacon bits', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = 'skim/',help='directory to write skimmed backon bits', metavar='odir')

    (options, args) = parser.parse_args()

    main(options,args)
