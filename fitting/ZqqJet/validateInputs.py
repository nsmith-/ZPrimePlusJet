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
	
	# plot input histos
	do2DHistInputs("hist_1DZqq.root");

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
	dh_w_p  = wp.data("wqq_pass_cat1");
	dh_z_p  = wp.data("zqq_pass_cat1");
	dh_t_p  = wp.data("tqq_pass_cat1");
	ph_q_p  = wpr.pdf("qcd_pass_cat1");
	ph_q_f  = wfr.pdf("qcd_fail_cat1");

 	frame = rrv.frame();
  	dh_w_p.plotOn(frame, r.RooFit.DrawOption("pe"), r.RooFit.MarkerColor(r.kRed));
  	dh_z_p.plotOn(frame);
	dh_t_p.plotOn(frame, r.RooFit.DrawOption("pe"), r.RooFit.MarkerColor(r.kBlue));
	ph_q_p.plotOn(frame, r.RooFit.LineColor(r.kBlue), r.RooFit.LineWidth(10 ));
	ph_q_f.plotOn(frame, r.RooFit.LineColor(r.kRed));

  	c = r.TCanvas("c","c",1000,800);
  	frame.Draw();
  	c.SaveAs("plots/test.pdf");
  	r.gPad.SetLogy();
  	c.SaveAs("plots/test-log.pdf");

  	######## Some print outs
  	print "-------"
  	print "qcd_fail_cat1_Bin1 = ", wfr.var("qcd_fail_cat1_Bin1").getValV();
  	print "qcdeff = ", wpr.var("qcdeff").getValV();

	# "Var_RhoPol_Bin_530.0_-10.138"
	# 	"Var_Pol_Bin_530.0_-10.138_0"
	# 		"r0","p1"
	# 	"Var_Pol_Bin_530.0_-10.138_1"
	# 		"r1","pr11"
  	print "r0 = ", wpr.var("r0").getValV();
  	print "p1 = ", wpr.var("p1").getValV();
  	print "r1 = ", wpr.var("r1").getValV();
  	print "pr11 = ", wpr.var("pr11").getValV();

def do2DHistInputs(fn):

	tf = r.TFile(fn);
	h2s = [];
	h2s.append( tf.Get("qcd_pass") );
	h2s.append( tf.Get("qcd_fail") );
	h2s.append( tf.Get("wqq_pass") );
	h2s.append( tf.Get("wqq_fail") );
	h2s.append( tf.Get("zqq_pass") );
	h2s.append( tf.Get("zqq_fail") );
	h2s.append( tf.Get("tqq_pass") );
	h2s.append( tf.Get("tqq_fail") );

	for h2 in h2s:
		for ipt in range(h2.GetNbinsY()):
			tmph1 = h2.ProjectionX( "px_" + h2.GetName() + str(ipt), ipt+1, ipt+1 );
			makeCanvas(tmph1);

def makeCanvas(h):

	c = r.TCanvas("c","c",1000,800);
	h.Draw("hist");
	c.SaveAs("plots/hinputs/"+h.GetName()+".pdf");
	r.gPad.SetLogy();
	c.SaveAs("plots/hinputs/"+h.GetName()+"_log.pdf");
	
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
