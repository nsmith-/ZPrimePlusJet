#!/usr/bin/env python

import ROOT as r,sys,math,array,os
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array

# including other directories
sys.path.insert(0, '../.')
from tools import *

class dazsleRhalphabetBuilder: 

	def __init__( self, hpass, hfail ): 

		self._hpass = hpass;
		self._hfail = hfail;

		self._outputName = "bern.root";

		self._mass_nbins = 60;
		self._mass_lo    = 30;
		self._mass_hi    = 330;

		#polynomial order for fit
		self._poly_lNP = 1;
		self._poly_lNR = 2;
		self._poly_lNRP = -1;

		self._nptbins = hpass[0].GetYaxis().GetNbins();
		self._pt_lo = hpass[0].GetYaxis().GetBinLowEdge( 1 );
		self._pt_hi = hpass[0].GetYaxis().GetBinUpEdge( self._nptbins );
	
		# define RooRealVars
		self._lMSD    = r.RooRealVar("x","x",self._mass_lo,self._mass_hi)
		self._lMSD.setBins(self._mass_nbins)		
		self._lPt     = r.RooRealVar("pt","pt",500,3000);
		self._lPt.setBins(self._nptbins)
		self._lRho    = r.RooFormulaVar("rho","log(x*x/pt)",r.RooArgList(self._lMSD,self._lPt))

		self._lEff    = r.RooRealVar("veff"      ,"veff"      ,0.5 ,0.,1.0)
		self._lEffQCD = r.RooRealVar("qcdeff"    ,"qcdeff"   ,0.01,0.,10.)
		self._lDM     = r.RooRealVar("dm","dm", 0.,-10,10)
		self._lShift  = r.RooFormulaVar("shift",self._lMSD.GetName()+"-dm",r.RooArgList(self._lMSD,self._lDM)) 

		self._allVars = [];
		self._allShapes = [];

		self.LoopOverPtBins();

	def LoopOverPtBins(self):

		print "number of pt bins = ", self._nptbins;
		for ipt in range(1,self._nptbins+1):
			print "------- pT bin number ",ipt		
			
			# 1d histograms in each pT bin
			hpass_inPtBin = [];
			hfail_inPtBin = [];
			for h in self._hpass: hpass_inPtBin.append( proj("cat",str(ipt),h,self._mass_nbins,self._mass_lo,self._mass_hi) ); 
			for h in self._hfail: hfail_inPtBin.append( proj("cat",str(ipt),h,self._mass_nbins,self._mass_lo,self._mass_hi) ); 

			# make RooDataset, RooPdfs, and histograms
			(pDatas,pPdfs,pHists) = self.workspaceInputs(hpass_inPtBin,hfail_inPtBin,"cat"+str(ipt),self._hpass[0].GetYaxis().GetBinCenter(ipt))
			#Get approximate pt bin value
			pPt = self._hpass[0].GetYaxis().GetBinLowEdge(ipt)+self._hpass[0].GetYaxis().GetBinWidth(ipt)*0.3;
			#Make the ralphabet fit for a specific pt bin
			lParHists = self.makeRhalph([hfail_inPtBin[4],hfail_inPtBin[0],hfail_inPtBin[1],hfail_inPtBin[2]],pPt,"cat"+str(ipt))
			
			#Get signals and SM backgrounds
			lPHists=[pHists[0],pHists[1],pHists[2]]
			lFHists=[pHists[3],pHists[4],pHists[5]]
			lPHists.extend(self.getSignals(hpass_inPtBin,hfail_inPtBin,"cat"+str(ipt))[0])
			lFHists.extend(self.getSignals(hpass_inPtBin,hfail_inPtBin,"cat"+str(ipt))[1])
			#Write to file
			self.makeWorkspace(self._outputName,[pDatas[0]],lPHists,self._allVars,"pass_cat"+str(ipt),True)
			self.makeWorkspace(self._outputName,[pDatas[1]],lFHists,self._allVars,"fail_cat"+str(ipt),True)
			
	def makeRhalph(self,iHs,iPt,iCat):
		
		lName ="qcd";
		lUnity = r.RooConstVar("unity","unity",1.);

		#Fix the pt (top) and teh qcd eff
		self._lPt.setVal(iPt)
		self._lEffQCD.setVal(0.02)
		self._lEffQCD.setConstant(False)

		polyArray = []
		self.buildPolynomialArray(polyArray,self._poly_lNP,self._poly_lNR,self._poly_lNRP,"p","r",-0.1,0.1)
		
		#Now build the function
		lPassBins = r.RooArgList()
		lFailBins = r.RooArgList()
		for i0 in range(1,self._mass_nbins+1):

			self._lMSD.setVal(iHs[0].GetXaxis().GetBinCenter(i0)) 
			lPass = self.buildRooPolyArray(self._lPt.getVal(),self._lRho.getVal(),lUnity,polyArray)
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
			lArg = r.RooArgList(pFail,lPass,self._lEffQCD)
			pPass = r.RooFormulaVar(lName+"_pass_"+iCat+"_Bin"+str(i0),lName+"_pass_"+iCat+"_Bin"+str(i0),"@0*max(@1,0)*@2",lArg)
			
			#If the number of events in the failing is small remove the bin from being free in the fit
			if pSum < 4:
				pFail.setConstant(True)
				pPass = r.RooRealVar   (lName+"_pass_"+iCat+"_Bin"+str(i0),lName+"_pass_"+iCat+"_Bin"+str(i0),0,0,0)
				pPass.setConstant(True)
			#Add bins to the array
			lPassBins.add(pPass)
			lFailBins.add(pFail)
			self._allVars.extend([pPass,pFail])
			# fPars.extend([pPass,pFail])
			# print  pFail.GetName(),"flatParam",lPass#,lPass+"/("+lFail+")*@0"

		lPass  = r.RooParametricHist(lName+"_pass_"+iCat,lName+"_pass_"+iCat,self._lMSD,lPassBins,iHs[0])
		lFail  = r.RooParametricHist(lName+"_fail_"+iCat,lName+"_fail_"+iCat,self._lMSD,lFailBins,iHs[0])
		lNPass = r.RooAddition(lName+"_pass_"+iCat+"_norm",lName+"_pass_"+iCat+"_norm",lPassBins)
		lNFail = r.RooAddition(lName+"_fail_"+iCat+"_norm",lName+"_fail_"+iCat+"_norm",lFailBins)
		self._allShapes.extend([lPass,lFail,lNPass,lNFail])
		
		#Now write the wrokspace with the rooparamhist
		lWPass = r.RooWorkspace("w_pass_"+str(iCat))
		lWFail = r.RooWorkspace("w_fail_"+str(iCat))
		getattr(lWPass,'import')(lPass,r.RooFit.RecycleConflictNodes())
		getattr(lWPass,'import')(lNPass,r.RooFit.RecycleConflictNodes())
		getattr(lWFail,'import')(lFail,r.RooFit.RecycleConflictNodes())
		getattr(lWFail,'import')(lNFail,r.RooFit.RecycleConflictNodes())
		if iCat.find("1") > -1:
			lWPass.writeToFile("ralpha"+self._outputName)
		else:
			lWPass.writeToFile("ralpha"+self._outputName,False)
		lWFail.writeToFile("ralpha"+self._outputName,False)
		return [lPass,lFail]

	def buildRooPolyArray(self,iPt,iRho,iQCD,iVars):
		
		lPt  = r.RooConstVar("Var_Pt_" +str(iPt)+"_"+str(iRho), "Var_Pt_" +str(iPt)+"_"+str(iRho),(iPt-500))
		lRho = r.RooConstVar("Var_Rho_"+str(iPt)+"_"+str(iRho), "Var_Rho_"+str(iPt)+"_"+str(iRho),(iRho-2.5))
		lRhoArray = r.RooArgList()
		lNCount=0
		for pRVar in range(0,self._poly_lNR):
			lTmpArray = r.RooArgList()
			lTmpArray.add(iQCD)
			pNP = self._poly_lNP if pRVar < self._poly_lNRP else 0
			for pVar in range(0,pNP):
				lTmpArray.add(iVars[lNCount])
				lNCount=lNCount+1
				print "----",iVars[lNCount].GetName()
			pLabel="Var_Pol_Bin_"+str(iPt)+"_"+str(iRho)+"_"+str(pRVar)
			pPol = r.RooPolyVar(pLabel,pLabel,lPt,lTmpArray)
			lRhoArray.add(pPol);
			self._allVars.append(pPol)
		lLabel="Var_RhoPol_Bin_"+str(iPt)+"_"+str(iRho)
		lRhoPol = r.RooPolyVar(lLabel,lLabel,lRho,lRhoArray)
		self._allVars.extend([lPt,lRho,lRhoPol])
		return lRhoPol

	def buildPolynomialArray(self, iVars,iNVar0,iNVar1,iNVar01,iLabel0,iLabel1,iXMin0,iXMax0):

		for i0 in range(0,iNVar1):
			for i1 in range(0,iNVar0):
				pVar    = iLabel0+iLabel1+str(i0)+str(i1)
				pXMin = iXMin0
				pXMax = iXMax0
				if i0 == 0: 
					pVar = iLabel0+str(i1)
				if i1 == 0: 
					pVar = iLabel1+str(i0)
				pRooVar = r.RooRealVar(pVar,pVar,0.0,pXMin,pXMax)
				iVars.append(pRooVar)	    

	def workspaceInputs(self, iHP,iHF,iBin,iPt):
		
		lCats = r.RooCategory("sample","sample") 
		lCats.defineType("pass",1) 
		lCats.defineType("fail",0) 
		lPData = r.RooDataHist("data_obs_pass_"+iBin,"data_obs_pass_"+iBin,r.RooArgList(self._lMSD),iHP[0])
		lFData = r.RooDataHist("data_obs_fail_"+iBin,"data_obs_fail_"+iBin,r.RooArgList(self._lMSD),iHF[0])
		lData  = r.RooDataHist("comb_data_obs","comb_data_obs",r.RooArgList(self._lMSD),r.RooFit.Index(lCats),r.RooFit.Import("pass",lPData),r.RooFit.Import("fail",lFData)) 

		lW    = self.rooTheHistFunc([iHP[0],iHF[0]],"wqq",iBin)
		lZ    = self.rooTheHistFunc([iHP[1],iHF[1]],"zqq",iBin)
		ltop  = self.rooTheHistFunc([iHP[2],iHF[2]],"tqq",iBin)		
		lQCD  = self.rooTheHistFunc([iHP[3],iHF[3]],"qcd",iBin)

		lTotP = r.RooAddPdf("tot_pass"+iBin,"tot_pass"+iBin,r.RooArgList(lQCD[0]))
		lTotF = r.RooAddPdf("tot_fail"+iBin,"tot_fail"+iBin,r.RooArgList(lQCD[1]))
		lEWKP = r.RooAddPdf("ewk_pass"+iBin,"ewk_pass"+iBin,r.RooArgList(lW[2],lZ[2],ltop[2]))
		lEWKF = r.RooAddPdf("ewk_fail"+iBin,"ewk_fail"+iBin,r.RooArgList(lW[3],lZ[3],ltop[3]))
		
		# lTot  = r.RooSimultaneous("tot","tot",lCats) 
		# lTot.addPdf(lTotP,"pass") 
		# lTot.addPdf(lTotF,"fail")     
		# fDatas.extend([lPData,lFData])
		# fFuncs.extend([lTotP,lTotF,lEWKP,lEWKF])

		## find out which to make global
		return ([lPData,lFData],[lTotP,lTotF,lEWKP,lEWKF],[lW[4],lZ[4],ltop[4],lW[5],lZ[5],ltop[5]])

	def getSignals(self,iHP,iHF,iBin):
		
		lPSigs  = []
		lFSigs  = []
		lPHists = [] 
		lFHists = [] 
		lVars=[125]
		for i0 in range(0,len(lVars)):
			lPHists.append(iHP[i0+3])
			lFHists.append(iHF[i0+3])
			lSig = self.rooTheHistFunc([lPHists[i0],lFHists[i0]],"zqq"+str(lVars[i0]),iBin)
			lPSigs.append(lSig[4])
			lFSigs.append(lSig[5])
		# lPHist = rooTheHistFunc(lVars,lPHists)
		# lFHist = rooTheHistFunc(lVars,lFHists)
		# masses=[50,60,75,90,100,112,125,140,150,160,170,180,190,200,210,220,230,240,250,260,270,280,290]
		# for i0 in range(0,len(masses)):
		# 	pHP   = lPHist.morph(masses[i0])
		# 	pHF   = lFHist.morph(masses[i0])
		# 	for i1 in range(0,len(lVars)):
		# 		if lVars[i1] == masses[i0]:
		# 			pHP=iHP[i1+3]
		# 			pHF=iHF[i1+3]
		# 	lSig = self.rooTheHistFunc([pHP,pHF],"zqq"+str(masses[i0]),iBin)
		# 	lPSigs.append(lSig[4])
		# 	lFSigs.append(lSig[5])
		return (lPSigs,lFSigs)

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

	def makeWorkspace(self,iOutput,iDatas,iFuncs,iVars,iCat="cat0",iShift=True):
		
		lW = r.RooWorkspace("w_"+str(iCat))
		
		print "datas"
		for pData in iDatas:
			print pData.GetName(),pData
			getattr(lW,'import')(pData,r.RooFit.RecycleConflictNodes())
		
		print "shapes"
		for pFunc in iFuncs:
			print pFunc.GetName(),pFunc
			getattr(lW,'import')(pFunc,r.RooFit.RecycleConflictNodes())
			# if iShift and pFunc.GetName().find("qq") > -1:
			# 	(pFUp, pFDown)  = shift(iVars[0],pFunc,5.)
			# 	(pSFUp,pSFDown) = smear(iVars[0],pFunc,0.05)
			# 	getattr(lW,'import')(pFUp,  r.RooFit.RecycleConflictNodes())
			# 	getattr(lW,'import')(pFDown,r.RooFit.RecycleConflictNodes())
			# 	getattr(lW,'import')(pSFUp,  r.RooFit.RecycleConflictNodes())
			# 	getattr(lW,'import')(pSFDown,r.RooFit.RecycleConflictNodes())
		
		if iCat.find("pass_cat1") == -1:
			lW.writeToFile(iOutput,False)
		else:
			lW.writeToFile(iOutput)		

