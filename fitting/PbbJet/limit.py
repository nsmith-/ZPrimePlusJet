#!/usr/bin/env python
import ROOT as r,sys,math,array,os
from optparse import OptionParser

#sys.path.insert(0, '$ZPRIMEPLUSJET_BASE/fitting/')
from tools import *

def exec_me(command, dryRun=False):
    print command
    if not dryRun:
        os.system(command)

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

def plotftest(iToys,iCentral,prob,iLabel,options):
    lCan   = r.TCanvas(str(iLabel),str(iLabel),800,600)    
    lCan.SetLeftMargin(0.12) 
    lCan.SetBottomMargin(0.12)
    lCan.SetRightMargin(0.1)
    lCan.SetTopMargin(0.1)
    
    if options.method=='FTest':
        lH = r.TH1F(iLabel+"hist",iLabel+"hist",70,0,max(max(iToys),iCentral)+1)
        lH_cut = r.TH1F(iLabel+"hist",iLabel+"hist",70,0,max(max(iToys),iCentral)+1)
    elif options.method=='GoodnessOfFit' and options.algo=='saturated':
        lH = r.TH1F(iLabel+"hist",iLabel+"hist",70,0,max(max(iToys),iCentral)+100)
        lH_cut = r.TH1F(iLabel+"hist",iLabel+"hist",70,0,max(max(iToys),iCentral)+100)
    elif options.method=='GoodnessOfFit' and options.algo=='KS':
        lH = r.TH1F(iLabel+"hist",iLabel+"hist",70,0,max(max(iToys),iCentral)+0.05)
        lH_cut = r.TH1F(iLabel+"hist",iLabel+"hist",70,0,max(max(iToys),iCentral)+0.05)
    
    if options.method=='FTest':
        lH.GetXaxis().SetTitle("F = #frac{-2log(#lambda_{1}/#lambda_{2})/(p_{2}-p_{1})}{-2log#lambda_{2}/(n-p_{2})}")
        lH.GetXaxis().SetTitleSize(0.025)
        lH.GetXaxis().SetTitleOffset(2)
        lH.GetYaxis().SetTitle("Pseudodatasets")
        lH.GetYaxis().SetTitleOffset(0.85)
    elif options.method=='GoodnessOfFit' and options.algo=='saturated':
        lH.GetXaxis().SetTitle("-2log#lambda")  
        lH.GetYaxis().SetTitle("Pseudodatasets")
        lH.GetYaxis().SetTitleOffset(0.85)
    elif options.method=='GoodnessOfFit' and options.algo=='KS':
        lH.GetXaxis().SetTitle("KS")  
        lH.GetYaxis().SetTitle("Pseudodatasets")
        lH.GetYaxis().SetTitleOffset(0.85)
    for val in iToys:
        lH.Fill(val)
        if val > iCentral:
            lH_cut.Fill(val)
    lH.SetMarkerStyle(20)
    lH.Draw("pez")
    lLine  = r.TArrow(iCentral,0.25*lH.GetMaximum(),iCentral,0)
    lLine.SetLineColor(r.kBlue+1)
    lLine.SetLineWidth(2)

    lH_cut.SetLineColor(r.kViolet-10)
    lH_cut.SetFillColor(r.kViolet-10)
    lH_cut.Draw("histsame")
    
    if options.method=='FTest':
        fdist = r.TF1("fDist", "[0]*TMath::FDist(x, [1], [2])", 0,max(max(iToys),iCentral)+1)
        fdist.SetParameter(0,lH.Integral()*((max(max(iToys),iCentral)+1)/70.))
        fdist.SetParameter(1,options.p2-options.p1)
        fdist.SetParameter(2,options.n-options.p2)
        fdist.Draw('same')
        #lH.Fit(fdist,'mle')
    elif options.method=='GoodnessOfFit' and options.algo=='saturated':
        chi2_func = r.TF1('chisqpdf','[0]*ROOT::Math::chisquared_pdf(x,[1])',0,max(max(iToys),iCentral)+100)
        chi2_func.SetParameter(0,lH.Integral())
        chi2_func.SetParameter(1,50)
        chi2_func.Draw('same')
        lH.Fit(chi2_func,"mle")        
    lH.Draw("pezsame")
    lLine.Draw()
        
    tLeg = r.TLegend(0.6,0.6,0.89,0.89)
    tLeg.SetLineColor(r.kWhite)
    tLeg.SetLineWidth(0)
    tLeg.SetFillStyle(0)
    tLeg.SetTextFont(42)
    tLeg.AddEntry(lH,"toy data","lep")
    tLeg.AddEntry(lLine,"observed = %.1f"%iCentral,"l")
    tLeg.AddEntry(lH_cut,"p-value = %.2f"%(1-prob),"f")
    if options.method=='FTest':
        #tLeg.AddEntry(fdist,"f-dist fit, ndf = (%.1f #pm %.1f, %.1f #pm %.1f) "%(fdist.GetParameter(1),fdist.GetParError(1),fdist.GetParameter(2),fdist.GetParError(2)),"l")
        tLeg.AddEntry(fdist,"F-dist, ndf = (%.0f, %.0f) "%(fdist.GetParameter(1),fdist.GetParameter(2)),"l")        
    elif options.method=='GoodnessOfFit' and options.algo=='saturated':
        tLeg.AddEntry(chi2_func,"#chi^{2} fit, ndf = %.1f #pm %.1f"%(chi2_func.GetParameter(1),chi2_func.GetParError(1)),"l")
            
    tLeg.Draw("same")

    l = r.TLatex()
    l.SetTextAlign(11)
    l.SetTextSize(0.06)
    l.SetTextFont(62)
    l.SetNDC()
    l.DrawLatex(0.12,0.91,"CMS")
    l.SetTextSize(0.05)
    l.SetTextFont(52)
    if options.isData:
        l.DrawLatex(0.23,0.91,"Preliminary")
    else:
        l.DrawLatex(0.23,0.91,"Simulation")
    l.SetTextFont(42)
    l.DrawLatex(0.76,0.91,"%.1f fb^{-1}"%options.lumi)
    l.SetTextFont(52)
    l.SetTextSize(0.045)
    

    
    lCan.SaveAs(options.odir+'/'+iLabel+".pdf")
    lCan.SaveAs(options.odir+'/'+iLabel+".C")
    #end()

