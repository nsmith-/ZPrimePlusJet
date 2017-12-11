import ROOT as rt
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array
import os
sys.path.insert(0, '../.')
import tools as tools

from buildRhalphabetHbb import MASS_BINS,MASS_LO,MASS_HI,BLIND_LO,BLIND_HI,RHO_LO,RHO_HI
from rhalphabet_builder import BB_SF,BB_SF_ERR,V_SF,V_SF_ERR,GetSF

def writeDataCard(boxes,txtfileName,sigs,bkgs,histoDict,histoDictSignal,tfile_signal,options):
    obsRate = {}
    for box in boxes:
        obsRate[box] = histoDict['data_obs_%s'%box].Integral()
    nBkgd = len(bkgs)
    nSig = len(sigs)
    rootFileName = txtfileName.replace('.txt','.root')
    numberOfGenPtBins = 4

    rates = {}
    lumiErrs = {}
    hqq125ptErrs = {}
    mcStatErrs = {}
    veffErrs = {}
    bbeffErrs = {}
    znormEWErrs = {}
    znormQErrs = {}
    wznormEWErrs = {}
    mutriggerErrs = {}
    muidErrs = {}
    muisoErrs = {}
    jesErrsUp = {}
    jesErrsDown = {}
    jerErrsUp = {}
    jerErrsDown = {}
    puErrs = {}
    for proc in sigs+bkgs:
        for box in boxes:
	    if tfile_signal is None:
            	print proc, box
            	error = array.array('d',[0.0])
            	rate = histoDict['%s_%s'%(proc,box)].IntegralAndError(1,histoDict['%s_%s'%(proc,box)].GetNbinsX(),error)
            	rates['%s_%s'%(proc,box)]  = rate
            	lumiErrs['%s_%s'%(proc,box)] = 1.025
            	if proc=='hqq125':
                    hqq125ptErrs['%s_%s'%(proc,box)] = 1.3                
            	else:
                    hqq125ptErrs['%s_%s'%(proc,box)] = 1.0
            	if proc=='wqq' or proc=='zqq' or 'hqq' in proc:
                    veffErrs['%s_%s'%(proc,box)] = 1.0+V_SF_ERR/V_SF
                    if box=='pass':
                    	bbeffErrs['%s_%s'%(proc,box)] = 1.0+BB_SF_ERR/BB_SF
                    else:
                    	ratePass = histoDict['%s_%s'%(proc,'pass')].Integral()
                    	rateFail = histoDict['%s_%s'%(proc,'fail')].Integral()
                    	if rateFail>0:
                            bbeffErrs['%s_%s'%(proc,box)] = 1.0-BB_SF_ERR*(ratePass/rateFail)
                    	else:
                            bbeffErrs['%s_%s'%(proc,box)] = 1.0
                    
            	else:
                    veffErrs['%s_%s'%(proc,box)] = 1.
                    bbeffErrs['%s_%s'%(proc,box)] = 1.
            	mutriggerErrs['%s_%s'%(proc,box)] = 1
            	muidErrs['%s_%s'%(proc,box)] = 1
            	muisoErrs['%s_%s'%(proc,box)] = 1
            	#jesErrs['%s_%s'%(proc,box)] = 1
            	#jerErrs['%s_%s'%(proc,box)] = 1
            	if proc=='wqq':
                    wznormEWErrs['%s_%s'%(proc,box)] = 1.05
            	else:
                    wznormEWErrs['%s_%s'%(proc,box)] = 1.
            	if proc=='zqq' or proc=='wqq':
                    znormQErrs['%s_%s'%(proc,box)] = 1.1
                    znormEWErrs['%s_%s'%(proc,box)] = 1.15
            	else:
                    znormQErrs['%s_%s'%(proc,box)] = 1.
                    znormEWErrs['%s_%s'%(proc,box)] = 1.
                
            	if rate>0:
                    mcStatErrs['%s_%s'%(proc,box)] = 1.0+(error[0]/rate)
            	else:
                    mcStatErrs['%s_%s'%(proc,box)] = 1.0
                
            	if rate>0:
                    rateJESUp = histoDict['%s_%s_JESUp'%(proc,box)].Integral()
                    rateJESDown = histoDict['%s_%s_JESDown'%(proc,box)].Integral()
                    rateJERUp = histoDict['%s_%s_JERUp'%(proc,box)].Integral()
                    rateJERDown = histoDict['%s_%s_JERDown'%(proc,box)].Integral()
                    ratePuUp = histoDict['%s_%s_PuUp'%(proc,box)].Integral()
                    ratePuDown = histoDict['%s_%s_PuDown'%(proc,box)].Integral()
                    jesErrsUp['%s_%s'%(proc,box)] =  1.0+(rateJESUp-rate)/(rate)
                    jesErrsDown['%s_%s'%(proc,box)] =  1.0+(rateJESDown-rate)/(rate)
                    jerErrsUp['%s_%s'%(proc,box)] =  1.0+(rateJERUp-rate)/(rate)
                    jerErrsDown['%s_%s'%(proc,box)] =  1.0+(rateJERDown-rate)/(rate)
