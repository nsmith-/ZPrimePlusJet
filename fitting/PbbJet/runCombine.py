from optparse import OptionParser
import os
import ROOT as rt
from array import array
import sys
import glob
import time

def massIterable(massList):    
    if len(massList.split(','))==1:
        massIterableList = [massList]
    else:
        massIterableList = list(eval(massList))
    return massIterableList


def exec_me(command,dryRun=True):
    print command
    if not dryRun: os.system(command)

def main(options,args):
    jet_type = 'AK8'
    if options.fillCA15:
        jet_type = 'CA15'

    cut = options.cuts.split(',')[0]

    exec_me('python makeCardsPhibb.py -i %s  -o %s/%s/%s --remove-unmatched --no-mcstat-shape  -c %s --lrho %f --hrho %f'%(options.ifile,
                                                                                                                           options.odir,
                                                                                                                           jet_type,
                                                                                                                           cut, cut,
                                                                                                                           options.lrho,
                                                                                                                           options.hrho),options.dryRun)
    exec_me('python buildRhalphabetPhibb.py -i %s -o %s/%s/%s/ --remove-unmatched  --prefit --use-qcd --pseudo -c %s --lrho %f --hrho %f'%(options.ifile,
                                                                                                                                            options.odir,
                                                                                                                                            jet_type,
                                                                                                                                            cut, cut,
                                                                                                                                            options.lrho,
                                                                                                                                            options.hrho),options.dryRun)

                                                                                                                                            
    pwd = os.environ['PWD']

    fillString = ''
    if options.fillCA15:
        fillString = '--fillCA15'
    for massPoint in massIterable(options.mass):
        exec_me('cp %s/%s/%s/base.root %s/%s/%s/%s/'%(options.odir,jet_type,cut,options.odir,jet_type,cut,options.model+str(massPoint)),options.dryRun)
        exec_me('cp %s/%s/%s/rhalphabase.root %s/%s/%s/%s/'%(options.odir,jet_type,cut,options.odir,jet_type,cut,options.model+str(massPoint)),options.dryRun)
        exec_me('python writeMuonCRDatacard.py -i ./ -o %s/%s/%s/%s/ %s -c %s --mass %s'%(options.odir,jet_type,cut,options.model+str(massPoint),fillString,cut,massPoint),options.dryRun)
        os.chdir('%s/%s/%s/%s/'%(options.odir,jet_type,cut,options.model+str(massPoint)))
        exec_me('combineCards.py cat1=card_rhalphabet_cat1.txt cat2=card_rhalphabet_cat2.txt  cat3=card_rhalphabet_cat3.txt cat4=card_rhalphabet_cat4.txt  cat5=card_rhalphabet_cat5.txt cat6=card_rhalphabet_cat6.txt muonCR=datacard_muonCR.txt > card_rhalphabet_muonCR.txt',options.dryRun)
        exec_me('combine -M Asymptotic -v 2 -t -1 --toysFreq card_rhalphabet_muonCR.txt',options.dryRun)
        os.chdir(pwd)
        
        
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('--model',dest="model", default="DMSbb",type="string", help="signal model name")
    parser.add_option('--mass',dest="mass", default='750',type="string", help="mass of resonance")
    parser.add_option('--fillCA15', action='store_true', dest='fillCA15', default =False,help='for CA15', metavar='fillCA15')
    parser.add_option('--lrho', dest='lrho', default=-6.0, type= 'float', help='low value rho cut')
    parser.add_option('--hrho', dest='hrho', default=-2.1, type='float', help=' high value rho cut')
    parser.add_option("--lumi", dest="lumi", default=35.9, type="float", help="luminosity", metavar="lumi")
    parser.add_option('-i', '--ifile', dest='ifile', default='hist_1DZbb.root', help='file with histogram inputs',metavar='ifile')
    parser.add_option('-c', '--cuts', dest='cuts', default='p9', type='string', help='double b-tag cut value')
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write histograms', metavar='odir')
    parser.add_option('--dry-run',dest="dryRun",default=False,action='store_true',
                  help="Just print out commands to run")


    (options,args) = parser.parse_args()

    main(options,args)
