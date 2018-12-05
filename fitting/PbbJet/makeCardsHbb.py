#!/usr/bin/env python

import ROOT as r,sys,math,array,os
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array

# including other directories
sys.path.insert(0, '../.')
from tools import *

from buildRhalphabetHbb import MASS_BINS,MASS_LO,MASS_HI,BLIND_LO,BLIND_HI,RHO_LO,RHO_HI
from rhalphabet_builder import BB_SF,BB_SF_ERR,V_SF,V_SF_ERR,GetSF


##-------------------------------------------------------------------------------------
def main(options,args):
	
    tfile = r.TFile.Open(options.ifile)
    tfile_loose = None
    if options.ifile_loose is not None:
        tfile_loose = r.TFile.Open(options.ifile_loose)
        
    boxes = ['pass', 'fail']
    sigs = ['tthqq125','whqq125','hqq125','zhqq125','vbfhqq125']
    bkgs = ['zqq','wqq','tqq']
    if options.forcomb:
        bkgs.append('qcd2017')
    else:
        bkgs.append('qcd')
    systs = ['JER','JES','Pu']

    removeUnmatched = options.removeUnmatched

    nBkgd = len(bkgs)
    nSig = len(sigs)
    numberOfMassBins = 23    
    numberOfPtBins = 6
    procsToRemove = []

    histoDict = {}
    histoDictLoose = {}

    for proc in (sigs+bkgs):
        for box in boxes:
            if options.forcomb and '2017' in proc:
                proc = proc.replace("2017","")
            print 'getting histogram for process: %s_%s'%(proc,box)
            histoDict['%s_%s'%(proc,box)] = tfile.Get('%s_%s'%(proc,box))
            if tfile_loose is not None:
                histoDictLoose['%s_%s'%(proc,box)] = tfile_loose.Get('%s_%s'%(proc,box))
                
            if removeUnmatched and (proc =='wqq' or proc=='zqq' or 'hqq' in proc):
                histoDict['%s_%s_matched'%(proc,box)] = tfile.Get('%s_%s_matched'%(proc,box))
                histoDict['%s_%s_unmatched'%(proc,box)] = tfile.Get('%s_%s_unmatched'%(proc,box))
                if tfile_loose is not None:
                    histoDictLoose['%s_%s_matched'%(proc,box)] = tfile_loose.Get('%s_%s_matched'%(proc,box))
                    histoDictLoose['%s_%s_unmatched'%(proc,box)] = tfile_loose.Get('%s_%s_unmatched'%(proc,box))
                    
                
            for syst in systs:
                print 'getting histogram for process: %s_%s_%sUp'%(proc,box,syst)
                histoDict['%s_%s_%sUp'%(proc,box,syst)] = tfile.Get('%s_%s_%sUp'%(proc,box,syst))
                print 'getting histogram for process: %s_%s_%sDown'%(proc,box,syst)
                histoDict['%s_%s_%sDown'%(proc,box,syst)] = tfile.Get('%s_%s_%sDown'%(proc,box,syst))

    if options.forcomb:
        dctpl = open("datacard_2017.tpl")
    else:
        dctpl = open("datacard.tpl")
    #dctpl = open("datacardZbb.tpl")
    #dctpl = open("datacardZonly.tpl")

    linel = []
    for line in dctpl: 
        print line.strip().split()
        linel.append(line.strip())

    for i in range(1,numberOfPtBins+1):

        jesErrs = {}
        jerErrs = {}
        puErrs = {}
        bbErrs = {}
        vErrs = {}
        mcstatErrs = {}
        scaleptErrs = {}
        for box in boxes:
            for proc in (sigs+bkgs):
                if options.forcomb and '2017' in proc:
                    proc = proc.replace("2017","")
                rate = histoDict['%s_%s'%(proc,box)].Integral(1, numberOfMassBins, i, i)
                if rate>0:
                    rateJESUp = histoDict['%s_%s_JESUp'%(proc,box)].Integral(1, numberOfMassBins, i, i)
                    rateJESDown = histoDict['%s_%s_JESDown'%(proc,box)].Integral(1, numberOfMassBins, i, i)
                    rateJERUp = histoDict['%s_%s_JERUp'%(proc,box)].Integral(1, numberOfMassBins, i, i)
                    rateJERDown = histoDict['%s_%s_JERDown'%(proc,box)].Integral(1, numberOfMassBins, i, i)
                    ratePuUp = histoDict['%s_%s_PuUp'%(proc,box)].Integral(1, numberOfMassBins, i, i)
                    ratePuDown = histoDict['%s_%s_PuDown'%(proc,box)].Integral(1, numberOfMassBins, i, i)
                    jesErrs['%s_%s'%(proc,box)] =  1.0+(abs(rateJESUp-rate)+abs(rateJESDown-rate))/(2.*rate)   
                    jerErrs['%s_%s'%(proc,box)] =  1.0+(abs(rateJERUp-rate)+abs(rateJERDown-rate))/(2.*rate) 
                    puErrs['%s_%s'%(proc,box)] =  1.0+(abs(ratePuUp-rate)+abs(ratePuDown-rate))/(2.*rate)
                else:
                    jesErrs['%s_%s'%(proc,box)] =  1.0
                    jerErrs['%s_%s'%(proc,box)] =  1.0
                    puErrs['%s_%s'%(proc,box)] =  1.0
                    print "to remove: proc, cat, box, rate =", proc, "cat%i"%i, box, rate
                    procsToRemove.append((proc, "cat%i"%i, box))
                if i == 2:
                    scaleptErrs['%s_%s'%(proc,box)] =  0.05
                elif i == 3:
                    scaleptErrs['%s_%s'%(proc,box)] =  0.1
                elif i == 4:
                    scaleptErrs['%s_%s'%(proc,box)] =  0.2
                elif i == 5:
                    scaleptErrs['%s_%s'%(proc,box)] =  0.3
                elif i == 6:
                    scaleptErrs['%s_%s'%(proc,box)] =  0.4
                
                vErrs['%s_%s'%(proc,box)] = 1.0+V_SF_ERR/V_SF
                if box=='pass':
                    bbErrs['%s_%s'%(proc,box)] = 1.0+BB_SF_ERR/BB_SF
                else:
                    ratePass = histoDict['%s_%s'%(proc,'pass')].Integral()
                    rateFail = histoDict['%s_%s'%(proc,'fail')].Integral()
                    if rateFail>0:
                        bbErrs['%s_%s'%(proc,box)] = 1.0-BB_SF_ERR*(ratePass/rateFail)
                    else:
                        bbErrs['%s_%s'%(proc,box)] = 1.0
                        
                    
                for j in range(1,numberOfMassBins+1):                    
                    if options.noMcStatShape:                 
                        matchString = ''
                        if removeUnmatched and (proc =='wqq' or proc=='zqq'):
                            matchString = '_matched'
                        if (tfile_loose is not None) and (proc =='wqq' or proc=='zqq') and 'pass' in box:
                            histo = histoDictLoose['%s_%s%s'%(proc,box,matchString)]
                        else:
                            histo = histoDict['%s_%s%s'%(proc,box,matchString)]
                            
                        error = array.array('d',[0.0])
                        rate = histo.IntegralAndError(1,histo.GetNbinsX(),i,i,error)                 
                        if rate>0:
                            mcstatErrs['%s_%s'%(proc,box),i,j] = 1.0+(error[0]/rate)
                        else:
                            mcstatErrs['%s_%s'%(proc,box),i,j] = 1.0
                            if (proc, "cat%i"%i, box) not in procsToRemove:
                                procsToRemove.append((proc, "cat%i"%i, box))
                    else:
                        mcstatErrs['%s_%s'%(proc,box),i,j] = 1.0
                        

        jesString = 'JES lnN'
        jerString = 'JER lnN'
        puString = 'Pu lnN'
        bbString = 'bbeff lnN'
        vString = 'veff lnN'
        scaleptString = 'scalept shape'
        mcStatStrings = {}
        mcStatGroupString = 'mcstat group ='
        if options.forcomb:
            qcdGroupString = 'qcd2017 group = qcd2017eff%s'%options.suffix
        else:
            qcdGroupString = 'qcd group = qcdeff%s'%options.suffix
        for box in boxes:
            for proc in sigs+bkgs:
                for j in range(1,numberOfMassBins+1):
                    if options.noMcStatShape:
                        mcStatStrings['%s_%s'%(proc,box),i,j] = '%s%scat%imcstat%i lnN'%(proc,box,i,j)
                    else:
                        mcStatStrings['%s_%s'%(proc,box),i,j] = '%s%scat%imcstat%i shape'%(proc,box,i,j)
                    
        for box in boxes:
            for proc in sigs+bkgs:
                if proc=='qcd' or proc=='qcd2017':
                    jesString += ' -'
                    jerString += ' -'
                    puString += ' -'
                else:
                    jesString += ' %.3f'%jesErrs['%s_%s'%(proc,box)]
                    jerString += ' %.3f'%jerErrs['%s_%s'%(proc,box)]
                    puString += ' %.3f'%puErrs['%s_%s'%(proc,box)]                        
                if proc in ['qcd','tqq','qcd2017']:
                    if i > 1:
                        scaleptString += ' -'
                else:
                    if i > 1:
                        scaleptString += ' %.3f'%scaleptErrs['%s_%s'%(proc,box)]
                if proc in ['qcd','tqq','wqq','qcd2017']:
                    bbString += ' -'
                else:
                    bbString += ' %.3f'%bbErrs['%s_%s'%(proc,box)]
                if proc in ['qcd','tqq','qcd2017']:
                    vString += ' -'
                else:
                    vString += ' %.3f'%vErrs['%s_%s'%(proc,box)]
                for j in range(1,numberOfMassBins+1):
                    for box1 in boxes:                    
                        for proc1 in sigs+bkgs:                            
                            if proc1==proc and box1==box and proc!='qcd' and proc !='qcd2017':
                                mcStatStrings['%s_%s'%(proc1,box1),i,j] += '\t%.3f'% mcstatErrs['%s_%s'%(proc,box),i,j]
                            else:                        
                                mcStatStrings['%s_%s'%(proc1,box1),i,j] += '\t-'

        tag = "cat"+str(i)
        dctmp = open(options.odir+"/card_rhalphabet_%s.txt" % tag, 'w')
        for l in linel:
            if 'shapes qcd' in l:
                newline = l+options.suffix
            elif 'shapes qcd2017' in l:
                newline = l+options.suffix
            elif 'JES' in l:
                newline = jesString
            elif 'JER' in l:
                newline = jerString
            elif 'Pu' in l:
                newline = puString
            elif 'bbeff' in l:
                newline = bbString
            elif 'veff' in l:
                newline = vString
            elif 'scalept' in l and i>1:
                newline = scaleptString
            elif 'TQQEFF' in l:
                tqqeff = histoDict['tqq_pass'].Integral() / (
                histoDict['tqq_pass'].Integral() + histoDict['tqq_fail'].Integral())
                newline = l.replace('TQQEFF','%.4f'%tqqeff)
            elif 'wznormEW' in l:
                if i==4:
                    newline = l.replace('1.05','1.15')
                elif i==5:
                    newline = l.replace('1.05','1.15')
                elif i==6:
                    newline = l.replace('1.05','1.15')
                else:
                    newline = l
            elif 'znormEW' in l:
                if i==3:
                    newline = l.replace('1.15','1.25')
                elif i==4:
                    newline = l.replace('1.15','1.35')
                elif i==5:
                    newline = l.replace('1.15','1.35')
                elif i==6:
                    newline = l.replace('1.15','1.35')      
                else:
                    newline = l              
            else:
                newline = l
            if "CATX" in l:
                newline = newline.replace('CATX',tag)
            dctmp.write(newline + "\n")
        for box in boxes:
            for proc in sigs+bkgs:
                if options.forcomb and '2017' in proc:
                    proc = proc.replace("2017","")
                if options.noMcStatShape and proc!='qcd' and proc!='qcd2017' and (proc, 'cat%i'%i, box) not in procsToRemove:
                    print 'include %s%scat%imcstat'%(proc,box,i)
                    dctmp.write(mcStatStrings['%s_%s'%(proc,box),i,1].replace('mcstat1','mcstat') + "\n")
                    mcStatGroupString += ' %s%scat%imcstat'%(proc,box,i)
                    continue
                for j in range(1,numberOfMassBins+1):                    
                    # if stat. unc. is greater than 50% 
                    matchString = ''
                    if removeUnmatched and (proc =='wqq' or proc=='zqq'):
                        matchString = '_matched'
                    if (tfile_loose is not None) and (proc =='wqq' or proc=='zqq') and 'pass' in box:
                        histo = histoDictLoose['%s_%s%s'%(proc,box,matchString)]
                    else:
                        histo = histoDict['%s_%s%s'%(proc,box,matchString)]
                    if abs(histo.GetBinContent(j,i)) > 0. and histo.GetBinError(j,i) > 0.5*histo.GetBinContent(j,i) and proc!='qcd' and proc!='qcd2017':
                        massVal = histo.GetXaxis().GetBinCenter(j)
                        ptVal = histo.GetYaxis().GetBinLowEdge(i) + 0.3*(histo.GetYaxis().GetBinWidth(i))
                        rhoVal = r.TMath.Log(massVal*massVal/ptVal/ptVal)
                        if not( options.blind and massVal > BLIND_LO and massVal < BLIND_HI) and not (rhoVal < RHO_LO or rhoVal > RHO_HI):
                            dctmp.write(mcStatStrings['%s_%s'%(proc,box),i,j] + "\n")
                            print 'include %s%scat%imcstat%i'%(proc,box,i,j)
                            mcStatGroupString += ' %s%scat%imcstat%i'%(proc,box,i,j)
                        else:
                            print 'do not include %s%scat%imcstat%i'%(proc,box,i,j)
                    else:
                        print 'do not include %s%scat%imcstat%i'%(proc,box,i,j)
                        
        for im in range(numberOfMassBins):
            if options.forcomb:
                dctmp.write("qcd2017_fail_%s_Bin%i%s flatParam \n" % (tag,im+1,options.suffix))
                qcdGroupString += ' qcd2017_fail_%s_Bin%i%s'%(tag,im+1,options.suffix)
            else:
                dctmp.write("qcd_fail_%s_Bin%i%s flatParam \n" % (tag,im+1,options.suffix))
                qcdGroupString += ' qcd_fail_%s_Bin%i%s'%(tag,im+1,options.suffix)
        if options.forcomb:
            flatPars = ['r1p0', 'r2p0', 'r0p1', 'r1p1', 'r2p1', 'qcd2017eff']
        else:
            flatPars = ['r1p0', 'r2p0', 'r0p1', 'r1p1', 'r2p1', 'qcdeff']
        for flatPar in flatPars:
            dctmp.write('%s%s flatParam \n'%(flatPar,options.suffix))

        dctmp.write(mcStatGroupString + "\n")
        dctmp.write(qcdGroupString + "\n")
        dctmp.close()
    def removeProc(proc, tag, box):
        dctmp = open(options.odir+"/card_rhalphabet_%s.txt" % tag, 'r')
        linel = []
        firstProcessLine = True
        for iline, line in enumerate(dctmp):
            l = line.strip().split()
            linel.append(l)
        for iline, l in enumerate(linel):
            if l[0]=='process' and firstProcessLine: 
                totalProcs = len(l)-1
                #procIndex = l.index(proc)
                procIndex = [il for il, nl in enumerate(l) if nl == proc][0] # first instance of process (pass category)
                if linel[iline-1][procIndex]!='%s_%s'%(box,tag):
                    procIndex = [il for il, nl in enumerate(l) if nl == proc][1] # second instance of process (fail category)
                if linel[iline-1][procIndex]=='%s_%s'%(box,tag):
                    print "REMOVING", proc, tag, box                    
                else:
                    print "NOT REMOVING; NO MATCH", proc, tag, box                    
                l.pop(procIndex)
                linel[iline] = l
                linel[iline-1].pop(procIndex)
                firstProcessLine = False
            elif not firstProcessLine and len(l) > 1 and l[1]=='group':
                continue
            elif not firstProcessLine and len(l)==totalProcs+1:
                l.pop(procIndex)
                linel[iline] = l
            elif not firstProcessLine and len(l)==totalProcs+2:
                l.pop(procIndex+1)     
                linel[iline]= l
        dctmp.close()
        dctmp_w = open(options.odir+"/card_rhalphabet_%s.txt" % tag, 'w')
        for l in linel: dctmp_w.write(' '.join(l)+'\n')

    for proc, tag, box in procsToRemove: 
        removeProc(proc, tag, box)
