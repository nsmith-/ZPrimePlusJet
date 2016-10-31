#! /usr/bin/env python
import ROOT as r,sys,math,array,os
from optparse import OptionParser
from ROOT import std,RooDataHist

import tdrstyle
tdrstyle.setTDRStyle()

parser = OptionParser()
parser.add_option('--input'  ,action='store',type='string',dest='input'    ,default='mlfit.root',help='input file')
parser.add_option('--data'   ,action='store',type='string',dest='data'     ,default='bern3.root',help='data file')
parser.add_option('--cats'    ,action='store',type='string',dest='cats'    ,default='0',help='categories 0,1,2,...')
parser.add_option('--passfail',action='store_true',         dest='passfail',default=False,help='fit pass and failng') 
parser.add_option('--divide'  ,action='store_true',         dest='divide'  ,default=False,help='ratio') 
parser.add_option('--mass'    ,action='store',              dest='mass'    ,default=100  ,help='mass') 

(options,args) = parser.parse_args()

def end():
    return
    if __name__ == '__main__':
        rep = ''
        while not rep in [ 'q', 'Q','a',' ' ]:
            rep = raw_input( 'enter "q" to quit: ' )
            if 1 < len(rep):
                rep = rep[0]

def divide(iData,iHists):
    lPass = -1
    lFail = -1
    for i0 in range(0,len(iHists)):
        if iHists[i0].GetName().find("pass") > -1 and lPass == -1:
            lPass = i0
        if iHists[i0].GetName().find("fail") > -1 and lFail == -1:
            lFail = i0
    if lPass != -1:
        iData[0].Divide(iHists[lPass])
        for i0 in range(0,len(iHists)):
            if i0 != lPass and iHists[i0].GetName().find("pass") > -1:
                iHists[i0].Divide(iHists[lPass])
        iHists[lPass].Divide(iHists[lPass])

    if lFail != -1:
        iData[1].Divide(iHists[lFail])
        for i0 in range(0,len(iHists)):
            if i0 != lFail and iHists[i0].GetName().find("fail") > -1:
                iHists[i0].Divide(iHists[lFail])
        iHists[lFail].Divide(iHists[lFail])

def draw(iData,iHists,iName="A",iPF=True,iDivide=False):
    if iDivide:
        divide(iData,iHists)

    lC0 = r.TCanvas("Can"+iName,"Can"+iName,800,600);
    if iPF:
        lC0.Divide(2)
    lC0.cd(1)
    iData[0].Draw("ep")
    pDraw=False
    for pHist in iHists:
        if pHist.GetName().find("pass") > -1:
            pHist.Draw("hist sames") if pDraw else pHist.Draw("e2 sames")
            pDraw=True
    iData[0].Draw("ep sames")
    lLegend = r.TLegend(0.63,0.63,0.88,0.88)
    lLegend.SetFillColor(0)
    lLegend.SetBorderSize(0)
    lLegend.AddEntry(iData [0],"data","lp")
    lLegend.AddEntry(iHists[0],"QCD","lf")
    lLegend.AddEntry(iHists[1],"W#rightarrow qq","l")
    lLegend.AddEntry(iHists[2],"Z#rightarrow qq","l")
    lLegend.AddEntry(iHists[3],"Signal","lf")
    lLegend.Draw()
    if not iPF:
        lC0.SaveAs(iName+".png")
        lC0.SaveAs(iName+".pdf")
        end()
        return

    lC0.cd(2)
    iData[1].Draw("ep")
    for pHist in iHists:
        pDraw=False
        if pHist.GetName().find("fail") > -1:
            pHist.Draw("hist sames") if pDraw else pHist.Draw("e2 sames")
            pDraw=True
    iData[1].Draw("ep sames")
    lC0.SaveAs(iName+".png")
    lC0.SaveAs(iName+".pdf")
    end()

def norm(iFile,iH,iName) :
    lNorms = iName.split("/")[0].replace("shapes","norm")
    lArg = iFile.Get(lNorms)
    lName = iName.replace(iName.split("/")[0]+"/","")
    print "!!!",lName,lNorms
    lVal = r.RooRealVar(lArg.find(lName)).getVal();
    iH.Scale(lVal/iH.Integral())

def load(iFile,iName):
    lHist = iFile.Get(iName)
    norm(iFile,lHist,iName)
    lHist.SetName(iName.replace("/","_"))
    lHist.SetTitle(iName.replace("/","_"))
    return lHist
    
def loadHist(iFile,iCat,iMass,iEWK=True,iS=True):
    lHists = []
    lFit = "shapes_fit_s/"+iCat+"/" if iS else "shapes_fit_b/"+iCat+"/"
    lHists.append(load(iFile,lFit+"qcd_pass"))
    if iEWK:
        lHists.append(load(iFile,lFit+"wqq_pass"))
        lHists.append(load(iFile,lFit+"zqq_pass"))
        lHists.append(load(iFile,lFit+"zqq"+iMass+"_pass"))
        lHists[1].SetLineColor(46)
        lHists[2].SetLineColor(9)
        lHists[3].SetLineColor(8)
        lHists[1].SetLineWidth(2)
        lHists[2].SetLineWidth(2)
        lHists[3].SetLineWidth(2)
        lHists[1].Add(lHists[0])
        lHists[2].Add(lHists[1])
        lHists[3].Add(lHists[2])
        lHists[2].SetFillColor(0)
    lHists[0].SetFillColor(16)
    lHists[0].SetFillStyle(3001)
    lHists[0].SetLineStyle(2)
    return lHists

def loadData(iDataFile,iCat):
    lW = iDataFile.Get("w_"+iCat)
    lData = lW.data("data_obs_"+iCat).createHistogram("x")
    lData.GetXaxis().SetTitle("m_{J} (GeV)")
    lData.SetMarkerStyle(20)
    return [lData]

if __name__ == "__main__":
    lHFile = r.TFile(options.input)
    lDFile = r.TFile(options.data)
    lDSum=[]
    lSum=[]
    for cat in options.cats.split(','):
        lData  = loadData(lDFile,"cat"+cat)
        lHists = loadHist(lHFile,"cat"+cat,options.mass)
        #lData  = loadData(lDFile,"pass_cat"+cat)
        #lHists = loadHist(lHFile,"pass_cat"+cat)
        if options.passfail:
            lData .extend(loadData(lDFile,"fail_cat"+cat))
            lHists.extend(loadHist(lHFile,"fail_cat"+cat,options.mass,False,False))
        if len(lSum) == 0:
            lDSum = lData
            lSum  = lHists
        else:
            for i0 in range(0,len(lDSum)-1):
                lDSum[i0].Add(lData[i0])
            for i0 in range(0,len(lSum)-1):
                lSum[i0].Add(lHists[i0])
        draw(lData,lHists,cat,options.passfail,options.divide)
    draw(lDSum,lSum,"sum",options.passfail)

