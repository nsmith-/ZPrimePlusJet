#!/usr/bin/env python
import ROOT as r,sys,math,array,os
from hist import hist
from optparse import OptionParser
from ROOT import std,RooDataHist

def end():
    if __name__ == '__main__':
        rep = ''
        while not rep in [ 'q', 'Q','a',' ' ]:
            rep = raw_input( 'enter "q" to quit: ' )
            if 1 < len(rep):
                rep = rep[0]


def drawFrame(iFrame,iData,iFuncs):
    iData.plotOn(iFrame)
    iColor=50
    for pFunc in iFuncs:
        #pFunc.plotOn(iFrame,r.RooFit.LineColor(iColor),r.RooFit.LineStyle(iColor != 50+1),r.RooFit.Components(pFunc.GetName()),r.RooFit.ProjWData(iData))
        #pFunc.plotOn(iFrame,r.RooFit.LineColor(iColor),r.RooFit.LineStyle(iColor != 50+1),r.RooFit.ProjWData(iData))
        pFunc.plotOn(iFrame,r.RooFit.LineColor(iColor),r.RooFit.LineStyle(iColor != 50+1))#,r.RooFit.ProjWData(iData))
        iColor+=10

def draw(iVar,iData,iFuncs,iLabel="A"):
    lCan   = r.TCanvas(str(iLabel),str(iLabel),800,600)
    lFrame = iVar.frame()
    drawFrame(lFrame,iData,iFuncs)
    lFrame.Draw()
    lCan.Modified()
    lCan.Update()
    end()

def drawPF(iVar,iData,iFuncs,iLabel="A"):
    lCan   = r.TCanvas(str(iLabel),str(iLabel),800,600)
    lCan.Divide(2)
    lPFrame = iVar.frame(r.RooFit.Bins(30),r.RooFit.Title("pass"))
    lFFrame = iVar.frame(r.RooFit.Bins(30),r.RooFit.Title("fail"))
    drawFrame(lPFrame,iData[0],iFuncs[0])
    drawFrame(lFFrame,iData[1],iFuncs[1])
    lCan.cd(1)
    lPFrame.Draw()
    lCan.cd(2)
    lFFrame.Draw()
    lCan.Modified()
    lCan.Update()
    end()

def shift(iVar,iDataHist,iShift=5.):
    lInt    = iDataHist.createHistogram("x").Integral()
    lDM     = r.RooRealVar   ("Xdm","Xdm", 0.,-10,10)
    lShift  = r.RooFormulaVar("Xshift",iVar.GetName()+"-Xdm",r.RooArgList(iVar,lDM))  
    lSPdf   = r.RooHistPdf(iDataHist.GetName()+"P",iDataHist.GetName()+"P", r.RooArgList(lShift),r.RooArgList(iVar),iDataHist,0)
    lDM.setVal(iShift)
    lHUp   = lSPdf.createHistogram("x")
    lHUp.Scale(lInt)
    lUp    = r.RooDataHist(iDataHist.GetName()+"_scaleUp",iDataHist.GetName()+"_scaleUp", r.RooArgList(iVar),lHUp)
    lDM.setVal(-iShift)
    lHDown = lSPdf.createHistogram("x")
    lHDown.Scale(lInt)
    lDown  = r.RooDataHist(iDataHist.GetName()+"_scaleDown",iDataHist.GetName()+"_scaleDown", r.RooArgList(iVar),lHDown)
    return (lUp,lDown)

def smear(iVar,iDataHist,iScale=0.1):
    lDM     = r.RooRealVar("Xshift","Xshift", 1.,0.,2.)
    lVar    = iDataHist.createHistogram("x").GetMean()
    lInt    = iDataHist.createHistogram("x").Integral()
    lShift  = r.RooFormulaVar("Xsmear","("+iVar.GetName()+"-"+str(lVar)+")/Xshift+"+str(lVar),r.RooArgList(iVar,lDM))  
    lHPdf   = r.RooHistPdf(iDataHist.GetName()+"S",iDataHist.GetName()+"S", r.RooArgList(lShift),r.RooArgList(iVar),iDataHist,0)
    lDM.setVal(1.+iScale)
    lHUp = lHPdf.createHistogram("x")
    lHUp.Scale(lInt)
    lUp = r.RooDataHist(iDataHist.GetName()+"_smearUp",iDataHist.GetName()+"_smearUp", r.RooArgList(iVar),lHUp)    
    lDM.setVal(1.-iScale)
    lHDown = lHPdf.createHistogram("x")
    lHDown.Scale(lInt)
    lDown  = r.RooDataHist(iDataHist.GetName()+"_smearDown",iDataHist.GetName()+"_smearDown", r.RooArgList(iVar),lHDown)
    return [lUp,lDown]    