def nllDiff(iFName1,iFName2):
    lFile1 = r.TFile.Open(iFName1)
    lTree1 = lFile1.Get("limit")
    lFile2 = r.TFile.Open(iFName2)
    lTree2 = lFile2.Get("limit")
    lDiffs=[]
    for i0 in range(0,lTree1.GetEntries()):
        lTree1.GetEntry(i0)
        lTree2.GetEntry(i0)
        diff = 2*(lTree1.nll-lTree1.nll0)-2*(lTree2.nll-lTree2.nll0)
        lDiffs.append(diff)
    return lDiffs


def fStat(iFName1,iFName2,p1,p2,n):
    lFile1 = r.TFile.Open(iFName1)
    lTree1 = lFile1.Get("limit")
    lFile2 = r.TFile.Open(iFName2)
    lTree2 = lFile2.Get("limit")
    lDiffs=[]
    for i0 in range(0,lTree1.GetEntries()):
        lTree1.GetEntry(i0)
        lTree2.GetEntry(i0)
        if lTree1.limit-lTree2.limit>0:
            F = (lTree1.limit-lTree2.limit)/(p2-p1)/(lTree2.limit/(n-p2))
            print i0, ":", lTree1.limit, "-", lTree2.limit, "=", lTree1.limit-lTree2.limit, "F =", F
            lDiffs.append(F)
    return lDiffs

def goodnessVals(iFName1):
    lFile1 = r.TFile.Open(iFName1)
    lTree1 = lFile1.Get("limit")
    lDiffs=[]
    for i0 in range(0,lTree1.GetEntries()):
        lTree1.GetEntry(i0)
        lDiffs.append(lTree1.limit)
    return lDiffs

