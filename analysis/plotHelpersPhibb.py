import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory, TVirtualFitter
import math
import sys
from math import sqrt
import time
import array


def getRatio(hist, reference):
	ratio = hist.Clone("%s_ratio"%hist.GetName())
	ratio.SetDirectory(0)
	ratio.SetLineColor(hist.GetLineColor())
	for xbin in xrange(1,reference.GetNbinsX()+1):
		ref = reference.GetBinContent(xbin)
		val = hist.GetBinContent(xbin)

		refE = reference.GetBinError(xbin)
		valE = hist.GetBinError(xbin)

		try:
			ratio.SetBinContent(xbin, val/ref)
			ratio.SetBinError(xbin, math.sqrt( (val*refE/(ref**2))**2 + (valE/ref)**2 ))
		except ZeroDivisionError:
			ratio.SetBinContent(xbin, 1.0)
			ratio.SetBinError(xbin, 0.0)

	return ratio


def getSoverRootB(hs, hallMC, iBin):
  bb=0.
  ss=0.
  for i in range(iBin, hallMC.GetNbinsX()):
      bb+=hallMC.GetBinContent(i)
      ss+=hs.GetBinContent(i)
  if bb > 0 :
    return ss/sqrt(bb)
  else:
    return 0.


def customSort(dictValue):
    (k, v) = dictValue
    if 'DY' in k:
        return 0
    elif 'W' in k:
        return -1
    elif 'Diboson' in k or 'VV' in k:
        return -2
    elif 'TTbar' in k:
        return -3
    elif 'ST' in k or 'SingleTop' in k:
        return -4
    elif 'QCD' in k:
        return -5
    else:
        return -v.Integral() #negative integral



def makeCanvas(hists,normalize=False,odir = "plots"):

	color = [1,2,4,6,7,8,3,4,1,1,7,8]
	style = [1,2,2,2,1,2,2,2,2,1,1,1]
	options = ["hist",
			   "histsames",
			   "histsames",
			   "histsames",
			   "histsames",
			   "histsames",
			   "histsames",
			   "histsames",
			   "histsames",
			   "histsames",
			   "histsames",
			   "histsames",
			   "histsames"]

	c = ROOT.TCanvas("c"+hists[0].GetName(),"c"+hists[0].GetName(),1000,800);

	max = -999;

	for i in range(len(hists)):
		hists[i].SetLineColor(color[i])
		hists[i].SetMarkerColor(color[i])
		hists[i].SetMarkerStyle(20)
		hists[i].SetLineStyle(style[i])
		hists[i].SetLineWidth(2)

		if hists[i].GetMaximum() > max: 
			max = hists[i].GetMaximum();
			hists[0].SetMaximum(max*1.25);
		if normalize and hists[i].Integral() > 0: hists[i].Scale(1./hists[i].Integral())

		hists[i].Draw(options[i]);

	c.SaveAs(odir+hists[0].GetName()+".pdf")
	ROOT.gPad.SetLogy();
	c.SaveAs(odir+hists[0].GetName()+"_log.pdf")

def makeCanvasDataMC(hd,hmcs,legname,name,pdir="plots",nodata=False):
	
    color = [ROOT.kBlue,ROOT.kGreen+1,ROOT.kCyan,ROOT.kViolet,ROOT.kBlack,ROOT.kRed,5,2,4,6,7,8,3,5,2,4,6,7,8,3,5]
    style = [1,2,5,6,7,1,1,2,2,2,2,2,2,2,3,3,3,3,3,3,3]
    for h in range(len(hmcs)): 
        hmcs[h].SetFillStyle(1001)
        hmcs[h].SetLineStyle(style[h])
        hmcs[h].SetLineColor(color[h])
        hmcs[h].SetFillColor(color[h])

    hstack = ROOT.THStack("hstack","hstack");
    for h in hmcs: hstack.Add(h);
    fullmc = hstack.GetStack().Last();

    # normalize MC to data
    scalefactor = hd.Integral()/fullmc.Integral();
    print "data/mc scale factor = ", scalefactor
    for i in range(len(hmcs)): hmcs[i].Scale( scalefactor );

    xtitle = hmcs[0].GetXaxis().GetTitle();
    ytitle = hmcs[0].GetYaxis().GetTitle();
    hstack2 = ROOT.THStack("hstack2",";"+xtitle+";"+ytitle+";");
    for h in hmcs: hstack2.Add(h);

    maxval = 2.*max(hstack2.GetStack().Last().GetMaximum(),hd.GetMaximum())
    # print maxval;
    leg = ROOT.TLegend(0.6,0.7,0.9,0.9);
    leg.SetFillStyle(0);
    leg.SetBorderSize(0);
    leg.SetTextSize(0.035);
    leg.AddEntry(hd,"data","pe");
    for i in range(len(hmcs)):
        leg.AddEntry(hmcs[i],legname[i],"f")
    # print hstack2.GetStack().Last().Integral(), hstack.GetStack().Last().Integral(),hd.Integral()
    # print hstack2.GetStack().Last().GetMaximum(),hd.GetMaximum())

    tag1 = ROOT.TLatex(0.7,0.95,"30 fb^{-1} (13 TeV)")
    tag1.SetNDC();
    tag1.SetTextFont(42)
    tag1.SetTextSize(0.045);
    tag2 = ROOT.TLatex(0.17,0.95,"CMS Preliminary")
    tag2.SetNDC();
    tag2.SetTextSize(0.045);

    c = ROOT.TCanvas("c"+name,"c"+name,1000,800);
    p2 = ROOT.TPad("pad2","pad2",0,0,1,0.31);
    p2.SetTopMargin(0);
    p2.SetBottomMargin(0.3);
    p2.SetLeftMargin(0.15)
    p2.SetRightMargin(0.03)
    p2.SetFillStyle(0);
    p2.Draw();
    p1 = ROOT.TPad("pad1","pad1",0,0.31,1,1);
    p1.SetBottomMargin(0);
    p1.SetLeftMargin(p2.GetLeftMargin())
    p1.SetRightMargin(p2.GetRightMargin())
    p1.Draw();
    p1.cd();

    mainframe = hmcs[0].Clone('mainframe')
    mainframe.Reset('ICE')
    mainframe.GetXaxis().SetTitleFont(43)
    mainframe.GetXaxis().SetLabelFont(43)
    mainframe.GetYaxis().SetTitleFont(43)
    mainframe.GetYaxis().SetLabelFont(43)
    mainframe.GetYaxis().SetTitle('Events')
    mainframe.GetYaxis().SetLabelSize(22)
    mainframe.GetYaxis().SetTitleSize(26)
    mainframe.GetYaxis().SetTitleOffset(2.0)
    mainframe.GetXaxis().SetTitle('')
    mainframe.GetXaxis().SetLabelSize(0)
    mainframe.GetXaxis().SetTitleSize(0)
    mainframe.GetXaxis().SetTitleOffset(1.5)
    mainframe.GetYaxis().SetNoExponent()
    mainframe.Draw()

    if nodata:
        hstack.SetMaximum(maxval);
        hstack.Draw("hist");
    else:
        hstack2.SetMaximum(maxval);
        hstack2.Draw("hist");
        hd.Draw("pesames");
    # ROOT.gPad.Update();
    # hstack2.GetXaxis.SetTitle( hmcs[0].GetXaxis().GetTitle() );
    # hstack2.GetYaxis.SetTitle( hmcs[0].GetYaxis().GetTitle() );	
    leg.Draw();
    tag1.Draw();
    tag2.Draw();

    p2.cd()
    ratioframe = mainframe.Clone('ratioframe')
    ratioframe.Reset('ICE')
    ratioframe.GetYaxis().SetRangeUser(0.50,1.50)
    ratioframe.GetYaxis().SetTitle('Data/MC')
    ratioframe.GetXaxis().SetTitle(hmcs[0].GetXaxis().GetTitle())
    ratioframe.GetXaxis().SetLabelSize(22)
    ratioframe.GetXaxis().SetTitleSize(26)
    ratioframe.GetYaxis().SetNdivisions(5)
    ratioframe.GetYaxis().SetNoExponent()
    ratioframe.GetYaxis().SetTitleOffset(mainframe.GetYaxis().GetTitleOffset())
    ratioframe.GetXaxis().SetTitleOffset(3.0)
    ratioframe.Draw()

    ## Calculate Ratios
    ratios = []
    ratios.append(getRatio(hd, fullmc))
    ratios[0].SetMinimum(0)
    ratios[0].SetMaximum(2)
    ratioframe.GetYaxis().SetRangeUser(0,2)

    line = ROOT.TLine(ratios[0].GetXaxis().GetXmin(), 1.0,
                      ratios[0].GetXaxis().GetXmax(), 1.0)
    line.SetLineColor(ROOT.kGray)
    line.SetLineStyle(2)
    line.Draw()

    ratios[0].Draw("P same")

    c.cd()
    c.Modified()
    c.Update()        
    c.SaveAs(pdir+"/"+name+".pdf")
    c.SaveAs(pdir+"/"+name+".png")

    p1.cd()
    ROOT.gPad.SetLogy()
    hstack.SetMinimum(0.1)
    c.SaveAs(pdir+"/"+name+"_log.pdf")
    c.SaveAs(pdir+"/"+name+"_log.png")

    c.Close()

