#include <iostream>
#include <time.h>

using namespace std;

#include "tdrstyle.C"
#include "CMS_lumi.C"

void plotEffW() {
    int iPeriod = 4;    // 1=7TeV, 2=8TeV, 3=7+8TeV, 7=7+8+13TeV
    int iPos =11;
    
    setTDRStyle();
    //gStyle->SetOptFit(1111);

    
    writeExtraText = true;       // if extra text
    extraText  = "Simulation Preliminary";  // default extra text is "Preliminary"
    
    
    const int nPoints = 5;
    double mass[nPoints] = { 300,500, 1000,1500,2000};
    double effcies0p35[nPoints] = {0.866,0.894,0.942};
   

    double effciesErr0p35[nPoints] = {0.056,0.06,0.058};
    double effcies0p35L[nPoints] = {0.866,0.879,0.904};
   
  
    double effciesErr0p35L[nPoints] = {0.049,0.05,0.044};
    double effcies0p55[nPoints] = {0.872,0.881,0.926};

    double effciesErr0p55[nPoints] = {0.044,0.047,0.042};

    double effciesN2[nPoints]  = {0.92236805,0.9363717,0.954628180365058,0.9378410,0.91516545};
    double effciesN2err[nPoints] = {0.04807797,0.0322001380475668,0.0349917797918506,0.0336957,0.03147089};
   

 
    int stInd = 1;
    
    //for (int i=0; i!=nPoints; ++i) {
           
    //        effciesErrG[j][i] = sqrt(50000*effciesG[j][i]*(1-effciesG[j][i]))/50000;
	    
    //}
    
   
    TGraphErrors* tFw = new TGraphErrors(nPoints, mass, effciesN2,0,effciesN2err);
    tFw->SetMarkerColor(kAzure);
    tFw->SetMarkerStyle(21);
    tFw->SetLineColor(kAzure);


  /*  TGraphErrors* tEw = new TGraphErrors(nPoints, mass, effciesEw,0,effciesErrEw);
    tEw->SetMarkerColor(kPink+2);
    tEw->SetMarkerStyle(21);
    tEw->SetLineColor(kPink+2);

    TGraphErrors* tG= new TGraphErrors(nPoints, mass, effciesG,0,effciesErrG);
    tG->SetMarkerColor(kGreen+2);
    //tG->SetMarkerStyle(21);
    tG->SetLineColor(kGreen+2);  
  
*/
  

    
    
    gStyle->SetOptStat(0);
    gStyle->SetFitFormat("0");//2.2g");
    gStyle->SetOptFit(0);
    

     TCanvas * c2= new TCanvas("c2","c2",800,800);
     c2->cd();
    TH1F *hr2 = c2->DrawFrame(0,0.6,2500.,1.2);
    hr2->GetXaxis()->SetLabelSize(0.035);
    hr2->GetYaxis()->SetLabelSize(0.035);
    hr2->GetXaxis()->SetTitleSize(0.045);
    hr2->GetYaxis()->SetTitleSize(0.045);
    hr2->SetXTitle("Jet p_{T} (GeV)");
    hr2->SetYTitle("Eff_{Herwig}/Eff_{Pythia}");
    c2->SetFillColor(kWhite);
	

     tFw->Draw("pe");
     TF1 * asd = new TF1("asd","[0] ", 200, 2500);
     tFw->Fit("asd","","",200,2300);
     tFw->GetFunction("asd")->SetLineColor(kBlue+2);	
     tFw->GetFunction("asd")->Draw("same");


     TLegend* leg2 = new TLegend(0.33,0.4,0.9,0.15,"Substructure selection","NDC");
     leg2->SetTextFont(42);
     leg2->SetTextSize(0.03);
     leg2->AddEntry(tFw,"N_{2}^{DDT}(5%) <0","pl");
     leg2->Draw("same");








     CMS_lumi(c2,iPeriod, iPos );


     c2->SaveAs("SF2.pdf");
     c2->SaveAs("SF2_run_2016.root");



}

