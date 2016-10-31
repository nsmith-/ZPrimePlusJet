#!/usr/bin/env python
import ROOT as r,sys,math,array,os
from hist import hist
from optparse import OptionParser
from ROOT import std,RooDataHist
from tools import *
#r.gROOT.Macro(os.path.expanduser('~/rootlogon.C'))
r.gSystem.Load("/uscms_data/d3/cvenier/DiH_13TeV/CMSSW_7_4_7/lib/slc6_amd64_gcc491/libHiggsAnalysisCombinedLimit.so");
r.gInterpreter.GenerateDictionary("std::pair<std::string, RooDataHist*>", "map;string;RooDataHist.h")
r.gInterpreter.GenerateDictionary("std::map<std::string, RooDataHist*>", "map;string;RooDataHist.h")

fOutput="bern.root"
fNBins=68
fXMin=28
fXMax=240
fVars=[]
fDatas=[]
fFuncs=[]
fPars=[]

def parser():
    parser = OptionParser()
    parser.add_option('--input'   ,action='store',type='string',dest='input'   ,default='hists.root',help='input file')
    parser.add_option('--output'  ,action='store',type='string',dest='output'  ,default='base.root' ,help='workspace output')
    parser.add_option('--xMin'    ,action='store',type='float' ,dest='xmin'    ,default=32          ,help='x-min')
    parser.add_option('--xMax'    ,action='store',type='float' ,dest='xmax'    ,default=300         ,help='x-max')
    parser.add_option('--nBins'   ,action='store',type='int'   ,dest='nbins'    ,default=67          ,help='n-bins')
    (options,args) = parser.parse_args()
    return options

def histFunc(iH,iVars,iLabel="w",iBin="_cat0",i1D=True):
    print(iLabel)
    print(str(iH))
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

def cat(iCat,iHP,iHF,iBin,iBase,iPt,iFunc):
    iCat.defineType("pass"+iBin)
    iCat.defineType("fail"+iBin)
    lCats = r.RooCategory("sample","sample") 
    lCats.defineType("pass",1) 
    lCats.defineType("fail",0) 
    lPData = r.RooDataHist("data_obs_pass_"+iBin,"data_obs_pass_"+iBin,r.RooArgList(iBase[0]),iHP[0])
    lFData = r.RooDataHist("data_obs_fail_"+iBin,"data_obs_fail_"+iBin,r.RooArgList(iBase[0]),iHF[0])
    lData  = r.RooDataHist("comb_data_obs","comb_data_obs",r.RooArgList(iBase[0]),r.RooFit.Index(lCats),r.RooFit.Import("pass",lPData),r.RooFit.Import("fail",lFData)) 
    print("asddddd")
    print(str(iHP))	
    lW    = histFunc([iHP[1],iHF[1]],iBase,"wqq",iBin)
    lZ    = histFunc([iHP[2],iHF[2]],iBase,"zqq",iBin)
    ltop  = histFunc([iHP[3],iHF[3]],iBase,"tqq",iBin)		
    #lQCD  = histFunc([iHP[len(iHP)-1],iHF[len(iHF)-1]],iBase,"qcd",iBin)	
    lQCD  = histFunc([iHP[5],iHF[5]],iBase,"qcd",iBin)
    lTotP = r.RooAddPdf("tot_pass"+iBin,"tot_pass"+iBin,r.RooArgList(lQCD[0]))
    lTotF = r.RooAddPdf("tot_fail"+iBin,"tot_fail"+iBin,r.RooArgList(lQCD[1]))
    lEWKP = r.RooAddPdf("ewk_pass"+iBin,"ewk_pass"+iBin,r.RooArgList(lW[2],lZ[2],ltop[2]))
    lEWKF = r.RooAddPdf("ewk_fail"+iBin,"ewk_fail"+iBin,r.RooArgList(lW[3],lZ[3],ltop[3]))
    lTot  = r.RooSimultaneous("tot","tot",lCats) 
    lTot.addPdf(lTotP,"pass") 
    lTot.addPdf(lTotF,"fail")     
    fDatas.extend([lPData,lFData])
    fFuncs.extend([lTotP,lTotF,lEWKP,lEWKF])
    return ([lPData,lFData],[lTotP,lTotF,lEWKP,lEWKF],[lW[4],lZ[4],ltop[4],lW[5],lZ[5],ltop[5]])

