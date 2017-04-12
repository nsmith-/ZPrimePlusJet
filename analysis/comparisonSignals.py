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
DBTAGMIN=-99
#

##############################################################################
def main(options,args):
    #idir = "/eos/uscms/store/user/lpchbb/ggHsample_V11/sklim-v0-28Oct/"
    #odir = "plots_2016_10_31/"
    idir = options.idir
    odir = options.odir
    lumi = options.lumi
    
    legname = {#'ggHbb': 'ggH(b#bar{b}) N3LO + 0/1/2 merged',
	       'ggHbbp': 'ggH(b#bar{b})',
               'VBFHbb':'VBF H(b#bar{b})',
	       'ZHbb': ' Z(q#bar{q})H(b#bar{b})',
	       'ZnnHbb': ' Z(#nu#nu)H(b#bar{b})',
	       'WHbb': 'W(q#bar{q})H(b#bar{b})',
	       'tthbb': 'ttH(b#bar{b})',	   	
	       'Phibb': ' Phi(125)(b#bar{b})'}

        
    tfiles = {#'ggHbb': [idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8_0_ptw_1000pb_weighted.root'],#amcatnloFXFX_pythia8_1000pb_weighted.root'],
	       'ggHbbp': [idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8_all_1000pb_weighted.root'],
               'VBFHbb': [idir+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root'],
               'ZHbb': [idir+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			idir+'/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
               'WHbb' : [idir+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                        idir+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
               'tthbb' : [idir+'/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
	       'ZnnHbb': [idir+'/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			  idir+'/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root'],
	       'Phibb':[idir+'/Spin0_ggPhi12j_g1_125_Scalar_13TeV_madgraph_1000pb_weighted.root']
               }

    color = {#'ggHbb': ROOT.kBlack,
	     'ggHbbp': ROOT.kBlue+2,
             'VBFHbb': ROOT.kAzure+3,
	     'ZnnHbb': ROOT.kPink+5,
	     'ZHbb': ROOT.kPink+1,
	     'WHbb': ROOT.kAzure+1,	
	     'tthbb': ROOT.kOrange+1,
	     'Phibb':ROOT.kRed-2
               }

    style = {#'ggHbb': 1,
	     'ggHbbp': 1,
             'VBFHbb': 2,
	     'ZHbb': 1,
	     'WHbb':1,
             'ZnnHbb': 1,
	     'tthbb':1,		
	     'Phibb':2
               }
        
    print "Signals... "
    sigSamples = {}
    #sigSamples['ggHbb']  = sampleContainer('ggHbb',tfiles['ggHbb']  , 1, lumi ) 
    sigSamples['ggHbbp']  = sampleContainer('ggHbbp',tfiles['ggHbbp']  , 1, DBTAGMIN,lumi)
    sigSamples['VBFHbb'] = sampleContainer('VBFHbb',tfiles['VBFHbb'], 1, DBTAGMIN,lumi) 
    sigSamples['ZHbb'] = sampleContainer('ZHbb',tfiles['ZHbb'], 1, DBTAGMIN,lumi ) 	
    sigSamples['WHbb'] = sampleContainer('WHbb',tfiles['WHbb'], 1, DBTAGMIN,lumi )
    sigSamples['tthbb'] = sampleContainer('tthbb',tfiles['tthbb'], 1, DBTAGMIN,lumi )	
    sigSamples['ZnnHbb'] = sampleContainer('ZnnHbb',tfiles['ZnnHbb'], 1, DBTAGMIN,lumi )
    #sigSamples['Phibb'] = sampleContainer('Phibb',tfiles['Phibb'], 1, lumi*0.035)   


    ofile = ROOT.TFile.Open(odir+'/Plots_1000pb_weighted.root','recreate')



    plots = [
'h_n_ak4'           ,
'h_met'             ,
'h_pt_ak8'          ,
'h_pt_ak8_dbtagCut' ,
'h_msd_ak8'         ,
'h_msd_ak8_dbtagCut',
'h_msd_ak8_t21ddtCut'  ,
'h_msd_ak8_N2Cut'   ,
'h_dbtag_ak8'       ,
'h_t21ddt_ak8'      ,
'h_t32_ak8'         ,
'h_t32_ak8_t21ddtCut'  ,
'h_n2b1sd_ak8'      ,
'h_n2b1sdddt_ak8'   ,
'h_pt_bbleading' ,
'h_bb_bbleading' ,
'h_msd_bbleading',
'h_msd_ak8_inc',
'h_msd_ak8_raw',
'h_msd_ak8_topR6_N2_pass',
'h_msd_ak8_topR6_N2_fail'
]
#'h_pt_ak8','h_msd_ak8','h_dbtag_ak8','h_n_ak4','h_n_ak4_dR0p8','h_pt_ak8_dbtagCut','h_msd_ak8_dbtagCut','h_t21_ak8','h_t32_ak8','h_msd_ak8_t21ddtCut','h_msd_ak8_N2Cut','h_met']
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
    parser.add_option("--lumi", dest="lumi", type=float,default = 35.9,help="luminosity", metavar="lumi")
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




