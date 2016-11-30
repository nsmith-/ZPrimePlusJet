import ROOT as rt
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array
import os

def writeDataCard(box,txtfileName,sigs,bkgs,histoDict,options):
    obsRate = histoDict['data_obs'].Integral()
    nBkgd = len(bkgs)
    nSig = len(sigs)
    rootFileName = txtfileName.replace('.txt','.root')
    
    rates = [histoDict['%s'%(sig)].Integral() for sig in sigs]
    rates.extend([histoDict['%s'%(bkg)].Integral() for bkg in bkgs])
    
    processes = ['%s_%s'%(box,sig) for sig in sigs]
    processes.extend(['%s_%s'%(box,bkg) for bkg in bkgs])
    
    lumiErrs = [1.30 for sig in sigs]          
    lumiErrs.extend([1.00 for bkg in bkgs])
    
    bkgErrs = [1.00 for sig in sigs]          
    bkgErrs.extend([1.50 for bkg in bkgs])
    
    divider = '------------------------------------------------------------\n'
    datacard = 'imax 1 number of channels\n' + \
      'jmax %i number of processes minus 1\n'%(nBkgd+nSig-1) + \
      'kmax * number of nuisance parameters\n' + \
      divider + \
      'observation %.3f\n'%obsRate + \
      divider + \
      'shapes * * %s $PROCESS $PROCESS_$SYSTEMATIC\n'%(rootFileName) + \
      divider
    binString = 'bin'
    processString = 'process'
    processNumberString = 'process'
    rateString = 'rate'
    lumiString = 'lumi\tlnN'
    bkgErrString = 'bkgErr\tlnN'
    for i in range(0,nBkgd+nSig):
        binString +='\t%s'%box
        processString += '\t%s'%processes[i]
        processNumberString += '\t%i'%(i-nSig+1)
        rateString += '\t%.3f' %rates[i]
        lumiString += '\t%.3f'%lumiErrs[i]
        bkgErrString += '\t%.3f'%bkgErrs[i]
    binString+='\n'; processString+='\n'; processNumberString+='\n'; rateString +='\n'; lumiString+='\n'; bkgErrString+='\n'
    datacard+=binString+processString+processNumberString+rateString+divider

    # now nuisances
    datacard+=lumiString+bkgErrString
    
    txtfile = open(options.odir+'/'+txtfileName,'w')
    txtfile.write(datacard)
    txtfile.close()
    
def main(options, args):
    treeName = 'otree'
    signalTreeName = 'Events'
    sigXsec = 0.65/1.458163e-02

    cutString = '%f*scale1fb*( AK8Puppijet0_pt > 500 && AK8CHSjet0_doublecsv > 0.90 && nmuLoose == 0 && neleLoose == 0) '%(options.lumi)
    
    cutStringSignal = '%f*scale1fb*%f*( AK8Puppijet0_pt > 500 && AK8CHSjet0_doublecsv > 0.90 && nmuLoose == 0 && neleLoose == 0)'%(sigXsec,options.lumi)
    
    varToProject = 'AK8Puppijet0_msd'
    minVar = 0
    maxVar = 600
    nBins = 60            
    box = 'BoostedDijet'
    sigs = ['Phibb125']
    bkgs = ['QCD','W','DY','TTbar','ST']

    tfileName = {}
    tfileName['Phibb125']= options.idir+'/DMSpin0_ggPhibb1j_125.root'
    for bkg in bkgs:
        tfileName[bkg]= options.idir+'/'+bkg+'.root'
    tfile = {}
    tree = {}
    histoDict = {}
    
    for bkg in bkgs:
        print 'making histogram for background: %s'%bkg
        tfile[bkg] = rt.TFile.Open(tfileName[bkg])
        tree[bkg] = tfile[bkg].Get(treeName)
        histoDict[bkg] = rt.TH1D(box+'_'+bkg,box+'_'+bkg,nBins,minVar,maxVar)
        tree[bkg].Project(histoDict[bkg].GetName(),varToProject,cutString)
        
    for sig in sigs:
        print 'making histogram for signal: %s'%sig
        tfile[sig] = rt.TFile.Open(tfileName[sig])
        tree[sig] = tfile[sig].Get(signalTreeName)
        histoDict[sig] = rt.TH1D(box+'_'+sig,box+'_'+sig,nBins,minVar,maxVar)
        tree[sig].Project(histoDict[sig].GetName(),varToProject,cutStringSignal)


    histoDict['data_obs'] = rt.TH1D('data_obs','data_obs',nBins,minVar,maxVar)
    
    for bkg in bkgs:
        histoDict['data_obs'].Add(histoDict[bkg])
    
    
    outFile = 'dataCard_%s_lumi-%.3f_%s.root'%('_'.join(sigs),options.lumi,box)
    
    outputFile = rt.TFile.Open(options.odir+'/'+outFile,'recreate')
    outputFile.cd()
    for key, histo in histoDict.iteritems():
        histo.Write()
    outputFile.Close()
    txtfileName = outFile.replace('.root','.txt')

    writeDataCard(box,txtfileName,sigs,bkgs,histoDict,options)
    print '\ndatacard:\n'
    os.system('cat %s/%s'%(options.odir,txtfileName))



if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('--lumi', dest='lumi', type=float, default = 20,help='lumi in 1/fb ', metavar='lumi')
    parser.add_option('-i','--idir', dest='idir', default = '../data',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = '../cards',help='directory to write cards', metavar='odir')
    
    (options, args) = parser.parse_args()

    main(options, args)