##################################################################################################
def makeCanvasDataMC_wpred(hd,gpred,hmcs,legname,name,pdir="plots",blind=True):
	
	print "makeCanvasDataMC_wpred---"
	# print "hd integral = ",hd.Integral();
	gpred.SetLineColor(2);
	gpred.SetFillColor(2);
	gpred.SetFillStyle(3001);

	color = [2,4,6,7,8,3,5]
	for h in range(len(hmcs)): 
		hmcs[h].SetFillStyle(0);
		hmcs[h].SetLineColor(4);
		hmcs[h].SetFillColor(0)

	hstack = ROOT.THStack("hstack","hstack");
	for h in hmcs: hstack.Add(h);
	fullmc = hstack.GetStack().Last();

	# normalize MC to data
	scalefactor = hd.Integral()/fullmc.Integral();
	for i in range(len(hmcs)): hmcs[i].Scale( scalefactor );

	xtitle = hmcs[0].GetXaxis().GetTitle();
	ytitle = hmcs[0].GetYaxis().GetTitle();
	hstack2 = ROOT.THStack("hstack2",";"+xtitle+";"+ytitle+";");
	for h in hmcs: hstack2.Add(h);

	# print maxval;
	leg = ROOT.TLegend(0.6,0.7,0.9,0.9);
	leg.SetFillStyle(0);
	leg.SetBorderSize(0);
	leg.SetTextSize(0.035);
	leg.AddEntry(hd,"data","pe");
	leg.AddEntry(gpred,"bkg pred.","f");
	for i in range(len(hmcs)):
		leg.AddEntry(hmcs[i],legname[i],"f")
	# print hstack2.GetStack().Last().Integral(), hstack.GetStack().Last().Integral(),hd.Integral()
	# print hstack2.GetStack().Last().GetMaximum(),hd.GetMaximum())

	tag1 = ROOT.TLatex(0.7,0.95,"0.46 fb^{-1} (13 TeV)")
	tag1.SetNDC();
	tag1.SetTextSize(0.035);
	tag2 = ROOT.TLatex(0.17,0.95,"CMS preliminary")
	tag2.SetNDC();
	tag2.SetTextSize(0.035);

	gpred.SetMarkerStyle(24);
	gpred.SetMarkerColor(2);

	#---------------------------------------------------------------
	c = ROOT.TCanvas("c"+name,"c"+name,1000,800);
	
	p1 = ROOT.TPad("p1","p1",0.0,0.3,1.0,1.0);
	p2 = ROOT.TPad("p2","p2",0.0,0.0,1.0,0.3);
	p1.SetBottomMargin(0.05);
	p2.SetTopMargin(0.05);
	p2.SetBottomMargin(0.3);

	c.cd();
	p1.Draw(); p1.cd();

	mcall = hstack2.GetStack().Last()
	maxval = 2.*max(mcall.GetMaximum(),hd.GetMaximum());
	hd.SetLineColor(1);
	mcall.SetLineColor(4);
	if not blind: 
		mcall.SetMaximum(maxval);
		mcall.Draw("hist");
		hd.Draw("pesames");
		gpred.Draw("2");
		mcall.Draw("histsames");
		hd.Draw("pesames");
		hd.SetMinimum(0);
	if blind: 
		mcall.SetMaximum(maxval);
		mcall.Draw("hist");
		gpred.Draw("2");
		mcall.Draw("histsames");
		mcall.SetMinimum(0);

	mcall.GetXaxis().SetTitle("");
	# ROOT.gPad.Update();
	# hstack2.GetXaxis.SetTitle( hmcs[0].GetXaxis().GetTitle() );
	# hstack2.GetYaxis.SetTitle( hmcs[0].GetYaxis().GetTitle() );	
	leg.Draw();
	tag1.Draw();
	tag2.Draw();

	c.cd();
	p2.Draw(); p2.cd();
	p2.SetGrid();

	hdOvPred = hd.Clone();
	hpred = gpred.GetHistogram();
	hdOvPred.SetMaximum(2);
	hdOvPred.SetMinimum(0);
	for i in range(hd.GetNbinsX()):

		# print "bin ", i, ", ", hd.GetBinContent(i+1),hpred.GetBinContent(i+1),gpred.GetY()[i]
		if gpred.GetY()[i] > 0:
			hdOvPred.SetBinContent( i+1, hd.GetBinContent(i+1)/gpred.GetY()[i] );
		else:
			hdOvPred.SetBinContent( i+1, 0. );		
	
	hdOvPred.GetXaxis().SetTitle("jet mass (GeV)"); 
	hdOvPred.GetXaxis().SetTitleSize(0.14);
	hdOvPred.GetYaxis().SetTitle("Data/MC"); 
	hdOvPred.GetYaxis().SetTitleSize(0.14); 
	hdOvPred.GetYaxis().SetTitleOffset(0.42);	
	hdOvPred.Draw('hist');

	c.SaveAs(pdir+"/"+name+".pdf");
	#---------------------------------------------------------------
	mcall.SetMinimum(0.1);
	p1.cd();
	p1.SetLogy();
	c.SaveAs(pdir+"/"+name+"_log.pdf")	

