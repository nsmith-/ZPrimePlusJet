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
    mass = 125

    fml = r.TFile(options.idir+"/mlfit.root")
    fd  = r.TFile(options.idir+"/base.root")
    histograms_pass_all = {}
    histograms_fail_all = {}

    histograms_pass_summed = {}
    histograms_fail_summed = {}

    shapes = ['wqq','zqq','tqq','qcd','hqq125','zhqq125','whqq125','tthqq125','vbfhqq125','data']	


    msd_binBoundaries=[]
    for i in range(0,24): msd_binBoundaries.append(40+i*7)
    pt_binBoundaries = [500,550,600,675,800,1000]

    for i in range(5):
        (tmppass,tmpfail) = plotCategory(fml,fd,i+1,options.fit)
        histograms_pass_all[i] = {}
        histograms_fail_all[i] = {}
        for shape in shapes:
            for hist in tmppass:
                if shape in hist.GetName(): histograms_pass_all[i][shape] = hist
            for hist in tmpfail:
                if shape in hist.GetName(): histograms_fail_all[i][shape] = hist
                    
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
        
    makeMLFitCanvas(histograms_pass_summed_list[0:4], histograms_pass_summed_list[9], histograms_pass_summed_list[4:8], shapes, "pass_allcats_"+options.fit,options.odir)
    makeMLFitCanvas(histograms_fail_summed_list[0:4], histograms_fail_summed_list[9], histograms_fail_summed_list[4:8], shapes, "fail_allcats_"+options.fit,options.odir)

    
	# print out fit results
    if options.fit == "fit_b" or options.fit == "fit_s":
        rfr = r.RooFitResult( fml.Get(options.fit) )
        lParams = []
        lParams.append("qcdeff")
        lParams.append("r0p1")
        lParams.append("r0p2") ##
        lParams.append("r1p0")
        lParams.append("r1p1")
        lParams.append("r1p2")
        lParams.append("r2p0") 
        lParams.append("r2p1")
        lParams.append("r2p2")

        pars = []
        for p in lParams:
            print p,"=",rfr.floatParsFinal().find(p).getVal(),"+/-",rfr.floatParsFinal().find(p).getError()
            pars.append(rfr.floatParsFinal().find(p).getVal())

        print lParams
        print pars
        # Plot TF poly
        makeTF(pars,ratio_2d_data_subtract)

def plotCategory(fml,fd,index,fittype):
    shapes = ['wqq','zqq','tqq','qcd','hqq125','zhqq125','whqq125','tthqq125','vbfhqq125']
    histograms_fail = []
    histograms_pass = []
    for i,ish in enumerate(shapes):
        if i<4:
            fitdir = fittype
        else:
            #fitdir = "prefit"
            fitdir = fittype
        print fitdir+"/cat%i_fail_cat%i/%s" % (index,index,ish)

        histograms_fail.append( fml.Get("shapes_"+fitdir+"/cat%i_fail_cat%i/%s" % (index,index,ish)) )
        histograms_pass.append( fml.Get("shapes_"+fitdir+"/cat%i_pass_cat%i/%s" % (index,index,ish)) )
        print fitdir
        rags = fml.Get("norm_"+fitdir)
        rags.Print()

        rrv_fail = r.RooRealVar(rags.find("cat%i_fail_cat%i/%s" % (index,index,ish)))
        curnorm_fail = rrv_fail.getVal()
        rrv_pass = r.RooRealVar(rags.find("cat%i_pass_cat%i/%s" % (index,index,ish)))
        curnorm_pass = rrv_pass.getVal()

        print ish, curnorm_fail, curnorm_pass, index
        if curnorm_fail > 0.: histograms_fail[i].Scale(curnorm_fail/histograms_fail[i].Integral())
        if curnorm_pass > 0.: histograms_pass[i].Scale(curnorm_pass/histograms_pass[i].Integral())

    wp = fd.Get("w_pass_cat%i" % (index))
    wf = fd.Get("w_fail_cat%i" % (index))
    rdhp = wp.data("data_obs_pass_cat%i" % (index))
    rdhf = wf.data("data_obs_fail_cat%i" % (index))
    rrv   = wp.var("x")

    data_fail = rdhf.createHistogram("data_fail_cat"+str(index)+"_"+fittype,rrv,r.RooFit.Binning(histograms_pass[0].GetNbinsX()))
    data_pass = rdhp.createHistogram("data_pass_cat"+str(index)+"_"+fittype,rrv,r.RooFit.Binning(histograms_pass[0].GetNbinsX()))

    histograms_fail.append(data_fail)
    histograms_pass.append(data_pass)

    makeMLFitCanvas(histograms_fail[:4], data_fail, histograms_fail[4:], shapes, "fail_cat"+str(index)+"_"+fittype,options.odir)
    makeMLFitCanvas(histograms_pass[:4], data_pass, histograms_pass[4:], shapes, "pass_cat"+str(index)+"_"+fittype,options.odir)

    return (histograms_pass,histograms_fail)