##############################################################################
##############################################################################
##############################################################################
##############################################################################

def main(options,args):
	
	idir = options.idir
	odir = options.odir
	lumi = options.lumi

	# Load the input histograms
	# 	- 2D histograms of pass and fail mass,pT distributions
	# 	- for each MC sample and the data
	f = r.TFile("../hists_1D.root");
	(hpass,hfail) = loadHistograms(f,options.pseudo);

	# Build the workspacees
	dazsleRhalphabetBuilder(hpass,hfail);

##-------------------------------------------------------------------------------------
def loadHistograms(f,pseudo):

	hpass = [];
	hfail = [];

	hpass.append( f.Get("wqq_pass") )
	hpass.append( f.Get("zqq_pass") )
	hpass.append( f.Get("tqq_pass") )
	hpass.append( f.Get("qcd_pass") )

	hfail.append( f.Get("wqq_fail") )
	hfail.append( f.Get("zqq_fail") )
	hfail.append( f.Get("tqq_fail") )
	hfail.append( f.Get("qcd_fail") )

	if pseudo:
		hpass_data   = f.Get("wqq_pass");
		hpass_data.Add(f.Get("zqq_pass"));
		hpass_data.Add(f.Get("tqq_pass"));
		hpass_data.Add(f.Get("qcd_pass"));
		hpass.append(hpass_data);
		hfail_data   = f.Get("wqq_fail");
		hfail_data.Add(f.Get("zqq_fail"));
		hfail_data.Add(f.Get("tqq_fail"));
		hfail_data.Add(f.Get("qcd_fail"));
		hfail.append(hfail_data);
	else:
		hpass.append( f.Get("data_obs_pass") );
		hfail.append( f.Get("data_obs_fail") );

	# masses=[50,75,100,125,150,200,250,300]
	masses=[125];
	for mass in masses:
		hpass.append(f.Get("hqq_"+str(mass)+"_pass"))
		hfail.append(f.Get("hqq_"+str(mass)+"_fail"))

	return (hpass,hfail);

