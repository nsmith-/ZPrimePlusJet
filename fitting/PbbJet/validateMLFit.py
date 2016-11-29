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
	
	fml = r.TFile("plots/mlfit.root");
	fd  = r.TFile("base.root");
	for i in range(5): plotCategory(fml, fd, i+1, "prefit");

###############################################################

def plotCategory(fml,fd,index,fittype):

	shapes = ['wqq','zqq','qcd']
	cats   = ['pass','fail']

	histograms_fail = [];
	histograms_pass = [];
	fitdir = fittype;
	for i,ish in enumerate(shapes):	
		print fitdir+"/ch%i_fail_cat%i/%s" % (index,index,ish)
		
		histograms_fail.append( fml.Get("shapes_"+fitdir+"/ch%i_fail_cat%i/%s" % (index,index,ish)) );
		histograms_pass.append( fml.Get("shapes_"+fitdir+"/ch%i_pass_cat%i/%s" % (index,index,ish)) );
		rags_fail = fml.Get("norm_"+fitdir);
		rrv_fail = r.RooRealVar(rags_fail.find("ch%i_fail_cat%i/%s" % (index,index,ish)));
		curnorm_fail = rrv_fail.getVal();
		rags_pass = fml.Get("norm_"+fitdir);
		rrv_pass = r.RooRealVar(rags_pass.find("ch%i_pass_cat%i/%s" % (index,index,ish)));
		curnorm_pass = rrv_pass.getVal();
		histograms_fail[i].Scale(curnorm_fail/histograms_fail[i].Integral());
		histograms_pass[i].Scale(curnorm_pass/histograms_pass[i].Integral());

	wp = fd.Get("w_pass_cat%i" % (index));
	wf = fd.Get("w_fail_cat%i" % (index));
	rdhp = wp.data("data_obs_pass_cat%i" % (index));
	rdhf = wf.data("data_obs_fail_cat%i" % (index));
	rrv   = wp.var("x"); 

	histograms_pass.append(rdhp.createHistogram("data_fail_cat"+str(index)+"_"+fittype,rrv,r.RooFit.Binning(histograms_pass[0].GetNbinsX())));
	histograms_fail.append(rdhf.createHistogram("data_pass_cat"+str(index)+"_"+fittype,rrv,r.RooFit.Binning(histograms_pass[0].GetNbinsX())));

	makeMLFitCanvas(histograms_fail[0:3], histograms_fail[3], shapes, "fail_cat"+str(index)+"_"+fittype);
	makeMLFitCanvas(histograms_pass[0:3], histograms_pass[3], shapes, "pass_cat"+str(index)+"_"+fittype);

###############################################################

def makeMLFitCanvas(bkgs, data, leg, tag):

	htot = bkgs[0].Clone("htot");
	for ih in range(1,len(bkgs)): htot.Add(bkgs[ih]);

	htot.SetLineColor(r.kBlack);
	colors = [r.kRed, r.kBlue, r.kMagenta, r.kViolet, r.kCyan + 1]
	for i,b in enumerate(bkgs): b.SetLineColor(colors[i]);

	c = r.TCanvas("c","c",1000,800);
	htot.Draw('hist');
	for b in bkgs: b.Draw('histsames');
	if data != None: data.Draw('pesames');
	c.SaveAs("plots/mlfit/mlfit_"+tag+".pdf")
	c.SaveAs("plots/mlfit/mlfit_"+tag+".png")
	r.gPad.SetLogy();
	htot.SetMinimum(1);
	c.SaveAs("plots/mlfit/mlfit_"+tag+"-log.pdf")
	c.SaveAs("plots/mlfit/mlfit_"+tag+"-log.png")

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
