#! /usr/bin/env python
import ROOT as r,sys,math,array,os
from optparse import OptionParser
from ROOT import std,RooDataHist
from array import array
sys.path.insert(0, '../.')

parser = OptionParser()
parser.add_option('--input'  ,action='store',type='string',dest='input'    ,default='mlfit.root',help='input file')
parser.add_option('--data'   ,action='store',type='string',dest='data'     ,default='base.root',help='data file')
parser.add_option('--cats'    ,action='store',type='string',dest='cats'    ,default='1,2,3,4',help='categories 0,1,2,...')
parser.add_option('--passfail',action='store_true',         dest='passfail',default=True,help='fit pass and failng') 
parser.add_option('--divide'  ,action='store_true',         dest='divide'  ,default=False,help='ratio') 
parser.add_option('--mass'    ,action='store',              dest='mass'    ,default=125  ,help='mass') 

(options,args) = parser.parse_args()

def end():
    if __name__ == '__main__':
        rep = ''
        while not rep in [ 'q', 'Q','a',' ' ]:
            rep = raw_input( 'enter "q" to quit: ' )
            if 1 < len(rep):
                rep = rep[0]

def divide(iData,iHists):
    lPass = -1
    iAllP = []
    iHistsP = []
    iSumHP = iHists[5].Clone()                                                                                                                             
    print iHists[0].GetName()
    print iHists[0].Integral()
    print iHists[1].GetName()
    print iHists[1].Integral()
    print iHists[2].GetName()
    print iHists[2].Integral()
    print iHists[3].GetName()
    print iHists[3].Integral()
    print iHists[4].GetName()
    print iHists[4].Integral()


    #for i0 in range(0,len(iHists)):
    #    if iHists[i0].GetName().find("pass") > -1 and lPass == -1:
    #        lPass = i0
    #ltmp = iHists[lPass].Clone()
    #iHistsP.append(ltmp)
    #if lPass != -1:
    ltot = iSumHP.Clone()
    ltmp = iData[0].Clone()
    #ltmp.Divide(iHists[lPass])
    ltmp.Divide(ltot)
    iAllP.append(ltmp);
    #for i0 in range(0,len(iHists)):
    #    ltmp = iHists[i0].Clone()
    ##    if i0 != lPass and iHists[i0].GetName().find("pass") > -1:
    #            #ltmp.Divide(iHists[lPass])
    #            ltmp.Divide(iSumHP)
    #            iHistsP.append(ltmp)
    #    iHistsP[lPass].Divide(iSumHP)
    #iHistsP[lPass].Divide(iHists[lPass])
    iAllP.extend(iHistsP)
    return iAllP[0]