# ##-------------------------------------------------------------------------------------    
# def buildCardsAndWorkspaces(hpass,hfail):


# 	# setup
# 	nptbins = hpass[0].GetYaxis().GetNbins();
# 	mass_nbins = 60;
# 	mass_lo    = 30;
# 	mass_hi    = 330;
# 	rrv_msd = ROOT.RooRealVar("x","x",mass_lo,mass_hi);
# 	rrv_msd.setBins(mass_nbins);
#     lBase = baseVars(rrv_msd,nptbins);

# 	# make a card for each pT bin
# 	for ipt in range(1,nptbins+1):
		
# 		# 1d histograms in each pT bin
# 		hpass_inPtBin = [];
# 		hfail_inPtBin = [];
# 		for h in hpass: hpass_inPtBin.append( proj("cat",str(ipt),h,mass_nbins,mass_lo,mass_hi) ); 
# 		for h in hfail: hhfail_inPtBin.append( proj("cat",str(ipt),h,mass_nbins,mass_lo,mass_hi) ); 

# 		# make RooDataset, RooPdfs, and histograms

#         (pDatas,pPdfs,pHists) = cat(hpass_inPtBin,hfail_inPtBin,"cat"+str(ipt),lBase,hpass[0].GetYaxis().GetBinCenter(ipt),0)

