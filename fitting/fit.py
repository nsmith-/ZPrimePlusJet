#!/usr/bin/env python
import ROOT as r,sys,math,array,os
from hist import hist
from optparse import OptionParser
from ROOT import std,RooDataHist
r.gROOT.Macro(os.path.expanduser('~/rootlogon.C'))
r.gInterpreter.GenerateDictionary("std::pair<std::string, RooDataHist*>", "map;string;RooDataHist.h")
r.gInterpreter.GenerateDictionary("std::map<std::string, RooDataHist*>", "map;string;RooDataHist.h")

fOutput="bern.root"
fNBins=68
#fNBins=30
fXMin=28
fXMax=240
f2D=False
fVars=[]
fDatas=[]
fFuncs=[]
fPars=[]

def end():
    if __name__ == '__main__':
        rep = ''
        while not rep in [ 'q', 'Q','a',' ' ]:
            rep = raw_input( 'enter "q" to quit: ' )
            if 1 < len(rep):
                rep = rep[0]

def parser():
    parser = OptionParser()
    parser.add_option('--card'    ,action='store_true',         dest='card'    ,default=False,       help='categorized bin by bin card fit')
    parser.add_option('--cat'     ,action='store_true',         dest='cat'     ,default=False,       help='categorized fit')
    parser.add_option('--1D'      ,action='store_true',         dest='fit1D'   ,default=False,       help='1D fit')
    parser.add_option('--2D'      ,action='store_true',         dest='fit2D'   ,default=False,       help='2D fit')
    parser.add_option('--fail'    ,action='store_true',         dest='fail'    ,default=False,       help='fit failing') 
    parser.add_option('--passfail',action='store_true',         dest='passfail',default=False,       help='fit pass and failng') 
    parser.add_option('--dummy',   action='store_true',         dest='dummy'   ,default=False,       help='dummy card') 
    parser.add_option('--input'   ,action='store',type='string',dest='input'   ,default='hists.root',help='input file')
    parser.add_option('--func'    ,action='store',type='int'   ,dest='func'    ,default=0           ,help='n=ith order of Bernstein')
    parser.add_option('--output'  ,action='store',type='string',dest='output'  ,default='bern.root' ,help='workspace output')
    parser.add_option('--xMin'    ,action='store',type='float' ,dest='xmin'    ,default=32          ,help='x-min')
    parser.add_option('--xMax'    ,action='store',type='float' ,dest='xmax'    ,default=300         ,help='x-max')
    parser.add_option('--nBins'   ,action='store',type='int'   ,dest='nbins'    ,default=67          ,help='n-bins')
    #parser.add_option('--xMax'    ,action='store',type='float' ,dest='xmax'    ,default=200         ,help='x-max')
    #parser.add_option('--nBins'   ,action='store',type='int'   ,dest='nbins'    ,default=38          ,help='n-bins')
    (options,args) = parser.parse_args()
    return options

def drawFrame(iFrame,iData,iFuncs):
    iData.plotOn(iFrame)
    iColor=50
    for pFunc in iFuncs:
        #pFunc.plotOn(iFrame,r.RooFit.LineColor(iColor),r.RooFit.LineStyle(iColor != 50+1),r.RooFit.Components(pFunc.GetName()),r.RooFit.ProjWData(iData))
        #pFunc.plotOn(iFrame,r.RooFit.LineColor(iColor),r.RooFit.LineStyle(iColor != 50+1),r.RooFit.ProjWData(iData))
        pFunc.plotOn(iFrame,r.RooFit.LineColor(iColor),r.RooFit.LineStyle(iColor != 50+1))#,r.RooFit.ProjWData(iData))
        iColor+=10

def draw(iVar,iData,iFuncs,iLabel="A"):
    lCan   = r.TCanvas(str(iLabel),str(iLabel),800,600)
    lFrame = iVar.frame()
    drawFrame(lFrame,iData,iFuncs)
    lFrame.Draw()
    lCan.Modified()
    lCan.Update()
    end()

def drawPF(iVar,iData,iFuncs,iLabel="A"):
    lCan   = r.TCanvas(str(iLabel),str(iLabel),800,600)
    lCan.Divide(2)
    lPFrame = iVar.frame(r.RooFit.Bins(30),r.RooFit.Title("pass"))
    lFFrame = iVar.frame(r.RooFit.Bins(30),r.RooFit.Title("fail"))
    drawFrame(lPFrame,iData[0],iFuncs[0])
    drawFrame(lFFrame,iData[1],iFuncs[1])
    lCan.cd(1)
    lPFrame.Draw()
    lCan.cd(2)
    lFFrame.Draw()
    lCan.Modified()
    lCan.Update()
    end()

def shift(iVar,iDataHist,iShift=5.):
    lInt    = iDataHist.createHistogram("x").Integral()
    lDM     = r.RooRealVar   ("Xdm","Xdm", 0.,-10,10)
    lShift  = r.RooFormulaVar("Xshift",iVar.GetName()+"-Xdm",r.RooArgList(iVar,lDM))  
    if f2D:
        lSPdf   = r.RooHistPdf(iDataHist.GetName()+"P",iDataHist.GetName()+"P", r.RooArgList(lShift,fVars[1]),r.RooArgList(iVar,fVars[1]),iDataHist,0)
    else:
        lSPdf   = r.RooHistPdf(iDataHist.GetName()+"P",iDataHist.GetName()+"P", r.RooArgList(lShift),r.RooArgList(iVar),iDataHist,0)
    lDM.setVal(iShift)
    lHUp   = lSPdf.createHistogram("x")
    lHUp.Scale(lInt)
    lUp    = r.RooDataHist(iDataHist.GetName()+"_scaleUp",iDataHist.GetName()+"_scaleUp", r.RooArgList(iVar),lHUp)
    lDM.setVal(-iShift)
    lHDown = lSPdf.createHistogram("x")
    lHDown.Scale(lInt)
    lDown  = r.RooDataHist(iDataHist.GetName()+"_scaleDown",iDataHist.GetName()+"_scaleDown", r.RooArgList(iVar),lHDown)
    return (lUp,lDown)

def smear(iVar,iDataHist,iScale=0.1):
    lDM     = r.RooRealVar("Xshift","Xshift", 1.,0.,2.)
    lVar    = iDataHist.createHistogram("x").GetMean()
    lInt    = iDataHist.createHistogram("x").Integral()
    lShift  = r.RooFormulaVar("Xsmear","("+iVar.GetName()+"-"+str(lVar)+")/Xshift+"+str(lVar),r.RooArgList(iVar,lDM))  
    if f2D:
        lHPdf   = r.RooHistPdf(iDataHist.GetName()+"S",iDataHist.GetName()+"S", r.RooArgList(lShift,fVars[1]),r.RooArgList(iVar,fVars[1]),iDataHist,0)
    else:
        lHPdf   = r.RooHistPdf(iDataHist.GetName()+"S",iDataHist.GetName()+"S", r.RooArgList(lShift),r.RooArgList(iVar),iDataHist,0)
    lDM.setVal(1.+iScale)
    lHUp = lHPdf.createHistogram("x")
    lHUp.Scale(lInt)
    lUp = r.RooDataHist(iDataHist.GetName()+"_smearUp",iDataHist.GetName()+"_smearUp", r.RooArgList(iVar),lHUp)    
    lDM.setVal(1.-iScale)
    lHDown = lHPdf.createHistogram("x")
    lHDown.Scale(lInt)
    lDown  = r.RooDataHist(iDataHist.GetName()+"_smearDown",iDataHist.GetName()+"_smearDown", r.RooArgList(iVar),lHDown)
    return [lUp,lDown]    