def proj(iLabel,iBin,iH,iNBins,iXMin,iXMax):
    lH = r.TH1D(iH.GetName()+"_"+iLabel+iBin,iH.GetName()+"_"+iLabel+iBin,iNBins,iXMin,iXMax)
    for iM in range(1,iH.GetNbinsX()+1):
        if iH.GetXaxis().GetBinCenter(iM) < lH.GetXaxis().GetXmin() or iH.GetXaxis().GetBinCenter(iM) > lH.GetXaxis().GetXmax():
            continue
        lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),iH.GetBinContent(iM,int(iBin)))
        lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),iH.GetBinError(iM,int(iBin)))
    lH.SetDirectory(0)
    return lH

def projMuCR(iLabel,iBin,iH,iNBins,iXMin,iXMax):
    lH = r.TH1D(iLabel,iLabel,iNBins,iXMin,iXMax)
    for iM in range(1,iH.GetNbinsX()+1):
        if iH.GetXaxis().GetBinCenter(iM) < lH.GetXaxis().GetXmin() or iH.GetXaxis().GetBinCenter(iM) > lH.GetXaxis().GetXmax():
            continue
        lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),iH.GetBinContent(iM,int(iBin)))
        lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),iH.GetBinError(iM,int(iBin)))
    lH.SetDirectory(0)
    return lH


def proj3D(iLabel,iBin,iGENptBin,iH,iNBins,iXMin,iXMax):
    lH = r.TH1D(iH.GetName()+"_"+iLabel+iBin+"_"+iGENptBin,iH.GetName()+"_"+iLabel+iBin+"_"+iGENptBin,iNBins,iXMin,iXMax)
    for iM in range(1,iH.GetNbinsX()+1):
        if iH.GetXaxis().GetBinCenter(iM) < lH.GetXaxis().GetXmin() or iH.GetXaxis().GetBinCenter(iM) > lH.GetXaxis().GetXmax():
            continue
        lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),iH.GetBinContent(iM,int(iBin),int(iGENptBin)))
        lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),iH.GetBinError(iM,int(iBin),int(iGENptBin)))
    lH.SetDirectory(0)
    return lH

def proj_PtRange(iLabel,iBin,iYMin,iYMax,iH,iNBins,iXMin,iXMax):
    lH = r.TH1F(iH.GetName()+"_"+iLabel+iBin,iH.GetName()+"_"+iLabel+iBin,iNBins,iXMin,iXMax)
    print "iH.GetName(): ", iH.GetName()
    for iM in range(1,iH.GetNbinsX()+1):
        if iH.GetXaxis().GetBinCenter(iM) < lH.GetXaxis().GetXmin() or iH.GetXaxis().GetBinCenter(iM) > lH.GetXaxis().GetXmax():
            continue
        if iYMin == 450 and iYMax == 600:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin))+iH.GetBinContent(iM,int(iBin)+1)+iH.GetBinContent(iM,int(iBin)+2)))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin))**2+iH.GetBinError(iM,int(iBin)+1)**2+iH.GetBinError(iM,int(iBin)+2)**2))
        elif iYMin == 600 and iYMax == 1000:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin)+2)+iH.GetBinContent(iM,int(iBin)+2+1)+iH.GetBinContent(iM,int(iBin)+2+2)))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin)+2)**2+iH.GetBinError(iM,int(iBin)+2+1)**2+iH.GetBinError(iM,int(iBin)+2+2)**2))
        elif iYMin == 450 and iYMax == 550:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin))+iH.GetBinContent(iM,int(iBin)+1)))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin))**2+iH.GetBinError(iM,int(iBin)+1)**2))
        elif iYMin == 550 and iYMax == 800:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin)+1)+iH.GetBinContent(iM,int(iBin)+1+1)+iH.GetBinContent(iM,int(iBin)+1+2)))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin)+1)**2+iH.GetBinError(iM,int(iBin)+1+1)**2+iH.GetBinError(iM,int(iBin)+1+2)**2))