def ftest(base,alt,ntoys,iLabel,options):
    if not options.justPlot:
        exec_me('combine -M GoodnessOfFit %s  --rMax 20 --rMin -20 --fixedSignalStrength 0 --algorithm saturated -n %s --freezeNuisances %s'% (base,base.split('/')[-1].replace('.txt',''), options.freezeNuisances),options.dryRun)
        exec_me('cp higgsCombine%s.GoodnessOfFit.mH120.root %s/base1.root'%(base.split('/')[-1].replace('.txt',''),options.odir),options.dryRun)
        exec_me('combine -M GoodnessOfFit %s --rMax 20 --rMin -20 --fixedSignalStrength 0 --algorithm saturated  -n %s --freezeNuisances %s' % (alt,alt.split('/')[-1].replace('.txt',''), options.freezeNuisances),options.dryRun)
        exec_me('cp higgsCombine%s.GoodnessOfFit.mH120.root %s/base2.root'%(alt.split('/')[-1].replace('.txt',''),options.odir),options.dryRun)
        exec_me('combine -M GenerateOnly %s --rMax 20 --rMin -20 --toysFrequentist -t %i --expectSignal %f --saveToys -n %s' % (base,ntoys,options.r,base.split('/')[-1].replace('.txt','')))
        exec_me('cp higgsCombine%s.GenerateOnly.mH120.123456.root %s/'%(base.split('/')[-1].replace('.txt',''),options.odir))
        exec_me('combine -M GoodnessOfFit %s --rMax 20 --rMin -20 -t %i --fixedSignalStrength 0 --toysFile %s/higgsCombine%s.GenerateOnly.mH120.123456.root --algorithm saturated -n %s --freezeNuisances %s' % (base,ntoys,options.odir,base.split('/')[-1].replace('.txt',''),base.split('/')[-1].replace('.txt',''), options.freezeNuisances),options.dryRun)
        exec_me('cp higgsCombine%s.GoodnessOfFit.mH120.123456.root %s/toys1.root'%(base.split('/')[-1].replace('.txt',''),options.odir),options.dryRun)
        exec_me('combine -M GoodnessOfFit %s --rMax 20 --rMin -20 -t %i --fixedSignalStrength 0 --toysFile %s/higgsCombine%s.GenerateOnly.mH120.123456.root --algorithm saturated -n %s --freezeNuisances %s' % (alt,ntoys,options.odir,base.split('/')[-1].replace('.txt',''),alt.split('/')[-1].replace('.txt',''), options.freezeNuisances),options.dryRun)
        exec_me('cp higgsCombine%s.GoodnessOfFit.mH120.123456.root %s/toys2.root'%(alt.split('/')[-1].replace('.txt',''),options.odir))    
    if options.dryRun: sys.exit()
    nllBase=fStat("%s/base1.root"%options.odir,"%s/base2.root"%options.odir,options.p1,options.p2,options.n)
    nllToys=fStat("%s/toys1.root"%options.odir,"%s/toys2.root"%options.odir,options.p1,options.p2,options.n)
    lPass=0
    for val in nllToys:
        #print val,nllBase[0]
        if nllBase[0] > val:
            lPass+=1
    pval = 1
    if len(nllToys)>0:
        pval = float(lPass)/float(len(nllToys))
        print "FTest p-value",pval
    plotftest(nllToys,nllBase[0],pval,iLabel,options)
    return float(lPass)/float(len(nllToys))

def goodness(base,ntoys,iLabel,options):
    if not options.justPlot:
        # --fixedSignalStrength %f  --freezeNuisances tqqnormSF,tqqeffSF 
        exec_me('combine -M GoodnessOfFit %s  --rMax 20 --rMin -20 --algorithm %s -n %s --freezeNuisances %s'% (base,options.algo,base.split('/')[-1].replace('.txt',''),options.freezeNuisances),options.dryRun)
        exec_me('cp higgsCombine%s.GoodnessOfFit.mH120.root %s/goodbase.root'%(base.split('/')[-1].replace('.txt',''),options.odir),options.dryRun)
        exec_me('combine -M GenerateOnly %s --rMax 20 --rMin -20 --toysFrequentist -t %i --expectSignal %f --saveToys -n %s --freezeNuisances %s' % (base,ntoys,options.r,base.split('/')[-1].replace('.txt',''),options.freezeNuisances),options.dryRun)
        exec_me('cp higgsCombine%s.GenerateOnly.mH120.123456.root %s/'%(base.split('/')[-1].replace('.txt',''),options.odir),options.dryRun)        
        exec_me('combine -M GoodnessOfFit %s --rMax 20 --rMin -20 -t %i --toysFile %s/higgsCombine%s.GenerateOnly.mH120.123456.root --algorithm %s -n %s --freezeNuisances %s' % (base,ntoys,options.odir,base.split('/')[-1].replace('.txt',''),options.algo,base.split('/')[-1].replace('.txt',''),options.freezeNuisances),options.dryRun)
        exec_me('cp higgsCombine%s.GoodnessOfFit.mH120.123456.root %s/goodtoys.root'%(base.split('/')[-1].replace('.txt',''),options.odir),options.dryRun)        
    if options.dryRun: sys.exit()
    nllBase=goodnessVals('%s/goodbase.root'%options.odir)
    nllToys=goodnessVals('%s/goodtoys.root'%options.odir)
    lPass=0
    for val in nllToys:
        if nllBase[0] > val:
            lPass+=1
    print "GoodnessOfFit p-value",float(lPass)/float(len(nllToys))
    plotftest(nllToys,nllBase[0],float(lPass)/float(len(nllToys)),iLabel,options)
    return float(lPass)/float(len(nllToys))