def workspace(iDatas,iFuncs,iVars,iCat="cat0",iShift=True):
    lW = r.RooWorkspace("w_"+str(iCat))
    #for var in iVars:
        #try:
            #var.setConstant(True)
        #except:
        #    pass
    for pData in iDatas:
        getattr(lW,'import')(pData,r.RooFit.RecycleConflictNodes())
    
    for pFunc in iFuncs:
        getattr(lW,'import')(pFunc,r.RooFit.RecycleConflictNodes())
        if iShift and pFunc.GetName().find("qq") > -1:
            (pFUp, pFDown)  = shift(iVars[0],pFunc,5.)
            (pSFUp,pSFDown) = smear(iVars[0],pFunc,0.05)
            getattr(lW,'import')(pFUp,  r.RooFit.RecycleConflictNodes())
            getattr(lW,'import')(pFDown,r.RooFit.RecycleConflictNodes())
            getattr(lW,'import')(pSFUp,  r.RooFit.RecycleConflictNodes())
            getattr(lW,'import')(pSFDown,r.RooFit.RecycleConflictNodes())
    
    if iCat.find("pass_cat1") == -1:
        lW.writeToFile(fOutput,False)
    else:
        lW.writeToFile(fOutput)

def writeHist(iH,iShift,iTemps,iBlanks=[]):  
    lOut = r.TFile(fOutput,"RECREATE")
    for pHist in iH:
        if pHist.GetName().find("data") > -1 and pHist.GetName().find("data_obs") < 0:
            pHist.SetName (pHist.GetName ().replace("data","data_obs"))
            pHist.SetTitle(pHist.GetTitle().replace("data","data_obs"))
        pHist.Write()
    iShift.setVal(5.)
    for pTemp in iTemps:
      lUp = pTemp.createHistogram("x")
      lUp.SetTitle(pTemp.GetName().replace("e_","_")+"_scaleUp")
      lUp.SetName (pTemp.GetName().replace("e_","_")+"_scaleUp")
      lUp.Write()
  
    iShift.setVal(-5.)
    for pTemp in iTemps:
      lDown = pTemp.createHistogram("x")
      lDown.SetTitle(pTemp.GetName().replace("e_","_")+"_scaleDown")
      lDown.SetName (pTemp.GetName().replace("e_","_")+"_scaleDown")
      lDown.Write()

def baseVars(i1D=False):
    global fNBins,fXMin,fXMax
    lMSD    = r.RooRealVar("x","x",fXMin,fXMax)
    lMSD.setBins(fNBins)
    lPt  = r.RooRealVar   ("pt","pt",500,1500)
    lRho = r.RooFormulaVar("rho","log(x*x/pt)",r.RooArgList(lMSD,lPt))
    lEff    = r.RooRealVar("veff"      ,"veff"      ,0.5 ,0.,1.0)
    lEffQCD = r.RooRealVar("qcdeff"    ,"qcdeff"   ,0.01,0.,10.)
    lDM     = r.RooRealVar("dm","dm", 0.,-10,10)
    lShift  = r.RooFormulaVar("shift",lMSD.GetName()+"-dm",r.RooArgList(lMSD,lDM))  
    lVars=[lMSD,lEff,lEffQCD,lDM,lShift]
    if not i1D:
        lVars.extend([lPt,lRho])
    fVars.extend([lMSD,lPt,lEff,lEffQCD,lDM])
    lPt .setBins(5)
    fPars.extend([lEffQCD,lDM,lEff])
    return lVars

def bestFit(iEffQCD,iDM,iVEff,iA0,iA1,iA2,iP1,iR1,iSigma):
    iA0.setVal(0.486)
    iA1.setVal(0.00326)
    iA2.setVal(-0.0000237)
    iP1.setVal(-0.00169)
    iR1.setVal(0.00939)
    iSigma.setVal(51.2)
    iEffQCD.setVal(0.0242)
    iDM.setVal(-2.3)
    iVEff.setVal(0.037)
    iA0.setConstant(True)
    iA1.setConstant(True)
    iA2.setConstant(True)
    iP1.setConstant(True)
    iSigma.setConstant(True)
    iEffQCD.setConstant(True)
    iDM.setConstant(True)
    iVEff.setConstant(True)
        
def command(iPt,iRho,iQCD,iVars,iNR=1,iNP=1,iNRNP=1):
    lPt  = r.RooConstVar("Var_Pt_" +str(iPt)+"_"+str(iRho), "Var_Pt_" +str(iPt)+"_"+str(iRho),(iPt-500))
    lRho = r.RooConstVar("Var_Rho_"+str(iPt)+"_"+str(iRho), "Var_Rho_"+str(iPt)+"_"+str(iRho),(iRho-2.5))
    lPtArray  = r.RooArgList()
    lRhoArray = r.RooArgList()
    lPtArray.add(iQCD)
    lNCount=0
    if iNP > 0:
        lPtArray.add(iVars[lNCount])
        lNCount=lNCount+1
    if iNP > 1:
        lPtArray.add(iVars[lNCount])
        lNCount=lNCount+1
    if iNP > 2:
        lPtArray.add(iVars[lNCount])
        lNCount=lNCount+1
    if iNP > 3:
        lPtArray.add(iVars[lNCount])
        lNCount=lNCount+1
        
    lPtPol = r.RooPolyVar("Var_PtPol_Bin_"+str(iPt)+"_"+str(iRho),"Var_PtPol_Bin_"+str(iPt)+"_"+str(iRho),lPt,lPtArray)
    lRhoArray.add(lPtPol)
    if iNR > 0:
        lTmpArray = r.RooArgList()
        lTmpArray.add(iVars[lNCount])
        lNCount=lNCount+1
        if iNRNP > 0:
            lTmpArray.add(iVars[lNCount])
            lNCount=lNCount+1
        if iNRNP > 1:
            lTmpArray.add(iVars[lNCount])
            lNCount=lNCount+1
        lRhoPol0 = r.RooPolyVar("Var_RhoPol0_Bin_"+str(iPt)+"_"+str(iRho),"Var_RhoPol0_Bin_"+str(iPt)+"_"+str(iRho),lPt,lTmpArray)
        fVars.append(lRhoPol0)
        lRhoArray.add(lRhoPol0)
    if iNR > 1:
        lTmpArray = r.RooArgList()
        lTmpArray.add(iVars[lNCount])
        lNCount=lNCount+1
        if iNRNP > 2:
            lTmpArray.add(iVars[lNCount])
            lNCount=lNCount+1
        if iNRNP > 3:
            lTmpArray.add(iVars[lNCount])
            lNCount=lNCount+1
        lRhoPol1 = r.RooPolyVar("Var_RhoPol1_Bin_"+str(iPt)+"_"+str(iRho),"Var_RhoPol1_Bin_"+str(iPt)+"_"+str(iRho),lPt,lTmpArray)
        fVars.append(lRhoPol1)
        lRhoArray.add(lRhoPol1)
    if iNR > 2:
        lTmpArray = r.RooArgList()
        lTmpArray.add(iVars[lNCount])
        lNCount=lNCount+1
        if iNRNP > 4:
            lTmpArray.add(iVars[lNCount])
            lNCount=lNCount+1
        if iNRNP > 5:
            lTmpArray.add(iVars[lNCount])
            lNCount=lNCount+1
        lRhoPol2 = r.RooPolyVar("Var_RhoPol2_Bin_"+str(iPt)+"_"+str(iRho),"Var_RhoPol2_Bin_"+str(iPt)+"_"+str(iRho),lPt,lTmpArray)
        fVars.append(lRhoPol2)
        lRhoArray.add(lRhoPol2)
    if iNR > 3:
        lTmpArray = r.RooArgList()
        lTmpArray.add(iVars[lNCount])
        lNCount=lNCount+1
        if iNRNP > 6:
            lTmpArray.add(iVars[lNCount])
            lNCount=lNCount+1
        if iNRNP > 7:
            lTmpArray.add(iVars[lNCount])
            lNCount=lNCount+1
        lRhoPol3 = r.RooPolyVar("Var_RhoPol3_Bin_"+str(iPt)+"_"+str(iRho),"Var_RhoPol2_Bin_"+str(iPt)+"_"+str(iRho),lPt,lTmpArray)
        fVars.append(lRhoPol3)
        lRhoArray.add(lRhoPol3)

    lRhoPol = r.RooPolyVar("Var_RhoPol_Bin_"+str(iPt)+"_"+str(iRho),"Var_RhoPol_Bin_"+str(iPt)+"_"+str(iRho),lRho,lRhoArray)
    fVars.extend([lPt,lRho,lPtPol,lRhoPol])
    return lRhoPol

