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
	fd =r.TFile("%s/base.root" % idir);
	histograms_pass_all = {};
	histograms_fail_all = {};

	histograms_pass_summed = {};
	histograms_fail_summed = {};

        shapes = ['wqq','zqq','tqq','qcd','zqq'+mass,'data']

	msd_binBoundaries=[]
	for i in range(0,58): msd_binBoundaries.append(40+i*5)
	pt_binBoundaries = [500,600,700,800,900,1000]

	# Pass and fail
	for i in range(5): 
		(tmppass,tmpfail) = plotCategory(fml, fd, i+1, options.fit, options.mass, options.useMLFit,options.tf);
		histograms_pass_all[i] = {}
		histograms_fail_all[i] = {}
		for shape in shapes:
			for hist in tmppass:
				if shape in hist.GetName(): histograms_pass_all[i][shape] = hist
			for hist in tmpfail:
				if shape in hist.GetName(): histograms_fail_all[i][shape] = hist
	# Added histograms
	for shape in shapes:
		histograms_pass_summed[shape] = histograms_pass_all[0][shape].Clone(shape+'_pass_sum')
		histograms_fail_summed[shape] = histograms_fail_all[0][shape].Clone(shape+'_fail_sum')
		for i in range(1,5):
			histograms_pass_summed[shape].Add(histograms_pass_all[i][shape])
			histograms_fail_summed[shape].Add(histograms_fail_all[i][shape])
	histograms_pass_summed_list = []
	histograms_fail_summed_list = []
	for shape in shapes:
		histograms_pass_summed_list.append(histograms_pass_summed[shape])
		histograms_fail_summed_list.append(histograms_fail_summed[shape])

	if options.tf:
		pass_2d = {}
		fail_2d = {}
		for shape in shapes:
			pass_2d[shape] =  r.TH2F('%s_pass_2d'%shape,'%s_pass_2d'%shape,len(msd_binBoundaries)-1, array.array('d',msd_binBoundaries), len(pt_binBoundaries)-1, array.array('d',pt_binBoundaries) )
			fail_2d[shape] =  r.TH2F('%s_fail_2d'%shape,'%s_fail_2d'%shape,len(msd_binBoundaries)-1, array.array('d',msd_binBoundaries), len(pt_binBoundaries)-1, array.array('d',pt_binBoundaries) )
			for i in range(1,pass_2d[shape].GetNbinsX()+1):
				for j in range(1,pass_2d[shape].GetNbinsY()+1):
					pass_2d[shape].SetBinContent(i,j,histograms_pass_all[j-1][shape].GetBinContent(i))
					fail_2d[shape].SetBinContent(i,j,histograms_fail_all[j-1][shape].GetBinContent(i))

			pass_2d_data_subtract = pass_2d['data'].Clone('data_pass_2d_subtract')
			fail_2d_data_subtract = fail_2d['data'].Clone('data_fail_2d_subtract')
			for shape in shapes:
				if shape=='qcd' or shape=='data': continue
				pass_2d_data_subtract.Add(pass_2d[shape],-1)
				fail_2d_data_subtract.Add(fail_2d[shape],-1)
			ratio_2d_data_subtract = pass_2d_data_subtract.Clone('ratio_2d_subtract')
			ratio_2d_data_subtract.Divide(fail_2d_data_subtract)
			ratio_2d_data_subtract.SetDirectory(0)
		if options.fit == "fit_b":
			rfr = r.RooFitResult( fml.Get(options.fit) )
			lParams = [];
			lParams.append("qcdeff");
			lParams.append("p1r0");
			lParams.append("p2r0");
			#lParams.append("p3r0");
			lParams.append("p0r1"); ##
			lParams.append("p1r1");
			lParams.append("p2r1");
			#lParams.append("p3r1");
			lParams.append("p0r2"); ##
			lParams.append("p1r2");
			lParams.append("p2r2");
			#lParams.append("p3r2"); ##
			#lParams.append("p0r3");
			#lParams.append("p1r3");
			#lParams.append("p2r3");
			#lParams.append("p3r3");	
		
			pars = [];
			for p in lParams:
				print p,"=",rfr.floatParsFinal().find(p).getVal(),"+/-",rfr.floatParsFinal().find(p).getError()
				pars.append(rfr.floatParsFinal().find(p).getVal())

			print lParams
			print pars
			makeTF(pars,ratio_2d_data_subtract)
	else:
		makeMLFitCanvas(histograms_pass_summed_list[0:4], histograms_pass_summed_list[5], histograms_pass_summed_list[4], shapes, "pass_allcats_"+options.fit+"_"+mass);
		makeMLFitCanvas(histograms_fail_summed_list[0:4], histograms_fail_summed_list[5], histograms_fail_summed_list[4], shapes, "fail_allcats_"+options.fit+"_"+mass);