##################################################################################################
def makeCanvasDataMC_MONEY(hd,gpred,hmcs,legname,name,pdir="plots",blind=True):
	
	print "makeCanvasDataMC_wpred---"
	print "hd integral = ",hd.Integral();

	gpred.SetLineColor(2);
	gpred.SetFillColor(2);
	gpred.SetFillStyle(3001);

	color = [2,4,6,7,8,3,5]
	for h in range(len(hmcs)): 
		hmcs[h].SetLineWidth(2);
		hmcs[h].SetLineColor(color[h])

	# build total stack
	hTotSM = hd.Clone();
	## for i in range(hd.GetNbinsX()):
	## 	hTotSM.SetBinContent(i+1, gpred.GetY()[i]+hmcs[0].GetBinContent(i+1)+hmcs[1].GetBinContent(i+1) );
	## 	# FinalErrorsVis = 0; 
	## 	# FinalErrorsVis += gpred.GetY()[i]*gpred.GetY()[i];		
	## 	# hTotSM.SetBinContent(i+1, gpred.GetY()[i]+hmcs[0].GetBinContent(i+1)+hmcs[1].GetBinContent(i+1)  );
	hTotSM.SetLineColor(ROOT.kGreen+2);
	hTotSM.SetLineWidth(2);
	hTotSM.GetYaxis().SetTitle("Events");
	
	# print maxval;
	leg = ROOT.TLegend(0.6,0.65,0.9,0.9);
	leg.SetFillStyle(0);
	leg.SetBorderSize(0);
	leg.SetTextSize(0.035);
	leg.AddEntry(hd,"data","pe");
	leg.AddEntry(hTotSM,"Total SM", "l");
	leg.AddEntry(gpred,"QCD pred.","f");
	for i in range(len(hmcs)):
		leg.AddEntry(hmcs[i],legname[i],"l")

	tag1 = ROOT.TLatex(0.7,0.95,"0.46 fb^{-1} (13 TeV)")
	tag1.SetNDC();
	tag1.SetTextSize(0.033);
	tag1.SetTextFont(52);
	txta = ROOT.TLatex(0.2,0.95,"CMS");
	txta.SetNDC();
	txtb = ROOT.TLatex(0.24,0.95,"Simulation Preliminary");
	txtb.SetNDC(); txtb.SetTextFont(52);
	txta.SetTextSize(0.033);
	txtb.SetTextSize(0.033);

	gpred.SetMarkerStyle(24);
	gpred.SetMarkerColor(2);

	#---------------------------------------------------------------
	c = ROOT.TCanvas("c"+name,"c"+name,1000,800);

	p1 = ROOT.TPad("p1","p1",0.0,0.3,1.0,1.0);
	p2 = ROOT.TPad("p2","p2",0.0,0.0,1.0,0.3);
	p1.SetBottomMargin(0.05);
	p2.SetTopMargin(0.05);
	p2.SetBottomMargin(0.3);

	c.cd();
	p1.Draw(); p1.cd();

	hTotSM.SetMaximum( hTotSM.GetMaximum()*1.2 );
	hTotSM.Draw("hist");
	if not blind: hd.Draw("pesames");
	gpred.Draw('2');
	for i in range(len(hmcs)):
		hmcs[i].Draw("histsames");

	leg.Draw();
	tag1.Draw();
	txta.Draw();
	txtb.Draw();

	c.cd();
	p2.Draw(); p2.cd();	
	p2.SetGrid();

	hdOvPred = hd.Clone();
	hdOvPred.SetMaximum(2);
	hdOvPred.SetMinimum(0);
	one_x = []
	one_y = []
	one_ex = []
	one_ey = []
	for i in range(hd.GetNbinsX()):

		if hd.GetBinContent(i+1) > 0:
			hdOvPred.SetBinContent( i+1, hd.GetBinContent(i+1)/hTotSM.GetBinContent(i+1) );
			errdat = hd.GetBinError(i+1)/hd.GetBinContent(i+1);
			errtot = math.sqrt(errdat*errdat)
			hdOvPred.SetBinError( i+1, errtot );
		else:
			hdOvPred.SetBinContent( i+1, 0. );		
			hdOvPred.SetBinError( i+1, 0. );		

	## 	one_x.append( hd.GetXaxis().GetBinCenter(i+1) );		
	## 	one_ex.append(  hd.GetXaxis().GetBinWidth(i+1) );
	## 	if gpred.GetY()[i] > 0:
	## 		one_y.append( 1. );
	## 		errmc  = gpred.GetEY()[i]/gpred.GetY()[i];
	## 		one_ey.append( errmc );
	## 	else:
	## 		one_y.append( 0 );
	## 		one_ey.append( 0 );

	hdOvPred.GetXaxis().SetTitle("jet mass (GeV)"); 
	hdOvPred.GetXaxis().SetTitleSize(0.14);
	hdOvPred.GetYaxis().SetTitle("Data/MC"); 
	hdOvPred.GetYaxis().SetTitleSize(0.14); 
	hdOvPred.GetYaxis().SetTitleOffset(0.42);	
	hdOvPred.Draw('pe');	

	## grrat = ROOT.TGraphErrors(len(one_x),array.array('d',one_x),array.array('d',one_y),array.array('d',one_ex),array.array('d',one_ey) );
	## grrat.SetLineColor(2);
	## grrat.SetFillColor(2);
	## grrat.SetFillStyle(3001);
	## grrat.Draw('2');
	c.SaveAs(pdir+"/"+name+".pdf");
	#---------------------------------------------------------------
	#---------------------------------------------------------------
	c2 = ROOT.TCanvas("c2"+name,"c2"+name,1000,800);

	p12 = ROOT.TPad("p12","p12",0.0,0.3,1.0,1.0);
	p22 = ROOT.TPad("p22","p22",0.0,0.0,1.0,0.3);
	p12.SetBottomMargin(0.05);
	p22.SetTopMargin(0.05);
	p22.SetBottomMargin(0.3);

	c2.cd();
	p12.Draw(); p12.cd();

	hTotSM.SetMaximum( hTotSM.GetMaximum()*2 );
	hTotSM.SetMinimum( 0.001 );
	hd.SetMaximum( hTotSM.GetMaximum()*2 );
	hd.SetMinimum( 0.001 );

	hd.Draw("histpe");
	hTotSM.Draw("histsames");
	gpred.Draw('2');
	for i in range(len(hmcs)):
		hmcs[i].Draw("histsames");

	leg.Draw();
	tag1.Draw();
	txta.Draw();
	txtb.Draw();
	p12.SetLogy();

	c2.cd();
	p22.Draw(); p22.cd();	
	p22.SetGrid();

	hdOvPred = hd.Clone();
	hdOvPred.SetMaximum(2);
	hdOvPred.SetMinimum(0);
	one_x = []
	one_y = []
	one_ex = []
	one_ey = []
	for i in range(hd.GetNbinsX()):

		if hd.GetBinContent(i+1) > 0:
			hdOvPred.SetBinContent( i+1, hd.GetBinContent(i+1)/hTotSM.GetBinContent(i+1) );
			errdat = hd.GetBinError(i+1)/hd.GetBinContent(i+1);
			errtot = math.sqrt(errdat*errdat)
			hdOvPred.SetBinError( i+1, errtot );
		else:
			hdOvPred.SetBinContent( i+1, 0. );		
			hdOvPred.SetBinError( i+1, 0. );		

	## 	one_x.append( hd.GetXaxis().GetBinCenter(i+1) );		
	## 	one_ex.append(  hd.GetXaxis().GetBinWidth(i+1) );
	## 	if gpred.GetY()[i] > 0:
	## 		one_y.append( 1. );
	## 		errmc  = gpred.GetEY()[i]/gpred.GetY()[i];
	## 		one_ey.append( errmc );
	## 	else:
	## 		one_y.append( 0 );
	## 		one_ey.append( 0 );

	hdOvPred.GetXaxis().SetTitle("jet mass (GeV)"); 
	hdOvPred.GetXaxis().SetTitleSize(0.14);
	hdOvPred.GetYaxis().SetTitle("Data/MC"); 
	hdOvPred.GetYaxis().SetTitleSize(0.14); 
	hdOvPred.GetYaxis().SetTitleOffset(0.42);	
	hdOvPred.Draw('pe');
	

	## grrat = ROOT.TGraphErrors(len(one_x),array.array('d',one_x),array.array('d',one_y),array.array('d',one_ex),array.array('d',one_ey) );
	## grrat.SetLineColor(2);
	## grrat.SetFillColor(2);
	## grrat.SetFillStyle(3001);
	## grrat.Draw('2');
	c2.SaveAs(pdir+"/"+name+"_log.pdf");

##################################################################################################
def makeCanvasShapeComparison(hs,legname,name,pdir="plots"):

	color = [2,4,6,7,8,3,5,2,4,6,7,8,3,5,2,4,6,7,8,3,5]
	style = [1,1,1,1,1,1,1,2,2,2,2,2,2,2,3,3,3,3,3,3,3]
	
	leg = ROOT.TLegend(0.6,0.5,0.9,0.9);
	leg.SetFillStyle(0);
	leg.SetBorderSize(0);
	leg.SetTextSize(0.035);

	maxval = -99;
	for h in range(len(hs)): 
		hs[h].SetLineColor(color[h]);
		hs[h].SetLineStyle(style[h]);
		hs[h].SetLineWidth(2);
		hs[h].SetFillStyle(0);
		if hs[h].Integral() > 0: hs[h].Scale(1./hs[h].Integral());
		if hs[h].GetMaximum() > maxval: maxval = hs[h].GetMaximum();
		leg.AddEntry(hs[h],legname[h],"l");

	tag2 = ROOT.TLatex(0.2,0.90,"CMS preliminary")
	tag2.SetNDC();
	tag2.SetTextSize(0.032);

	c = ROOT.TCanvas("c"+name,"c"+name,1000,800);
	hs[0].SetMaximum(2.*maxval);
	hs[0].Draw("hist");
	for h in range(1,len(hs)): hs[h].Draw("histsames"); 
	leg.Draw();
	c.SaveAs(pdir+"/"+name+".pdf");	
	ROOT.gPad.SetLogy();
	hs[0].SetMinimum(1e-3);
	tag2.Draw();
	c.SaveAs(pdir+"/"+name+"_log.pdf")	

