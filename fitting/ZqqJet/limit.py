#!/usr/bin/env python
import ROOT as r,sys,math,array,os
from optparse import OptionParser
import random

import tdrstyle
tdrstyle.setTDRStyle()

def parser():
    parser = OptionParser()
    parser.add_option('--sig'    ,action='store',type='float',dest='sig'       ,default=1, help='mass')
    parser.add_option('--toys'   ,action='store',type='float',dest='toys'      ,default=100,help='mass')
    parser.add_option('--mass'    ,action='store',type='string',dest='mass'    ,default='50,55,60,65,70,75,80,85,90,95,100,105,110,115,120,125,130,135,140,145,150,155,160,165,170,175,180,185,190,195,200,205,210,215,220,225,230,235,240,245,250,255,260,265,270,275,280,285,290,295,300'  ,help='sig')
    #parser.add_option('--mass'    ,action='store',type='string',dest='mass'    ,default='55,65,70,80,85,95,105,115,120,130,140,145,155,160,170,175,185,190'  ,help='sig')
    #parser.add_option('--mass'    ,action='store',type='string',dest='mass'    ,default='195,205,210,215,220,225,230,235,240,245,255,260,265,270,285,280,295'  ,help='sig')
    #parser.add_option('--mass'    ,action='store',type='string',dest='mass'    ,default='275,290'  ,help='sig')
    parser.add_option('--condense',action='store_true',         dest='condense',default=False,help='condense') 
    (options,args) = parser.parse_args()
    return options

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
    lH    = r.TH1F("h","h",20,-5,5)
    lTree.Draw("(mu-%f)/muErr>>h" % injet,"fit_status == 0")
    lH.Fit("gaus","L")
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
    lH = r.TH1F(iLabel+"hist",iLabel+"hist",20,min(min(iToys),iCentral)-0.01,max(max(iToys),iCentral)+0.01)
    lH.GetXaxis().SetTitle("#DeltaLL (higher-lower)")  
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
    print "NLL",iFName1,iFName2
    lDiffs=[]
    if not os.path.isfile(iFName1):
        return lDiffs
    if not os.path.isfile(iFName2):
        return lDiffs
    lFile1 = r.TFile(iFName1)
    print "A",[key.GetName() for key in lFile1.GetListOfKeys()]
    if not "limit"  in [key.GetName() for key in lFile1.GetListOfKeys()]:
        return lDiffs
    lTree1 = lFile1.Get("limit")
    lFile2 = r.TFile(iFName2)
    print "B",[key.GetName() for key in lFile2.GetListOfKeys()],"limit" in [key.GetName() for key in lFile2.GetListOfKeys()]
    lCheck = "limit" in [key.GetName() for key in lFile2.GetListOfKeys()]
    if not lCheck:
        return lDiffs
    lTree2 = lFile2.Get("limit")
    pMin = 0 if lTree1.GetEntries() == 1 else 1
    for i0 in range(pMin,lTree1.GetEntries()):
        lTree1.GetEntry(i0)
        lTree2.GetEntry(i0)
        #if lTree1.limit-lTree2.limit > 0:
        #    print i0,"Sign error"
        #    continue
        lDiffs.append(lTree1.limit-lTree2.limit)
        lDiffs.append(lTree1.limit/lTree2.limit-1)
    return lDiffs

def goodnessVals(iFName1):
    lFile1 = r.TFile(iFName1)
    lTree1 = lFile1.Get("limit")
    lDiffs=[]
    for i0 in range(0,lTree1.GetEntries()):
        lTree1.GetEntry(i0)
        lDiffs.append(lTree1.limit)
    return lDiffs

def cmsenv(iFile):
    iFile.write('#!/bin/bash\n')
    iFile.write('cd  /afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/tmp/CMSSW_7_4_7/src  \n')
    iFile.write('eval `scramv1 runtime -sh`\n')
    iFile.write('cd - \n')