def qcdFunc(iH,iVars,iBin="_cat0",iFunc=0,i1D=True,iPt=-1):
    lNTot   = r.RooRealVar   ("qcdnorm"+iBin,"qcdnorm"+iBin,(iH[0].Integral()+iH[1].Integral()),0.,3000.*(iH[0].Integral()+iH[1].Integral()))
    lNPass  = r.RooFormulaVar("fqpass"+iBin ,"qcdnorm"+iBin+"*(qcdeff)"  ,r.RooArgList(lNTot,iVars[2]))
    lNFail  = r.RooFormulaVar("fqfail"+iBin ,"qcdnorm"+iBin+"*(1-qcdeff)",r.RooArgList(lNTot,iVars[2]))
    lA0     = r.RooRealVar   ("a0"          ,"a0"          ,0.486,-1000.,1000.)          
    lA1     = r.RooRealVar   ("a1"          ,"a1"          ,0.0,-1  ,1.)
    lA2     = r.RooRealVar   ("a2"          ,"a2"          ,0.0,-0.1,0.1)
    lA3     = r.RooRealVar   ("a3"          ,"a3"          ,0.0,-0.1,0.1)
    lA4     = r.RooRealVar   ("a4"          ,"a4"          ,0.0,-0.1,0.1)
    lA5     = r.RooRealVar   ("a5"          ,"a5"          ,0.0,-0.1,0.1)
    lA6     = r.RooRealVar   ("a6"          ,"a6"          ,0.0,-0.1,0.1)
    lA7     = r.RooRealVar   ("a7"          ,"a7"          ,0.0,-0.1,0.1)
    lA8     = r.RooRealVar   ("a8"          ,"a8"          ,0.0,-0.1,0.1)
    lA9     = r.RooRealVar   ("a9"          ,"a9"          ,0.0,-0.1,0.1)
    lA10    = r.RooRealVar   ("a10"         ,"a10"         ,0.0,-0.1,0.1)
    lA11    = r.RooRealVar   ("a11"         ,"a11"         ,0.0,-0.1,0.1)
    lSigma1 = r.RooRealVar   ("sigma1"      ,"sigma1"      ,50,0,1000)
    lP1     = r.RooRealVar   ("p1" ,"p1", 0.0   ,-1.0  ,1.0)
    lP2     = r.RooRealVar   ("p2" ,"p2", 0.0   ,-0.001,0.001)
    lR1     = r.RooRealVar   ("r1" ,"r1", 0.0   ,-1.0 ,1.0)
    lR2     = r.RooRealVar   ("r2" ,"r2", 0.0   ,-0.1 ,0.1)
    if i1D:
        lFunc="1"
        lQFuncP1 = 0
        lQFuncF1 = 0
        if iFunc == 3:
            lQFuncP1 = r.RooBernstein("qcd_pass_"+iBin,"qcd_pass_"+iBin,iVars[0],r.RooArgList(lA0,lA1,lA2,lA3))
            lQFuncF1 = r.RooBernstein("qcd_fail_"+iBin,"qcd_fail_"+iBin,iVars[0],r.RooArgList(lA0,lA1,lA2,lA3))
        elif iFunc == 4:
            lQFuncP1 = r.RooBernstein("qcd_pass_"+iBin,"qcd_pass_"+iBin,iVars[0],r.RooArgList(lA0,lA1,lA2,lA3,lA4))
            lQFuncF1 = r.RooBernstein("qcd_fail_"+iBin,"qcd_fail_"+iBin,iVars[0],r.RooArgList(lA0,lA1,lA2,lA3,lA4))
        elif iFunc == 5:
            lQFuncP1 = r.RooBernstein("qcd_pass_"+iBin,"qcd_pass_"+iBin,iVars[0],r.RooArgList(lA0,lA1,lA2,lA3,lA4,lA5))
            lQFuncF1 = r.RooBernstein("qcd_fail_"+iBin,"qcd_fail_"+iBin,iVars[0],r.RooArgList(lA0,lA1,lA2,lA3,lA4,lA5))
        elif iFunc == 6:
            lQFuncP1 = r.RooBernstein("qcd_pass_"+iBin,"qcd_pass_"+iBin,iVars[0],r.RooArgList(lA0,lA1,lA2,lA3,lA4,lA5,lA6))
            lQFuncF1 = r.RooBernstein("qcd_fail_"+iBin,"qcd_fail_"+iBin,iVars[0],r.RooArgList(lA0,lA1,lA2,lA3,lA4,lA5,lA6))
        elif iFunc == 7:
            lQFuncP1 = r.RooBernstein("qcd_pass_"+iBin,"qcd_pass_"+iBin,iVars[0],r.RooArgList(lA0,lA1,lA2,lA3,lA4,lA5,lA6,lA7))
            lQFuncF1 = r.RooBernstein("qcd_fail_"+iBin,"qcd_fail_"+iBin,iVars[0],r.RooArgList(lA0,lA1,lA2,lA3,lA4,lA5,lA6,lA7))
        elif iFunc == 8:
            lQFuncP1 = r.RooBernstein("qcd_pass_"+iBin,"qcd_pass_"+iBin,iVars[0],r.RooArgList(lA0,lA1,lA2,lA3,lA4,lA5,lA6,lA7,lA8))
            lQFuncF1 = r.RooBernstein("qcd_fail_"+iBin,"qcd_fail_"+iBin,iVars[0],r.RooArgList(lA0,lA1,lA2,lA3,lA4,lA5,lA6,lA7,lA8))
        elif iFunc == 9:
            lArg = r.RooArgList(lA0,lA1,lA2,lA3,lA4,lA5,lA6,lA7,lA8) 
            lArg.add(lA9)
            lQFuncP1 = r.RooBernstein("qcd_pass_"+iBin,"qcd_pass_"+iBin,iVars[0],lArg)
            lQFuncF1 = r.RooBernstein("qcd_fail_"+iBin,"qcd_fail_"+iBin,iVars[0],lArg)
        elif iFunc == 10:
            lArg = r.RooArgList(lA0,lA1,lA2,lA3,lA4,lA5,lA6,lA7,lA8) 
            lArg.add(lA9)
            lArg.add(lA10)
            lQFuncP1 = r.RooBernstein("qcd_pass_"+iBin,"qcd_pass_"+iBin,iVars[0],lArg)
            lQFuncF1 = r.RooBernstein("qcd_fail_"+iBin,"qcd_fail_"+iBin,iVars[0],lArg)
        elif iFunc == 11:
            lArg = r.RooArgList(lA0,lA1,lA2,lA3,lA4,lA5,lA6,lA7,lA8) 
            lArg.add(lA9)
            lArg.add(lA10)
            lArg.add(lA11)
            lQFuncP1 = r.RooBernstein("qcd_pass_"+iBin,"qcd_pass_"+iBin,iVars[0],lArg)
            lQFuncF1 = r.RooBernstein("qcd_fail_"+iBin,"qcd_fail_"+iBin,iVars[0],lArg)
        elif iFunc == 2:
            lQFuncP1 = r.RooBernstein("qcd_pass_"+iBin,"qcd_pass_"+iBin,iVars[0],r.RooArgList(lA0,lA1,lA2))
            lQFuncF1 = r.RooBernstein("qcd_fail_"+iBin,"qcd_fail_"+iBin,iVars[0],r.RooArgList(lA0,lA1,lA2))
        elif iFunc == 1:
            lQFuncP1 = r.RooBernstein("qcd_pass_"+iBin,"qcd_pass_"+iBin,iVars[0],r.RooArgList(lA0,lA1))
            lQFuncF1 = r.RooBernstein("qcd_fail_"+iBin,"qcd_fail_"+iBin,iVars[0],r.RooArgList(lA0,lA1))
        else:
            lQFuncP1 = r.RooBernstein("qcd_pass_"+iBin,"qcd_pass_"+iBin,iVars[0],r.RooArgList(lA0))
            lQFuncF1 = r.RooBernstein("qcd_fail_"+iBin,"qcd_fail_"+iBin,iVars[0],r.RooArgList(lA0))
        if iPt > 0:
            iVars[5].setVal(iPt)
            lPFunc = command(lFunc,iPt,-1,-1,False,2,2)
            lFFunc = command(lFunc,iPt,-1,-1,True ,2,2)
            lQFuncP1.SetName("qcd_pass1_"+iBin)
            lQFuncF1.SetName("qcd_fail1_"+iBin)
            lQFuncP1.SetTitle("qcd_pass1_"+iBin)
            lQFuncF1.SetTitle("qcd_fail1_"+iBin)
            lQFuncP2 = r.RooGenericPdf("qcd_pass2_"+iBin,lPFunc,r.RooArgList(iVars[0],lP1,lR1,lP2,lR2))
            lQFuncF2 = r.RooGenericPdf("qcd_fail2_"+iBin,lFFunc,r.RooArgList(iVars[0],lP1,lR1,lP2,lR2))
            lQFuncP  = r.RooProdPdf("qcd_pass_"+iBin,"qcd_pass_"+iBin,lQFuncP1,lQFuncP2)
            lQFuncF  = r.RooProdPdf("qcd_fail_"+iBin,"qcd_fail_"+iBin,lQFuncF1,lQFuncF2)
            fFuncs.extend([lQFuncP1,lQFuncF1,lQFuncP2,lQFuncF2])
        else:
            lQFuncP = lQFuncP1
            lQFuncF = lQFuncF1
    else:
        lQFuncP = r.RooGenericPdf("qcd_pass_"+iBin,"("+lFunc+"*(1+p1*(pt-500)+r1*(rho-2.5))",r.RooArgList(iVars[0],lSigma1,lA0,lA1,lA2,lP1,iVars[5],lR1,iVars[6]))
        lQFuncF = r.RooGenericPdf("qcd_fail_"+iBin,"("+lFunc+"*(1-p1*(pt-500)-r1*(rho-2.5))",r.RooArgList(iVars[0],lSigma1,lA0,lA1,lA2,lP1,iVars[5],lR1,iVars[6]))
    lQCDP   = r.RooExtendPdf ("qcdpassE"+iBin,"qcdpass"+iBin,lQFuncP,lNPass)
    lQCDF   = r.RooExtendPdf ("qcdfailE"+iBin,"qcdfail"+iBin,lQFuncF,lNFail)
    lQCD    = [lQCDP,lQCDF,lQFuncP,lQFuncF]
    fVars.extend([lNTot,lA0,lA1,lA2,lR1,lSigma1,lNPass,lNFail,lP1,lR1,lR2,lP2,lA3,lA4,lA5,lA6,lA7,lA8,lA9,lA10,lA11])
    fFuncs.extend(lQCD)
    fPars.extend([lA0,lA1,lA2,lP1,lR1,lP2,lR2,lSigma1])
    lP1.setConstant(True)
    lR1.setConstant(True)
    return lQCD