def makeCanvasComparison(hs,legname,color,style,name,pdir="plots",lumi=30,ofile=None,unitnorm=False):
    #color = [ROOT.kBlue,ROOT.kGreen+1,ROOT.kCyan,ROOT.kViolet,ROOT.kBlack,ROOT.kRed,5,2,4,6,7,8,3,5,2,4,6,7,8,3,5]
    #style = [1,2,5,6,7,1,1,2,2,2,2,2,2,2,3,3,3,3,3,3,3]
    leg = ROOT.TLegend(0.69,0.7,0.90,0.87)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.027)
    leg.SetTextFont(42)

    leg1 = ROOT.TLegend(0.38,0.65,0.81,0.87)
    leg1.SetFillStyle(0)
    leg1.SetBorderSize(0)
    leg1.SetTextSize(0.027)
    leg1.SetTextFont(42)

    maxval = -99
    for iname, h in sorted(hs.iteritems(),key=lambda (k,v): v.Integral()):
        h.SetLineColor(color[iname])
        h.SetLineStyle(style[iname])
        h.SetLineWidth(2)
        h.SetFillStyle(0)
	h.GetXaxis().SetLabelSize(0.03)
	h.GetXaxis().SetTitleOffset(1.1)
	h.GetXaxis().SetTitleSize(0.033)
        h.GetYaxis().SetLabelSize(0.03)
	h.GetYaxis().SetTitleOffset(1.2)
	h.GetYaxis().SetTitleSize(0.033)


        if h.GetMaximum() > maxval: maxval = h.GetMaximum()
        if 'Phibb' in iname: leg1.AddEntry(h,legname[iname],"l")
        else: leg.AddEntry(h,legname[iname],"l")


    print "======== signal contribution =========="
    for iname, h in sorted(hs.iteritems(),key=lambda (k,v): v.Integral()):
        print iname+":        %.4f "%(h.Integral())


    c = ROOT.TCanvas("c"+name,"c"+name,900,800)
    i=0
    for process, s in sorted(hs.iteritems(),key=lambda (k,v): v.Integral()): 
         i+=1
         if i==1:
		s.SetMaximum(1.5*maxval)
         	s.SetMinimum(0.01)
	 	if unitnorm : 
			s.SetMaximum(100.)
			s.DrawNormalized("hist")
                else: s.Draw("hist")
         else : 	
		if unitnorm : s.DrawNormalized("histsame")
		else : s.Draw("histsame")
    leg.Draw()
    leg1.Draw()
    #hs[0].GetXaxis().SetRangeUser(0,400)
    #hs[0].SetMinimum(1e-1); i
    tag1 = ROOT.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.033)
    tag2 = ROOT.TLatex(0.17,0.92,"CMS")
    tag2.SetNDC(); tag2.SetTextFont(62)
    tag3 = ROOT.TLatex(0.25,0.92,"Simulation Preliminary")
    tag3.SetNDC(); tag3.SetTextFont(52)
    tag2.SetTextSize(0.042); tag3.SetTextSize(0.033); tag1.Draw(); tag2.Draw(); tag3.Draw()
    c.SaveAs(pdir+"/"+name+".pdf")
    c.SaveAs(pdir+"/"+name+".gif")
    c.SaveAs(pdir+"/"+name+".C")
    ROOT.gPad.SetLogy()

    c.SaveAs(pdir+"/"+name+"_log.pdf")
    c.SaveAs(pdir+"/"+name+"_log.gif")
    c.SaveAs(pdir+"/"+name+"_log.C")
    if ofile is not None:
        ofile.cd()
        c.Write('c'+name)


    return c

    
def makeCanvasComparisonStack(hs,hb,legname,color,style,nameS,outname,pdir="plots",lumi=30,printSB=True,ofile=None):
    #leg_y = 0.88 - (len(hs)+len(hb))*0.04
#    leg = ROOT.TLegend(0.65,leg_y,0.88,0.88)
#    leg.SetFillStyle(0)
#    leg.SetBorderSize(0)
#    leg.SetTextSize(0.035)
#    leg.SetTextFont(42)
    leg_y = 0.87 - (2+len(hb))*0.04
    leg = ROOT.TLegend(0.72,leg_y,0.89,0.87)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.027)
    leg.SetTextFont(42)

    leg1 = ROOT.TLegend(0.48,leg_y,0.85,0.87)
    leg1.SetFillStyle(0)
    leg1.SetBorderSize(0)
    leg1.SetTextSize(0.027)
    leg1.SetTextFont(42)

    maxval = -99
    nevt=[]
    hstack = ROOT.THStack("hstack","hstack")
    #for name, h in (sorted(hb.iteritems(),key=customSort)):
    for name, h in sorted(hb.iteritems(),key=lambda (k,v): v.Integral()):
    	print name
        hstack.Add(h)
        h.SetFillColor(color[name])
        h.SetLineColor(1)
        h.SetLineStyle(1)
        h.SetLineWidth(1)
        h.SetFillStyle(1001)
	nevt.append(h.Integral())
        if h.GetMaximum() > maxval: maxval = h.GetMaximum()

    allMC=hstack.GetStack().Last().Clone()
    ntotal=allMC.Integral()
    nsig=hs[nameS].Integral()

    if(printSB): 
      ratio = hs[nameS].Clone("%s_ratio"%hs[nameS].GetName())
      ratio.SetDirectory(0)
      for i in range(0, allMC.GetNbinsX()):
        SoverB=0
        SoverB= getSoverRootB(hs[nameS],allMC,i)
        ratio.SetBinContent(i,SoverB)

    
    for name, h in sorted(hs.iteritems(),key=lambda (k,v): v.Integral()):
        h.SetLineColor(color[name])
        h.SetLineStyle(style[name])
        h.SetLineWidth(2)
        h.SetFillStyle(0)
	#h.Scale(100)
    
        
    for name, h in sorted(hb.iteritems(),key=lambda (k,v): -v.Integral()):
        leg.AddEntry(h,legname[name],"f")
    for name, h in sorted(hs.iteritems(),key=lambda (k,v): -v.Integral()):
        leg1.AddEntry(h,legname[name],"l")


    c = ROOT.TCanvas("c"+outname,"c"+outname,1000,800)
    c.SetFillStyle(4000)
    c.SetFrameFillStyle(1000)
    c.SetFrameFillColor(0)

    if(printSB): 
     oben = ROOT.TPad('oben','oben',0,0.3 ,1.0,1.0)
     oben.SetBottomMargin(0)
     oben.SetFillStyle(4000)
     oben.SetFrameFillStyle(1000)
     oben.SetFrameFillColor(0)
     unten = ROOT.TPad('unten','unten',0,0.0,1.0,0.3)
     unten.SetTopMargin(0.)
     unten.SetBottomMargin(0.35)
     unten.SetFillStyle(4000)
     unten.SetFrameFillStyle(1000)
     unten.SetFrameFillColor(0)

     oben.Draw()
     unten.Draw()
     oben.cd()
    else :
     c.cd()

    hstack.Draw('hist')
    #hstack.SetMaximum(1.5*maxval)
    hstack.SetMaximum(1e+12)
    hstack.GetYaxis().SetTitle('Events')
    hstack.GetXaxis().SetTitle(allMC.GetXaxis().GetTitle())
    hstack.Draw('hist')
    for name, h in hs.iteritems(): h.Draw("histsame")
    leg.Draw()
    leg1.Draw()
    
    tag1 = ROOT.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1 = ROOT.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.033)
    tag2 = ROOT.TLatex(0.17,0.92,"CMS")
    tag2.SetNDC(); tag2.SetTextFont(62)
    tag3 = ROOT.TLatex(0.27,0.92,"Simulation Preliminary")
    tag3.SetNDC(); tag3.SetTextFont(52)
    tag2.SetTextSize(0.042); tag3.SetTextSize(0.033); tag1.Draw(); tag2.Draw(); tag3.Draw()

    if(printSB): 
     unten.cd()
     unten.SetLogy()	
     ratio.SetStats(0)
     ratio.SetLineColor(hs[nameS].GetLineColor())
     ratio.SetLineWidth(2)
     ratio.SetLineStyle(1)
     #if "dbtag" in outname: ratio.GetYaxis().SetRangeUser(0,8)
     #else: ratio.GetYaxis().SetRangeUser(-3,4.1)
     ratio.GetYaxis().SetRangeUser(0.0001,10)
     ratio.GetYaxis().SetTitle("S/#sqrt{B}")
     ratio.GetXaxis().SetTitle(allMC.GetXaxis().GetTitle())
     ratio.GetXaxis().SetTitleSize(0.14)
     ratio.GetXaxis().SetTitleOffset(1.0)
     ratio.GetYaxis().SetTitleOffset(0.5)
     ratio.GetYaxis().SetLabelSize(0.12)
     ratio.GetYaxis().SetTitleSize(0.14)
     ratio.GetXaxis().SetLabelSize(0.12)

     line = ROOT.TLine(ratio.GetXaxis().GetXmin(), 1.0,
                      ratio.GetXaxis().GetXmax(), 1.0)
     line.SetLineColor(ROOT.kGray)
     line.SetLineStyle(2)
     line.Draw()

     ratio.Draw("HIST")
     line.Draw("same")


    c.SaveAs(pdir+"/"+outname+".pdf")
    c.SaveAs(pdir+"/"+outname+".gif")
    c.SaveAs(pdir+"/"+outname+".C")
		
	
    #ROOT.gPad.SetLogy()
    if(printSB): 
	oben.SetLogy()	
    else:
      c.SetLogy()
    hstack.SetMinimum(1e-1)	

    c.SaveAs(pdir+"/"+outname+"_log.pdf")
    c.SaveAs(pdir+"/"+outname+"_log.gif")
    c.SaveAs(pdir+"/"+outname+"_log.C")

    
    allMC=hstack.GetStack().Last().Clone()	    
    ntotal=allMC.Integral()
    i=0
    print "========== Background composition ==========="
    for name, h in sorted(hb.iteritems(),key=lambda (k,v): v.Integral()):
        if ntotal>0:        
            print name+":        %.2f            frac : %.3f"%(h.Integral(),nevt[i]/ntotal*100.)
            i+=1
            print "ggH:        %.2f             : %.3f "%(nsig,nsig/ntotal*100.)
    

    if ofile is not None:
        ofile.cd()
        c.Write('c'+outname)

    return c


