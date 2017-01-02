#!/usr/bin/env python
import ROOT as r,sys,math,array,os
from optparse import OptionParser

sys.path.insert(0, '../.')
from tools import *

def end():
    if __name__ == '__main__':
        rep = ''
        while not rep in [ 'q', 'Q','a',' ' ]:
            rep = raw_input( 'enter "q" to quit: ' )
            if 1 < len(rep):
                rep = rep[0]

def plotgaus(iFName,injet,iLabel):
    lCan   = r.TCanvas(str(iLabel),str(iLabel),800,600)
    lFile = r.TFile(iFName)
    lTree = lFile.Get("tree_fit_sb")
    lH    = r.TH1F("h","h",100,-20,20)
    lTree.Draw("(mu-%i)/muErr>>h" % injet)
    lH.Fit("gaus")
    lH.GetXaxis().SetTitle("(#mu_{i}-#bar{#mu})/#sigma")
    lH.GetFunction("gaus").SetLineColor(2)
    lH.GetFunction("gaus").SetLineStyle(2)
    lH.Draw("ep")
    lH.GetFunction("gaus").Draw("sames")
    lH.Draw("ep sames")
    lCan.Modified()
    lCan.Update()
    lCan.SaveAs(iLabel+".png")
    lCan.SaveAs(iLabel+".pdf")
    #end()

def plotftest(iToys,iCentral,prob,iLabel):
    lCan   = r.TCanvas(str(iLabel),str(iLabel),800,600)
    lH = r.TH1F(iLabel+"hist",iLabel+"hist",20,min(min(iToys),iCentral)-20,max(max(iToys),iCentral)+20)
    lH.GetXaxis().SetTitle("#DeltaLL")  
    for val in iToys:
        lH.Fill(val)
    lH.Draw("hist")
    lLine  = r.TLine(iCentral,0,iCentral,lH.GetMaximum())
    lLine.SetLineColor(2)
    lLine.Draw()
    lText  = r.TPaveText(0.7,0.7,0.88,0.88,"NDCNB") 
    lText.SetFillColor(0)
    lText.SetBorderSize(0)
    lText.AddText("F-test prob = "+str(prob)) if iLabel.find('f') > -1 else  lText.AddText("Goodness prob = "+str(prob))
    lText.Draw()
    lCan.SaveAs(iLabel+".png")
    lCan.SaveAs(iLabel+".pdf")
    #end()

def nllDiff(iFName1,iFName2):
    lFile1 = r.TFile(iFName1)
    lTree1 = lFile1.Get("limit")
    lFile2 = r.TFile(iFName2)
    lTree2 = lFile2.Get("limit")
    lDiffs=[]
    for i0 in range(0,lTree1.GetEntries()):
        lTree1.GetEntry(i0)
        lTree2.GetEntry(i0)
        lDiffs.append(lTree1.nll0-lTree2.nll0)
    return lDiffs

def goodnessVals(iFName1):
    lFile1 = r.TFile(iFName1)
    lTree1 = lFile1.Get("limit")
    lDiffs=[]
    for i0 in range(0,lTree1.GetEntries()):
        lTree1.GetEntry(i0)
        lDiffs.append(lTree1.limit)
    return lDiffs

def ftest(base,alt,ntoys,iLabel):
    os.system('combine -M MultiDimFit %s --rMax 100 --rMin -100 --saveNLL' % alt)
    os.system('mv higgsCombineTest.MultiDimFit.mH120.root base1.root')
    os.system('combine -M MultiDimFit %s  --rMax 100 --rMin -100 --saveNLL'% base)
    os.system('mv higgsCombineTest.MultiDimFit.mH120.root base2.root')
    os.system('combine -M GenerateOnly %s --rMax 100 --rMin -100 --toysFrequentist -t %i --expectSignal 10 --saveToys ' % (base,ntoys))
    os.system('combine -M MultiDimFit  %s --rMax 100 --rMin -100 -t %i --saveNLL --toysFile higgsCombineTest.GenerateOnly.mH120.123456.root' % (alt,ntoys))
    os.system('mv higgsCombineTest.MultiDimFit.mH120.123456.root toys1.root')
    os.system('combine -M MultiDimFit  %s --rMax 100 --rMin -100 -t %i --saveNLL --toysFile higgsCombineTest.GenerateOnly.mH120.123456.root' % (base,ntoys))
    os.system('mv higgsCombineTest.MultiDimFit.mH120.123456.root toys2.root')
    #os.system('rm higgsCombineTest.GenerateOnly.mH120.123456.root')
    nllBase=nllDiff("base1.root","base2.root")
    nllToys=nllDiff("toys1.root","toys2.root")
    lPass=0
    for val in nllToys:
        print val,nllBase[0]
        if val < nllBase[0]:
            lPass+=1
    print "ftest prob",float(lPass)/float(len(nllToys))
    plotftest(nllToys,nllBase[0],float(lPass)/float(len(nllToys)),iLabel)
    return float(lPass)/float(len(nllToys))