def biasgrid(base,alt,ntoys,mu,iLabel,iMass):
    rand=int(random.random()*10000)
    fileName='runbias_1_%s.sh' % (iLabel)
    dirs=os.getcwd().split("/")
    sub_file  = open(fileName,'a')
    cmsenv(sub_file)
    sub_file.write('cp -r %s . \n' % os.getcwd())
    sub_file.write('cd    %s   \n' % dirs[len(dirs)-1])
    #sub_file.write('combine -M GenerateOnly     %s --rMax 1.0 --rMin -1.0 --toysFrequentist -t %i --expectSignal %s --saveToys --seed %i  \n' % (base,ntoys,str(mu),rand))
    #sub_file.write('combine -M MaxLikelihoodFit %s --rMax 1.0 --rMin -1.0 -t %i --saveNLL --toysFile higgsCombineTest.GenerateOnly.mH120.123456.root > /dev/null  \n' % (base,ntoys))
    sub_file.write('combine -M MaxLikelihoodFit --toysNoSystematics  -t %i --expectSignal %s  --rMax 20.0 --rMin -20.0 --initFromBonly --minos none --seed %i   %s  > /dev/null   \n' % (ntoys,str(mu),rand,base))
    sub_file.write('mv mlfit.root %s/%s%stoys.root \n' % (os.getcwd(),iMass,iLabel)) 
    sub_file.close()
    os.system('chmod +x %s' % os.path.abspath(sub_file.name))
    os.system('bsub -q 1nh -o out.%%J %s' % (os.path.abspath(sub_file.name)))

def biascondense(iLabel,iSig,iMass):
    os.system("rm alltoys.root")
    os.system("hadd alltoys.root "+str(iMass)+iLabel+"*toys.root")
    plotgaus("alltoys.root",iSig,"pull"+iLabel)

def goodnessgrid(base,ntoys,sig,iLabel,iMass,algo):
    fileName='rungood_2_%s_%s.sh' % (algo,iLabel)
    dirs=os.getcwd().split("/")
    sub_file  = open(fileName,'a')
    cmsenv(sub_file)
    sub_file.write('cp -r %s . \n' % os.getcwd())
    sub_file.write('cd    %s   \n' % dirs[len(dirs)-1])
    sub_file.write('combine  -M GoodnessOfFit --algo %s  %s --rMax 2 --rMin -2   \n' % (algo,base))
    sub_file.write('mv higgsCombineTest.GoodnessOfFit.mH120.root %s/%sbase1.root \n' % (os.getcwd(),iLabel)) 
    rand=int(random.random()*10000)
    sub_file.write('combine -M GenerateOnly   %s --rMax 2 --rMin -2 --toysFrequentist -t %i --expectSignal 0  --saveToys  --seed %s \n' % (base,ntoys,rand))
    sub_file.write('combine -M GoodnessOfFit  %s --rMax 2 --rMin -2 --algo %s -t %i   --toysFile higgsCombineTest.GenerateOnly.mH120.%s.root \n' % (base,algo,ntoys,rand))
    sub_file.write('mv higgsCombineTest.GoodnessOfFit.mH120.123456.root %s/%s%sgoodness.root \n' % (os.getcwd(),iMass,iLabel))
    sub_file.close()
    os.system('chmod +x %s' % os.path.abspath(sub_file.name))
    os.system('bsub -q 8nh -o out.%%J %s' % (os.path.abspath(sub_file.name)))

def goodnesscondense(iLabel,iMass):
    nllBase=goodnessVals(iLabel.replace(iMass,"")+"5base1.root")
    nllToys=[]
    for pFile in os.listdir(os.getcwd()):
        if pFile.find(".root") > 0 and pFile.find("goodness") > 0 and pFile.find(iLabel) > -1:
            pLabel=pFile.replace("toys1.root","")
            print pLabel
            nllToys.extend(goodnessVals(pLabel))
    lPass=0
    for val in nllToys:
        if val > nllBase[0]:
            lPass+=1
    print "Goodness prob",float(lPass)/float(len(nllToys))
    plotftest(nllToys,nllBase[0],float(lPass)/float(len(nllToys)),iLabel)
    return float(lPass)/float(len(nllToys))