def histFunc(iH,iVars,iLabel="w",iBin="_cat0",i1D=True):
    lNTot   = r.RooRealVar (iLabel+"norm"+iBin,iLabel+"norm"+iBin,(iH[0].Integral()+iH[1].Integral()),0.,5.*(iH[0].Integral()+iH[1].Integral()))
    lNPass  = r.RooFormulaVar(iLabel+"fpass"+iBin ,iLabel+"norm"+iBin+"*(veff)"  ,r.RooArgList(lNTot,iVars[1]))
    lNFail  = r.RooFormulaVar(iLabel+"fqail"+iBin ,iLabel+"norm"+iBin+"*(1-veff)",r.RooArgList(lNTot,iVars[1]))
    if i1D:
        lPData  = r.RooDataHist(iLabel+"_pass_"+iBin,iLabel+"_pass_"+iBin, r.RooArgList(iVars[0]),iH[0])
        lMData  = r.RooDataHist(iLabel+"_fail_"+iBin,iLabel+"_fail_"+iBin, r.RooArgList(iVars[0]),iH[1]) 
        lP      = r.RooHistPdf (iLabel+"passh"+iBin,iLabel+"passh"+iBin, r.RooArgList(iVars[4]),r.RooArgList(iVars[0]),lPData,0)
        lF      = r.RooHistPdf (iLabel+"failh"+iBin,iLabel+"failh"+iBin, r.RooArgList(iVars[4]),r.RooArgList(iVars[0]),lMData,0)
    else:
        lPData  = r.RooDataHist(iLabel+"_pass_" +iBin,iLabel+"_pass_"+iBin, r.RooArgList(iVars[0],iVars[5]),iH[0])
        lMData  = r.RooDataHist(iLabel+"_fail_" +iBin,iLabel+"_fail_"+iBin, r.RooArgList(iVars[0],iVars[5]),iH[1]) 
        lP      = r.RooHistPdf (iLabel+"passh" +iBin,iLabel+"passh"+iBin, r.RooArgList(iVars[4],iVars[5]),r.RooArgList(iVars[0],iVars[5]),lPData,0)
        lF      = r.RooHistPdf (iLabel+"failh" +iBin,iLabel+"failh"+iBin, r.RooArgList(iVars[4],iVars[5]),r.RooArgList(iVars[0],iVars[5]),lMData,0)
    lEP     = r.RooExtendPdf(iLabel+"_passe_" +iBin,iLabel+"pe" +iBin,lP,lNPass)
    lEF     = r.RooExtendPdf(iLabel+"_faile_" +iBin,iLabel+"fe" +iBin,lF,lNFail)
    lHist   = [lP,lF,lEP,lEF,lPData,lMData]
    fVars.extend([lNTot,lNPass,lNFail])
    fFuncs.extend(lHist)
    return lHist