#                    jesErrs['%s_%s'%(proc,box)] =  1.0+(abs(rateJESUp-rate)+abs(rateJESDown-rate))/(2.*rate)   
#                    jerErrs['%s_%s'%(proc,box)] =  1.0+(abs(rateJERUp-rate)+abs(rateJERDown-rate))/(2.*rate)
                    puErrs['%s_%s'%(proc,box)] =  1.0+(abs(ratePuUp-rate)+abs(ratePuDown-rate))/(2.*rate)
            	else:
                    jesErrsUp['%s_%s'%(proc,box)] =  1.0
                    jesErrsDown['%s_%s'%(proc,box)] =  1.0
                    jerErrsUp['%s_%s'%(proc,box)] =  1.0
                    jerErrsDown['%s_%s'%(proc,box)] =  1.0
#                    jesErrs['%s_%s'%(proc,box)] =  1.0
#                    jerErrs['%s_%s'%(proc,box)] =  1.0
                    puErrs['%s_%s'%(proc,box)] =  1.0

            else:
		if proc != 'hqq125':
                    print proc, box
                    error = array.array('d',[0.0])
                    rate = histoDict['%s_%s'%(proc,box)].IntegralAndError(1,histoDict['%s_%s'%(proc,box)].GetNbinsX(),error)
                    rates['%s_%s'%(proc,box)]  = rate
                    lumiErrs['%s_%s'%(proc,box)] = 1.025
                    if proc=='hqq125':
                        hqq125ptErrs['%s_%s'%(proc,box)] = 1.3
                    else:
                        hqq125ptErrs['%s_%s'%(proc,box)] = 1.0
                    if proc=='wqq' or proc=='zqq' or 'hqq' in proc:
                        veffErrs['%s_%s'%(proc,box)] = 1.0+V_SF_ERR/V_SF
                        if box=='pass':
                            bbeffErrs['%s_%s'%(proc,box)] = 1.0+BB_SF_ERR/BB_SF
                        else:
                            ratePass = histoDict['%s_%s'%(proc,'pass')].Integral()
                            rateFail = histoDict['%s_%s'%(proc,'fail')].Integral()
                            if rateFail>0:
                                bbeffErrs['%s_%s'%(proc,box)] = 1.0-BB_SF_ERR*(ratePass/rateFail)
                            else:
                                bbeffErrs['%s_%s'%(proc,box)] = 1.0

                    else:
                        veffErrs['%s_%s'%(proc,box)] = 1.
                        bbeffErrs['%s_%s'%(proc,box)] = 1.
                    mutriggerErrs['%s_%s'%(proc,box)] = 1
                    muidErrs['%s_%s'%(proc,box)] = 1
                    muisoErrs['%s_%s'%(proc,box)] = 1
                    #jesErrs['%s_%s'%(proc,box)] = 1
                    #jerErrs['%s_%s'%(proc,box)] = 1
                    if proc=='wqq':
                    	wznormEWErrs['%s_%s'%(proc,box)] = 1.05
                    else:
                    	wznormEWErrs['%s_%s'%(proc,box)] = 1.
                    if proc=='zqq' or proc=='wqq':
                    	znormQErrs['%s_%s'%(proc,box)] = 1.1
                    	znormEWErrs['%s_%s'%(proc,box)] = 1.15
                    else:
                    	znormQErrs['%s_%s'%(proc,box)] = 1.
                    	znormEWErrs['%s_%s'%(proc,box)] = 1.
                    if rate>0:
                    	print "testing1"
                    	print proc, box
                    	mcStatErrs['%s_%s'%(proc,box)] = 1.0+(error[0]/rate)
                    else:
                        print "testing2"
                        print proc, box
                    	mcStatErrs['%s_%s'%(proc,box)] = 1.0

                    if rate>0:
                    	rateJESUp = histoDict['%s_%s_JESUp'%(proc,box)].Integral()
                    	rateJESDown = histoDict['%s_%s_JESDown'%(proc,box)].Integral()
                    	rateJERUp = histoDict['%s_%s_JERUp'%(proc,box)].Integral()
                    	rateJERDown = histoDict['%s_%s_JERDown'%(proc,box)].Integral()
                    	ratePuUp = histoDict['%s_%s_PuUp'%(proc,box)].Integral()
                    	ratePuDown = histoDict['%s_%s_PuDown'%(proc,box)].Integral()
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
                else:
		    for k in range(1, numberOfGenPtBins + 1):
		    	print proc, box
                    	error = array.array('d',[0.0])
                    	rate = histoDictSignal['%s_GenpT%s_%s'%(proc,str(k),box)].IntegralAndError(1,histoDictSignal['%s_GenpT%s_%s'%(proc,str(k),box)].GetNbinsX(),error)
                    	rates['%s_GenpT%s_%s'%(proc,str(k),box)]  = rate
                    	lumiErrs['%s_GenpT%s_%s'%(proc,str(k),box)] = 1.025
                	if proc=='hqq125':
                    	    hqq125ptErrs['%s_GenpT%s_%s'%(proc,str(k),box)] = 1.3
                	else:
                    	    hqq125ptErrs['%s_GenpT%s_%s'%(proc,str(k),box)] = 1.0
                	if proc=='wqq' or proc=='zqq' or 'hqq' in proc:
                    	    veffErrs['%s_GenpT%s_%s'%(proc,str(k),box)] = 1.0+V_SF_ERR/V_SF
                    	    if box=='pass':
                        	bbeffErrs['%s_GenpT%s_%s'%(proc,str(k),box)] = 1.0+BB_SF_ERR/BB_SF
                    	    else:
                        	ratePass = histoDictSignal['%s_GenpT%s_%s'%(proc,str(k),'pass')].Integral()
                        	rateFail = histoDictSignal['%s_GenpT%s_%s'%(proc,str(k),'fail')].Integral()
                                if rateFail>0:
                            	    bbeffErrs['%s_GenpT%s_%s'%(proc,str(k),box)] = 1.0-BB_SF_ERR*(ratePass/rateFail)
                                else:
                            	    bbeffErrs['%s_GenpT%s_%s'%(proc,str(k),box)] = 1.0

                	else:
                            veffErrs['%s_GenpT%s_%s'%(proc,str(k),box)] = 1.
                            bbeffErrs['%s_GenpT%s_%s'%(proc,str(k),box)] = 1.
                    	mutriggerErrs['%s_GenpT%s_%s'%(proc,str(k),box)] = 1
                    	muidErrs['%s_GenpT%s_%s'%(proc,str(k),box)] = 1
                    	muisoErrs['%s_GenpT%s_%s'%(proc,str(k),box)] = 1
                    	#jesErrs['%s_%s'%(proc,box)] = 1
                    	#jerErrs['%s_%s'%(proc,box)] = 1
                    	if proc=='wqq':
                            wznormEWErrs['%s_%s'%(proc,box)] = 1.05
                    	else:
                            wznormEWErrs['%s_GenpT%s_%s'%(proc,str(k),box)] = 1.
                    	if proc=='zqq' or proc=='wqq':
                            znormQErrs['%s_%s'%(proc,box)] = 1.1
                            znormEWErrs['%s_%s'%(proc,box)] = 1.15
                    	else:
                            znormQErrs['%s_GenpT%s_%s'%(proc,str(k),box)] = 1.
                            znormEWErrs['%s_GenpT%s_%s'%(proc,str(k),box)] = 1.
                    	if rate>0:
                            mcStatErrs['%s_GenpT%s_%s'%(proc,str(k),box)] = 1.0+(error[0]/rate)
                    	else:
                            mcStatErrs['%s_GenpT%s_%s'%(proc,str(k),box)] = 1.0

                    	if rate>0:
                            rateJESUp = histoDictSignal['%s_GenpT%s_%s_JESUp'%(proc,str(k),box)].Integral()
                            rateJESDown = histoDictSignal['%s_GenpT%s_%s_JESDown'%(proc,str(k),box)].Integral()
                            rateJERUp = histoDictSignal['%s_GenpT%s_%s_JERUp'%(proc,str(k),box)].Integral()
                            rateJERDown = histoDictSignal['%s_GenpT%s_%s_JERDown'%(proc,str(k),box)].Integral()
                            ratePuUp = histoDictSignal['%s_GenpT%s_%s_PuUp'%(proc,str(k),box)].Integral()
                            ratePuDown = histoDictSignal['%s_GenpT%s_%s_PuDown'%(proc,str(k),box)].Integral()
                            jesErrsUp['%s_GenpT%s_%s'%(proc,str(k),box)] =  1.0+(rateJESUp-rate)/(rate)
                            jesErrsDown['%s_GenpT%s_%s'%(proc,str(k),box)] =  1.0+(rateJESDown-rate)/(rate)
                            jerErrsUp['%s_GenpT%s_%s'%(proc,str(k),box)] =  1.0+(rateJERUp-rate)/(rate)
                            jerErrsDown['%s_GenpT%s_%s'%(proc,str(k),box)] =  1.0+(rateJERDown-rate)/(rate)
                            puErrs['%s_GenpT%s_%s'%(proc,str(k),box)] =  1.0+(abs(ratePuUp-rate)+abs(ratePuDown-rate))/(2.*rate)
                    	else:
                            jesErrsUp['%s_GenpT%s_%s'%(proc,str(k),box)] =  1.0
                            jesErrsDown['%s_GenpT%s_%s'%(proc,str(k),box)] =  1.0
                            jerErrsUp['%s_GenpT%s_%s'%(proc,str(k),box)] =  1.0
                            jerErrsDown['%s_GenpT%s_%s'%(proc,str(k),box)] =  1.0
                            puErrs['%s_GenpT%s_%s'%(proc,str(k),box)] =  1.0



 
    divider = '------------------------------------------------------------\n'
    datacard = 'imax 2 number of channels\n' + \
       'jmax * number of processes minus 1\n' + \
      'kmax * number of nuisance parameters\n' + \
      divider + \
      'bin fail_muonCR pass_muonCR\n' + \
      'observation %.3f %.3f\n'%(obsRate['fail'],obsRate['pass']) + \
      divider + \
      'shapes * pass_muonCR %s w_muonCR:$PROCESS_pass w_muonCR:$PROCESS_pass_$SYSTEMATIC\n'%rootFileName + \
      'shapes * fail_muonCR %s w_muonCR:$PROCESS_fail w_muonCR:$PROCESS_fail_$SYSTEMATIC\n'%rootFileName + \
      divider
    binString = 'bin'
    processString = 'process'
    processNumberString = 'process'
    rateString = 'rate'
    lumiString = 'lumi\tlnN'
    hqq125ptString = 'hqq125pt\tlnN'
    veffString = 'veff\tlnN'
    bbeffString = 'bbeff\tlnN'
    znormEWString = 'znormEW\tlnN'
    znormQString = 'znormQ\tlnN'    
    wznormEWString = 'wznormEW\tlnN'
    muidString = 'muid\tshape'   
    muisoString = 'muiso\tshape'   
    mutriggerString = 'mutrigger\tshape'  
    #jesString = 'JES\tshape'    
    #jerString = 'JER\tshape'
    jesString = 'JES\tlnN'
    jerString = 'JER\tlnN'
    puString = 'Pu\tlnN'
    mcStatErrString = {}
    for proc in sigs+bkgs:
        for box in boxes:
	    if tfile_signal is None and 'hqq' in proc:
                mcStatErrString['%s_%s'%(proc,box)] = '%s%smuonCRmcstat\tlnN'%(proc,box)
	    elif tfile_signal is not None and proc == 'hqq125':
		for k in range(1, numberOfGenPtBins + 1):
                    mcStatErrString['%s_GenpT%s_%s'%(proc,str(k),box)] = '%s%smuonCRmcstat\tlnN'%(proc,box)
	    else:
		mcStatErrString['%s_%s'%(proc,box)] = '%s%smuonCRmcstat\tlnN'%(proc,box)

    if tfile_signal is None:
	sigs = ['xhqq125','hqq125']
    else:
	sigs = ['xhqq125','hqq125_GenpT1','hqq125_GenpT2','hqq125_GenpT3','hqq125_GenpT4']

    nSig = len(sigs)

    for box in boxes:
        i = -1
        for proc in sigs+bkgs:
            i+=1
	    if tfile_signal is not None and 'hqq' in proc:
                if rates['%s_%s'%(proc,box)] <= 0.0: continue
                binString +='\t%s_muonCR'%box
                processString += '\t%s'%(proc)
                processNumberString += '\t%i'%(i-nSig+1)
                rateString += '\t%.3f' %rates['%s_%s'%(proc,box)]
                lumiString += '\t%.3f'%lumiErrs['%s_%s'%(proc,box)]
                hqq125ptString += '\t%.3f'%hqq125ptErrs['%s_%s'%(proc,box)]
                veffString += '\t%.3f'%veffErrs['%s_%s'%(proc,box)]
                bbeffString += '\t%.3f'%bbeffErrs['%s_%s'%(proc,box)]
                znormEWString += '\t%.3f'%znormEWErrs['%s_%s'%(proc,box)]
                znormQString += '\t%.3f'%znormQErrs['%s_%s'%(proc,box)]
                wznormEWString += '\t%.3f'%wznormEWErrs['%s_%s'%(proc,box)]
                mutriggerString += '\t%.3f'%mutriggerErrs['%s_%s'%(proc,box)]
                muidString += '\t%.3f'%muidErrs['%s_%s'%(proc,box)]
                muisoString += '\t%.3f'%muisoErrs['%s_%s'%(proc,box)]
                jesString += '\t%.3f/%.3f'%(jesErrsDown['%s_%s'%(proc,box)],jesErrsUp['%s_%s'%(proc,box)])
                jerString += '\t%.3f/%.3f'%(jerErrsDown['%s_%s'%(proc,box)],jerErrsUp['%s_%s'%(proc,box)])
                puString += '\t%.3f'%puErrs['%s_%s'%(proc,box)]
                for proc1 in sigs+bkgs:
                    for box1 in boxes:
                        if proc1==proc and box1==box:
                            mcStatErrString['%s_%s'%(proc1,box1)] += '\t%.3f'% mcStatErrs['%s_%s'%(proc,box)]
                        else:
                            mcStatErrString['%s_%s'%(proc1,box1)] += '\t-'
	    else:
            	if rates['%s_%s'%(proc,box)] <= 0.0: continue
            	binString +='\t%s_muonCR'%box
            	processString += '\t%s'%(proc)
            	processNumberString += '\t%i'%(i-nSig+1)
            	rateString += '\t%.3f' %rates['%s_%s'%(proc,box)]
            	lumiString += '\t%.3f'%lumiErrs['%s_%s'%(proc,box)]
            	hqq125ptString += '\t%.3f'%hqq125ptErrs['%s_%s'%(proc,box)]
            	veffString += '\t%.3f'%veffErrs['%s_%s'%(proc,box)]
            	bbeffString += '\t%.3f'%bbeffErrs['%s_%s'%(proc,box)]
            	znormEWString += '\t%.3f'%znormEWErrs['%s_%s'%(proc,box)]
            	znormQString += '\t%.3f'%znormQErrs['%s_%s'%(proc,box)]
            	wznormEWString += '\t%.3f'%wznormEWErrs['%s_%s'%(proc,box)]
            	mutriggerString += '\t%.3f'%mutriggerErrs['%s_%s'%(proc,box)]
            	muidString += '\t%.3f'%muidErrs['%s_%s'%(proc,box)]
            	muisoString += '\t%.3f'%muisoErrs['%s_%s'%(proc,box)]
                jesString += '\t%.3f/%.3f'%(jesErrsDown['%s_%s'%(proc,box)],jesErrsUp['%s_%s'%(proc,box)])
                jerString += '\t%.3f/%.3f'%(jerErrsDown['%s_%s'%(proc,box)],jerErrsUp['%s_%s'%(proc,box)])
            	puString += '\t%.3f'%puErrs['%s_%s'%(proc,box)]
            	for proc1 in sigs+bkgs:
                    for box1 in boxes:
                    	if proc1==proc and box1==box:
                            mcStatErrString['%s_%s'%(proc1,box1)] += '\t%.3f'% mcStatErrs['%s_%s'%(proc,box)]
                    	else:                        
                            mcStatErrString['%s_%s'%(proc1,box1)] += '\t-'
            
    binString+='\n'; processString+='\n'; processNumberString+='\n'; rateString +='\n'; lumiString+='\n'; hqq125ptString+='\n';
    veffString+='\n'; bbeffString+='\n'; znormEWString+='\n'; znormQString+='\n'; wznormEWString+='\n'; mutriggerString+='\n'; muidString+='\n'; muisoString+='\n'; 
    jesString+='\n'; jerString+='\n'; puString+='\n';     
    for proc in (sigs+bkgs):
        for box in boxes:
            mcStatErrString['%s_%s'%(proc,box)] += '\n'
            
    datacard+=binString+processString+processNumberString+rateString+divider

    # now nuisances
    datacard+=lumiString+hqq125ptString+veffString+bbeffString+znormEWString+znormQString+wznormEWString+mutriggerString+muidString+muisoString+jesString+jerString+puString

    for proc in (sigs+bkgs):
        for box in boxes:
            if rates['%s_%s'%(proc,box)] <= 0.0: continue
            datacard+=mcStatErrString['%s_%s'%(proc,box)]

    # now top rate params
    tqqeff = histoDict['tqq_pass'].Integral()/(histoDict['tqq_pass'].Integral()+histoDict['tqq_fail'].Integral())

    
    datacard+='tqqpassmuonCRnorm rateParam pass_muonCR tqq (@0*@1) tqqnormSF,tqqeffSF\n' + \
        'tqqfailmuonCRnorm rateParam fail_muonCR tqq (@0*(1.0-@1*%.4f)/(1.0-%.4f)) tqqnormSF,tqqeffSF\n'%(tqqeff,tqqeff) + \
        'tqqnormSF extArg 1.0 [0.0,10.0]\n' + \
        'tqqeffSF extArg 1.0 [0.0,10.0]\n'

    txtfile = open(options.odir+'/'+txtfileName,'w')
    txtfile.write(datacard)
    txtfile.close()

    