def getSignals(iHP,iHF,iBin,iBase):
    lPSigs  = []
    lFSigs  = []
    lPHists = [] 
    lFHists = [] 
    lVars=[125]#50,75,100,125,150,200,250,300]
    for i0 in range(0,len(lVars)):
        lPHists.append(iHP[i0+4])
        lFHists.append(iHF[i0+4])
    print(str(lPHists))
    print("asdSig")
    lPHist = hist(lVars,lPHists)
    lFHist = hist(lVars,lFHists)
    masses=[125]#50,60,75,90,100,112,125,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290]
    for i0 in range(0,len(masses)):
      if len(masses) > 1:
        pHP   = lPHist.morph(masses[i0])
        pHF   = lFHist.morph(masses[i0])
      else :
	pHP   = lPHist
	pHF   = lFHist
        for i1 in range(0,len(lVars)):
            if lVars[i1] == masses[i0]:
                pHP=iHP[i1+4]
                pHF=iHF[i1+4]
        lSig = histFunc([pHP,pHF],iBase,"hqq_"+str(masses[i0]),iBin)
        lPSigs.append(lSig[4])
        lFSigs.append(lSig[5])
    return (lPSigs,lFSigs)

def command(iPt,iMsd,iQCD,iVars,iNR=1,iNP=1,iNRNP=1):
    lPt  = r.RooConstVar("Var_Pt_" +str(iPt)+"_"+str(iMsd), "Var_Pt_" +str(iPt)+"_"+str(iMsd),(iPt-500))
    #lRho = r.RooConstVar("Var_Rho_"+str(iPt)+"_"+str(iRho), "Var_Rho_"+str(iPt)+"_"+str(iRho),(iRho-2.5))
    lMsd = r.RooConstVar("Var_Msd_"+str(iPt)+"_"+str(iMsd), "Var_Msd_"+str(iPt)+"_"+str(iMsd),(iMsd-50.))
    lMsdArray = r.RooArgList()
    lNCount=0
    for pRVar in range(0,iNR):
        lTmpArray = r.RooArgList()
        lTmpArray.add(iQCD)
        pNP = iNP if pRVar < iNRNP else 0
        for pVar in range(0,pNP):
            lTmpArray.add(iVars[lNCount])
            lNCount=lNCount+1
            print "----",iVars[lNCount].GetName()
        pLabel="Var_Pol_Bin_"+str(iPt)+"_"+str(iMsd)+"_"+str(pRVar)
        pPol = r.RooPolyVar(pLabel,pLabel,lPt,lTmpArray)
        lMsdArray.add(pPol)
        fVars.append(pPol)
    lLabel="Var_MsdPol_Bin_"+str(iPt)+"_"+str(iMsd)
    lMsdPol = r.RooPolyVar(lLabel,lLabel,lMsd,lMsdArray)
    fVars.extend([lPt,lMsd,lMsdPol])
    return lMsdPol

def baseVars(iPtBins):
    global fNBins,fXMin,fXMax
    lMSD    = r.RooRealVar("x","x",fXMin,fXMax)
    lMSD.setBins(fNBins)
    lPt  = r.RooRealVar   ("pt","pt",500,3000)
    lPt .setBins(iPtBins)
    #lRho = r.RooFormulaVar("rho","log(x*x/pt)",r.RooArgList(lMSD,lPt))
    #eff variables
    lEff    = r.RooRealVar("veff"      ,"veff"      ,0.5 ,0.,1.0)
    lEffQCD = r.RooRealVar("qcdeff"    ,"qcdeff"   ,0.01,0.,10.)
    lDM     = r.RooRealVar("dm","dm", 0.,-10,10)
    lShift  = r.RooFormulaVar("shift",lMSD.GetName()+"-dm",r.RooArgList(lMSD,lDM))  
    lVars=[lMSD,lEff,lEffQCD,lDM,lShift,lPt]
    fVars.extend([lMSD,lPt,lEff,lEffQCD,lDM])
    fPars.extend([lEffQCD,lDM,lEff])
    return lVars

