#include "TFile.h"
#include "TTree.h"
#include "TH2F.h"
#include "TGraph.h"
#include "TMath.h"
#include <iostream>
#include <iomanip>
#include <sstream>

const double fRhoRange=(7-1.5);
const double fPtRange =(1000-500);
const int fN     = 50;
const double fDPt   = 10;
const int    fNBins = 8;
double fPt  = 500;
double fRho = -3.;

struct dataObj {
  double rho;
  double pt;
  double n2;
  double weight;
  dataObj(double iRho,double iPt,double iN2,double iWeight) : rho(iRho),pt(iPt),n2(iN2),weight(iWeight) {}
};
bool nearest(const dataObj& iObj1, const dataObj& iObj2){
  double pDRho1 = fabs(iObj1.rho - fRho)/fRhoRange;
  double pDPt1  = fabs(iObj1.pt  - fPt) /fPtRange;
  double pDRho2 = fabs(iObj2.rho - fRho)/fRhoRange;
  double pDPt2  = fabs(iObj2.pt  - fPt) /fPtRange;
  return (pDRho1*pDRho1+pDPt1*pDPt1 < pDRho2*pDRho2+pDPt2*pDPt2);
}
bool n2sort(const dataObj& iObj1,const dataObj& iObj2) { return iObj1.n2 < iObj2.n2; }

void knnQuantile(double iRho=-4.) {
  iRho = -iRho;
  TFile *lFile =  TFile::Open("root://eoscms//eos/cms/store/user/pharris/prod/SQCD_HT.root");
  TTree *lTree = (TTree*) lFile->FindObjectAny("otree");
  double lPt   = 0; lTree->SetBranchAddress("AK8Puppijet0_pt"    ,&lPt);
  double lEta  = 0; lTree->SetBranchAddress("AK8Puppijet0_eta"   ,&lEta);
  double lMass = 0; lTree->SetBranchAddress("AK8Puppijet0_msd"   ,&lMass);
  float lW0   = 0; lTree->SetBranchAddress("puWeight"           ,&lW0);
  float lW1   = 0; lTree->SetBranchAddress("scale1fb"           ,&lW1);
  double lN2   = 0; lTree->SetBranchAddress("AK8Puppijet0_N2sdb1",&lN2);
  std::vector<dataObj> lObjs;
  for(int i0 = 0; i0 < lTree->GetEntriesFast(); i0++) { 
    lTree->GetEntry(i0);
    if(i0 % 100000 == 0) std::cout << "==> " << float(i0)/float(lTree->GetEntriesFast()) << std::endl;
    if(lPt  < 475) continue;
    if(lMass < 30) continue;
    double pRho = 2.*log(lMass/lPt);
    if(fabs(pRho-iRho) > fRhoRange/fNBins) continue;
    dataObj lObj(pRho,lPt,lN2,double(lW1*lW0));
    lObjs.push_back(lObj);
  }
  std::cout << "===> total " << lObjs.size() << std::endl;
  fRho = iRho;
  unsigned int lNLoop = 100000;
  if(lObjs.size() < lNLoop) lNLoop = lObjs.size();
  double *lX = new double[fN];
  double *lY = new double[fN];
  for(int i0 = 0; i0 < fN; i0++) {
    fPt = 500. + i0*fDPt;
    std::sort(lObjs.begin(),lObjs.end(),nearest);
    double pTotWeight = 0;
    std::vector<dataObj> pObjs;
    for(unsigned int i1 = 0; i1 < lNLoop; i1++) {
      double pDRho1 = fabs(lObjs[i1].rho - fRho)/fRhoRange;
      double pDPt1  = fabs(lObjs[i1].pt  - fPt) /fPtRange;      
      double pWeight = 1./(0.025+sqrt(pDRho1*pDRho1+pDPt1*pDPt1));
      dataObj pObj(lObjs[i1].rho,lObjs[i1].pt,lObjs[i1].n2,lObjs[i1].weight*pWeight);
      pObjs.push_back(pObj);
      pTotWeight += pObj.weight;
    }
    std::sort(pObjs.begin(),pObjs.end(),n2sort);
    double pN2 = -1,pWeight = 0;
    int pId = 0;
    for(unsigned int i1 = 0; i1 < lNLoop; i1++) {
      pWeight += pObjs[i1].weight;
      //std::cout << i1 << "==> " << fPt << " == " << fRho << " == " << pObjs[i1].n2 << " -- " << pWeight/pTotWeight << std::endl;
      if(pWeight/pTotWeight < 0.05) continue;
      pN2 = pObjs[i1].n2;
      pId = i1;
      break;
    }
    double pDelta = (pWeight-0.05*pTotWeight)/pObjs[pId].weight;
    lX[i0] = fPt;
    lY[i0] = (pObjs[pId].n2*pDelta + pObjs[TMath::Max(pId-1,0)].n2*(1.-pDelta));
  }
  std::stringstream pSS; pSS << "N2DDT_" << std::setw(3) << fabs(iRho);
  TFile *lOFile = new TFile((pSS.str()+".root").c_str(),"RECREATE");
  TGraph *lGraph = new TGraph(fN,lX,lY);
  lGraph->SetTitle(pSS.str().c_str());
  lGraph->SetName (pSS.str().c_str());
  lGraph->Write();
}
