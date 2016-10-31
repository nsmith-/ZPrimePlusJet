#!/usr/bin/env python
import ROOT as r,sys,math,array,os
from optparse import OptionParser

import tdrstyle
tdrstyle.setTDRStyle()

def parser():
    parser = OptionParser()
    parser.add_option('--mass'   ,action='store',type='int',dest='mass'   ,default=50, help='mass')
    parser.add_option('--toys'   ,action='store',type='int',dest='toys'   ,default=100,help='mass')
    parser.add_option('--sig'    ,action='store',type='int',dest='sig'    ,default=10 ,help='sig')
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
    os.system('combine -M GenerateOnly     %s --rMax 100 --rMin -100 --toysFrequentist -t %i --expectSignal %i --saveToys ' % (alt,ntoys,mu))
    os.system('combine -M MaxLikelihoodFit %s --rMax 100 --rMin -100 -t %i --saveNLL --toysFile higgsCombineTest.GenerateOnly.mH120.123456.root' % (base,ntoys))
    os.system('rm  higgsCombineTest.MaxLikelihoodFit.mH120.123456.root')
    os.system('mv  mlfit.root toys.root')
    plotgaus("toys.root",mu,"pull"+iLabel)
    
def limit(base):
    os.system('combine -M Asymptotic %s --rMax 100 --rMin -100 ' % base)
    os.system('mv higgsCombineTest.Asymptotic.mH120.123456.root limits.root')

def plotmass(base,mass):
    os.system('combine -M MaxLikelihoodFit %s --rMax 100 --rMin -100 --saveWithUncertainties --saveShapes' % base)
    os.system('cp ../plot.py .')
    os.system('cp ../tdrstyle.py .')
    os.system('python plot.py --mass %s' % str(mass))

def setup(iLabel,mass,iBase,iAlt):
    os.system('mkdir %s' % iLabel)
    os.system('sed "s@XXX@%s@g" card_cat_%s_tmp.txt > %s/card_cat_%s.txt' %(mass,iBase,iLabel,iBase))
    os.system('sed "s@XXX@%s@g" card_cat_%s_tmp.txt > %s/card_cat_%s.txt' %(mass,iAlt ,iLabel,iAlt))
    os.system('cp %s.root %s' % (iBase,iLabel))
    os.system('cp %s.root %s' % (iAlt,iLabel))
    os.chdir (iLabel)

if __name__ == "__main__":
    options = parser()
    print options
    setup('ZQQ_'+str(options.mass),options.mass,"bern5","bern6")
    limit('card_cat_bern5.txt')
    ftest('card_cat_bern5.txt','card_cat_bern6.txt',options.toys,"ftest"+str(options.mass))
    goodness('card_cat_bern5.txt',options.toys,"goodness"+str(options.mass))
    bias('card_cat_bern5.txt','card_cat_bern6.txt',options.toys,options.sig,"fitbias"+str(options.mass))
    bias('card_cat_bern5.txt','card_cat_bern5.txt',options.toys,options.sig,"fitbase"+str(options.mass))
    plotmass('card_cat_bern5.txt',options.mass)