###############################################################

def makeMLFitCanvas(bkgs, data, hsigs, leg, tag, odir='cards'):
    htot = bkgs[0].Clone("htot")
    for ih in range(1,len(bkgs)):
        htot.Add(bkgs[ih])
    hsig = hsigs[0].Clone("hsig")

    for ih in range(1,len(hsigs)):
        hsig.Add(hsigs[ih])
    # for ih in range(len(bkgs)): print bkgs[ih].GetNbinsX(), bkgs[ih].GetBinLowEdge(1), bkgs[ih].GetBinLowEdge( bkgs[ih].GetNbinsX() ) + bkgs[ih].GetBinWidth( bkgs[ih].GetNbinsX() );


    htot.SetLineColor(r.kBlack)
    colors = [r.kRed, r.kBlue, r.kMagenta, r.kGreen+1, r.kCyan + 1]
    for i,b in enumerate(bkgs): 
    #	b.SetFillColor(colors[i])
        b.SetLineColor(colors[i])
        b.SetLineStyle(i+2)
        b.SetLineWidth(2)
    hsig.SetLineColor(r.kBlack)
    hsig.SetLineStyle(2)
    hsig.SetLineWidth(2)

    l = r.TLegend(0.7,0.6,0.9,0.85)
    l.SetFillStyle(0)
    l.SetBorderSize(0)
    l.SetTextFont(42)
    l.SetTextSize(0.035)
    legnames = {'wqq':'W','zqq':'Z','qcd':'QCD','tqq':'t#bar{t}'}
    for i in range(len(bkgs)):
        l.AddEntry(bkgs[i],legnames[leg[i]],"l")
    l.AddEntry(htot,"Total Bkg.","lf")
    l.AddEntry(hsig,"H(b#bar{b})","l")


    if data != None:
        l.AddEntry(data,"Data","pe")

    c = r.TCanvas("c","c",1000,800)
    htot.SetFillStyle(3004)
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
    for b in bkgs: 
    #	b.SetFillStyle(1001)
        b.Draw('hist sames')
    #hsig.SetFillStyle(1001)
    #hsig.SetFillColor(r.kGray+1)
    #hsig.Draw('hist sames')
    if data != None:
        data.Draw('pezsame')
    l.Draw()    
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
    c.SaveAs(odir+"/mlfit/mlfit_"+tag+".pdf")
    c.SaveAs(odir+"/mlfit/mlfit_"+tag+".C")
    data.SetMinimum(5e-1)
    r.gPad.SetLogy()
    data.SetMaximum(data.GetMaximum()*2)
    c.SaveAs(odir+"/mlfit/mlfit_"+tag+"-log.pdf")
    c.SaveAs(odir+"/mlfit/mlfit_"+tag+"-log.C")
    
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
    f2 = r.TF2("f2",fun2, 40+3.5, 201-3.5, 500+25, 1000-100, npar)
    f2.SetParameters(f2params)

    c = r.TCanvas("c","c",1000,800)
    c.SetFillStyle(4000)
    c.SetFrameFillStyle(1000)
    c.SetFrameFillColor(0)
    ratio.Draw('surf1')
    #ratio.Fit('f2','RN')
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

    c.SaveAs(options.odir+"/mlfit/tf.pdf")
    c.SaveAs(options.odir+"/mlfit/tf.C")

    
    for i in range(0,360):        
        r.gPad.SetPhi(30+270+i)
        r.gPad.Modified()
        r.gPad.Update()
        c.SaveAs(options.odir+"/mlfit/tf_%03d.png"%i)
##-------------------------------------------------------------------------------------
if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
	parser.add_option("--lumi", dest="lumi", type=float, default = 30,help="luminosity", metavar="lumi")
	parser.add_option('-i','--idir', dest='idir', default = 'cards/',help='directory with data', metavar='idir')
	parser.add_option('-o','--odir', dest='odir', default = 'cards/',help='directory for plots', metavar='odir')
	parser.add_option('--fit', dest='fit', default = 'prefit',help='choice is either prefit, fit_s or fit_b', metavar='fit')
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
