#!/usr/bin/env python
import ROOT as r,sys,math,os
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array
#r.gSystem.Load("~/Dropbox/RazorAnalyzer/python/lib/libRazorRun2.so")
r.gSystem.Load(os.getenv('CMSSW_BASE')+'/lib/'+os.getenv('SCRAM_ARCH')+'/libHiggsAnalysisCombinedLimit.so')


# including other directories
sys.path.insert(0, '../.')
from tools import *
from hist import *
from rhalphabet_builder import RhalphabetBuilder, LoadHistograms

NBINS = 23
MASS_LO = 40
MASS_HI = 201
BLIND_LO = 110
BLIND_HI = 131
RHO_LO = -6
RHO_HI = -2.1

def main(options, args):
    
    ifile = options.ifile
    odir = options.odir

    # Load the input histograms
    #   - 2D histograms of pass and fail mass,pT distributions
    #   - for each MC sample and the data
    f = r.TFile.Open(ifile)
    (pass_hists,fail_hists) = LoadHistograms(f, options.pseudo, options.blind, options.useQCD, mass_range=[MASS_LO, MASS_HI], blind_range=[BLIND_LO, BLIND_HI])
    f.Close()

    # Build the workspaces
    rhalphabuilder = RhalphabetBuilder(pass_hists, fail_hists, options.odir, mass_nbins=MASS_BINS, mass_lo=MASS_LO, mass_hi=MASS_HI, blind_lo=BLIND_LO, blind_hi=BLIND_HI, mass_fit=options.mass_fit, freeze_poly=options.freeze_poly)
    # rhalphabuilder._poly_degree_pt = 2
    # rhalphabuilder._poly_degree_rho = 2
    rhalphabuilder.run()


##-------------------------------------------------------------------------------------
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('-i','--ifile', dest='ifile', default='hist_1DZbb.root',help='file with histogram inputs', metavar='ifile')
    parser.add_option('-o','--odir', dest='odir', default = './',help='directory to write plots', metavar='odir')
    parser.add_option('--pseudo', action='store_true', dest='pseudo', default =False,help='use MC', metavar='pseudo')
    parser.add_option('--blind', action='store_true', dest='blind', default =False,help='blind signal region', metavar='blind')
    parser.add_option('--use-qcd', action='store_true', dest='useQCD', default =False,help='use real QCD MC', metavar='useQCD')
    parser.add_option('--massfit', action='store_true', dest='massfit', default =False,help='mass fit or rho', metavar='massfit')
    parser.add_option('--freeze', action='store_true', dest='freeze', default =False,help='freeze pol values', metavar='freeze')
    parser.add_option('--scale',dest='scale', default=1,type='float',help='scale factor to scale MC (assuming only using a fraction of the data)')
    parser.add_option('--nr', dest='NR', default=2, type='int', help='order of rho (or mass) polynomial')
    parser.add_option('--np', dest='NP', default=2, type='int', help='order of pt polynomial')


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
