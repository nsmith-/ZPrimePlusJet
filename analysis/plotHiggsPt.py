import ROOT as rt
import math
import sys
import time
import array

if __name__ == '__main__':
    tfile = rt.TFile.Open("sklimming/signalXS/Higgs.root")
    tfile_tth = rt.TFile.Open("sklimming/signalXS/tth.root")

    hpt = {}
    hpt['ggh'] =  tfile.Get("ggh_hpt_binwdith")
    hpt['tth'] = tfile_tth.Get("hpt_binWidth")
    hpt['vbf'] = tfile.Get("vbf_hpt_binwdith")

    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetOptTitle(0)
    rt.gROOT.SetBatch()
    c = rt.TCanvas('c','c',500,400)
    c.SetBottomMargin(0.12)
    c.SetLeftMargin(0.12)

    hpt['ggh'].SetLineColor(rt.kRed)
    hpt['vbf'].SetLineColor(rt.kGreen)
    hpt['tth'].SetLineColor(rt.kBlue)
    hpt['ggh'].SetMarkerColor(rt.kRed)
    hpt['vbf'].SetMarkerColor(rt.kGreen)
    hpt['tth'].SetMarkerColor(rt.kBlue)
    hpt['ggh'].SetMarkerStyle(20)
    hpt['vbf'].SetMarkerStyle(20)
    hpt['tth'].SetMarkerStyle(20)
    hpt['ggh'].SetMarkerSize(0.5)
    hpt['vbf'].SetMarkerSize(0.5)
    hpt['tth'].SetMarkerSize(0.5)
    hpt['tth'].Scale(1000.)
    
    hpt['tth'].GetXaxis().SetTitle('Higgs p_{T} (GeV)')
    hpt['tth'].GetYaxis().SetTitle('d#sigma/dp_{T} (fb/GeV)')
    hpt['tth'].GetXaxis().SetTitleSize(0.05)
    hpt['tth'].GetYaxis().SetTitleSize(0.05)
    hpt['tth'].GetXaxis().SetLabelSize(0.04)
    hpt['tth'].GetYaxis().SetLabelSize(0.04)
    hpt['tth'].SetMaximum(1e4)
    hpt['tth'].Draw('pez')
    hpt['ggh'].Draw('pezsame')
    hpt['vbf'].Draw('pezsame')
    hpt['tth'].Draw('pezsame')
    
    c.SetLogy()
    leg = rt.TLegend(0.6,0.7,0.9,0.9)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.05)
    leg.AddEntry(hpt['ggh'],'ggH','pe')
    leg.AddEntry(hpt['vbf'],'VBF H','pe')
    leg.AddEntry(hpt['tth'],'ttH','pe')
    leg.Draw()

    c.Print("hpt.pdf")
    c.Print("hpt.C")

    
