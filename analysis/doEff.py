import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array

from plotHelpers import *
from printEff import *
#

##############################################################################
def main(options,args):
    #idir = "/eos/uscms/store/user/lpchbb/ggHsample_V11/sklim-v0-28Oct/"
    #odir = "plots_2016_10_31/"
    idir = options.idir

    
    tfiles = {  'hh3000':[idir+'/BulkGravTohhTohbbhbb_narrow_M_3000_13TeV_madgraph.root'],
		'ww2000h':[idir+'/BulkGravToWW_narrow_M_2000_13TeV_madgraph_herwigpp.root'],
		'ww3000h':[idir+'/BulkGravToWW_narrow_M_3000_13TeV_madgraph_herwigpp.root'],
		'hh1000h':[idir+'/BulkGravTohhTohbbhbb_narrow_M_1000_13TeV_madgraph_herwig_ext.root'],
		'hh2000':[idir+'/BulkGravTohhTohbbhbb_narrow_M_2000_13TeV_madgraph.root'],
		'ww3000':[idir+'/BulkGravToWW_narrow_M_3000_13TeV_madgraph.root'],
		'hh2000h':[idir+'/BulkGravTohhTohbbhbb_narrow_M_2000_13TeV_madgraph_herwig_ext.root'],
		'hh3000h':[idir+'/BulkGravTohhTohbbhbb_narrow_M_3000_13TeV_madgraph_herwig.root'],
		'ww1000':[idir+'/BulkGravToWW_narrow_M_1000_13TeV_madgraph.root'],
		'ww2000':[idir+'/BulkGravToWW_narrow_M_2000_13TeV_madgraph.root'],
		'hh1000':[idir+'/BulkGravTohhTohbbhbb_narrow_M_1000_13TeV_madgraph.root'],
		'ww1000h':[idir+'/BulkGravToWW_narrow_M_1000_13TeV_madgraph_herwigpp.root'],
		'ww4000h':[idir+'/bulkWW4000_herwig.root'],
		'ww4000':[idir+'/bulkWW4000.root'],
		'ww600h':[idir+'/bulkWW600_herwig.root'],
                'ww600':[idir+'/bulkWW600.root']
            }

    print "Signals... "
    sigSamples = {}
    sigSamples['hh3000']  = printEff('hh3000',tfiles['hh3000']  , 1) 
    sigSamples['hh3000h']  = printEff('hh3000h',tfiles['hh3000h']  , 1)   
    sigSamples['hh2000']  = printEff('hh2000',tfiles['hh2000']  , 1)   
    sigSamples['hh2000h']  = printEff('hh2000h',tfiles['hh2000h']  , 1)	
    sigSamples['hh1000']  = printEff('hh1000',tfiles['hh1000']  , 1)   
    sigSamples['hh1000h']  = printEff('hh1000h',tfiles['hh1000h']  , 1)
    sigSamples['ww3000']  = printEff('ww3000',tfiles['ww3000']  , 1)   
    sigSamples['ww3000h']  = printEff('ww3000h',tfiles['ww3000h']  , 1)
    sigSamples['ww2000']  = printEff('ww2000',tfiles['ww2000']  , 1)
    sigSamples['ww2000h']  = printEff('ww2000h',tfiles['ww2000h']  , 1)
    sigSamples['ww1000']  = printEff('ww1000',tfiles['ww1000']  , 1)
    sigSamples['ww1000h']  = printEff('ww1000h',tfiles['ww1000h']  , 1)
    sigSamples['ww4000']  = printEff('ww4000',tfiles['ww4000']  , 1)
    sigSamples['ww4000h']  = printEff('ww4000h',tfiles['ww4000h']  , 1)
    sigSamples['ww600']  = printEff('ww600',tfiles['ww600']  , 1)
    sigSamples['ww600h']  = printEff('ww600h',tfiles['ww600h']  , 1)	


##----##----##----##----##----##----##
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')

    (options, args) = parser.parse_args()

     
    import tdrstyle
    tdrstyle.setTDRStyle()
    ROOT.gStyle.SetPadTopMargin(0.10)
    ROOT.gStyle.SetPadLeftMargin(0.16)
    ROOT.gStyle.SetPadRightMargin(0.10)
    ROOT.gStyle.SetPalette(1)
    ROOT.gStyle.SetPaintTextFormat("1.1f")
    ROOT.gStyle.SetOptFit(0000)
    ROOT.gROOT.SetBatch()
    
    main(options,args)
##----##----##----##----##----##----##