def bias(base,alt,ntoys,mu,iLabel):
    exec_me('combine -M GenerateOnly     %s --rMax 20 --rMin -20 -t %i --expectSignal %i --saveToys ' % (alt,ntoys,mu))
    exec_me('combine -M MaxLikelihoodFit %s --rMax 20 --rMin -20 -t %i --saveNLL --toysFile higgsCombineTest.GenerateOnly.mH120.123456.root'  % (base,ntoys))
    exec_me('rm  higgsCombineTest.MaxLikelihoodFit.mH120.123456.root')
    exec_me('mv  mlfit.root toys.root')
    plotgaus("toys.root",mu,"pull"+iLabel)

def fit(base,options):
    exec_me('combine -M MaxLikelihoodFit %s -v 2 --freezeNuisances tqqeffSF,tqqnormSF --rMin=-20 --rMax=20 --saveNormalizations --plot --saveShapes --saveWithUncertainties --minimizerTolerance 0.001 --minimizerStrategy 2'%base)
    exec_me('mv mlfit.root %s/'%options.odir)
    exec_me('mv higgsCombineTest.MaxLikelihoodFit.mH120.root %s/'%options.odir)
    
def limit(base):
    exec_me('combine -M Asymptotic %s  ' % base)
    exec_me('mv higgsCombineTest.Asymptotic.mH120.root limits.root')
    #exec_me('mv higgsCombineTest.Asymptotic.mH120.123456.root limits.root')

def plotmass(base,mass):
    exec_me('combine -M MaxLikelihoodFit %s --saveWithUncertainties --saveShapes' % base)
    exec_me('cp ../plot.py .')
    #exec_me('cp ../tdrstyle.py .')
    exec_me('python plot.py --mass %s' % str(mass))

def setup(iLabel,mass,iBase,iRalph):
    #exec_me('mkdir %s' % iLabel)
    exec_me('sed "s@XXX@%s@g" card_%s_tmp2.txt > %s/card_%s.txt' %(mass,iBase,iLabel,iBase))
    exec_me('cp %s*.root %s' % (iBase,iLabel))
    exec_me('cp %s*.root %s' % (iRalph,iLabel))
    #os.chdir (iLabel)

