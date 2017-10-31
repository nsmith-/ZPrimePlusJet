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
    tfile_signal = None
    if options.ifile_loose is not None:
        tfile_loose = r.TFile.Open(options.ifile_loose)
    if options.ifile_signal is not None:
	tfile_signal = r.TFile.Open(options.ifile_signal)
        
    boxes = ['pass', 'fail']
#    if tfile_signal is None:
    sigs = ['tthqq125','whqq125','hqq125','zhqq125','vbfhqq125']
#    else:
#        sigs = ['tthqq125_GenpT1','whqq125_GenpT1','hqq125_GenpT1','zhqq125_GenpT1','vbfhqq125_GenpT1',
#		'tthqq125_GenpT2','whqq125_GenpT2','hqq125_GenpT2','zhqq125_GenpT2','vbfhqq125_GenpT2',
#		'tthqq125_GenpT3','whqq125_GenpT3','hqq125_GenpT3','zhqq125_GenpT3','vbfhqq125_GenpT3',
#		'tthqq125_GenpT4','whqq125_GenpT4','hqq125_GenpT4','zhqq125_GenpT4','vbfhqq125_GenpT4',
#		'tthqq125_GenpT5','whqq125_GenpT5','hqq125_GenpT5','zhqq125_GenpT5','vbfhqq125_GenpT5',
#		'tthqq125_GenpT6','whqq125_GenpT6','hqq125_GenpT6','zhqq125_GenpT6','vbfhqq125_GenpT6',
#		'tthqq125_GenpT7','whqq125_GenpT7','hqq125_GenpT7','zhqq125_GenpT7','vbfhqq125_GenpT7',
#		'tthqq125_GenpT8','whqq125_GenpT8','hqq125_GenpT8','zhqq125_GenpT8','vbfhqq125_GenpT8']
    bkgs = ['zqq','wqq','qcd','tqq']
    systs = ['JER','JES','Pu']

    removeUnmatched = options.removeUnmatched

    nBkgd = len(bkgs)
    nSig = len(sigs)
    numberOfMassBins = 23    
    numberOfPtBins = 6
    numberOfGenPtBins = 7

    histoDict = {}
    histoDictLoose = {}
    histoDictSignal = {}

    for proc in (sigs+bkgs):
        for box in boxes:
            print 'getting histogram for process: %s_%s'%(proc,box)
            histoDict['%s_%s'%(proc,box)] = tfile.Get('%s_%s'%(proc,box))
            if tfile_loose is not None:
                histoDictLoose['%s_%s'%(proc,box)] = tfile_loose.Get('%s_%s'%(proc,box))
            if tfile_signal is not None:
		histoDictSignal['%s_%s'%(proc,box)] = tfile_signal.Get('%s_%s'%(proc,box))    
            if removeUnmatched and (proc =='wqq' or proc=='zqq' or ('hqq' in proc and tfile_signal is None)):
                histoDict['%s_%s_matched'%(proc,box)] = tfile.Get('%s_%s_matched'%(proc,box))
                histoDict['%s_%s_unmatched'%(proc,box)] = tfile.Get('%s_%s_unmatched'%(proc,box))
                if tfile_loose is not None:
                    histoDictLoose['%s_%s_matched'%(proc,box)] = tfile_loose.Get('%s_%s_matched'%(proc,box))
                    histoDictLoose['%s_%s_unmatched'%(proc,box)] = tfile_loose.Get('%s_%s_unmatched'%(proc,box))
                    
	    elif removeUnmatched and 'hqq' in proc and tfile_signal is not None:
		histoDictSignal['%s_%s_matched'%(proc,box)] = tfile_signal.Get('%s_%s_matched'%(proc,box))
                histoDictSignal['%s_%s_unmatched'%(proc,box)] = tfile_signal.Get('%s_%s_unmatched'%(proc,box))

                
            for syst in systs:
                print 'getting histogram for process: %s_%s_%sUp'%(proc,box,syst)
                histoDict['%s_%s_%sUp'%(proc,box,syst)] = tfile.Get('%s_%s_%sUp'%(proc,box,syst))
                print 'getting histogram for process: %s_%s_%sDown'%(proc,box,syst)
                histoDict['%s_%s_%sDown'%(proc,box,syst)] = tfile.Get('%s_%s_%sDown'%(proc,box,syst))
		if tfile_signal is not None:
		    histoDictSignal['%s_%s_%sUp'%(proc,box,syst)] = tfile_signal.Get('%s_%s_%sUp'%(proc,box,syst))
                    histoDictSignal['%s_%s_%sDown'%(proc,box,syst)] = tfile_signal.Get('%s_%s_%sDown'%(proc,box,syst))

    if tfile_signal is None:
    	dctpl = open("datacard.tpl")
    else:
	dctpl = open("datacard_7GenpTbins.tpl")
    #dctpl = open("datacardZbb.tpl")
    #dctpl = open("datacardZonly.tpl")
    if tfile_signal is None:
        sigs = ['tthqq125','whqq125','hqq125','zhqq125','vbfhqq125']
    else:
        sigs = ['tthqq125_GenpT1','whqq125_GenpT1','hqq125_GenpT1','zhqq125_GenpT1','vbfhqq125_GenpT1',
               'tthqq125_GenpT2','whqq125_GenpT2','hqq125_GenpT2','zhqq125_GenpT2','vbfhqq125_GenpT2',
               'tthqq125_GenpT3','whqq125_GenpT3','hqq125_GenpT3','zhqq125_GenpT3','vbfhqq125_GenpT3',
               'tthqq125_GenpT4','whqq125_GenpT4','hqq125_GenpT4','zhqq125_GenpT4','vbfhqq125_GenpT4',
               'tthqq125_GenpT5','whqq125_GenpT5','hqq125_GenpT5','zhqq125_GenpT5','vbfhqq125_GenpT5',
               'tthqq125_GenpT6','whqq125_GenpT6','hqq125_GenpT6','zhqq125_GenpT6','vbfhqq125_GenpT6',
               'tthqq125_GenpT7','whqq125_GenpT7','hqq125_GenpT7','zhqq125_GenpT7','vbfhqq125_GenpT7']

    linel = [];
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
		if 'hqq' in proc and tfile_signal is not None:
#		    for k in range(1,numberOfGenPtBins+1):
			k = int(proc[-1])
			proc2 = proc[:-7]
#			print "proc2: ", proc2
                    	rate = histoDictSignal['%s_%s'%(proc2,box)].Integral(1, numberOfMassBins, i, i, k, k)
                    	if rate>0:
                    	    rateJESUp = histoDictSignal['%s_%s_JESUp'%(proc2,box)].Integral(1, numberOfMassBins, i, i, k, k)
                    	    rateJESDown = histoDictSignal['%s_%s_JESDown'%(proc2,box)].Integral(1, numberOfMassBins, i, i, k, k)
                    	    rateJERUp = histoDictSignal['%s_%s_JERUp'%(proc2,box)].Integral(1, numberOfMassBins, i, i, k, k)
                    	    rateJERDown = histoDictSignal['%s_%s_JERDown'%(proc2,box)].Integral(1, numberOfMassBins, i, i, k, k)
                    	    ratePuUp = histoDictSignal['%s_%s_PuUp'%(proc2,box)].Integral(1, numberOfMassBins, i, i, k, k)
                    	    ratePuDown = histoDictSignal['%s_%s_PuDown'%(proc2,box)].Integral(1, numberOfMassBins, i, i, k, k)
                    	    jesErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] =  1.0+(abs(rateJESUp-rate)+abs(rateJESDown-rate))/(2.*rate)   
                    	    jerErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] =  1.0+(abs(rateJERUp-rate)+abs(rateJERDown-rate))/(2.*rate) 
                    	    puErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] =  1.0+(abs(ratePuUp-rate)+abs(ratePuDown-rate))/(2.*rate)
                    	else:
                    	    jesErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] =  1.0
                    	    jerErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] =  1.0
			    puErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] =  1.0

                    	if i == 2:
                    	    scaleptErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] =  0.05
                    	elif i == 3:
                    	    scaleptErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] =  0.1
                    	elif i == 4:
                    	    scaleptErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] =  0.2
                    	elif i == 5:
                    	    scaleptErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] =  0.3
                    	elif i == 6:
                    	    scaleptErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] =  0.4
                
                    	vErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] = 1.0+V_SF_ERR/V_SF
                    	if box=='pass':
                            bbErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] = 1.0+BB_SF_ERR/BB_SF
                    	else:
                    	    ratePass = histoDict['%s_%s'%(proc2,'pass')].Integral()
                    	    rateFail = histoDict['%s_%s'%(proc2,'fail')].Integral()
                    	    if rateFail>0:
                            	bbErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] = 1.0-BB_SF_ERR*(ratePass/rateFail)
                    	    else:
                            	bbErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] = 1.0
                        
                    
                    	for j in range(1,numberOfMassBins+1):                    
                    	    if options.noMcStatShape:                 
                            	matchString = ''
                            	histo = histoDictSignal['%s_%s%s'%(proc2,box,matchString)]
                            
                            	error = array.array('d',[0.0])
                            	rate = histo.IntegralAndError(1,histo.GetNbinsX(),i,i,k,k,error)                 
                            	#mcstatErrs['%s_%s'%(proc,box),i,j] = 1.0+histo.GetBinError(j,i)/histo.Integral()
				if rate > 0:
                            	    mcstatErrs['%s_%s'%(proc,box),i,j,k] = 1.0+(error[0]/rate)
				else:
                                    mcstatErrs['%s_%s'%(proc,box),i,j,k] = 1.0

                    	    else:
                            	mcstatErrs['%s_%s'%(proc,box),i,j,k] = 1.0
                        
		else:
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
                            #mcstatErrs['%s_%s'%(proc,box),i,j] = 1.0+histo.GetBinError(j,i)/histo.Integral()
                            mcstatErrs['%s_%s'%(proc,box),i,j] = 1.0+(error[0]/rate)
                        else:
                            mcstatErrs['%s_%s'%(proc,box),i,j] = 1.0		    

	############# Start changing from here######################
        jesString = 'JES lnN'
        jerString = 'JER lnN'
        puString = 'Pu lnN'
        bbString = 'bbeff lnN'
        vString = 'veff lnN'
        scaleptString = 'scalept shape'
        mcStatStrings = {}
        mcStatGroupString = 'mcstat group ='
        qcdGroupString = 'qcd group = qcdeff'
        for box in boxes:
            for proc in sigs+bkgs:
                for j in range(1,numberOfMassBins+1):
                    if options.noMcStatShape:
			if 'hqq' in proc and tfile_signal is not None:
#			    for k in range(1,numberOfGenPtBins+1):
			    k = int(proc[-1])
			    proc2 = proc[:-7]
                            mcStatStrings['%s_GenpT%s_%s'%(proc2,str(k),box),i,j] = '%sGenpT%s%scat%imcstat%i lnN'%(proc2,str(k),box,i,j)
			else:
			    mcStatStrings['%s_%s'%(proc,box),i,j] = '%s%scat%imcstat%i lnN'%(proc,box,i,j)
                    else:
			if 'hqq' in proc and tfile_signal is not None:
#			    for k in range(1,numberOfGenPtBins+1):
			    k = int(proc[-1])
                            proc2 = proc[:-7]
                            mcStatStrings['%s_GenpT%s_%s'%(proc2,str(k),box),i,j] = '%sGenpT%s%scat%imcstat%i shape'%(proc2,str(k),box,i,j)
			else:
			    mcStatStrings['%s_%s'%(proc,box),i,j] = '%s%scat%imcstat%i shape'%(proc,box,i,j)

        for box in boxes:
            for proc in sigs+bkgs:
                if proc=='qcd':
                    jesString += ' -'
                    jerString += ' -'
                    puString += ' -'
                else:
		    if 'hqq' in proc and tfile_signal is not None:
#			for k in range(1,numberOfGenPtBins+1):
			k = int(proc[-1])
                        proc2 = proc[:-7]
                    	jesString += ' %.3f'%jesErrs['%s_GenpT%s_%s'%(proc2,str(k),box)]
                    	jerString += ' %.3f'%jerErrs['%s_GenpT%s_%s'%(proc2,str(k),box)]
                    	puString += ' %.3f'%puErrs['%s_GenpT%s_%s'%(proc2,str(k),box)]
		    else:
                    	jesString += ' %.3f'%jesErrs['%s_%s'%(proc,box)]
                    	jerString += ' %.3f'%jerErrs['%s_%s'%(proc,box)]
                    	puString += ' %.3f'%puErrs['%s_%s'%(proc,box)]
                        
                if proc in ['qcd','tqq']:
                    if i > 1:
                        scaleptString += ' -'
                else:
                    if i > 1:
			if 'hqq' in proc and tfile_signal is not None:
#                            for k in range(1,numberOfGenPtBins+1):
			    k = int(proc[-1])
                            proc2 = proc[:-7]
                            scaleptString += ' %.3f'%scaleptErrs['%s_GenpT%s_%s'%(proc2,str(k),box)]
			else:
			    scaleptString += ' %.3f'%scaleptErrs['%s_%s'%(proc,box)]
                if proc in ['qcd','tqq','wqq']:
                    bbString += ' -'
                else:
		    if 'hqq' in proc and tfile_signal is not None:
#                    	for k in range(1,numberOfGenPtBins+1):
			k = int(proc[-1])
                        proc2 = proc[:-7]
			bbString += ' %.3f'%bbErrs['%s_GenpT%s_%s'%(proc2,str(k),box)]
		    else:
			bbString += ' %.3f'%bbErrs['%s_%s'%(proc,box)]
                if proc in ['qcd','tqq']:
                    vString += ' -'
                else:
		    if 'hqq' in proc and tfile_signal is not None:
#                        for k in range(1,numberOfGenPtBins+1):
			k = int(proc[-1])
                        proc2 = proc[:-7]
                    	vString += ' %.3f'%vErrs['%s_GenpT%s_%s'%(proc2,str(k),box)]
		    else:
			vString += ' %.3f'%vErrs['%s_%s'%(proc,box)]
                for j in range(1,numberOfMassBins+1):
                    for box1 in boxes:                    
                        for proc1 in sigs+bkgs:                            
                            if proc1==proc and box1==box:
				if 'hqq' in proc and tfile_signal is not None:
#				    for k in range(1,numberOfGenPtBins+1):
				    k = int(proc1[-1])
                            	    proc2 = proc1[:-7]
                                    mcStatStrings['%s_GenpT%s_%s'%(proc2,str(k),box1),i,j] += '\t%.3f'% mcstatErrs['%s_%s'%(proc1,box),i,j,k]
                            	else:                        
                                    mcStatStrings['%s_%s'%(proc1,box1),i,j] += '\t%.3f'% mcstatErrs['%s_%s'%(proc,box),i,j]
			    else:
				mcStatStrings['%s_%s'%(proc1,box1),i,j] += '\t-'

        tag = "cat"+str(i)
        dctmp = open(options.odir+"/card_rhalphabet_%s.txt" % tag, 'w')
        for l in linel:
            if 'JES' in l:
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
                if options.noMcStatShape and proc!='qcd':
		    if 'hqq' in proc and tfile_signal is not None:
#                        for k in range(1,numberOfGenPtBins+1):
			k = int(proc[-1])
                        proc2 = proc[:-7]
                    	print 'include %sGenpT%s%scat%imcstat'%(proc2,str(k),box,i)
                    	dctmp.write(mcStatStrings['%s_GenpT%s_%s'%(proc2,str(k),box),i,1].replace('mcstat1','mcstat') + "\n")
                    	mcStatGroupString += ' %sGenpT%s%scat%imcstat'%(proc2,str(k),box,i)
		    else:
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
		    elif (tfile_loose is not None) and 'hqq' in proc:
			histo = histoDictSignal['%s_%s%s'%(proc,box,matchString)]
                    else:
                        histo = histoDict['%s_%s%s'%(proc,box,matchString)]
		    if (tfile_loose is not None) and 'hqq' in proc:
#			for k in range(1,numberOfGenPtBins+1):
			k = int(proc[-1])
                        proc2 = proc[:-7]
			if abs(histo.GetBinContent(j,i,k)) > 0. and histo.GetBinError(j,i,k) > 0.5*histo.GetBinContent(j,i,k):
	                    massVal = histo.GetXaxis().GetBinCenter(j)
        	            ptVal = histo.GetYaxis().GetBinLowEdge(i) + 0.3*(histo.GetYaxis().GetBinWidth(i))
	                    rhoVal = r.TMath.Log(massVal*massVal/ptVal/ptVal)
	                    if not( options.blind and massVal > BLIND_LO and massVal < BLIND_HI) and not (rhoVal < RHO_LO or rhoVal > RHO_HI):
	                        dctmp.write(mcStatStrings['%s_GenpT%s_%s'%(proc2,str(k),box),i,j] + "\n")
        	                print 'include %sGenpT%s%scat%imcstat%i'%(proc2,str(k),box,i,j)
                	        mcStatGroupString += ' %sGenpT%s%scat%imcstat%i'%(proc2,str(k),box,i,j)
                            else:
                                print 'do not include %sGenpT%s%scat%imcstat%i'%(proc2,str(k),box,i,j)
	                else:
        	            print 'do not include %sGenpT%s%scat%imcstat%i'%(proc2,str(k),box,i,j)
		    else:
                    	if abs(histo.GetBinContent(j,i)) > 0. and histo.GetBinError(j,i) > 0.5*histo.GetBinContent(j,i) and proc!='qcd':
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
            dctmp.write("qcd_fail_%s_Bin%i flatParam \n" % (tag,im+1))
            qcdGroupString += ' qcd_fail_%s_Bin%i'%(tag,im+1)
        dctmp.write(mcStatGroupString + "\n")
        dctmp.write(qcdGroupString + "\n")


###############################################################


	
##-------------------------------------------------------------------------------------
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", type=float, default = 30,help="luminosity", metavar="lumi")
    parser.add_option('-i','--ifile', dest='ifile', default = 'hist_1DZbb.root',help='file with histogram inputs', metavar='ifile')
    parser.add_option('--ifile-loose', dest='ifile_loose', default=None, help='second file with histogram inputs (looser b-tag cut to take W/Z/H templates)', metavar='ifile_loose')
    parser.add_option('--ifile-signal', dest='ifile_signal', default=None, help='second file with 3D histogram inputs for the signal samples',
                      metavar='ifile_signal')
    parser.add_option('-o','--odir', dest='odir', default = 'cards/',help='directory to write cards', metavar='odir')
    parser.add_option('--pseudo', action='store_true', dest='pseudo', default =False,help='signal comparison', metavar='isData')
    parser.add_option('--blind', action='store_true', dest='blind', default =False,help='blind signal region', metavar='blind')
    parser.add_option('--remove-unmatched', action='store_true', dest='removeUnmatched', default =False,help='remove unmatched', metavar='removeUnmatched')
    parser.add_option('--no-mcstat-shape', action='store_true', dest='noMcStatShape', default =False,help='change mcstat uncertainties to lnN', metavar='noMcStatShape')

    (options, args) = parser.parse_args()

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
