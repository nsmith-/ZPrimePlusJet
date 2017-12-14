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
r.gROOT.Macro(os.path.expanduser('~/rootlogon.C'))
# including other directories
sys.path.insert(0, '../.')
from tools import *
from hist import *

TT_SF = 0.83
W_SF = 1.35
DY_SF = 1.45
W_SF = 1.35
V_SF = 0.891
V_SF_ERR = 0.066


fHists=[]
##############################################################################
##############################################################################
#### B E G I N N I N G   O F   C L A S S
##############################################################################
##############################################################################
def scaleHists(iHist,iType,iPassId):
	if iPassId == 1:
		iHist.Scale(V_SF)
	#if iPassId == 2:
	        #iHist.Scale(1./(1.-0.11*(0.3/0.7)))
		#iHist.Scale(1.009)
	if iType == 0:
		iHist.Scale(DY_SF)

	if iType == 0 and iPassId > 0: #w boson
		#wscale=[1.0,1.05,1.05,1.25,1.25,1.25,1.0]
		wscale=[1.0,1.0,1.0,1.20,1.25,1.25,1.0]
		for i0 in range(1,iHist.GetNbinsX()+1):
			for i1 in range(1,iHist.GetNbinsY()+1):
				iHist.SetBinContent(i0,i1,iHist.GetBinContent(i0,i1)*wscale[i1])
	if iType == 1 and iPassId > 0: 
		# correcting Z *was scaled by W_SF*
		iHist.Scale(DY_SF/W_SF)

