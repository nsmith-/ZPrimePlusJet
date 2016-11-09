#! /usr/bin/env python
import os
import glob
import math
from array import array
import sys
import time

import ROOT

# ROOT.gROOT.ProcessLine(".L ~/tdrstyle.C");
# ROOT.setTDRStyle();
# ROOT.gStyle.SetPadTopMargin(0.06);
# ROOT.gStyle.SetPadLeftMargin(0.16);
# ROOT.gStyle.SetPadRightMargin(0.10);
# ROOT.gStyle.SetPalette(1);
# ROOT.gStyle.SetPaintTextFormat("1.1f");

############################################
#            Job steering                  #
############################################
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
parser.add_option('--train', action='store_true', dest='train', default=False, help='no X11 windows')

(options, args) = parser.parse_args()

############################################################

# observableTraining takes in 2 root files, list of observables, spectator observables ... launches a CONDOR job
# TMVAhelper.py is used by observableTraining
# analysis.py defines the list of trainings, the signal and background process

########################################################################################################################
########################################################################################################################

def main():

	DataDir = '/uscmst1b_scratch/lpc1/3DayLifetime/ntran/DAZSLE16/VectorDiJet1Jetv4'
	# DataDir = "/Users/ntran/Documents/Research/Ext/DissectingJetsPlusMET/sampleProcessing/DissectingJetsPlusMET/localData/Backgrounds/Backgrounds_13TEV/TTBAR/";
	# DataDir = "/Users/ntran/Documents/Research/Ext/DissectingJetsPlusMET/sampleProcessing/DissectingJetsPlusMET/andrewBkg/";
	# DataDir = "/Users/ntran/Documents/Research/Ext/DissectingJetsPlusMET/sampleProcessing/DissectingJetsPlusMET/rawData-v3/";
	OutDir = 'sklim-v0-Nov2'

	tags = [];
	tags.append( ['QCD',0] );
	tags.append( ['W.root',0] );
	tags.append( ['DY',0] );
	tags.append( ['ST_tW_antitop_5f_inclusiveDecays_13TeV',0] );
	tags.append( ['ST_tW_top_5f_inclusiveDecays_13TeV',0]);
	tags.append( ['TTbar_madgraphMLM',0])

	tags.append( ['VectorDiJet1Jet_M50',50] );
	tags.append( ['VectorDiJet1Jet_M75',75] );
	tags.append( ['VectorDiJet1Jet_M100',100] );
	tags.append( ['VectorDiJet1Jet_M125',125] );
	tags.append( ['VectorDiJet1Jet_M150',150] );
	tags.append( ['VectorDiJet1Jet_M200',200] );
	tags.append( ['VectorDiJet1Jet_M250',250] );
	tags.append( ['VectorDiJet1Jet_M300',300] );
	# tags.append( ['VBFHToBB_M125_13TeV_amcatnlo_pythia8',0] );
	
	tags.append( ['JetHTRun2016B',0] );
	tags.append( ['JetHTRun2016C',0] );
	tags.append( ['JetHTRun2016D',0] );


	# make a tmp dir
	#####
	postfix = '';
	for i in range(len(tags)):
		
		filesToConvert = getFilesRecursively(DataDir,tags[i][0]);
		print "files To Convert = ",filesToConvert
		# curweight = getLHEWeight( filesToConvert );
		

		for f in filesToConvert:
			print f;
			sklimAdd(f,OutDir,tags[i][1]);
		## hadd stuff

	# 	oname = OutDir + '/ProcJPM_'+tags[i][0]+"_"+tags[i][1]+"-"+postfix+".root";
	# 	# oname = OutDir + '/ProcJPM_'+tags[i][0]+"_"+tags[i][1]+".root";
	# 	haddCmmd = 'hadd -f '+oname+" ";
	# 	for f in filesToConvert:
	# 		ofile = OutDir + "/" + os.path.basename( f );
	# 		haddCmmd += ofile + " ";
	# 	print haddCmmd;
	# 	os.system(haddCmmd);

	# for files in os.listdir(OutDir):
	# 	if 'slim' in files: os.system('rm '+OutDir+'/'+files)

	# cmmd = 'hadd -f %s/ProcJPM_ttbar-%s.root %s/*ttbar*-%s.root' % (OutDir,postfix,OutDir,postfix)
	# os.system(cmmd)
	# cmmd = 'hadd -f %s/ProcJPM_Wjets-%s.root %s/*Wjets*-%s.root' % (OutDir,postfix,OutDir,postfix)
	# os.system(cmmd)
	# cmmd = 'hadd -f %s/ProcJPM_QCD-%s.root %s/*QCD*-%s.root' % (OutDir,postfix,OutDir,postfix)
	# os.system(cmmd)
	# cmmd = 'hadd -f %s/ProcJPM_znunu-%s.root %s/*znunu*-%s.root' % (OutDir,postfix,OutDir,postfix)
	# os.system(cmmd)



