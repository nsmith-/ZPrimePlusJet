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
    jet_type = options.box

    cut = options.cuts.split(',')[0]

    blindString = ''
    if options.blind:
        blindString = '--blind'

    pseudoString = ''
    if options.pseudo:
        blindString = '--pseudo'


    if options.ifile_loose is not None:
        ifile_loose = '--ifile-loose %s'%options.ifile_loose
    else:
        ifile_loose = ''
    exec_me('python makeCardsPhibb.py -i %s %s  -o %s/%s/%s --remove-unmatched --no-mcstat-shape  -c %s --lrho %f --hrho %f --masses %s %s'%(options.ifile,ifile_loose,
                                                                                                                           options.odir,
                                                                                                                           jet_type,
                                                                                                                           cut, cut,
                                                                                                                           options.lrho,
                                                                                                                           options.hrho,repr(options.masses),blindString),options.dryRun)
    exec_me('python buildRhalphabetPhibb.py -i %s %s -o %s/%s/%s/ --remove-unmatched  --prefit --use-qcd -c %s --lrho %f --hrho %f --nr %i --np %i --masses %s %s %s'%(options.ifile,ifile_loose,
                                                                                                                                            options.odir,
                                                                                                                                            jet_type,
                                                                                                                                            cut, cut,
                                                                                                                                            options.lrho,
                                                                                                                                            options.hrho,
                                                                                                                                            options.NR,
                                                                                                                                            options.NP,repr(options.masses),blindString,pseudoString),options.dryRun)

                                                                                                                                            
    pwd = os.environ['PWD']
    print 'pwd = ', pwd

    fillString = ''
    if options.box=='CA15':
        fillString = '--fillCA15'
    for massPoint in massIterable(options.masses):
        exec_me('cp %s/%s/%s/base.root %s/%s/%s/%s/'%(options.odir,jet_type,cut,options.odir,jet_type,cut,options.model+str(massPoint)),options.dryRun)
        exec_me('cp %s/%s/%s/rhalphabase.root %s/%s/%s/%s/'%(options.odir,jet_type,cut,options.odir,jet_type,cut,options.model+str(massPoint)),options.dryRun)
        exec_me('python writeMuonCRDatacard.py -i %s/ -o %s/%s/%s/%s/ %s -c %s --mass %s --no-mcstat-shape'%(os.path.dirname(options.ifile),options.odir,jet_type,cut,options.model+str(massPoint),fillString,cut,massPoint),options.dryRun)
        os.chdir('%s/%s/%s/%s/'%(options.odir,jet_type,cut,options.model+str(massPoint)))
        if options.box=='CA15':
            exec_me('combineCards.py cat2=card_rhalphabet_cat2.txt  cat3=card_rhalphabet_cat3.txt cat4=card_rhalphabet_cat4.txt  cat5=card_rhalphabet_cat5.txt cat6=card_rhalphabet_cat6.txt muonCR=datacard_muonCR.txt > card_rhalphabet_muonCR.txt',options.dryRun)
        else:
            exec_me('combineCards.py cat1=card_rhalphabet_cat1.txt cat2=card_rhalphabet_cat2.txt  cat3=card_rhalphabet_cat3.txt cat4=card_rhalphabet_cat4.txt  cat5=card_rhalphabet_cat5.txt cat6=card_rhalphabet_cat6.txt muonCR=datacard_muonCR.txt > card_rhalphabet_muonCR.txt',options.dryRun)
        if options.observed:
            observedString = '' # real data, observed
        elif not options.observed and options.pseudo:
            observedString = '-t -1 --run expected' #MC, a-priori expected
        elif not options.observed and not options.pseudo:
            observedString = '-t -1 --toysFreq --run expected' #real dataset, a-posteriori expected
        
        exec_me('combine -M Asymptotic -v 2 card_rhalphabet_muonCR.txt --saveWorkspace -n %s_%s_lumi-%.1f_%s %s'%(options.model,massPoint,options.lumi,jet_type,observedString),options.dryRun)
        #exec_me('combine -M MaxLikelihoodFit -v 2 -t -1 card_rhalphabet_muonCR.txt --saveNormalizations --plot --saveShapes --saveWithUncertainties --saveWorkspace -n %s_%s_lumi-%.1f_%s'%(options.model,massPoint,options.lumi,jet_type),options.dryRun)
        os.chdir(pwd)
        
        
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('--model',dest="model", default="DMSbb",type="string", help="signal model name")
    parser.add_option('--masses',dest='masses', default='50,100,125,200,300,350,400,500',type="string", help="masses of resonance")
    parser.add_option('-b','--box',dest="box", default="AK8",type="string", help="box name")
    parser.add_option('--lrho', dest='lrho', default=-6.0, type= 'float', help='low value rho cut')
    parser.add_option('--hrho', dest='hrho', default=-2.1, type='float', help=' high value rho cut')
    parser.add_option("--lumi", dest="lumi", default=35.9, type="float", help="luminosity", metavar="lumi")
    parser.add_option('-i', '--ifile', dest='ifile', default='hist_1DZbb.root', help='file with histogram inputs',metavar='ifile')
    parser.add_option('--ifile-loose', dest='ifile_loose', default=None, help='second file with histogram inputs (looser b-tag cut to take W/Z templates)',metavar='ifile_loose')
    parser.add_option('-c', '--cuts', dest='cuts', default='p9', type='string', help='double b-tag cut value')
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write histograms', metavar='odir')    
    parser.add_option('--nr' ,action='store',type='int',dest='NR'   ,default=2, help='order of rho polynomial for model')
    parser.add_option('--np' ,action='store',type='int',dest='NP'   ,default=1, help='order of pt polynomial for model')
    parser.add_option('--pseudo', action='store_true', dest='pseudo', default=False, help='use MC', metavar='pseudo')
    parser.add_option('--blind', action='store_true', dest='blind', default=False, help='run on blinded dataset')
    parser.add_option('--observed', action='store_true', dest='observed', default=False, help='get observed limits')
    parser.add_option('--dry-run',dest="dryRun",default=False,action='store_true',
                  help="Just print out commands to run")


    (options,args) = parser.parse_args()

    main(options,args)
