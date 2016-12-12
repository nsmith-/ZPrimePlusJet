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

        mass = 125;

        fml = r.TFile("mlfit.root");
        fd  = r.TFile("base.root");

        histograms_pass_all = [];
        histograms_fail_all = [];

        histograms_pass_summed = None;
        histograms_fail_summed = None;

	shapes = ['wqq','zqq','tqq','qcd','hqq125','zhqq125','wmhqq125','wphqq125','tthqq125','vbfhqq125']	


        for i in range(5):
                (tmppass,tmpfail) = plotCategory(fml,fd,i+1,options.fit);
                histograms_pass_all.append(tmppass);
                histograms_fail_all.append(tmpfail);
		if i == 0:
                        histograms_pass_summed = tmppass;
                        histograms_fail_summed = tmpfail;

        for i in range(1,len(histograms_pass_all)):
        #        for j in range(len(histograms_pass_all[i])):
		#for j in range(len(shapes)):
                        histograms_pass_summed.append( histograms_pass_all[i] );
                        histograms_fail_summed.append( histograms_fail_all[i] );

	print("here")
	print(histograms_pass_summed[4:10])
	print(histograms_pass_summed[0:4])
	print(histograms_pass_summed[10])
        makeMLFitCanvas(histograms_pass_summed[0:4], histograms_pass_summed[10], histograms_pass_summed[5:9], shapes, "pass_allcats_"+options.fit);
        makeMLFitCanvas(histograms_fail_summed[0:4], histograms_fail_summed[10], histograms_fail_summed[5:9], shapes, "fail_allcats_"+options.fit);



def plotCategory(fml,fd,index,fittype):

        shapes = ['wqq','zqq','tqq','qcd','hqq125','zhqq125','wmhqq125','wphqq125','tthqq125','vbfhqq125']
	histograms_fail = [];
	histograms_pass = [];
	for i,ish in enumerate(shapes):	
		if i<4:
		   fitdir = fittype;
		else :  fitdir = "prefit"	
		print fitdir+"/ch%i_fail_cat%i/%s" % (index,index,ish)
		
		histograms_fail.append( fml.Get("shapes_"+fitdir+"/ch%i_fail_cat%i/%s" % (index,index,ish)) );
		histograms_pass.append( fml.Get("shapes_"+fitdir+"/ch%i_pass_cat%i/%s" % (index,index,ish)) );
			
		
		rags = fml.Get("norm_"+fitdir);
		rags.Print();

		rrv_fail = r.RooRealVar(rags.find("ch%i_fail_cat%i/%s" % (index,index,ish)));
		curnorm_fail = rrv_fail.getVal();
		rrv_pass = r.RooRealVar(rags.find("ch%i_pass_cat%i/%s" % (index,index,ish)));
		curnorm_pass = rrv_pass.getVal();
		
		print ish, curnorm_fail, curnorm_pass, index
		if curnorm_fail > 0.: histograms_fail[i].Scale(curnorm_fail/histograms_fail[i].Integral());
		if curnorm_pass > 0.: histograms_pass[i].Scale(curnorm_pass/histograms_pass[i].Integral());

	wp = fd.Get("w_pass_cat%i" % (index));
	wf = fd.Get("w_fail_cat%i" % (index));
	rdhp = wp.data("data_obs_pass_cat%i" % (index));
	rdhf = wf.data("data_obs_fail_cat%i" % (index));
	rrv   = wp.var("x"); 

	data_fail = rdhf.createHistogram("data_fail_cat"+str(index)+"_"+fittype,rrv,r.RooFit.Binning(histograms_pass[0].GetNbinsX()));
	data_pass = rdhp.createHistogram("data_pass_cat"+str(index)+"_"+fittype,rrv,r.RooFit.Binning(histograms_pass[0].GetNbinsX()));
	
	histograms_fail.append(data_fail);
        histograms_pass.append(data_pass);

	makeMLFitCanvas(histograms_fail[0:4], data_fail, histograms_fail[4:10], shapes, "fail_cat"+str(index)+"_"+fittype);
	makeMLFitCanvas(histograms_pass[0:4], data_pass, histograms_pass[4:10], shapes, "pass_cat"+str(index)+"_"+fittype);
	


	return (histograms_pass,histograms_fail)

###############################################################

def makeMLFitCanvas(bkgs, data, hsigs, leg, tag):

	htot = bkgs[0].Clone("htot");
	for ih in range(1,len(bkgs)): htot.Add(bkgs[ih]);
	hsig = hsigs[0].Clone("hsig");
		
	for ih in range(1,len(hsigs)):
		hsig.Add(hsigs[ih]);
	# for ih in range(len(bkgs)): print bkgs[ih].GetNbinsX(), bkgs[ih].GetBinLowEdge(1), bkgs[ih].GetBinLowEdge( bkgs[ih].GetNbinsX() ) + bkgs[ih].GetBinWidth( bkgs[ih].GetNbinsX() );
		

	htot.SetLineColor(r.kBlack);
	colors = [r.kRed, r.kBlue, r.kMagenta, r.kGreen+1, r.kCyan + 1]
	for i,b in enumerate(bkgs): 
	#	b.SetFillColor(colors[i]);
		b.SetLineColor(colors[i]);
	hsig.SetLineColor(r.kBlack);
	hsig.SetLineStyle(2);

	l = r.TLegend(0.75,0.6,0.9,0.85);
	l.SetFillStyle(0);
	l.SetBorderSize(0);
	l.SetTextFont(42);
	l.SetTextSize(0.035);
	for i in range(len(bkgs)):
		l.AddEntry(bkgs[i],leg[i],"l");
	l.AddEntry(htot,"total bkg","l")
	l.AddEntry(hsig,"hqq125","l")
	
	if data != None: l.AddEntry(data,"data","pe");

	c = r.TCanvas("c","c",1000,800);
	htot.SetFillStyle(1001)
	htot.SetFillColor(r.kGray+1)
	htot.SetMinimum(1);
	
	htot.Draw('E2');
	for b in bkgs: 
	#	b.SetFillStyle(1001)
		b.Draw('hist sames');
	#hsig.SetFillStyle(1001)
	#hsig.SetFillColor(r.kGray+1)
	hsig.Draw('hist sames');
	if data != None: data.Draw('pesames');
	l.Draw();
	c.SaveAs("plots/mlfit/mlfit_"+tag+".pdf")
	c.SaveAs("plots/mlfit/mlfit_"+tag+".png")
	r.gPad.SetLogy();
	htot.SetMaximum(data.GetMaximum()*2);
	c.SaveAs("plots/mlfit/mlfit_"+tag+"-log.pdf")
	c.SaveAs("plots/mlfit/mlfit_"+tag+"-log.png")

##-------------------------------------------------------------------------------------
if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
	parser.add_option("--lumi", dest="lumi", type=float, default = 30,help="luminosity", metavar="lumi")
	parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
	parser.add_option('--fit', dest='fit', default = 'prefit',help='choice is either prefit, fit_sb or fit_b', metavar='fit')
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
