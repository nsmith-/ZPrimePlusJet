import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory, TVirtualFitter
import math
import sys
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

    maxval = 1.5*max(hstack2.GetStack().Last().GetMaximum(),hd.GetMaximum());
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
	maxval = 1.5*max(mcall.GetMaximum(),hd.GetMaximum());
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
	tag1.SetTextSize(0.035);
	tag1.SetTextFont(52);
	txta = ROOT.TLatex(0.17,0.95,"CMS");
	txta.SetNDC();
	txtb = ROOT.TLatex(0.22,0.95,"Simulation Preliminary");
	txtb.SetNDC(); txtb.SetTextFont(52);
	txta.SetTextSize(0.035);
	txtb.SetTextSize(0.035);

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

	tag2 = ROOT.TLatex(0.17,0.90,"CMS preliminary")
	tag2.SetNDC();
	tag2.SetTextSize(0.032);

	c = ROOT.TCanvas("c"+name,"c"+name,1000,800);
	hs[0].SetMaximum(1.5*maxval);
	hs[0].Draw("hist");
	for h in range(1,len(hs)): hs[h].Draw("histsames"); 
	leg.Draw();
	c.SaveAs(pdir+"/"+name+".pdf");	
	ROOT.gPad.SetLogy();
	hs[0].SetMinimum(1e-3);
	tag2.Draw();
	c.SaveAs(pdir+"/"+name+"_log.pdf")	

def makeCanvasComparison(hs,legname,name,pdir="plots",lumi=30):

    color = [ROOT.kBlue,ROOT.kGreen+1,ROOT.kCyan,ROOT.kViolet,ROOT.kBlack,ROOT.kRed,5,2,4,6,7,8,3,5,2,4,6,7,8,3,5]
    style = [1,2,5,6,7,1,1,2,2,2,2,2,2,2,3,3,3,3,3,3,3]

    leg = ROOT.TLegend(0.55,0.65,0.9,0.9)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.035)

    maxval = -99
    for h in range(len(hs)): 
        hs[h].SetLineColor(color[h])
        hs[h].SetLineStyle(style[h])
        hs[h].SetLineWidth(2)
        hs[h].SetFillStyle(0)
        # hs[h].Scale(1./hs[h].Integral())
        if hs[h].GetMaximum() > maxval: maxval = hs[h].GetMaximum()
        leg.AddEntry(hs[h],legname[h],"l")

    c = ROOT.TCanvas("c"+name,"c"+name,1000,800)
    hs[0].SetMaximum(1.5*maxval)
    hs[0].Draw("hist")
    for h in range(1,len(hs)): hs[h].Draw("histsames")
    leg.Draw()
    c.SaveAs(pdir+"/"+name+".pdf")
    ROOT.gPad.SetLogy()
    hs[0].GetXaxis().SetRangeUser(0,400)
    hs[0].SetMinimum(1e-1); tag1 = ROOT.TLatex(0.67,0.92,"%.0f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag2 = ROOT.TLatex(0.1,0.92,"CMS")
    tag2.SetNDC(); tag2.SetTextFont(62)
    tag3 = ROOT.TLatex(0.2,0.92,"Simulation Preliminary")
    tag3.SetNDC(); tag3.SetTextFont(52)
    tag2.SetTextSize(0.055); tag3.SetTextSize(0.045); tag1.Draw(); tag2.Draw(); tag3.Draw()

    c.SaveAs(pdir+"/"+name+"_log.pdf")		

    
def makeCanvasComparisonStack(hs,hb,legname,color,style,outname,pdir="plots",lumi=30,ofile=None):
    leg_y = 0.88 - len(legname.keys())*0.04
    leg = ROOT.TLegend(0.65,leg_y,0.88,0.88)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.035)
    leg.SetTextFont(42)

    maxval = -99

    hstack = ROOT.THStack("hstack","hstack")
    for name, h in sorted(hb.iteritems(),key=lambda (k,v): v.Integral()):
        hstack.Add(h)
        h.SetFillColor(color[name])
        h.SetLineColor(color[name])
        h.SetLineStyle(1)
        h.SetLineWidth(1)
        h.SetFillStyle(1001)
        if h.GetMaximum() > maxval: maxval = h.GetMaximum()
    fullmc = hstack.GetStack().Last()
    
    for name, h in sorted(hs.iteritems(),key=lambda (k,v): v.Integral()):
        h.SetLineColor(color[name])
        h.SetLineStyle(style[name])
        h.SetLineWidth(2)
        h.SetFillStyle(0)
        
    for name, h in sorted(hb.iteritems(),key=lambda (k,v): -v.Integral()):
        leg.AddEntry(h,legname[name],"f")
    for name, h in sorted(hs.iteritems(),key=lambda (k,v): -v.Integral()):
        leg.AddEntry(h,legname[name],"l")

    c = ROOT.TCanvas("c"+outname,"c"+outname,1000,800)
    hstack.Draw('hist')
    hstack.SetMaximum(1.5*maxval)
    hstack.GetYaxis().SetTitle('Events')
    hstack.GetXaxis().SetTitle(fullmc.GetXaxis().GetTitle())
    hstack.Draw('hist')
    for name, h in hs.iteritems(): h.Draw("histsame")
    leg.Draw()
    c.SaveAs(pdir+"/"+outname+".pdf")
    c.SaveAs(pdir+"/"+outname+".C")
    ROOT.gPad.SetLogy()
    hstack.SetMinimum(1e-1)
    tag1 = ROOT.TLatex(0.67,0.92,"%.0f fb^{-1} (13 TeV)"%lumi)
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

    c.SaveAs(pdir+"/"+outname+"_log.pdf")
    c.SaveAs(pdir+"/"+outname+"_log.C")

    if ofile is not None:
        ofile.cd()
        c.Write('c'+outname)

    return c
    
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

