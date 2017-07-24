import ROOT as rt
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array
import os

from buildRhalphabetPhibb import MASS_BINS,MASS_LO,MASS_HI,BLIND_LO,BLIND_HI
from rhalphabet_builder_Phibb import BB_SF,BB_SF_ERR,V_SF,V_SF_ERR,GetSF

def writeDataCardPhibb(boxes,txtfileName,sigs,bkgs,histoDict,options):
    obsRate = {}
    dbtagcut = options.dbtagcut
    print "Anter : ", dbtagcut
    for box in boxes:
        obsRate[box] = histoDict['data_obs_p%s_%s'%(dbtagcut,box)].Integral()
    nBkgd = len(bkgs)
    nSig = len(sigs)
    rootFileName = txtfileName.replace('.txt','.root')

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
    jesErrs = {}
    jerErrs = {}
    puErrs = {}
    for proc in sigs+bkgs:
        for box in boxes:
            print proc, box
            error = array.array('d',[0.0])
            rate = histoDict['%s_p%s_%s'%(proc,dbtagcut,box)].IntegralAndError(1,histoDict['%s_p%s_%s'%(proc,dbtagcut,box)].GetNbinsX(),error)
            rates['%s_p%s_%s'%(proc,dbtagcut,box)]  = rate
            lumiErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1.025
            if proc=='hqq125':
                hqq125ptErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1.3                
            else:
                hqq125ptErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1.0
            if proc=='wqq' or proc=='zqq' or 'hqq' in proc:
                veffErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1.0+V_SF_ERR/V_SF
                if box=='pass':
                    bbeffErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1.0+BB_SF_ERR/BB_SF
                else:
                    ratePass = histoDict['%s_p%s_%s'%(proc,dbtagcut,'pass')].Integral()
                    rateFail = histoDict['%s_p%s_%s'%(proc,dbtagcut,'fail')].Integral()
                    if rateFail>0:
                        bbeffErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1.0-BB_SF_ERR*(ratePass/rateFail)
                    else:
                        bbeffErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1.0
                    
            else:
                veffErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1.
                bbeffErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1.
            mutriggerErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1
            muidErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1
            muisoErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1
            #jesErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1
            #jerErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1
            if proc=='wqq':
                wznormEWErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1.05
            else:
                wznormEWErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1.
            if proc=='zqq' or proc=='wqq':
                znormQErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1.1
                znormEWErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1.15
            else:
                znormQErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1.
                znormEWErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1.
                
            if rate>0:
                mcStatErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1.0+(error[0]/rate)
            else:
                mcStatErrs['%s_p%s_%s'%(proc,dbtagcut,box)] = 1.0
                
            if rate>0:
                rateJESUp = histoDict['%s_p%s_%s_JESUp'%(proc,dbtagcut,box)].Integral()
                rateJESDown = histoDict['%s_p%s_%s_JESDown'%(proc,dbtagcut,box)].Integral()
                rateJERUp = histoDict['%s_p%s_%s_JERUp'%(proc,dbtagcut,box)].Integral()
                rateJERDown = histoDict['%s_p%s_%s_JERDown'%(proc,dbtagcut,box)].Integral()
                ratePuUp = histoDict['%s_p%s_%s_PuUp'%(proc,dbtagcut,box)].Integral()
                ratePuDown = histoDict['%s_p%s_%s_PuDown'%(proc,dbtagcut,box)].Integral()
                jesErrs['%s_p%s_%s'%(proc,dbtagcut,box)] =  1.0+(abs(rateJESUp-rate)+abs(rateJESDown-rate))/(2.*rate)   
                jerErrs['%s_p%s_%s'%(proc,dbtagcut,box)] =  1.0+(abs(rateJERUp-rate)+abs(rateJERDown-rate))/(2.*rate)
                puErrs['%s_p%s_%s'%(proc,dbtagcut,box)] =  1.0+(abs(ratePuUp-rate)+abs(ratePuDown-rate))/(2.*rate)
            else:
                jesErrs['%s_p%s_%s'%(proc,dbtagcut,box)] =  1.0
                jerErrs['%s_p%s_%s'%(proc,dbtagcut,box)] =  1.0
                puErrs['%s_p%s_%s'%(proc,dbtagcut,box)] =  1.0

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
            mcStatErrString['%s_p%s_%s'%(proc,dbtagcut,box)] = '%sp%s%smuonCRmcstat\tlnN'%(proc,dbtagcut,box)

    for box in boxes:
        i = -1
        for proc in sigs+bkgs:
            i+=1
            if rates['%s_p%s_%s'%(proc,dbtagcut,box)] <= 0.0: continue
            binString +='\t%s_muonCR'%box
            processString += '\t%s'%(proc)
            processNumberString += '\t%i'%(i-nSig+1)
            rateString += '\t%.3f' %rates['%s_p%s_%s'%(proc,dbtagcut,box)]
            lumiString += '\t%.3f'%lumiErrs['%s_p%s_%s'%(proc,dbtagcut,box)]
            hqq125ptString += '\t%.3f'%hqq125ptErrs['%s_p%s_%s'%(proc,dbtagcut,box)]
            veffString += '\t%.3f'%veffErrs['%s_p%s_%s'%(proc,dbtagcut,box)]
            bbeffString += '\t%.3f'%bbeffErrs['%s_p%s_%s'%(proc,dbtagcut,box)]
            znormEWString += '\t%.3f'%znormEWErrs['%s_p%s_%s'%(proc,dbtagcut,box)]
            znormQString += '\t%.3f'%znormQErrs['%s_p%s_%s'%(proc,dbtagcut,box)]
            wznormEWString += '\t%.3f'%wznormEWErrs['%s_p%s_%s'%(proc,dbtagcut,box)]
            mutriggerString += '\t%.3f'%mutriggerErrs['%s_p%s_%s'%(proc,dbtagcut,box)]
            muidString += '\t%.3f'%muidErrs['%s_p%s_%s'%(proc,dbtagcut,box)]
            muisoString += '\t%.3f'%muisoErrs['%s_p%s_%s'%(proc,dbtagcut,box)]
            jesString += '\t%.3f'%jesErrs['%s_p%s_%s'%(proc,dbtagcut,box)]
            jerString += '\t%.3f'%jerErrs['%s_p%s_%s'%(proc,dbtagcut,box)]
            puString += '\t%.3f'%puErrs['%s_p%s_%s'%(proc,dbtagcut,box)]
            for proc1 in sigs+bkgs:
                for box1 in boxes:
                    if proc1==proc and box1==box:
                        mcStatErrString['%s_p%s_%s'%(proc1,dbtagcut,box1)] += '\t%.3f'% mcStatErrs['%s_p%s_%s'%(proc,dbtagcut,box)]
                    else:                        
                        mcStatErrString['%s_p%s_%s'%(proc1,dbtagcut,box1)] += '\t-'
            
    binString+='\n'; processString+='\n'; processNumberString+='\n'; rateString +='\n'; lumiString+='\n'; hqq125ptString+='\n';
    veffString+='\n'; bbeffString+='\n'; znormEWString+='\n'; znormQString+='\n'; wznormEWString+='\n'; mutriggerString+='\n'; muidString+='\n'; muisoString+='\n'; 
    jesString+='\n'; jerString+='\n'; puString+='\n';     
    for proc in (sigs+bkgs):
        for box in boxes:
            mcStatErrString['%s_p%s_%s'%(proc,dbtagcut,box)] += '\n'
            
    datacard+=binString+processString+processNumberString+rateString+divider

    # now nuisances
    datacard+=lumiString+hqq125ptString+veffString+bbeffString+znormEWString+znormQString+wznormEWString+mutriggerString+muidString+muisoString+jesString+jerString+puString

    for proc in (sigs+bkgs):
        for box in boxes:
            if rates['%s_p%s_%s'%(proc,dbtagcut,box)] <= 0.0: continue
            datacard+=mcStatErrString['%s_p%s_%s'%(proc,dbtagcut,box)]

    # now top rate params
    tqqeff = histoDict['tqq_p' + str(dbtagcut) + '_pass'].Integral()/(histoDict['tqq_p' + str(dbtagcut) + '_pass'].Integral()+histoDict['tqq_p' + str(dbtagcut) + '_fail'].Integral())

    
    datacard+='tqqpassmuonCRnorm rateParam pass_muonCR tqq (@0*@1) tqqnormSF,tqqeffSF\n' + \
        'tqqfailmuonCRnorm rateParam fail_muonCR tqq (@0*(1.0-@1*%.4f)/(1.0-%.4f)) tqqnormSF,tqqeffSF\n'%(tqqeff,tqqeff) + \
        'tqqnormSF extArg 1.0 [0.0,10.0]\n' + \
        'tqqeffSF extArg 1.0 [0.0,10.0]\n'

    txtfile = open(options.odir+'/'+txtfileName,'w')
    txtfile.write(datacard)
    txtfile.close()

    