def getSignals(iHP,iHF,iBin,iBase):
    lPSigs  = []
    lFSigs  = []
    lPHists = [] 
    lFHists = [] 
    lVars=[50,75,100,125,150,200,250,300]
    for i0 in range(0,len(lVars)):
        lPHists.append(iHP[i0+3])
        lFHists.append(iHF[i0+3])
    lPHist = hist(lVars,lPHists)
    lFHist = hist(lVars,lFHists)
    masses=[50,60,75,90,100,112,125,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290,300]
    for i0 in range(0,len(masses)):
        pHP   = lPHist.morph(masses[i0])
        pHF   = lFHist.morph(masses[i0])
        for i1 in range(0,len(lVars)):
            if lVars[i1] == masses[i0]:
                pHP=iHP[i1+3]
                pHF=iHF[i1+3]
        lSig = histFunc([pHP,pHF],iBase,"zqq"+str(masses[i0]),iBin)
        lPSigs.append(lSig[4])
        lFSigs.append(lSig[5])
    return (lPSigs,lFSigs)

def fit1D(iHP,iHF,iFail,iFunc=0,iBin="cat0"):
    lBase  = baseVars()
    if iFail:
        lData = r.RooDataHist("data_obs_"+iBin,"data_obs_"+iBin,r.RooArgList(lBase[0]),iHF[0])
    else:
        lData = r.RooDataHist("data_obs_"+iBin,"data_obs_"+iBin,r.RooArgList(lBase[0]),iHP[0])
    lW    = histFunc([iHP[1],iHF[1]],lBase,"wqq",iBin)
    lZ    = histFunc([iHP[2],iHF[2]],lBase,"zqq",iBin)
    lTT   = histFunc([iHP[len(iHP)-1],iHF[len(iHF)-1]],lBase,"tt" ,iBin)
    lQCD  = qcdFunc ([iHP[len(iHP)-2],iHF[len(iHF)-2]],lBase,iBin,iFunc)
    #lBase[0].setRange("R1",30,60)
    #lBase[0].setRange("R2",110,300)
    lTot  = r.RooAddPdf("tot"+iBin,"tot"+iBin,r.RooArgList(lQCD[0+iFail],lW[2+iFail]))#,lZ[2+iFail]))
    #lTot.fitTo(lData,r.RooFit.Extended())
    lTot.fitTo(lData,r.RooFit.Extended())#,r.RooFit.Minos())
    lHists=[lTT[4+iFail],lW[4+iFail],lZ[4+iFail],lQCD[0+iFail]]
    lHists.extend(getSignals(iHP,iHF,iBin,lBase)[iFail])
    workspace([lData],lHists,fVars,iBin)
    lFuncs=[lTot,lQCD[0+iFail]]#,lW[2+iFail],lZ[2+iFail]]
    draw(lBase[0],lData,lFuncs)
    
def fit1DPF(iHP,iHF,iFunc=0,iBin="cat0"):
    lCats = r.RooCategory("sample","sample") 
    lCats.defineType("pass",1) 
    lCats.defineType("fail",0) 
    lBase  = baseVars()
    lPData = r.RooDataHist("data_obs_pass_"+iBin,"data_obs_pass_"+iBin,r.RooArgList(lBase[0]),iHP[0])
    lFData = r.RooDataHist("data_obs_fail_"+iBin,"data_obs_fail_"+iBin,r.RooArgList(lBase[0]),iHF[0])
    lData  = r.RooDataHist("comb_data_obs","comb_data_obs",r.RooArgList(lBase[0]),r.RooFit.Index(lCats),r.RooFit.Import("pass",lPData),r.RooFit.Import("fail",lFData))
    lW    = histFunc([iHP[1],iHF[1]],lBase,"wqq",iBin)
    lZ    = histFunc([iHP[2],iHF[2]],lBase,"zqq",iBin)
    lQCD  = qcdFunc ([iHP[len(iHP)-2],iHF[len(iHF)-2]],lBase,iBin,iFunc)
    lTotP = r.RooAddPdf("tot_pass"+iBin,"tot_pass"+iBin,r.RooArgList(lQCD[0],lW[2],lZ[2]))
    lTotF = r.RooAddPdf("tot_fail"+iBin,"tot_fail"+iBin,r.RooArgList(lQCD[1]))#,lW[3],lZ[3]))
    lTot  = r.RooSimultaneous("tot","tot",lCats) 
    lTot.addPdf(lTotP,"pass") 
    lTot.addPdf(lTotF,"fail")     
    lTot.fitTo(lData,r.RooFit.Extended(),r.RooFit.Minos())
    lHists=[lW[4],lZ[4],lQCD[0],lW[5],lZ[5],lQCD[1]]
    lHists.extend(getSignals(iHP,iHF,iBin,lBase)[0])
    lHists.extend(getSignals(iHP,iHF,iBin,lBase)[1])
    lDatas=[lPData,lFData]
    workspace(lDatas,lHists,fVars,iBin)
    lPFuncs=[lTotP,lQCD[0]]#,lW[2],lZ[2]]
    lFFuncs=[lTotF,lQCD[1]]#,lW[3],lZ[3]]
    drawPF(lBase[0],[lPData,lFData],[lPFuncs,lFFuncs])
        
def fit2D(iHP,iHF,iFail,iBin="cat0"):
    lBase  = baseVars(False)
    if iFail:
        lData = r.RooDataHist("data_obs_"+iBin,"data_obs_"+iBin,r.RooArgList(lBase[0],lBase[5]),iHF[0])
    else:
        lData = r.RooDataHist("data_obs_"+iBin,"data_obs_"+iBin,r.RooArgList(lBase[0],lBase[5]),iHP[0])
    lW    = histFunc([iHP[1],iHF[1]],lBase,"wqq",iBin,False)
    lZ    = histFunc([iHP[2],iHF[2]],lBase,"zqq",iBin,False)
    lQCD  = qcdFunc ([iHP[3],iHF[3]],lBase,iBin,False)
    lTot  = r.RooAddPdf("tot"+iBin,"tot"+iBin,r.RooArgList(lQCD[0+iFail],lW[2+iFail],lZ[2+iFail]))
    #lTot.fitTo(lData,r.RooFit.Extended(),r.RooFit.Minos(),r.RooFit.ConditionalObservables(r.RooArgSet(lBase[5])))
    workspace([lData],[lW[4+iFail],lZ[4+iFail],lQCD[2+iFail]],fVars,iBin)
    writeHist(iHP,lBase[3],[lW[4+iFail],lZ[4+iFail],lQCD[2+iFail]])
    lFuncs=[lTot,lQCD[0+iFail]]#,lW[2+iFail],lZ[2+iFail]]
    draw(lBase[0],lData,lFuncs)

