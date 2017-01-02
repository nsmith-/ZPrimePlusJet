#!/usr/bin/env python
import ROOT as r,sys,math,os
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array
#r.gSystem.Load("~/Dropbox/RazorAnalyzer/python/lib/libRazorRun2.so")
r.gSystem.Load(os.getenv('CMSSW_BASE')+'/lib/'+os.getenv('SCRAM_ARCH')+'/libHiggsAnalysisCombinedLimit.so')


# including other directories
sys.path.insert(0, '../.')
from tools import *

NBINS = 23
MASS_LO = 40
MASS_HI = 201
BLIND_LO = 110
BLIND_HI = 131
##############################################################################
##############################################################################
#### B E G I N N I N G   O F   C L A S S
##############################################################################
##############################################################################

class dazsleRhalphabetBuilder: 

    def __init__( self, hpass, hfail, odir ): 

        self._hpass = hpass;
        self._hfail = hfail;
	self._massfit = options.massfit
	self._freeze = options.freeze

        self._outputName = odir+"/base.root";

        self._mass_nbins = NBINS
        self._mass_lo    = MASS_LO
        self._mass_hi    = MASS_HI
        self._mass_blind_lo = BLIND_LO
        self._mass_blind_hi = BLIND_HI
        # self._mass_nbins = hpass[0].GetXaxis().GetNbins();
        # self._mass_lo    = hpass[0].GetXaxis().GetBinLowEdge( 1 );
        # self._mass_hi    = hpass[0].GetXaxis().GetBinUpEdge( self._mass_nbins );

        print "number of mass bins and lo/hi: ", self._mass_nbins, self._mass_lo, self._mass_hi;

        #polynomial order for fit
        self._poly_lNP = 2 #1 = linear ; 2 is quadratic
        self._poly_lNR = 2
        #self._poly_lNRP =1;

        self._nptbins = hpass[0].GetYaxis().GetNbins();
        self._pt_lo = hpass[0].GetYaxis().GetBinLowEdge( 1 );
        self._pt_hi = hpass[0].GetYaxis().GetBinUpEdge( self._nptbins );

        # define RooRealVars
        self._lMSD    = r.RooRealVar("x","x",self._mass_lo,self._mass_hi)
        self._lMSD.setRange('Low',self._mass_lo,self._mass_blind_lo)
        self._lMSD.setRange('Blind',self._mass_blind_lo,self._mass_blind_hi)
        self._lMSD.setRange('High',self._mass_blind_hi,self._mass_hi)
        #self._lMSD.setBins(self._mass_nbins)		
        self._lPt     = r.RooRealVar("pt","pt",self._pt_lo,self._pt_hi);
        self._lPt.setBins(self._nptbins)
        self._lRho    = r.RooFormulaVar("rho","log(x*x/pt/pt)",r.RooArgList(self._lMSD,self._lPt))

        self._lEff    = r.RooRealVar("veff"      ,"veff"      ,0.5 ,0.,1.0)

        self._lEffQCD = r.RooRealVar("qcdeff"    ,"qcdeff"   ,0.01,0.,10.)
        qcd_pass_integral = 0
        qcd_fail_integral = 0
        for i in range(1,hfail[3].GetNbinsX()+1):
            for j in range(1,hfail[3].GetNbinsY()+1):
                if hfail[3].GetXaxis().GetBinCenter(i) > MASS_LO and hfail[3].GetXaxis().GetBinCenter(i) < MASS_HI:
                    qcd_fail_integral += hfail[3].GetBinContent(i,j)
                    qcd_pass_integral += hpass[3].GetBinContent(i,j)
        if qcd_fail_integral>0:
            qcdeff = qcd_pass_integral/qcd_fail_integral
            self._lEffQCD.setVal(qcdeff)
        print "qcdeff = %f"%qcdeff
        self._lDM     = r.RooRealVar("dm","dm", 0.,-10,10)
        self._lShift  = r.RooFormulaVar("shift",self._lMSD.GetName()+"-dm",r.RooArgList(self._lMSD,self._lDM)) 

        self._allVars = [];
        self._allShapes = [];
        self._allData = [];
        self._allPars = [];

        self.LoopOverPtBins();

    def LoopOverPtBins(self):

        print "number of pt bins = ", self._nptbins;
        for ipt in range(1,self._nptbins+1):
        # for ipt in range(1,2):
            print "------- pT bin number ",ipt		

            # 1d histograms in each pT bin (in the order... data, w, z, qcd, top, signals)
            hpass_inPtBin = [];
            hfail_inPtBin = [];
            for h in self._hpass: hpass_inPtBin.append( proj("cat",str(ipt),h,self._mass_nbins,self._mass_lo,self._mass_hi) ); 
            for h in self._hfail: hfail_inPtBin.append( proj("cat",str(ipt),h,self._mass_nbins,self._mass_lo,self._mass_hi) ); 

            # make RooDataset, RooPdfs, and histograms
            curptbincenter = self._hpass[0].GetYaxis().GetBinCenter(ipt);
            (pDatas,pPdfs,pHists) = self.workspaceInputs(hpass_inPtBin,hfail_inPtBin,"cat"+str(ipt),curptbincenter)
            #Get approximate pt bin value
            pPt = self._hpass[0].GetYaxis().GetBinLowEdge(ipt)+self._hpass[0].GetYaxis().GetBinWidth(ipt)*0.3;
            print "------- pT bin value ",pPt

            #Make the ralphabet fit for a specific pt bin
            lParHists = self.makeRhalph([hfail_inPtBin[0],hfail_inPtBin[1],hfail_inPtBin[2],hfail_inPtBin[4]],pPt,"cat"+str(ipt))

            # #Get signals and SM backgrounds
            lPHists=[pHists[0],pHists[1],pHists[2]]
            lFHists=[pHists[3],pHists[4],pHists[5]]
            lPHists.extend(self.getSignals(hpass_inPtBin,hfail_inPtBin,"cat"+str(ipt))[0])
            lFHists.extend(self.getSignals(hpass_inPtBin,hfail_inPtBin,"cat"+str(ipt))[1])
            # #Write to file
            self.makeWorkspace(self._outputName,[pDatas[0]],lPHists,self._allVars,"pass_cat"+str(ipt),True)
            self.makeWorkspace(self._outputName,[pDatas[1]],lFHists,self._allVars,"fail_cat"+str(ipt),True)

        
        for ipt in range(1,self._nptbins+1):
            for imass in range(1,self._mass_nbins+1):
                print "qcd_fail_cat%i_Bin%i flatParam" % (ipt,imass);

    def makeRhalph(self,iHs,iPt,iCat):

        print "---- [makeRhalph]"	

        lName ="qcd";
        lUnity = r.RooConstVar("unity","unity",1.)
        lZero  = r.RooConstVar("lZero","lZero",0.)

        #Fix the pt (top) and teh qcd eff
        self._lPt.setVal(iPt)
        self._lEffQCD.setConstant(False)

        polyArray = []
        self.buildPolynomialArray(polyArray,self._poly_lNP,self._poly_lNR,"p","r",-0.3,0.3)
        print polyArray

        #Now build the function
        lPassBins = r.RooArgList()
        lFailBins = r.RooArgList()

        for i0 in range(1,self._mass_nbins+1):
	    self._lMSD.setVal(iHs[0].GetXaxis().GetBinCenter(i0))
            if self._massfit :
                print ("Pt/mass poly")
                lPass = self.buildRooPolyArray(self._lPt.getVal(),self._lMSD.getVal(),lUnity,lZero,polyArray)
            else :
                print ("Pt/Rho poly")
                lPass = self.buildRooPolyRhoArray(self._lPt.getVal(),self._lRho.getVal(),lUnity,lZero,polyArray)
            pSum = 0
            for i1 in range(0,len(iHs)):
                if i1 == 0:
                    print i1, iHs[i1].GetName(), "add data"
                    pSum = pSum + iHs[i1].GetBinContent(i0) # add data
                else:                    
                    print i1, iHs[i1].GetName(), "subtract W/Z/ttbar"
                    pSum = pSum - iHs[i1].GetBinContent(i0) # subtract W/Z/ttbar from data
            if pSum < 0: pSum = 0

            print lName+"_fail_"+iCat+"_Bin"+str(i0), pSum

            #5 sigma range + 10 events
            pUnc = math.sqrt(pSum)*5+10
            #Define the failing category
            #pFail = r.RooRealVar(lName+"_fail_"+iCat+"_Bin"+str(i0),lName+"_fail_"+iCat+"_Bin"+str(i0),pSum,max(pSum-pUnc,0),max(pSum+pUnc,0))
            pFail = r.RooRealVar(lName+"_fail_"+iCat+"_Bin"+str(i0),lName+"_fail_"+iCat+"_Bin"+str(i0),pSum,0,max(pSum+pUnc,0))
            #Now define the passing cateogry based on the failing (make sure it can't go negative)
            lArg = r.RooArgList(pFail,lPass,self._lEffQCD)
            pPass = r.RooFormulaVar(lName+"_pass_"+iCat+"_Bin"+str(i0),lName+"_pass_"+iCat+"_Bin"+str(i0),"@0*max(@1,0)*@2",lArg)

            print pPass.Print()

            # print pPass.GetName()

            #If the number of events in the failing is small remove the bin from being free in the fit
            if pSum < 4:
                print "too small number of events", pSum, "Bin", str(i0)
                pFail.setConstant(True)
                pPass = r.RooRealVar(lName+"_pass_"+iCat+"_Bin"+str(i0),lName+"_pass_"+iCat+"_Bin"+str(i0),0,0,0)
                pPass.setConstant(True)

            #Add bins to the array
            lPassBins.add(pPass)
            lFailBins.add(pFail)
            self._allVars.extend([pPass,pFail])
            self._allPars.extend([pPass,pFail])
            # print  pFail.GetName(),"flatParam",lPass#,lPass+"/("+lFail+")*@0"

        lPass  = r.RooParametricHist(lName+"_pass_"+iCat,lName+"_pass_"+iCat,self._lMSD,lPassBins,iHs[0])
        lFail  = r.RooParametricHist(lName+"_fail_"+iCat,lName+"_fail_"+iCat,self._lMSD,lFailBins,iHs[0])
        lNPass = r.RooAddition(lName+"_pass_"+iCat+"_norm",lName+"_pass_"+iCat+"_norm",lPassBins)
        lNFail = r.RooAddition(lName+"_fail_"+iCat+"_norm",lName+"_fail_"+iCat+"_norm",lFailBins)
        lNPass.Print()
        lNFail.Print()        
        self._allShapes.extend([lPass,lFail,lNPass,lNFail])

        #Now write the wrokspace with the rooparamhist
        lWPass = r.RooWorkspace("w_pass_"+str(iCat))
        lWFail = r.RooWorkspace("w_fail_"+str(iCat))
        getattr(lWPass,'import')(lPass,r.RooFit.RecycleConflictNodes())
        getattr(lWPass,'import')(lNPass,r.RooFit.RecycleConflictNodes())
        getattr(lWFail,'import')(lFail,r.RooFit.RecycleConflictNodes())
        getattr(lWFail,'import')(lNFail,r.RooFit.RecycleConflictNodes())
        if iCat.find("1") > -1:
            lWPass.writeToFile(self._outputName.replace("base","ralphabase"))
        else:
            lWPass.writeToFile(self._outputName.replace("base","ralphabase"),False)
        lWFail.writeToFile(self._outputName.replace("base","ralphabase"),False)
        return [lPass,lFail]

    def buildRooPolyArray(self,iPt,iMass,iQCD,iZero,iVars):

        # print "---- [buildRooPolyArray]"	
        # print len(iVars);

        lPt  = r.RooConstVar("Var_Pt_" +str(iPt)+"_"+str(iMass), "Var_Pt_" +str(iPt)+"_"+str(iMass),(iPt))
        lMass = r.RooConstVar("Var_Mass_"+str(iPt)+"_"+str(iMass), "Var_Mass_"+str(iPt)+"_"+str(iMass),(iMass))
        lMassArray = r.RooArgList()
        lNCount=0
        for pRVar in range(0,self._poly_lNR+1):
            lTmpArray = r.RooArgList()
            for pVar in range(0,self._poly_lNP+1):
                if lNCount == 0: lTmpArray.add(iQCD) # for the very first constant (e.g. p0r0), just set that to 1
                else: lTmpArray.add(iVars[lNCount])
                lNCount=lNCount+1
            pLabel="Var_Pol_Bin_"+str(round(iPt,2))+"_"+str(round(iMass,3))+"_"+str(pRVar)
            pPol = r.RooPolyVar(pLabel,pLabel,lPt,lTmpArray)
            lMassArray.add(pPol)
            self._allVars.append(pPol)

        lLabel="Var_MassPol_Bin_"+str(round(iPt,2))+"_"+str(round(iMass,3))
        lMassPol = r.RooPolyVar(lLabel,lLabel,lMass,lMassArray)
        self._allVars.extend([lPt,lMass,lMassPol])
        return lMassPol

    def buildRooPolyRhoArray(self,iPt,iRho,iQCD,iZero,iVars):

                # print "---- [buildRooPolyArray]"      

                lPt  = r.RooConstVar("Var_Pt_" +str(iPt)+"_"+str(iRho), "Var_Pt_" +str(iPt)+"_"+str(iRho),(iPt))
                lRho = r.RooConstVar("Var_Rho_"+str(iPt)+"_"+str(iRho), "Var_Rho_"+str(iPt)+"_"+str(iRho),(iRho))
                lRhoArray = r.RooArgList()
                lNCount=0
                for pRVar in range(0,self._poly_lNR+1):
                        lTmpArray = r.RooArgList()
                        for pVar in range(0,self._poly_lNP+1):
                                if lNCount == 0: lTmpArray.add(iQCD); # for the very first constant (e.g. p0r0), just set that to 1
                                else: lTmpArray.add(iVars[lNCount])
                                lNCount=lNCount+1
                        pLabel="Var_Pol_Bin_"+str(round(iPt,2))+"_"+str(round(iRho,3))+"_"+str(pRVar)
                        pPol = r.RooPolyVar(pLabel,pLabel,lPt,lTmpArray)
                        print pPol.Print()
                        lRhoArray.add(pPol);
                        self._allVars.append(pPol)

                lLabel="Var_RhoPol_Bin_"+str(round(iPt,2))+"_"+str(round(iRho,3))
                lRhoPol = r.RooPolyVar(lLabel,lLabel,lRho,lRhoArray)
                self._allVars.extend([lPt,lRho,lRhoPol])
                return lRhoPol


    def buildPolynomialArray(self, iVars,iNVar0,iNVar1,iLabel0,iLabel1,iXMin0,iXMax0):

        print "---- [buildPolynomialArray]"
        ## form of polynomial
        ## (p0r0 + p1r0 * pT + p2r0 * pT^2 + ...) + 
        ## (p0r1 + p1r1 * pT + p2r1 * pT^2 + ...) * rho + 
        ## (p0r2 + p1r2 * pT + p2r2 * pT^2 + ...) * rho^2 + ...
	'''
	r0p0    =    0, pXMin,pXMax
	r1p0    =   -3.7215e-03 +/-  1.71e-08
 	r2p0    =    2.4063e-06 +/-  2.76e-11
        r0p1    =   -2.1088e-01 +/-  2.72e-06I	
        r1p1    =    3.6847e-05 +/-  4.66e-09
        r2p1    =   -3.8415e-07 +/-  7.23e-12
        r0p2    =   -8.5276e-02 +/-  6.90e-07
        r1p2    =    2.2058e-04 +/-  1.10e-09
        r2p2    =   -2.2425e-07 +/-  1.64e-12
	'''
	value = [ 0.,
		-3.7215e-03,
 		2.4063e-06,
		-2.1088e-01, 
 		3.6847e-05, 
		-3.8415e-07, 
		-8.5276e-02, 
 		2.2058e-04,
		-2.2425e-07]
	error = [iXMax0,
		1.71e-08,
		2.76e-11,
		2.72e-06,
		4.66e-09,
		7.23e-12,
		6.90e-07,
		1.10e-09,
		1.64e-12]
		
        for i0 in range(iNVar0+1):
            for i1 in range(iNVar1+1):
                pVar = iLabel1+str(i1)+iLabel0+str(i0);		
		if self._freeze :
		
			start = value [i0*3+i1]
			pXMin = value [i0*3+i1]-error[i0*3+i1]
			pXMax = value [i0*3+i1]+error[i0*3+i1]
			
		else: 
			 start = 0.0
                	 pXMin = iXMin0
               		 pXMax = iXMax0
		
                pRooVar = r.RooRealVar(pVar,pVar,0.0,pXMin,pXMax)
		print("========  here i0 %s i1 %s"%(i0,i1))
                print pVar
		print(" is : %s  +/- %s"%(value[i0*3+i1],error[i0*3+i1]))
                
                iVars.append(pRooVar)



    def workspaceInputs(self, iHP,iHF,iBin,iPt):

        lCats = r.RooCategory("sample","sample") 
        lCats.defineType("pass",1) 
        lCats.defineType("fail",0) 
        lPData = r.RooDataHist("data_obs_pass_"+iBin,"data_obs_pass_"+iBin,r.RooArgList(self._lMSD),iHP[0])
        lFData = r.RooDataHist("data_obs_fail_"+iBin,"data_obs_fail_"+iBin,r.RooArgList(self._lMSD),iHF[0])
        lData  = r.RooDataHist("comb_data_obs","comb_data_obs",r.RooArgList(self._lMSD),r.RooFit.Index(lCats),r.RooFit.Import("pass",lPData),r.RooFit.Import("fail",lFData)) 

        lW    = self.rooTheHistFunc([iHP[1],iHF[1]],"wqq",iBin)
        lZ    = self.rooTheHistFunc([iHP[2],iHF[2]],"zqq",iBin)	
        lQCD  = self.rooTheHistFunc([iHP[3],iHF[3]],"qcd",iBin)
        ltop  = self.rooTheHistFunc([iHP[4],iHF[4]],"tqq",iBin)

        lTotP = r.RooAddPdf("tot_pass"+iBin,"tot_pass"+iBin,r.RooArgList(lQCD[0]))
        lTotF = r.RooAddPdf("tot_fail"+iBin,"tot_fail"+iBin,r.RooArgList(lQCD[1]))
        lEWKP = r.RooAddPdf("ewk_pass"+iBin,"ewk_pass"+iBin,r.RooArgList(lW[2],lZ[2],ltop[2]))
        lEWKF = r.RooAddPdf("ewk_fail"+iBin,"ewk_fail"+iBin,r.RooArgList(lW[3],lZ[3],ltop[3]))

        lTot  = r.RooSimultaneous("tot","tot",lCats) 
        lTot.addPdf(lTotP,"pass") 
        lTot.addPdf(lTotF,"fail")     
        self._allData.extend([lPData,lFData])
        self._allShapes.extend([lTotP,lTotF,lEWKP,lEWKF])

        ## find out which to make global
        ## RooDataHist (data), then RooAbsPdf (qcd,ewk), then RooHistPdf of each electroweak
        return ([lPData,lFData],[lTotP,lTotF,lEWKP,lEWKF],[lW[4],lZ[4],ltop[4],lW[5],lZ[5],ltop[5]])

    def rooTheHistFunc(self,iH,iLabel="w",iBin="_cat0"):

        # normalization
        lNTot   = r.RooRealVar (iLabel+"norm"+iBin,iLabel+"norm"+iBin,(iH[0].Integral()+iH[1].Integral()),0.,5.*(iH[0].Integral()+iH[1].Integral()))
        lNPass  = r.RooFormulaVar(iLabel+"fpass"+iBin ,iLabel+"norm"+iBin+"*(veff)"  ,r.RooArgList(lNTot,self._lEff))
        lNFail  = r.RooFormulaVar(iLabel+"fqail"+iBin ,iLabel+"norm"+iBin+"*(1-veff)",r.RooArgList(lNTot,self._lEff))
        # shapes
        lPData  = r.RooDataHist(iLabel+"_pass_"+iBin,iLabel+"_pass_"+iBin, r.RooArgList(self._lMSD),iH[0])
        lMData  = r.RooDataHist(iLabel+"_fail_"+iBin,iLabel+"_fail_"+iBin, r.RooArgList(self._lMSD),iH[1]) 
        lP      = r.RooHistPdf (iLabel+"passh"+iBin,iLabel+"passh"+iBin, r.RooArgList(self._lShift),r.RooArgList(self._lMSD),lPData,0)
        lF      = r.RooHistPdf (iLabel+"failh"+iBin,iLabel+"failh"+iBin, r.RooArgList(self._lShift),r.RooArgList(self._lMSD),lMData,0)
        # extended likelihood from normalization and shape above
        lEP     = r.RooExtendPdf(iLabel+"_passe_" +iBin,iLabel+"pe" +iBin,lP,lNPass)
        lEF     = r.RooExtendPdf(iLabel+"_faile_" +iBin,iLabel+"fe" +iBin,lF,lNFail)

        lHist   = [lP,lF,lEP,lEF,lPData,lMData]
        self._allVars.extend([lNTot,lNPass,lNFail])
        self._allShapes.extend(lHist)
        return lHist

    def getSignals(self,iHP,iHF,iBin):
        # get signals
        lPSigs  = []
        lFSigs  = []
        lPHists = [] 
        lFHists = [] 
        lVars=[125] #50,75,100,125,150,200,250,300]        
        sigs = ["hqq","zhqq","whqq","vbfhqq","tthqq"]
        for i0 in range(0,len(lVars)):            
            for i1, sig in enumerate(sigs):
                lSig = self.rooTheHistFunc([iHP[i0+i1+5],iHF[i0+i1+5]],sig+str(lVars[i0]),iBin)
                lPSigs.append(lSig[4])
                lFSigs.append(lSig[5])
        return (lPSigs,lFSigs)


    def makeWorkspace(self,iOutput,iDatas,iFuncs,iVars,iCat="cat0",iShift=True):

        lW = r.RooWorkspace("w_"+str(iCat))

        for pFunc in iFuncs:
            pFunc.Print()
            getattr(lW,'import')(pFunc, r.RooFit.RecycleConflictNodes())
            # if iShift and pFunc.GetName().find("qq") > -1:
            # 	(pFUp, pFDown)  = shift(iVars[0],pFunc,5.)
            # 	(pSFUp,pSFDown) = smear(iVars[0],pFunc,0.05)
            # 	getattr(lW,'import')(pFUp,  r.RooFit.RecycleConflictNodes())
            # 	getattr(lW,'import')(pFDown,r.RooFit.RecycleConflictNodes())
            # 	getattr(lW,'import')(pSFUp,  r.RooFit.RecycleConflictNodes())
            # 	getattr(lW,'import')(pSFDown,r.RooFit.RecycleConflictNodes())

        for pData in iDatas:
            pData.Print()
            getattr(lW,'import')(pData, r.RooFit.RecycleConflictNodes())

        if iCat.find("pass_cat1") == -1:
            lW.writeToFile(iOutput,False)
        else:
            lW.writeToFile(iOutput)	
        # lW.writeToFile(iOutput)	