def goodness(base,ntoys,iLabel):
    os.system('combine -M GoodnessOfFit %s --rMax 100 --rMin -100  --algorithm saturated' % base)
    os.system('mv higgsCombineTest.GoodnessOfFit.mH120.root goodbase.root')
    os.system('combine -M GoodnessOfFit %s --rMax 100 --rMin -100 --toysFrequentist -t %i  --algorithm saturated ' % (base,ntoys))
    os.system('mv higgsCombineTest.GoodnessOfFit.mH120.123456.root goodtoys.root')
    nllBase=goodnessVals('goodbase.root')
    nllToys=goodnessVals('goodtoys.root')
    lPass=0
    for val in nllToys:
        if val > nllBase[0]:
            lPass+=1
    print "Goodness prob",float(lPass)/float(len(nllToys))
    plotftest(nllToys,nllBase[0],float(lPass)/float(len(nllToys)),iLabel)
    return float(lPass)/float(len(nllToys))

def bias(base,alt,ntoys,mu,iLabel):
    os.system('combine -M GenerateOnly     %s --rMax 50 --rMin -50 -t %i --expectSignal %i --saveToys ' % (alt,ntoys,mu))
    os.system('combine -M MaxLikelihoodFit %s --rMax 50 --rMin -50 -t %i --saveNLL --toysFile higgsCombineTest.GenerateOnly.mH120.123456.root'  % (base,ntoys))
    os.system('rm  higgsCombineTest.MaxLikelihoodFit.mH120.123456.root')
    os.system('mv  mlfit.root toys.root')
    plotgaus("toys.root",mu,"pull"+iLabel)
    
def limit(base):
    os.system('combine -M Asymptotic %s  ' % base)
    os.system('mv higgsCombineTest.Asymptotic.mH120.root limits.root')
    #os.system('mv higgsCombineTest.Asymptotic.mH120.123456.root limits.root')

def plotmass(base,mass):
    os.system('combine -M MaxLikelihoodFit %s --saveWithUncertainties --saveShapes' % base)
    os.system('cp ../plot.py .')
    #os.system('cp ../tdrstyle.py .')
    os.system('python plot.py --mass %s' % str(mass))

def setup(iLabel,mass,iBase,iRalph):
    #os.system('mkdir %s' % iLabel)
    os.system('sed "s@XXX@%s@g" card_%s_tmp2.txt > %s/card_%s.txt' %(mass,iBase,iLabel,iBase))
    os.system('cp %s*.root %s' % (iBase,iLabel))
    os.system('cp %s*.root %s' % (iRalph,iLabel))
    #os.chdir (iLabel)

def setupMC(iLabel,mass,iBase):
    os.system('mkdir %s' % iLabel)
    os.system('sed "s@XXX@%s@g" mc_tmp2.txt > %s/mc.txt' %(mass,iLabel))
    os.system('cp %s*.root %s' % (iBase,iLabel))
    #os.chdir (iLabel)

def generate(mass,toys):
    for i0 in range(0,toys):
        fileName='runtoy_%s.sh' % (i0)
        sub_file  = open(fileName,'a')
        sub_file.write('#!/bin/bash\n')
        sub_file.write('cd  /afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/CMSSW_7_1_20/src  \n')
        sub_file.write('eval `scramv1 runtime -sh`\n')
        sub_file.write('cd - \n')
        sub_file.write('cp -r %s . \n' % os.getcwd())
        sub_file.write('cd ZQQ_%s \n' % mass)
        sub_file.write('combine -M GenerateOnly --toysNoSystematics -t 1 mc.txt --saveToys --expectSignal 1 --seed %s \n' % i0)
        sub_file.write('combine -M MaxLikelihoodFit card_ralpha.txt -t 1  --toysFile higgsCombineTest.GenerateOnly.mH120.%s.root  > /dev/null \n' % i0 )
        sub_file.write('mv mlfit.root %s/mlfit_%s.root  \n' % (os.getcwd(),i0))
        sub_file.close()
        os.system('chmod +x %s' % os.path.abspath(sub_file.name))
        os.system('bsub -q 8nh -o out.%%J %s' % (os.path.abspath(sub_file.name)))

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('--mass'   ,action='store',type='int',dest='mass'   ,default=125, help='mass')
    parser.add_option('--toys'   ,action='store',type='int',dest='toys'   ,default=200,help='mass')
    parser.add_option('--sig'    ,action='store',type='int',dest='sig'    ,default=1 ,help='sig')
    (options,args) = parser.parse_args()
    print options

    import tdrstyle
    tdrstyle.setTDRStyle()

    #setupMC('ZQQ_'+str(options.mass),options.mass,"mc")
    #setup('ZQQ_'+str(options.mass),options.mass,"ralpha","base")
    #os.chdir ('ZQQ_'+str(options.mass))
    #generate(options.mass,options.toys)

    #limit('combined.txt')
    #ftest('combined.txt','combined_r2p1.txt',100,'ftestpol2')	

    #goodness('card_ralpha.txt',options.toys,"goodness"+str(options.mass))
    bias('combined.txt','combined.txt',options.toys,options.sig,"fitbase"+str(options.mass))
    #plotmass('card_ralpha.txt',options.mass)