###############################################################
def convertAsymGraph(iData):
	lX = array.array('d')
	for i0 in range(iData.GetN()):
		lX.append(-iData.GetErrorXlow(i0)+iData.GetX()[i0])
	lX.append(iData.GetX()[iData.GetN()-1]+iData.GetErrorXhigh(iData.GetN()-1))
	lHist = r.TH1D(iData.GetName(),iData.GetName(),len(lX)-1,lX)
	for i0 in range(iData.GetN()):
		lHist.Fill(iData.GetX()[i0],iData.GetY()[i0]*(iData.GetErrorXlow(i0)+iData.GetErrorXhigh(i0)))
	for i0 in range(1,iSum.GetNbinsX()+1):
		lHist.SetBinError(i0,math.sqrt(lHist.GetBinContent(i0)))
	return lHist

###############################################################
def plotCategory(fml,fd,index,fittype,mass,usemlfit,tf):

        #fd = r.TFile("results/base1.root");

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
		print fitdir
		rags.Print();
		
		rrv_fail = r.RooRealVar(rags.find("ch%i_fail_cat%i/%s" % (index,index,ish)));
		curnorm_fail = rrv_fail.getVal();
		rrv_pass = r.RooRealVar(rags.find("ch%i_pass_cat%i/%s" % (index,index,ish)));
		curnorm_pass = rrv_pass.getVal();
		
		print ish, curnorm_fail, curnorm_pass, index, histograms_fail[i].GetNbinsX(),histograms_pass[i].GetNbinsX()
		if curnorm_fail > 0.: histograms_fail[i].Scale(curnorm_fail/histograms_fail[i].Integral());
		if curnorm_pass > 0.: histograms_pass[i].Scale(curnorm_pass/histograms_pass[i].Integral());
	
	if usemlfit:
		histograms_fail.append(fml.Get("shapes_"+fitdir+"/ch%i_fail_cat%i/data" % (index,index)) );
		histograms_pass.append(fml.Get("shapes_"+fitdir+"/ch%i_pass_cat%i/data" % (index,index)) );
	else:
		wp = fd.Get("w_pass_cat%i" % (index));
		wf = fd.Get("w_fail_cat%i" % (index));
		rdhp = wp.data("data_obs_pass_cat%i" % (index));
		rdhf = wf.data("data_obs_fail_cat%i" % (index));
		rrv   = wp.var("x"); 
		
		data_fail = rdhf.createHistogram("data_fail_cat"+str(index)+"_"+fittype,rrv,r.RooFit.Binning(histograms_pass[0].GetNbinsX()));
		data_pass = rdhp.createHistogram("data_pass_cat"+str(index)+"_"+fittype,rrv,r.RooFit.Binning(histograms_pass[0].GetNbinsX()));

		histograms_fail.append(data_fail);
		histograms_pass.append(data_pass);

	if not tf:
		makeMLFitCanvas(histograms_fail[:4], histograms_fail[5], histograms_fail[4], shapes, "fail_cat"+str(index)+"_"+fittype+"_"+mass);
		makeMLFitCanvas(histograms_pass[:4], histograms_pass[5], histograms_pass[4], shapes, "pass_cat"+str(index)+"_"+fittype+"_"+mass);

	return (histograms_pass,histograms_fail)

###############################################################