class dazsleRhalphabetBuilder: 

	def __init__( self, hpass, hfail, inputfile ): 

		self._hpass = hpass;
		self._hfail = hfail;
		self._inputfile = inputfile;

		self._outputName = "base.root";
		self._outfile_validation = r.TFile("validation.root","RECREATE");

		self._mass_nbins = 60;
		self._mass_lo    = 30;
		self._mass_hi    = 330;

		print "number of mass bins and lo/hi: ", self._mass_nbins, self._mass_lo, self._mass_hi;

		# polynomial order for fit
		self._poly_lNP = 3; # 3rd order in pT
		self._poly_lNR = 4; # 4th order in rho

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
		self._lEffQCD = r.RooRealVar("qcdeff"    ,"qcdeff"    ,0.1 ,0.,1.0)
		self._lDM     = r.RooRealVar("dm","dm", 0.,-10,10)
		self._lShift  = r.RooFormulaVar("shift",self._lMSD.GetName()+"-dm",r.RooArgList(self._lMSD,self._lDM)) 

		self._allVars = [];
		self._allShapes = [];
		self._allData = [];
		self._allPars = [];

		self.LoopOverPtBins();

	def LoopOverPtBins(self):

		print "number of pt bins = ", self._nptbins;
		# loop over 5 pt bins, cat 1: pt500-600, cat 2: pt600-700, cat 3: pt700-800, cat 4: pt800-900, cat5: pt900-1000
		for ipt in range(1,self._nptbins+1):
			print "------- pT bin number ",ipt		
			
			# 1d histograms in each pT bin (in the order... data, w, z, qcd, top, signals)
			hpass_inPtBin = [];
			hfail_inPtBin = [];
			for ih,h in enumerate(self._hpass):
				tmppass_inPtBin = proj("cat",str(ipt),h,self._mass_nbins,self._mass_lo,self._mass_hi)
				# remove low mass and high mass (cat 1 if m>185, cat 2 if m>220 or m<50, cat 3 if m>260 or m<55, cat4 if m>310 or m<65, cat5 if m<65)
				for i0 in range(1,self._mass_nbins+1):
					if ((i0 > 31 or i0 < 0) and ipt == 1) or ((i0 > 38 or i0 < 4) and ipt == 2) or ((i0 > 46 or i0 < 5) and ipt == 3) or ((i0 > 56 or i0 < 7) and ipt == 4) or (i0 < 7 and ipt == 5):
						tmppass_inPtBin.SetBinContent(i0,0);
				hpass_inPtBin.append( tmppass_inPtBin )
                        for ih,h in enumerate(self._hfail):
                                tmpfail_inPtBin = proj("cat",str(ipt),h,self._mass_nbins,self._mass_lo,self._mass_hi); 
				# remove low mass and high mass (cat 1 if m>185, cat 2 if m>220 or m<50, cat 3 if m>260 or m<55, cat4 if m>310 or m<65, cat5 if m<65)
				for i0 in range(1,self._mass_nbins+1):
					if ((i0 > 31 or i0 < 0) and ipt == 1) or ((i0 > 38 or i0 < 4) and ipt == 2) or ((i0 > 46 or i0 < 5) and ipt == 3) or ((i0 > 56 or i0 < 7 ) and ipt == 4) or (i0 < 7 and ipt == 5):
						tmpfail_inPtBin.SetBinContent(i0,0);
                                hfail_inPtBin.append( tmpfail_inPtBin ) 
			
			# make RooDataset, RooPdfs, and histograms
			(pDatas,pPdfs,pHists) = self.workspaceInputs(hpass_inPtBin,hfail_inPtBin,"cat"+str(ipt))
			# get approximate pt bin value
			pPt = self._hpass[0].GetYaxis().GetBinLowEdge(ipt)+self._hpass[0].GetYaxis().GetBinWidth(ipt)*0.3;
			
			# make the ralphabet fit for this specific pt bin
			lParHists = self.makeRhalph([hfail_inPtBin[0],hfail_inPtBin[1],hfail_inPtBin[2],hfail_inPtBin[4]],[hpass_inPtBin[0],hpass_inPtBin[1],hpass_inPtBin[2],hpass_inPtBin[4]],pPt,"cat"+str(ipt))			
			
			# get signals and SM backgrounds
			lPHists=[pHists[0],pHists[1],pHists[2],pHists[3]]
			lFHists=[pHists[4],pHists[5],pHists[6],pHists[7]]
			lPHists.extend(self.getSignals(hpass_inPtBin,hfail_inPtBin,"cat"+str(ipt))[0])
			lFHists.extend(self.getSignals(hpass_inPtBin,hfail_inPtBin,"cat"+str(ipt))[1])
			# write to file
			self.makeWorkspace(self._outputName,[pDatas[0]],lPHists,self._allVars,"pass_cat"+str(ipt),True)
			self.makeWorkspace(self._outputName,[pDatas[1]],lFHists,self._allVars,"fail_cat"+str(ipt),True)

		self._outfile_validation.Write();
		self._outfile_validation.Close();
		#for ipt in range(1,self._nptbins+1):
		#	for imass in range(1,self._mass_nbins):
		#		print "qcd_fail_cat%i_Bin%i flatParam" % (ipt,imass);
			
	def makeRhalph(self,iHs,iHPs,iPt,iCat):
		
		print "---- [makeRhalph]"	

		lName ="qcd";
		lUnity = r.RooConstVar("unity","unity",1.);
		lZero  = r.RooConstVar("lZero","lZero",0.);

		# fix the pt (top) and the qcd eff
		self._lPt.setVal(iPt)
		self._lEffQCD.setVal(0.05)
		self._lEffQCD.setConstant(False)

		# build polynomial array with n = (order in pt)*(order in rho) parameters
		polyArray = []
		self.buildPolynomialArray(polyArray,self._poly_lNR,self._poly_lNP,"r","p",-1.0,1.0)
		#print polyArray;

		# now build the function
		lPassBins = r.RooArgList()
		lFailBins = r.RooArgList()
		for i0 in range(1,self._mass_nbins+1):
			self._lMSD.setVal(iHs[0].GetXaxis().GetBinCenter(i0)) 
			lPass = self.buildRooPolyArray(self._lPt.getVal(),self._lRho.getVal(),lUnity,lZero,polyArray)
			pSum = 0
			pRes = 0

			for i1 in range(0,len(iHs)):
				pSum = pSum + iHs[i1].GetBinContent(i0) if i1 == 0 else pSum - iHs[i1].GetBinContent(i0); # subtract W/Z from data
				if i1 > 0 : pRes += iHs[i1].GetBinContent(i0)
			if pSum < 0: pSum = 0

			# 10 sigma range + 10 events
			pUnc = math.sqrt(pSum)*10.+10
			#pUnc = math.sqrt(pSum)*3.+10
			pUnc += pRes

			# define the failing category
			pFail = r.RooRealVar(lName+"_fail_"+iCat+"_Bin"+str(i0),lName+"_fail_"+iCat+"_Bin"+str(i0),pSum,max(pSum-pUnc,0),max(pSum+pUnc,0))
			# now define the passing cateogry based on the failing (make sure it can't go negative)
			lArg = r.RooArgList(pFail,lPass,self._lEffQCD)
			pPass = r.RooFormulaVar(lName+"_pass_"+iCat+"_Bin"+str(i0),lName+"_pass_"+iCat+"_Bin"+str(i0),"@0*max(@1,0)*@2",lArg)
			
			#print pPass.Print();
			#print pPass.GetName();
			pSumP = 0
			for i1 in range(0,len(iHPs)):
			        pSumP = pSumP + iHPs[i1].GetBinContent(i0) if i1 == 0 else pSumP - iHPs[i1].GetBinContent(i0); # subtract W/Z from data 
			if pSumP < 0: pSumP = 0

			# if the number of events in the failing is small remove the bin from being free in the fit
			if pSum < 5 and pSumP < 5:
				pFail = r.RooRealVar(lName+"_pass_"+iCat+"_Bin"+str(i0),lName+"_pass_"+iCat+"_Bin"+str(i0),pSum ,0.,max(pSum,0.1))
				pFail.setConstant(True)
				pPass = r.RooRealVar(lName+"_pass_"+iCat+"_Bin"+str(i0),lName+"_pass_"+iCat+"_Bin"+str(i0),pSumP,0.,max(pSumP,0.1))
				pPass.setConstant(True)

			# add bins to the array
			lPassBins.add(pPass)
			lFailBins.add(pFail)
			self._allVars.extend([pPass,pFail])
			self._allPars.extend([pPass,pFail])
			#print  pFail.GetName(),"flatParam",lPass#,lPass+"/("+lFail+")*@0"

		lPass  = r.RooParametricHist(lName+"_pass_"+iCat,lName+"_pass_"+iCat,self._lMSD,lPassBins,iHs[0])
		lFail  = r.RooParametricHist(lName+"_fail_"+iCat,lName+"_fail_"+iCat,self._lMSD,lFailBins,iHs[0])
		lNPass = r.RooAddition(lName+"_pass_"+iCat+"_norm",lName+"_pass_"+iCat+"_norm",lPassBins)
		lNFail = r.RooAddition(lName+"_fail_"+iCat+"_norm",lName+"_fail_"+iCat+"_norm",lFailBins)
		self._allShapes.extend([lPass,lFail,lNPass,lNFail])
		
		# now write the workspace with the rooparamhist
		lWPass = r.RooWorkspace("w_pass_"+str(iCat))
		lWFail = r.RooWorkspace("w_fail_"+str(iCat))
		getattr(lWPass,'import')(lPass,r.RooFit.RecycleConflictNodes())
		getattr(lWPass,'import')(lNPass,r.RooFit.RecycleConflictNodes())
		getattr(lWFail,'import')(lFail,r.RooFit.RecycleConflictNodes())
		getattr(lWFail,'import')(lNFail,r.RooFit.RecycleConflictNodes())
		if iCat.find("1") > -1:
			lWPass.writeToFile("ralpha"+self._outputName+"_"+str(self._poly_lNP)+str(self._poly_lNR)+"_pt")
		else:
			lWPass.writeToFile("ralpha"+self._outputName+"_"+str(self._poly_lNP)+str(self._poly_lNR)+"_pt",False)
		lWFail.writeToFile("ralpha"+self._outputName,False)
		return [lPass,lFail]

	def buildRooPolyArray(self,iPt,iRho,iQCD,iZero,iVars):
		
		#print "---- [buildRooPolyArray]"	
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
			#print pPol.Print()
			lRhoArray.add(pPol);
			self._allVars.append(pPol)

		lLabel="Var_RhoPol_Bin_"+str(round(iPt,2))+"_"+str(round(iRho,3))
		lRhoPol = r.RooPolyVar(lLabel,lLabel,lRho,lRhoArray)
		self._allVars.extend([lPt,lRho,lRhoPol])
		return lRhoPol

	def buildPolynomialArray(self, iVars,iNVar0,iNVar1,iLabel0,iLabel1,iXMin0,iXMax0):

		#print "---- [buildPolynomialArray]"
		## form of polynomial
		## (p0r0 + p1r0 * pT + p2r0 * pT^2 + ...) + 
		## (p0r1 + p1r1 * pT + p2r1 * pT^2 + ...) * rho + 
		## (p0r2 + p1r2 * pT + p2r2 * pT^2 + ...) * rho^2 + ...
		# Set to the background only
		lFile = r.TFile("mlfit_param.root")
		lFit  = r.RooFitResult(lFile.Get("fit_b"))
		self._lEffQCD.setVal(lFit.floatParsFinal().find("qcdeff").getVal())
		for i0 in range(iNVar0+1):
                       for i1 in range(iNVar1+1):
                               pVar = iLabel1+str(i1)+iLabel0+str(i0);
                               pXMin = iXMin0
                               pXMax = iXMax0
                               pVal  = math.pow(10,-min(i1,2))
                               #pVal  = math.pow(10,-i1-i0)
			       if i1 == 0:
				       pVal  = math.pow(10,-i1-min(int(i0*0.5),1))
			       pCent = 0 if pVar == "p0r0" else lFit.floatParsFinal().find(pVar).getVal()
                               pRooVar = r.RooRealVar(pVar,pVar,pCent,pXMin*pVal,pXMax*pVal)
                               #print pVar,pVal,"!!!!!!!!!!"
                               iVars.append(pRooVar)
		lFile.Close()

	def workspaceInputs(self, iHP,iHF,iBin):
		
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
		## RooDataHist (data), then RooAbsPdf (qcd,ewk+top), then RooDataHist of each ewk+top
		return ([lPData,lFData],[lTotP,lTotF,lEWKP,lEWKF],[lW[4],lZ[4],ltop[4],lQCD[4],lW[5],lZ[5],ltop[5],lQCD[5]])

	def rooTheHistFunc(self,iH,iLabel="w",iBin="_cat0"):

		#normalization
		lNTot   = r.RooRealVar (iLabel+"norm"+iBin,iLabel+"norm"+iBin,(iH[0].Integral()+iH[1].Integral()),0.,5.*(iH[0].Integral()+iH[1].Integral()))
		lNPass  = r.RooFormulaVar(iLabel+"fpass"+iBin ,iLabel+"norm"+iBin+"*(veff)"  ,r.RooArgList(lNTot,self._lEff))
		lNFail  = r.RooFormulaVar(iLabel+"fqail"+iBin ,iLabel+"norm"+iBin+"*(1-veff)",r.RooArgList(lNTot,self._lEff))
		#shapes
		lPData  = r.RooDataHist(iLabel+"_pass_"+iBin,iLabel+"_pass_"+iBin, r.RooArgList(self._lMSD),iH[0])
		lMData  = r.RooDataHist(iLabel+"_fail_"+iBin,iLabel+"_fail_"+iBin, r.RooArgList(self._lMSD),iH[1]) 
		lP      = r.RooHistPdf (iLabel+"passh"+iBin,iLabel+"passh"+iBin, r.RooArgList(self._lShift),r.RooArgList(self._lMSD),lPData,0)
		lF      = r.RooHistPdf (iLabel+"failh"+iBin,iLabel+"failh"+iBin, r.RooArgList(self._lShift),r.RooArgList(self._lMSD),lMData,0)
		#extended likelihood from normalization and shape above
		lEP     = r.RooExtendPdf(iLabel+"_passe_" +iBin,iLabel+"pe" +iBin,lP,lNPass)
		lEF     = r.RooExtendPdf(iLabel+"_faile_" +iBin,iLabel+"fe" +iBin,lF,lNFail)
		
		lHist   = [lP,lF,lEP,lEF,lPData,lMData]
		self._allVars.extend([lNTot,lNPass,lNFail])
		self._allShapes.extend(lHist)
		return lHist	

	def getSignals(self,iHP,iHF,iBin):
		
		#getting signals - skip data+MC (first 5 elm in iHP and iHF)
		lPSigs  = []
		lFSigs  = []
		lPHists = [] 
		lFHists = [] 
		lVars=[50,75,100,125,150,200,250,300]
		for i0 in range(0,len(lVars)):
			lSig = self.rooTheHistFunc([iHP[i0+5],iHF[i0+5]],"zqq"+str(lVars[i0]),iBin)
			lPSigs.append(lSig[4])
			lFSigs.append(lSig[5])

		return (lPSigs,lFSigs)		

					

	def makeWorkspace(self,iOutput,iDatas,iFuncs,iVars,iCat="cat0",iShift=True):
		
		lW = r.RooWorkspace("w_"+str(iCat))

		# get the pT bin
		ipt = iCat[-1:];

		sigMassesForInterpolation = [];
		shapeForInterpolation_central = [];
		shapeForInterpolation_scaleUp = [];
		shapeForInterpolation_scaleDn = [];
		shapeForInterpolation_smearUp = [];
		shapeForInterpolation_smearDn = [];
		shapeForInterpolation_effUp   = [];
		shapeForInterpolation_effDn   = [];
		self._outfile_validation.cd();			

		for pFunc in iFuncs:
			
			ptbin = ipt;
			process = pFunc.GetName().split("_")[0];
			cat     = pFunc.GetName().split("_")[1];
			mass    = 0.;
			if iShift and ("wqq" in process or "zqq" in process):

				if process == "wqq": mass = 80.;
				elif process == "zqq": mass = 91.;
				elif process == "tqq": mass = 80.;
				else: mass = float(process[3:])
				#print process, mass;			

				# get the matched and unmatched hist
				tmph_matched = self._inputfile.Get(process+"_"+cat+"_matched");
				tmph_unmatched = self._inputfile.Get(process+"_"+cat+"_unmatched");
				procid = 0 if "wqq" in process else 1
				passid = 1 if "pass" in cat    else 2 
				# scale unmatched and matched hists only once
				if int(ipt) == 1 :
					scaleHists(tmph_matched,procid,passid)
					scaleHists(tmph_unmatched,procid,0)#passid)
				if process == "tqq":
					tmph_matched = self._inputfile.Get(process+"_"+cat+"_unmatched");
					tmph_unmatched = self._inputfile.Get(process+"_"+cat+"_matched");
				tmph_mass_matched = proj("cat",str(ipt),tmph_matched,self._mass_nbins,self._mass_lo,self._mass_hi);
				tmph_mass_unmatched = proj("cat",str(ipt),tmph_unmatched,self._mass_nbins,self._mass_lo,self._mass_hi);

				# again,get rid of very low or high mass bins according to pT cat
				for i0 in range(1,self._mass_nbins+1):
					print pFunc.GetName()
					if ((i0 > 31 or i0 < 0) and int(ipt) == 1) or ((i0 > 38 or i0 < 4) and int(ipt) == 2) or ((i0 > 46 or i0 < 5) and int(ipt) == 3) or ((i0 > 56 or i0 < 7) and int(ipt) == 4) or ( i0 < 7 and int(ipt) == 5):
						tmph_mass_matched.SetBinContent(i0,0);
						tmph_mass_unmatched.SetBinContent(i0,0);

				if pFunc.GetName() == "zqq300_pass_cat5": # bork the last 2 bins!
					tmph_mass_matched.SetBinContent(59,0.);
					tmph_mass_matched.SetBinContent(59,0.);
					tmph_mass_unmatched.SetBinContent(60,0.);
					tmph_mass_unmatched.SetBinContent(60,0.);
					
				# smear/shift the matched
				hist_container = hist( [mass],[tmph_mass_matched] );	
				# mass = 1.001+/-0.05, resolution = 1.1+0.4
				# mass_shift = m_data/m_mc = MASS_SF = 1.001
				# MASS_SF_ERR = sqrt((0.323/82.333)^2+(0.433/82.215)^2) = 0.0065
				# mass_shift_unc = math.sqrt((m_data_err / m_data) * (m_data_err / m_data) + (m_mc_err / m_mc)) * sigma shift = MASS_SF_ERR*sigma shift (MASS_SF_ERR = 0.03)
				# res_shift = s_data/s_mc = 1.114
				# res_shift_unc = math.sqrt((s_data_err / s_data) * (s_data_err / s_data) + (s_mc_err / s_mc)) * sigma shift = sqrt((0.453/8.831)^2+(0.340/7.93)^2) * sigma shift= 0.067* sigma shift
				mass_shift = 1.0;
				mass_shift_unc = 0.15; # 5 (23?) sigma shift!  Change the card accordingly
				res_shift = 1.1;
				res_shift_unc = 0.4; # 5 sigma shift! 
				# get new central value
				shift_val = mass - mass*mass_shift;
				tmp_shifted_h = hist_container.shift( tmph_mass_matched, shift_val);
				# get new central value and new smeared value
				smear_val = res_shift - 1.;
				tmp_smeared_h =  hist_container.smear( tmp_shifted_h[0] , smear_val)
				hmatched_new_central = tmp_smeared_h[0];
				if smear_val <= 0.: hmatched_new_central = tmp_smeared_h[1];
				# get shift up/down
				shift_unc = mass*mass_shift*mass_shift_unc;
				hmatchedsys_shift = hist_container.shift( hmatched_new_central, shift_unc);
				# get res up/down
				hmatchedsys_smear = hist_container.smear( hmatched_new_central, res_shift_unc);	
				hmatchedsys_eff   = hist_container.smear( hmatched_new_central, 0.);	
				# get efficiency
				if "pass" in cat:
					hmatchedsys_eff[0].Scale(1.1)
					hmatchedsys_eff[1].Scale(0.9)
				else:
					hmatchedsys_eff[0].Scale(0.98)
					hmatchedsys_eff[1].Scale(1.02)


				# add back the unmatched - well, never mind
				#hmatched_new_central.Add(tmph_mass_unmatched);
				#hmatchedsys_shift[0].Add(tmph_mass_unmatched);
				#hmatchedsys_shift[1].Add(tmph_mass_unmatched);
				#hmatchedsys_smear[0].Add(tmph_mass_unmatched);
				#hmatchedsys_smear[1].Add(tmph_mass_unmatched);
				#hmatchedsys_eff  [0].Add(tmph_mass_unmatched);
				#hmatchedsys_eff  [1].Add(tmph_mass_unmatched);
				hmatched_new_central.SetName(pFunc.GetName());
				if mass == 50 and int(ipt) > 2:
					hmatchedsys_shift[1] = hmatched_new_central.Clone("zqq50"+str(cat)+"_"+str(ipt)+"tmpScaleDn")
				if (mass == 50 and int(ipt) > 3) or (mass == 250 and int(ipt) < 2): # basically 50 GeV is 1 event
					pInt = hmatched_new_central.Integral()+0.01
					hmatched_new_central.Add(tmph_mass_unmatched); hmatched_new_central.Scale(pInt/hmatched_new_central.Integral());
					hmatchedsys_shift[0].Add(tmph_mass_unmatched); hmatchedsys_shift[0].Scale(pInt/hmatchedsys_shift[0].Integral());
					hmatchedsys_shift[1].Add(tmph_mass_unmatched); hmatchedsys_shift[1].Scale(pInt/hmatchedsys_shift[1].Integral());
					hmatchedsys_smear[0].Add(tmph_mass_unmatched); hmatchedsys_smear[0].Scale(pInt/hmatchedsys_smear[0].Integral());
					hmatchedsys_smear[1].Add(tmph_mass_unmatched); hmatchedsys_smear[1].Scale(pInt/hmatchedsys_smear[1].Integral());
					hmatchedsys_eff  [0].Add(tmph_mass_unmatched); hmatchedsys_eff  [0].Scale(pInt/hmatchedsys_eff  [0].Integral());
					hmatchedsys_eff  [1].Add(tmph_mass_unmatched); hmatchedsys_eff  [1].Scale(pInt/hmatchedsys_eff  [1].Integral());
				if process == "tqq":
					hmatchedsys_shift[0].SetName(pFunc.GetName()+"_tscaleUp");
					hmatchedsys_shift[1].SetName(pFunc.GetName()+"_tscaleDown");
				else:
					hmatchedsys_shift[0].SetName(pFunc.GetName()+"_scaleUp");
					hmatchedsys_shift[1].SetName(pFunc.GetName()+"_scaleDown");
				hmatchedsys_smear[0].SetName(pFunc.GetName()+"_smearUp");
				hmatchedsys_smear[1].SetName(pFunc.GetName()+"_smearDown");
				if "zqq" in process:
					hmatchedsys_eff  [0].SetName(pFunc.GetName()+"_effUp");
					hmatchedsys_eff  [1].SetName(pFunc.GetName()+"_effDown");
				if "wqq" in process:
					hmatchedsys_eff  [0].SetName(pFunc.GetName()+"_effUp");
					hmatchedsys_eff  [1].SetName(pFunc.GetName()+"_effDown");
				hout = [hmatched_new_central,hmatchedsys_shift[0],hmatchedsys_shift[1],hmatchedsys_smear[0],hmatchedsys_smear[1],hmatchedsys_eff[0],hmatchedsys_eff[1]];
	
				if mass > 0 and mass != 80. and mass != 91.:# and mass != 250. and mass != 300.: 
					sigMassesForInterpolation.append(mass);     
					shapeForInterpolation_central.append(hmatched_new_central) 
					shapeForInterpolation_scaleUp.append(hmatchedsys_shift[0]) 
					shapeForInterpolation_scaleDn.append(hmatchedsys_shift[1])  
					shapeForInterpolation_smearUp.append(hmatchedsys_smear[0])  
					shapeForInterpolation_smearDn.append(hmatchedsys_smear[1])  
					shapeForInterpolation_effUp  .append(hmatchedsys_eff[0])  
					shapeForInterpolation_effDn  .append(hmatchedsys_eff[1])  

				for h in hout:
					#print h.GetName()
					# again,get rid of very low or high mass bins according to pT cat
					for i0 in range(1,self._mass_nbins+1):
						if ((i0 > 31 or i0 < 0) and int(ipt) == 1) or ((i0 > 38 or i0 < 4) and int(ipt) == 2) or ((i0 > 46 or i0 < 5) and int(ipt) == 3) or ((i0 > 56 or i0 < 7) and int(ipt) == 4) or ( i0 < 7 and int(ipt) == 5):
							h.SetBinContent(i0,0);
						
					h.Write();
					tmprdh = RooDataHist(h.GetName(),h.GetName(),r.RooArgList(self._lMSD),h)
					getattr(lW,'import')(tmprdh, r.RooFit.RecycleConflictNodes())
					if h.GetName().find("scale") > -1:
						pName=h.GetName().replace("scale","scalept")
						tmprdh = RooDataHist(pName,pName,r.RooArgList(self._lMSD),h)
						getattr(lW,'import')(tmprdh, r.RooFit.RecycleConflictNodes())

			else: 
				getattr(lW,'import')(pFunc,r.RooFit.RecycleConflictNodes())
				
		# do the signal interpolation
		print "---------------------------------------------------------------"
		print len(sigMassesForInterpolation), sigMassesForInterpolation
		print iCat
		morphedHistContainer_central = hist(sigMassesForInterpolation,shapeForInterpolation_central);
		morphedHistContainer_scaleUp = hist(sigMassesForInterpolation,shapeForInterpolation_scaleUp);
		morphedHistContainer_scaleDn = hist(sigMassesForInterpolation,shapeForInterpolation_scaleDn);
		morphedHistContainer_smearUp = hist(sigMassesForInterpolation,shapeForInterpolation_smearUp);
		morphedHistContainer_smearDn = hist(sigMassesForInterpolation,shapeForInterpolation_smearDn);
		morphedHistContainer_effUp   = hist(sigMassesForInterpolation,shapeForInterpolation_effUp);
		morphedHistContainer_effDn   = hist(sigMassesForInterpolation,shapeForInterpolation_effDn);
		interpolatedMasses = [55.,60.0,65.,70.,
				      80.,85.,90.0,95.,
				      105.,110.0,115.,120.,
				      130.,135.0,140.,145.,
				      155.,160.,165.0,170.,
				      175.,180.0,185.,190.,195.,
				      205.,210.,215.,220.,225.,
				      230.,235.,240,245.,
				      255.,260.,265.,270.,275.,
				      280.,285.,290.,295.]

		for m in interpolatedMasses:
			mid=-1
			if m > 200 and  int(ipt) == 1:
				mid=len(sigMassesForInterpolation)-3
			if m > 250 and  int(ipt) == 2:
				mid=len(sigMassesForInterpolation)-2
			#if m < 75  and  int(ipt) >  4:
			#	mid=0
			if mid != -1:
				htmp_central = shapeForInterpolation_central[mid].Clone("tmp"+str(m)+"scaleup")
				htmp_scaleUp = shapeForInterpolation_scaleUp[mid].Clone("tmp"+str(m)+"scaleup")
				htmp_scaleDn = shapeForInterpolation_scaleDn[mid].Clone("tmp"+str(m)+"scaledn")
				htmp_smearUp = shapeForInterpolation_smearUp[mid].Clone("tmp"+str(m)+"smearup")
				htmp_smearDn = shapeForInterpolation_smearDn[mid].Clone("tmp"+str(m)+"smeardn")
				htmp_effUp   = shapeForInterpolation_effUp  [mid].Clone("tmp"+str(m)+"effup")
				htmp_effDn   = shapeForInterpolation_effDn  [mid].Clone("tmp"+str(m)+"effdn")
				if m > 200:
					htmp_central.Scale(0.001)
					htmp_scaleUp.Scale(0.001)
					htmp_scaleDn.Scale(0.001)
					htmp_smearUp.Scale(0.001)
					htmp_smearDn.Scale(0.001)
					htmp_effUp  .Scale(0.001)
					htmp_effDn  .Scale(0.001)
			else:
				htmp_central = morphedHistContainer_central.morph(m);
				htmp_scaleUp = morphedHistContainer_scaleUp.morph(m);
				htmp_scaleDn = morphedHistContainer_scaleDn.morph(m);
				htmp_smearUp = morphedHistContainer_smearUp.morph(m);
				htmp_smearDn = morphedHistContainer_smearDn.morph(m);
				htmp_effUp   = morphedHistContainer_effUp  .morph(m);
				htmp_effDn   = morphedHistContainer_effDn  .morph(m);
			htmp_central.SetName("zqq%i_%s" % (int(m),iCat));
			htmp_scaleUp.SetName("zqq%i_%s_scaleUp" % (int(m),iCat)); 
			htmp_scaleDn.SetName("zqq%i_%s_scaleDown" % (int(m),iCat));
			htmp_smearUp.SetName("zqq%i_%s_smearUp" % (int(m),iCat));
			htmp_smearDn.SetName("zqq%i_%s_smearDown" % (int(m),iCat));
			htmp_effUp  .SetName("zqq%i_%s_effUp"    % (int(m),iCat));
			htmp_effDn  .SetName("zqq%i_%s_effDown"  % (int(m),iCat));

			if iCat == "pass_cat5" and m < 125 and m > 100: self.signalChopper(htmp_central,m);

			hout = [htmp_central,htmp_scaleUp,htmp_scaleDn,htmp_smearUp,htmp_smearDn,htmp_effUp,htmp_effDn];
			for h in hout:
				print h.GetName()
				for i0 in range(1,self._mass_nbins+1):
					if (i0 > 31 and int(ipt) == 1) or ((i0 > 38 or i0 < 4) and int(ipt) == 2) or ((i0 > 46 or i0 < 5) and int(ipt) == 3) or ( (i0 < 7 or i0 > 56) and int(ipt) == 4) or ( i0 < 7 and int(ipt) == 5):
						h.SetBinContent(i0,0);
				h.Write();
				tmprdh = RooDataHist(h.GetName(),h.GetName(),r.RooArgList(self._lMSD),h)
				getattr(lW,'import')(tmprdh, r.RooFit.RecycleConflictNodes())
				if h.GetName().find("scale") > -1:
					pName=h.GetName().replace("scale","scalept")
					tmprdh = RooDataHist(pName,pName,r.RooArgList(self._lMSD),h)
					getattr(lW,'import')(tmprdh, r.RooFit.RecycleConflictNodes())

		for pData in iDatas:
			getattr(lW,'import')(pData,r.RooFit.RecycleConflictNodes())

		if iCat.find("pass_cat1") == -1:
			lW.writeToFile(iOutput,False)
		else:
			lW.writeToFile(iOutput)	
		#lW.writeToFile(iOutput)	

	def signalChopper(self,h,m):
		for i in range(1,h.GetNbinsX()+1):
			if h.GetBinCenter(i) > m + 1.5*math.sqrt(m): h.SetBinContent(i,0.);

