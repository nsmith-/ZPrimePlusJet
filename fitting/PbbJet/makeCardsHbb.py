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

from buildRhalphabetHbb_temp import MASS_BINS,MASS_LO,MASS_HI,BLIND_LO,BLIND_HI,RHO_LO,RHO_HI
from rhalphabet_builder_temp import BB_SF,BB_SF_ERR,V_SF,V_SF_ERR,GetSF


##-------------------------------------------------------------------------------------
def main(options,args):
	
    tfile = r.TFile.Open(options.ifile)
    tfile_loose = None
    tfile_signal = None
    if options.ifile_loose is not None:
        tfile_loose = r.TFile.Open(options.ifile_loose)
    if options.ifile_signal is not None:
	tfile_signal = r.TFile.Open(options.ifile_signal)
        histo_temp = tfile_signal.Get('hqq125_pass')
        numberOfGenPtBins = histo_temp.GetZaxis().GetNbins()
        
    boxes = ['pass', 'fail']
    sigs = ['xhqq125','hqq125']
    bkgs = ['zqq','wqq','qcd','tqq']
    systs = ['JER','JES','Pu']

    removeUnmatched = options.removeUnmatched

    nBkgd = len(bkgs)
    nSig = len(sigs)
    numberOfMassBins = 23    
    numberOfPtBins = options.nRecoBins

    histoDict = {}
    histoDictLoose = {}
    histoDictSignal = {}

    for proc in (sigs+bkgs):
        for box in boxes:
            print 'getting histogram for process: %s_%s'%(proc,box)
            histoDict['%s_%s'%(proc,box)] = tfile.Get('%s_%s'%(proc,box))
            if tfile_loose is not None:
                histoDictLoose['%s_%s'%(proc,box)] = tfile_loose.Get('%s_%s'%(proc,box))
            if tfile_signal is not None and proc == 'hqq125':
		histoDictSignal['%s_%s'%(proc,box)] = tfile_signal.Get('%s_%s'%(proc,box))
            if removeUnmatched and (proc =='wqq' or proc=='zqq' or ('hqq' in proc and tfile_signal is None) or proc == 'xhqq125'):
                histoDict['%s_%s_matched'%(proc,box)] = tfile.Get('%s_%s_matched'%(proc,box))
                histoDict['%s_%s_unmatched'%(proc,box)] = tfile.Get('%s_%s_unmatched'%(proc,box))
                if tfile_loose is not None:
                    histoDictLoose['%s_%s_matched'%(proc,box)] = tfile_loose.Get('%s_%s_matched'%(proc,box))
                    histoDictLoose['%s_%s_unmatched'%(proc,box)] = tfile_loose.Get('%s_%s_unmatched'%(proc,box))
                    
	    elif removeUnmatched and proc == 'hqq125' and tfile_signal is not None:
		histoDictSignal['%s_%s_matched'%(proc,box)] = tfile_signal.Get('%s_%s_matched'%(proc,box))
                histoDictSignal['%s_%s_unmatched'%(proc,box)] = tfile_signal.Get('%s_%s_unmatched'%(proc,box))

                
            for syst in systs:
                print 'getting histogram for process: %s_%s_%sUp'%(proc,box,syst)
                histoDict['%s_%s_%sUp'%(proc,box,syst)] = tfile.Get('%s_%s_%sUp'%(proc,box,syst))
                print 'getting histogram for process: %s_%s_%sDown'%(proc,box,syst)
                histoDict['%s_%s_%sDown'%(proc,box,syst)] = tfile.Get('%s_%s_%sDown'%(proc,box,syst))
		if tfile_signal is not None and proc == 'hqq125':
		    histoDictSignal['%s_%s_%sUp'%(proc,box,syst)] = tfile_signal.Get('%s_%s_%sUp'%(proc,box,syst))
                    histoDictSignal['%s_%s_%sDown'%(proc,box,syst)] = tfile_signal.Get('%s_%s_%sDown'%(proc,box,syst))

    sigs_temp = ['xhqq125','hqq125']
    if tfile_signal is None:
        sigs = ['xhqq125','hqq125']
    else:
	sigs = []
        for proc in sigs_temp:
	    if proc == 'hqq125':
                for i in range(1, numberOfGenPtBins + 1):
