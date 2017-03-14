import ROOT
from optparse import OptionParser
from operator import add
import math
import sys
import time
from array import array
import os
import glob

# including other directories
sys.path.insert(0, '../.')

import tdrstyle
tdrstyle.setTDRStyle()
ROOT.gStyle.SetPadRightMargin(0.08);
ROOT.gStyle.SetPadLeftMargin(0.11);
ROOT.gStyle.SetPadTopMargin(0.10);

ROOT.gStyle.SetPalette(1);

########################################################################################
def Upsilonconstraints(x):
	
	mUps = 9.46;
	WidUps = 54e-6;
	alpha = 1/130.;
	Argus = 5.3e-2;
	DimuUps = 2.48e-2;
	RUps = Argus/DimuUps;
	mZp = x[0];

	y = ( 2*4*math.pi*alpha ) * ( math.sqrt( 3.*RUps + 1 ) + 1 ) * (1-(mZp*mZp/(mUps*mUps)))
	if y < 0.: y *= -1;

	return math.sqrt(y)/6.;

def Psiconstraints(x):
	
	sinthetaW2 = 0.2312;
	sinthetaW = math.sqrt(sinthetaW2);
	costhetaW = math.sqrt(1 - sinthetaW2);
	mW = 80.;
	vev = 246.;
	g = mW*2./vev;
	e = g*sinthetaW;

	Vu = 0.25 - (4. * sinthetaW2 / 6);
	Vd = -0.25 - (2. * sinthetaW2 / 6);
	mZ = 91.18;
	mZp = x[0];

	# y = gZ
	ynum = relZwidthUnc * 3 * g * (1-(mZp*mZp/(mZ*mZ))) * (2*Vu*Vu + 3*Vd*Vd + 5/16.)
	yden = 2*0.01*costhetaW*sinthetaW*(2*Vu+3*Vd);
	# print ynum,yden,x[0],math.sqrt(ynum/yden)
	if ynum > 0: ynum *= -1.;
	y = math.sqrt(ynum/yden);
	
	###
	y = math.sqrt( math.fabs(1-(mZp*mZp/(mZ*mZ))) )

	return y/6.;

def Zconstraints(x):
	
	# Zwidth = 2.4952;
	# ZwidthError = 0.0023*3; # times 3 to give 3 sigma
	# relZwidthUnc = ZwidthError/Zwidth;
	# sin2thetaW = 0.2312;
	# sinthetaW = math.sqrt(sin2thetaW);
	# costhetaW = math.sqrt(1 - sin2thetaW);
	# mW = 80.385;
	# vev = 246.;
	# g = mW*2./vev;
	# Vu = 0.25 - (4. * sin2thetaW / 6.);
	# Vd = -0.25 - (2. * sin2thetaW / 6.);
	# mZ = 91.18;
	# mZp = x[0];

	# # y = gZ
	# ynum = relZwidthUnc * 3 * g * -1. * math.fabs(1-(mZp*mZp/(mZ*mZ))) * (2*Vu*Vu + 3*Vd*Vd + 5/16.)
	# yden = 2*0.01*costhetaW*sinthetaW*(2*Vu+3*Vd);
	# # print ynum,yden,x[0],math.sqrt(ynum/yden)
	# y = math.sqrt(ynum/yden);
	# y *= 1.5;

	mZ = 91.18;
	mZp = x[0];
	ynum = 4. * math.sqrt( 4. * math.pi ) * 1.96 * 1.1e-3 * ( 1-(mZp*mZp/(mZ*mZ)) );
	yden = 1.193 * 0.02;
	if ynum < 0: ynum *= -1.;
	y = math.sqrt(ynum/yden);

	return y/6.;

