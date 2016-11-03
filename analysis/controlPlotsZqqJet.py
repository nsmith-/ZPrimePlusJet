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

    
    legname = {'Zp100': "Z\'(100)",
               'Zp125':'Z\'(125)',
               'Zp200':'Z\'(200)',
               'DY': 'Z+jets',
               'W': 'W+jets',
               'TTbar': 't#bar{t}+jets',        
               'QCD': 'QCD',
               'data': 'data'
               }

    tfiles = {'Zp100': [idir+'/VectorDiJet1Jet_M100.root'],
               'Zp125': [idir+'/VectorDiJet1Jet_M125.root'],
               'Zp200': [idir+'/VectorDiJet1Jet_M200.root'],
               'DY':  [idir+'/DY.root'],
               'W':  [idir+'/W.root'],
               'TTbar':  [idir+'/TTbar_madgraphMLM.root'],
               'QCD': [idir+'/QCD.root'],
               'data': [idir+'/JetHTRun2016.root']
               }

    color = {'Zp100': ROOT.kRed,
               'Zp125': ROOT.kBlue-9,
               'Zp200': ROOT.kMagenta-9,
               'DY':  ROOT.kCyan,
               'W':  ROOT.kTeal-1,
               'TTbar':  ROOT.kGray,
               'QCD': ROOT.kBlue+1,
               'data': ROOT.kBlack
               }

    style = {'Zp100': 2,
               'Zp125': 3,
               'Zp200':4,
               'DY': 1,
               'W': 1,
               'TTbar': 1,
               'QCD': 1,
               'data': 1
               }

        
    print "Signals... "
    sigSamples = {}
    sigSamples['Zp100']  = sampleContainer(tfiles['Zp100']  , 1, lumi * 1) # 1fb
    sigSamples['Zp125'] = sampleContainer(tfiles['Zp125'], 1, lumi * 1) # 1fb
    sigSamples['Zp200'] = sampleContainer(tfiles['Zp200'], 1, lumi * 1) # 1fb
    print "Backgrounds..."
    bkgSamples = {}
    bkgSamples['DY'] = sampleContainer(tfiles['DY'], 1, lumi)
    bkgSamples['W']  = sampleContainer(tfiles['W'], 1, lumi)
    bkgSamples['TTbar']  = sampleContainer(tfiles['TTbar'], 1, lumi)
    # this 100 scale factor...just makes the QCD run faster, to use all the QCD, make the SF = 1
    bkgSamples['QCD'] = sampleContainer(tfiles['QCD'], 100, lumi) 

    isData = True;
    dataSample = sampleContainer(tfiles['data'],10,lumi,isData)

    ofile = ROOT.TFile.Open(odir+'/PlotsGGH.root','recreate')

    # plots = ['h_pt_ak8','h_msd_ak8','h_dbtag_ak8','h_n_ak4','h_n_ak4_dR0p8','h_pt_ak8_dbtagCut','h_msd_ak8_dbtagCut','h_t21_ak8','h_t32_ak8']
    plots = ['h_pt_ak8','h_msd_ak8']
    canvases = []
    for plot in plots:
        hs = {}
        for process, s in sigSamples.iteritems():
            hs[process] = getattr(s,plot)
        hb = {}
        for process, s in bkgSamples.iteritems():
            hb[process] = getattr(s,plot)
        hd = getattr(dataSample,plot)
        c = makeCanvasComparisonStackWData(hd,hs,hb,legname,color,style,plot.replace('h_','stack_'),odir,lumi,ofile)
        canvases.append(c)


##----##----##----##----##----##----##
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", type=float, default = 30,help="luminosity", metavar="lumi")
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