def makeMLFitCanvas(bkgs, data, hsig, leg, tag):

	htot = bkgs[0].Clone("htot");
	for ih in range(1,len(bkgs)): htot.Add(bkgs[ih])
	
	print 'N BINS'
	for ih in range(len(bkgs)): print bkgs[ih].GetNbinsX(), bkgs[ih].GetBinLowEdge(1), bkgs[ih].GetBinLowEdge( bkgs[ih].GetNbinsX() ) + bkgs[ih].GetBinWidth( bkgs[ih].GetNbinsX() );

	if 'cat5' in tag:
		print 'DATA!!!'
		print data.GetNbinsX()
		for i in range(1,data.GetNbinsX()):
			print i
			print data.GetBinLowEdge(i)
			print data.GetBinWidth(data.GetNbinsX())
			print data.GetBinContent(i)
			print 'vs' 
			print bkgs[0].GetBinContent(i)+bkgs[1].GetBinContent(i)+bkgs[2].GetBinContent(i)+bkgs[3].GetBinContent(i)
	htot.SetLineColor(r.kBlack);
	colors = [r.kRed, r.kBlue, r.kMagenta, r.kGreen+1, r.kCyan + 1]
	for i,b in enumerate(bkgs): b.SetLineColor(colors[i]);
	hsig.SetLineColor(r.kBlack);
	hsig.SetLineStyle(2);
	hsig.SetLineWidth(2);
    
	l = r.TLegend(0.75,0.6,0.9,0.85);
	l.SetFillStyle(0);
	l.SetBorderSize(0);
	l.SetTextFont(42);
	l.SetTextSize(0.035);
	legnames = {'wqq':'W','zqq':'Z','qcd':'QCD','tqq':'t#bar{t}'}
	for i in range(len(bkgs)):
		l.AddEntry(bkgs[i],legnames[leg[i]],"l")
	l.AddEntry(htot,"Total Bkg.","lf")
	l.AddEntry(hsig,leg[len(leg)-1],"l")
	if data != None:        
		l.AddEntry(data,"Data","pe")

	c = r.TCanvas("c","c",1000,800);
	p12 = r.TPad("p12","p12",0.0,0.3,1.0,1.0);
	p22 = r.TPad("p22","p22",0.0,0.0,1.0,0.3);
	p12.SetBottomMargin(0.02);
	p22.SetTopMargin(0.05);
	p22.SetBottomMargin(0.3);

	c.cd();
	p12.Draw(); p12.cd();

	htot.SetFillStyle(3004);
	htot.SetFillColor(r.kGray+1)
	htot.SetLineColor(r.kGray+2)
	htot.SetMinimum(0)
	htot.SetMarkerSize(0)
	htot.SetMarkerColor(r.kGray+2)
	htot.SetLineWidth(2)
	data.GetXaxis().SetTitle('m_{SD}^{PUPPI} (GeV)')
	if data != None:
		data.Draw('pez')
		htot.Draw('E2same')
	else:
		htot.Draw('E2')

	htot_line = htot.Clone('htot_line')
	htot_line.SetFillStyle(0)
	htot_line.Draw('histsame')
	for b in bkgs: b.Draw('histsames');
	hsig.Draw('histsames');
	l.Draw();
	
	c.cd();
	p22.Draw(); p22.cd();
	p22.SetGrid();

	tag1 = r.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%options.lumi)
	tag1.SetNDC(); tag1.SetTextFont(42)
	tag1.SetTextSize(0.045)
	tag2 = r.TLatex(0.15,0.92,"CMS")
	tag2.SetNDC()
	tag2.SetTextFont(62)
	tag3 = r.TLatex(0.25,0.92,"Preliminary")
	tag3.SetNDC()
	tag3.SetTextFont(52)
	tag2.SetTextSize(0.055)
	tag3.SetTextSize(0.045)
	tag1.Draw()
	tag2.Draw()
	tag3.Draw()
	data.SetMaximum(data.GetMaximum()*1.2)

	iRatio = data.Clone();
	iRatio.Divide(htot);
	iRatio.SetTitle("; m_{SD}^{PUPPI} (GeV); Data/Prediction");
	iRatio.SetMaximum(1.5);
	iRatio.SetMinimum(1.5);
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
	c.SaveAs("plots/mlfit/mlfit_"+tag+".C")
	data.SetMinimum(5e-1)
	p12.SetLogy();
	data.SetMaximum(data.GetMaximum()*2)
	htot.SetMaximum(data.GetMaximum()*2);
	htot.SetMinimum(1);
	c.SaveAs("plots/mlfit/mlfit_"+tag+"-log.pdf")
	c.SaveAs("plots/mlfit/mlfit_"+tag+"-log.png")
        c.SaveAs("plots/mlfit/mlfit_"+tag+"-log.C")

###############################################################
def fun2(x, par):
	rho = r.TMath.Log((x[0]*x[0])/(x[1]*x[1]))
	poly0 = par[0]*(1.0 + par[1]*rho + par[2]*rho*rho)
	poly1 = par[0]*(par[3] + par[4]*rho + par[5]*rho*rho)*x[1]
	poly2 = par[0]*(par[6] + par[7]*rho + par[8]*rho*rho)*x[1]*x[1]
	return poly0+poly1+poly2