#        elif iYMin == 800 and iYMax == 1000:
#                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin)+3)))
#                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin)+3)**2))
	elif iYMin == 450 and iYMax == 1000:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin))+iH.GetBinContent(iM,int(iBin)+1)+iH.GetBinContent(iM,int(iBin)+2)+iH.GetBinContent(iM,int(iBin)+3)+iH.GetBinContent(iM,int(iBin)+4)+iH.GetBinContent(iM,int(iBin)+5)))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin))**2+iH.GetBinError(iM,int(iBin)+1)**2+iH.GetBinError(iM,int(iBin)+2)**2+iH.GetBinError(iM,int(iBin)+3)**2+iH.GetBinError(iM,int(iBin)+4)**2+iH.GetBinError(iM,int(iBin)+5)**2))
        elif iYMin == 450 and iYMax == 500:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin))**2))
        elif iYMin == 500 and iYMax == 675:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin))+iH.GetBinContent(iM,int(iBin)+1)+iH.GetBinContent(iM,int(iBin)+1+1)+iH.GetBinContent(iM,int(iBin)+1+2)))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin))**2+iH.GetBinError(iM,int(iBin)+1)**2+iH.GetBinError(iM,int(iBin)+1+1)**2+iH.GetBinError(iM,int(iBin)+1+2)**2))
        elif iYMin == 675 and iYMax == 1000:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin)+2)+iH.GetBinContent(iM,int(iBin)+3)))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin)+2)**2+iH.GetBinError(iM,int(iBin)+3)**2))
        elif iYMin == 500 and iYMax == 550:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin))**2))
        elif iYMin == 550 and iYMax == 600:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin))**2))
        elif iYMin == 600 and iYMax == 675:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin))**2))
        elif iYMin == 675 and iYMax == 800:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin))**2))
        elif iYMin == 800 and iYMax == 1000:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin))**2))

        else:
                print "iYMin: ", iYMin
                print "iYMax: ", iYMax
                print "FAIL!!!!"
                print "Need to add conditional statements to proj_PtRange function in tools.py"
    lH.SetDirectory(0)
    return lH

def proj3D_PtRange(iLabel,iBin,iYMin,iYMax,iGENptBin,iH,iNBins,iXMin,iXMax):
    lH = r.TH1D(iH.GetName()+"_"+iLabel+iBin+"_"+iGENptBin,iH.GetName()+"_"+iLabel+iBin+"_"+iGENptBin,iNBins,iXMin,iXMax)
    for iM in range(1,iH.GetNbinsX()+1):
        if iH.GetXaxis().GetBinCenter(iM) < lH.GetXaxis().GetXmin() or iH.GetXaxis().GetBinCenter(iM) > lH.GetXaxis().GetXmax():
            continue
        if iYMin == 450 and iYMax == 600:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin),int(iGENptBin))+iH.GetBinContent(iM,int(iBin)+1,int(iGENptBin))+iH.GetBinContent(iM,int(iBin)+2,int(iGENptBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin),int(iGENptBin))**2+iH.GetBinError(iM,int(iBin)+1,int(iGENptBin))**2+iH.GetBinError(iM,int(iBin)+2,int(iGENptBin))**2))
        elif iYMin == 600 and iYMax == 1000:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin)+2,int(iGENptBin))+iH.GetBinContent(iM,int(iBin)+2+1,int(iGENptBin))+iH.GetBinContent(iM,int(iBin)+2+2,int(iGENptBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin)+2,int(iGENptBin))**2+iH.GetBinError(iM,int(iBin)+2+1,int(iGENptBin))**2+iH.GetBinError(iM,int(iBin)+2+2,int(iGENptBin))**2))
        elif iYMin == 450 and iYMax == 550:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin),int(iGENptBin))+iH.GetBinContent(iM,int(iBin)+1,int(iGENptBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin),int(iGENptBin))**2+iH.GetBinError(iM,int(iBin)+1,int(iGENptBin))**2))
        elif iYMin == 550 and iYMax == 800:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin)+1,int(iGENptBin))+iH.GetBinContent(iM,int(iBin)+1+1,int(iGENptBin))+iH.GetBinContent(iM,int(iBin)+1+2,int(iGENptBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin)+1,int(iGENptBin))**2+iH.GetBinError(iM,int(iBin)+1+1,int(iGENptBin))**2+iH.GetBinError(iM,int(iBin)+1+2,int(iGENptBin))**2))