##############################################################################
##############################################################################
#### E N D   O F   C L A S S
##############################################################################
##############################################################################

def main(options,args):
	
	ifile = options.ifile
	odir = options.odir

	# Load the input histograms
	# 	- 2D histograms of pass and fail mass,pT distributions
	# 	- for each MC sample and the data
	f = r.TFile.Open(ifile)
	(hpass,hfail) = loadHistograms(f,options.pseudo,options.blind,options.useQCD);

	# Build the workspacees
	dazsleRhalphabetBuilder(hpass,hfail,odir)

##-------------------------------------------------------------------------------------
def loadHistograms(f,pseudo,blind,useQCD):
    hpass = []
    hfail = []
    hpass.append(f.Get('data_obs_pass'))
    hfail.append(f.Get('data_obs_fail'))

    hpass_bkg = []
    hfail_bkg = []
    bkgs = ["wqq", "zqq", "qcd", "tqq"]
    for i, bkg in enumerate(bkgs):
        if bkg=='qcd':
            qcd_fail = f.Get('qcd_fail')
            if useQCD:
                qcd_pass = f.Get('qcd_pass')
            else:
                qcd_pass_real = f.Get('qcd_pass').Clone('qcd_pass_real')
                qcd_pass = qcd_fail.Clone('qcd_pass')
                qcd_pass_real_integral = 0
                qcd_fail_integral = 0
                for i in range(1,qcd_pass_real.GetNbinsX()+1):
                    for j in range(1,qcd_pass_real.GetNbinsY()+1):
                        if qcd_pass_real.GetXaxis().GetBinCenter(i) > MASS_LO and qcd_pass_real.GetXaxis().GetBinCenter(i) < MASS_HI:
                            qcd_pass_real_integral += qcd_pass_real.GetBinContent(i,j)
                            qcd_fail_integral += qcd_fail.GetBinContent(i,j)                   
                qcd_pass.Scale(qcd_pass_real_integral/qcd_fail_integral) # qcd_pass = qcd_fail * eff(pass)/eff(fail)
            hpass_bkg.append(qcd_pass)
            hfail_bkg.append(qcd_fail)
            print 'qcd pass integral', qcd_pass.Integral()
            print 'qcd fail integral', qcd_fail.Integral()
        else:            
            hpass_bkg.append(f.Get(bkg+'_pass'))
            hfail_bkg.append(f.Get(bkg+'_fail'))
        
    if pseudo:        
        hpass[0] = hpass_bkg[0].Clone('data_obs_pass')
        hfail[0] = hfail_bkg[0].Clone('data_obs_fail')
        for i, bkg in enumerate(bkgs):
            if i==0:
                continue # don't add again
            else:                
                hpass[0].Add(hpass_bkg[i])
                hfail[0].Add(hfail_bkg[i])        

    #signals
    hpass_sig = []
    hfail_sig = []
    masses=[125]#50,75,125,100,150,200,250,300]
    sigs = ["hqq","zhqq","whqq","vbfhqq","tthqq"]
    for mass in masses:
        for sig in sigs:
            passhist = f.Get(sig+str(mass)+"_pass").Clone()
            failhist = f.Get(sig+str(mass)+"_fail").Clone()
            for hist in [passhist, failhist]:
                for i in range(0,hist.GetNbinsX()+2):
                    for j in range(0,hist.GetNbinsY()+2):
                        if hist.GetBinContent(i,j) <= 0:
                            hist.SetBinContent(i,j,0)
            hpass_sig.append(passhist)            
            hfail_sig.append(failhist)
            #hpass_sig.append(f.Get(sig+str(mass)+"_pass"))

    hpass.extend(hpass_bkg)
    hpass.extend(hpass_sig)
    hfail.extend(hfail_bkg)
    hfail.extend(hfail_sig)
    
    for lH in (hpass+hfail):
        if blind:            
            for i in range(1,lH.GetNbinsX()+1):
                for j in range(1,lH.GetNbinsY()+1):
                    if lH.GetXaxis().GetBinCenter(i) > BLIND_LO and lH.GetXaxis().GetBinCenter(i) < BLIND_HI:
                        print "blinding signal region for %s, mass bin [%i,%i] "%(lH.GetName(),lH.GetXaxis().GetBinLowEdge(i),lH.GetXaxis().GetBinUpEdge(i))
                        lH.SetBinContent(i,j,0.)
                        print lH.GetBinContent(i,j)
        lH.SetDirectory(0)	

    # print "lengths = ", len(hpass), len(hfail)
    # print hpass;
    # print hfail;
    return (hpass,hfail)
    # return (hfail,hpass)