def sklimAdd(fn,odir,mass=0):

	basename = os.path.basename( fn );

	f1 = ROOT.TFile(fn,'read');
	tree = f1.Get("Events");

	ofile = ROOT.TFile(odir+'/'+basename,'RECREATE');
	ofile.cd();
	otree = tree.CloneTree(0);
	otree.SetName("otree");
	
	otree.SetBranchStatus("*Puppijet0_e2*",0);
	otree.SetBranchStatus("*Puppijet0_e3*",0);
	otree.SetBranchStatus("*Puppijet0_e4*",0);
	otree.SetBranchStatus("CA15Puppi*",0);	
	
	
	# signal reweighting, can clean it up nicer...
	nent = tree.GetEntriesFast();
	finfo = ROOT.TFile("signalXS/sig_vectordijet_xspt.root");
	h_rw = None
	if 'VectorDiJet1Jet' in fn and mass > 0: 	
		hname = "med_"+str(mass)+"_0.1_proc_800";
		if '75' in fn: hname = "med_"+str(mass)+"_0.1_proc_801";
		hinfo = finfo.Get(hname)
		hinfo.Scale(100*1000.); # 100. for coupling, 1000. for conversion to pb is the cross-section
		hinfo_nbins = hinfo.GetNbinsX();
		hinfo_xlo = hinfo.GetXaxis().GetBinLowEdge(1);
		hinfo_xhi = hinfo.GetXaxis().GetBinUpEdge(hinfo_nbins);
		htmp = ROOT.TH1F("htmp","htmp",hinfo_nbins,hinfo_xlo,hinfo_xhi)
		for i in range(nent):
			tree.GetEntry(i);
			htmp.Fill(tree.genVPt,tree.scale1fb) 
		
		h_rw = ROOT.TH1F( hinfo.Clone() );
		h_rw.Divide(htmp);

	newscale1fb = array( 'f', [ 0. ] ); #rewriting this guy
	tree.SetBranchAddress("scale1fb",newscale1fb)

	for i in range(nent):

		if(i % (1 * nent/100) == 0):
			sys.stdout.write("\r[" + "="*int(20*i/nent) + " " + str(round(100.*i/nent,0)) + "% done");
			sys.stdout.flush();

		tree.GetEntry(i);
		# print tree.HT, tree.mT2, tree.alphaT, tree.dRazor, tree.mRazor, tree.sumJetMass

		if tree.AK8Puppijet0_pt > 500 :
			
			if 'VectorDiJet1Jet' in fn and mass > 0: newscale1fb[0] = tree.scale1fb*h_rw.GetBinContent( h_rw.FindBin(tree.genVPt) )
			else: newscale1fb[0] = tree.scale1fb
			
			otree.Fill();   

	# fto.cd();
	# if 'VectorDiJet' in fn and mass > 0: h_rw.Write();
	# fto.Close();

	print "\n"
	#otree.Print();
	otree.AutoSave();
	ofile.cd();
	otree.Write();
	ofile.Close();

def getFilesRecursively(dir,searchstring,additionalstring = None):
	
	# thesearchstring = "_"+searchstring+"_";
	thesearchstring = searchstring;
	
	theadditionalstring = None;
	if not additionalstring == None: 
		theadditionalstring = additionalstring;

	cfiles = [];
	for root, dirs, files in os.walk(dir):
		for file in files:
			# print file	
			if thesearchstring in file:
				if theadditionalstring == None or theadditionalstring in file:
					cfiles.append(os.path.join(root, file))
	return cfiles;

if __name__ == '__main__':
	main();



