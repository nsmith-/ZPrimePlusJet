#!/usr/bin/env python

import ROOT as r,sys,math,array,os
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array

# including other directories
sys.path.insert(0, '../.')
from tools import *


##-------------------------------------------------------------------------------------
def main(options,args):
	
	# Load the input histograms
	f = r.TFile("base.root");
	wp = f.Get("w_pass_cat1");
	wf = f.Get("w_fail_cat1");

	fr  = r.TFile("ralphabase.root");
	wpr = fr.Get("w_pass_cat1");
	wfr = fr.Get("w_fail_cat1");

	# wp.Print();
	# wf.Print();
	wpr.Print();
	# wfr.Print();

	rrv   = wp.var("x"); 
	dh_w  = wp.data("wqq_pass_cat1");
	dh_z  = wp.data("zqq_pass_cat1");
	dh_t  = wp.data("tqq_pass_cat1");
	ph_q  = wpr.pdf("qcd_pass_cat1");

 	frame = rrv.frame();
  	dh_w.plotOn(frame, r.RooFit.DrawOption("pe"), r.RooFit.MarkerColor(r.kRed));
  	dh_z.plotOn(frame);
	dh_t.plotOn(frame, r.RooFit.DrawOption("pe"), r.RooFit.MarkerColor(r.kBlue));
	ph_q.plotOn(frame);
	
  	c = r.TCanvas("c","c",1000,800);
  	frame.Draw();
  	c.SaveAs("plots/test.pdf");


##-------------------------------------------------------------------------------------
if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
	parser.add_option("--lumi", dest="lumi", type=float, default = 30,help="luminosity", metavar="lumi")
	parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
	parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
	parser.add_option('--pseudo', action='store_true', dest='pseudo', default =False,help='signal comparison', metavar='isData')

	(options, args) = parser.parse_args()

	import tdrstyle
	tdrstyle.setTDRStyle()
	r.gStyle.SetPadTopMargin(0.10)
	r.gStyle.SetPadLeftMargin(0.16)
	r.gStyle.SetPadRightMargin(0.10)
	r.gStyle.SetPalette(1)
	r.gStyle.SetPaintTextFormat("1.1f")
	r.gStyle.SetOptFit(0000)
	r.gROOT.SetBatch()
	
	main(options,args)
##-------------------------------------------------------------------------------------