########################################################################################
def main():
	
	# sigXS = [4.94,4.82,4.78,4.72,4.64,4.509,4.4,4.29]; # in pb
	# masses = [50,75,100,125,150,200,250,300];

	# sigXS = [4.94,4.82,4.78,4.72,4.64,4.509,4.4,4.29]; # in pb
	#sigXS  = [4.94,4.94,4.82,4.78,4.78,4.72,4.64,4.509,4.509,4.4,4.4,4.4,4.29]; # in pb
	# sXSgb1 = [1.939e+04,1.462e+04,9976,7870,5707,4254,3233,2320,1131, 620]
	# masses = [      100,      110, 125, 135, 150, 165, 180, 200, 250, 300];
	# sXSgb1 = [1.394e+05,4.481e+04,2.641e+04,1.939e+04,1.462e+04,9976,7870,5707,4254,3233,2320,1131, 620]
	# masses = [       50,       75,       90,      100,      110, 125, 135, 150, 165, 180, 200, 250, 300];
	#bsXSgb1 = [1.394e+05,8.419e+04,4.481e+04,2.641e+04,1.939e+04,1.462e+04,7870,5707,4254,3233,2320,1131, 620]
	#bmasses = [       50,       60,       75,       90,      100,      110, 135, 150, 165, 180, 200, 250, 300]
	#masses = []
	#sXSgb1 = []
	#lGraph = ROOT.TGraph(len(bmasses),array('d',bmasses),array('d',bsXSgb1))
	#for x in range(50,300,5):
	#if x == 200: continue;
	#if x > 260 and x < 280: continue;
	# if x > 160 and x < 170: continue;

	#masses.append(x)
	#sXSgb1.append(lGraph.Eval(x))
	bsXSgb1 = [1.394e+05,8.419e+04,4.481e+04,2.641e+04,1.939e+04,1.462e+04,7870,5707,4254,3233,2320,1131, 620]
        bmasses = [       50,       60,       75,       90,      100,      110, 135, 150, 165, 180, 200, 250, 300]
        masses = []
        sXSgb1 = []
        lGraph = ROOT.TGraph(len(bmasses),array('d',bmasses),array('d',bsXSgb1))
        for x in range(50,300,5):
                masses.append(x)
                sXSgb1.append(lGraph.Eval(x))

	#sXSgb1 = [1.394e+05,4.481e+04,1.939e+04,9976,5707,2320,1131,620]
	#masses = [       50,       75,      100, 125, 150, 200, 250,300];
	#sXSgb1 = [1.394e+05,4.481e+04,1.939e+04,9976,5707,2320]
	#masses = [       50,       75,      100, 125, 150, 200];
	KFACTOR = 1.218;
	idir = "results";

	#--------------------------------
	results = [];
	for i in range(len(masses)): 
		print str(masses[i])
                results.append( getAsymLimits('results7/ZQQ_%s/lim_34_results7limit.root' % ( str(masses[i])),'Zp'+str(masses[i])));


	names   = [];
	l_obs   = [];
	l_m2sig = [];
	l_m1sig = [];
	l_exp   = [];
	l_p1sig = [];
	l_p2sig = [];
	ctr = 0
	for r in results:
		names.append( "Zp"+str(masses[ctr]) );
		l_m2sig.append(r[1]);
		l_m1sig.append(r[2]);
		l_exp.append(r[3]);
		l_p1sig.append(r[4]);
		l_p2sig.append(r[5]);
		l_obs.append(r[0]);
		ctr+=1;

	lxs_obs   = [];
	lxs_m2sig = [];
	lxs_m1sig = [];
	lxs_exp   = [];
	lxs_p1sig = [];
	lxs_p2sig = [];
	for i,v in enumerate(sXSgb1):
		lxs_obs.append( l_obs[i]*v*KFACTOR );
		lxs_m2sig.append( l_m2sig[i]*v*KFACTOR );
		lxs_m1sig.append( l_m1sig[i]*v*KFACTOR );
		lxs_exp.append( l_exp[i]*v*KFACTOR );
		lxs_p1sig.append( l_p1sig[i]*v*KFACTOR );
		lxs_p2sig.append( l_p2sig[i]*v*KFACTOR );

	gr_mu_exp    = makeAGraph( masses, l_exp, 1, 2 );
	gr_mu_obs    = makeAGraph( masses, l_obs, 1, 1 );
	gr_mu_1sigma = makeAFillGraph( masses, l_m1sig, l_p1sig, 0, 3, 1001 );
	gr_mu_2sigma = makeAFillGraph( masses, l_m2sig, l_p2sig, 0, ROOT.kOrange, 1001 );

	gr_xs_exp    = makeAGraph( masses, lxs_exp, 1, 2 );
	gr_xs_obs    = makeAGraph( masses, lxs_obs, 1, 1 );
	gr_xs_1sigma = makeAFillGraph( masses, lxs_m1sig, lxs_p1sig, 0, 3, 1001 );
	gr_xs_2sigma = makeAFillGraph( masses, lxs_m2sig, lxs_p2sig, 0, ROOT.kOrange, 1001 );

	gr_xs_gb1d0    = makeAGraph( masses, [x*KFACTOR for x in sXSgb1], 4, 4 )
	gr_xs_gb0d5    = makeAGraph( masses, [x*0.25*KFACTOR for x in sXSgb1] , 4, 6 )

	# convert to g_B limits! 
	l_obs_gB = [];
	l_exp_gB = [];
	l_m2sig_gB = [];
	l_m1sig_gB = [];
	l_p1sig_gB = [];
	l_p2sig_gB = [];
	for i in range(len(l_exp)):
		l_obs_gB.append( math.sqrt(l_obs[i])/6. );
		l_exp_gB.append( math.sqrt(l_exp[i])/6. );
		l_m2sig_gB.append( math.sqrt(l_m2sig[i])/6. );
		l_m1sig_gB.append( math.sqrt(l_m1sig[i])/6. );
		l_p1sig_gB.append( math.sqrt(l_p1sig[i])/6. );
		l_p2sig_gB.append( math.sqrt(l_p2sig[i])/6. );

	gr_gB_exp    = makeAGraph( masses, l_exp_gB, 1, 2 );
	gr_gB_obs    = makeAGraph( masses, l_obs_gB, 1, 1 );
	gr_gB_1sigma = makeAFillGraph( masses, l_m1sig_gB, l_p1sig_gB, 0, 3, 1001 );
	gr_gB_2sigma = makeAFillGraph( masses, l_m2sig_gB, l_p2sig_gB, 0, ROOT.kOrange, 1001 );

	#--------------------------------
	addFactor=True;
	gr_UA2 = csvToGraph( "externDat/UA2.csv",4,addFactor);
	gr_CDFRun1 = csvToGraph( "externDat/CDF_Run1.csv",2,addFactor );
	gr_CDFRun2 = csvToGraph( "externDat/CDF_Run2.csv",6,addFactor );
	gr_ATLAS = csvToGraph( "externDat/gBMZB_ATLAS_all_fbinv.csv",7,False );
	gr_CMS = csvToGraph( "externDat/CMS_Scouting.csv",8,False );
	gr_ATLAS_isrphoton = csvToGraph( "externDat/ATLAS_Run2ISRPhoton.csv",2,False );
	gr_ATLAS_scouting = csvToGraph( "externDat/ATLAS_Run2Scouting.csv",4,False );
	gr_UA2.SetLineStyle(3);
	gr_CDFRun1.SetLineStyle(3);
	gr_CDFRun2.SetLineStyle(3);
	#--------------------------------


	Ufunc1 = ROOT.TF1('uni1','5',0,10000);
	Ufunc2 = ROOT.TF1('uni2','5',0,10000);

	Zfunc = ROOT.TF1('myfunc',Zconstraints,0,1000,0);
	Zfunc.SetNpx(1000) 
	Zfunc.SetLineColor(15);
	Zfunc.SetLineStyle(9);
	Zfunc.SetLineWidth(2);

	Upsfunc = ROOT.TF1('myfunc',Upsilonconstraints,0,1000,0);
	Upsfunc.SetNpx(1000) 
	Upsfunc.SetLineColor(30);
	Upsfunc.SetLineStyle(9);
	Upsfunc.SetLineWidth(2);

	#--------------------------------
	#--------------------------------
	#--------------------------------
	#--------------------------------
	#--------------------------------
	#--------------------------------
	#--------------------------------
	# PLOTTING
	lowlim = 40;

	txta = ROOT.TLatex(0.16,0.92,"CMS");
	txta.SetNDC();
	txtb = ROOT.TLatex(0.24,0.92,"Preliminary");
	txtb.SetNDC(); txtb.SetTextFont(52);
	txtc = ROOT.TLatex(0.68,0.92,"35.9 fb^{-1} (13 TeV)");
	txtc.SetNDC(); txtc.SetTextFont(42); txtc.SetTextSize(0.04);
	txtd = ROOT.TLatex(0.60,0.80,"g_{B} = 1 or g_{q} = 1/6");
	txtd.SetNDC(); txtd.SetTextFont(42); txtd.SetTextSize(0.04);

	leg = ROOT.TLegend(0.20,0.65,0.4,0.85);
	leg.SetFillStyle(1001);
	leg.SetFillColor(0);    
	leg.SetBorderSize(1);  
	leg.AddEntry(gr_mu_obs,"Observed","l")
	leg.AddEntry(gr_mu_exp,"Expected","l")
	leg.AddEntry(gr_mu_1sigma,"#pm 1 std. deviation","f")	
	leg.AddEntry(gr_mu_2sigma,"#pm 2 std. deviation","f")
	

	legbb = ROOT.TLegend(0.45,0.55,0.90,0.85);
	legbb.SetFillStyle(1001);
	legbb.SetFillColor(0);    
	legbb.SetBorderSize(0);  
	legbb.SetTextSize(0.040);
	legbb.SetTextFont(42);
	legbb.AddEntry(gr_mu_obs,"Observed","l")
	legbb.AddEntry(gr_mu_exp,"Expected","l")
	legbb.AddEntry(gr_mu_1sigma,"#pm 1 std. deviation","f")	
	legbb.AddEntry(gr_mu_2sigma,"#pm 2 std. deviation","f")
	legbb.AddEntry(gr_xs_gb0d5,"theory, g_{q} = 0.17","l")	
	legbb.AddEntry(gr_xs_gb1d0,"theory, g_{q} = 0.08","l")	

	can_mu = ROOT.TCanvas("can_mu","can_mu",1200,800);
	hrl = can_mu.DrawFrame(lowlim,0,320,3);
	hrl.GetYaxis().SetTitle("#mu = #sigma_{95%CL}/#sigma_{th}");
	hrl.GetYaxis().SetTitleOffset(0.85);
	hrl.GetXaxis().SetTitle("Z\' mass (GeV)");
	gr_mu_2sigma.Draw('f');
	gr_mu_1sigma.Draw('fsames');
	gr_mu_obs.Draw('Csames');
	gr_mu_exp.Draw('Csames');

	txta.Draw();
	txtb.Draw();
	txtc.Draw();
	txtd.Draw();
	leg.Draw();

	can_mu.SaveAs('plots/mu.pdf');

	can_XS = ROOT.TCanvas("can_XS","can_XS",1000,800);
	hrlxs = can_mu.DrawFrame(lowlim,200,320,100000) ;
	hrlxs.GetYaxis().SetTitle("#sigma_{95% CL} (pb)");
	hrlxs.GetYaxis().SetTitleOffset(0.85);
	hrlxs.GetXaxis().SetTitle("Z\' mass (GeV)");
	gr_xs_2sigma.Draw('f');
	gr_xs_1sigma.Draw('fsames');
	gr_xs_obs.Draw('Csames');
	gr_xs_exp.Draw('Csames');
	gr_xs_gb0d5.Draw("lsames");
	gr_xs_gb1d0.Draw("lsames");

	txta.Draw();
	# txtb.Draw();
	txtc.Draw();
	legbb.Draw();
	ROOT.gPad.SetLogy();
	can_XS.SaveAs('plots/xslim.pdf');
	#--------------------------------

	leg2 = ROOT.TLegend(0.13,0.60,0.50,0.88);
	leg2.SetFillStyle(0);
	leg2.SetFillColor(10);    
	leg2.SetBorderSize(0);
	leg2.SetTextFont(42);  
	leg2.SetTextSize(0.029);  
	# leg2.AddEntry(gr_mu_exp,"expected","l")
	# leg2.AddEntry(gr_mu_obs,"observed","l")
	# leg2.AddEntry(gr_mu_2sigma,"expected 2#sigma","f")
	# leg2.AddEntry(gr_mu_1sigma,"expected 1#sigma","f")	
	leg2.AddEntry(gr_UA2,"UA2","l")	
	leg2.AddEntry(gr_CDFRun1,"CDF Run 1","l")	
	leg2.AddEntry(gr_CDFRun2,"CDF Run 2","l")	
	leg2.AddEntry(gr_ATLAS,"ATLAS 13 #oplus 20.3  fb^{-1}","l")
	leg2.AddEntry(gr_ATLAS_isrphoton,"ATLAS 13 #oplus 3.2 fb^{-1} (ISR #gamma)","l")
	leg2.AddEntry(gr_ATLAS_scouting,"ATLAS 13 #oplus 3.2 fb^{-1} (TLA)","l")
	leg2.AddEntry(gr_CMS,"CMS 8 #oplus 18.8 fb^{-1} (Scouting)","l")
	leg2.AddEntry(Zfunc,"Z Width (indirect)","l")
	# leg2.AddEntry(Upsfunc,"#Upsilon Width","l")

	leg2b = ROOT.TLegend(0.5,0.15,0.85,0.30);
	leg2b.SetFillStyle(0);
	leg2b.SetFillColor(10);    
	leg2b.SetBorderSize(0);
	leg2b.SetTextFont(42);  
	leg2b.SetTextSize(0.035);  
	leg2b.AddEntry(gr_mu_obs,"Observed","l")	
	leg2b.AddEntry(gr_mu_exp,"Expected","l")
	leg2b.AddEntry(gr_mu_1sigma,"#pm 1 std. deviation","f")	
	leg2b.AddEntry(gr_mu_2sigma,"#pm 2 std. deviation","f")

	leg3 = ROOT.TLegend(0.50,0.6,0.95,0.85);
	leg3.SetFillStyle(0);
	leg3.SetFillColor(0);    
	leg3.SetBorderSize(0);  
	leg3.SetTextFont(42);  
	leg3.SetTextSize(0.035);  	
	leg3.AddEntry(gr_mu_exp,"expected","l")
	leg3.AddEntry(gr_mu_obs,"observed","l")
	leg3.AddEntry(gr_mu_2sigma,"expected 2#sigma","f")
	leg3.AddEntry(gr_mu_1sigma,"expected 1#sigma","f")	
	leg3.AddEntry(gr_UA2,"UA2","l")	
	leg3.AddEntry(gr_CDFRun1,"CDF Run 1","l")	
	leg3.AddEntry(gr_CDFRun2,"CDF Run 2","l")	
	leg3.AddEntry(gr_ATLAS,"ATLAS 13 #oplus 20.3  fb^{-1}","l")	
	leg3.AddEntry(gr_ATLAS_isrphoton,"ATLAS 13 #oplus 3.2 fb^{-1} (ISR #gamma)","l")
	leg3.AddEntry(gr_ATLAS_scouting,"ATLAS 13 #oplus 3.2 fb^{-1} (TLA)","l")
	leg3.AddEntry(gr_CMS,"CMS 8 #oplus 18.8 fb^{-1} (Scouting)","l")

	###---------- gB stuff -----------------
	###---------- gB stuff -----------------



	can_gB = ROOT.TCanvas("can_gB","can_gB",900,800);
	hrl = can_gB.DrawFrame(lowlim,0,300,0.5);
	hrl.GetYaxis().SetTitle("coupling, g_{q}");
	hrl.GetYaxis().SetTitleOffset(0.85);
	hrl.GetXaxis().SetTitle("Z\' mass (GeV)");
	
	gr_gB_2sigma.Draw('f');
	gr_gB_1sigma.Draw('fsames');
	gr_gB_obs.Draw('lsames');
	gr_gB_exp.Draw('csames');

	gr_UA2.Draw("csames")
	gr_CDFRun1.Draw("csames")
	gr_CDFRun2.Draw("csames")
	gr_ATLAS.Draw("csames")
	gr_ATLAS_isrphoton.Draw("csames")
	gr_ATLAS_scouting.Draw("csames")	
	gr_CMS.Draw("csames")
	Zfunc.Draw("sames");

	txta.Draw();
	txtb.Draw();
	txtc.Draw();
	# txtd.Draw();
	leg3.Draw();

	gr_gB_2sigma.GetXaxis().SetMoreLogLabels(True);	
	gr_gB_2sigma.GetXaxis().SetNdivisions(10);	

	# ROOT.gPad.SetLogx();
	can_gB.SaveAs('plots/gB.pdf');

	#####

	can_gB2 = ROOT.TCanvas("can_gB2","can_gB2",1000,800);
	hrl2 = can_gB.DrawFrame(40,0.05,1201,01.0);
	hrl2.GetYaxis().SetTitle("coupling, g_{q}");
	hrl2.GetYaxis().SetTitleOffset(0.85);	
	hrl2.GetXaxis().SetTitle("Z\' mass (GeV)");
	
	# Zfunc.SetFillStyle(1001)
	# Zfunc.SetFillColor(10);
	# Upsfunc.SetFillStyle(1001)
	# Upsfunc.SetFillColor(10);
	# Ufunc1.SetFillStyle(1001)
	# Ufunc1.SetFillColor(1);
	# Ufunc2.SetFillStyle(1001)
	# Ufunc2.SetFillColor(2);
	# Ufunc1.Draw("sames");
	
	# Upsfunc.Draw("sames");
	# Ufunc2.Draw("fillsames");
	Zfunc.Draw("sames");
	
	gr_gB_2sigma.Draw('fsames');
	gr_gB_1sigma.Draw('fsames');
	gr_gB_obs.Draw('csames');
	gr_gB_exp.Draw('csames');

	gr_UA2.Draw("csames")
	gr_CDFRun1.Draw("csames")
	gr_CDFRun2.Draw("csames")
	gr_ATLAS.Draw("csames")
	gr_ATLAS_isrphoton.Draw("csames")
	gr_ATLAS_scouting.Draw("csames")
	gr_CMS.Draw("csames")

	txta.Draw();
	# txtb.Draw();
	txtc.Draw();
	# txtd.Draw();
	leg2.Draw();
	leg2b.Draw();

	hrl2.GetXaxis().SetMoreLogLabels(True);	
	hrl2.GetXaxis().SetNdivisions(10);	
	hrl2.GetXaxis().SetNoExponent(True);	
	hrl2.GetYaxis().SetMoreLogLabels(True);	
	hrl2.GetYaxis().SetNdivisions(10);	
	hrl2.GetYaxis().SetNoExponent(True);	

	ROOT.gPad.SetLogx();
	ROOT.gPad.SetLogy();
	can_gB2.SaveAs('plots/gB_logx.pdf');

	###---------- gB stuff -----------------
	###---------- gB stuff -----------------