def main(options, args):
    for model in ["DMSbb"]: # [PS, Zp]
        for mass in [50, 100, 125, 200, 300, 350, 400, 500]:
            boxes = ['pass', 'fail']
            #for Hbb extraction:
            sigs = ["{}{}".format(model, mass)]
            bkgs = ['zqq','wqq','qcd','tqq','hqq125','tthqq125', 'vbfhqq125', 'whqq125', 'zhqq125','vvqq','stqq','wlnu','zll']
            #for Wqq/Zbb extraction:
            #sigs = ['zqq','wqq']
            #bkgs = ['tthqq125','whqq125','hqq125','zhqq125','vbfhqq125','qcd','tqq','vvqq','stqq','wlnu','zll']
            #for just Zbb extraction:
            #sigs = ['zqq']
            #bkgs = ['tthqq125','whqq125','hqq125','zhqq125','vbfhqq125','qcd','tqq','wqq','vvqq','stqq','wlnu','zll']
            systs = ['JER','JES','mutrigger','muid','muiso','Pu']

            
            #tfile = rt.TFile.Open(options.idir+'/hist_1DZbb_muonCR.root','read')
            tfile = rt.TFile.Open(options.idir+'/hist_1DZbb_muonCR_AK8_test.root','read')
            
            histoDict = {}
            datahistDict = {}
            dbtagcut = options.dbtagcut
            for proc in (bkgs+sigs+['data_obs']):
                for box in boxes:
                    print "Anter : ", dbtagcut
                    print 'getting histogram for process: %s_p%s_%s'%(proc,dbtagcut,box)
                    histoDict['%s_p%s_%s'%(proc,dbtagcut,box)] = tfile.Get('%s_p%s_%s'%(proc,dbtagcut,box)).Clone()
                    histoDict['%s_p%s_%s'%(proc,dbtagcut,box)].Scale(GetSF(proc,dbtagcut,box,tfile))
                    for syst in systs:
                        if proc!='data_obs':
                            print 'getting histogram for process: %s_p%s_%s_%sUp'%(proc,dbtagcut,box,syst)
                            histoDict['%s_p%s_%s_%sUp'%(proc,dbtagcut,box,syst)] = tfile.Get('%s_p%s_%s_%sUp'%(proc,dbtagcut,box,syst)).Clone()
                            histoDict['%s_p%s_%s_%sUp'%(proc,dbtagcut,box,syst)].Scale(GetSF(proc,dbtagcut,box,tfile))
                            print 'getting histogram for process: %s_p%s_%s_%sDown'%(proc,dbtagcut,box,syst)
                            histoDict['%s_p%s_%s_%sDown'%(proc,dbtagcut,box,syst)] = tfile.Get('%s_p%s_%s_%sDown'%(proc,dbtagcut,box,syst)).Clone()
                            histoDict['%s_p%s_%s_%sDown'%(proc,dbtagcut,box,syst)].Scale(GetSF(proc,dbtagcut,box,tfile))
                            
                        
            
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
            w.Write()
            outputFile.Close()
            txtfileName = outFile.replace('.root','.txt')

            writeDataCardPhibb(boxes,txtfileName,sigs,bkgs,histoDict,options)
            print '\ndatacard:\n'
            os.system('cat %s/%s'%(options.odir,txtfileName))



if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('--lumi', dest='lumi', type=float, default = 20,help='lumi in 1/fb ', metavar='lumi')
    parser.add_option('-i','--idir', dest='idir', default = './',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = './',help='directory to write cards', metavar='odir')
    parser.add_option('-d','--dbtagcut', dest='dbtagcut', default = 7, type='int', help=' dbtag value cut')
    
    (options, args) = parser.parse_args()

    main(options, args)
