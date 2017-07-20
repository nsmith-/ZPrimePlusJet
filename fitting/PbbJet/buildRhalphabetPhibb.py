#!/usr/bin/env python
import ROOT as r, sys, math, os
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array

#r.gSystem.Load("~/Dropbox/RazorAnalyzer/python/lib/libRazorRun2.so")
r.gSystem.Load(os.getenv('CMSSW_BASE') + '/lib/' + os.getenv('SCRAM_ARCH') + '/libHiggsAnalysisCombinedLimit.so')

# including other directories
# sys.path.insert(0, '../.')
from tools import *
from hist import *
from rhalphabet_builder_Phibb import RhalphabetBuilder, LoadHistograms, GetSF

#MASS_BINS = 23
#MASS_LO = 40
#MASS_HI = 201
MASS_BINS =80 
MASS_LO = 40
MASS_HI = 600
BLIND_LO = 110
BLIND_HI = 131
#RHO_LO = -6
#RHO_HI = -2.1


def main(options, args):
    ifile = options.ifile
    odir = options.odir

    # Load the input histograms
    # 	- 2D histograms of pass and fail mass,pT distributions
    # 	- for each MC sample and the data
    f = r.TFile.Open(ifile)    
    fLoose = None
    if options.ifile_loose is not None:
        fLoose = r.TFile.Open(options.ifile_loose)
    #(hpass, hfail) = loadHistograms(f, options.pseudo, options.blind, options.useQCD, options.scale, options.r)
    (pass_hists,fail_hists) = LoadHistograms(f, options.pseudo, options.blind, options.useQCD, scale=options.scale, r_signal=options.r, mass_range=[MASS_LO, MASS_HI], blind_range=[BLIND_LO, BLIND_HI], rho_range=[options.lrho, options.hrho], fLoose=fLoose, cuts = options.cuts)
    #f.Close()

    # Build the workspacees
    #dazsleRhalphabetBuilder(hpass, hfail, f, odir, options.NR, options.NP)

    rhalphabuilder = RhalphabetBuilder(pass_hists, fail_hists, f, options.odir, nr=options.NR, np=options.NP, mass_nbins=MASS_BINS, mass_lo=MASS_LO, mass_hi=MASS_HI, blind_lo=BLIND_LO, blind_hi=BLIND_HI, rho_lo=options.lrho, rho_hi=options.hrho, blind=options.blind, mass_fit=options.massfit, freeze_poly=options.freeze, remove_unmatched=options.removeUnmatched, input_file_loose=fLoose, cuts=options.cuts)

    rhalphabuilder.run()
    if options.prefit:
        rhalphabuilder.prefit()
    elif options.loadfit is not None:
        rhalphabuilder.loadfit(options.loadfit)
        

##-------------------------------------------------------------------------------------
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('-i', '--ifile', dest='ifile', default='hist_1DZbb.root', help='file with histogram inputs',
                      metavar='ifile')
    parser.add_option('--ifile-loose', dest='ifile_loose', default=None, help='second file with histogram inputs (looser b-tag cut to take W/Z/H templates)',
                      metavar='ifile_loose')
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write plots', metavar='odir')
    parser.add_option('--pseudo', action='store_true', dest='pseudo', default=False, help='use MC', metavar='pseudo')
    parser.add_option('--blind', action='store_true', dest='blind', default=False, help='blind signal region',
                      metavar='blind')
    parser.add_option('--use-qcd', action='store_true', dest='useQCD', default=False, help='use real QCD MC',
                      metavar='useQCD')
    parser.add_option('--massfit', action='store_true', dest='massfit', default=False, help='mass fit or rho',
                      metavar='massfit')
    parser.add_option('--freeze', action='store_true', dest='freeze', default=False, help='freeze pol values',
                      metavar='freeze')
    parser.add_option('--scale', dest='scale', default=1, type='float',
                      help='scale factor to scale MC (assuming only using a fraction of the data)')
    parser.add_option('--nr', dest='NR', default=2, type='int', help='order of rho (or mass) polynomial')
    parser.add_option('--np', dest='NP', default=1, type='int', help='order of pt polynomial')
    parser.add_option('-r', dest='r', default=0, type='float', help='signal strength for MC pseudodataset')
    parser.add_option('--remove-unmatched', action='store_true', dest='removeUnmatched', default =False,help='remove unmatched', metavar='removeUnmatched')
    parser.add_option('--prefit', action='store_true', dest='prefit', default =False,help='do prefit', metavar='prefit')
    parser.add_option('--loadfit', dest='loadfit', default=None, help='load qcd polynomial parameters from alternative rhalphabase.root',metavar='loadfit')
    parser.add_option('--lrho', dest='lrho', default=-6.0, type= 'float', help='low value rho cut')
    parser.add_option('--hrho', dest='hrho', default=-2.1, type='float', help=' high value rho cut')

    parser.add_option('-c', '--cuts', dest='cuts', default='p9', type='string', help='double b-tag cut value')

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
##-------------------------------------------------------------------------------------
