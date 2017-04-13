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

    
    legname = {'ggHbb': 'ggH(b#bar{b})',
               'Hbb': 'H(b#bar{b})',
               'VBFHbb':'VBF H(b#bar{b})',
               'VHbb': 'VH(b#bar{b})',
	       'ttHbb': 't#bar{t}H(b#bar{b})',
               'TTbar': 't#bar{t}+jets',        
               'QCD': 'QCD',
               }
    tfiles = {'Hbb':   [idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8_all_1000pb_weighted.root',
                        idir+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root',
                        idir+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                        idir+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                        idir+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                        idir+'/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                        idir+'/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                        idir+'/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                        idir+'/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root'],
              'ggHbb': [idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8_all_1000pb_weighted.root'],
                        # idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root'],
              'VBFHbb': [idir+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root'],
              'VHbb': [idir+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir+'/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                        idir+'/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir+'/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root'],
              'ttHbb':  [idir+'/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],#ttHTobb_M125_TuneCUETP8M2_ttHtranche3_13TeV_powheg_pythia8_1000pb_weighted.root'],
              'Diboson': [idir+'/WWTo4Q_13TeV_powheg_1000pb_weighted.root',
                          idir+'/ZZ_13TeV_pythia8_1000pb_weighted.root',#ZZTo4Q_13TeV_amcatnloFXFX_madspin_pythia8_1000pb_weighted.root',
                          idir+'/WZ_13TeV_pythia8_1000pb_weighted.root'],
              'DY': [idir+'/DYJetsToQQ_HT180_13TeV_1000pb_weighted.root'],
              'DYll': [idir+'/DYJetsToLL_M_50_13TeV_ext_1000pb_weighted.root'],
              'SingleTop':  [idir+'/ST_t_channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
                             idir+'/ST_t_channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
                             idir+'/ST_tW_antitop_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root',
                             idir+'/ST_tW_top_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root'],
              'W':  [idir+'/WJetsToQQ_HT180_13TeV_1000pb_weighted.root'],
              'Wlnu': [idir+'WJetsToLNu_HT_100To200_13TeV_1000pb_weighted.root',
                     idir+'/WJetsToLNu_HT_200To400_13TeV_1000pb_weighted.root',
                     idir+'/WJetsToLNu_HT_400To600_13TeV_1000pb_weighted.root',
                     idir+'/WJetsToLNu_HT_600To800_13TeV_1000pb_weighted.root',
                     idir+'/WJetsToLNu_HT_800To1200_13TeV_1000pb_weighted.root',
                    idir+'/WJetsToLNu_HT_1200To2500_13TeV_1000pb_weighted.root',
                    idir+'/WJetsToLNu_HT_2500ToInf_13TeV_1000pb_weighted.root'],
              'TTbar':  [idir+'/TT_powheg_1000pb_weighted_v1204.root'], #Powheg is the new default
              'QCD': [idir+'/QCD_HT100to200_13TeV_1000pb_weighted.root',
                      idir+'/QCD_HT200to300_13TeV_all_1000pb_weighted.root',
                      idir+'/QCD_HT300to500_13TeV_all_1000pb_weighted.root',
                      idir+'/QCD_HT500to700_13TeV_ext_1000pb_weighted.root',
                      idir+'/QCD_HT700to1000_13TeV_ext_1000pb_weighted.root',
                      idir+'/QCD_HT1000to1500_13TeV_all_1000pb_weighted.root',
                      idir+'/QCD_HT1500to2000_13TeV_all_1000pb_weighted.root',
                      idir+'/QCD_HT2000toInf_13TeV_1000pb_weighted.root'],

            }

    color = {'ggHbb': ROOT.kRed+1,
             'Hbb': ROOT.kRed,
             'VHbb': ROOT.kTeal+1,
             'VBFHbb': ROOT.kAzure+2,
		     'ttHbb': ROOT.kOrange+1,
             'TTbar':  ROOT.kGray,
             'QCD': ROOT.kBlue+2,
            }

    style = {'Hbb': 1,
             'ggHbb': 2,             
		     'Phibb50': 2,
             'Phibb75': 3,
		     'Phibb150': 4,
		     'Phibb250': 5,
             'VBFHbb': 1,
		     'VHbb': 4,
		     'ttHbb': 5,
             'TTbar': 1,
             'QCD': 1,
            }
        
    print "Signals... "
    sigSamples = {}
    sigSamples['ggHbb']  = sampleContainer('ggHbb',tfiles['ggHbb']  , 1, lumi) 
    sigSamples['VBFHbb'] = sampleContainer('VBFHbb',tfiles['VBFHbb'], 1, lumi ) 
    #sigSamples['VHbb'] = sampleContainer('VHbb',tfiles['VHbb'], 1, lumi ) 	
    sigSamples['ttHbb'] = sampleContainer('ttHbb',tfiles['ttHbb'], 1, lumi )    
    #sigSamples['Phibb50']  = sampleContainer('Phibb50',tfiles['Phibb50']  , 1, 0.2480*lumi) 
    #sigSamples['Phibb75'] = sampleContainer('Phibb75',tfiles['Phibb75'], 1, 0.2080*lumi ) 
    #sigSamples['Phibb150'] = sampleContainer('Phibb150',tfiles['Phibb150'], 1, 0.2764*lumi ) 	
    #sigSamples['Phibb250'] = sampleContainer('Phibb250',tfiles['Phibb250'], 1, 0.6699*lumi ) 	
    print "Backgrounds..."
    bkgSamples = {}    
    bkgSamples['QCD'] = sampleContainer('QCD',tfiles['QCD'], 1000, lumi)
    bkgSamples['TTbar']  = sampleContainer('TTbar',tfiles['TTbar'], 10, lumi)
    #bkgSamples['Hbb'] = sampleContainer('Hbb',tfiles['Hbb'], 1, lumi ) 	

    ofile = ROOT.TFile.Open(odir+'/Plots_1000pb_weighted.root ','recreate')


    canvases = []
    plots = ['h_Cuts']
    for plot in plots:
        hs = {}
        hb = {}
        hall={}
        for process, s in sigSamples.iteritems():
            hs[process] = getattr(s,plot)
            hall[process] = getattr(s,plot)
        for process, s in bkgSamples.iteritems():
            hb[process] = getattr(s,plot)
            hall[process] = getattr(s,plot)
        c = makeCanvasComparisonStack(hs,hb,legname,color,style,'ggHbb',plot.replace('h_','stack_'),odir,lumi,ofile)
        c1 = makeCanvasComparison(hall,legname,color,style,plot.replace('h_','signalcomparison_'),odir,lumi,ofile)
        canvases.append(c)	


##----##----##----##----##----##----##
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", default = 35.9,type=float,help="luminosity", metavar="lumi")
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