def draw(iData,iHists,iName,iPF,iCats):

    iData[0].GetXaxis().SetTitle("m_{SD} (GeV)")
    lC0 = r.TCanvas("c","c",900,800);
    p12 = r.TPad("p12","p12",0.0,0.3,1.0,1.0);
    p22 = r.TPad("p22","p22",0.0,0.0,1.0,0.3);
    p12.SetBottomMargin(0.02);
    p22.SetTopMargin(0.05);
    p22.SetBottomMargin(0.3);
    #iHists[4].Scale(10)
    iSumHP = iHists[0].Clone()
    iSumHP.Add(iHists[1])
    iSumHP.Add(iHists[2])
    iSumHP.Add(iHists[3])
    ksScoreP = iData[0].KolmogorovTest( iHists[5] )
    chiScoreP = iData[0].Chi2Test( iHists[5] , "UW P")
    print 'pscore ',chiScoreP
    print 'ksscore ',ksScoreP

    lC0.cd()
    p12.Draw(); p12.cd();
    iData[0].GetYaxis().SetTitle("Events / 5 GeV")
    iData[0].GetXaxis().SetTitleOffset(2)
    iData[0].GetYaxis().SetTitleOffset(1.3)
    iData[0].GetYaxis().SetTitleSize(0.04)
    iData[0].GetYaxis().SetLabelSize(0.035)
    iData[0].GetXaxis().SetLabelOffset(0.05)

    #iData[0].GetYaxis().SetTitl
    if iCats ==1: 
        iData[0].GetYaxis().SetRangeUser(0.,iData[0].GetMaximum()*0.95) #22000
        iData[0].GetXaxis().SetRangeUser(40.,185.)
        tagpt = 'p_{T}: 500-600 GeV'
    elif iCats ==2: 
        iData[0].GetYaxis().SetRangeUser(0.,iData[0].GetMaximum()*1.005) #6000.)
        iData[0].GetXaxis().SetRangeUser(45.,220.)
        tagpt = 'p_{T}: 600-700 GeV'
    elif iCats ==3: 
        iData[0].GetYaxis().SetRangeUser(0.,iData[0].GetMaximum()*1.03) #2200.)
        iData[0].GetXaxis().SetRangeUser(50.,255.)
        tagpt = 'p_{T}: 700-800 GeV'
    elif iCats ==4: 
        iData[0].GetYaxis().SetRangeUser(0.,iData[0].GetMaximum()*1.05) #800.)
        iData[0].GetXaxis().SetRangeUser(60.,310.) 
        tagpt = 'p_{T}: 800-900 GeV'
    elif iCats ==5: 
        iData[0].GetYaxis().SetRangeUser(0.,iData[0].GetMaximum()*1.055) #400.)
        iData[0].GetXaxis().SetRangeUser(60.,330.)
        tagpt = 'p_{T}: 900-1000 GeV'
    else:
        iData[0].GetYaxis().SetRangeUser(0.,iData[0].GetMaximum()*1.1) #35000.)
        iData[0].GetXaxis().SetRangeUser(40.,330.)
        tagpt = 'All p_{T} categories'

    iData[0].Draw("ex0")
    pDraw=False
    print iHists[4].Integral()
    #iHists[4].Scale(7870*0.25*1.218*0.5)

    print iHists[4].Integral()

    for pHist in iHists:
        if iCats ==1:
            pHist.GetXaxis().SetRangeUser(40.,185.)
        elif iCats ==2:
            pHist.GetXaxis().SetRangeUser(45.,220.)
        elif iCats ==3:
            pHist.GetXaxis().SetRangeUser(50.,255.)
        elif iCats ==4:
            pHist.GetXaxis().SetRangeUser(60.,310.)
        elif iCats ==5:
            pHist.GetXaxis().SetRangeUser(60.,330.)
        else:
            pHist.GetXaxis().SetRangeUser(40.,330.)
        pHist.SetLineWidth(2)
        if pHist.GetName().find("pass") > -1:
            #if pHist.GetName().find("tqq") > -1: continue
            pHist.Draw("hist sames") if pDraw else pHist.Draw("e2 sames")
            pDraw=True
    iData[0].Draw("pex0 sames")
    #lLegend = r.TLegend(0.55, 0.5, 0.75, 0.88)
    lLegend = r.TLegend(0.33,0.73,0.88,0.88)
    lLegend.SetFillColor(0)
    lLegend.SetBorderSize(0)
    lLegend.SetTextFont(42)
    lLegend.SetTextSize(0.037)
    lLegend.SetNColumns(2)
    lLegend.AddEntry(iData [0],"Data","px0e")
    lLegend.AddEntry(iHists[1],"W(qq)+jets","l")

    lLegend.AddEntry(iHists[5],"Total SM pred.","l")
    lLegend.AddEntry(iHists[2],"Z(qq)+jets","l")

    lLegend.AddEntry(iHists[0],"Multijet pred.","lf")
    lLegend.AddEntry(iHists[3],"t#bar{t}/single-t (qq)+jets","l")

    lLegend.AddEntry(iHists[4],"Z'(qq), g_{q'}=1/6, m_{Z'}=125 GeV","lf")

    lLegend.Draw()
    
    tag1 = r.TLatex(0.69,0.92,"35.9 fb^{-1} (13 TeV)")
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag2 = r.TLatex(0.2,0.8,"CMS")
    tag2.SetNDC()
    tag2.SetTextFont(62)
    tag3 = r.TLatex(0.24,0.92,"Preliminary")
    tag3.SetNDC()
    tag3.SetTextFont(52)
    tag2.SetTextSize(0.07)
    tag3.SetTextSize(0.045)
    tag1.Draw()
    tag2.Draw()
    #tag3.Draw()
    tag4 = r.TLatex(0.67,0.42,"p_{value} = %.2f"%chiScoreP)
    tag4.SetNDC()
    tag4.SetTextSize(0.030)
    #tag4.Draw()
    #tag5 = r.TLatex(0.57,0.42,"ks = %.2f"%ksScoreP)
    #tag5.SetNDC()
    #tag5.SetTextSize(0.030)
    #tag5.Draw()
    tag6 = r.TLatex(0.705,0.422,tagpt)
    #tag6 = r.TLatex(0.695,0.422,tagpt)
    tag6.SetNDC()
    tag6.SetTextFont(42)
    tag6.SetTextSize(0.037)
    tag6.Draw()
    iData[0].SetMaximum(iData[0].GetMaximum()*1.2)

    #lC0.cd(1).RedrawAxis()
    lC0.cd()
    p22.Draw(); p22.cd();
    p22.SetGrid();
    iRatios1 = divide(iData,iHists)
    iRatios1.GetYaxis().SetRangeUser(0.5,1.5)
    iRatios1.GetYaxis().SetNdivisions(5)
    iRatios1.GetYaxis().SetTitle("Data/Prediction")
    iRatios1.GetYaxis().SetTitleSize(0.09)
    iRatios1.GetXaxis().SetTitleSize(0.12)
    iRatios1.GetXaxis().SetTitleOffset(1)
    iRatios1.GetYaxis().SetTitleOffset(0.45)
    iRatios1.GetXaxis().SetLabelOffset(0.007)

    if iCats ==1:
        iRatios1.GetYaxis().SetRangeUser(0.85,1.15)
        iRatios1.GetXaxis().SetRangeUser(40,185.)
    elif iCats ==2:
        iRatios1.GetYaxis().SetRangeUser(0.85,1.15)
        iRatios1.GetXaxis().SetRangeUser(45,220.)
    elif iCats ==3:
        iRatios1.GetXaxis().SetRangeUser(50,255.)
        iRatios1.GetYaxis().SetRangeUser(0.8,1.2)
    elif iCats ==4:
        iRatios1.GetXaxis().SetRangeUser(60,310.)
        iRatios1.GetYaxis().SetRangeUser(0.8,1.2)
    elif iCats ==5:
        iRatios1.GetXaxis().SetRangeUser(60,330.)
        iRatios1.GetYaxis().SetRangeUser(0.65,1.35)
    else:
        iRatios1.GetYaxis().SetRangeUser(0.9,1.1)
        iRatios1.GetXaxis().SetRangeUser(40,330.)


    iRatios1.GetYaxis().SetLabelSize(0.09)
    iRatios1.GetXaxis().SetLabelSize(0.1)
    #iRatios1.GetXaxis().SetTitleSize(0.05)
    iRatios1.GetXaxis().SetTitle("m_{SD} (GeV)")
    iRatios1.Draw("px0e")
    iOneWithErrors = iHists[5].Clone();
    iOneWithErrors.Divide(iHists[5].Clone());
    for i in range(iOneWithErrors.GetNbinsX()): 
        #print iHists[3].GetBinContent(i+1)
        if iHists[3].GetBinContent(i+1) > 0: 
            print iHists[5].GetBinError(i+1)/iHists[5].GetBinContent(i+1)
            iOneWithErrors.SetBinError( i+1, iHists[5].GetBinError(i+1)/iHists[5].GetBinContent(i+1) );
        else: iOneWithErrors.SetBinError( i+1, 0.014);
    iOneWithErrors.SetFillStyle(3001);
    iOneWithErrors.SetFillColor(r.kAzure);
    iOneWithErrors.SetMarkerSize(0);
    iOneWithErrors.SetLineWidth(0);
    iOneWithErrors.Draw(" sames");
    iRatios1.Draw("px0e sames")
    #lC0.cd(1);
    #p12.cd().RedrawAxis()
    lC0.Modified()
    lC0.Update()

    lC0.SaveAs(iName+".png")
    lC0.SaveAs(iName+".pdf")
    lC0.SaveAs(iName+".root")
    end()