def fit2DPF(iHP,iHF,iBin="_cat0"):
    lBase  = baseVars(False)
    lCats = r.RooCategory("sample","sample") 
    lCats.defineType("pass",1) 
    lCats.defineType("fail",0) 
    lPData = r.RooDataHist("data_obs_pass_"+iBin,"data_obs_pass"+iBin,r.RooArgList(lBase[0],lBase[5]),iHP[0])
    lFData = r.RooDataHist("data_obs_fail_"+iBin,"data_obs_fail"+iBin,r.RooArgList(lBase[0],lBase[5]),iHF[0])
    lData  = r.RooDataHist("comb_data_obs","comb_data_obs",r.RooArgList(lBase[0],lBase[5]),r.RooFit.Index(lCats),r.RooFit.Import("pass",lPData),r.RooFit.Import("fail",lFData))
    lW    = histFunc([iHP[1],iHF[1]],lBase,"wqq",iBin,False)
    lZ    = histFunc([iHP[2],iHF[2]],lBase,"zqq",iBin,False)
    lQCD  = qcdFunc ([iHP[3],iHF[3]],lBase,iBin,False)
    lTotP = r.RooAddPdf("tot_pass"+iBin,"tot_pass"+iBin,r.RooArgList(lQCD[0],lW[2],lZ[2]))
    lTotF = r.RooAddPdf("tot_fail"+iBin,"tot_fail"+iBin,r.RooArgList(lQCD[1]))#,lW[3],lZ[3]))
    lTot  = r.RooSimultaneous("tot","tot",lCats) 
    lTot.addPdf(lTotP,"pass") 
    lTot.addPdf(lTotF,"fail")     
    #bestFit(fPars[0],fPars[1],fPars[2],fPars[3],fPars[4],fPars[5],fPars[6],fPars[7],fPars[8])
    lTot.fitTo(lData,r.RooFit.Extended(),r.RooFit.ConditionalObservables(r.RooArgSet(lBase[5])))
    workspace([lPData,lFData],[lW[4],lZ[4],lQCD[2],lW[5],lZ[5],lQCD[3]],fVars,iBin)
    lPFuncs=[lTotP,lQCD[0]]
    lFFuncs=[lTotF,lQCD[1]]
    drawPF(lBase[0],[lPData,lFData],[lPFuncs,lFFuncs])

def proj(iLabel,iBin,iH):
    global fNBins,fXMin,fXMax
    lH = r.TH1F(iH.GetName()+"_"+iLabel+iBin,iH.GetName()+"_"+iLabel+iBin,fNBins,fXMin,fXMax)
    for iM in range(1,iH.GetNbinsX()+1):
        if iH.GetXaxis().GetBinCenter(iM) < lH.GetXaxis().GetXmin() or iH.GetXaxis().GetBinCenter(iM) > lH.GetXaxis().GetXmax():
            continue
        lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),iH.GetBinContent(iM,int(iBin)))
    lH.SetDirectory(0)
    return lH
    
def cat(iCat,iHP,iHF,iBin,iBase,iPt,iFunc):
    iCat.defineType("pass"+iBin)
    iCat.defineType("fail"+iBin)
    lCats = r.RooCategory("Xsample","Xsample") 
    lCats.defineType("pass",1) 
    lCats.defineType("fail",0) 
    lPData = r.RooDataHist("data_obs_pass_"+iBin,"data_obs_pass_"+iBin,r.RooArgList(iBase[0]),iHP[0])
    lFData = r.RooDataHist("data_obs_fail_"+iBin,"data_obs_fail_"+iBin,r.RooArgList(iBase[0]),iHF[0])
    lData  = r.RooDataHist("comb_data_obs","comb_data_obs",r.RooArgList(iBase[0]),r.RooFit.Index(lCats),r.RooFit.Import("pass",lPData),r.RooFit.Import("fail",lFData))
    lW    = histFunc([iHP[1],iHF[1]],iBase,"wqq",iBin)
    lZ    = histFunc([iHP[2],iHF[2]],iBase,"zqq",iBin)
    lQCD  = qcdFunc ([iHP[len(iHP)-2],iHF[len(iHF)-2]],iBase,iBin,iFunc)#,True,iPt)
    lTotP = r.RooAddPdf("tot_pass"+iBin,"tot_pass"+iBin,r.RooArgList(lQCD[0]))#,lW[2],lZ[2]))
    lTotF = r.RooAddPdf("tot_fail"+iBin,"tot_fail"+iBin,r.RooArgList(lQCD[1]))#,lW[3],lZ[3]))
    lEWKP = r.RooAddPdf("ewk_pass"+iBin,"ewk_pass"+iBin,r.RooArgList(lW[2],lZ[2]))
    lEWKF = r.RooAddPdf("ewk_fail"+iBin,"ewk_fail"+iBin,r.RooArgList(lW[3],lZ[3]))
    lTot  = r.RooSimultaneous("tot","tot",lCats) 
    lTot.addPdf(lTotP,"pass") 
    lTot.addPdf(lTotF,"fail")     
    if iFunc > 0: lTot.fitTo(lData,r.RooFit.Extended(),r.RooFit.Minos()) 
    fDatas.extend([lPData,lFData])
    fFuncs.extend([lTotP,lTotF,lEWKP,lEWKF])
    return ([lPData,lFData],[lTotP,lTotF,lEWKP,lEWKF],[lW[4],lZ[4],lW[5],lZ[5]])
    
def fitCat(iHP,iHF,iFunc=0,iBin="_cat0"):
    lBase = baseVars(False)
    lCats   = r.RooCategory("sample","sample") 
    lBase   = baseVars()
    lPtBins = iHP[0].GetNbinsY()
    lPdfs   = []
    lRDatas = []
    lDatas  = r.std.map ('string, RooDataHist*')()
    for pt in range(1,lPtBins+1):
        lPCat = []
        lFCat = []
        for pH in iHP:
            print pH.GetName(),pH.Integral()
            lHP = proj(iBin,str(pt),pH)
            lPCat.append(lHP)
        for pH in iHF:
            print pH.GetName(),pH.Integral()
            lHF = proj(iBin,str(pt),pH)
            lFCat.append(lHF)
        (pDatas,pPdfs,pHists) = cat(lCats,lPCat,lFCat,"cat"+str(pt),lBase,iHP[0].GetYaxis().GetBinCenter(pt),iFunc)
        #for i0 in range(0,len(pDatas)):
        #    lPdfs .append(pPdfs[i0])
        #    lRDatas.append(pDatas[i0])
        #lPair0 = r.std.pair('string, RooDataHist*')("pass_"+str(pt),pDatas[0])
        #lPair1 = r.std.pair('string, RooDataHist*')("fail_"+str(pt),pDatas[1])
        #lDatas.insert(lPair0)
        #lDatas.insert(lPair1)
        lPHists=[pHists[0],pHists[1],pPdfs[0]]
        lFHists=[pHists[2],pHists[3],pPdfs[1]]
        lPHists.extend(getSignals(lPCat,lFCat,"cat"+str(pt),lBase)[0])
        lFHists.extend(getSignals(lPCat,lFCat,"cat"+str(pt),lBase)[1])
        workspace([pDatas[0]],lPHists,fVars,"pass_cat"+str(pt))
        workspace([pDatas[1]],lFHists,fVars,"fail_cat"+str(pt))
        print "Integral",lPCat[0].Integral(),lFCat[0].Integral(),"----->"
    return
    print len(lPdfs),lDatas["pass_1"]
    lData  = r.RooDataHist("comb_data_obs","comb_data_obs",r.RooArgList(lBase[0]),lCats,lDatas)
    lPdf   = r.RooSimultaneous("tot","tot",lCats)
    for i0 in range(0,len(lPdfs)):
        lPdf .addPdf(lPdfs [i0],lPdfs[i0].GetName().replace("tot_",""))
    lPdf.fitTo(lData,r.RooFit.Extended(),r.RooFit.Minos())
    #for i0 in range(0,lPtBins):
    #    drawPF(lBase[0],[lRDatas[2*i0],lRDatas[2*i0+1]],[[lPdfs[2*i0]],[lPdfs[2*i0+1]]],i0)

