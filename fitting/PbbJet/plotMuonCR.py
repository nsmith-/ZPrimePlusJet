import ROOT as rt
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array
import os


# including other directories
sys.path.insert(0, '../.')
from tools import *

def main(options, args):
    fml = rt.TFile.Open(options.idir+'/mlfit.root','read')


    #bkgs = ['qcd','tqq','stqq','zqq','wqq','wlnu','vvqq','zll','total_background']
    bkgs = ['qcd','tqq','stqq','zqq','wqq','wlnu','vvqq','total_background']
    sigs = ['hqq125','tthqq125','whqq125','zhqq125']
    data = ['data']
    boxes = ['fail_muonCR','pass_muonCR']

    shapes = {}
    for box in boxes:
        for proc in (bkgs+sigs+data):
            tmph = fml.Get('shapes_%s/%s/%s'%(options.fit,box,proc))
            if tmph is not None:
                try:                    
                    tmph.InheritsFrom('TH1')
                except:
                    continue
                if tmph.InheritsFrom('TH1'):
                    tmph.Sumw2()
                    binWidth = tmph.GetXaxis().GetBinUpEdge(1)-tmph.GetXaxis().GetBinLowEdge(1)
                    tmph.Scale(binWidth)
                    shapes['%s_%s'%(box,proc)] = tmph
                elif tmph.InheritsFrom('TGraph'):                    
                    alpha = 1-0.6827
                    for i in range(0,tmph.GetN()):                            
                        binWidth = tmph.GetEXlow()[i] + tmph.GetEXhigh()[i]
                        N = tmph.GetY()[i]*binWidth
                        L = 0
                        if N!=0:
                            L = rt.Math.gamma_quantile(alpha/2,N,1.)
                        U = rt.Math.gamma_quantile_c(alpha/2,N+1,1)
                        tmph.SetPointEYlow(i, (N-L))
                        tmph.SetPointEYhigh(i, (U-N))
                        tmph.SetPoint(i, tmph.GetX()[i], N)                        
                    shapes['%s_%s'%(box,proc)] = tmph

    print shapes
    
    for box in boxes:
        
        c = rt.TCanvas("c%s"%box,"c%s"%box,1000,800)    
        rt.SetOwnership(c, False)
        p12 = rt.TPad("p12%s"%box,"p12%s"%box,0.0,0.3,1.0,1.0)
        p22 = rt.TPad("p22%s"%box,"p22%s"%box,0.0,0.0,1.0,0.3)
        p12.SetBottomMargin(0.02)
        p22.SetTopMargin(0.05)
        p22.SetBottomMargin(0.3)
        
        c.cd()
        p12.Draw()
        p12.cd()
        
        htot = shapes['%s_%s'%(box,'total_background')]
        datagraph = shapes['%s_%s'%(box,'data')]
        data = htot.Clone('%s_%s'%(box,'data'))
        for i in range(1,data.GetNbinsX()+1):
            data.SetBinContent(i,0)
            data.SetBinError(i,0)
        for i in range(1,data.GetNbinsX()+1):
            data.SetBinContent(i,datagraph.GetY()[i-1])
            if datagraph.GetY()[i-1]>=1:
                data.SetBinError(i,rt.TMath.Sqrt(datagraph.GetY()[i-1]))
            else:
                data.SetBinError(i,1)
        
        l = r.TLegend(0.7,0.6,0.9,0.85)
        l.SetFillStyle(0)
        l.SetBorderSize(0)
        l.SetTextFont(42)
        l.SetTextSize(0.035)
        l.AddEntry(htot,"Total Bkg.","lf")
        l.AddEntry(datagraph,"Data","pe")

        
        htot.SetLineColor(rt.kBlack)
        #htot.SetFillStyle(3004)
        #htot.SetFillColor(r.kGray+1)
        htot.SetFillStyle(3001)
        htot.SetFillColor(4)
        #htot.SetLineColor(r.kGray+2)
        htot.SetLineColor(r.kBlue+1)        
        htot.SetMinimum(0)
        htot.SetMarkerSize(0)
        htot.SetMarkerColor(r.kGray+2)
        htot.SetLineWidth(2)
        data.GetXaxis().SetTitle('m_{SD}^{PUPPI} (GeV)')
        datagraph.SetMarkerStyle(20)
        htot_line = htot.Clone('htot_line%s'%box)
        htot_line.SetFillStyle(0)
        data.GetYaxis().SetTitle('Events')
        data.Draw('pez')
        htot.Draw('E2same')        
        htot_line.Draw('histsame')
        
        datagraph.Draw('pezsame')
        
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
        data.SetMaximum(data.GetMaximum()*2.1)
        data.SetMinimum(0)
        
        c.cd()
        p22.Draw()
        p22.cd()
        p22.SetGrid()
        iRatio = data.Clone('iRatio%s'%box)
        iRatio.SetLineColor(rt.kBlack)
        for i in range(iRatio.GetNbinsX()):            
            if htot.GetBinContent(i+1) > 0:
                iRatio.SetBinContent( i+1, data.GetBinContent(i+1)/htot.GetBinContent(i+1) )
                iRatio.SetBinError( i+1, data.GetBinError(i+1)/htot.GetBinContent(i+1) )
        iRatioGraph = rt.TGraphAsymmErrors(iRatio)        
        alpha = 1-0.6827
        for i in range(0,iRatioGraph.GetN()):
            N = iRatioGraph.GetY()[i]*htot.GetBinContent(i+1)
            L = 0
            if N!=0:
                L = rt.Math.gamma_quantile(alpha/2,N,1.)
            U = rt.Math.gamma_quantile_c(alpha/2,N+1,1)
            iRatioGraph.SetPointEYlow(i, (N-L)/htot.GetBinContent(i+1))
            iRatioGraph.SetPointEYhigh(i, (U-N)/htot.GetBinContent(i+1))
            iRatioGraph.SetPoint(i, iRatioGraph.GetX()[i], N/htot.GetBinContent(i+1) )
        
        data.GetXaxis().SetTitleOffset(100)
        data.GetXaxis().SetLabelOffset(100)
        iRatio.SetTitle("; m_{SD}^{PUPPI} (GeV); Data/Prediction")
        iRatio.SetMaximum(1.5)
        iRatio.SetMinimum(0.)
        iRatio.GetYaxis().SetTitleSize(0.13)
        iRatio.GetYaxis().SetNdivisions(6)
        iRatio.GetYaxis().SetLabelSize(0.12)
        iRatio.GetYaxis().SetTitleOffset(0.44)
        iRatio.GetXaxis().SetTitleSize(0.13)
        iRatio.GetXaxis().SetLabelSize(0.12)
        iRatio.GetXaxis().SetTitleOffset(0.9)
        #iRatio.GetYaxis().SetRangeUser(0.51,1.49)
        iRatio.GetYaxis().SetRangeUser(0.,3.5)
        iRatio.SetMarkerStyle(20)
        iRatio.SetLineColor(rt.kBlack)
        iOneWithErrors = htot.Clone('iOneWithErrors%s'%box)
        iOneWithErrors.Divide(htot.Clone())
        for i in range(iOneWithErrors.GetNbinsX()): 
            if htot.GetBinContent(i+1) > 0:
                iOneWithErrors.SetBinError( i+1, htot.GetBinError(i+1)/htot.GetBinContent(i+1) )
            else:
                iOneWithErrors.SetBinError( i+1, 1)


                
        #iOneWithErrors.SetFillStyle(3004)
        #iOneWithErrors.SetFillColor(r.kGray+1)
        iOneWithErrors.SetFillStyle(3001)
        iOneWithErrors.SetFillColor(4)
        #iOneWithErrors.SetLineColor(r.kGray+2)
        iOneWithErrors.SetLineColor(r.kBlue+1)
        iOneWithErrors.SetMarkerSize(0)
        iOneWithErrors.SetLineWidth(2)
        iRatio.Draw('pez')
        iOneWithErrorsLine = iOneWithErrors.Clone('iOneWithErrorsLine%s'%box)
        iOneWithErrorsLine.SetFillStyle(0)
        iOneWithErrorsLine.Draw("hist sames")
        iOneWithErrors.Draw("e2 sames")
        iRatioGraph.Draw("pezsames")
        
        c.Print(options.odir+'/'+box+'_'+options.fit+'.pdf')
        c.Print(options.odir+'/'+box+'_'+options.fit+'.C')

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('--lumi', dest='lumi', type=float, default = 20,help='lumi in 1/fb ', metavar='lumi')
    parser.add_option('-i','--idir', dest='idir', default = './',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = './',help='directory to write cards', metavar='odir')
    parser.add_option('--fit', dest='fit', default = 'prefit',help='choice is either prefit, fit_s or fit_b', metavar='fit')
    
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

    main(options, args)