def norm(iFile,iH,iName) :
    lNorms = iName.split("/")[0].replace("shapes","norm")
    lArg = iFile.Get(lNorms)
    lName = iName.replace(iName.split("/")[0]+"/","")
    #print "!!!",lName,lNorms
    lVal = r.RooRealVar(lArg.find(lName)).getVal();
    iH.Scale(lVal/iH.Integral())
    
def load(iFile,iName,iNorm=True):
    lHist = iFile.Get(iName)
    if iNorm:
        norm(iFile,lHist,iName)
    lHist.SetName(iName.replace("/","_"))
    lHist.SetTitle(iName.replace("/","_"))
    return lHist
    
def loadHist(iFile,iCat,iMass,iEWK=True,iS=True):
    lHists = []
    lFit = "shapes_fit_s/"+iCat+"/" if iS else "shapes_fit_b/"+iCat+"/"
    #lFit = "shapes_prefit/"+iCat+"/"
    lHists.append(load(iFile,lFit+"qcd"))
    lHists[0].SetFillColor(r.kGray+3)
    lHists[0].SetFillStyle(3001)
    lHists[0].SetLineStyle(2)
    lHists[0].SetLineWidth(0)
    if iEWK:
        lId = len(lHists)
        lHists.append(load(iFile,lFit+"wqq"))
        lHists.append(load(iFile,lFit+"zqq"))
        lHists.append(load(iFile,lFit+"tqq"))
        lHists.append(load(iFile,lFit+"zqq"+str(iMass)))
        #lHists[lId].SetLineColor(46)
        lHists[lId].SetLineColor(r.kGreen+3)
        #lHists[lId+1].SetLineColor(r.kGreen+3)
        lHists[lId+1].SetLineColor(r.kRed+1)
        lHists[lId+2].SetLineColor(r.kMagenta+3)
        #lHists[lId+3].SetLineColor(r.kMagenta-4)
        lHists[lId+3].SetLineColor(r.kPink + 7)
        lHists[lId+3].SetFillColor(r.kPink + 7)
        lHists[lId].SetLineStyle(3)
        lHists[lId+1].SetLineStyle(4)
        lHists[lId+2].SetLineStyle(5)
        lHists[lId+3].SetLineStyle(2)
        for i0 in range(lId,lId+3):
            lHists[i0].SetLineWidth(2)
            #lHists[i0].Add(lHists[i0-1])
        lHists.append(load(iFile,lFit+"qcd"))
        lHists[5].Add(lHists[1])
        lHists[5].Add(lHists[2])
        lHists[5].Add(lHists[3])
        lHists[5].SetLineWidth(3)
        #lHists[5].SetLineColor(4)
        lHists[5].SetLineColor(r.kAzure - 5)
    return lHists

