import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array
import glob

from plotHelpersPhibb import *
from sampleContainerPhibb import *
#

MIN_M = {} #
MAX_M = {} #299 # AK8

def makePlots(hb,style,odir,lumi,ofile,canvases,rho_lo,rho_hi,nr,np):
    hist_pass_cat = []
    hist_fail_cat = []
    msd_binBoundaries=range(40,607,7)
    ptBinBoundaries = []
    ptBinBoundaries.append(hb['QCD']['pass'].GetYaxis().GetBinLowEdge(1))
    for j in range(1,hb['QCD']['fail'].GetNbinsY()+1):
        hist_pass = ROOT.TH1F('pass_cat%i'%j, 'pass_cat%i'%j, len(msd_binBoundaries)-1, array.array('d',msd_binBoundaries))
        hist_fail = ROOT.TH1F('fail_cat%i'%j, 'fail_cat%i'%j, len(msd_binBoundaries)-1, array.array('d',msd_binBoundaries))
        hist_pass.GetXaxis().SetTitle(hb['QCD']['pass'].GetXaxis().GetTitle())
        hist_fail.GetXaxis().SetTitle(hb['QCD']['fail'].GetXaxis().GetTitle())
        ptBinBoundaries.append(hb['QCD']['pass'].GetYaxis().GetBinUpEdge(j))
        for i in range(1,hb['QCD']['fail'].GetNbinsX()+1):
            hist_pass.SetBinContent(i,hb['QCD']['pass'].GetBinContent(i,j))
            hist_pass.SetBinError(i,hb['QCD']['pass'].GetBinError(i,j))
            hist_fail.SetBinContent(i,hb['QCD']['fail'].GetBinContent(i,j))
            hist_fail.SetBinError(i,hb['QCD']['fail'].GetBinError(i,j))
        hist_pass_cat.append(hist_pass)
        hist_fail_cat.append(hist_fail)

    c1, f2params = makeCanvasRatio2D(hb['QCD']['fail'],hb['QCD']['pass'],['QCD fail, p_{T} > 500 GeV','QCD pass, p_{T}>500 GeV'],[ROOT.kBlue,ROOT.kBlack],style,'ratio_msd_v_pt_ak8_topR6_N2',odir,lumi,ofile=ofile, rho_lo=rho_lo, rho_hi=rho_hi,nr=nr,np=np, minM = MIN_M['allcats'], maxM = MAX_M['allcats'])
    canvases.append(c1)
    for i in range(1,len(ptBinBoundaries)):
        c = makeCanvasRatio(hist_fail_cat[i-1],hist_pass_cat[i-1],['QCD fail, %i < p_{T} < %i GeV'%(ptBinBoundaries[i-1],ptBinBoundaries[i]),'QCD pass, %i < p_{T} < %i GeV'%(ptBinBoundaries[i-1],ptBinBoundaries[i])],[ROOT.kBlue,ROOT.kBlack],style,'ratio_msd_ak8_topR6_N2_cat%i'%i,odir,lumi,ofile,(ptBinBoundaries[i-1]+ptBinBoundaries[i])/2.,f2params, MIN_M['cat%i'%i], MAX_M['cat%i'%i],nr,np)
        canvases.append(c)
    
