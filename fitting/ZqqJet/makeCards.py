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
from buildRhalphabet import *

##-------------------------------------------------------------------------------------
def main(options,args):

	dctpl = open("datacard.tpl");
	numberOfMassBins = options.nmass;
	numberOfPtBins = 5;

	combinecards = 'combineCards.py ';
	linel = [];
	for line in dctpl: 
		print line.strip().split();
		linel.append(line.strip());

	boxes = ['pass','fail']            
	sigs = ['zqq100']
	bkgs = ['zqq','wqq','qcd','tqq']
	for i in range(1,numberOfPtBins+1):
                vErrs = {}
                scaleptErrs = {}
                tag = "cat"+str(i);
                for box in boxes:
			for proc in (sigs+bkgs):
				if i == 2:
					scaleptErrs['%s_%s'%(proc,box)] =  0.03
				elif i == 3:
					scaleptErrs['%s_%s'%(proc,box)] =  0.06
				elif i == 4:
					scaleptErrs['%s_%s'%(proc,box)] =  0.09
				elif i == 5:
					scaleptErrs['%s_%s'%(proc,box)] =  0.12
					
				vErrs['%s_%s'%(proc,box)] = 1.0+V_SF_ERR/V_SF
				
		vString = 'veff lnN'
                scaleptString = 'scalept shape'
		for box in boxes:
			for proc in (sigs+bkgs):
				if proc in ['qcd','tqq']:
					if i > 1:
						scaleptString += ' -'
				else:
					if i > 1:
						scaleptString += ' %.3f'%scaleptErrs['%s_%s'%(proc,box)]
				if proc in ['qcd','tqq']:
					vString += ' -'
				else:
					vString += ' %.3f'%vErrs['%s_%s'%(proc,box)]
		tag = "cat"+str(i);
		combinecards += "card_rhalphabet_%s%s_%s.txt " % (str(options.np),str(options.nr),tag)
		dctmp = open("card_rhalphabet_%s%s_%s.txt" % (str(options.np),str(options.nr),tag), 'w')
		for l in linel:
			if 'veff' in l:
				newline = vString
			elif 'scalept' in l and i>1:
				newline = scaleptString
                        elif 'znormEW' in l and 'wznormEW' not in l:
				l = l.replace('EW','E'+str(i))
				if i==3:
                                        newline = l.replace('1.15','1.25')
                                elif i==4:
                                        newline = l.replace('1.15','1.35')
                                elif i==5:
                                        newline = l.replace('1.15','1.35')
                                elif i==6:
                                        newline = l.replace('1.15','1.35')
				else:
					newline = l
			elif 'wznormEW' in l:
				l = l.replace('EW','E'+str(i))
				if i==4:
					newline = l.replace('1.05','1.15')
				elif i==5:
					newline = l.replace('1.05','1.15')
				elif i==6:
					newline = l.replace('1.05','1.15')
				else:
					newline = l
			elif 'ralphabase' in l:
				newline = l.replace('ralphabase','ralphabase_'+str(options.np)+str(options.nr)+'_pt')
			else:
				newline = l;
			if "CATX" in l: newline = l.replace('CATX',tag);
			dctmp.write(newline + "\n");
		for im in range(numberOfMassBins):
			dctmp.write("qcd_fail_%s_Bin%i flatParam \n" % (tag,im+1))

	print '%s > card_rhalphabet_%s%s_pt.txt'%(combinecards,str(options.np),str(options.nr))
	#os.system('%s > card_rhalphabet_%s%s_pt.txt'%(combinecards,str(options.np),str(options.nr)))
	

##-------------------------------------------------------------------------------------
if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
	parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
	parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
        parser.add_option('--np', dest="np", type=int,default=3, help='degree poly pt')
        parser.add_option('--nr', dest="nr", type=int,default=4, help='degree poly rho')
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