def loadData(iDataFile,iCat):
    #lW = iDataFile.Get("w_"+iCat)
    #lData = lW.data("data_obs_"+iCat).createHistogram("x")
    #lData = load(iDataFile,"shapes_prefit/"+str(iCat)+"/data",False)
    lData = load(iDataFile,"shapes_fit_s/"+str(iCat)+"/data",False)
    lData.GetXaxis().SetTitle("m_{J} (GeV)")
    lData.SetMarkerStyle(20)
    return [lData]

def hist(iData):
    lX = []
    for i0 in range(iData.GetN()):
        lX.append(-iData.GetErrorXlow(i0)+iData.GetX()[i0])
    lX.append(iData.GetX()[iData.GetN()-1]+iData.GetErrorXhigh(iData.GetN()-1))
    lHist = r.TH1F("dataSum","dataSum",iData.GetN(),array('d',lX))
    lHist.Sumw2()
    return lHist

def add(iSum,iData):
    for i0 in range(iData.GetN()):
        iSum.Fill(iData.GetX()[i0],iData.GetY()[i0]*(iData.GetErrorXlow(i0)+iData.GetErrorXhigh(i0)))
        #iSum.SetBinContent(i0,iSum.GetBinContent(i0)+iData.GetY()[i0])
    for i0 in range(1,iSum.GetNbinsX()+1):
        iSum.SetBinError(i0,math.sqrt(iSum.GetBinContent(i0)))
    return iSum

if __name__ == "__main__":
    import tdrstyle
    tdrstyle.setTDRStyle()
    r.gStyle.SetPadTopMargin(0.10)
    r.gStyle.SetPadLeftMargin(0.16)
    r.gStyle.SetPadRightMargin(0.10)
    r.gStyle.SetPalette(1)
    r.gStyle.SetPaintTextFormat("1.1f")
    r.gStyle.SetOptFit(0000)
    r.gROOT.SetBatch()

    lHFile = r.TFile(options.input)
    lDFile = r.TFile(options.input)
    lDSum=[]
    lSum=[]
    iC=0
    for cat in options.cats.split(','):
        iC=iC+1
        lData  = loadData(lDFile,"ch"+str(cat)+"_pass_cat"+cat)
        lHists = loadHist(lHFile,"ch"+str(cat)+"_pass_cat"+cat,options.mass)
        if options.passfail:
            lData .extend(loadData(lDFile,"ch"+str(cat)+"_fail_cat"+cat))
            lHists.extend(loadHist(lHFile,"ch"+str(cat)+"_fail_cat"+cat,options.mass,True,True))
        if len(lSum) == 0:
            lDSum = [hist(lData[0]),hist(lData[1])]
            for i0 in range(0,len(lDSum)):
                add(lDSum[i0],lData[i0])
            lSum  = lHists
        else:
            for i0 in range(0,len(lDSum)):
                add(lDSum[i0],lData[i0])
                print i0,lDSum[i0].Integral()
            for i0 in range(0,len(lSum)):
                lSum[i0].Add(lHists[i0])
                print i0,lHists[i0].Integral()
    if iC == 1: cat = int(options.cats)
    else: cat = 6
    name = 'postfit_s_'+str(options.mass)+'_cat'+str(cat)#+'_10'
    #if options.divide: name = 'prefit_s_'+str(options.mass)+'_ratio'
    print 'CAT', iC 
    draw(lDSum,lSum,name,options.passfail,cat)
    