##############################################################################
def main(options,args,outputExists):
    
    msd_binBoundaries=range(40,607,7)
    pt_binBoundaries = [450, 500, 550, 600, 675, 800, 1000]
    
    empty = ROOT.TH2F('empty', 'empty', len(msd_binBoundaries) - 1,
                array.array('d', msd_binBoundaries), len(pt_binBoundaries) - 1,
                array.array('d', pt_binBoundaries))
    for j in range(1, empty.GetNbinsY() + 1):
        ptVal = empty.GetYaxis().GetBinLowEdge(j) + empty.GetYaxis().GetBinWidth(j) * 0.3        
        massMin = ROOT.TMath.Sqrt(ROOT.TMath.Exp(options.lrho))*ptVal
        massMax = ROOT.TMath.Sqrt(ROOT.TMath.Exp(options.hrho))*ptVal
        print j, massMin, massMax
        MIN_M['cat%i'%j] = empty.GetXaxis().GetBinUpEdge(empty.GetXaxis().FindBin(massMin))
        MAX_M['cat%i'%j] = empty.GetXaxis().GetBinLowEdge(empty.GetXaxis().FindBin(massMax))
        print j, MIN_M['cat%i'%j], MAX_M['cat%i'%j]


    MIN_M['allcats'] = MIN_M['cat1']
    MAX_M['allcats'] = MAX_M['cat6']

    
    ifile = options.ifile
    odir = options.odir
    lumi = options.lumi
    isData = options.isData        
        
    canvases = []
    plots = ['pass','fail']
        
    ofile = ROOT.TFile.Open(ifile,'read')
        
    hb = {}
    hb['QCD'] = {}
    hb['QCD']['pass'] = ofile.Get('DMSbb350_%s_pass'%options.cuts)
    hb['QCD']['fail'] = ofile.Get('DMSbb350_%s_fail'%options.cuts)
    hb['QCD']['pass'].Sumw2()
    hb['QCD']['fail'].Sumw2()

    old = hb['QCD']['fail'].Integral()+hb['QCD']['pass'].Integral()
    for histogram in hb['QCD'].values():
        for i in range(1, histogram.GetNbinsX()+1):
            for j in range(1, histogram.GetNbinsY()+1):
                massVal = histogram.GetXaxis().GetBinCenter(i)
                ptVal = histogram.GetYaxis().GetBinLowEdge(j) + histogram.GetYaxis().GetBinWidth(j) * 0.3
                rhoVal = ROOT.TMath.Log(massVal * massVal / ptVal / ptVal)
                if rhoVal < options.lrho or rhoVal > options.hrho:
                    print "removing rho = %.2f for %s, pt bin [%i, %i], mass bin [%i,%i]" % (
                    rhoVal, histogram.GetName(), histogram.GetYaxis().GetBinLowEdge(j), histogram.GetYaxis().GetBinUpEdge(j),
                    histogram.GetXaxis().GetBinLowEdge(i), histogram.GetXaxis().GetBinUpEdge(i))
                    histogram.SetBinContent(i, j, 0.)
                    histogram.SetBinError(i, j, 0.)
            
    new = hb['QCD']['fail'].Integral()+hb['QCD']['pass'].Integral()
    print new/old

    sys.exit()
                
    hb['QCD']['pass'].Scale(1./hb['QCD']['pass'].Integral())
    hb['QCD']['fail'].Scale(1./hb['QCD']['fail'].Integral())

    
    style = {'Hbb': 1,
             'ggHbb': 2,             
		     'Phibb50': 2,
             'Phibb75': 3,
		     'Phibb150': 4,
		     'Phibb250': 5,
             'VBFHbb': 3,
		     'VHbb': 4,
		     'ttHbb': 5,
             'Diboson': 1,
             'SingleTop': 1,
             'DY': 1,
             'W': 1,
             'TTbar': 1,
             'TTbar1Mu': 1,
             'TTbar1Ele': 1,
             'TTbar1Tau': 1,
             'TTbar0Lep': 1,
             'QCD': 1,
             'data': 1,
		     'muon':1
            }
                
    makePlots(hb,style,odir,lumi,ofile,canvases,options.lrho,options.hrho,options.NR,options.NP)
        
        


##----##----##----##----##----##----##
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", default = 30,type=float,help="luminosity", metavar="lumi")
    parser.add_option('-i','--ifile', dest='ifile', default = 'data/hist.root',help='directory with data', metavar='ifile')
    parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
    parser.add_option('-s','--isData', action='store_true', dest='isData', default =False,help='signal comparison', metavar='isData')
    parser.add_option('--lrho', dest='lrho', default=-6.0, type= 'float', help='low value rho cut')
    parser.add_option('--hrho', dest='hrho', default=-2.1, type='float', help=' high value rho cut')
    parser.add_option('-c', '--cuts', dest='cuts', default='p9', type='string', help='double b-tag cut value')
    parser.add_option('--nr', dest='NR', default=2, type='int', help='order of rho (or mass) polynomial')
    parser.add_option('--np', dest='NP', default=1, type='int', help='order of pt polynomial')


    (options, args) = parser.parse_args()

     
    import tdrstyle
    tdrstyle.setTDRStyle()
    ROOT.gStyle.SetPadTopMargin(0.10)
    ROOT.gStyle.SetPadLeftMargin(0.16)
    ROOT.gStyle.SetPadRightMargin(0.10)
    ROOT.gStyle.SetPaintTextFormat("1.1f")
    ROOT.gStyle.SetOptFit(0000)
    ROOT.gROOT.SetBatch()
    ROOT.gStyle.SetPalette(ROOT.kBird)
    #ROOT.gStyle.SetPalette(1)

    #stops = [ 0.0, 1.0]
    #red =   [ 1.0, 0.3]
    #green = [ 1.0, 0.3]
    #blue =  [ 1.0, 1.0]

    #s = array.array('d', stops)
    #r = array.array('d', red)
    #g = array.array('d', green)
    #b = array.array('d', blue)

    #npoints = len(s)
    #ROOT.TColor.CreateGradientColorTable(npoints, s, r, g, b, 999)

    #ROOT.gStyle.SetNumberContours(999)

    outputExists = True
        
    main(options,args,outputExists)
        
##----##----##----##----##----##----##