def main(options, args):
    
    boxes = ['pass', 'fail']
    #for Hbb extraction:
    sigs = ['xhqq125','hqq125']
    bkgs = ['zqq','wqq','qcd','tqq','vvqq','stqq','wlnu','zll']
    #for Wqq/Zbb extraction:
    #sigs = ['zqq','wqq']
    #bkgs = ['tthqq125','whqq125','hqq125','zhqq125','vbfhqq125','qcd','tqq','vvqq','stqq','wlnu','zll']
    #for just Zbb extraction:
    #sigs = ['zqq']
    #bkgs = ['tthqq125','whqq125','hqq125','zhqq125','vbfhqq125','qcd','tqq','wqq','vvqq','stqq','wlnu','zll']
    systs = ['JER','JES','mutrigger','muid','muiso','Pu']

    numberOfMassBins = 23
    numberOfGenPtBins = 4
    massLow = 40.
    massHigh = 201.
    
    tfile = rt.TFile.Open(options.idir+'/hist_1DZbb_muonCR.root','read')
    tfile_signal = None
    if options.ifile_signal is not None:
        tfile_signal = rt.TFile.Open(options.ifile_signal)
 
    histoDict = {}
    datahistDict = {}
    histoDictSignal = {}
    
#    for proc in (bkgs):
    for proc in (sigs+bkgs+['data_obs']):
        for box in boxes:
	    if proc != 'hqq125':
            	print 'getting histogram for process: %s_%s'%(proc,box)
            	histoDict['%s_%s'%(proc,box)] = tfile.Get('%s_%s'%(proc,box)).Clone()
            	histoDict['%s_%s'%(proc,box)].Scale(GetSF(proc,box,tfile))
            	for syst in systs:
                    if proc!='data_obs':
                    	print 'getting histogram for process: %s_%s_%sUp'%(proc,box,syst)
                    	histoDict['%s_%s_%sUp'%(proc,box,syst)] = tfile.Get('%s_%s_%sUp'%(proc,box,syst)).Clone()
                    	histoDict['%s_%s_%sUp'%(proc,box,syst)].Scale(GetSF(proc,box,tfile))
                    	print 'getting histogram for process: %s_%s_%sDown'%(proc,box,syst)
                    	histoDict['%s_%s_%sDown'%(proc,box,syst)] = tfile.Get('%s_%s_%sDown'%(proc,box,syst)).Clone()
                    	histoDict['%s_%s_%sDown'%(proc,box,syst)].Scale(GetSF(proc,box,tfile))
	    else:
                histoDictSignal['%s_%s'%(proc,box)] = tfile_signal.Get('%s_%s'%(proc,box)).Clone()
                histoDictSignal['%s_%s'%(proc,box)].Scale(GetSF(proc,box,tfile))
                for syst in systs:
                    histoDictSignal['%s_%s_%sUp'%(proc,box,syst)] = tfile_signal.Get('%s_%s_%sUp'%(proc,box,syst))
                    histoDictSignal['%s_%s_%sUp'%(proc,box,syst)].Scale(GetSF(proc,box,tfile))
                    histoDictSignal['%s_%s_%sDown'%(proc,box,syst)] = tfile_signal.Get('%s_%s_%sDown'%(proc,box,syst))
                    histoDictSignal['%s_%s_%sDown'%(proc,box,syst)].Scale(GetSF(proc,box,tfile))
		

    entries = 0.
    histoDictSignal_1D = {}
    if tfile_signal is not None:
	for proc in sigs:
	    if proc == 'hqq125':
	    	for box in boxes:
		    for k in range(1, numberOfGenPtBins + 1):
		    	name = proc + '_GenpT' + str(k) + '_' + box
		    	histoDictSignal_1D['%s_GenpT%s_%s'%(proc,str(k),box)] = tools.projMuCR(name,str(k),histoDictSignal['%s_%s'%(proc,box)],numberOfMassBins,MASS_LO,MASS_HI)
		    	print "name: ", name
		    	for syst in systs:
			    nameUp = proc + '_GenpT' + str(k) + '_' + box + '_' + syst + 'Up' 
                            nameDown = proc + '_GenpT' + str(k) + '_' + box + '_' + syst + 'Down'
		            histoDictSignal_1D['%s_GenpT%s_%s_%sUp'%(proc,str(k),box,syst)] = tools.projMuCR(nameUp,str(k),histoDictSignal['%s_%s_%sUp'%(proc,box,syst)],numberOfMassBins,MASS_LO,MASS_HI)
                            histoDictSignal_1D['%s_GenpT%s_%s_%sDown'%(proc,str(k),box,syst)] = tools.projMuCR(nameDown,str(k),histoDictSignal['%s_%s_%sDown'%(proc,box,syst)],numberOfMassBins,MASS_LO,MASS_HI)


    
    outFile = 'datacard_muonCR.root'
    
    outputFile = rt.TFile.Open(options.odir+'/'+outFile,'recreate')
    outputFile.cd()
    w = rt.RooWorkspace('w_muonCR')
    #w.factory('y[40,40,201]')
    #w.var('y').setBins(1)
    w.factory('x[%i,%i,%i]'%(MASS_LO,MASS_LO,MASS_HI))
    w.var('x').setBins(MASS_BINS)
    for key, histo in histoDict.iteritems():
        #histo.Rebin(23)
        #ds = rt.RooDataHist(key,key,rt.RooArgList(w.var('y')),histo)
        ds = rt.RooDataHist(key,key,rt.RooArgList(w.var('x')),histo)
        getattr(w,'import')(ds, rt.RooCmdArg())

    if tfile_signal is not None:
        for key, histo in histoDictSignal_1D.iteritems():
            ds = rt.RooDataHist(key,key,rt.RooArgList(w.var('x')),histo)
            getattr(w,'import')(ds, rt.RooCmdArg())


    w.Write()
    outputFile.Close()
    txtfileName = outFile.replace('.root','.txt')

    writeDataCard(boxes,txtfileName,sigs,bkgs,histoDict,histoDictSignal_1D,tfile_signal,options)
    print '\ndatacard:\n'
    os.system('cat %s/%s'%(options.odir,txtfileName))



if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('--lumi', dest='lumi', type=float, default = 20,help='lumi in 1/fb ', metavar='lumi')
    parser.add_option('-i','--idir', dest='idir', default = './',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = './',help='directory to write cards', metavar='odir')
    parser.add_option('--ifile-signal', dest='ifile_signal', default=None, help='second file with 3D histogram inputs for the signal samples',
                      metavar='ifile_signal')
    
    (options, args) = parser.parse_args()

    main(options, args)
