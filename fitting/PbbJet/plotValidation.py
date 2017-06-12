#!/usr/bin/env python
import ROOT as rt,sys,math,os
import numpy as np
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time

# including other directories
#sys.path.insert(0, '../.')
#from tools import *
#from RootIterator import RootIterator

from array import array

def main(options, args):
    tfile = rt.TFile.Open(options.idir+'/validation.root')
    
    bkgs = ['wqq','zqq','tqq']
    #sigs = ['hqq125','tthqq125','whqq125','zhqq125','vbfhqq125']
    sigs = ['DMSbb50','DMSbb100','DMSbb200','DMSbb300']
    procdict = {}
    procdict['tqq'] = 't#bar{t}'
    procdict['wqq'] = 'W(qq)'
    procdict['zqq'] = 'Z(qq)'
    procdict['hqq125'] = 'ggH(b#bar{b})'
    procdict['tthqq125'] = 'ttH(b#bar{b})'
    procdict['whqq125'] = 'WH(b#bar{b})'
    procdict['zhqq125'] = 'ZH(b#bar{b})'
    procdict['vbfhqq125'] = 'VBF H(b#bar{b})'
    procdict['DMSbb50'] = '#Phi(b#bar{b}), m = 50 GeV'
    procdict['DMSbb100'] = '#Phi(b#bar{b}), m = 100 GeV'
    procdict['DMSbb200'] = '#Phi(b#bar{b}), m = 200 GeV'
    procdict['DMSbb300'] = '#Phi(b#bar{b}), m = 300 GeV'
    boxes = ['pass_cat1','pass_cat2','pass_cat3','pass_cat4','pass_cat5','pass_cat6',
             'fail_cat1','fail_cat2','fail_cat3','fail_cat4','fail_cat5','fail_cat6']
    #systs = ['JER','JES','scale','smear','trigger','Pu']
    systs = ['scale','smear']
    
    #numberOfMassBins = 23    
    #numberOfPtBins = 6
    #for box in boxes:
    #    for proc in (bkgs+sigs):
    #        for i in range(1,numberOfMassBins+1):
    #            systs.append('%s%s%s%i'%(proc,box.replace('_',''),'mcstat',i))        

    shapes = {}
    
    c = rt.TCanvas("c","c",1000,800)    
    for box in boxes:
        for proc in (bkgs+sigs):
            print proc, box
            tmph = tfile.Get('%s_%s'%(proc,box))
            tmph.SetMaximum(2.*tmph.GetMaximum())
            tmph.SetLineColor(rt.kBlack)
            tmph.GetXaxis().SetTitle('m_{SD} (GeV)')
            for syst in systs:
                tmphUp = tfile.Get('%s_%s_%sUp'%(proc,box,syst))
                tmphDown = tfile.Get('%s_%s_%sDown'%(proc,box,syst))
                try:
                    if not tmphUp.InheritsFrom('TH1'):
                        continue
                except:
                    continue
                if 'mcstat' in syst:
                    iBin = int(syst.split('mcstat')[-1])
                    diff = (tmphUp.GetBinContent(iBin)-tmphDown.GetBinContent(iBin))/2.   
                    ave = (tmphUp.GetBinContent(iBin)+tmphDown.GetBinContent(iBin))/2.
                    cen = tmph.GetBinContent(iBin)
                    #print proc, box, syst, iBin, diff, ave, cen, tmphUp.GetBinContent(iBin), tmphDown.GetBinContent(iBin)
                    if ave<=0.: continue
                    if diff <= 0.5*ave: continue
                tmphUp.SetLineColor(rt.kBlue)
                tmphUp.SetLineStyle(2)
                tmphDown.SetLineColor(rt.kRed)
                tmphDown.SetLineStyle(3)
                tmph.Draw('hist')
                tmphUp.Draw('histsame')
                tmphDown.Draw('histsame')    
                tLeg = rt.TLegend(0.2,0.6,0.44,0.89)
                tLeg.SetLineColor(rt.kWhite)
                tLeg.SetFillColor(rt.kWhite)
                tLeg.SetLineWidth(0)
                tLeg.SetTextFont(42)
                tLeg.SetFillStyle(0)
                tLeg.AddEntry(tmph,"%s, %s"%(procdict[proc],box.replace('_',', ')),"l")
                nsigma = 1
                if syst in ['scale']:
                    nsigma = 10         
                if syst in ['smear']:
                    nsigma = 2                     
                tLeg.AddEntry(tmphUp,"%s +%i#sigma"%(syst,nsigma),"l")
                tLeg.AddEntry(tmphDown,"%s -%i#sigma"%(syst,nsigma),"l")
                tLeg.Draw('same')
                #c.Print('%s/%s_%s_%s.pdf'%(options.odir,proc,box,syst))
                #c.Print('%s/%s_%s_%s.C'%(options.odir,proc,box,syst))
                c.Print('%s/%s_%s_%s.gif'%(options.odir,proc,box,syst))
                #c.Print('%s/png/%s_%s_%s.png'%(options.odir,proc,box,syst))
            
    
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
    rt.gStyle.SetPalette(1)
    rt.gStyle.SetPaintTextFormat("1.1f")
    rt.gStyle.SetOptFit(0000)
    rt.gROOT.SetBatch()

    main(options, args)