def ftestgrid(base,alt,ntoys,sig,iLabel,iMass):
    freeze="--freezeNuisances ttnormSF,tteffSF,eveto,muveto,trigger,jecs,znormE,znormQ,veff,smear,scale,lumi"
    fileName='runtoy_2_%s.sh' % (iLabel)
    dirs=os.getcwd().split("/")
    sub_file  = open(fileName,'a')
    cmsenv(sub_file)
    sub_file.write('cp -r %s . \n' % os.getcwd())
    sub_file.write('cd    %s   \n' % dirs[len(dirs)-1])
    sub_file.write('combine  -M GoodnessOfFit --algo saturated  %s --rMax 5.0 --rMin -5.0 %s \n' % (alt,freeze))
    sub_file.write('mv higgsCombineTest.GoodnessOfFit.mH120.root %s/%sbase1.root \n' % (os.getcwd(),iLabel)) 
    sub_file.write('combine  -M GoodnessOfFit --algo saturated  %s  --rMax 5.0 --rMin -5.0 %s \n'% (base,freeze))
    sub_file.write('mv higgsCombineTest.GoodnessOfFit.mH120.root %s/%sbase2.root \n' % (os.getcwd(),iLabel))
    rand=int(random.random()*10000)
    sub_file.write('combine -M GenerateOnly  %s --rMax 5.0 --rMin -5.0 --toysFrequentist -t %i --expectSignal 0 --saveToys  --seed %s \n' % (base,ntoys,rand))
    sub_file.write('combine -M GoodnessOfFit %s --rMax 5.0 --rMin -5.0 --algo saturated -t %i --toysFile higgsCombineTest.GenerateOnly.mH120.%s.root  %s \n' % (alt,ntoys,rand,freeze))
    sub_file.write('mv higgsCombineTest.GoodnessOfFit.mH120.123456.root %s/%s%stoys1.root \n' % (os.getcwd(),iMass,iLabel))
    sub_file.write('combine -M GoodnessOfFit  %s --rMax 5.0 --rMin -5.0 --algo saturated -t %i --toysFile higgsCombineTest.GenerateOnly.mH120.%s.root %s \n' % (base,ntoys,rand,freeze))
    sub_file.write('mv higgsCombineTest.GoodnessOfFit.mH120.123456.root %s/%s%stoys2.root \n' % (os.getcwd(),iMass,iLabel))
    sub_file.close()
    os.system('chmod +x %s' % os.path.abspath(sub_file.name))
    os.system('bsub -q 8nh -o out.%%J %s' % (os.path.abspath(sub_file.name)))

def ftestcondense(iLabel):
    os.system('rm '+iLabel+'toys2.root')
    os.system('rm '+iLabel+'toys1.root')
    #os.system('hadd '+iLabel+'toys2.root '+iLabel+'*toys2.root')
    #os.system('hadd '+iLabel+'toys1.root '+iLabel+'*toys1.root')
    nllBase=nllDiff(iLabel+"10base1.root",iLabel+"10base2.root")
    print "test",nllBase
    nllToys=[]
    for pFile in os.listdir(os.getcwd()):
        if pFile.find(".root") > 0 and pFile.find("toys1") > 0 and pFile.find(iLabel) > -1:
            print pFile,iLabel
            pLabel=pFile.replace("toys1.root","")
            print pLabel
            nllToys.extend(nllDiff(pLabel+"toys1.root",pLabel+"toys2.root"))
    lPass=0
    for val in nllToys:
        print val,nllBase[0]
        if val < nllBase[0]:
            lPass+=1
    print "ftest prob",float(lPass)/float(len(nllToys))
    plotftest(nllToys,nllBase[0],float(lPass)/float(len(nllToys)),iLabel+"f")
    return float(lPass)/float(len(nllToys))

def ftest(base,alt,ntoys,sig,iLabel):
    freeze="--freezeNuisances ttnormSF,tteffSF,eveto,muveto,trigger,jecs,znormE,znormQ,veff,smear,scale,lumi"
    os.system('combine -M  GoodnessOfFit --algo saturated  %s --rMax 2 --rMin -2  ' % (alt))
    os.system('mv higgsCombineTest.GoodnessOfFit.mH120.root base1.root')
    os.system('combine -M  GoodnessOfFit --algo saturated  %s  --rMax 2 --rMin -2 '% (base))
    os.system('mv higgsCombineTest.GoodnessOfFit.mH120.root base2.root')
    os.system('combine -M GenerateOnly %s --rMax 2 --rMin -2 --toysFrequentist -t %i --expectSignal %s --saveToys ' % (base,ntoys,sig))
    os.system('combine -M GoodnessOfFit --algo saturated  %s --rMax 2 --rMin -2 -t %i --toysFile higgsCombineTest.GenerateOnly.mH120.123456.root %s' % (alt,ntoys,freeze))
    os.system('mv higgsCombineTest.GoodnessOfFit.mH120.123456.root toys1.root')
    os.system('combine -M GoodnessOfFit --algo saturated  %s --rMax 2 --rMin -2 -t %i  --toysFile higgsCombineTest.GenerateOnly.mH120.123456.root %s' % (base,ntoys,freeze))
    os.system('mv higgsCombineTest.GoodnessOfFit.mH120.123456.root toys2.root')
    #os.system('rm higgsCombineTest.GenerateOnly.mH120.123456.root')
    nllBase=nllDiff("base2.root","base1.root")
    nllToys=nllDiff("toys2.root","toys1.root")
    lPass=0
    for val in nllToys:
        print val,nllBase[0]
        if val < nllBase[0]:
            lPass+=1
    print "ftest prob",float(lPass)/float(len(nllToys))
    plotftest(nllToys,nllBase[0],float(lPass)/float(len(nllToys)),iLabel)
    return float(lPass)/float(len(nllToys))