##############################################################################
##############################################################################
#### E N D   O F   C L A S S
##############################################################################
##############################################################################

def main(options,args):
	
	idir = options.idir
	odir = options.odir

	#load input histograms: 2D histograms(mass,pT) of pass and fail region, for each MC and data
	#1:wqq,2:zqq,3:qcd,4:tqq,0:data+signals(50,75,100,125,150,200,250,300)
	f  = r.TFile(options.input);
	(hpass,hfail) = loadHistograms(f,options.pseudo,options.pseudo15);

	#build the workspacees
	dazsleRhalphabetBuilder(hpass,hfail,f);

##-------------------------------------------------------------------------------------
def loadHistograms(f,pseudo,pseudo15):

	#load histograms and scale W,Z,top+st
	hpass = [];
	hfail = [];
	lHP1 = f.Get("wqq_pass_matched")
	print 'wqq_pass ', lHP1.Integral() 
	lHF1 = f.Get("wqq_fail_matched")
	scaleHists(lHP1,0,1)
	scaleHists(lHF1,0,2)
	lHP2 = f.Get("zqq_pass_matched")
        print 'zqq_pass ', lHP2.Integral()
	lHF2 = f.Get("zqq_fail_matched")
	scaleHists(lHP2,1,1)
	scaleHists(lHF2,1,2)
	print 'zqq_fail ', lHF2.Integral()
	fHists.append(lHP1)
	fHists.append(lHF1)
	fHists.append(lHP2)
	fHists.append(lHF2)
	f.cd()
	lHP3 = f.Get("qcd_pass")
        print 'qcd_pass ', lHP3.Integral()
	lHF3 = f.Get("qcd_fail")
        print 'qcd_fail ', lHF3.Integral()
	lHP4 = f.Get("tqq_pass")
	lHP4.Scale(0.83)
        print 'tqq_pass ', lHP4.Integral()
	lHF4 = f.Get("tqq_fail")
        lHF4.Scale(1./(1-0.1*0.17))
	#top pT dependent SF
	scale=[1.0,0.8,0.75,0.7,0.6,0.5,0.5]
	for i0 in range(1,lHF4.GetNbinsX()+1):
		for i1 in range(1,lHF4.GetNbinsY()+1):
			lHP4.SetBinContent(i0,i1,lHP4.GetBinContent(i0,i1)*scale[i1])
			lHF4.SetBinContent(i0,i1,lHF4.GetBinContent(i0,i1)*scale[i1])
        print 'tqq_pass 2 ', lHP4.Integral()
	fHists.append(lHP3)
	fHists.append(lHF3)
	fHists.append(lHP4)
	fHists.append(lHF4)
	lHP3.SetDirectory(0)
	lHF3.SetDirectory(0)
	lHP4.SetDirectory(0)
	lHF4.SetDirectory(0)
	
	#getting st from tmp file
	# f2   = r.TFile("histInputs/hist_1DZqq-dataReRecoSpring165eff-3481-Gridv1340WP-sig-pt5006007008009001000_msd_st.root")
	lTHP4 = f.Get("stqq_pass")
	lTHF4 = f.Get("stqq_fail")
	lHP4.Add(lTHP4)
	lHF4.Add(lTHF4)

	print 'tqq_fail ', lHF4.Integral()
	print 'total mc pass ', lHP1.Integral()+lHP2.Integral()+lHP3.Integral()+lHP4.Integral()
        print 'total mc fail ', lHF1.Integral()+lHF2.Integral()+lHF3.Integral()+lHF4.Integral()
  
	if pseudo:
		lHP0 = lHP3.Clone("data_obs_pass")
		lHF0 = lHF3.Clone("data_obs_fail")
		lHF0.Add(lHF1)
		lHF0.Add(lHF2)
		lHF0.Add(lHF4)
		lHP0.Add(lHP1)
		lHP0.Add(lHP2)
		lHP0.Add(lHP4)
		print 'pass ', lHP0.Integral()
		print 'fail ', lHF0.Integral()

	elif pseudo15:
		lHF0 = lHF3.Clone("data_obs_fail")
		lHP0 = lHF3.Clone("data_obs_pass");
		lHP0.Scale(0.05);
		#lHP1.Scale(1.2)
		#lHP2.Scale(1.5)
		#lHP4.Scale(1.5)
		lHP0.Add(lHP1)
		lHP0.Add(lHP2)
		lHP0.Add(lHP4)
		lHF0.Add(lHF1)
                lHF0.Add(lHF2)
                lHF0.Add(lHF4)
	else:
		lHP0 = f.Get("data_obs_pass")
		lHF0 = f.Get("data_obs_fail")

	#lHP0.Smooth(10);
        #lHP1.Smooth(10);
        #lHP2.Smooth(10);
        #lHP3.Smooth(10);
        #lHP4.Smooth(10);
        #lHF0.Smooth(10);
        #lHF1.Smooth(10);
        #lHF2.Smooth(10);
        #lHF3.Smooth(10);
        #lHF4.Smooth(10);

	hpass.extend([lHP0,lHP1,lHP2])
	hfail.extend([lHF0,lHF1,lHF2])
	hpass.extend([lHP3,lHP4])
	hfail.extend([lHF3,lHF4])

	#signals
	# f1.cd()
	masses=[50,75,100,125,150,200,250,300]
	for mass in masses:
		hpass.append(f.Get("zqq"+str(mass)+"_pass_matched"))
		hfail.append(f.Get("zqq"+str(mass)+"_fail_matched"))
		scaleHists(hpass[len(hpass)-1],1,1)
		scaleHists(hfail[len(hfail)-1],1,2)
		hpass[len(hpass)-1].SetDirectory(0)
		hfail[len(hfail)-1].SetDirectory(0)
		fHists.append(hpass[len(hpass)-1])
		fHists.append(hfail[len(hfail)-1])

	for lH in (hpass+hfail):
		lH.SetDirectory(0)	
		print lH.GetName(), lH.Integral()
	# f1.Close()
	# print "lengths = ", len(hpass), len(hfail)
	# print hpass;
	# print hfail;
	return (hpass,hfail);
	# return (hfail,hpass);

##-------------------------------------------------------------------------------------
if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
	parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
	parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
	parser.add_option('--pseudo', action='store_true', dest='pseudo', default =False,help='data = MC', metavar='isData')
	parser.add_option('--pseudo15', action='store_true', dest='pseudo15', default =False,help='data = MC (fail) and fail*0.05 (pass)', metavar='isData')
	parser.add_option('--input', dest='input', default = 'histInputs/hist_1DZqq-dataReRecoSpring165eff-3481-Gridv130-final.root',help='directory with data', metavar='idir')

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