#        elif iYMin == 800 and iYMax == 1000:
#                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin)+3,int(iGENptBin))))
#                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin)+3,int(iGENptBin))**2))
        elif iYMin == 450 and iYMax == 1000:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin),int(iGENptBin))+iH.GetBinContent(iM,int(iBin)+1,int(iGENptBin))+iH.GetBinContent(iM,int(iBin)+2,int(iGENptBin))+iH.GetBinContent(iM,int(iBin)+3,int(iGENptBin))+iH.GetBinContent(iM,int(iBin)+4,int(iGENptBin))+iH.GetBinContent(iM,int(iBin)+5,int(iGENptBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin),int(iGENptBin))**2+iH.GetBinError(iM,int(iBin)+1,int(iGENptBin))**2+iH.GetBinError(iM,int(iBin)+2,int(iGENptBin))**2+iH.GetBinError(iM,int(iBin)+3,int(iGENptBin))**2+iH.GetBinError(iM,int(iBin)+4,int(iGENptBin))**2+iH.GetBinError(iM,int(iBin)+5,int(iGENptBin))**2))
        elif iYMin == 450 and iYMax == 500:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin),int(iGENptBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin),int(iGENptBin))**2))
        elif iYMin == 500 and iYMax == 675:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin),int(iGENptBin))+iH.GetBinContent(iM,int(iBin)+1,int(iGENptBin))+iH.GetBinContent(iM,int(iBin)+1+1,int(iGENptBin))+iH.GetBinContent(iM,int(iBin)+1+2,int(iGENptBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin),int(iGENptBin))**2+iH.GetBinError(iM,int(iBin)+1,int(iGENptBin))**2+iH.GetBinError(iM,int(iBin)+1+1,int(iGENptBin))**2+iH.GetBinError(iM,int(iBin)+1+2,int(iGENptBin))**2))
        elif iYMin == 675 and iYMax == 1000:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin)+2,int(iGENptBin))+iH.GetBinContent(iM,int(iBin)+3,int(iGENptBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin)+2,int(iGENptBin))**2+iH.GetBinError(iM,int(iBin)+3,int(iGENptBin))**2))
        elif iYMin == 500 and iYMax == 550:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin),int(iGENptBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin),int(iGENptBin))**2))
        elif iYMin == 550 and iYMax == 600:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin),int(iGENptBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin),int(iGENptBin))**2))
        elif iYMin == 600 and iYMax == 675:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin),int(iGENptBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin),int(iGENptBin))**2))
        elif iYMin == 675 and iYMax == 800:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin),int(iGENptBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin),int(iGENptBin))**2))
        elif iYMin == 800 and iYMax == 1000:
                lH.SetBinContent(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),(iH.GetBinContent(iM,int(iBin),int(iGENptBin))))
                lH.SetBinError(lH.FindBin(iH.GetXaxis().GetBinCenter(iM)),math.sqrt(iH.GetBinError(iM,int(iBin),int(iGENptBin))**2))

        else:
                print "iYMin: ", iYMin
                print "iYMax: ", iYMax
                print "FAIL!!!!"
                print "Need to add conditional statements to proj_PtRange function in tools.py"
    lH.SetDirectory(0)
    return lH

def workspace(iOutput,iDatas,iFuncs,iVars,iCat="cat0",iShift=True):
    lW = r.RooWorkspace("w_"+str(iCat))
    for pData in iDatas:
        getattr(lW,'import')(pData,r.RooFit.RecycleConflictNodes())
    
    for pFunc in iFuncs:
        getattr(lW,'import')(pFunc,r.RooFit.RecycleConflictNodes())
        if iShift and pFunc.GetName().find("qq") > -1:
            (pFUp, pFDown)  = shift(iVars[0],pFunc,5.)
            (pSFUp,pSFDown) = smear(iVars[0],pFunc,0.05)
            getattr(lW,'import')(pFUp,  r.RooFit.RecycleConflictNodes())
            getattr(lW,'import')(pFDown,r.RooFit.RecycleConflictNodes())
            getattr(lW,'import')(pSFUp,  r.RooFit.RecycleConflictNodes())
            getattr(lW,'import')(pSFDown,r.RooFit.RecycleConflictNodes())
    
    if iCat.find("pass_cat1") == -1:
        lW.writeToFile(iOutput,False)
    else:
        lW.writeToFile(iOutput)

