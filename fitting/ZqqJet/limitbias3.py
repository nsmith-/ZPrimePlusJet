#!/usr/bin/env python
import ROOT as r,sys,math,array,os
from optparse import OptionParser
import random

import tdrstyle
tdrstyle.setTDRStyle()

def parser():
    parser = OptionParser()
    parser.add_option('--sig'    ,action='store',type='float',dest='sig'       ,default=0.25, help='mass')
    parser.add_option('--toys'   ,action='store',type='float',dest='toys'      ,default=100,help='toys')
    parser.add_option('--mass'    ,action='store',type='string',dest='mass'    ,default='50,60,75,90,100,110,125,135,150,165,180,200,250,300'  ,help='sig')
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
    lTree.Draw("(mu-%f)/muErr>>h" % injet)
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
    sub_file.write('combine -M MaxLikelihoodFit --saveNLL --saveWithUncertainties --saveShapes --toysFrequentist  -t 1 --expectSignal %s  --rMax 1.0 --rMin -1.0 --seed %i %s > /dev/null   \n' % (mu,rand,base))
    sub_file.write('mv mlfit.root %s/%stoys.root \n' % (os.getcwd(),iLabel)) 
    sub_file.close()
    os.system('chmod +x %s' % os.path.abspath(sub_file.name))
    os.system('bsub -q 8nh -o out.%%J %s' % (os.path.abspath(sub_file.name)))

def biascondense(iLabel,iSig,iMass):
    os.system("rm alltoys.root")
    #os.system("pwd")
    #print iLabel+"*toys.root"
    os.system("hadd alltoys.root "+iLabel+"*toys.root")
    plotgaus("alltoys.root",iSig,"pull"+iLabel+str(iMass))

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
    sub_file.write('combine  -M GoodnessOfFit --algo saturated  %s --rMax 0.5 --rMin -0.5 --fixedSignalStrength 0 %s \n' % (alt,freeze))
    sub_file.write('mv higgsCombineTest.GoodnessOfFit.mH120.root %s/%sbase1.root \n' % (os.getcwd(),iLabel)) 
    sub_file.write('combine  -M GoodnessOfFit --algo saturated  %s  --rMax 0.5 --rMin -0.5 --fixedSignalStrength 0 %s \n'% (base,freeze))
    sub_file.write('mv higgsCombineTest.GoodnessOfFit.mH120.root %s/%sbase2.root \n' % (os.getcwd(),iLabel))
    rand=int(random.random()*10000)
    sub_file.write('combine -M GenerateOnly %s --rMax 0.5 --rMin -0.5 --toysFrequentist -t %i --expectSignal 0 --saveToys  --seed %s \n' % (base,ntoys,rand))
    sub_file.write('combine -M GoodnessOfFit  %s --rMax 0.5 --rMin -0.5 --algo saturated -t %i --toysFile higgsCombineTest.GenerateOnly.mH120.%s.root --fixedSignalStrength 0 %s \n' % (alt,ntoys,rand,freeze))
    sub_file.write('mv higgsCombineTest.GoodnessOfFit.mH120.123456.root %s/%s%stoys1.root \n' % (os.getcwd(),iMass,iLabel))
    sub_file.write('combine -M GoodnessOfFit  %s --rMax 0.5 --rMin -0.5 --algo saturated -t %i --toysFile higgsCombineTest.GenerateOnly.mH120.%s.root --fixedSignalStrength 0 %s \n' % (base,ntoys,rand,freeze))
    sub_file.write('mv higgsCombineTest.GoodnessOfFit.mH120.123456.root %s/%s%stoys2.root \n' % (os.getcwd(),iMass,iLabel))
    sub_file.close()
    os.system('chmod +x %s' % os.path.abspath(sub_file.name))
    os.system('bsub -q 8nh -o out.%%J %s' % (os.path.abspath(sub_file.name)))

def ftestcondense(iLabel):
    os.system('rm '+iLabel+'toys2.root')
    os.system('rm '+iLabel+'toys1.root')
    #os.system('hadd '+iLabel+'toys2.root '+iLabel+'*toys2.root')
    #os.system('hadd '+iLabel+'toys1.root '+iLabel+'*toys1.root')
    nllBase=nllDiff(iLabel+"1base1.root",iLabel+"1base2.root")
    nllToys=[]
    for pFile in os.listdir(os.getcwd()):
        if pFile.find(".root") > 0 and pFile.find("toys1") > 0 and pFile.find(iLabel) > -1:
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
    
