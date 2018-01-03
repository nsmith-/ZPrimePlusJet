#!/usr/bin/env python
import ROOT as rt,sys,math,os
import numpy as np
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time

# including other directories
#sys.path.insert(0, '../.')

def main(options, args):
    
        lumi_GH = 16.146
        lumi_BCDEF = 19.721
        lumi_total = lumi_GH + lumi_BCDEF
        
        f_trig = rt.TFile.Open(
            "$ZPRIMEPLUSJET_BASE/analysis/ggH/RUNTriggerEfficiencies_SingleMuon_Run2016_V2p1_v03.root", "read")
        trig_denom = f_trig.Get("DijetTriggerEfficiencySeveralTriggers/jet1SoftDropMassjet1PtDenom_cutJet")
        trig_numer = f_trig.Get("DijetTriggerEfficiencySeveralTriggers/jet1SoftDropMassjet1PtPassing_cutJet")
        trig_denom.SetDirectory(0)
        trig_numer.SetDirectory(0)
        trig_denom.RebinX(2)
        trig_numer.RebinX(2)
        trig_denom.RebinY(5)
        trig_numer.RebinY(5)
        trig_eff = rt.TEfficiency()
        if (rt.TEfficiency.CheckConsistency(trig_numer, trig_denom)):
            trig_eff = rt.TEfficiency(trig_numer, trig_denom)
            trig_eff.SetDirectory(0)
        f_trig.Close()

        c = rt.TCanvas('c','c',500,500)
        c.SetRightMargin(0.15)
        trig_eff.Draw('colztexte')
        trig_eff.Paint('colztexte')
        
        hist_eff = trig_eff.GetPaintedHistogram()
        hist_eff.SetMarkerSize(1.0)
        hist_eff.GetYaxis().SetRangeUser(0,1000)
        hist_eff.GetXaxis().SetRangeUser(0,300)
        hist_eff.Draw('colztext')
        hist_eff.GetXaxis().SetTitle('AK8 m_{SD} (GeV)')
        hist_eff.GetYaxis().SetTitle('AK8 p_{T} (GeV)')

        tlatex = []
        l = rt.TLatex()                
        l.SetTextSize(0.011)
        l.SetTextAlign(13)
        for i in range(1,hist_eff.GetNbinsX()+1):
            for j in range(1,hist_eff.GetNbinsY()+1):
                massForTrig = hist_eff.GetXaxis().GetBinCenter(i)
                ptForTrig = hist_eff.GetYaxis().GetBinCenter(j)
                eff = trig_eff.GetEfficiency(trig_eff.FindFixBin(massForTrig, ptForTrig))
                errUp = trig_eff.GetEfficiencyErrorUp(trig_eff.FindFixBin(massForTrig, ptForTrig))
                errDown = trig_eff.GetEfficiencyErrorLow(trig_eff.FindFixBin(massForTrig, ptForTrig))
                hist_eff.SetBinError(i,j,max(errUp,errDown))
                #if eff > 0 and massForTrig < 300 and ptForTrig < 1000:
                #    l.DrawLatex(massForTrig-5,ptForTrig+20,"#splitline{%.3f}{#splitline{+%.3f}{-%.3f}}"%(eff,errUp,errDown))
            
        tag1 = rt.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi_total)
        tag1.SetNDC(); tag1.SetTextFont(42)
        tag1.SetTextSize(0.033)
        tag2 = rt.TLatex(0.17,0.92,"CMS")
        tag2.SetNDC(); tag2.SetTextFont(62)
        tag3 = rt.TLatex(0.25,0.92,"  Preliminary")
        tag3.SetNDC(); tag3.SetTextFont(52)
        tag2.SetTextSize(0.042); tag3.SetTextSize(0.033);
        tag1.Draw(); tag2.Draw(); tag3.Draw()
        c.Print('trig_eff.pdf')
        
        d = rt.TCanvas('d','d',600,500)
        d.SetRightMargin(0.15)
        # get muon trigger efficiency object
        
        f_mutrig_GH = rt.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ggH/EfficienciesAndSF_Period4.root", "read")
        mutrig_eff_GH = f_mutrig_GH.Get("Mu50_OR_TkMu50_PtEtaBins/efficienciesDATA/pt_abseta_DATA")
        mutrig_eff_GH.Sumw2()
        mutrig_eff_GH.SetDirectory(0)
        f_mutrig_GH.Close()

        f_mutrig_BCDEF = rt.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ggH/EfficienciesAndSF_RunBtoF.root", "read")
        mutrig_eff_BCDEF = f_mutrig_BCDEF.Get("Mu50_OR_TkMu50_PtEtaBins/efficienciesDATA/pt_abseta_DATA")
        mutrig_eff_BCDEF.Sumw2()
        mutrig_eff_BCDEF.SetDirectory(0)
        f_mutrig_BCDEF.Close()

        mutrig_eff = mutrig_eff_GH.Clone('pt_abseta_DATA_mutrig_ave')
        mutrig_eff.Scale(lumi_GH / lumi_total)
        mutrig_eff.Add(mutrig_eff_BCDEF, lumi_BCDEF / lumi_total)

        d.SetLogx()
        mutrig_eff.SetMinimum(0)
        mutrig_eff.SetMaximum(1)
        mutrig_eff.GetXaxis().SetMoreLogLabels(1)
        mutrig_eff.GetXaxis().SetNoExponent()
        mutrig_eff.Draw('colztexte')
        rt.gStyle.SetPaintTextFormat("3.3f")
        
        tag1 = rt.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi_total)
        tag1.SetNDC(); tag1.SetTextFont(42)
        tag1.SetTextSize(0.033)
        tag2 = rt.TLatex(0.17,0.92,"CMS")
        tag2.SetNDC(); tag2.SetTextFont(62)
        tag3 = rt.TLatex(0.25,0.92,"Preliminary")
        tag3.SetNDC(); tag3.SetTextFont(52)
        tag2.SetTextSize(0.042); tag3.SetTextSize(0.033);
        tag1.Draw(); tag2.Draw(); tag3.Draw()        
        d.Print('mutrig_eff.pdf') 
        
        f_muid_GH = rt.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ggH/EfficienciesAndSF_GH.root", "read")
        muid_eff_GH = f_muid_GH.Get("MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta/efficienciesDATA/pt_abseta_DATA")
        muid_eff_GH.Sumw2()
        muid_eff_GH.SetDirectory(0)
        f_muid_GH.Close()

        f_muid_BCDEF = rt.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ggH/EfficienciesAndSF_BCDEF.root", "read")
        muid_eff_BCDEF = f_muid_BCDEF.Get(
            "MC_NUM_LooseID_DEN_genTracks_PAR_pt_eta/efficienciesDATA/pt_abseta_DATA")
        muid_eff_BCDEF.Sumw2()
        muid_eff_BCDEF.SetDirectory(0)
        f_muid_BCDEF.Close()

        
        muid_eff = muid_eff_GH.Clone('pt_abseta_DATA_muid_ave')
        muid_eff.Scale(lumi_GH / lumi_total)
        muid_eff.Add(muid_eff_BCDEF, lumi_BCDEF / lumi_total)

        
        muid_eff.SetMinimum(0)
        muid_eff.SetMaximum(1)
        muid_eff.GetXaxis().SetMoreLogLabels(1)
        muid_eff.GetXaxis().SetNoExponent()
        #muid_eff.GetZaxis().SetTitle('')
        muid_eff.Draw('colztexte')
        rt.gPad.Modified()
        rt.gPad.Update()
        rt.gStyle.SetPaintTextFormat("3.3f")
        
        tag1 = rt.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi_total)
        tag1.SetNDC(); tag1.SetTextFont(42)
        tag1.SetTextSize(0.033)
        tag2 = rt.TLatex(0.17,0.92,"CMS")
        tag2.SetNDC(); tag2.SetTextFont(62)
        tag3 = rt.TLatex(0.25,0.92,"Preliminary")
        tag3.SetNDC(); tag3.SetTextFont(52)
        tag2.SetTextSize(0.042); tag3.SetTextSize(0.033);
        tag1.Draw(); tag2.Draw(); tag3.Draw()
        d.Print('muid_eff.pdf')
        

        f_muiso_GH = rt.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ggH/EfficienciesAndSF_ISO_GH.root", "read")
        muiso_eff_GH = f_muiso_GH.Get("LooseISO_LooseID_pt_eta/efficienciesDATA/pt_abseta_DATA")
        muiso_eff_GH.Sumw2()
        muiso_eff_GH.SetDirectory(0)
        f_muiso_GH.Close()

        f_muiso_BCDEF = rt.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ggH/EfficienciesAndSF_ISO_BCDEF.root", "read")
        muiso_eff_BCDEF = f_muiso_BCDEF.Get("LooseISO_LooseID_pt_eta/efficienciesDATA/pt_abseta_DATA")
        muiso_eff_BCDEF.Sumw2()
        muiso_eff_BCDEF.SetDirectory(0)
        f_muiso_BCDEF.Close()

        muiso_eff = muiso_eff_GH.Clone('pt_abseta_DATA_muiso_ave')
        muiso_eff.Scale(lumi_GH / lumi_total)
        muiso_eff.Add(muiso_eff_BCDEF, lumi_BCDEF / lumi_total)
        
        muiso_eff.SetMinimum(0)
        muiso_eff.SetMaximum(1)
        muiso_eff.GetXaxis().SetMoreLogLabels(1)
        muiso_eff.GetXaxis().SetNoExponent()
        muiso_eff.Draw('colztexte')
        rt.gStyle.SetPaintTextFormat("4.4f")
        
        tag1 = rt.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi_total)
        tag1.SetNDC(); tag1.SetTextFont(42)
        tag1.SetTextSize(0.033)
        tag2 = rt.TLatex(0.17,0.92,"CMS")
        tag2.SetNDC(); tag2.SetTextFont(62)
        tag3 = rt.TLatex(0.25,0.92,"Preliminary")
        tag3.SetNDC(); tag3.SetTextFont(52)
        tag2.SetTextSize(0.042); tag3.SetTextSize(0.033);
        tag1.Draw(); tag2.Draw(); tag3.Draw()
        d.Print('muiso_eff.pdf')

        
    
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('--lumi', dest='lumi', type=float, default = 20,help='lumi in 1/fb ', metavar='lumi')
    parser.add_option('-i','--idir', dest='idir', default = './',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = './',help='directory to write cards', metavar='odir')
    
    (options, args) = parser.parse_args()
    import tdrstyle
    tdrstyle.setTDRStyle()
    rt.gStyle.SetPadTopMargin(0.10)
    rt.gStyle.SetPadLeftMargin(0.16)
    rt.gStyle.SetPadRightMargin(0.10)
    #rt.gStyle.SetPaintTextFormat("5.5f")
    rt.gStyle.SetPaintTextFormat("2.2f")
    rt.gStyle.SetOptFit(0000)
    rt.gStyle.SetPalette(rt.kBird)
    rt.gStyle.SetNumberContours(999)
    rt.gROOT.SetBatch()

    main(options, args)
