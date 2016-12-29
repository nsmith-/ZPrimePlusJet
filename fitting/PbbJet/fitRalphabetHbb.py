#!/usr/bin/env python
import ROOT as rt,sys,math,os
import numpy as np
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
#rt.gSystem.Load("~/Dropbox/RazorAnalyzer/python/lib/libRazorRun2.so")
rt.gSystem.Load(os.getenv('CMSSW_BASE')+'/lib/'+os.getenv('SCRAM_ARCH')+'/libHiggsAnalysisCombinedLimit.so')
rt.gInterpreter.GenerateDictionary("std::pair<std::string, RooDataHist*>", "map;string;RooDataHist.h")
rt.gInterpreter.GenerateDictionary("std::map<std::string, RooDataHist*>", "map;string;RooDataHist.h")
rt.RooRandom.randomGenerator().SetSeed(1988)

# including other directories
sys.path.insert(0, '../.')
from tools import *
from RootIterator import RootIterator

from array import array


def reset(w,fr):
    for p in RootIterator(fr.floatParsFinal()):
        w.var(p.GetName()).setVal(p.getVal())
        w.var(p.GetName()).setError(p.getError())
    return True

def main(options,args):

    idir = options.idir
    odir = options.odir
    lumi = options.lumi
    npoints = 20
    printYields = True
    
    nBins = 23
    msdMin = 40.
    msdMax = 201.    
    pt_binBoundaries = [500,550,600,675,800,1000]
    
    fbase = rt.TFile.Open(idir+"/base.root")
    fralphabase = rt.TFile.Open(idir+"/ralphabase.root")

    categories = ['pass_cat1','pass_cat2','pass_cat3','pass_cat4','pass_cat5','fail_cat1','fail_cat2','fail_cat3','fail_cat4','fail_cat5']
    
    bkgs = ['qcd','wqq','zqq','tqq']
    sigs = ['hqq125','zhqq125','whqq125','vbfhqq125','tthqq125']
    
    wbase = {}
    wralphabase = {}
    for cat in categories:
        wbase[cat] = fbase.Get('w_%s'%cat)
        wralphabase[cat] = fralphabase.Get('w_%s'%cat)
    
    w = rt.RooWorkspace('w')
    w.factory('r[1.,%f,20.]'%options.rMin)
    x = wbase[categories[0]].var('x')
    rooCat = rt.RooCategory('cat','cat')
       
    #r = rt.RooRealVar('r','r,',1.,0.,20.)
    r = w.var('r')
    epdf_b = {} 
    epdf_s = {}
    datahist = {}
    histpdf = {}
    histpdfnorm = {}
    data = {}
    signorm = {}
    for cat in categories:
        rooCat.defineType(cat)
        
    for cat in categories:        
        norms_b = rt.RooArgList()
        norms_s = rt.RooArgList()
        ## lBins = rt.RooArgList()
        ## for iMsdBin in range(1, nBins+1):
        ##     if 'fail' in cat:
        ##         p = wralphabase[cat].var('qcd_%s_Bin%i'%(cat,iMsdBin))
        ##     else:
        ##         p = wralphabase[cat].function('qcd_%s_Bin%i'%(cat,iMsdBin))
        ##     if options.fitRegion=='Low,High' and iMsdBin in [11,12,13]:
        ##         continue
        ##     else:
        ##         lBins.add(p)
        ## lN = rt.RooAddition('qcd_%s_newnorm'%cat,'qcd_%s_newnorm'%cat,lBins)
        ## norms_b.add(lN)
        ## norms_s.add(lN)
        norms_b.add(wralphabase[cat].function('qcd_%s_norm'%cat))
        norms_s.add(wralphabase[cat].function('qcd_%s_norm'%cat))
        pdfs_b = rt.RooArgList()
        pdfs_s = rt.RooArgList()
        pdfs_b.add(wralphabase[cat].pdf('qcd_%s'%cat))
        pdfs_s.add(wralphabase[cat].pdf('qcd_%s'%cat))

        data[cat] = wbase[cat].data('data_obs_%s'%cat)
        for proc in (bkgs+sigs):
            if proc=='qcd': continue

            datahist['%s_%s'%(proc,cat)] = wbase[cat].data('%s_%s'%(proc,cat))
            histpdf['%s_%s'%(proc,cat)] = rt.RooHistPdf('histpdf_%s_%s'%(proc,cat),
                                                        'histpdf_%s_%s'%(proc,cat),
                                                        rt.RooArgSet(wbase[cat].var('x')),
                                                        datahist['%s_%s'%(proc,cat)])
            getattr(w,'import')(datahist['%s_%s'%(proc,cat)],rt.RooFit.RecycleConflictNodes())
            getattr(w,'import')(histpdf['%s_%s'%(proc,cat)],rt.RooFit.RecycleConflictNodes())
            if 'hqq125' in proc:
                # signal
                signorm['%s_%s'%(proc,cat)] = rt.RooRealVar('signorm_%s_%s'%(proc,cat),
                                                            'signorm_%s_%s'%(proc,cat),
                                                            datahist['%s_%s'%(proc,cat)].sumEntries(),
                                                            0,10.*datahist['%s_%s'%(proc,cat)].sumEntries())
                signorm['%s_%s'%(proc,cat)].setConstant(True)                
                getattr(w,'import')(signorm['%s_%s'%(proc,cat)],rt.RooFit.RecycleConflictNodes())
                histpdfnorm['%s_%s'%(proc,cat)] = rt.RooFormulaVar('histpdfnorm_%s_%s'%(proc,cat),
                                                                   '@0*@1',rt.RooArgList(r,signorm['%s_%s'%(proc,cat)]))
                pdfs_s.add(histpdf['%s_%s'%(proc,cat)])
                norms_s.add(histpdfnorm['%s_%s'%(proc,cat)])
            else:
                # background
                histpdfnorm['%s_%s'%(proc,cat)] = rt.RooRealVar('histpdfnorm_%s_%s'%(proc,cat),
                                                                'histpdfnorm_%s_%s'%(proc,cat),
                                                                datahist['%s_%s'%(proc,cat)].sumEntries(),
                                                                0,10.*datahist['%s_%s'%(proc,cat)].sumEntries())
                histpdfnorm['%s_%s'%(proc,cat)].setConstant(True)
                getattr(w,'import')(histpdfnorm['%s_%s'%(proc,cat)])
                pdfs_b.add(histpdf['%s_%s'%(proc,cat)])
                pdfs_s.add(histpdf['%s_%s'%(proc,cat)])
                norms_b.add(histpdfnorm['%s_%s'%(proc,cat)])
                norms_s.add(histpdfnorm['%s_%s'%(proc,cat)])
            

        epdf_b[cat] = rt.RooAddPdf('epdf_b_'+cat,'epdf_b_'+cat,pdfs_b,norms_b)
        epdf_s[cat] = rt.RooAddPdf('epdf_s_'+cat,'epdf_s_'+cat,pdfs_s,norms_s)

        getattr(w,'import')(epdf_b[cat],rt.RooFit.RecycleConflictNodes())
        getattr(w,'import')(epdf_s[cat],rt.RooFit.RecycleConflictNodes())

    #arguments = ["data_obs","data_obs",rt.RooArgList(x),rt.RooFit.Index(rooCat)]
    arguments = ["data_obs","data_obs",rt.RooArgList(x),rooCat]
    
    m = rt.std.map('string, RooDataHist*')()
    for cat in categories:
        m.insert(rt.std.pair('string, RooDataHist*')(cat, data[cat]))
        #arguments.append(rt.RooFit.Import(cat,data[cat]))
    arguments.append(m)
        
    combData = getattr(rt,'RooDataHist')(*arguments)
    
    
    simPdf_b = rt.RooSimultaneous('simPdf_b','simPdf_b',rooCat)
    simPdf_s = rt.RooSimultaneous('simPdf_s','simPdf_s',rooCat)
    for cat in categories:
        simPdf_b.addPdf(epdf_b[cat],cat)    
        simPdf_s.addPdf(epdf_s[cat],cat)

    r.setVal(0.)    

    getattr(w,'import')(simPdf_b,rt.RooFit.RecycleConflictNodes())
    #getattr(w,'import')(simPdf_s,rt.RooFit.RecycleConflictNodes())
    getattr(w,'import')(combData,rt.RooFit.RecycleConflictNodes())

    w.Print('v')
    simPdf_b = w.pdf('simPdf_b')
    #simPdf_s = w.pdf('simPdf_s')
    combData = w.data('data_obs')
    x = w.var('x')
    rooCat = w.cat('cat')
    r = w.var('r')
    CMS_set = rt.RooArgSet()
    CMS_set.add(rooCat)
    CMS_set.add(x)
    
    iBin = -1
    if printYields:
        csvFile = open(odir+'/yields.csv','w')
        csvOutput = "cat,pT range,msd range,signal yield (S),background yield from MC (B),S/B,S/sqrt(B)"
        for cat in categories:
            catNum = int(cat.replace('pass_cat','').replace('fail_cat',''))
            ptBinMin = pt_binBoundaries[catNum-1]
            ptBinMax = pt_binBoundaries[catNum]
            for iMsdBin in range(0, nBins):
                iBin+=1
                signal = 0
                msdBinMin = float(msdMin+iMsdBin*(msdMax-msdMin)/nBins)
                msdBinMax = float(msdMin+(iMsdBin+1)*(msdMax-msdMin)/nBins)
                mc = data[cat].sumEntries('x>= %f && x<%f'%(msdBinMin,msdBinMax ))
                for sig in sigs:
                    signal += datahist['%s_%s'%(sig,cat)].sumEntries('x>= %f && x<%f'%(msdBinMin,msdBinMax ))
                print "%s,%i-%i,%.2f-%.2f,%f,%f,=D%i/E%i,=D%i/sqrt(E%i)" % (cat, ptBinMin, ptBinMax, msdBinMin, msdBinMax, signal,mc,iBin+2,iBin+2,iBin+2,iBin+2)                    
                csvOutput += "\n%s,%i-%i,%.2f-%.2f,%f,%f,=D%i/E%i,=D%i/sqrt(E%i)" % (cat, ptBinMin, ptBinMax, msdBinMin, msdBinMax, signal,mc,iBin+2,iBin+2,iBin+2,iBin+2)
        csvFile.write(csvOutput)
        csvFile.close()
        print ""
        print "yields written into %s/%s"%(odir,'yields.csv')
            
    ## w.var('r0p1').setConstant(True)
    ## w.var('r0p2').setConstant(True)
    ## w.var('r1p0').setConstant(True)
    ## w.var('r1p1').setConstant(True)
    ## w.var('r1p2').setConstant(True)
    ## w.var('r2p0').setConstant(True)
    ## w.var('r2p1').setConstant(True)
    ## w.var('r2p2').setConstant(True)
    ## w.var('qcdeff').setConstant(True)
            
    opt = rt.RooLinkedList()
    opt.Add(rt.RooFit.CloneData(False))
    ## if options.fitRegion!='Full':
    ##     opt.Add(rt.RooFit.Range(options.fitRegion))
    ## if options.fitRegion=='Low,High':
    ##     for cat in categories:
    ##         if 'pass' in cat: continue
    ##         w.var('qcd_%s_Bin11'%cat).setConstant(True)
    ##         w.var('qcd_%s_Bin12'%cat).setConstant(True)
    ##         w.var('qcd_%s_Bin13'%cat).setConstant(True)
    ##         w.var('qcd_%s_Bin11'%cat).setVal(0)
    ##         w.var('qcd_%s_Bin12'%cat).setVal(0)
    ##         w.var('qcd_%s_Bin13'%cat).setVal(0)
    allParams = simPdf_b.getParameters(combData)
    rt.RooStats.RemoveConstantParameters(allParams)            
    opt.Add(rt.RooFit.Constrain(allParams))

    
    #nll = simPdf_s.createNLL(combData,opt)
    nll = simPdf_b.createNLL(combData,opt)
    m2 = rt.RooMinimizer(nll)
    m2.setStrategy(2)
    m2.setMaxFunctionCalls(100000)
    m2.setMaxIterations(100000)
    m2.setPrintLevel(-1)
    m2.setPrintEvalErrors(-1)
    m2.setEps(1e-5)
    m2.optimizeConst(2)

    migrad_status = m2.minimize('Minuit2','migrad')
    improve_status = m2.minimize('Minuit2','improve')
    hesse_status = m2.minimize('Minuit2','hesse')
    fr = m2.save()
    fr.Print('v')
    
    minNll = fr.minNll()
    rBestFit = r.getVal()

    r.setVal(0)
    
    asimov = simPdf_b.generateBinned(CMS_set,rt.RooFit.Asimov(),rt.RooFit.Name('central'))
        
    frame = {}
    h_data = {}
    h_fit = {}
    dataCat = {}
    asimovCat = {}
    for cat in categories:
        rooCat.setLabel(cat)
        dataCat[cat] = combData.reduce(rt.RooFit.Cut('cat==cat::%s'%cat))
        asimovCat[cat] = asimov.reduce(rt.RooFit.Cut('cat==cat::%s'%cat))
        h_data[cat] = dataCat[cat].createHistogram('h_data_%s'%cat,x)
        h_fit[cat] = asimovCat[cat].createHistogram('h_fit_%s'%cat,x)
        h_data[cat].SetMarkerSize(0.7)
        h_fit[cat].SetLineWidth(2)
        h_fit[cat].SetLineColor(rt.kBlue)
        h_fit[cat].SetMarkerStyle(0)
        h_fit[cat].SetMarkerSize(0)
        h_fit[cat].SetMarkerColor(rt.kBlue)
        ## frame[cat] = x.frame(rt.RooFit.Title(cat),rt.RooFit.Range(40,201))
        ## combData.plotOn(frame[cat],rt.RooFit.Cut('cat==cat::%s'%cat),rt.RooFit.DataError(rt.RooAbsData.Poisson))
        ## simPdf_b.plotOn(frame[cat],rt.RooFit.Slice(rooCat,cat),
        ##                 rt.RooFit.ProjWData(rt.RooArgSet(rooCat),combData))
        ## simPdf_b.plotOn(frame[cat],rt.RooFit.Slice(rooCat,cat),
        ##                 rt.RooFit.Components('qcd_%s'%cat),rt.RooFit.ProjWData(rt.RooArgSet(rooCat),combData),
        ##                 rt.RooFit.LineStyle(rt.kDashed))      
        ## simPdf_b.plotOn(frame[cat],rt.RooFit.Slice(rooCat,cat),
        ##                 rt.RooFit.Components('wqq_%s'%cat),rt.RooFit.ProjWData(rt.RooArgSet(rooCat),combData),
        ##                 rt.RooFit.LineStyle(3))          
        ## simPdf_b.plotOn(frame[cat],rt.RooFit.Slice(rooCat,cat),
        ##                 rt.RooFit.Components('zqq_%s'%cat),rt.RooFit.ProjWData(rt.RooArgSet(rooCat),combData),
        ##                 rt.RooFit.LineStyle(4))          
        ## simPdf_b.plotOn(frame[cat],rt.RooFit.Slice(rooCat,cat),
        ##                 rt.RooFit.Components('tqq_%s'%cat),rt.RooFit.ProjWData(rt.RooArgSet(rooCat),combData),
        ##                 rt.RooFit.LineStyle(5))          
        ## simPdf_s.plotOn(frame[cat],rt.RooFit.Slice(rooCat,cat),
        ##                 rt.RooFit.Components('histpdf_hqq125_%s'%cat),rt.RooFit.ProjWData(rt.RooArgSet(rooCat),combData),
        ##                 rt.RooFit.LineColor(rt.kRed))
        ## simPdf_s.plotOn(frame[cat],rt.RooFit.Slice(rooCat,cat),
        ##                 rt.RooFit.Components('histpdf_whqq125_%s'%cat),rt.RooFit.ProjWData(rt.RooArgSet(rooCat),combData),
        ##                 rt.RooFit.LineColor(rt.kViolet),rt.RooFit.LineStyle(2))
        ## simPdf_s.plotOn(frame[cat],rt.RooFit.Slice(rooCat,cat),
        ##                 rt.RooFit.Components('histpdf_tthqq125_%s'%cat),rt.RooFit.ProjWData(rt.RooArgSet(rooCat),combData),
        ##                 rt.RooFit.LineColor(rt.kBlack),rt.RooFit.LineStyle(3))
        ## simPdf_s.plotOn(frame[cat],rt.RooFit.Slice(rooCat,cat),
        ##                 rt.RooFit.Components('histpdf_zhqq125_%s'%cat),rt.RooFit.ProjWData(rt.RooArgSet(rooCat),combData),
        ##                 rt.RooFit.LineColor(rt.kGreen),rt.RooFit.LineStyle(5))        
        #histpdf['hqq125_%s'%cat].plotOn(frame[cat],rt.RooFit.LineColor(rt.kRed))
        #histpdf['whqq125_%s'%cat].plotOn(frame[cat],rt.RooFit.LineColor(rt.kViolet),rt.RooFit.LineStyle(2))
        #histpdf['tthqq125_%s'%cat].plotOn(frame[cat],rt.RooFit.LineColor(rt.kBlack),rt.RooFit.LineStyle(3))
        #histpdf['vbfhqq125_%s'%cat].plotOn(frame[cat],rt.RooFit.LineColor(rt.kBlue),rt.RooFit.LineStyle(4))
        #histpdf['zhqq125_%s'%cat].plotOn(frame[cat],rt.RooFit.LineColor(rt.kGreen),rt.RooFit.LineStyle(5))

    r.setVal(rBestFit)
    c = rt.TCanvas('c','c',600,300)
    for i in range(1,5+1):
        c.Clear() 
        c.Divide(2)
        c.cd(1)
        h_data['fail_cat%i'%i].Draw('pez')
        h_fit['fail_cat%i'%i].Draw("histsame")
        #rt.gPad.SetLogy()
        #frame['fail_cat%i'%i].GetYaxis().SetTitleOffset(1.4)
        #frame['fail_cat%i'%i].Draw()
        #frame['fail_cat%i'%i].SetMinimum(0.1)
        #frame['fail_cat%i'%i].SetMaximum(2e5)
        c.cd(2)
        h_data['pass_cat%i'%i].Draw('pez')
        h_fit['pass_cat%i'%i].Draw("histsame")
        #rt.gPad.SetLogy()
        #frame['pass_cat%i'%i].GetYaxis().SetTitleOffset(1.4)
        #frame['pass_cat%i'%i].Draw()
        #frame['pass_cat%i'%i].SetMinimum(0.1)
        #frame['pass_cat%i'%i].SetMaximum(2e5)
        c.Print(odir+'/c%i.pdf'%i)
        c.Print(odir+'/c%i.C'%i)


    sys.exit()
    poi = rt.RooArgSet(r)
    pll = nll.createProfile(poi)
    n2ll = rt.RooFormulaVar("n2ll","2*@0-2*%f"%minNll,rt.RooArgList(nll))
    p2ll = n2ll.createProfile(poi)
    
    print "signal+background nll = %f on data at r = %f"%(minNll,rBestFit)
    
    xs, ys = np.linspace(options.rMin, options.rMax, npoints + 1), []    
    for xi in xs:
        r.setVal(xi)
        r.setConstant(True)
        ys.append(2.*nll.getVal() - 2.*minNll)
    xp, yp = np.linspace(options.rMin, options.rMax, npoints + 1), []
    for xi in xp:        
        r.setVal(xi)
        r.setConstant(True)
        m2.minimize('Minuit2','migrad')
        m2.minimize('Minuit2','improve')     
        if nll.getVal() - minNll < 0:
            reset(w,fr)
            r.setVal(xi)
            r.setConstant(True)
            m2.minimize('Minuit2','migrad')
            m2.minimize('Minuit2','improve')
        yp.append(2.*nll.getVal() - 2.*minNll)
        
    gr_s = rt.TGraph(len(xs), array('f', xs), array('f', ys))
    gr_s.SetLineStyle(2)
    gr_s.SetLineColor(rt.kBlue)
    gr_s.SetLineWidth(3)
    gr_s.SetName("n2ll_data")
    
    gr_p = rt.TGraph(len(xp), array('f', xp), array('f', yp))
    gr_p.SetLineColor(rt.kBlack)
    gr_p.SetLineWidth(3)
    gr_p.SetName("p2ll_data")
    
    rFrame = r.frame(rt.RooFit.Bins(npoints),rt.RooFit.Range(options.rMin,options.rMax),rt.RooFit.Title("r frame (data)"))
    rFrame.SetMinimum(0)
    rFrame.SetMaximum(6)

    #n2ll.plotOn(rFrame,rt.RooFit.ShiftToZero(),rt.RooFit.LineStyle(2),rt.RooFit.Name("n2ll_data"))
    #p2ll.plotOn(rFrame,rt.RooFit.LineColor(rt.kBlack),rt.RooFit.Name("p2ll_data"),rt.RooFit.Precision(-1))
    rFrame.addObject(gr_s, 'L')
    rFrame.addObject(gr_p, 'L')

    tlines = []
    cl = 0.95
    crossing = rt.TMath.Power(rt.Math.normal_quantile(1-0.5*(1-cl), 1.0),2)
    tline = rt.TLine(options.rMin,crossing,options.rMax,crossing)
    tline.SetLineColor(rt.kRed)
    tline.SetLineWidth(2)
    tlines.append(tline)
    
    rLimit = -1
    rLimitNoSys = -1
    for xi in range(0,1001):
        xr = xi*options.rMax/1000.
        if gr_p.Eval(xr) >= crossing and rLimit < 0:
            rLimit = xr
        if gr_s.Eval(xr) >= crossing and rLimitNoSys < 0:
            rLimitNoSys = xr

    tline = rt.TLine(rLimit,0,rLimit,crossing)
    tline.SetLineColor(rt.kBlack)
    tline.SetLineWidth(2)
    tlines.append(tline)
    tline = rt.TLine(rLimitNoSys,0,rLimitNoSys,crossing)
    tline.SetLineColor(rt.kBlue)
    tline.SetLineStyle(2)
    tline.SetLineWidth(2)
    tlines.append(tline)
            
    for tline in tlines:
        rFrame.addObject(tline,"")


    d = rt.TCanvas('d','d',500,400)
    rFrame.Draw()
    rFrame.SetMinimum(0)
    rFrame.SetMaximum(6)
    
    rFrame.SetXTitle("#mu (signal strength)")
    rFrame.SetYTitle("-2 #Delta log L(data)")
    rFrame.SetTitleSize(0.04,"X")
    rFrame.SetTitleOffset(0.85,"X")
    rFrame.SetTitleSize(0.04,"Y")
    rFrame.SetTitleOffset(0.8,"Y")
    rFrame.SetLabelSize(0.04,"X")
    rFrame.SetLabelSize(0.04,"Y")
    rFrame.SetNdivisions(505,"X")
    
    leg = rt.TLegend(0.7,0.15,0.89,0.3)
    leg.SetTextFont(42)
    leg.SetFillColor(rt.kWhite)
    leg.SetLineColor(rt.kWhite)
    leg.SetFillStyle(0)
    leg.AddEntry("p2ll_data", "stat + syst","l")
    leg.AddEntry("n2ll_data", "stat only","l")
    leg.Draw("same")
    
    tag1 = rt.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.04)
    tag2 = rt.TLatex(0.17,0.92,"CMS")
    tag2.SetNDC(); tag2.SetTextFont(62)
    tag3 = rt.TLatex(0.27,0.92,"Simulation Preliminary")
    tag3.SetNDC(); tag3.SetTextFont(52)
    tag2.SetTextSize(0.05); tag3.SetTextSize(0.04); tag1.Draw(); tag2.Draw(); tag3.Draw()
    
    d.Print(odir+"/deltaLL.pdf")
    d.Print(odir+"/deltaLL.C")

    print "stat+sys:  r < %f"%rLimit
    print "stat-only: r < %f"%rLimitNoSys



##-------------------------------------------------------------------------------------
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('--lumi', dest='lumi', type=float, default = 30,help='luminosity', metavar='lumi')
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
    parser.add_option('--pseudo', action='store_true', dest='pseudo', default =False,help='signal comparison', metavar='isData')
    parser.add_option('--rMin',dest='rMin', default=0 ,type='float',help='minimum of r (signal strength) in profile likelihood plot')
    parser.add_option('--rMax',dest='rMax', default=20,type='float',help='maximum of r (signal strength) in profile likelihood plot')    
    
    (options, args) = parser.parse_args()

    import tdrstyle
    tdrstyle.setTDRStyle()
    rt.gStyle.SetPadTopMargin(0.10)
    rt.gStyle.SetPadLeftMargin(0.16)
    rt.gStyle.SetPadRightMargin(0.10)
    rt.gStyle.SetPalette(1)
    rt.gStyle.SetPaintTextFormat("1.1f")
    rt.gStyle.SetOptFit(0000)
    rt.gROOT.SetBatch()

    main(options,args)