def limit(base):
    os.system('combine -M Asymptotic %s  ' % base)
    os.system('mv higgsCombineTest.Asymptotic.mH120.123456.root limits.root')

def plotmass(base,mass):
    os.system('combine -M MaxLikelihoodFit %s --saveWithUncertainties --saveShapes' % base)
    os.system('cp ../plot.py .')
    os.system('cp ../tdrstyle.py .')
    os.system('python plot.py --mass %s' % str(mass))

def setup(iLabel,mass,iBase,condense):
    if not condense:
        os.system('mkdir %s' % iLabel)
        os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet.txt    > %s/card_rhalphabet.txt'    %(mass,iLabel))
        os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_23.txt > %s/card_rhalphabet_23.txt' %(mass,iLabel))
        os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_33_pt.txt > %s/card_rhalphabet_33_pt.txt' %(mass,iLabel))
        os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_24_pt.txt > %s/card_rhalphabet_24_pt.txt' %(mass,iLabel))
        os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_34_pt.txt > %s/card_rhalphabet_34_pt.txt' %(mass,iLabel))
        os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_43_pt.txt > %s/card_rhalphabet_43_pt.txt' %(mass,iLabel))
        os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_44_pt.txt > %s/card_rhalphabet_44_pt.txt' %(mass,iLabel))
        os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_35_pt.txt > %s/card_rhalphabet_35_pt.txt' %(mass,iLabel))
        os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_35_pt.txt > %s/card_rhalphabet_35_pt.txt' %(mass,iLabel))
        os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_25_pt.txt > %s/card_rhalphabet_25_pt.txt' %(mass,iLabel))
        os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_15_pt.txt > %s/card_rhalphabet_15_pt.txt' %(mass,iLabel))
        os.system('sed "s@zqq100@zqq%s@g" card_rhalphabet_26.txt > %s/card_rhalphabet_26.txt' %(mass,iLabel))
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
        #setup('ZQQ_'+str(mass),mass,"ralpha",options.condense)
        os.chdir ('bias3WZ/ZQQ_'+mass+'_43')
        if not options.condense:
            for i0 in range(0,100):
                #biasgrid('card_rhalphabet_34_pt.txt','card_rhalphabet_34_pt.txt',options.toys,options.sig,'test_34_'+str(i0),mass)
                biasgrid('cards_all_43_zqq%s.txt'%(mass),'cards_all_43_zqq%s.txt'%mass,options.toys,options.sig,'test_43_'+str(i0),mass)
                #ftestgrid('card_rhalphabet_34_pt.txt','card_rhalphabet_35_pt.txt',options.toys,options.sig,'test_34_'+str(i0),mass)
                #ftestgrid('card_rhalphabet_25_pt.txt','card_rhalphabet_35_pt.txt',options.toys,options.sig,'test_25_'+str(i0),mass)
                #ftestgrid('card_rhalphabet_15_pt.txt','card_rhalphabet_25_pt.txt',options.toys,options.sig,'test_15_'+str(i0),mass)
                #ftestgrid('card_rhalphabet_24_pt.txt','card_rhalphabet_25_pt.txt',options.toys,options.sig,'test_24_'+str(i0),mass)
                #goodnessgrid('card_rhalphabet_34_pt.txt',options.toys,options.sig,'test_34_KS_'+str(i0),mass,'KS')
                #goodnessgrid('card_rhalphabet_34_pt.txt',options.toys,options.sig,'test_34_Sat_'+str(i0),mass,'saturated')
        else:
            #goodnesscondense(str(mass)+"test_34_KS_",mass)
            #goodnesscondense(str(mass)+"test_34_Sat_" ,mass)
            #ftestcondense('test_34_')
            #ftestcondense('test_25_')
            #ftestcondense('test_15_')
            #ftestcondense('test_24_')
            biascondense('test_43_',options.sig,mass)
            #biascondense('test_44_',options.sig,mass)
        os.chdir("../..")
    #setupMC('ZQQ_'+str(options.mass),options.mass,"mc")
    #setup('ZQQ_'+str(options.mass),options.mass,"ralpha","base")
    #os.chdir ('ZQQ_'+str(options.mass))
    #generate(options.mass,options.toys)
    #limit('card_ralpha.txt')
    #goodness('card_rhalphabet_cat.txt',options.toys,"goodness"+str(options.mass))
    #bias('card_ralpha.txt','card_ralpha.txt',options.toys,options.sig,"fitbase"+str(options.mass))
    #plotmass('card_ralpha.txt',options.mass)