def goodness(base,ntoys,iLabel):
    os.system('combine -M GoodnessOfFit %s --rMax 2 --rMin -2  --algorithm saturated ' % base)
    os.system('mv higgsCombineTest.GoodnessOfFit.mH120.root goodbase.root')
    #os.system('combine -M GoodnessOfFit %s --rMax 2 --rMin -2 --toysNoSystematics -t %i   --algorithm saturated --fixedSignalStrength 0' % (base,ntoys))
    #os.system('combine -M GoodnessOfFit %s --rMax 2 --rMin -2 --toysFrequentist -t %i  --algorithm saturated --fixedSignalStrength 0 ' % (base,ntoys))
    os.system('combine -M GoodnessOfFit %s --rMax 2 --rMin -2 -t %i  --algorithm saturated --fixedSignalStrength 0 ' % (base,ntoys))
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
    os.system('combine -M GenerateOnly     %s --rMax 100 --rMin -100 --toysFrequentist -t %i --expectSignal %i --saveToys ' % (alt,ntoys,mu))
    os.system('combine -M MaxLikelihoodFit %s --rMax 100 --rMin -100 -t %i --saveNLL --toysFile higgsCombineTest.GenerateOnly.mH120.123456.root' % (base,ntoys))
    os.system('rm  higgsCombineTest.MaxLikelihoodFit.mH120.123456.root')
    os.system('mv  mlfit.root toys.root')
    plotgaus("toys.root",mu,"pull"+iLabel)
    
def limit(base,iLabel,iMass):
    fileName='runlimit_1_%s.sh' % (iLabel)
    sub_file  = open(fileName,'a')
    dirs=os.getcwd().split("/")
    cmsenv(sub_file)
    sub_file.write('cp -r %s . \n' % os.getcwd())
    sub_file.write('cd    %s   \n' % dirs[len(dirs)-1])
    if int(iMass) < 200:
        sub_file.write('combine -M Asymptotic %s  --rMin -2 --rMax 2 --minimizerStrategy 1 \n' % base)
        sub_file.write('combine -M MaxLikelihoodFit %s  --rMin -2 --rMax 2 --minimizerStrategy 1 --saveShapes --saveWithUncertainties > /dev/null \n' % base)
    else:
        sub_file.write('combine -M Asymptotic %s  --rMin -10 --rMax 10 --minimizerStrategy 1 \n' % base)
        sub_file.write('combine -M MaxLikelihoodFit %s  --rMin -10 --rMax 10 --minimizerStrategy 1 --saveShapes --saveWithUncertainties > /dev/null \n' % base)
    sub_file.write('mv higgsCombineTest.Asymptotic.mH120.root %s/%slimit.root \n' % (os.getcwd(),iLabel)) 
    sub_file.write('mv mlfit.root %s/%smlfit.root \n' % (os.getcwd(),iLabel)) 
    sub_file.close()
    os.system('chmod +x %s' % os.path.abspath(sub_file.name))
    os.system('bsub -q cmscaf1nd -o out.%%J %s' % (os.path.abspath(sub_file.name)))

def plotmass(base,mass):
    os.system('combine -M MaxLikelihoodFit %s --saveWithUncertainties --saveShapes' % base)
    os.system('cp ../plot.py .')
    os.system('cp ../tdrstyle.py .')
    os.system('python plot.py --mass %s' % str(mass))

