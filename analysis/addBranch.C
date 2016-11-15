#include "TMath.h"
#include "TTree.h"
#include "TFile.h"
#include "TBranch.h"

void addBranch() {
  //TFile *f = TFile::Open("TTbar_madgraphMLM_1000pb_weighted.root","update");
  //TFile *f = TFile::Open("QCD_1000pb_weighted.root","update");
  TFile *f = TFile::Open("GluGluHToBB_M125_13TeV_powheg_pythia8_1000pb_weighted.root","update"); 
  TTree *T = (TTree*)f->Get("otree");
  double AK8Puppijet0_tau21,AK8Puppijet0_msd,AK8Puppijet0_pt;
  double AK8Puppijet0_tau21DDT = 999;
  TBranch *bpt = T->Branch("AK8Puppijet0_tau21DDT",&AK8Puppijet0_tau21DDT,"AK8Puppijet0_tau21DDT/D");
  T->SetBranchAddress("AK8Puppijet0_tau21",&AK8Puppijet0_tau21);
  T->SetBranchAddress("AK8Puppijet0_msd",&AK8Puppijet0_msd);
  T->SetBranchAddress("AK8Puppijet0_pt",&AK8Puppijet0_pt);
  Long64_t nentries = T->GetEntries();
  for (Long64_t i=0;i<nentries;i++) {
     T->GetEntry(i);
     if (AK8Puppijet0_pt > 0. && AK8Puppijet0_msd > 0.)
       AK8Puppijet0_tau21DDT = AK8Puppijet0_tau21 + 0.063*TMath::Log(AK8Puppijet0_msd*AK8Puppijet0_msd/AK8Puppijet0_pt);
     bpt->Fill();
  }
  T->Print();
  T->Write();
  delete f;
}