def addArray(iVars,iNVar0,iNVar1,iNVar01,iLabel0,iLabel1,iXMin0,iXMax0,iXMin1,iXMax1):
    for i0 in range(0,iNVar1):
        for i1 in range(0,iNVar0):
            pVar    = iLabel0+iLabel1+str(i0)+str(i1)
            pXMin = iXMin0
            pXMax = iXMax0
            if i0 == 0: 
                pVar = iLabel0+str(i1)
            if i1 == 0: 
                pVar = iLabel1+str(i0)
            pRooVar = r.RooRealVar   (pVar,pVar, 0.0,pXMin,pXMax)
            print "Add:",pRooVar.GetName()
            iVars.append(pRooVar)

def makeRalph(iHs,iBase,iPt,iCat):
    lName="qcd"
    lUnity    = r.RooConstVar("unity","unity",1.)
    #Fix the pt (top) and teh qcd eff
    iBase[5].setVal(iPt)
    iBase[2].setVal(0.02)
    iBase[2].setConstant(False)
    #polynomial order for fit
    lNP=1
    lNR=2
    lNRP=-1
    lVars = []
    addArray(lVars,lNP,lNR,lNRP,"p","r",-0.1,0.1,-10.5,10.5)
    #Now build the function
    lPassBins = r.RooArgList()
    lFailBins = r.RooArgList()
    for i0 in range(1,iHs[0].GetNbinsX()+1):
        iBase[0].setVal(iHs[0].GetXaxis().GetBinCenter(i0)) 
        lPass = command(iBase[0].getVal(),iBase[5].getVal(),lUnity,lVars,lNR,lNP,lNRP)
        pSum = 0
        for i1 in range(0,len(iHs)):
            pSum = pSum + iHs[i1].GetBinContent(i0) if i1 == 0 else pSum - iHs[i1].GetBinContent(i0)
        if pSum < 0:
            pSum = 0
        #5 sigma range + 10 events
        pUnc = math.sqrt(pSum)*5+10
        #Define the failing category
        pFail = r.RooRealVar   (lName+"_fail_"+iCat+"_Bin"+str(i0),lName+"_fail_"+iCat+"_Bin"+str(i0),pSum,max(pSum-pUnc,0),max(pSum+pUnc,0))
        #Now define the passing cateogry based on the failing (make sure it can't go negative)
        lArg = r.RooArgList(pFail,lPass,iBase[2])
        pPass = r.RooFormulaVar(lName+"_pass_"+iCat+"_Bin"+str(i0),lName+"_pass_"+iCat+"_Bin"+str(i0),"@0*max(@1,0)*@2",lArg)
        #If the number of events in the failing is small remove the bin from being free in the fit
        if pSum < 4:
            pFail.setConstant(True)
            pPass = r.RooRealVar   (lName+"_pass_"+iCat+"_Bin"+str(i0),lName+"_pass_"+iCat+"_Bin"+str(i0),0,0,0)
            pPass.setConstant(True)
        #Add bins to the array
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
    #Now write the wrokspace with the rooparamhist
    lWPass = r.RooWorkspace("w_pass_"+str(iCat))
    lWFail = r.RooWorkspace("w_fail_"+str(iCat))
    getattr(lWPass,'import')(lPass,r.RooFit.RecycleConflictNodes())
    getattr(lWPass,'import')(lNPass,r.RooFit.RecycleConflictNodes())
    getattr(lWFail,'import')(lFail,r.RooFit.RecycleConflictNodes())
    getattr(lWFail,'import')(lNFail,r.RooFit.RecycleConflictNodes())
    if iCat.find("1") > -1:
        lWPass.writeToFile("ralpha"+fOutput)
    else:
        lWPass.writeToFile("ralpha"+fOutput,False)
    lWFail.writeToFile("ralpha"+fOutput,False)
    return [lPass,lFail]