def setup(iLabel,mass,iBase,condense):
    if not condense:
        os.system('mkdir %s' % iLabel)
        #os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet.txt    > %s/card_rhalphabet.txt'    %(mass,iLabel))
        #os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_23.txt > %s/card_rhalphabet_23.txt' %(mass,iLabel))
        #os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_33_pt.txt > %s/card_rhalphabet_33_pt.txt' %(mass,iLabel))
        #os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_24_pt.txt > %s/card_rhalphabet_24_pt.txt' %(mass,iLabel))
        os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_34_pt.txt > %s/card_rhalphabet_34_pt.txt' %(mass,iLabel))
        #os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_43_pt.txt > %s/card_rhalphabet_43_pt.txt' %(mass,iLabel))
        #os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_44_pt.txt > %s/card_rhalphabet_44_pt.txt' %(mass,iLabel))
        #os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_35_pt.txt > %s/card_rhalphabet_35_pt.txt' %(mass,iLabel))
        #os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_35_pt.txt > %s/card_rhalphabet_35_pt.txt' %(mass,iLabel))
        #os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_25_pt.txt > %s/card_rhalphabet_25_pt.txt' %(mass,iLabel))
        #os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_15_pt.txt > %s/card_rhalphabet_15_pt.txt' %(mass,iLabel))
        #os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_26.txt > %s/card_rhalphabet_26.txt' %(mass,iLabel))
        os.system('cp base*.root %s' % (iLabel))
        os.system('cp %s*.root %s' % (iBase,iLabel))
    os.chdir (iLabel)

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
        #os.system('bsub -q 8nh -o out.%%J %s' % (os.path.abspath(sub_file.name)))

if __name__ == "__main__":
    options = parser()
    print options
    #ftest('card_rhalphabet.txt','card_rhalphabet_34.txt',options.toys,options.sig,'test_34')
    for mass in options.mass.split(','):
        setup('ZQQ_'+str(mass),mass,"ralpha",options.condense)
        
        if not options.condense:
            for i0 in range(0,1):
                #biasgrid('card_rhalphabet_34_pt.txt','card_rhalphabet_34_pt.txt',options.toys,options.sig,'test_34_'+str(i0),mass)
                #biasgrid('card_rhalphabet_35_pt.txt','card_rhalphabet_35_pt.txt',options.toys,options.sig,'test_35_'+str(i0),mass)
                #ftestgrid('card_rhalphabet_34_pt.txt','card_rhalphabet_35_pt.txt',options.toys,options.sig,'test_34_35_'+str(i0),mass)
                #ftestgrid('card_rhalphabet_34_pt.txt','card_rhalphabet_44_pt.txt',options.toys,options.sig,'test_34_44_'+str(i0),mass)
                #ftestgrid('card_rhalphabet_33_pt.txt','card_rhalphabet_34_pt.txt',options.toys,options.sig,'test_33_34_'+str(i0),mass)
                #ftestgrid('card_rhalphabet_24_pt.txt','card_rhalphabet_34_pt.txt',options.toys,options.sig,'test_24_34_'+str(i0),mass)
                #goodnessgrid('card_rhalphabet_34_pt.txt',options.toys,options.sig,'test_34_Sat_'+str(i0),mass,'saturated')
                #goodnessgrid('card_rhalphabet_35_pt.txt',options.toys,options.sig,'test_35_Sat_'+str(i0),mass,'saturated')
                limit('card_rhalphabet_34_pt.txt','lim_34',mass)
        else:
            goodnesscondense(str(mass)+"test_34_Sat_",mass)
            #goodnesscondense(str(mass)+"test_35_Sat_",mass)
            #ftestcondense('test_34_35_')
            #ftestcondense('test_34_44_')
            #ftestcondense('test_33_34_')
            #ftestcondense('test_24_34_')
            #biascondense('test_34_',options.sig,mass)
            #biascondense('test_35_',options.sig,mass)
        os.chdir("..")
    #setupMC('ZQQ_'+str(options.mass),options.mass,"mc")
    #setup('ZQQ_'+str(options.mass),options.mass,"ralpha","base")
    #os.chdir ('ZQQ_'+str(options.mass))
    #generate(options.mass,options.toys)
    #limit('card_ralpha.txt')
    #goodness('card_rhalphabet_cat.txt',options.toys,"goodness"+str(options.mass))
    #bias('card_ralpha.txt','card_ralpha.txt',options.toys,options.sig,"fitbase"+str(options.mass))
    #plotmass('card_ralpha.txt',options.mass)