###############################################################


	
##-------------------------------------------------------------------------------------
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", type=float, default = 30,help="luminosity", metavar="lumi")
    parser.add_option('-i','--ifile', dest='ifile', default = 'hist_1DZbb.root',help='file with histogram inputs', metavar='ifile')
    parser.add_option('--ifile-loose', dest='ifile_loose', default=None, help='second file with histogram inputs (looser b-tag cut to take W/Z/H templates)', metavar='ifile_loose')
    parser.add_option('-o','--odir', dest='odir', default = 'cards/',help='directory to write cards', metavar='odir')
    parser.add_option('--pseudo', action='store_true', dest='pseudo', default =False,help='signal comparison', metavar='isData')
    parser.add_option('--blind', action='store_true', dest='blind', default =False,help='blind signal region', metavar='blind')
    parser.add_option('--for-comb', action='store_true', dest='forcomb', default =False,help='use 2017 qcd', metavar='forcomb')
    parser.add_option('--remove-unmatched', action='store_true', dest='removeUnmatched', default =False,help='remove unmatched', metavar='removeUnmatched')
    parser.add_option('--no-mcstat-shape', action='store_true', dest='noMcStatShape', default =False,help='change mcstat uncertainties to lnN', metavar='noMcStatShape')
    parser.add_option('--suffix', dest='suffix', default='', help='suffix for conflict variables',metavar='suffix')

    (options, args) = parser.parse_args()

    if options.suffix!='':
        options.suffix='_'+options.suffix
    import tdrstyle
    tdrstyle.setTDRStyle()
    r.gStyle.SetPadTopMargin(0.10)
    r.gStyle.SetPadLeftMargin(0.16)
    r.gStyle.SetPadRightMargin(0.10)
    r.gStyle.SetPalette(1)
    r.gStyle.SetPaintTextFormat("1.1f")
    r.gStyle.SetOptFit(0000)
    r.gROOT.SetBatch()

    main(options,args)
##-------------------------------------------------------------------------------------
