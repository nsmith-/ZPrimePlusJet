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
from sampleContainer import *
#

##############################################################################
def main(options,args):
    #idir = "/eos/uscms/store/user/lpchbb/ggHsample_V11/sklim-v0-28Oct/"
    #odir = "plots_2016_10_31/"
    idir = options.idir
    odir = options.odir
    lumi = options.lumi
    
    legname = {'ggHbb': 'ggH(b#bar{b} MC@NLO)',
	   	'ggHbbp': 'ggH(b#bar{b} powheg)',
               'VBFHbb':'VBF H(b#bar{b})',
	       'ZHbb': ' ZH(b#bar{b})',
		'Phibb': ' Phi(125)(b#bar{b})'}

        
    tfiles = {'ggHbb': [idir+'/GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8_ext.root'],
		'ggHbbp': [idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8.root'],
               'VBFHbb': [idir+'/VBFHToBB_M125_13TeV_amcatnlo_pythia8.root'],
		'ZHbb': [idir+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8.root'],
		'Phibb':[idir+'/DMSpin0_ggPhibb1j_125.root']
               }

    color = {'ggHbb': ROOT.kRed,
	      'ggHbbp': ROOT.kRed+4,
               'VBFHbb': ROOT.kBlue-10,
		'ZHbb': ROOT.kAzure+1,
		'Phibb':ROOT.kBlue+2
               }

    style = {'ggHbb': 2,
	     'ggHbbp': 2,
               'VBFHbb': 3,
		'ZHbb': 4,
		'Phibb':1
               }
        
    print "Signals... "
    sigSamples = {}
    print(tfiles['ggHbb'])
    sigSamples['ggHbb']  = sampleContainer(tfiles['ggHbb']  , 1, lumi * 48.85 * 0.5824) 
    sigSamples['ggHbbp']  = sampleContainer(tfiles['ggHbbp']  , 1, lumi* 48.85 * 0.5824)
    sigSamples['VBFHbb'] = sampleContainer(tfiles['VBFHbb'], 1, lumi* 3.782 * 0.5824) 
    sigSamples['ZHbb'] = sampleContainer(tfiles['ZHbb'], 1, lumi * 0.6072 * 0.5824) 	
    sigSamples['Phibb'] = sampleContainer(tfiles['Phibb'], 1, lumi * 48.85 * 0.5824)   


    ofile = ROOT.TFile.Open(odir+'/Plots.root','recreate')



    plots = ['h_pt_ak8','h_msd_ak8','h_dbtag_ak8','h_n_ak4','h_n_ak4_dR0p8','h_pt_ak8_dbtagCut','h_msd_ak8_dbtagCut','h_t21_ak8','h_t32_ak8','h_msd_ak8_t21ddtCut']
    for plot in plots:
        hs = {}
        for process, s in sigSamples.iteritems():
            hs[process] = getattr(s,plot)
        c = makeCanvasComparison(hs,legname,color,plot.replace('h_','signalcomparison_'),odir,lumi)

        ofile.cd()
        for process, h in hs.iteritems():
            h.Write()
        
        #c.Write()
	


##----##----##----##----##----##----##
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", type=float,default = 30,help="luminosity", metavar="lumi")
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')

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




