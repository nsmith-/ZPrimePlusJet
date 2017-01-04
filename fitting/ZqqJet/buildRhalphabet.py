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

##############################################################################
##############################################################################
#### B E G I N N I N G   O F   C L A S S
##############################################################################
##############################################################################

class dazsleRhalphabetBuilder: 

	def __init__( self, hpass, hfail ): 

		self._hpass = hpass;
		self._hfail = hfail;

		self._outputName = "base.root";

		self._mass_nbins = 16;
		self._mass_lo    = 2*(500/75.);
		self._mass_hi    = 42*(500/75.);

		print "number of mass bins and lo/hi: ", self._mass_nbins, self._mass_lo, self._mass_hi;

		#polynomial order for fit
		self._poly_lNP = 2; # 1 means linear, 2 means quadratic
		self._poly_lNR = 2;
		# self._poly_lNRP =2;

		self._nptbins = hpass[0].GetYaxis().GetNbins();
		self._pt_lo = hpass[0].GetYaxis().GetBinLowEdge( 1 );
		self._pt_hi = hpass[0].GetYaxis().GetBinUpEdge( self._nptbins );
	
		# define RooRealVars
		self._lMSD    = r.RooRealVar("x","x",self._mass_lo,self._mass_hi)
		self._lMSD.setBins(self._mass_nbins)		
		self._lPt     = r.RooRealVar("pt","pt",self._pt_lo,self._pt_hi);
		self._lPt.setBins(self._nptbins)
		self._lRho    = r.RooFormulaVar("rho","log(x*x/pt/pt)",r.RooArgList(self._lMSD,self._lPt))

		self._lEff    = r.RooRealVar("veff"      ,"veff"      ,0.5 ,0.,1.0)
		self._lEffQCD = r.RooRealVar("qcdeff"    ,"qcdeff"   ,0.01,0.,10.)
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
			
			#Make the ralphabet fit for a specific pt bin
			#lParHists = self.makeRhalph([hfail_inPtBin[0],hfail_inPtBin[1],hfail_inPtBin[2],hfail_inPtBin[4]],pPt,"cat"+str(ipt))
			lParHists = self.makeRhalph([hfail_inPtBin[0],hfail_inPtBin[1],hfail_inPtBin[2],hfail_inPtBin[4]],[hpass_inPtBin[0],hpass_inPtBin[1],hpass_inPtBin[2],hpass_inPtBin[4]],pPt,"cat"+str(ipt))			
			
			# #Get signals and SM backgrounds
			lPHists=[pHists[0],pHists[1],pHists[2]]
			lFHists=[pHists[3],pHists[4],pHists[5]]
			lPHists.extend(self.getSignals(hpass_inPtBin,hfail_inPtBin,"cat"+str(ipt))[0])
			lFHists.extend(self.getSignals(hpass_inPtBin,hfail_inPtBin,"cat"+str(ipt))[1])
			# #Write to file
			self.makeWorkspace(self._outputName,[pDatas[0]],lPHists,self._allVars,"pass_cat"+str(ipt),True)
			self.makeWorkspace(self._outputName,[pDatas[1]],lFHists,self._allVars,"fail_cat"+str(ipt),True)

		for ipt in range(1,self._nptbins+1):
			for imass in range(1,self._mass_nbins):
				print "qcd_fail_cat%i_Bin%i flatParam" % (ipt,imass);
			
	def makeRhalph(self,iHs,iHPs,iPt,iCat):
		
		print "---- [makeRhalph]"	

		lName ="qcd";
		lUnity = r.RooConstVar("unity","unity",1.);
		lZero  = r.RooConstVar("lZero","lZero",0.);

		#Fix the pt (top) and teh qcd eff
		self._lPt.setVal(iPt)
		self._lEffQCD.setVal(0.05)
		self._lEffQCD.setConstant(False)

		polyArray = []
		self.buildPolynomialArray(polyArray,self._poly_lNR,self._poly_lNP,"r","p",-0.1,0.1)
		print polyArray;

		#Now build the function
		lPassBins = r.RooArgList()
		lFailBins = r.RooArgList()
		
		for i0 in range(1,self._mass_nbins+1):

			self._lMSD.setVal(iHs[0].GetXaxis().GetBinCenter(i0)) 
			lPass = self.buildRooPolyArray(self._lPt.getVal(),self._lRho.getVal(),lUnity,lZero,polyArray)
			pSum = 0
			for i1 in range(0,len(iHs)):
				pSum = pSum + iHs[i1].GetBinContent(i0) if i1 == 0 else pSum - iHs[i1].GetBinContent(i0); # subtract W/Z from data
			if pSum < 0: pSum = 0

			#5 sigma range + 10 events
			pUnc = math.sqrt(pSum)*5+10
			#Define the failing category
			pFail = r.RooRealVar(lName+"_fail_"+iCat+"_Bin"+str(i0),lName+"_fail_"+iCat+"_Bin"+str(i0),pSum,max(pSum-pUnc,0),max(pSum+pUnc,0))
			#Now define the passing cateogry based on the failing (make sure it can't go negative)
			lArg = r.RooArgList(pFail,lPass,self._lEffQCD)
			pPass = r.RooFormulaVar(lName+"_pass_"+iCat+"_Bin"+str(i0),lName+"_pass_"+iCat+"_Bin"+str(i0),"@0*max(@1,0)*@2",lArg)
			
			print pPass.Print();
			# print pPass.GetName();
			pSumP = 0
			for i1 in range(0,len(iHPs)):
			        pSumP = pSumP + iHPs[i1].GetBinContent(i0) if i1 == 0 else pSumP - iHPs[i1].GetBinContent(i0); # subtract W/Z from data 
			if pSumP < 0: pSumP = 0

			#If the number of events in the failing is small remove the bin from being free in the fit
			if pSum < 4 and pSumP < 4:
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

	def buildRooPolyArray(self,iPt,iRho,iQCD,iZero,iVars):
		
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
		
		for i0 in range(iNVar0+1):
			for i1 in range(iNVar1+1):
				pVar = iLabel1+str(i1)+iLabel0+str(i0);		
				pXMin = iXMin0
				pXMax = iXMax0
				pRooVar = r.RooRealVar(pVar,pVar,0.0,pXMin,pXMax)
				print pVar
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
		ltop  = self.rooTheHistFunc([iHP[4],iHF[4]],"tqq",iBin)		
		lQCD  = self.rooTheHistFunc([iHP[3],iHF[3]],"qcd",iBin)

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
			
		lPSigs  = []
		lFSigs  = []
		lPHists = [] 
		lFHists = [] 
		lVars=[50,75,100,125,150,200,250,300]
		for i0 in range(0,len(lVars)):
			# lPHists.append(iHP[i0+4])
			# lFHists.append(iHF[i0+4])
			lSig = self.rooTheHistFunc([iHP[i0+5],iHF[i0+5]],"zqq"+str(lVars[i0]),iBin)
			lPSigs.append(lSig[4])
			lFSigs.append(lSig[5])
		# lPHist = hist(lVars,lPHists)
		# lFHist = hist(lVars,lFHists)
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

		# 	lSig[4].Print();
		# 	lSig[5].Print();

		return (lPSigs,lFSigs)		

	def makeWorkspace(self,iOutput,iDatas,iFuncs,iVars,iCat="cat0",iShift=True):
		
		lW = r.RooWorkspace("w_"+str(iCat))

		for pFunc in iFuncs:
			getattr(lW,'import')(pFunc,r.RooFit.RecycleConflictNodes())
			# if iShift and pFunc.GetName().find("qq") > -1:
			# 	(pFUp, pFDown)  = shift(iVars[0],pFunc,5.)
			# 	(pSFUp,pSFDown) = smear(iVars[0],pFunc,0.05)
			# 	getattr(lW,'import')(pFUp,  r.RooFit.RecycleConflictNodes())
			# 	getattr(lW,'import')(pFDown,r.RooFit.RecycleConflictNodes())
			# 	getattr(lW,'import')(pSFUp,  r.RooFit.RecycleConflictNodes())
			# 	getattr(lW,'import')(pSFDown,r.RooFit.RecycleConflictNodes())

		for pData in iDatas:
			getattr(lW,'import')(pData,r.RooFit.RecycleConflictNodes())
		
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
	
	idir = options.idir
	odir = options.odir
	lumi = options.lumi

	# Load the input histograms
	# 	- 2D histograms of pass and fail mass,pT distributions
	# 	- for each MC sample and the data
	f = r.TFile(options.input);
	(hpass,hfail) = loadHistograms(f,options.pseudo);

	# Build the workspacees
	dazsleRhalphabetBuilder(hpass,hfail);