def makeTF(pars,ratio):
	
	ratio.GetXaxis().SetTitle('m_{SD}^{PUPPI} (GeV)')
	ratio.GetYaxis().SetTitle('p_{T} (GeV)')
	
	ratio.GetXaxis().SetTitleOffset(1.5)
	ratio.GetYaxis().SetTitleOffset(1.5)
	ratio.GetZaxis().SetTitle('Ratio')
	ratio.GetXaxis().SetNdivisions(504)
	ratio.GetYaxis().SetNdivisions(504)
	ratio.GetZaxis().SetNdivisions(504)
	
	f2params = array.array('d',pars)
	npar = len(f2params)
	print npar
	#f2 = r.TF2("f2","[0]*(1.0 + [1]*(TMath.Log((x[0]*x[0])/(x[1]*x[1]))) + [2]*(TMath.Log((x[0]*x[0])/(x[1]*x[1])))*(TMath.Log((x[0]*x[0])/(x[1]*x[1])))+([3] + [4]*(TMath.Log((x[0]*x[0])/(x[1]*x[1]))) + [5]*(TMath.Log((x[0]*x[0])/(x[1]*x[1])))*(TMath.Log((x[0]*x[0])/(x[1]*x[1]))))*x[1]+([6] + [7]*(TMath.Log((x[0]*x[0])/(x[1]*x[1]))) + [8]*(TMath.Log((x[0]*x[0])/(x[1]*x[1])))*(TMath.Log((x[0]*x[0])/(x[1]*x[1]))))*x[1]*x[1])",43.5, 327.5, 525, 900, npar)
	f2 = r.TF2("f2",fun2, 40+3.5, 201-3.5, 500+25, 1000-100, npar)
	#f2 = r.TF2("tf","[0]*((1+[1]*x+[2]*x*x)+([3]+[4]*x+[5]*x*x)*y+([6]+[7]*x+[8]*x*x)*y*y)", 500, 1000, -6, -1.5)
	#for i in range(0,9):
	#    tf.SetParameter(i,pars[i]);
	f2.SetParameters(f2params)

	c = r.TCanvas("c","c",1000,800)
	c.SetFillStyle(4000)
	c.SetFrameFillStyle(1000)
	c.SetFrameFillColor(0)
	ratio.Draw('surf1')
	f2.Draw("surf fb bb same")

	r.gPad.SetTheta(30)
	r.gPad.SetPhi(30+270)
	r.gPad.Modified()
	r.gPad.Update()
	
	tag1 = r.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%options.lumi)
	tag1.SetNDC(); tag1.SetTextFont(42)
	tag1.SetTextSize(0.045)
	tag2 = r.TLatex(0.15,0.92,"CMS")
	tag2.SetNDC()
	tag2.SetTextFont(62)
	tag3 = r.TLatex(0.25,0.92,"Preliminary")
	tag3.SetNDC()
	tag3.SetTextFont(52)
	tag2.SetTextSize(0.055)
	tag3.SetTextSize(0.045)
	tag1.Draw()
	tag2.Draw()
	tag3.Draw()

	c.SaveAs("plots/mlfit/tf.pdf")
	c.SaveAs("plots/mlfit/tf.C")
	
	for i in range(0,360):        
		r.gPad.SetPhi(30+270+i)
		r.gPad.Modified()
		r.gPad.Update()
		c.SaveAs("plots/mlfit/tf_%03d.png"%i)

##-------------------------------------------------------------------------------------
if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
	parser.add_option("--lumi", dest="lumi", type=float, default = 30,help="luminosity", metavar="lumi")
	parser.add_option('--fit', dest='fit', default = 'prefit',help='choice is either prefit, fit_sb or fit_b', metavar='fit')
	parser.add_option('--idir', dest='idir', default = 'results',help='choice is either prefit, fit_sb or fit_b', metavar='fit')
	parser.add_option('--mass', dest='mass', default = '100',help='choice is either prefit, fit_sb or fit_b', metavar='fit')
	parser.add_option('--pseudo', action='store_true', dest='pseudo', default =False,help='signal comparison', metavar='isData')
	parser.add_option('--useMLFit', action='store_true', dest='useMLFit', default =False,help='signal comparison', metavar='isData')
        parser.add_option('--tfo', action='store_true', dest='tf', default =False,help='draw TF')

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
