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
	
	if options.np==2 and options.nr==2:
		dctpl = open("datacard.tpl");
	if options.np==3 and options.nr==2:
                dctpl = open("datacard32.tpl");
	if options.np==2 and options.nr==3:
                dctpl = open("datacard23.tpl");
        if options.np==3 and options.nr==3:
                dctpl = open("datacard33.tpl");

	numberOfMassBins = options.nmass;

	linel = [];
	for line in dctpl: 
		print line.strip().split();
		linel.append(line.strip());

	for i in range(1,5):

		tag = "cat"+str(i);
		dctmp = open("cards/card_rhalphabet_%s.txt" % tag, 'w')
		for l in linel:
			newline = l;
			if "CATX" in l: newline = l.replace('CATX',tag);
			dctmp.write(newline + "\n");
		for im in range(numberOfMassBins):
			dctmp.write("qcd_fail_%s_Bin%i flatParam \n" % (tag,im+1))


###############################################################


	
##-------------------------------------------------------------------------------------
if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
	parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
	parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
        parser.add_option('--np', dest="np", type=int,default=3, help='degree poly pt')
        parser.add_option('--nr', dest="nr", type=int,default=3, help='degree poly rho')
        parser.add_option('--nmass', dest="nmass", type=int,default=60, help='number of mass bins')
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
