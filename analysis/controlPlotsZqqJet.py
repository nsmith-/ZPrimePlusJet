B1;3201;0cimport ROOT
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
    idir = options.idir
    odir = options.odir
    lumi = options.lumi
    isData = options.isData
    
    legname = {'Zp100': "Z\'(100)",
               'Zp125':'Z\'(125)',
               'Zp200':'Z\'(200)',
               'DY': 'Z+jets',
               'W': 'W+jets',
               'TTbar': 't#bar{t}+jets',        
               'QCD': 'QCD',
               'data': 'data'
               }

    tfiles = {'Zp100': [idir+'/VectorDiJet1Jet_M100_1000pb_weighted.root'],
              'Zp125': [idir+'/VectorDiJet1Jet_M125_1000pb_weighted.root'],
              'Zp200': [idir+'/VectorDiJet1Jet_M200_1000pb_weighted.root'],
              'Diboson': [idir+'/WWTo4Q_13TeV_amcatnlo_1000pb_weighted.root',idir+'/ZZTo4Q_13TeV_amcatnlo_1000pb_weighted.root'],
              'SingleTop':  [idir+'/ST_t-channel_antitop_4f_inclusiveDecays_13TeV_powheg_1000pb_weighted.root',
                             idir+'/ST_t-channel_top_4f_inclusiveDecays_13TeV_powheg_1000pb_weighted.root',
                             idir+'/ST_tW_antitop_5f_inclusiveDecays_13TeV_1000pb_weighted.root',
                             idir+'/ST_tW_top_5f_inclusiveDecays_13TeV_1000pb_weighted.root'],
              'TTbar':  [idir+'/TTJets_13TeV_1000pb_weighted.root'],
              'DY':  [idir+'/DY_1000pb_weighted.root'],
              'W':  [idir+'/WJets_1000pb_weighted.root'],
              'QCD': [idir+'/QCD.root'],
              'data': [idir+'/JetHTRun2016.root']
              }

    color = {'Zp100': ROOT.kRed,
             'Zp125': ROOT.kBlue-9,
             'Zp200': ROOT.kMagenta-9,
             'Diboson': ROOT.kOrange,
             'SingleTop': ROOT.kRed-2,
             'TTbar':  ROOT.kGray,
             'DY':  ROOT.kCyan,
             'W':  ROOT.kTeal-1,
             'QCD': ROOT.kBlue+1,
             'data': ROOT.kBlack
             }

    style = {'Zp100': 2,
             'Zp125': 3,
             'Zp200':4,
             'Diboson': 1,
             'SingleTop': 1,
             'TTbar': 1,
             'DY': 1,
             'W': 1
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
    #bkgSamples['SingleTop'] = sampleContainer(tfiles['SingleTop'], 1, lumi)
    #bkgSamples['Diboson'] = sampleContainer(tfiles['Diboson'], 1, lumi)
    bkgSamples['TTbar']  = sampleContainer(tfiles['TTbar'], 1, lumi)
    bkgSamples['DY'] = sampleContainer(tfiles['DY'], 1, lumi)
    bkgSamples['W']  = sampleContainer(tfiles['W'], 1, lumi)
    bkgSamples['QCD'] = sampleContainer(tfiles['QCD'], 100, lumi) 

    if isData:
        dataSample = sampleContainer(tfiles['data'],10,lumi,isData)

    ofile = ROOT.TFile.Open(odir+'/PlotsZqq.root','recreate')

    plots = ['h_pt_ak8','h_msd_ak8','h_n2b1sd_ak8','h_n2b1sdddt_ak8','h_t21_ak8','h_t21ddt_ak8']
    canvases = []
    for plot in plots:
        hall = {}
        hs = {}
        for process, s in sigSamples.iteritems():
            hs[process] = getattr(s,plot)
            hall[process] = getattr(s,plot)
        hb = {}
        for process, s in bkgSamples.iteritems():
            hb[process] = getattr(s,plot)
            hall[process] = getattr(s,plot)
        if isData:
            hd = getattr(dataSample,plot)
            c = makeCanvasComparisonStackWData(hd,hs,hb,legname,color,style,plot.replace('h_','stack_'),odir,lumi,ofile)
        else:
            c = makeCanvasComparisonStack(hs,hb,legname,color,style,'ggHbb',plot.replace('h_','stack_'),odir,lumi,ofile)
            c1 = makeCanvasComparison(hall,legname,color,style,plot.replace('h_','signalcomparison_'),odir,lumi,ofile,True)
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