def dumpRalph(iHs,iBase,iPt,iCat):
    #lName=(((iH.GetName().replace("_fail_","")).replace("_pass_","")).replace(iCat,"")).replace("2D_","")
    lName="qcd"
    iBase[5].setVal(iPt)
    lP1     = r.RooRealVar   ("p1" ,"p1", 0.0   ,-0.1  ,0.1)
    lP2     = r.RooRealVar   ("p2" ,"p2", 0.0   ,-0.1  ,0.1)
    lP3     = r.RooRealVar   ("p3" ,"p3", 0.0   ,-0.1  ,0.1)
    lR1     = r.RooRealVar   ("r1" ,"r1", 0.0   ,-10.5 ,10.5)
    lR2     = r.RooRealVar   ("r2" ,"r2", 0.0   ,-10.5 ,10.5)
    lR3     = r.RooRealVar   ("r3" ,"r3", 0.0   ,-10.5 ,10.5)
    lR4     = r.RooRealVar   ("r4" ,"r4", 0.0   ,-10.5 ,10.5)
    lPR1    = r.RooRealVar   ("pr1","pr1", 0.0   ,-0.5 ,0.5)
    lPR2    = r.RooRealVar   ("pr2","pr2", 0.0   ,-0.1 ,0.1)
    lPR3    = r.RooRealVar   ("pr3","pr3", 0.0   ,-0.1 ,0.1)
    lPR4    = r.RooRealVar   ("pr4","pr4", 0.0   ,-0.1 ,0.1)
    lPR5    = r.RooRealVar   ("pr5","pr5", 0.0   ,-0.1 ,0.1)
    lPR6    = r.RooRealVar   ("pr6","pr6", 0.0   ,-0.1 ,0.1)
    lPR7    = r.RooRealVar   ("pr7","pr7", 0.0   ,-0.1 ,0.1)
    lPR8    = r.RooRealVar   ("pr8","pr8", 0.0   ,-0.1 ,0.1)
    lPR9    = r.RooRealVar   ("pr9","pr9", 0.0   ,-0.1 ,0.1)
    lVars = r.RooArgList(lP1,lP2,lR1,lPR1,lPR2,lR2,lPR3,lPR4,lR3)
    lVars.add(lPR5)
    lVars.add(lPR6)
    lVars.add(lR4)
    lVars.add(lPR7)
    lVars.add(lPR8)
    lPassBins = r.RooArgList()
    lFailBins = r.RooArgList()
    iBase[2].setVal(0.02)
    iBase[2].setConstant(False)
    lUnity    = r.RooConstVar("unity","unity",1.)
    for i0 in range(1,iHs[0].GetNbinsX()+1):
        iBase[0].setVal(iHs[0].GetXaxis().GetBinCenter(i0)) 
        lPass = command(iBase[0].getVal(),iBase[6].getVal(),lUnity,lVars,4,2,8)
        pSum = 0
        for i1 in range(0,len(iHs)):
            pSum = pSum + iHs[i1].GetBinContent(i0) if i1 == 0 else pSum - iHs[i1].GetBinContent(i0)
        if pSum < 0:
            pSum = 0
        pUnc = math.sqrt(pSum)*5+10
        pFail = r.RooRealVar   (lName+"_fail_"+iCat+"_Bin"+str(i0),lName+"_fail_"+iCat+"_Bin"+str(i0),pSum,max(pSum-pUnc,0),max(pSum+pUnc,0))
        lArg = r.RooArgList(pFail,lPass,iBase[2])
        pPass = r.RooFormulaVar(lName+"_pass_"+iCat+"_Bin"+str(i0),lName+"_pass_"+iCat+"_Bin"+str(i0),"@0*max(@1,0)*@2",lArg)
        #pPass = r.RooPolyVar(lName+"_pass_"+iCat+"_Bin"+str(i0),lName+"_pass_"+iCat+"_Bin"+str(i0),pFail,lArg)
        if pSum < 4:
            pFail.setConstant(True)
            pPass = r.RooRealVar   (lName+"_pass_"+iCat+"_Bin"+str(i0),lName+"_pass_"+iCat+"_Bin"+str(i0),0,0,0)
            pPass.setConstant(True)
        lPassBins.add(pPass)
        lFailBins.add(pFail)
        fVars.extend([pPass,pFail])
        fPars.extend([pPass,pFail])
        print  pFail.GetName(),"flatParam",lPass#,lPass+"/("+lFail+")*@0"
    lPass  = r.RooParametricHist(lName+"_pass_"+iCat,lName+"_pass_"+iCat,iBase[0],lPassBins,iHs[0])
    lFail  = r.RooParametricHist(lName+"_fail_"+iCat,lName+"_fail_"+iCat,iBase[0],lFailBins,iHs[0])
    lNPass = r.RooAddition(lName+"_pass_"+iCat+"_norm",lName+"_pass_"+iCat+"_norm",lPassBins)
    lNFail = r.RooAddition(lName+"_fail_"+iCat+"_norm",lName+"_fail_"+iCat+"_norm",lFailBins)
    fFuncs.extend([lPass,lFail,lNPass,lNFail])
    lWPass = r.RooWorkspace("w_pass_"+str(iCat))
    lWFail = r.RooWorkspace("w_fail_"+str(iCat))
    getattr(lWPass,'import')(lPass,r.RooFit.RecycleConflictNodes())
    getattr(lWPass,'import')(lNPass,r.RooFit.RecycleConflictNodes())
    getattr(lWFail,'import')(lFail,r.RooFit.RecycleConflictNodes())
    getattr(lWFail,'import')(lNFail,r.RooFit.RecycleConflictNodes())
    if iCat.find("1") > -1:
        lWPass.writeToFile("paramHist"+fOutput)
    else:
        lWPass.writeToFile("paramHist"+fOutput,False)
    lWFail.writeToFile("paramHist"+fOutput,False)
    return [lPass,lFail]

def blank(iFront,iEnd,iH):
    lH = iH.Clone(iFront+iEnd)
    for i0 in range(0,iH.GetNbinsX()+1):
        lH.SetBinContent(i0,1.)
    return lH

