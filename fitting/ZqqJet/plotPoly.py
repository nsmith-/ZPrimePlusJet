import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array


def makeTF():

    par = [0.0720440015378454, 0.0003889369394270148, 7.95764967791851e-08, -5.111705262631633e-10, 0.07708032586904112, 6.80182224468695e-05, 1.3285240501453854e-08, -9.836573591250064e-11, -0.01644955233687273, -5.415718956541804e-06, 1.2176447848274985e-08, 2.195316064351749e-11, -0.0019296052485793247, -4.595025706544131e-06, -2.857007243631249e-09, 1.1505536974543151e-11]

    tf = ROOT.TF2("tf","[0]*((1+[1]*x+[2]*x*x+[3]*x*x*x)+([4]+[5]*x+[6]*x*x+[7]*x*x*x)*y+([8]+[9]*x+[10]*x*x+[11]*x*x*x)*y*y+([12]+[13]*x+[14]*x*x+[15]*x*x*x)*y*y*y)", 500, 1000, -6, -2)
    tf.SetParameter(0,1)
    tf.SetParameter(0,par[0])
    tf.SetParameter(1,par[1])
    tf.SetParameter(2,par[2])
    tf.SetParameter(3,par[3])
    tf.SetParameter(4,par[4])
    tf.SetParameter(5,par[5])
    tf.SetParameter(6,par[6])
    tf.SetParameter(7,par[7])
    tf.SetParameter(8,par[8])
    tf.SetParameter(9,par[9])
    tf.SetParameter(10,par[10])
    tf.SetParameter(11,par[11])
    tf.SetParameter(12,par[12])
    tf.SetParameter(13,par[13])
    tf.SetParameter(14,par[14])
    tf.SetParameter(15,par[15])

    c = ROOT.TCanvas("c","c",1000,800)
    c.SetFillStyle(4000)
    c.SetFrameFillStyle(1000)
    c.SetFrameFillColor(0)
    tf.GetZaxis().SetRangeUser(0.025,0.075)
    #tf.Draw("surf bb")
    tf.Draw("colz")

    #ROOT.gPad.SetTheta(30)
    #ROOT.gPad.SetPhi(30+270)
    #ROOT.gPad.Modified()
    #ROOT.gPad.Update()
   
    tag1 = ROOT.TLatex(0.67,0.92,"2.3 fb^{-1} (13 TeV)")
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

    
    c.SaveAs("colzPoly.pdf")
    c.SaveAs("colzPoly.C")

import tdrstyle
tdrstyle.setTDRStyle()
ROOT.gStyle.SetPadTopMargin(0.10)
ROOT.gStyle.SetPadLeftMargin(0.16)
ROOT.gStyle.SetPadRightMargin(0.10)
ROOT.gStyle.SetPaintTextFormat("1.1f")
ROOT.gStyle.SetOptFit(0000)
ROOT.gStyle.SetPalette(ROOT.kBird)
ROOT.gROOT.SetBatch()

makeTF()