########################################################################################
########################################################################################

def makeAGraph(listx,listy,linecolor = 1, linestyle = 1):

	a_m = array('d', []);
	a_g = array('d', []);

	for i in range(len(listx)):
		a_m.append(listx[i]);
		a_g.append(listy[i]);

	gr = ROOT.TGraph(len(listx),a_m,a_g);

	gr.SetLineColor(linecolor)
	gr.SetLineStyle(linestyle)
	gr.SetLineWidth(4)

	return gr

def makeAFillGraph(listx,listy1,listy2,linecolor = 1, fillcolor = 0, fillstyle = 0):

	a_m = array('d', []);
	a_g = array('d', []);

	for i in range(len(listx)):
		a_m.append(listx[i]);
		a_g.append(listy1[i]);
	
	for i in range(len(listx)-1,-1,-1):
		a_m.append(listx[i]);
		a_g.append(listy2[i]);

	gr = ROOT.TGraph(2*len(listx),a_m,a_g);

	gr.SetLineColor(linecolor)
	gr.SetFillColor(fillcolor)
	gr.SetFillStyle(fillstyle)

	return gr

def csvToGraph(fn, linecolor=1, addFactor=False):

	factor = 1.;
	if addFactor: factor = 6.;

	a_m = array('d', []);
	a_g = array('d', []);

	ifile = open(fn,'r');
	npoints = 0;
	for line in ifile: 
		lline = line.strip().split(',');
		a_m.append(float(lline[0]))
		a_g.append(float(lline[1])*factor/6.)
		npoints += 1;

	gr = ROOT.TGraph(npoints,a_m,a_g);
	gr.SetLineColor(linecolor);
	gr.SetLineWidth(2);

	return gr