def makeCanvasComparisonStackWData(hd,hs,hb,legname,color,style,outname,pdir="plots",lumi=30,ofile=None,normalize=False,ratio=True):
    ttbarInt = 0
    ttbarErr = 0
    ttbarErr2 = 0
    otherInt = 0
    otherErr = 0
    otherErr2 = 0
    print "========== Background composition ==========="
    for name, h in sorted(hb.iteritems(),key=lambda (k,v): v.Integral()):            
        error = array.array('d',[0.0])
        integral = h.IntegralAndError(1,h.GetNbinsX(),error)
        print name, integral, '+/-', error[0]        
        if 'TTbar' in name:
            ttbarInt += integral
            ttbarErr2 += error[0]*error[0]
        else:
            otherInt += integral
            otherErr2 += error[0]*error[0]

    ttbarErr = sqrt(ttbarErr2)
    otherErr = sqrt(otherErr2)
    error = array.array('d',[0.0])
    integral = hd.IntegralAndError(1,hd.GetNbinsX(),error)
    print 'data', integral, '+/-', error[0]
    dataInt = integral
    dataErr = error[0]

    kTTbar = 1
    kTTbarErr = 1
    if ttbarInt>0 and dataInt-otherInt>0:
	    kTTbar = (dataInt-otherInt)/ttbarInt
	    kTTbarErr = kTTbar*sqrt(pow(sqrt(dataErr*dataErr + otherErr*otherErr)/(dataInt-otherInt),2.) + pow(ttbarErr/ttbarInt,2.))

    print 'kTTbar', kTTbar, '+/-', kTTbarErr
    
    print 'data TTBar', dataInt-otherInt,'+/-', sqrt(dataErr*dataErr + otherErr*otherErr)
    print 'mc   TTBar', ttbarInt, '+/-', ttbarErr
    

    maxval = -99

    hstack = ROOT.THStack("hstack","hstack")
    for name, h in sorted(hb.iteritems(),key=lambda (k,v): v.Integral()):
        #if 'TTbar' in name:
        #    print 'scaling %s by k = %f'%(name, kTTbar)
        #    h.Scale(kTTbar)
        hstack.Add(h)
        h.SetFillColor(color[name])
        h.SetLineColor(1)
        h.SetLineStyle(1)
        h.SetLineWidth(1)
        h.SetFillStyle(1001)
        if h.GetMaximum() > maxval: maxval = h.GetMaximum()
    allMC=hstack.GetStack().Last().Clone()
    maxval = max(hd.GetMaximum(),maxval)
    
    fullmc = hstack.GetStack().Last();

    # normalize MC to data
    scalefactor = hd.Integral()/fullmc.Integral();
    print "data/mc scale factor = ", scalefactor
    if normalize:
    	for name, h in sorted(hb.iteritems(),key=lambda (k,v): v.Integral()): h.Scale( scalefactor );
    hstack2 = ROOT.THStack("hstack2","hstack2");
    for name, h in sorted(hb.iteritems(),key=lambda (k,v): v.Integral()):	
	hstack2.Add(h);
	h.SetFillColor(color[name])
        h.SetLineColor(1)
        h.SetLineStyle(1)
        h.SetLineWidth(1)
        h.SetFillStyle(1001)
    
    for name, h in sorted(hs.iteritems(),key=lambda (k,v): v.Integral()):
	#if 'ggH' in name:
	if 'Phibb' in name:
          h.SetLineColor(color[name])
          h.SetLineStyle(style[name])
          h.SetLineWidth(2)
          h.SetFillStyle(0)
    #leg_y = 0.88 - (2+len(hb))*0.04
    leg_y = 0.87 - (2+len(hb))*0.04
    #print "Length ", leg_y, " : ", len(hb)
##    leg = ROOT.TLegend(0.6,leg_y,0.88,0.88,"data/mc scale factor %.2f"%(scalefactor),"NDC")
##    leg.SetFillStyle(0)
##    leg.SetBorderSize(0)
##    leg.SetTextSize(0.035)
##    leg.SetTextFont(42)
##
##    for name, h in sorted(hb.iteritems(),key=lambda (k,v): -v.Integral()):
##        leg.AddEntry(h,legname[name],"f")
##    for name, h in sorted(hs.iteritems(),key=lambda (k,v): -v.Integral()):
##      #if 'ggH' in name:
##      if 'Phibb' in name:
##        leg.AddEntry(h,legname[name],"l")
##    leg.AddEntry(hd,legname['data'],"pe");
    leg = ROOT.TLegend(0.65,leg_y,0.82,0.87,"data/mc scale factor %.2f"%(scalefactor),"NDC")
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.035)
    leg.SetTextFont(42)
    leg2 = ROOT.TLegend(0.35,leg_y,0.72,0.87)
    leg2.SetFillStyle(0)
    leg2.SetBorderSize(0)
    leg2.SetTextSize(0.035)
    leg2.SetTextFont(42)

    count=1
    for name, h in sorted(hb.iteritems(),key=lambda (k,v): -v.Integral()):
        if count <7: 
                leg.AddEntry(h,legname[name],"f")
        #print " count : ",count, "Name : ", h.GetName(); 
        count = count+1
    for name, h in sorted(hs.iteritems(),key=lambda (k,v): -v.Integral()):
      if 'Phibb' in name:
        leg2.AddEntry(h,legname[name],"l")
    leg.AddEntry(hd,'Data',"pe");
    c = ROOT.TCanvas("c"+outname,"c"+outname,1000,800)
    c.SetFillStyle(4000)
    c.SetFrameFillStyle(1000)
    c.SetFrameFillColor(0)
    if ratio:
    	oben = ROOT.TPad('oben','oben',0,0.3 ,1.0,1.0)
	unten = ROOT.TPad('unten','unten',0,0.0,1.0,0.3)
        oben.SetBottomMargin(0)
	unten.SetTopMargin(0.)
	unten.SetBottomMargin(0.35)

    else:	
        oben = ROOT.TPad('oben','oben',0,0.05 ,1.0,1.0)
	unten = ROOT.TPad('unten','unten',0,0.0,1.0,0.0)
    oben.SetFillStyle(4000)
    oben.SetFrameFillStyle(1000)
    oben.SetFrameFillColor(0)
    unten.SetFillStyle(4000)
    unten.SetFrameFillStyle(1000)
    unten.SetFrameFillColor(0)
    oben.Draw()
    unten.Draw()
    oben.cd()
 
    hstack2.Draw('hist')
    hstack2.SetMaximum(500000.*maxval)
    hstack2.GetYaxis().SetTitle('Events')
    hstack2.GetYaxis().SetTitleOffset(1.0)	
    hstack2.GetXaxis().SetTitle(allMC.GetXaxis().GetTitle())
    hstack2.GetXaxis().SetTitleOffset(1.3)
    hstack2.GetXaxis().SetLabelSize(0.04)
    hstack2.GetXaxis().SetTitleSize(0.045)
    hstack2.Draw('hist')
    for name, h in hs.iteritems(): 
	  #if 'ggH' in name:
	  if 'Phibb' in name:
		h.Draw("histsame")
    leg.Draw()
    leg2.Draw()
    hstack2.SetMinimum(1e-1)
    hd.Draw('pesames');
    tag1 = ROOT.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag2 = ROOT.TLatex(0.17,0.92,"CMS")
    tag2.SetNDC()
    tag2.SetTextFont(62)
    tag3 = ROOT.TLatex(0.27,0.92,"Preliminary")
    tag3.SetNDC()
    tag3.SetTextFont(52)
    tag2.SetTextSize(0.055)
    tag3.SetTextSize(0.045)
    tag1.Draw()
    tag2.Draw()
    tag3.Draw()
    allMC2=hstack2.GetStack().Last().Clone()
    if ratio:	
    	unten.cd()
    	ratio= getRatio(hd,allMC2)
    	ksScore = hd.KolmogorovTest( allMC2 )
    	chiScore = hd.Chi2Test( allMC2 , "UWCHI2/NDF")
    	print ksScore
    	print chiScore
    	ratio.SetStats(0)
        ratio.GetYaxis().SetRangeUser(0,2.5)	
        ratio.GetYaxis().SetNdivisions(504)
    	ratio.GetYaxis().SetTitle("Data/Simulation")
    	ratio.GetXaxis().SetTitle(allMC.GetXaxis().GetTitle())    
    	ratio.GetXaxis().SetTitleSize(0.14)
    	ratio.GetXaxis().SetTitleOffset(1.0)
    	ratio.GetYaxis().SetTitleOffset(0.5)
    	ratio.GetYaxis().SetLabelSize(0.12)
    	ratio.GetYaxis().SetTitleSize(0.11)
    	ratio.GetXaxis().SetLabelSize(0.11)
	
    	line = ROOT.TLine(ratio.GetXaxis().GetXmin(), 1.0,
                      ratio.GetXaxis().GetXmax(), 1.0)
    	line.SetLineColor(ROOT.kGray)
    	line.SetLineStyle(2)
    	line.Draw()
    	tKsChi = ROOT.TLatex()
    	tKsChi.SetNDC()
    	tKsChi.SetTextFont(42)
    	tKsChi.SetTextSize(0.09)

    #ratioError = ROOT.TGraphErrors(error)
    #ratioError.SetFillColor(ROOT.kGray+3)
    #ratioError.SetFillStyle(3013)
    	ratio.Draw("E1 ")	
    	line.Draw("same")	
        tKsChi.DrawLatex(0.7,0.895,"#chi^{2}_{ }#lower[0.1]{/^{}#it{NDF} = %.2f}"%(chiScore))

    c.SaveAs(pdir+"/"+outname+".pdf")
    c.SaveAs(pdir+"/"+outname+".gif")
    c.SaveAs(pdir+"/"+outname+".C")
    oben.SetLogy()


    c.SaveAs(pdir+"/"+outname+"_log.pdf")
    c.SaveAs(pdir+"/"+outname+"_log.gif")
    c.SaveAs(pdir+"/"+outname+"_log.C")

    if ofile is not None:
        ofile.cd()
        c.Write('c'+outname)

    
    return c        

