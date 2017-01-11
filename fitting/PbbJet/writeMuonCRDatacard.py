import ROOT as rt
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array
import os

def writeDataCard(boxes,txtfileName,sigs,bkgs,histoDict,options):
    obsRate = {}
    for box in boxes:
        obsRate[box] = histoDict['data_obs_%s'%box].Integral()
    nBkgd = len(bkgs)
    nSig = len(sigs)
    rootFileName = txtfileName.replace('.txt','.root')

    rates = {}
    lumiErrs = {}
    mcStatErrs = {}
    for proc in sigs+bkgs:
        for box in boxes:
            print proc, box
            error = array.array('d',[0.0])
            rate = histoDict['%s_%s'%(proc,box)].IntegralAndError(1,histoDict['%s_%s'%(proc,box)].GetNbinsX(),error)
            rates['%s_%s'%(proc,box)]  = rate
            lumiErrs['%s_%s'%(proc,box)] = 1.05
            if rate>0:
                mcStatErrs['%s_%s'%(proc,box)] = 1.0+(error[0]/rate)
            else:
                mcStatErrs['%s_%s'%(proc,box)] = 1.0

    divider = '------------------------------------------------------------\n'
    datacard = 'imax 2 number of channels\n' + \
      'jmax %i number of processes minus 1\n'%(nBkgd+nSig-1) + \
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
    mcStatErrString = {}
    for proc in sigs+bkgs:
        for box in boxes:
            mcStatErrString['%s_%s'%(proc,box)] = '%s_%s_muonCR_mcstat\tlnN'%(proc,box)

    for box in boxes:
        i = -1
        for proc in sigs+bkgs:
            i+=1
            if rates['%s_%s'%(proc,box)] <= 0.0: continue
            binString +='\t%s_muonCR'%box
            processString += '\t%s'%(proc)
            processNumberString += '\t%i'%(i-nSig+1)
            rateString += '\t%.3f' %rates['%s_%s'%(proc,box)]
            lumiString += '\t%.3f'%lumiErrs['%s_%s'%(proc,box)]
            for proc1 in sigs+bkgs:
                for box1 in boxes:
                    if proc1==proc and box1==box:
                        mcStatErrString['%s_%s'%(proc1,box1)] += '\t%.3f'% mcStatErrs['%s_%s'%(proc,box)]
                    else:                        
                        mcStatErrString['%s_%s'%(proc1,box1)] += '\t-'
            
    binString+='\n'; processString+='\n'; processNumberString+='\n'; rateString +='\n'; lumiString+='\n';
    for proc in (sigs+bkgs):
        for box in boxes:
            mcStatErrString['%s_%s'%(proc,box)] += '\n'
            
    datacard+=binString+processString+processNumberString+rateString+divider

    # now nuisances
    datacard+=lumiString

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
    sigs = ['tthqq125','hqq125','whqq125','zhqq125','vbfhqq125']
    bkgs = ['zqq','wqq','qcd','tqq','vvqq','stqq']

    
    tfile = rt.TFile.Open(options.idir+'/hist_1DZbb_muonCR.root','read')
    
    histoDict = {}
    datahistDict = {}
    
    for proc in (bkgs+sigs+['data_obs']):
        for box in boxes:
            print 'getting histogram for process: %s_%s'%(proc,box)
            histoDict['%s_%s'%(proc,box)] = tfile.Get('%s_%s'%(proc,box))
    
    outFile = 'datacard_muonCR.root'
    
    outputFile = rt.TFile.Open(options.odir+'/'+outFile,'recreate')
    outputFile.cd()
    w = rt.RooWorkspace('w_muonCR')
    w.factory('x[40,40,201]')
    w.var('x').setBins(23)
    for key, histo in histoDict.iteritems():
        ds = rt.RooDataHist(key,key,rt.RooArgList(w.var('x')),histo)
        getattr(w,'import')(ds)
    w.Write()
    outputFile.Close()
    txtfileName = outFile.replace('.root','.txt')

    writeDataCard(boxes,txtfileName,sigs,bkgs,histoDict,options)
    print '\ndatacard:\n'
    os.system('cat %s/%s'%(options.odir,txtfileName))



if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('--lumi', dest='lumi', type=float, default = 20,help='lumi in 1/fb ', metavar='lumi')
    parser.add_option('-i','--idir', dest='idir', default = './',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = './',help='directory to write cards', metavar='odir')
    
    (options, args) = parser.parse_args()

    main(options, args)