##-------------------------------------------------------------------------------------
def loadHistograms(f,pseudo):

	hpass = [];
	hfail = [];

	lHP0 = f.Get("data_obs_pass")
	lHF0 = f.Get("data_obs_fail")
	lHP1 = f.Get("wqq_pass")
	lHF1 = f.Get("wqq_fail")
	lHP2 = f.Get("zqq_pass")
	lHF2 = f.Get("zqq_fail")
	lHP3 = f.Get("qcd_pass")
	lHF3 = f.Get("qcd_fail")
	lHP4 = f.Get("tqq_pass")
	lHF4 = f.Get("tqq_fail")
	if pseudo:
		# lHP0 = lHP3.Clone("qcd_pass")
		lHF0 = lHF3.Clone("qcd_fail")
		lHF0.Add(lHF1)
		lHF0.Add(lHF2)
		lHF0.Add(lHF4)
		lHP0 = lHF3.Clone("qcd_pass");
		lHP0.Scale(0.05);
		lHP0.Add(lHP1)
		lHP0.Add(lHP2)
		lHP0.Add(lHP4)

	hpass.extend([lHP0,lHP1,lHP2])
	hfail.extend([lHF0,lHF1,lHF2])
	hpass.extend([lHP3,lHP4])
	hfail.extend([lHF3,lHF4])

	#signals
	masses=[50,75,100,125,150,200,250,300]
	for mass in masses:
		hpass.append(f.Get("zqq"+str(mass)+"_pass"))
		hfail.append(f.Get("zqq"+str(mass)+"_fail"))

	for lH in (hpass+hfail):
		lH.SetDirectory(0)	
		print lH.GetName(), lH.Integral()

	# print "lengths = ", len(hpass), len(hfail)
	# print hpass;
	# print hfail;
	return (hpass,hfail);
	# return (hfail,hpass);

##-------------------------------------------------------------------------------------
if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
	parser.add_option("--lumi", dest="lumi", type=float, default = 30,help="luminosity", metavar="lumi")
	parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
	parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
	parser.add_option('--pseudo', action='store_true', dest='pseudo', default =False,help='signal comparison', metavar='isData')
	parser.add_option('--input', dest='input', default = 'hist_1DZqq.root',help='directory with data', metavar='idir')

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