def makeCanvasRatio(h_denom,h_numer,legname,color,style,outname,pdir="plots",lumi=30,ofile=None,pt=None,f2params=None):
    leg_y = 0.88 - (6)*0.04
    leg = ROOT.TLegend(0.5,leg_y,0.88,0.88)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.035)
    leg.SetTextFont(42)

    maxval = -99

    #h_denom.Scale(1./h_denom.Integral())
    #h_numer.Scale(1./h_numer.Integral())
    leg.AddEntry(h_denom,legname[0],'l')
    leg.AddEntry(h_numer,legname[1],'pe')
    
    c = ROOT.TCanvas("c"+outname,"c"+outname,1000,800)

    c.SetFillStyle(4000)
    c.SetFrameFillStyle(1000)
    c.SetFrameFillColor(0)

    oben = ROOT.TPad('oben','oben',0,0.3 ,1.0,1.0)
    oben.SetBottomMargin(0)
    oben.SetFillStyle(4000)
    oben.SetFrameFillStyle(1000)
    oben.SetFrameFillColor(0)
    unten = ROOT.TPad('unten','unten',0,0.0,1.0,0.3)
    unten.SetTopMargin(0.)
    unten.SetBottomMargin(0.35)
    unten.SetFillStyle(4000)
    unten.SetFrameFillStyle(1000)
    unten.SetFrameFillColor(0)

    oben.Draw()
    unten.Draw()
    oben.cd()

    h_denom.GetYaxis().SetTitle('Probability')
    h_denom.GetYaxis().SetTitleOffset(1.0)
    h_denom.SetMaximum(1.2*max(h_denom.GetMaximum(),h_numer.GetMaximum()))
    h_denom.SetMinimum(0.)
    h_denom.SetLineColor(color[0])
    h_numer.SetLineColor(color[1])
    h_denom.Draw('hist')
    h_numer.Draw('pezsame')

    if pt is not None and f2params is not None:
        f1params = array.array('d',list(f2params))
        f1params.append(pt)
        npar = len(f2params)
        f2 = ROOT.TF2("f2",fun2,h_denom.GetXaxis().GetXmin(),h_denom.GetXaxis().GetXmax(),h_denom.GetYaxis().GetXmin(),h_denom.GetYaxis().GetXmax(),npar)
        f2.SetParameters(f2params)
        f1 = ROOT.TF1("f1",fun1,h_denom.GetXaxis().GetXmin(),h_denom.GetXaxis().GetXmax(),npar+1)
        f1.SetParameters(f1params)

        h_pred = h_denom.Clone('h_pred')
        for i in range(1,h_pred.GetXaxis().GetNbins()+1):
            h_pred.SetBinContent(i,f2.Eval(h_pred.GetBinCenter(i),pt)*h_pred.GetBinContent(i))

        h_pred.SetLineColor(ROOT.kRed)
        h_pred.Draw('histsame')        
        leg.AddEntry(h_pred,'QCD fail #times polynomial','l')
    
    leg.Draw()
    tag1 = ROOT.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag2 = ROOT.TLatex(0.15,0.92,"CMS")
    tag2.SetNDC()
    tag2.SetTextFont(62)
    tag3 = ROOT.TLatex(0.25,0.92,"Preliminary")
    tag3.SetNDC()
    tag3.SetTextFont(52)
    tag2.SetTextSize(0.055)
    tag3.SetTextSize(0.045)
    tag1.Draw()
    tag2.Draw()
    tag3.Draw()

    unten.cd()
    ratio= getRatio(h_numer,h_denom)
    ksScore = h_numer.KolmogorovTest( h_denom )
    chiScore = h_numer.Chi2Test( h_denom , "WWCHI2/NDF")
    print ksScore
    print chiScore
    ratio.SetStats(0)
    ratio.GetYaxis().SetRangeUser(0.3,1.7)	
    ratio.GetYaxis().SetNdivisions(504)
    ratio.GetYaxis().SetTitle("Ratio")
    ratio.GetXaxis().SetTitle(h_denom.GetXaxis().GetTitle())    
    ratio.GetXaxis().SetTitleSize(0.14)
    ratio.GetXaxis().SetTitleOffset(1.0)
    ratio.GetYaxis().SetTitleOffset(0.5)
    ratio.GetYaxis().SetLabelSize(0.12)
    ratio.GetYaxis().SetTitleSize(0.14)
    ratio.GetXaxis().SetLabelSize(0.12)
	
    
    line = ROOT.TLine(ratio.GetXaxis().GetXmin(), 1.0,
                      ratio.GetXaxis().GetXmax(), 1.0)
    line.SetLineColor(ROOT.kGray)
    line.SetLineStyle(2)
    line.Draw()
    tKsChi = ROOT.TLatex()
    tKsChi.SetNDC()
    tKsChi.SetTextFont(42)
    tKsChi.SetTextSize(0.09)

    #ratioError = ROOT.TGraphErrors(error)
    #ratioError.SetFillColor(ROOT.kGray+3)
    #ratioError.SetFillStyle(3013)
    ratio.Draw("pez")	
    line.Draw("same")
    
    if pt is not None:
        f1.SetLineColor(ROOT.kRed)
        f1.Draw("csame")
        
    tKsChi.DrawLatex(0.7,0.895,"#chi^{2}_{ }#lower[0.1]{/^{}#it{NDF} = %.2f}"%(chiScore))

    c.SaveAs(pdir+"/"+outname+".pdf")
    c.SaveAs(pdir+"/"+outname+".C")
    
    h_denom.SetMinimum(0.0005)
    h_denom.SetMaximum(1)
    oben.SetLogy()


    c.SaveAs(pdir+"/"+outname+"_log.pdf")
    c.SaveAs(pdir+"/"+outname+"_log.C")

    if ofile is not None:
        ofile.cd()
        c.Write('c'+outname)

    return c        

