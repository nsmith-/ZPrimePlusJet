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
    
    legname = {'ggHbb': 'ggH(b#bar{b}) MC@NLO',
	       'ggHbbp': 'ggH(b#bar{b}) powheg',
               'VBFHbb':'VBF H(b#bar{b})',
	       'ZHbb': ' ZH(b#bar{b})',
	       'WHbb': 'WH(b#bar{b})',
	       'tthbb': 'ttH(b#bar{b})',	   	
	       'Phibb': ' Phi(125)(b#bar{b})'}

        
    tfiles = {'ggHbb': [idir+'/GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8_1000pb_weighted.root'],
       	      'ggHbbp': [idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
              'VBFHbb': [idir+'/VBFHToBB_M125_13TeV_amcatnlo_pythia8_1000pb_weighted.root'],
	      'ZHbb': [idir+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
	      'WHbb' : [idir+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root', idir+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
	      'tthbb' : [idir+'ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
	      'Phibb':[idir+'/DMSpin0_ggPhibb1j_125_1000pb_weighted.root']
               }

    color = {'ggHbb': ROOT.kRed,
	     'ggHbbp': ROOT.kBlue+2,
             'VBFHbb': ROOT.kAzure+3,
	     'ZHbb': ROOT.kAzure+1,
	     'WHbb': ROOT.kPink+2,	
	     'tthbb': ROOT.kOrange+1,
	     'Phibb':ROOT.kRed-2
               }

    style = {'ggHbb': 2,
	     'ggHbbp': 1,
             'VBFHbb': 2,
	     'ZHbb': 1,
	     'WHbb':1,
	     'tthbb':1,		
	     'Phibb':2
               }
        
    print "Signals... "
    sigSamples = {}
    print(tfiles['ggHbb'])
    #sigSamples['ggHbb']  = sampleContainer(tfiles['ggHbb']  , 1, lumi ) 
    sigSamples['ggHbbp']  = sampleContainer(tfiles['ggHbbp']  , 1, lumi)
    sigSamples['VBFHbb'] = sampleContainer(tfiles['VBFHbb'], 1, lumi) 
    sigSamples['ZHbb'] = sampleContainer(tfiles['ZHbb'], 1, lumi ) 	
    sigSamples['WHbb'] = sampleContainer(tfiles['WHbb'], 1, lumi )
    sigSamples['tthbb'] = sampleContainer(tfiles['tthbb'], 1, lumi )	
    sigSamples['Phibb'] = sampleContainer(tfiles['Phibb'], 1, lumi*0.00126535)   


    ofile = ROOT.TFile.Open(odir+'/Plots_1000pb_weighted.root','recreate')



    plots = ['h_pt_ak8','h_msd_ak8','h_dbtag_ak8','h_n_ak4','h_n_ak4_dR0p8','h_pt_ak8_dbtagCut','h_msd_ak8_dbtagCut','h_t21_ak8','h_t32_ak8','h_msd_ak8_t21ddtCut','h_msd_ak8_N2Cut','h_met']
    for plot in plots:
        hs = {}
        for process, s in sigSamples.iteritems():
            hs[process] = getattr(s,plot)
        c = makeCanvasComparison(hs,legname,color,style,plot.replace('h_','signalcomparison_'),odir,lumi)

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