def setupMC(iLabel,mass,iBase):
    exec_me('mkdir %s' % iLabel)
    exec_me('sed "s@XXX@%s@g" mc_tmp2.txt > %s/mc.txt' %(mass,iLabel))
    exec_me('cp %s*.root %s' % (iBase,iLabel))
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
        exec_me('chmod +x %s' % os.path.abspath(sub_file.name))
        exec_me('bsub -q 8nh -o out.%%J %s' % (os.path.abspath(sub_file.name)))

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-m','--mass'   ,action='store',type='int',dest='mass'   ,default=125, help='mass')
    parser.add_option('-n','--n' ,action='store',type='int',dest='n'   ,default=5*20, help='number of bins')
    parser.add_option('--p1' ,action='store',type='int',dest='p1'   ,default=9, help='number of parameters for default datacard (p1 > p2)')
    parser.add_option('--p2' ,action='store',type='int',dest='p2'   ,default=12, help='number of parameters for alternative datacard (p2 > p1)')
    parser.add_option('-t','--toys'   ,action='store',type='int',dest='toys'   ,default=200, help='number of toys')
    parser.add_option('--sig'    ,action='store',type='int',dest='sig'    ,default=1 ,help='sig')
    parser.add_option('-d','--datacard'   ,action='store',type='string',dest='datacard'   ,default='card_rhalphabet.txt', help='datacard name')
    parser.add_option('--datacard-alt'   ,action='store',type='string',dest='datacardAlt'   ,default='card_rhalphabet_alt.txt', help='alternative datacard name')
    parser.add_option('-M','--method'   ,dest='method'   ,default='GoodnessOfFit', 
                      choices=['GoodnessOfFit','FTest','Asymptotic','Bias','MaxLikelihoodFit'],help='combine method to use')
    parser.add_option('-a','--algo'   ,dest='algo'   ,default='saturated', 
                      choices=['saturated','KS'],help='GOF algo  to use')
    parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots and output toys', metavar='odir')
    parser.add_option('--just-plot', action='store_true', dest='justPlot', default=False, help='just plot')
    parser.add_option('--data', action='store_true', dest='isData', default=False, help='is data')
    parser.add_option('-l','--lumi'   ,action='store',type='float',dest='lumi'   ,default=36.4, help='lumi')
    parser.add_option('-r','--r',dest='r', default=0 ,type='float',help='default value of r')
    parser.add_option('--rMin',dest='rMin', default=-20 ,type='float',help='minimum of r (signal strength) in profile likelihood plot')
    parser.add_option('--rMax',dest='rMax', default=20,type='float',help='maximum of r (signal strength) in profile likelihood plot')  
    parser.add_option('--freezeNuisances'   ,action='store',type='string',dest='freezeNuisances'   ,default='None', help='freeze nuisances')
    parser.add_option('--dry-run',dest="dryRun",default=False,action='store_true',
                  help="Just print out commands to run")    


    (options,args) = parser.parse_args()

    import tdrstyle
    tdrstyle.setTDRStyle()
    
    r.gStyle.SetOptStat(0)
    r.gStyle.SetOptFit(0)
    r.gStyle.SetOptTitle(0)
    r.gStyle.SetPaintTextFormat("1.2g")
    r.gROOT.SetBatch()
    r.RooMsgService.instance().setGlobalKillBelow(r.RooFit.FATAL)

    #setupMC('ZQQ_'+str(options.mass),options.mass,"mc")
    #setup('ZQQ_'+str(options.mass),options.mass,"ralpha","base")
    #os.chdir ('ZQQ_'+str(options.mass))
    #generate(options.mass,options.toys)

    #limit('combined.txt')
    #goodness('card_ralpha.txt',options.toys,"goodness"+str(options.mass))
    #bias('combined.txt','combined.txt',options.toys,options.sig,"fitbase"+str(options.mass))
    #plotmass('card_ralpha.txt',options.mass)


    #ftest('card_rhalphabet_r2p2.txt','card_rhalphabet_r3p2.txt',1000,'ftest_r2p2_v_r3p2')

    ## nllBase=nllDiff("base1.root","base2.root",p1=11,p2=8)
    ## nllToys=nllDiff("toys1.root","toys2.root",p1=11,p2=8)
    ## lPass=0
    ## for val in nllToys:
    ##     print val,nllBase[0]
    ##     if val < nllBase[0]:
    ##         lPass+=1
    ## print "ftest prob",float(lPass)/float(len(nllToys))
    ## plotftest(nllToys,nllBase[0],float(lPass)/float(len(nllToys)),'ftest_r2p2_v_r3p2')

    if options.method=='GoodnessOfFit':
        iLabel= 'goodness_%s'%(options.datacard.split('/')[-1].replace('.txt',''))
        goodness(options.datacard, options.toys, iLabel, options)

    elif options.method=='MaxLikelihoodFit':
        fit(options.datacard,options)

    elif options.method=='FTest':
        iLabel= 'ftest_%s_vs_%s'%(options.datacard.split('/')[-1].replace('.txt',''),options.datacardAlt.split('/')[-1].replace('.txt',''))
        ftest(options.datacard, options.datacardAlt, options.toys, iLabel, options)