def fun2(x, par):
    rho = ROOT.TMath.Log((x[0]*x[0])/(x[1]*x[1]))
    poly0 = par[0]*(1.0 + par[1]*rho + par[2]*rho*rho)
    poly1 = par[0]*(par[3] + par[4]*rho + par[5]*rho*rho)*x[1]
    poly2 = par[0]*(par[6] + par[7]*rho + par[8]*rho*rho)*x[1]*x[1]
    return poly0+poly1+poly2

def fun2rho(x, par):
    rho = x[0]
    poly0 = par[0]*(1.0 + par[1]*rho + par[2]*rho*rho)
    poly1 = par[0]*(par[3] + par[4]*rho + par[5]*rho*rho)*x[1]
    poly2 = par[0]*(par[6] + par[7]*rho + par[8]*rho*rho)*x[1]*x[1]
    return poly0+poly1+poly2

def fun1(x, par):
    rho = ROOT.TMath.Log((x[0]*x[0])/(par[9]*par[9]))
    poly0 = par[0]*(1.0 + par[1]*rho + par[2]*rho*rho)
    poly1 = par[0]*(par[3] + par[4]*rho + par[5]*rho*rho)*par[9]
    poly2 = par[0]*(par[6] + par[7]*rho + par[8]*rho*rho)*par[9]*par[9]
    return poly0+poly1+poly2

def makeCanvasRatio2D(h_denom,h_numer,legname,color,style,outname,pdir="plots",lumi=30,ofile=None):
    leg_y = 0.88 - (6)*0.04
    leg = ROOT.TLegend(0.5,leg_y,0.88,0.88)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.035)
    leg.SetTextFont(42)

    maxval = -99

    #h_denom.Scale(1./h_denom.Integral())
    #h_numer.Scale(1./h_numer.Integral())
    ratio = h_numer.Clone('ratio')
    ratio.Divide(h_denom)
    ratio.GetXaxis().SetTitleOffset(1.5)
    ratio.GetYaxis().SetTitleOffset(1.5)
    ratio.GetZaxis().SetTitle('Ratio')
    ratio.GetXaxis().SetNdivisions(504)
    ratio.GetYaxis().SetNdivisions(508)
    ratio.GetZaxis().SetNdivisions(504)
    for i in range(ratio.GetNbinsX()):
        for j in range(ratio.GetNbinsY()):
            if ratio.GetBinContent(i+1,j+1)==0:
                ratio.SetBinContent(i+1,j+1,0)
    c = ROOT.TCanvas("c"+outname,"c"+outname,1000,800)

    c.SetFillStyle(4000)
    c.SetFrameFillStyle(1000)
    c.SetFrameFillColor(0)

    ratio.SetLineColor(ROOT.kBlue+1)


    f2params = array.array('d',[1,0,0,0,0,0,0,0,0])
    npar = len(f2params)
    f2 = ROOT.TF2("f2",fun2,ratio.GetXaxis().GetXmin(),ratio.GetXaxis().GetXmax(),ratio.GetYaxis().GetXmin(),ratio.GetYaxis().GetXmax(),npar)
    f2.SetParameters(f2params)
    #f2.FixParameter(2,0)
    #f2.FixParameter(5,0)
    #f2.FixParameter(8,0)
    f2.FixParameter(6,0)
    f2.FixParameter(7,0)
    f2.FixParameter(8,0)
    fr = ratio.Fit('f2','RNS')
    #f2.Draw("surf")
    ratio.Draw('surf1')

    
    f2graph = ROOT.TGraph2D()
    N = -1
    for i in range(101):
        for j in range(101):
            N+=1
            x = ratio.GetXaxis().GetXmin() + i*(ratio.GetXaxis().GetXmax()-ratio.GetXaxis().GetXmin())/100
            y = ratio.GetYaxis().GetXmin() + j*(ratio.GetYaxis().GetXmax()-ratio.GetYaxis().GetXmin())/100
            z = f2.Eval(x,y)
            if math.log(x*x/(y*y)) < -6 or math.log(x*x/(y*y)) > -2.1:
                z = 0
            #print x, y, z
            f2graph.SetPoint(N,x,y,z)
    f2.Draw("surf fb bb same")
    #f2graph.SetLineColor(ROOT.kRed)
    #f2graph.Draw("surf fb bb same")

    #raw_input("Press Enter to continue...")
    print 'chi2 = ', fr.Chi2()

    #ratio.GetZaxis().SetRangeUser(0.3,1.7)
    #ratio.SetMinimum(0.3)
    #ratio.SetMaximum(1.7)

    ROOT.gPad.SetTheta(30)
    ROOT.gPad.SetPhi(30+270)
    ROOT.gPad.Modified()
    ROOT.gPad.Update()
    #h1 = c.DrawFrame(40,500,200,1000)
    #ratio.Draw('surf1')
    #f2.Draw("surf same bb")
   
    tag1 = ROOT.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag2 = ROOT.TLatex(0.15,0.92,"CMS")
    tag2.SetNDC()
    tag2.SetTextFont(62)
    tag3 = ROOT.TLatex(0.25,0.92,"Simulation Preliminary")
    tag3.SetNDC()
    tag3.SetTextFont(52)
    tag2.SetTextSize(0.055)
    tag3.SetTextSize(0.045)
    tag1.Draw()
    tag2.Draw()
    tag3.Draw()

    c.SaveAs(pdir+"/"+outname+".pdf")
    c.SaveAs(pdir+"/"+outname+".C")
    #for i in range(0,360):        
    #    ROOT.gPad.SetPhi(30+270+i)
    #    ROOT.gPad.Modified()
    #    ROOT.gPad.Update()
    #    c.SaveAs(pdir+"/"+outname+"_%03d.png"%i)
    
    ROOT.gPad.SetLogz()

    ratio.SetMinimum(1e-2)
    ratio.SetMaximum(10)
    f2.GetParameters(f2params)
    print f2params

    c.SaveAs(pdir+"/"+outname+"_log.pdf")
    c.SaveAs(pdir+"/"+outname+"_log.C")

    if ofile is not None:
        ofile.cd()
        c.Write('c'+outname)


    #c.Clear()
    c.SetLogz(0)

    ratiorho = ROOT.TH2D('ratiorho','ratiorho',100,-6,-2.1,100,ratio.GetYaxis().GetXmin(),ratio.GetYaxis().GetXmax())
    ratiorho.GetYaxis().SetTitle(ratio.GetYaxis().GetTitle())    
    ratiorho.GetXaxis().SetTitle('#rho')
    ratiorho.GetZaxis().SetTitle(ratio.GetZaxis().GetTitle())
    ratiorhograph = ROOT.TGraph2D()
    N = -1
    for i in range(1,ratio.GetNbinsX()+1):
        for j in range(1,ratio.GetNbinsY()+1):
            N+=1
            m = ratio.GetXaxis().GetBinCenter(i)
            y = ratio.GetYaxis().GetBinCenter(j)
            x = math.log(m*m/(y*y))
            z = ratio.GetBinContent(i,j)
            #print N, x, y, z
            ratiorhograph.SetPoint(N,x,y,z)
    f2rho = ROOT.TF2("f2",fun2rho,-6,-2.1,ratio.GetYaxis().GetXmin(),ratio.GetYaxis().GetXmax(),npar)
    f2rho.SetParameters(f2params)
    f2rhograph = ROOT.TGraph2D()
    N = -1
    for i in range(101):
        for j in range(101):
            N+=1
            x = -6 + i*(-2.1+6)/100
            y = ratio.GetYaxis().GetXmin() + j*(ratio.GetYaxis().GetXmax()-ratio.GetYaxis().GetXmin())/100
            z = f2rho.Eval(x,y)
            m = math.sqrt(math.exp(x))*y
            if m < 40 or m > 201:
                z = 0
            #print x, y, z
            f2rhograph.SetPoint(N,x,y,z)
    #ratiorho.Draw('surf1')    
    ratiorhograph.GetHistogram().GetYaxis().SetTitle(ratio.GetYaxis().GetTitle())    
    ratiorhograph.GetHistogram().GetXaxis().SetTitle('#rho')
    ratiorhograph.GetHistogram().GetZaxis().SetTitle(ratio.GetZaxis().GetTitle())
    ratiorhograph.GetHistogram().GetYaxis().SetNdivisions(505)
    ratiorhograph.GetHistogram().GetXaxis().SetNdivisions(505)
    ratiorhograph.GetHistogram().GetXaxis().SetTitleOffset(1.5)
    ratiorhograph.GetHistogram().GetYaxis().SetTitleOffset(1.5)
    ratiorhograph.Draw("surf1")
    f2rho.Draw("surf fb bb same")
    #f2rhograph.SetLineColor(ROOT.kRed)
    #f2rhograph.Draw("surf fb bb same")
    tag1 = ROOT.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag2 = ROOT.TLatex(0.15,0.92,"CMS")
    tag2.SetNDC()
    tag2.SetTextFont(62)
    tag3 = ROOT.TLatex(0.25,0.92,"Simulation Preliminary")
    tag3.SetNDC()
    tag3.SetTextFont(52)
    tag2.SetTextSize(0.055)
    tag3.SetTextSize(0.045)
    tag1.Draw()
    tag2.Draw()
    tag3.Draw()
    c.SaveAs(pdir+"/"+outname.replace('msd','rho')+".pdf")
    c.SaveAs(pdir+"/"+outname.replace('msd','rho')+".C")
    
    #f2rho.Draw("colz")
    c.SetRightMargin(0.20)
    f2graph.Draw("colz")
    f2graph.GetHistogram().GetXaxis().SetTitle(ratio.GetXaxis().GetTitle())
    f2graph.GetHistogram().GetYaxis().SetTitle(ratio.GetYaxis().GetTitle())
    f2graph.GetHistogram().GetZaxis().SetTitle(ratio.GetZaxis().GetTitle())
    tag1 = ROOT.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag2 = ROOT.TLatex(0.15,0.92,"CMS")
    tag2.SetNDC()
    tag2.SetTextFont(62)
    tag3 = ROOT.TLatex(0.25,0.92,"Simulation Preliminary")
    tag3.SetNDC()
    tag3.SetTextFont(52)
    tag2.SetTextSize(0.055)
    tag3.SetTextSize(0.045)
    tag1.Draw()
    tag2.Draw()
    tag3.Draw()
    
    c.SaveAs(pdir+"/"+outname.replace('msd','msdcolz')+".pdf")
    c.SaveAs(pdir+"/"+outname.replace('msd','msdcolz')+".C")
    
    f2rhograph.Draw("colz")
    f2rhograph.GetHistogram().GetXaxis().SetTitle('#rho')
    f2rhograph.GetHistogram().GetYaxis().SetTitle(ratio.GetYaxis().GetTitle())
    f2rhograph.GetHistogram().GetZaxis().SetTitle(ratio.GetZaxis().GetTitle())
    tag1 = ROOT.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag2 = ROOT.TLatex(0.15,0.92,"CMS")
    tag2.SetNDC()
    tag2.SetTextFont(62)
    tag3 = ROOT.TLatex(0.25,0.92,"Simulation Preliminary")
    tag3.SetNDC()
    tag3.SetTextFont(52)
    tag2.SetTextSize(0.055)
    tag3.SetTextSize(0.045)
    tag1.Draw()
    tag2.Draw()
    tag3.Draw()
    
    c.SaveAs(pdir+"/"+outname.replace('msd','rhocolz')+".pdf")
    c.SaveAs(pdir+"/"+outname.replace('msd','rhocolz')+".C")
    
    
    #raw_input("Press Enter to continue...")

    return c, f2params