#pt categories with rhalpha Fit constraints does on as RateParams
def makeFullRalph(iHP,iHF,iBin="cat"):
    global fNBins,fXMin,fXMax
    lCats   = r.RooCategory("sample","sample") 
    lPtBins = iHP[0].GetNbinsY()
    lBase = baseVars(lPtBins)
    lPdfs   = []
    lHists  = []
    lBlanks = []
    lDatas  = r.std.map ('string, RooDataHist*')()
    #Loop over pt bins
    for pt in range(1,lPtBins+1):
        lPCat = []
        lFCat = []
        #Convert 2 D histograms to 1D
        for pH in iHP:
            lHP = proj(iBin,str(pt),pH,fNBins,fXMin,fXMax)
            lPCat.append(lHP)
        for pH in iHF:
            lHF = proj(iBin,str(pt),pH,fNBins,fXMin,fXMax)
            lFCat.append(lHF)
        #Make the standard datahists
        (pDatas,pPdfs,pHists) = cat(lCats,lPCat,lFCat,iBin+str(pt),lBase,iHP[0].GetYaxis().GetBinCenter(pt),0)
        #Get approximate pt bin value
        pPt = iHP[0].GetYaxis().GetBinLowEdge(pt)+iHP[0].GetYaxis().GetBinWidth(pt)*0.3
        #Make the ralphabet fit for a specific pt bin
        lParHists = makeRalph([lFCat[0],lFCat[1],lFCat[2],lFCat[3]],lBase,pPt,iBin+str(pt))
        #Get signals and SM backgrounds
        lPHists=[pHists[0],pHists[1],pHists[2]]
        lFHists=[pHists[3],pHists[4],pHists[5]]
        lPHists.extend(getSignals(lPCat,lFCat,"cat"+str(pt),lBase)[0])
        lFHists.extend(getSignals(lPCat,lFCat,"cat"+str(pt),lBase)[1])
        #Write to file
        workspace(fOutput,[pDatas[0]],lPHists,fVars,"pass_"+iBin+str(pt),True)
        workspace(fOutput,[pDatas[1]],lFHists,fVars,"fail_"+iBin+str(pt),True)
	
def plot(fOutput):
	ofile = TFile(fOutput)
	WS = ofile.Get()
        
def load(iFileName,iHP,iHF,i2D=True,iPseudo=True):
    end=""
    #if i2D:
        #end="_2D"
    lFile = r.TFile(iFileName)
    lHP0 = lFile.Get("data_obs_pass"+end)
    lHF0 = lFile.Get("data_obs_fail"+end)
    lHP1 = lFile.Get("wqq_pass" +end)
    lHF1 = lFile.Get("wqq_fail" +end)
    lHP2 = lFile.Get("zqq_pass" +end)
    lHF2 = lFile.Get("zqq_fail" +end)
    lHP3 = lFile.Get("tqq_pass" +end)
    lHF3 = lFile.Get("tqq_fail" +end)
    lHP4 = lFile.Get("qcd_pass" +end)
    lHF4 = lFile.Get("qcd_fail" +end)
    if iPseudo:
        lHP0 = lHP4.Clone("data_obs_pass"+end)
        lHF0 = lHF4.Clone("data_obs_fail"+end)
        lHP0.Add(lHP1)
        lHF0.Add(lHF1)
        lHP0.Add(lHP2)
        lHF0.Add(lHF2)
        lHP0.Add(lHP3)
	lHF0.Add(lHF3)
    iHP.extend([lHP0,lHP1,lHP2,lHP3])
    iHF.extend([lHF0,lHF1,lHF2,lHF3])	
    masses=[125]#50,75,100,125,150,200,250,300]
    for mass in masses:
        iHP.append(lFile.Get("hqq_"+str(mass)+"_pass" +end))
        iHF.append(lFile.Get("hqq_"+str(mass)+"_fail" +end))
    iHP.extend([lHP4])
    iHF.extend([lHF4])
    print("here")
    print(str(iHP))	
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
    load(options.input,lHP,lHF)
    makeFullRalph(lHP,lHF)
