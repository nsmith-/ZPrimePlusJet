#include "TFile.h"
#include "TTree.h"
#include "TH2F.h"
#include "TF1.h"
#include "TGraph.h"
#include "TMath.h"
#include <iostream>
#include <iomanip>
#include <sstream>

const double fRhoRange=(7-1.5);
const double fPtRange =(1000-500);
const int fN     = 102;
const double fDPt   = 10;
const int    fNBins = 16;
double fPt  = 180;
double fRho = -3.;

TF1* fCorrGEN = new TF1("corrGEN","[0]+[1]*pow(x*[2],-[3])",200,3500);
TF1* fCorrRECO_cen = new TF1("corrRECO_cen","[0]+[1]*x+[2]*pow(x,2)+[3]*pow(x,3)+[4]*pow(x,4)+[5]*pow(x,5)",200,3500);
TF1* fCorrRECO_for = new TF1("corrRECO_for","[0]+[1]*x+[2]*pow(x,2)+[3]*pow(x,3)+[4]*pow(x,4)+[5]*pow(x,5)",200,3500);

void setupCorr() { 
  fCorrGEN->SetParameter(0,1.00626);
  fCorrGEN->SetParameter(1, -1.06161);
  fCorrGEN->SetParameter(2,0.0799900);
  fCorrGEN->SetParameter(3,1.20454);
  fCorrRECO_cen->SetParameter(0,1.09302);
  fCorrRECO_cen->SetParameter(1,-0.000150068);
  fCorrRECO_cen->SetParameter(2,3.44866e-07);
  fCorrRECO_cen->SetParameter(3,-2.68100e-10);
  fCorrRECO_cen->SetParameter(4,8.67440e-14);
  fCorrRECO_cen->SetParameter(5,-1.00114e-17);
  fCorrRECO_for->SetParameter(0,1.27212);
  fCorrRECO_for->SetParameter(1,-0.000571640);
  fCorrRECO_for->SetParameter(2,8.37289e-07);
  fCorrRECO_for->SetParameter(3,-5.20433e-10);
  fCorrRECO_for->SetParameter(4,1.45375e-13);
  fCorrRECO_for->SetParameter(5,-1.50389e-17);
}
double correct(double iEta,double iPt, double iMass) { 
  double genCorr  = 1.;
  double recoCorr = 1.;
  genCorr =  fCorrGEN->Eval( iPt );
  if( fabs(iEta)  < 1.3 ) { recoCorr = fCorrRECO_cen->Eval( iPt );}
  else { recoCorr = fCorrRECO_for->Eval( iPt ); }
  //std::cout << "===> " << recoCorr << " -- " << genCorr << " -- " << iMass << " -- " << iPt << std::endl;
  return iMass*recoCorr*genCorr;
}
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
  setupCorr();
  iRho = -iRho;
  TFile *lFile =  TFile::Open("root://eoscms//eos/cms/store/user/pharris/prod/QCD_HT_v2.root");
  TTree *lTree = (TTree*) lFile->FindObjectAny("otree");
  double lPt   = 0; lTree->SetBranchAddress("AK8Puppijet0_pt"    ,&lPt);
  double lEta  = 0; lTree->SetBranchAddress("AK8Puppijet0_eta"   ,&lEta);
  double lMass = 0; lTree->SetBranchAddress("AK8Puppijet0_msd"   ,&lMass);
  float  lW0   = 0; lTree->SetBranchAddress("puWeight"           ,&lW0);
  float  lW1   = 0; lTree->SetBranchAddress("scale1fb"           ,&lW1);
  double lN2   = 0; lTree->SetBranchAddress("AK8Puppijet0_N2sdb1",&lN2);
  std::vector<dataObj> lObjs;
  for(int i0 = 0; i0 < lTree->GetEntriesFast(); i0++) { 
    lTree->GetEntry(i0);
    if(i0 % 100000 == 0) std::cout << "==> " << float(i0)/float(lTree->GetEntriesFast()) << std::endl;
    if(lPt  < 180) continue;
    lMass = correct(lEta,lPt,lMass);
    if(lMass < 30) continue;
    double pRho = 2.*log(lMass/lPt);
    if(fabs(pRho-iRho) > fRhoRange/fNBins) continue;
    dataObj lObj(pRho,lPt,lN2,double(lW1*lW0));
    lObjs.push_back(lObj);
  }
  std::cout << "===> total " << lObjs.size() << std::endl;
  fRho = iRho;
  unsigned int lNLoop = 10000;
  if(lObjs.size() < lNLoop) lNLoop = lObjs.size();
  double *lX = new double[fN];
  double *lY = new double[fN];
  for(int i0 = 0; i0 < fN; i0++) {
    fPt = 180. + i0*fDPt;
    std::sort(lObjs.begin(),lObjs.end(),nearest);
    double pTotWeight = 0;
    std::vector<dataObj> pObjs;
    for(unsigned int i1 = 0; i1 < lNLoop; i1++) {
      double pDRho1 = fabs(lObjs[i1].rho - fRho)/fRhoRange;
      double pDPt1  = fabs(lObjs[i1].pt  - fPt) /fPtRange;      
      double pWeight = 1./(0.001+sqrt(pDRho1*pDRho1+pDPt1*pDPt1));
      dataObj pObj(lObjs[i1].rho,lObjs[i1].pt,lObjs[i1].n2,lObjs[i1].weight*pWeight);
      pObjs.push_back(pObj);
      pTotWeight += pObj.weight;
    }
    std::sort(pObjs.begin(),pObjs.end(),n2sort);
    double pN2 = -1,pWeight = 0;
    int pId = 0;
    lNLoop = pObjs.size();
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
