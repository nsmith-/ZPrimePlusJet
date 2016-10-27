import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array

parser = OptionParser()
parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
parser.add_option("--lumi", dest="lumi", default = 4,help="mass of LSP", metavar="MLSP")
parser.add_option("--binning",dest="binning",default="RA2bBins",help="Select binning to be used: Classic, SMJ, extSMJ", metavar="binning")

(options, args) = parser.parse_args()

from plotHelpers import *
from sampleContainer import *
#
import tdrstyle
tdrstyle.setTDRStyle()
ROOT.gStyle.SetPadTopMargin(0.06);
ROOT.gStyle.SetPadLeftMargin(0.16);
ROOT.gStyle.SetPadRightMargin(0.10);
ROOT.gStyle.SetPalette(1);
ROOT.gStyle.SetPaintTextFormat("1.1f");
ROOT.gStyle.SetOptFit(0000);

##############################################################################
def main():

	idir = "/eos/uscms/store/user/lpchbb/VectorDiJet1Jetv4/sklim-v0-Oct27/";
	lumi = 30.;

	print "Signals... (cross-sections by hand corresponding to gB = 0.5) ... "
	sigSamples = [];
	sigSamples.append( sampleContainer(idir+"/GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8_all.root"  , 1, lumi * 28.45) );
	sigSamples.append( sampleContainer(idir+"/VBFHToBB_M125_13TeV_amcatnlo_pythia8.root", 1, lumi * 28.45) );
	'''
 	sigSamples.append( sampleContainer(idir+"/VectorDiJet1Jet_M100.root" , 1, lumi * 5) );
	sigSamples.append( sampleContainer(idir+"/VectorDiJet1Jet_M125.root" , 1, lumi * 2.25) );
	sigSamples.append( sampleContainer(idir+"/VectorDiJet1Jet_M150.root" , 1, lumi * 1.5) );
	sigSamples.append( sampleContainer(idir+"/VectorDiJet1Jet_M200.root" , 1, lumi * 0.6) );
	sigSamples.append( sampleContainer(idir+"/VectorDiJet1Jet_M250.root" , 1, lumi * 0.25) );
	sigSamples.append( sampleContainer(idir+"/VectorDiJet1Jet_M300.root" , 1, lumi * 0.15) );
	sigSamples.append( sampleContainer(idir+"/VectorDiJet1Jet_M400.root" , 1, lumi * 0.004) );
	sigSamples.append( sampleContainer(idir+"/VectorDiJet1Jet_M500.root" , 1, lumi * 0.001) );
	'''
	print "Backgrounds..."
	bkgSamples = [];
	bkgSamples.append( sampleContainer(idir+"/QCD.root", 100, lumi) ); 
        #bkgSamples.append( sampleContainer(idir+"/W.root", 100, lumi) );
	bkgSamples.append( sampleContainer(idir+"/DY.root", 100, lumi) );
	bkgSamples.append( sampleContainer(idir+"/WWTo4Q_13TeV_amcatnlo.root", 100, lumi) );
	bkgSamples.append( sampleContainer(idir+"/ZZTo4Q_13TeV_amcatnlo.root", 100, lumi) );
	bkgSamples.append( sampleContainer(idir+"/ST_tW_antitop_5f_inclusiveDecays_13TeV.root", 100, lumi) );
	bkgSamples.append( sampleContainer(idir+"/ST_tW_top_5f_inclusiveDecays_13TeV.root", 100, lumi) );
	bkgSamples.append( sampleContainer(idir+"/TTbar_madgraphMLM.root", 100, lumi) );

	
	# this 100 scale factor...just makes the QCD run faster, to use all the QCD, make the SF = 1

	normalize = False;
	# plot(sigSamples,bkgSamples,"");
	hs = [];
	for s in sigSamples: hs.append(s.h_pt_ak8);
	for s in bkgSamples: hs.append(s.h_pt_ak8);
	makeCanvas(hs,normalize);
	hs = [];
	for s in sigSamples: hs.append(s.h_msd_ak8);
	for s in bkgSamples: hs.append(s.h_msd_ak8);
	makeCanvas(hs,normalize);
	hs = [];
	for s in sigSamples: hs.append(s.h_msd_ak8_t21ddtCut);
	for s in bkgSamples: hs.append(s.h_msd_ak8_t21ddtCut);
	makeCanvas(hs,normalize);	
	hs = [];
	for s in sigSamples: hs.append(s.h_t21_ak8);
	for s in bkgSamples: hs.append(s.h_t21_ak8);
	makeCanvas(hs,normalize);	
	hs = [];
	for s in sigSamples: hs.append(s.h_t21ddt_ak8);
	for s in bkgSamples: hs.append(s.h_t21ddt_ak8);
	makeCanvas(hs,normalize);	
	# hs = [];
	# for s in sigSamples: hs.append(s.h_msd_ak8);
	# makeCanvas(hs,True);	

	hs = [];
	for s in sigSamples: hs.append(s.h_pt_ca15);
	for s in bkgSamples: hs.append(s.h_pt_ca15);
	makeCanvas(hs,normalize);
	hs = [];
	for s in sigSamples: hs.append(s.h_msd_ca15);
	for s in bkgSamples: hs.append(s.h_msd_ca15);
	makeCanvas(hs,normalize);
	hs = [];
	for s in sigSamples: hs.append(s.h_msd_ca15_t21ddtCut);
	for s in bkgSamples: hs.append(s.h_msd_ca15_t21ddtCut);
	makeCanvas(hs,normalize);	
	hs = [];
	for s in sigSamples: hs.append(s.h_t21_ca15);
	for s in bkgSamples: hs.append(s.h_t21_ca15);
	makeCanvas(hs,normalize);
	hs = [];
	for s in sigSamples: hs.append(s.h_t21ddt_ca15);
	for s in bkgSamples: hs.append(s.h_t21ddt_ca15);
	makeCanvas(hs,normalize);
	# hs = [];
	# for s in sigSamples: hs.append(s.h_msd_ca15);
	# makeCanvas(hs,True);	

	makeCanvas( [bkgSamples[0].h_rhop_v_t21_ak8_Px], False );
	makeCanvas( [bkgSamples[0].h_rhop_v_t21_ca15_Px], False );


##----##----##----##----##----##----##
if __name__ == '__main__':
	main();
##----##----##----##----##----##----##




