import ROOT as r,sys,math,os
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array


def exec_me(command, dryRun=False):
    print command
    if not dryRun:
        os.system(command)

        
if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('--model',dest="model", default="DMSbb",type="string", help="signal model name")
    parser.add_option('-m','--mass'   ,action='store',type='int',dest='mass'   ,default=125, help='mass')
    parser.add_option('--nr1' ,action='store',type='int',dest='NR1'   ,default=1, help='order of rho polynomial for model 1')
    parser.add_option('--np1' ,action='store',type='int',dest='NP1'   ,default=1, help='order of pt polynomial for model 1')
    parser.add_option('--nr2' ,action='store',type='int',dest='NR2'   ,default=2, help='order of rho polynomial for model 2')
    parser.add_option('--np2' ,action='store',type='int',dest='NP2'   ,default=1, help='order of pt polynomial for model 2')
    parser.add_option('--scale',dest='scale', default=1,type='float',help='scale factor to scale MC (assuming only using a fraction of the data)')
    parser.add_option('-l','--lumi'   ,action='store',type='float',dest='lumi'   ,default=36.4, help='lumi')
    parser.add_option('-i','--ifile', dest='ifile', default = 'hist_1DZbb.root',help='file with histogram inputs', metavar='ifile')
    parser.add_option('-t','--toys'   ,action='store',type='int',dest='toys'   ,default=200, help='number of toys')
    parser.add_option('-r','--r',dest='r', default=0 ,type='string',help='default value of r')    
    parser.add_option('--rMin',dest='rMin', default='-20' ,type='string',help='minimum of r (signal strength) in profile likelihood plot')
    parser.add_option('--rMax',dest='rMax', default='20',type='string',help='maximum of r (signal strength) in profile likelihood plot')  
    parser.add_option('-n','--n' ,action='store',type='int',dest='n'   ,default=5*20, help='number of bins')
    parser.add_option('--just-plot', action='store_true', dest='justPlot', default=False, help='just plot')
    parser.add_option('--pseudo', action='store_true', dest='pseudo', default=False, help='run on asimov dataset')
    parser.add_option('--blind', action='store_true', dest='blind', default=False, help='run on blinded dataset')
    parser.add_option('--dry-run',dest="dryRun",default=False,action='store_true',
                  help="Just print out commands to run")    
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write plots', metavar='odir')
    parser.add_option('-c', '--cuts', dest='cuts', default='p9', type='string', help='double b-tag cut value')
    parser.add_option('-b','--box',dest="box", default="AK8",type="string", help="box name")
    parser.add_option('--lrho', dest='lrho', default=-6.0, type= 'float', help='low value rho cut')
    parser.add_option('--hrho', dest='hrho', default=-2.1, type='float', help=' high value rho cut')


    (options,args) = parser.parse_args()
    jet_type = options.box
    cut = options.cuts.split(',')[0]
    
    rhalphDir1 = '%s/cards_r%ip%i/'%(options.odir,options.NR1,options.NP1)
    cardsDir1 = '%s/cards_r%ip%i/%s/%s'%(options.odir,options.NR1,options.NP1, jet_type, cut)
    sigDir1 = '%s/cards_r%ip%i/%s/%s/%s'%(options.odir,options.NR1,options.NP1, jet_type, cut, options.model+str(options.mass))
    
    fillString = ''
    if options.box=='CA15':
        fillString = '--fillCA15'
    exec_me('python writeMuonCRDatacard.py -i ./ -o %s/ -c %s --mass %s %s --no-mcstat-shape'%(sigDir1, cut, options.mass, fillString),options.dryRun)
    
    exec_me('combineCards.py cat1=%s/card_rhalphabet_cat1.txt cat2=%s/card_rhalphabet_cat2.txt cat3=%s/card_rhalphabet_cat3.txt cat4=%s/card_rhalphabet_cat4.txt cat5=%s/card_rhalphabet_cat5.txt cat6=%s/card_rhalphabet_cat6.txt muonCR=%s/datacard_muonCR.txt > %s/card_rhalphabet_muonCR_r%ip%i.txt'%(sigDir1,sigDir1,sigDir1,sigDir1,sigDir1,sigDir1,sigDir1,sigDir1,options.NR1, options.NP1),options.dryRun)

    dataString = '--data'

    exec_me('python limit.py -M Bias --datacard %s/card_rhalphabet_muonCR_r%ip%i.txt --datacard-alt %s/card_rhalphabet_muonCR_r%ip%i.txt -o %s -t %i --lumi %f %s -r %s --rMin %s --rMax %s --mass %s'%(sigDir1, options.NR1, options.NP1, sigDir1, options.NR1, options.NP1, sigDir1, options.toys, options.lumi, dataString, options.r, options.rMin, options.rMax, options.mass),options.dryRun)
     

     