########################################################################################
########################################################################################
def getAsymLimits(fname,tag):

	lims = [0]*6;
	
	f = ROOT.TFile(fname);
	t = f.Get("limit");

	#if not t.GetListOfKeys().Contains("limit"): 
	if not t: 
		print "file is corrupted";
		return lims

	entries = t.GetEntries();
	for i in range(entries):

		t.GetEntry(i);
		t_quantileExpected = t.quantileExpected;
		t_limit = t.limit;

		#print "limit: ", t_limit, ", quantileExpected: ",t_quantileExpected;
		
		if t_quantileExpected == -1.: lims[0] = t_limit;
		elif t_quantileExpected >= 0.024 and t_quantileExpected <= 0.026: lims[1] = t_limit;
		elif t_quantileExpected >= 0.15 and t_quantileExpected <= 0.17: lims[2] = t_limit;            
		elif t_quantileExpected == 0.5: lims[3] = t_limit;            
		elif t_quantileExpected >= 0.83 and t_quantileExpected <= 0.85: lims[4] = t_limit;
		elif t_quantileExpected >= 0.974 and t_quantileExpected <= 0.976: lims[5] = t_limit;
		else: print "Unknown quantile!"

	print "lims = ", lims
	return lims;

if __name__ == '__main__':

	main();
