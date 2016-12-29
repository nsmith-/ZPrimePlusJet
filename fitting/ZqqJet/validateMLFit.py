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
	
	mass = options.mass;
	idir = options.idir;

	fml = r.TFile("%s/mlfit_asym_zqq%s.root" % (idir,mass) );
	fd  = r.TFile("%s/base.root" % idir);
	
	histograms_pass_all = [];
	histograms_fail_all = [];

	histograms_pass_summed = None;
	histograms_fail_summed = None;

	for i in range(5): 
		(tmppass,tmpfail) = plotCategory(fml, fd, i+1, options.fit, options.mass);
		histograms_pass_all.append(tmppass);
		histograms_fail_all.append(tmpfail);
		if i == 0:
			histograms_pass_summed = tmppass;
			histograms_fail_summed = tmpfail;

	for i in range(1,len(histograms_pass_all)): 
		#for j in range(len(histograms_pass_all[i])):
			histograms_pass_summed.append( histograms_pass_all[i] );
                        histograms_fail_summed.append( histograms_fail_all[i] );

	shapes = ['wqq','zqq','tqq','qcd','zqq'+mass]
	makeMLFitCanvas(histograms_pass_summed[0:4], histograms_pass_summed[5], histograms_pass_summed[4], shapes, "pass_allcats_"+options.fit+"_"+mass);
	makeMLFitCanvas(histograms_fail_summed[0:4], histograms_fail_summed[5], histograms_fail_summed[4], shapes, "fail_allcats_"+options.fit+"_"+mass);

	# print out fit results
	if options.fit == "fit_b" or options.fit == "fit_s":
		rfr = r.RooFitResult( fml.Get(options.fit) )
		lParams = [];
		lParams.append("qcdeff");
		lParams.append("p1r0");
		lParams.append("p2r0");
		lParams.append("p0r1"); ##
		lParams.append("p1r1");
		lParams.append("p2r1");
		lParams.append("p0r2"); ##
		lParams.append("p1r2");
		lParams.append("p2r2");

		for p in lParams:
			print p,"=",rfr.floatParsFinal().find(p).getVal(),"+/-",rfr.floatParsFinal().find(p).getError() # ,"+",rfr.floatParsFinal().find(p).getAsymErrorHi(),"-",rfr.floatParsFinal().find(p).getAsymErrorLo()



###############################################################

def plotCategory(fml,fd,index,fittype,mass):

	shapes = ['wqq','zqq','tqq','qcd','zqq'+mass]
	cats   = ['pass','fail']

	histograms_fail = [];
	histograms_pass = [];
	fitdir = fittype;
	for i,ish in enumerate(shapes):	
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

	makeMLFitCanvas(histograms_fail[0:4], data_fail, histograms_fail[4], shapes, "fail_cat"+str(index)+"_"+fittype+"_"+mass);
	makeMLFitCanvas(histograms_pass[0:4], data_pass, histograms_pass[4], shapes, "pass_cat"+str(index)+"_"+fittype+"_"+mass);

	return (histograms_pass,histograms_fail)

###############################################################

def makeMLFitCanvas(bkgs, data, hsig, leg, tag):

	htot = bkgs[0].Clone("htot");
	for ih in range(1,len(bkgs)): htot.Add(bkgs[ih]);
	# for ih in range(len(bkgs)): print bkgs[ih].GetNbinsX(), bkgs[ih].GetBinLowEdge(1), bkgs[ih].GetBinLowEdge( bkgs[ih].GetNbinsX() ) + bkgs[ih].GetBinWidth( bkgs[ih].GetNbinsX() );
		

	htot.SetLineColor(r.kBlack);
	colors = [r.kRed, r.kBlue, r.kMagenta, r.kGreen+1, r.kCyan + 1]
	for i,b in enumerate(bkgs): b.SetLineColor(colors[i]);
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
	l.AddEntry(hsig,leg[len(leg)-1],"l")
	if data != None: l.AddEntry(data,"data","pe");

	c = r.TCanvas("c","c",1000,800);

	p12 = r.TPad("p12","p12",0.0,0.3,1.0,1.0);
	p22 = r.TPad("p22","p22",0.0,0.0,1.0,0.3);
	p12.SetBottomMargin(0.02);
	p22.SetTopMargin(0.05);
	p22.SetBottomMargin(0.3);

	c.cd();
	p12.Draw(); p12.cd();

	htot.SetFillStyle(3001);
	htot.SetFillColor(1);
	htot.Draw('e2');
	for b in bkgs: b.Draw('histsames');
	hsig.Draw('histsames');
	if data != None: data.Draw('pesames');
	l.Draw();
	
	c.cd();
	p22.Draw(); p22.cd();
	p22.SetGrid();

	iRatio = data.Clone();
	iRatio.Divide(htot);
	iRatio.SetTitle("; soft drop mass (GeV); Data/Prediction");
	iRatio.GetYaxis().SetTitleSize(0.13);
	iRatio.GetYaxis().SetNdivisions(6);
	iRatio.GetYaxis().SetLabelSize(0.12);
	iRatio.GetYaxis().SetTitleOffset(0.44);
	iRatio.GetXaxis().SetTitleSize(0.13);
	iRatio.GetXaxis().SetLabelSize(0.12);
	iRatio.GetXaxis().SetTitleOffset(0.9);
	iRatio.GetYaxis().SetRangeUser(0.51,1.49);
	iOneWithErrors = htot.Clone();
	iOneWithErrors.Divide(htot.Clone());
	for i in range(iOneWithErrors.GetNbinsX()): 
		if htot.GetBinContent(i+1) > 0: iOneWithErrors.SetBinError( i+1, htot.GetBinError(i+1)/htot.GetBinContent(i+1) );
		else: iOneWithErrors.SetBinError( i+1, 1);
		
	iOneWithErrors.SetFillStyle(3001);
	iOneWithErrors.SetFillColor(4);
	iOneWithErrors.SetMarkerSize(0);
	iOneWithErrors.SetLineWidth(0);
	iRatio.Draw();
	iOneWithErrors.Draw("e2 sames");
	iRatio.Draw("sames");

	c.SaveAs("plots/mlfit/mlfit_"+tag+".pdf")
	c.SaveAs("plots/mlfit/mlfit_"+tag+".png")
	
	p12.SetLogy();
	htot.SetMaximum(data.GetMaximum()*2);
	htot.SetMinimum(1);
	c.SaveAs("plots/mlfit/mlfit_"+tag+"-log.pdf")
	c.SaveAs("plots/mlfit/mlfit_"+tag+"-log.png")

##-------------------------------------------------------------------------------------
if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
	parser.add_option("--lumi", dest="lumi", type=float, default = 30,help="luminosity", metavar="lumi")
	# parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
	parser.add_option('--fit', dest='fit', default = 'prefit',help='choice is either prefit, fit_sb or fit_b', metavar='fit')
	parser.add_option('--idir', dest='idir', default = 'results',help='choice is either prefit, fit_sb or fit_b', metavar='fit')
	parser.add_option('--mass', dest='mass', default = '100',help='choice is either prefit, fit_sb or fit_b', metavar='fit')
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