#                for i in range(2, numberOfGenPtBins + 1):
		    sigs.append(proc + '_GenpT' + str(i))
	    else:
		sigs.append(proc)

    nSig = len(sigs)

    RecoBins = []
    nCombinedRecoBins = []
    if numberOfPtBins == 6:
        RecoBins.append(1)
        RecoBins.append(2)
        RecoBins.append(3)
        RecoBins.append(4)
        RecoBins.append(5)
        RecoBins.append(6)
	nCombinedRecoBins.append(0)
        nCombinedRecoBins.append(0)
        nCombinedRecoBins.append(0)
        nCombinedRecoBins.append(0)
        nCombinedRecoBins.append(0)
        nCombinedRecoBins.append(0)	
    if numberOfPtBins == 3:
        RecoBins.append(1)
        RecoBins.append(2)
        RecoBins.append(5)
        nCombinedRecoBins.append(0)
        nCombinedRecoBins.append(2)
        nCombinedRecoBins.append(1)
    if numberOfPtBins == 2:
        RecoBins.append(1)
        RecoBins.append(4)
        nCombinedRecoBins.append(2)
        nCombinedRecoBins.append(2)
    if numberOfPtBins == 1:
        RecoBins.append(1)
        nCombinedRecoBins.append(5)


    for i in range(1,numberOfPtBins+1):

    	rates = {}
        jesErrsUp = {}
        jesErrsDown = {}
        jerErrsUp = {}
        jerErrsDown = {}
        puErrs = {}
        bbErrs = {}
        vErrs = {}
        mcstatErrs = {}
        scaleptErrs = {}
        for box in boxes:
            for proc in (sigs+bkgs):
		if 'GenpT' in proc and tfile_signal is not None:
			k = int(proc[-1])
			proc2 = proc[:-7]
			print "proc: ", proc
			print "box: ", box
                    	rate = histoDictSignal['%s_%s'%(proc2,box)].Integral(1, numberOfMassBins, RecoBins[i-1], RecoBins[i-1]+nCombinedRecoBins[i-1], k, k)
			rates['%s_GenpT%s_%s'%(proc2,str(k),box)] = rate
                    	if rate>0:
                    	    rateJESUp = histoDictSignal['%s_%s_JESUp'%(proc2,box)].Integral(1, numberOfMassBins, RecoBins[i-1], RecoBins[i-1]+nCombinedRecoBins[i-1], k, k)
                    	    rateJESDown = histoDictSignal['%s_%s_JESDown'%(proc2,box)].Integral(1, numberOfMassBins, RecoBins[i-1], RecoBins[i-1]+nCombinedRecoBins[i-1], k, k)
                    	    rateJERUp = histoDictSignal['%s_%s_JERUp'%(proc2,box)].Integral(1, numberOfMassBins, RecoBins[i-1], RecoBins[i-1]+nCombinedRecoBins[i-1], k, k)
                    	    rateJERDown = histoDictSignal['%s_%s_JERDown'%(proc2,box)].Integral(1, numberOfMassBins, RecoBins[i-1], RecoBins[i-1]+nCombinedRecoBins[i-1], k, k)
                    	    ratePuUp = histoDictSignal['%s_%s_PuUp'%(proc2,box)].Integral(1, numberOfMassBins, RecoBins[i-1], RecoBins[i-1]+nCombinedRecoBins[i-1], k, k)
                    	    ratePuDown = histoDictSignal['%s_%s_PuDown'%(proc2,box)].Integral(1, numberOfMassBins, RecoBins[i-1], RecoBins[i-1]+nCombinedRecoBins[i-1], k, k)
                    	    jesErrsUp['%s_GenpT%s_%s'%(proc2,str(k),box)] =  1.0+(rateJESUp-rate)/(rate)   
                            jesErrsDown['%s_GenpT%s_%s'%(proc2,str(k),box)] =  1.0+(rateJESDown-rate)/(rate)
                            jerErrsUp['%s_GenpT%s_%s'%(proc2,str(k),box)] =  1.0+(rateJERUp-rate)/(rate)
                    	    jerErrsDown['%s_GenpT%s_%s'%(proc2,str(k),box)] =  1.0+(rateJERDown-rate)/(rate) 
                    	    puErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] =  1.0+(abs(ratePuUp-rate)+abs(ratePuDown-rate))/(2.*rate)
			    print "rateJERUp: ", rateJERUp
			    print "rateJERDown: ", rateJERDown
			    print "rate: ", rate
                            print "1.0+(rateJERUp-rate)/(rate): ", 1.0+(rateJERUp-rate)/(rate)
			    print "1.0+(rateJERDown-rate)/(rate): ", 1.0+(rateJERDown-rate)/(rate)
                    	else:
                            jesErrsUp['%s_GenpT%s_%s'%(proc2,str(k),box)] =  1.0
                    	    jesErrsDown['%s_GenpT%s_%s'%(proc2,str(k),box)] =  1.0
                            jerErrsUp['%s_GenpT%s_%s'%(proc2,str(k),box)] =  1.0
                    	    jerErrsDown['%s_GenpT%s_%s'%(proc2,str(k),box)] =  1.0
			    puErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] =  1.0

                    	if RecoBins[i-1]+nCombinedRecoBins[i-1] == 2:
                    	    scaleptErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] =  0.05
                    	elif RecoBins[i-1]+nCombinedRecoBins[i-1] == 3:
                    	    scaleptErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] =  0.1
                    	elif RecoBins[i-1]+nCombinedRecoBins[i-1] == 4:
                    	    scaleptErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] =  0.2
                    	elif RecoBins[i-1]+nCombinedRecoBins[i-1] == 5:
                    	    scaleptErrs['%s_GenpT%s_%s'%(proc2,str(k),box)] =  0.3
                    	elif RecoBins[i-1]+nCombinedRecoBins[i-1] == 6:
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
                            	rate = histo.IntegralAndError(1,histo.GetNbinsX(),RecoBins[i-1], RecoBins[i-1]+nCombinedRecoBins[i-1],k,k,error)                 
                            	#mcstatErrs['%s_%s'%(proc,box),i,j] = 1.0+histo.GetBinError(j,i)/histo.Integral()
				if rate > 0:
                            	    mcstatErrs['%s_%s'%(proc,box),i,j,k] = 1.0+(error[0]/rate)
				else:
                                    mcstatErrs['%s_%s'%(proc,box),i,j,k] = 1.0

                    	    else:
                            	mcstatErrs['%s_%s'%(proc,box),i,j,k] = 1.0
                        
		else:
                    rate = histoDict['%s_%s'%(proc,box)].Integral(1, numberOfMassBins, RecoBins[i-1], RecoBins[i-1]+nCombinedRecoBins[i-1])
                    rates['%s_%s'%(proc,box)] = rate
                    if rate>0:
                        rateJESUp = histoDict['%s_%s_JESUp'%(proc,box)].Integral(1, numberOfMassBins, RecoBins[i-1], RecoBins[i-1]+nCombinedRecoBins[i-1])
                        rateJESDown = histoDict['%s_%s_JESDown'%(proc,box)].Integral(1, numberOfMassBins, RecoBins[i-1], RecoBins[i-1]+nCombinedRecoBins[i-1])
                        rateJERUp = histoDict['%s_%s_JERUp'%(proc,box)].Integral(1, numberOfMassBins, RecoBins[i-1], RecoBins[i-1]+nCombinedRecoBins[i-1])
                        rateJERDown = histoDict['%s_%s_JERDown'%(proc,box)].Integral(1, numberOfMassBins, RecoBins[i-1], RecoBins[i-1]+nCombinedRecoBins[i-1])
                        ratePuUp = histoDict['%s_%s_PuUp'%(proc,box)].Integral(1, numberOfMassBins, RecoBins[i-1], RecoBins[i-1]+nCombinedRecoBins[i-1])
                        ratePuDown = histoDict['%s_%s_PuDown'%(proc,box)].Integral(1, numberOfMassBins, RecoBins[i-1], RecoBins[i-1]+nCombinedRecoBins[i-1])
                        jesErrsUp['%s_%s'%(proc,box)] =  1.0+(rateJESUp-rate)/(rate)
                        jesErrsDown['%s_%s'%(proc,box)] =  1.0+(rateJESDown-rate)/(rate)
                        jerErrsUp['%s_%s'%(proc,box)] =  1.0+(rateJERUp-rate)/(rate)
                        jerErrsDown['%s_%s'%(proc,box)] =  1.0+(rateJERDown-rate)/(rate)
                        puErrs['%s_%s'%(proc,box)] =  1.0+(abs(ratePuUp-rate)+abs(ratePuDown-rate))/(2.*rate)
                    else:
                        jesErrsUp['%s_%s'%(proc,box)] =  1.0
                        jesErrsDown['%s_%s'%(proc,box)] =  1.0
                        jerErrsUp['%s_%s'%(proc,box)] =  1.0
                        jerErrsDown['%s_%s'%(proc,box)] =  1.0
			puErrs['%s_%s'%(proc,box)] =  1.0

                    if RecoBins[i-1]+nCombinedRecoBins[i-1] == 2:
                        scaleptErrs['%s_%s'%(proc,box)] =  0.05
                    elif RecoBins[i-1]+nCombinedRecoBins[i-1] == 3:
                        scaleptErrs['%s_%s'%(proc,box)] =  0.1
                    elif RecoBins[i-1]+nCombinedRecoBins[i-1] == 4:
                        scaleptErrs['%s_%s'%(proc,box)] =  0.2
                    elif RecoBins[i-1]+nCombinedRecoBins[i-1] == 5:
                        scaleptErrs['%s_%s'%(proc,box)] =  0.3
                    elif RecoBins[i-1]+nCombinedRecoBins[i-1] == 6:
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
                            rate = histo.IntegralAndError(1,histo.GetNbinsX(),RecoBins[i-1], RecoBins[i-1]+nCombinedRecoBins[i-1],error)
                            #mcstatErrs['%s_%s'%(proc,box),i,j] = 1.0+histo.GetBinError(j,i)/histo.Integral()
                            mcstatErrs['%s_%s'%(proc,box),i,j] = 1.0+(error[0]/rate)
                        else:
                            mcstatErrs['%s_%s'%(proc,box),i,j] = 1.0		    

	divider = '------------------------------------------------------------\n'
    	datacard = 'imax 2 number of channels\n' + \
       'jmax * number of processes minus 1\n' + \
      'kmax * number of nuisance parameters\n' + \
      divider + \
      'shapes * fail_cat%s base.root w_fail_cat%s:$PROCESS_fail_cat%s w_fail_cat%s:$PROCESS_fail_cat%s_$SYSTEMATIC\n'%(str(i),str(i),str(i),str(i),str(i)) + \
      'shapes qcd fail_cat%s rhalphabase.root w_fail_cat%s:$PROCESS_fail_cat%s\n'%(str(i),str(i),str(i)) +\
      'shapes * pass_cat%s base.root w_pass_cat%s:$PROCESS_pass_cat%s w_pass_cat%s:$PROCESS_pass_cat%s_$SYSTEMATIC\n'%(str(i),str(i),str(i),str(i),str(i)) + \
      'shapes qcd pass_cat%s rhalphabase.root w_pass_cat%s:$PROCESS_pass_cat%s\n'%(str(i),str(i),str(i)) + \
      divider + \
      'bin pass_cat%s fail_cat%s\n'%(str(i),str(i)) + \
      'observation -1.0 -1.0\n' + \
      divider
    	binString = 'bin'
    	processString = 'process'
    	processNumberString = 'process'
    	rateString = 'rate'
    	lumiString = 'lumi\tlnN'
    	hqq125ptString = 'hqq125pt lnN'
	hqq125ptShapeString = 'hqq125ptShape shape'
    	veffString = 'veff\tlnN'
    	bbeffString = 'bbeff\tlnN'
    	znormEWString = 'znormEW\tlnN'
    	znormQString = 'znormQ\tlnN'
    	wznormEWString = 'wznormEW lnN'
    	elevetoString = 'eleveto\tlnN'
    	muvetoString = 'muveto\tlnN'
    	triggerString = 'trigger\tlnN'
    	jesString = 'JES\tlnN'
    	jerString = 'JER\tlnN'
    	puString = 'Pu\tlnN'
    	scaleString = 'scale shape'
    	smearString = 'smear\tshape'
    	mcStatErrString = {}
        scaleptString = 'scalept shape'
        mcStatStrings = {}
        mcStatGroupString = 'mcstat group ='
        qcdGroupString = 'qcd group = qcdeff'
        for box in boxes:
            for proc in sigs+bkgs:
                for j in range(1,numberOfMassBins+1):
                    if options.noMcStatShape:
			if 'GenpT' in proc and tfile_signal is not None:
			    k = int(proc[-1])
			    proc2 = proc[:-7]
                            mcStatStrings['%s_GenpT%s_%s'%(proc2,str(k),box),i,j] = '%sGenpT%s%scat%imcstat%i lnN'%(proc2,str(k),box,i,j)
			else:
			    mcStatStrings['%s_%s'%(proc,box),i,j] = '%s%scat%imcstat%i lnN'%(proc,box,i,j)
                    else:
			if 'GenpT' in proc and tfile_signal is not None:
			    k = int(proc[-1])
                            proc2 = proc[:-7]
                            mcStatStrings['%s_GenpT%s_%s'%(proc2,str(k),box),i,j] = '%sGenpT%s%scat%imcstat%i shape'%(proc2,str(k),box,i,j)
			else:
			    mcStatStrings['%s_%s'%(proc,box),i,j] = '%s%scat%imcstat%i shape'%(proc,box,i,j)

        for box in boxes:
	    h = -1
            for proc in sigs+bkgs:
		h += 1
                if proc=='qcd':
                    jesString += ' -'
                    jerString += ' -'
                    puString += ' -'
                    binString += ' %s_cat%s'%(box,str(i))
                    processString += ' %s'%(proc)
                    processNumberString += ' %i'%(h-nSig+1)
                    rateString += ' 1.0'
		    lumiString += ' -'
		    hqq125ptString += ' -'
		    hqq125ptShapeString += ' -'
		    znormQString += ' -'
		    znormEWString += ' -'
		    wznormEWString += ' -'
		    elevetoString += ' -'
		    muvetoString += ' -'
		    triggerString += ' -'
		    scaleString += ' -'
		    smearString += ' -'
                else:
		    if 'GenpT' in proc and tfile_signal is not None:
			k = int(proc[-1])
                        proc2 = proc[:-7]
			if rates['%s_GenpT%s_%s'%(proc2,str(k),box)] <= 0.0: continue
			binString += ' %s_cat%s'%(box,str(i))
	                processString += ' %s_GenpT%s'%(proc2,str(k))
        	        processNumberString += ' %i'%(h-nSig+1)
		        rateString += ' -1'
                        lumiString += ' 1.025'
			if proc2 == 'hqq125':
			    hqq125ptString += ' 1.30'
			    hqq125ptShapeString += ' 1'
			else:
			    hqq125ptString += ' -'
			    hqq125ptShapeString += ' -'
			znormQString += ' -'
			wznormEWString += ' -'
			znormEWString += ' -'
                        elevetoString += ' 1.005'
                        muvetoString += ' 1.005'
                        triggerString += ' 1.02'
			scaleString += ' 0.1'
			smearString += ' 0.5'
                    	jesString += ' %.3f/%.3f'%(jesErrsDown['%s_GenpT%s_%s'%(proc2,str(k),box)],jesErrsUp['%s_GenpT%s_%s'%(proc2,str(k),box)])
			if jerErrsUp['%s_GenpT%s_%s'%(proc2,str(k),box)]==0:
                    	    jerString += ' %.3f/%.3f'%(jerErrsDown['%s_GenpT%s_%s'%(proc2,str(k),box)],0.001)
			else:
                            jerString += ' %.3f/%.3f'%(jerErrsDown['%s_GenpT%s_%s'%(proc2,str(k),box)],jerErrsUp['%s_GenpT%s_%s'%(proc2,str(k),box)])
                    	puString += ' %.3f'%puErrs['%s_GenpT%s_%s'%(proc2,str(k),box)]
		    else:
                        if rates['%s_%s'%(proc,box)] <= 0.0: continue
                        binString += ' %s_cat%s'%(box,str(i))
                        processString += ' %s'%(proc)
                        processNumberString += ' %i'%(h-nSig+1)
                        rateString += ' -1'
                        if proc == 'tqq':
                            lumiString += ' -'
                        else:
                            lumiString += ' 1.025'
                        if proc == 'hqq125':
                            hqq125ptString += ' 1.30'
                            hqq125ptShapeString += ' 1'
                        else:
                            hqq125ptString += ' -'
                            hqq125ptShapeString += ' -'
			if proc == 'zqq' or proc == 'wqq':
			    znormQString += ' 1.1'
			    if RecoBins[i-1]+nCombinedRecoBins[i-1] == 1 or RecoBins[i-1]+nCombinedRecoBins[i-1] ==2:
				znormEWString += ' 1.15'
			    elif RecoBins[i-1]+nCombinedRecoBins[i-1] ==3:
                                znormEWString += ' 1.25'
			    elif RecoBins[i-1]+nCombinedRecoBins[i-1]==4 or RecoBins[i-1]+nCombinedRecoBins[i-1]==5 or RecoBins[i-1]+nCombinedRecoBins[i-1]==6:
                                znormEWString += ' 1.35'
			else:
			    znormQString += ' -'
			    znormEWString += ' -'
                        if proc == 'wqq':
			    if RecoBins[i-1]+nCombinedRecoBins[i-1]==1 or RecoBins[i-1]+nCombinedRecoBins[i-1]==2 or RecoBins[i-1]+nCombinedRecoBins[i-1]==3:
			    	wznormEWString += ' 1.05'
			    elif RecoBins[i-1]+nCombinedRecoBins[i-1]==4 or RecoBins[i-1]+nCombinedRecoBins[i-1]==5 or RecoBins[i-1]+nCombinedRecoBins[i-1]==6:
                                wznormEWString += ' 1.15'
			else:
			    wznormEWString += ' -'
                        elevetoString += ' 1.005'
                        muvetoString += ' 1.005'
                        triggerString += ' 1.02'
			if proc == 'tqq':
			    scaleString += ' -'
			    smearString += ' -'
			else:
			    scaleString += ' 0.1'
			    smearString += ' 0.5'
                    	jesString += ' %.3f/%.3f'%(jesErrsDown['%s_%s'%(proc,box)],jesErrsUp['%s_%s'%(proc,box)])
                    	jerString += ' %.3f/%.3f'%(jerErrsDown['%s_%s'%(proc,box)],jerErrsUp['%s_%s'%(proc,box)])
                    	puString += ' %.3f'%puErrs['%s_%s'%(proc,box)]
                        
                if proc in ['qcd','tqq']:
                    if i > 1:
                        scaleptString += ' -'
                else:
                    if i > 1:
			if 'GenpT' in proc and tfile_signal is not None:
			    k = int(proc[-1])
                            proc2 = proc[:-7]
			    if rates['%s_GenpT%s_%s'%(proc2,str(k),box)] <= 0.0: continue
                            scaleptString += ' %.3f'%scaleptErrs['%s_GenpT%s_%s'%(proc2,str(k),box)]
			else:
			    if rates['%s_%s'%(proc,box)] <= 0.0: continue
			    scaleptString += ' %.3f'%scaleptErrs['%s_%s'%(proc,box)]
                if proc in ['qcd','tqq','wqq']:
                    bbeffString += ' -'
                else:
		    if 'GenpT' in proc and tfile_signal is not None:
			k = int(proc[-1])
                        proc2 = proc[:-7]
			if rates['%s_GenpT%s_%s'%(proc2,str(k),box)] <= 0.0: continue
			bbeffString += ' %.3f'%bbErrs['%s_GenpT%s_%s'%(proc2,str(k),box)]
		    else:
			if rates['%s_%s'%(proc,box)] <= 0.0: continue
			bbeffString += ' %.3f'%bbErrs['%s_%s'%(proc,box)]
                if proc in ['qcd','tqq']:
                    veffString += ' -'
                else:
		    if 'GenpT' in proc and tfile_signal is not None:
			k = int(proc[-1])
                        proc2 = proc[:-7]
			if rates['%s_%s'%(proc,box)] <= 0.0: continue
                    	veffString += ' %.3f'%vErrs['%s_GenpT%s_%s'%(proc2,str(k),box)]
		    else:
			if rates['%s_%s'%(proc,box)] <= 0.0: continue
			veffString += ' %.3f'%vErrs['%s_%s'%(proc,box)]
                for j in range(1,numberOfMassBins+1):
                    for box1 in boxes:                    
                        for proc1 in sigs+bkgs:                            
                            if proc1==proc and box1==box:
				if 'GenpT' in proc and tfile_signal is not None:
				    k = int(proc1[-1])
                            	    proc2 = proc1[:-7]
				    if rates['%s_GenpT%s_%s'%(proc2,str(k),box)] <= 0.0: continue
                                    mcStatStrings['%s_GenpT%s_%s'%(proc2,str(k),box1),i,j] += '\t%.3f'% mcstatErrs['%s_%s'%(proc1,box),i,j,k]
                            	else:
				    if rates['%s_%s'%(proc,box)] <= 0.0: continue
                                    mcStatStrings['%s_%s'%(proc1,box1),i,j] += '\t%.3f'% mcstatErrs['%s_%s'%(proc,box),i,j]
			    else:
				if rates['%s_%s'%(proc,box)] <= 0.0: continue
				mcStatStrings['%s_%s'%(proc1,box1),i,j] += '\t-'

        tag = "cat"+str(i)
        dctmp = open(options.odir+"/card_rhalphabet_%s.txt" % tag, 'w')


	binString+='\n'; processString+='\n'; processNumberString+='\n'; rateString +='\n'; lumiString+='\n'; hqq125ptString+='\n';
    	veffString+='\n'; bbeffString+='\n'; znormEWString+='\n'; znormQString+='\n'; wznormEWString+='\n'; triggerString+='\n'; elevetoString+='\n'; muvetoString+='\n';
    	jesString+='\n'; jerString+='\n'; puString+='\n'; scaleptString+='\n'; hqq125ptShapeString+='\n'; scaleString+='\n'; smearString+='\n';

    	datacard+=binString+processString+processNumberString+rateString+divider

	if i == 1:
    	    datacard+=lumiString+hqq125ptString+hqq125ptShapeString+veffString+bbeffString+znormQString+znormEWString+wznormEWString+jerString+jesString+puString+triggerString+muvetoString+elevetoString+scaleString+smearString
	else:
            datacard+=lumiString+hqq125ptString+hqq125ptShapeString+veffString+bbeffString+znormQString+znormEWString+wznormEWString+jerString+jesString+puString+triggerString+muvetoString+elevetoString+scaleString+scaleptString+smearString

	tqqeff = histoDict['tqq_pass'].Integral()/(histoDict['tqq_pass'].Integral() + histoDict['tqq_fail'].Integral())

	datacard+='tqqpasscat%snorm rateParam pass_cat%s tqq (@0*@1) tqqnormSF,tqqeffSF\n'%(str(i),str(i)) + \
        'tqqfailcat%snorm rateParam fail_cat%s tqq (@0*(1.0-@1*%.4f)/(1.0-%.4f)) tqqnormSF,tqqeffSF\n'%(str(i),str(i),tqqeff,tqqeff) + \
        'tqqnormSF extArg 1.0 [0.0,10.0]\n' + \
        'tqqeffSF extArg 1.0 [0.0,10.0]\n' + \
	'r1p0 flatParam\n' + \
	'r2p0 flatParam\n' + \
	'r0p1 flatParam\n' + \
	'r1p1 flatParam\n' + \
	'r2p1 flatParam\n' + \
	'qcdeff flatParam\n'



    	dctmp.write(datacard)

        for box in boxes:
            for proc in sigs+bkgs:
                if options.noMcStatShape and proc!='qcd':
		    if 'GenpT' in proc and tfile_signal is not None:
			k = int(proc[-1])
                        proc2 = proc[:-7]
                        if rates['%s_GenpT%s_%s'%(proc2,str(k),box)] <= 0.0: continue
                    	print 'include %sGenpT%s%scat%imcstat'%(proc2,str(k),box,i)
                    	dctmp.write(mcStatStrings['%s_GenpT%s_%s'%(proc2,str(k),box),i,1].replace('mcstat1','mcstat') + "\n")
                    	mcStatGroupString += ' %sGenpT%s%scat%imcstat'%(proc2,str(k),box,i)
		    else:
                        if rates['%s_%s'%(proc,box)] <= 0.0: continue
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
		    elif (tfile_signal is not None) and 'GenpT' in proc:
			histo = histoDictSignal['%s_%s%s'%(proc,box,matchString)]
                    else:
                        histo = histoDict['%s_%s%s'%(proc,box,matchString)]
		    if (tfile_signal is not None) and 'GenpT' in proc:
			k = int(proc[-1])
                        proc2 = proc[:-7]
			if abs(histo.GetBinContent(j,i,k)) > 0. and histo.GetBinError(j,i,k) > 0.5*histo.GetBinContent(j,i,k):
	                    massVal = histo.GetXaxis().GetBinCenter(j)
        	            ptVal = histo.GetYaxis().GetBinLowEdge(i) + 0.3*(histo.GetYaxis().GetBinWidth(i))
	                    rhoVal = r.TMath.Log(massVal*massVal/ptVal/ptVal)
	                    if not( options.blind and massVal > BLIND_LO and massVal < BLIND_HI) and not (rhoVal < RHO_LO or rhoVal > RHO_HI):
	                        if rates['%s_GenpT%s_%s'%(proc2,str(k),box)] <= 0.0: continue
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
	                        if rates['%s_%s'%(proc,box)] <= 0.0: continue
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
    parser.add_option('--nRecoBins', dest='nRecoBins', default=6, type='int', help='number of Reco pT bins')

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
