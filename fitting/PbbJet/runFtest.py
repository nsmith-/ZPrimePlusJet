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
    parser.add_option('-m','--mass'   ,action='store',type='int',dest='mass'   ,default=125, help='mass')
    parser.add_option('--nr1' ,action='store',type='int',dest='NR1'   ,default=1, help='order of rho polynomial for model 1')
    parser.add_option('--np1' ,action='store',type='int',dest='NP1'   ,default=1, help='order of pt polynomial for model 1')
    parser.add_option('--nr2' ,action='store',type='int',dest='NR2'   ,default=2, help='order of rho polynomial for model 2')
    parser.add_option('--np2' ,action='store',type='int',dest='NP2'   ,default=1, help='order of pt polynomial for model 2')
    parser.add_option('--scale',dest='scale', default=1,type='float',help='scale factor to scale MC (assuming only using a fraction of the data)')
    parser.add_option('-l','--lumi'   ,action='store',type='float',dest='lumi'   ,default=36.4, help='lumi')
    parser.add_option('-i','--ifile', dest='ifile', default = 'hist_1DZbb.root',help='file with histogram inputs', metavar='ifile')
    parser.add_option('-t','--toys'   ,action='store',type='int',dest='toys'   ,default=200, help='number of toys')
    
    parser.add_option('-n','--n' ,action='store',type='int',dest='n'   ,default=5*20, help='number of bins')
    parser.add_option('--just-plot', action='store_true', dest='justPlot', default=False, help='just plot')
    parser.add_option('--dry-run',dest="dryRun",default=False,action='store_true',
                  help="Just print out commands to run")    


    (options,args) = parser.parse_args()

    cardsDir1 = 'cards_r%ip%i'%(options.NR1,options.NP1)
    cardsDir2 = 'cards_r%ip%i'%(options.NR2,options.NP2)
    exec_me('mkdir -p %s'%cardsDir1,options.dryRun)
    exec_me('mkdir -p %s'%cardsDir2,options.dryRun)
    exec_me('python buildRhalphabetHbb.py -i %s --scale %f -o %s --nr %i --np %i --blind '%(options.ifile, options.scale, cardsDir1, options.NR1, options.NP1),options.dryRun )
    exec_me('python buildRhalphabetHbb.py -i %s --scale %f -o %s --nr %i --np %i --blind '%(options.ifile, options.scale, cardsDir2, options.NR2, options.NP2),options.dryRun )
    exec_me('python makeCardsHbb.py -o %s'%cardsDir1,options.dryRun)
    exec_me('python makeCardsHbb.py -o %s'%cardsDir2,options.dryRun)
    exec_me('combineCards.py cat1=%s/card_rhalphabet_cat1.txt cat2=%s/card_rhalphabet_cat2.txt cat3=%s/card_rhalphabet_cat3.txt cat4=%s/card_rhalphabet_cat4.txt cat5=%s/card_rhalphabet_cat5.txt > card_rhalphabet_r%ip%i.txt'%(cardsDir1,cardsDir1,cardsDir1,cardsDir1,cardsDir1,options.NR1, options.NP1),options.dryRun)
    exec_me('combineCards.py cat1=%s/card_rhalphabet_cat1.txt cat2=%s/card_rhalphabet_cat2.txt cat3=%s/card_rhalphabet_cat3.txt cat4=%s/card_rhalphabet_cat4.txt cat5=%s/card_rhalphabet_cat5.txt > card_rhalphabet_r%ip%i.txt'%(cardsDir2,cardsDir2,cardsDir2,cardsDir2,cardsDir2,options.NR2, options.NP2),options.dryRun)
    p1 = int((options.NR1+1)*(options.NP1+1))
    p2 = int((options.NR2+1)*(options.NP2+1))
    
    exec_me('mkdir -p ftest_r%ip%i_r%ip%i'%(options.NR1, options.NP1, options.NR2, options.NP2),options.dryRun)
    exec_me('python limit.py -M FTest --datacard card_rhalphabet_r%ip%i.txt --datacard-alt card_rhalphabet_r%ip%i.txt -o ftest_r%ip%i_r%ip%i -n %i --p1 %i --p2 %i -t %i --lumi %f '%(options.NR1, options.NP1, options.NR2, options.NP2,options.NR1, options.NP1, options.NR2, options.NP2, options.n, p1, p2, options.toys,options.lumi ),options.dryRun)
     

     