##-------------------------------------------------------------------------------------
if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
	parser.add_option('-i','--ifile', dest='ifile', default = 'hist_1DZbb.root',help='file with histogram inputs', metavar='ifile')
	parser.add_option('-o','--odir', dest='odir', default = './',help='directory to write plots', metavar='odir')
	parser.add_option('--pseudo', action='store_true', dest='pseudo', default =False,help='use MC', metavar='pseudo')
	parser.add_option('--blind', action='store_true', dest='blind', default =False,help='blind signal region', metavar='blind')
	parser.add_option('--use-qcd', action='store_true', dest='useQCD', default =False,help='use real QCD MC', metavar='useQCD')
	parser.add_option('--massfit', action='store_true', dest='massfit', default =False,help='mass fit or rho', metavar='massfit')
	parser.add_option('--freeze', action='store_true', dest='freeze', default =False,help='freeze pol values', metavar='freeze')
	
	(options, args) = parser.parse_args()

	import tdrstyle
	tdrstyle.setTDRStyle()
	r.gStyle.SetPadTopMargin(0.10)
	r.gStyle.SetPadLeftMargin(0.16)
	r.gStyle.SetPadRightMargin(0.10)
	r.gStyle.SetPalette(1)
	r.gStyle.SetPaintTextFormat("1.1f")
	r.gStyle.SetOptFit(0000)
	r.gROOT.SetBatch()
	
	main(options,args)
##-------------------------------------------------------------------------------------