#pt categories with rhalpha Fit constraints does on as RateParams
def rhoCard(iHP,iHF,iBin="cat"):
    lBase = baseVars(False)
    lCats   = r.RooCategory("sample","sample") 
    lPtBins = iHP[0].GetNbinsY()
    lPdfs   = []
    lPPdfs  = []
    lHists  = []
    lRDatas = []
    lBlanks = []
    lDatas  = r.std.map ('string, RooDataHist*')()
    for pt in range(1,lPtBins+1):
        #fXmax = lXMax
        #if iHP[0].GetYaxis().GetBinCenter(pt) < 600: 
        #    fXMax = 270
        lPCat = []
        lFCat = []
        for pH in iHP:
            lHP = proj(iBin,str(pt),pH)
            lPCat.append(lHP)
        for pH in iHF:
            lHF = proj(iBin,str(pt),pH)
            lFCat.append(lHF)
        (pDatas,pPdfs,pHists) = cat(lCats,lPCat,lFCat,iBin+str(pt),lBase,iHP[0].GetYaxis().GetBinCenter(pt),0)
        for i0 in range(0,len(pPdfs)-2):
            lRDatas.append(pDatas[i0])
        lPPdfs.extend([pPdfs[0],pPdfs[1]])
        pPt = iHP[0].GetYaxis().GetBinLowEdge(pt)+iHP[0].GetYaxis().GetBinWidth(pt)*0.3
        print "!!!!!",pPt
        lParHists = dumpRalph([lFCat[0],lFCat[1],lFCat[2]],lBase,pPt,iBin+str(pt))
        #pSPass,pSFail = sigcat(lCats,lPCat,lFCat,iBin+str(pt),lBase,iHP[0].GetYaxis().GetBinCenter(pt))
        lPHists=[pHists[0],pHists[1]]
        lFHists=[pHists[2],pHists[3]]
        lPHists.extend(getSignals(lPCat,lFCat,"cat"+str(pt),lBase)[0])
        lFHists.extend(getSignals(lPCat,lFCat,"cat"+str(pt),lBase)[1])
        workspace([pDatas[0]],lPHists,fVars,"pass_"+iBin+str(pt),True)
        workspace([pDatas[1]],lFHists,fVars,"fail_"+iBin+str(pt),True)
        lPair0 = r.std.pair('string, RooDataHist*')("pass_"+str(pt),pDatas[0])
        lPair1 = r.std.pair('string, RooDataHist*')("fail_"+str(pt),pDatas[1])
        lDatas.insert(lPair0)
        lDatas.insert(lPair1)
        pNCat   = r.RooRealVar ("bkg_"+iBin+str(pt)+"norm","bkg_"+iBin+str(pt)+"norm",iHF[3].Integral(),-1,500000.)
        pEPHist = r.RooExtendPdf(lParHists[0].GetName()+"E",lParHists[0].GetName()+"E",lParHists[0],pNCat)
        pEFHist = r.RooExtendPdf(lParHists[1].GetName()+"E",lParHists[1].GetName()+"E",lParHists[1],pNCat)
        pPass   = r.RooAddPdf("tot_pass"+iBin,"tot_pass"+iBin,r.RooArgList(pEPHist,pPdfs[2]))
        pFail   = r.RooAddPdf("tot_fail"+iBin,"tot_fail"+iBin,r.RooArgList(pEFHist))#,pPdfs[3]))
        lPdfs.extend([pPass,pFail])
    lData  = r.RooDataHist("comb_data_obs","comb_data_obs",r.RooArgList(lBase[0]),lCats,lDatas)
    lPdf   = r.RooSimultaneous("tot","tot",lCats)
    for i0 in range(0,len(lPdfs)):
        lPdf .addPdf(lPdfs [i0],lPdfs[i0].GetName().replace("tot_",""))
    lPdf.fitTo(lData,r.RooFit.Extended(),r.RooFit.Minos())
    #for i0 in range(0,lPtBins):
    #    drawPF(lBase[0],[lRDatas[2*i0],lRDatas[2*i0+1]],[[lPdfs[2*i0]],[lPdfs[2*i0+1]]],i0)

    #print lSigs[0].GetName()
    #writeHist(lRDatas,lBase[3],lSigs,lBlanks)  

def dummy(iHP,iHF,iBin="cat"):
    lBase = baseVars(False)
    lPtBins = iHP[0].GetNbinsY()
    for pt in range(1,lPtBins+1):
        lPCat = []
        lFCat = []
        for pH in iHP:
            lHP = proj(iBin,str(pt),pH)
            lPCat.append(lHP)
 
        for pH in iHF:
            lHF = proj(iBin,str(pt),pH)
            lFCat.append(lHF)
 
        lPData = r.RooDataHist("data_obs_pass_"+iBin+str(pt),"data_obs_pass_"+iBin,r.RooArgList(lBase[0]),lPCat[0])
        lFData = r.RooDataHist("data_obs_fail_"+iBin+str(pt),"data_obs_fail_"+iBin,r.RooArgList(lBase[0]),lFCat[0])
        lPW    = r.RooDataHist("wqq_pass_"     +iBin+str(pt),"wqq_pass_"     +iBin,r.RooArgList(lBase[0]),lPCat[1])
        lFW    = r.RooDataHist("wqq_fail_"     +iBin+str(pt),"wqq_fail_"     +iBin,r.RooArgList(lBase[0]),lFCat[1])
        lPZ    = r.RooDataHist("zqq_pass_"     +iBin+str(pt),"zqq_pass_"     +iBin,r.RooArgList(lBase[0]),lPCat[2])
        lFZ    = r.RooDataHist("zqq_fail_"     +iBin+str(pt),"zqq_fail_"     +iBin,r.RooArgList(lBase[0]),lFCat[2])
        lPQCD  = r.RooDataHist("qcd_pass_"     +iBin+str(pt),"qcd_pass_"     +iBin,r.RooArgList(lBase[0]),lPCat[len(iHP)-2])
        lFQCD  = r.RooDataHist("qcd_fail_"     +iBin+str(pt),"qcd_fail_"     +iBin,r.RooArgList(lBase[0]),lFCat[len(iHF)-2])
        lPHists=[lPW,lPZ,lPQCD]
        lFHists=[lFW,lFZ,lFQCD]
        lPHists.extend(getSignals(lPCat,lFCat,"cat"+str(pt),lBase)[0])
        lFHists.extend(getSignals(lPCat,lFCat,"cat"+str(pt),lBase)[1])
        workspace([lPData],lPHists,fVars,"pass_"+iBin+str(pt),True)
        workspace([lFData],lFHists,fVars,"fail_"+iBin+str(pt),True)
            

def load(iFileName,iHP,iHF,i2D,iPseudo=False):
    end=""
    if i2D:
        end="_2D"
    lFile = r.TFile(iFileName)
    lHP0 = lFile.Get("data_obs_pass"+end)
    lHF0 = lFile.Get("data_obs_fail"+end)
    lHP1 = lFile.Get("wqq_pass" +end)
    lHF1 = lFile.Get("wqq_fail" +end)
    lHP2 = lFile.Get("zqq_pass" +end)
    lHF2 = lFile.Get("zqq_fail" +end)
    lHP3 = lFile.Get("qcd_pass" +end)
    lHF3 = lFile.Get("qcd_fail" +end)
    lHP4 = lFile.Get("tt_pass" +end)
    lHF4 = lFile.Get("tt_fail" +end)
    if iPseudo:
        lHP0 = lHP3.Clone("data_obs_pass"+end)
        lHF0 = lHF3.Clone("data_obs_fail"+end)
        lHP0.Add(lHP1)
        lHF0.Add(lHF1)
        lHP0.Add(lHP2)
        lHF0.Add(lHF2)
    iHP.extend([lHP0,lHP1,lHP2])
    iHF.extend([lHF0,lHF1,lHF2])
    masses=[50,75,100,125,150,200,250,300]
    for mass in masses:
        lHP.append(lFile.Get("zqq"+str(mass)+"_pass" +end))
        iHF.append(lFile.Get("zqq"+str(mass)+"_fail" +end))
    iHP.extend([lHP3,lHP4])
    iHF.extend([lHF3,lHF4])
    for lH in (iHP+iHF):
        lH.SetDirectory(0)
    return 
    
if __name__ == "__main__":
    options = parser()
    print options
    lHP =[]
    lHF =[]
    fOutput = options.output 
    fXMin   = options.xmin
    fXMax   = options.xmax
    fNBins  = options.nbins
    load(options.input,lHP,lHF,options.fit2D or (options.cat and not options.fit1D) or (options.card and not options.fit1D) or options.dummy)
    if options.fit1D and not options.cat and not options.card:
        if options.passfail:
            fit1DPF(lHP,lHF,options.func)
        else:
            fit1D(lHP,lHF,options.fail,options.func)

    if options.fit2D:
        f2D=True
        if options.passfail:
            fit2DPF(lHP,lHF)
        else:
            fit2D(lHP,lHF,options.fail)

    if options.cat:
        fitCat(lHP,lHF,options.func)
    
    if options.card:
        rhoCard(lHP,lHF)
    
    if options.dummy:
        dummy(lHP,lHF)