##########
## helpers
##########

# def cat(iHP,iHF,iBin,iBase,iPt,iFunc):
	
# 	lCats = r.RooCategory("sample","sample") 
# 	lCats.defineType("pass",1) 
# 	lCats.defineType("fail",0) 
# 	lPData = r.RooDataHist("data_obs_pass_"+iBin,"data_obs_pass_"+iBin,r.RooArgList(iBase[0]),iHP[0])
# 	lFData = r.RooDataHist("data_obs_fail_"+iBin,"data_obs_fail_"+iBin,r.RooArgList(iBase[0]),iHF[0])
# 	lData  = r.RooDataHist("comb_data_obs","comb_data_obs",r.RooArgList(iBase[0]),r.RooFit.Index(lCats),r.RooFit.Import("pass",lPData),r.RooFit.Import("fail",lFData)) 

# 	lW    = histFunc([iHP[1],iHF[1]],iBase,"wqq",iBin)
# 	lZ    = histFunc([iHP[2],iHF[2]],iBase,"zqq",iBin)
# 	ltop  = histFunc([iHP[3],iHF[3]],iBase,"tqq",iBin)		
# 	lQCD  = histFunc([iHP[5],iHF[5]],iBase,"qcd",iBin)
# 	lTotP = r.RooAddPdf("tot_pass"+iBin,"tot_pass"+iBin,r.RooArgList(lQCD[0]))
# 	lTotF = r.RooAddPdf("tot_fail"+iBin,"tot_fail"+iBin,r.RooArgList(lQCD[1]))
# 	lEWKP = r.RooAddPdf("ewk_pass"+iBin,"ewk_pass"+iBin,r.RooArgList(lW[2],lZ[2],ltop[2]))
# 	lEWKF = r.RooAddPdf("ewk_fail"+iBin,"ewk_fail"+iBin,r.RooArgList(lW[3],lZ[3],ltop[3]))
# 	lTot  = r.RooSimultaneous("tot","tot",lCats) 
# 	lTot.addPdf(lTotP,"pass") 
# 	lTot.addPdf(lTotF,"fail")     
# 	fDatas.extend([lPData,lFData])
# 	fFuncs.extend([lTotP,lTotF,lEWKP,lEWKF])
# 	return ([lPData,lFData],[lTotP,lTotF,lEWKP,lEWKF],[lW[4],lZ[4],ltop[4],lW[5],lZ[5],ltop[5]])

# def baseVars(rrv_msd, iPtBins):
	
# 	lMSD = rrv_msd;
	
# 	lPt = r.RooRealVar   ("pt","pt",500,3000)
# 	lPt .setBins(iPtBins)

# 	lEff    = r.RooRealVar("veff"      ,"veff"      ,0.5 ,0.,1.0)
# 	lEffQCD = r.RooRealVar("qcdeff"    ,"qcdeff"   ,0.01,0.,10.)
# 	lDM     = r.RooRealVar("dm","dm", 0.,-10,10)
# 	lShift  = r.RooFormulaVar("shift",lMSD.GetName()+"-dm",r.RooArgList(lMSD,lDM))  
# 	lVars=[lMSD,lEff,lEffQCD,lDM,lShift,lPt]
# 	fVars.extend([lMSD,lPt,lEff,lEffQCD,lDM])
# 	fPars.extend([lEffQCD,lDM,lEff])
# 	return lVars

##-------------------------------------------------------------------------------------
if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
	parser.add_option("--lumi", dest="lumi", type=float, default = 30,help="luminosity", metavar="lumi")
	parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
	parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
	parser.add_option('--pseudo', action='store_true', dest='pseudo', default =False,help='signal comparison', metavar='isData')

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