def	makeCanvas2D( TFMap, name, pdir='plots' ):

	c1 = ROOT.TCanvas("c1","c1",1000,800)
	TFMap.Draw("colz");
	c1.SetRightMargin(0.15);
	c1.SaveAs(pdir+"/"+name+".pdf");

	# hxs = [];
	hys = [];
	
	# for i in range(TFMap.GetNbinsX()):
	# 	xnam = TFMap.GetYaxis().GetTitle();
	# 	nbin = TFMap.GetNbinsY();
	# 	ylo = TFMap.GetYaxis().GetBinLowEdge(1);
	# 	yhi = TFMap.GetYaxis().GetBinUpEdge(nbin);
	# 	hxs.append( ROOT.TH1F("hxs"+str(i),";"+xnam+";",nbin,ylo,yhi) );
	
	for i in range(TFMap.GetNbinsY()):
		xnam = TFMap.GetXaxis().GetTitle();
		nbin = TFMap.GetNbinsX();
		ylo = TFMap.GetXaxis().GetBinLowEdge(1);
		yhi = TFMap.GetXaxis().GetBinUpEdge(nbin);
		hys.append( ROOT.TH1F("hys"+str(i),";"+xnam+";",nbin,ylo,yhi) );		

	# for i in range(TFMap.GetNbinsX()):
	# 	for j in range(TFMap.GetNbinsY()):
	# 		hxs[i].SetBinContent( j+1, TFMap.GetBinContent(i+1,j+1) );
	# 		hxs[i].SetBinError( j+1, TFMap.GetBinError(i+1,j+1) );

	for i in range(TFMap.GetNbinsY()):
		for j in range(TFMap.GetNbinsX()):
			hys[i].SetBinContent( j+1, TFMap.GetBinContent(j+1,i+1) );			
			hys[i].SetBinError( j+1, TFMap.GetBinError(j+1,i+1) );			

	colors = [];
	for i in range(10):
		colors.append(1); colors.append(2); colors.append(4); colors.append(6);
	# for i in range(len(hxs)): 
	# 	hxs[i].SetLineColor(colors[i]);
	# 	hxs[i].SetMarkerSize(0);
	for i in range(len(hys)): 
		hys[i].SetLineColor(colors[i]);
		hys[i].SetMarkerSize(0);

	# cx = ROOT.TCanvas("cx","cx",1000,800);
	# hxs[0].SetMaximum( 1.25*TFMap.GetMaximum() );
	# hxs[0].SetMinimum( 0. );
	# hxs[0].Draw("histe");
	# for i in range(1,len(hxs)):
	# 	hxs[i].Draw("histesames")
	# cx.SaveAs(pdir+"/"+name+"_hxs.pdf");

	cy = ROOT.TCanvas("cy","cy",1000,800);
	hys[0].SetMaximum( 1.25*TFMap.GetMaximum() );
	hys[0].SetMinimum( 0. );
	hys[0].Draw("histe");
	for i in range(1,len(hys)):
		hys[i].Draw("histesames")
	cy.SaveAs(pdir+"/"+name+"_hys.pdf");

	return hys;

def plotROCs(grs,legs,pdir,name):

	canroc = ROOT.TCanvas("c","c",1000,800);
	hrl1 = canroc.DrawFrame(0.,0.,1.0,1.0);
	hrl1.GetXaxis().SetTitle("signal efficiency");
	hrl1.GetYaxis().SetTitle("background efficiency");
	
	leg = ROOT.TLegend( 0.2, 0.6, 0.5, 0.9 );
	leg.SetBorderSize( 0 );
	leg.SetFillStyle( 0 );
	leg.SetTextSize( 0.03 );  

	colors = [1,2,4,6,7]
	ctr = 0;
	for gr in grs:
		gr.Draw();
		gr.SetLineColor(colors[ctr]);
		leg.AddEntry(gr,legs[ctr],"l");
		ctr += 1;
	leg.Draw();
	canroc.SaveAs(pdir+"/"+name+".pdf");


def makeROCFromHisto(hists,LtoR=True):

	hsig = hists[0];
	hbkg = hists[1];

	nbins = hsig.GetNbinsX();
	binsize = hsig.GetBinWidth(1);
	lowedge = hsig.GetBinLowEdge(1);

	#print "lowedge: ",lowedge

	hsigIntegral = hsig.Integral();
	hbkgIntegral = hbkg.Integral();

	xval = array.array('d', [])
	yval = array.array('d', [])
	ctr = 0;
	effBkgPrev = -9999;
	for i in range(1,nbins+1):

			effBkg = 0;
			effSig = 0;

			if LtoR: effBkg = hbkg.Integral( i, nbins )/hbkgIntegral;
			else: effBkg = hbkg.Integral( 1, i )/hbkgIntegral;

			if LtoR: effSig = hsig.Integral( i, nbins )/hsigIntegral;
			else: effSig = hsig.Integral( 1, i )/hsigIntegral;

			#if not effBkg == 0.: print "cut: ",(lowedge+(i-1)*binsize),"effBkg: ", effBkg, ", effSig: ", effSig;

			xval.append( effSig );
			yval.append( effBkg );

			#effBkgPrev = effBkg;
			ctr = ctr + 1;

	#print nbins, "and ", ctr
	tg = ROOT.TGraph( nbins, xval, yval );
	tg.SetName( "tg"+hsig.GetName() );
	return tg;

def dummy():
	print "hi";

