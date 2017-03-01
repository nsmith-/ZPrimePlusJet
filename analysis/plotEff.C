#include <iostream>
#include <time.h>

using namespace std;

#include "tdrstyle.C"
#include "CMS_lumi.C"

void plotEff() {
    int iPeriod = 4;    // 1=7TeV, 2=8TeV, 3=7+8TeV, 7=7+8+13TeV
    int iPos =11;
    
    setTDRStyle();
    //gStyle->SetOptFit(1111);

    
    writeExtraText = true;       // if extra text
    extraText  = "Simulation Preliminary";  // default extra text is "Preliminary"
    
    
    const int nPoints = 3;
    double mass[nPoints] = { 500, 1000,1500};
    double effcies0p35[nPoints] = {0.866,0.894,0.942};
   

    double effciesErr0p35[nPoints] = {0.056,0.06,0.058};
    double effcies0p35L[nPoints] = {0.866,0.879,0.904};
   
  
    double effciesErr0p35L[nPoints] = {0.049,0.05,0.044};
    double effcies0p55[nPoints] = {0.872,0.881,0.926};

    double effciesErr0p55[nPoints] = {0.044,0.047,0.042};

    double effciesN2[nPoints]  = {0.9870191,0.9927595,0.993109006675056};
    double effciesN2err[nPoints] = { 0.0580185,0.0538194,0.0548572736077112};
   

 
    int stInd = 1;
    
    //for (int i=0; i!=nPoints; ++i) {
            
    //        effciesErrG[j][i] = sqrt(50000*effciesG[j][i]*(1-effciesG[j][i]))/50000;
	    
    //}
    
    TGraphErrors* tBD = new TGraphErrors(nPoints, mass, effcies0p35,0,effciesErr0p35);
    tBD->SetMarkerColor(kRed+2);
    tBD->SetLineColor(1);
    tBD->SetLineColor(kRed+2);

    TGraphErrors* tBDw = new TGraphErrors(nPoints, mass, effcies0p35L,0,effciesErr0p35L);
    tBDw->SetMarkerColor(2);
    tBDw->SetMarkerStyle(21);
    tBDw->SetLineColor(2);


    TGraphErrors* tF = new TGraphErrors(nPoints, mass, effcies0p55,0,effciesErr0p55);
    tF->SetMarkerColor(kBlue+2);
    //tF->SetMarkerStyle(21);
    tF->SetLineColor(kBlue+2); 
   
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
    
    TCanvas* c1 = new TCanvas("c1","c1",800,800);
    
    //TH1F *hr = p1->DrawFrame(0,0.0001,3500,1.0);
    TH1F *hr = c1->DrawFrame(0,0.6,2500.,1.2);
    hr->GetXaxis()->SetLabelSize(0.035);
    hr->GetYaxis()->SetLabelSize(0.035); 
    hr->GetXaxis()->SetTitleSize(0.045);
    hr->GetYaxis()->SetTitleSize(0.045);
    hr->SetXTitle("Jet p_{T} (GeV)");
    hr->SetYTitle("R_{Herwig}/R_{Pythia}");
    c1->SetFillColor(kWhite);
    TF1 * asd = new TF1("asd"," [0]*TMath::Log(x+[1]) ", 450, 1550);
    tBD->Fit("asd","","",300,2000);
    tBD->GetFunction("asd")->SetLineColor(kRed+2);
    tBDw->Fit("asd","","",300,2000);
    tBDw->GetFunction("asd")->SetLineColor(kRed-7);
    tBD->SetLineColor(kRed+2);
    tBDw->SetLineColor(kRed-7);
    tBD->SetLineWidth(2);
    tBDw->SetLineWidth(2);

    
    tBD->GetFunction("asd")->SetLineWidth(2);
    tBDw->GetFunction("asd")->SetLineWidth(2);

    tBD->Draw("pe");

    tBDw->Draw("pe same");
     tF->Draw("pe same");

    tBD->GetFunction("asd")->Draw("same");
    tBDw->GetFunction("asd")->Draw("same");
 
    tF->Fit("asd","","",300,2000);
    tF->GetFunction("asd")->SetLineColor(kBlue+2);

    /*tFw->Fit("pol4","","",300,2000);
    tFw->GetFunction("pol4")->SetLineColor(kAzure);


    tEw->Fit("pol5","","",0,1);
    tEw->GetFunction("pol5")->SetLineColor(kPink+2);
	
    tG->Fit("pol4","","",0,1);
    tG->GetFunction("pol4")->SetLineColor(kGreen);
    tF->SetLineColor(kBlue+2);
    tG->SetLineColor(kGreen);
    tF->SetLineWidth(2);
    */
    tFw->SetLineColor(kAzure);
    tFw->SetLineWidth(2);
    tF->GetFunction("asd")->SetLineWidth(2);

  
    //tEw->GetFunction("pol5")->SetLineWidth(2);
    
     tF->Draw("pe same");

    tF->GetFunction("asd")->Draw("same");


    
    TLegend* leg = new TLegend(0.33,0.4,0.9,0.15,"Substructure selection","NDC");
    leg->SetTextFont(42);
    leg->SetTextSize(0.03);
    leg->AddEntry(tBD,"#tau_{21}<0.35","pl");
    leg->AddEntry(tBDw,"0.35<#tau_{21}<0.75","pl");
    


    leg->AddEntry(tF,"#tau_{21}<0.55","pl");
    

    
    leg->Draw("same");
    
    CMS_lumi(c1,iPeriod, iPos );
    

     c1->SaveAs("SF.pdf"); 
     c1->SaveAs("SF_run_2016.root");

     TCanvas * c2= new TCanvas("c2","c2",800,800);
     c2->cd();
    TH1F *hr2 = c2->DrawFrame(0,0.6,2500.,1.2);
    hr2->GetXaxis()->SetLabelSize(0.035);
    hr2->GetYaxis()->SetLabelSize(0.035);
    hr2->GetXaxis()->SetTitleSize(0.045);
    hr2->GetYaxis()->SetTitleSize(0.045);
    hr2->SetXTitle("Jet p_{T} (GeV)");
    hr2->SetYTitle("R_{Herwig}/R_{Pythia}");
    c2->SetFillColor(kWhite);
	

     tFw->Draw("pe");
     tFw->Fit("asd","","",300,2000);
     tFw->GetFunction("asd")->SetLineColor(kBlue+2);	
     tFw->GetFunction("asd")->Draw("same");


     TLegend* leg2 = new TLegend(0.33,0.4,0.9,0.15,"Substructure selection","NDC");
     leg2->SetTextFont(42);
     leg2->SetTextSize(0.03);
     leg2->AddEntry(tFw,"N_{2}^{DDT}(26%) <0","pl");
     leg2->Draw("same");








     CMS_lumi(c2,iPeriod, iPos );


     c2->SaveAs("SF2.pdf");
     c2->SaveAs("SF2_run_2016.root");



}

