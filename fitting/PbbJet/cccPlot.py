import ROOT as rt
from RootIterator import RootIterator

catDict = {}
catDict['muonCR'] = '#splitline{Combined}{   #scale[0.8]{#mu=%.2f^{-%.2f}_{+%.2f}}}'
catDict['cat1'] = '#splitline{[450, 500  GeV]}{    #scale[0.8]{#mu=%.2f^{-%.2f}_{+%.2f}}}'
catDict['cat2'] = '#splitline{[500, 550  GeV]}{    #scale[0.8]{#mu=%.2f^{-%.2f}_{+%.2f}}}'
catDict['cat3'] = '#splitline{[550, 600  GeV]}{    #scale[0.8]{#mu=%.2f^{-%.2f}_{+%.2f}}}'
catDict['cat4'] = '#splitline{[600, 675  GeV]}{    #scale[0.8]{#mu=%.2f^{-%.2f}_{+%.2f}}}'
catDict['cat5'] = '#splitline{[675, 800  GeV]}{    #scale[0.8]{#mu=%.2f^{-%.2f}_{+%.2f}}}'
catDict['cat6'] = '#splitline{[800, 1000 GeV]}{     #scale[0.8]{#mu=%.2f^{-%.2f}_{+%.2f}}}'
def cccPlot(poi = "r", rMax=10, filename="ccc.pdf"):
    c1 = rt.TCanvas("c1")
    c1.SetLeftMargin(0.4)
    c1.SetBottomMargin(0.12)
    c1.SetGridx(1)
    if (rt.gFile == 0):
        print "No input file open"
        sys.exit()
    fit_nominal   = rt.gFile.Get("fit_nominal")
    fit_alternate = rt.gFile.Get("fit_alternate")
    if (fit_nominal == 0 or fit_alternate == 0):
        print"Input file ", gFile.GetName(), " does not contain fit_nominal or fit_alternate"
        sys.exit()
    rFit = fit_nominal.floatParsFinal().find(poi)
    if (rFit == 0):
        print "Nominal fit does not contain parameter ", poi
        sys.exit()

    prefix =  "_ChannelCompatibilityCheck_%s_"%poi

    nChann = 0
    for a in RootIterator(fit_alternate.floatParsFinal()):
        if prefix in a.GetName():
            nChann+=1
    frame = rt.TH2F("frame",";best fit #sigma/#sigma_{SM};",1,-10,15,nChann,0,nChann)

    iChann = 0
    points = rt.TGraphAsymmErrors(nChann)
    
    for a in sorted(RootIterator(fit_alternate.floatParsFinal())):
        if (rt.TString(a.GetName()).Index(prefix) == 0):
            ri = a
            channel = a.GetName()
            channel = channel.replace(prefix,"")
            points.SetPoint(iChann,       ri.getVal(), iChann+0.5)
            points.SetPointError(iChann, -ri.getAsymErrorLo(), ri.getAsymErrorHi(), 0, 0)
            iChann+=1
            if channel=='muonCR':
                frame.GetYaxis().SetBinLabel(iChann, catDict[channel]%(rFit.getVal(),-rFit.getAsymErrorLo(), rFit.getAsymErrorHi()))
            else:
                frame.GetYaxis().SetBinLabel(iChann, catDict[channel]%(ri.getVal(),-ri.getAsymErrorLo(), ri.getAsymErrorHi()))
    points.SetLineColor(rt.kRed)
    points.SetLineWidth(3)
    points.SetMarkerStyle(21)
    frame.GetXaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetLabelSize(0.06)
    frame.Draw()
    rt.gStyle.SetOptStat(0)
    globalFitBand = rt.TBox(rFit.getVal()+rFit.getAsymErrorLo(), 0, rFit.getVal()+rFit.getAsymErrorHi(), nChann)
    globalFitBand.SetFillColor(rt.kGreen)
    globalFitBand.SetLineStyle(0)
    globalFitBand.Draw('')
    globalFitLine = rt.TLine(rFit.getVal(), 0, rFit.getVal(), nChann)
    globalFitLine.SetLineWidth(4)
    globalFitLine.SetLineColor(214)
    globalFitLine.Draw('')
    points.Draw("PZ SAME")
    
    l = rt.TLatex()
    l.SetTextAlign(11)
    l.SetTextSize(0.045)
    l.SetNDC()
    l.SetTextFont(62)
    l.DrawLatex(0.41,0.85,"CMS")
    l.SetTextFont(52)
    l.DrawLatex(0.41,0.8,"Internal")
    tag1 = rt.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%(35.9))
    tag1.SetNDC()
    tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag1.Draw()
    
    c1.RedrawAxis()
    c1.Print(filename)
    c1.Print(filename.replace('.pdf','.C'))

if __name__ == '__main__':
    
    rt.gROOT.SetBatch()
    f = rt.TFile.Open('cards_2017_03_29_fixtrig_hptcorr/higgsCombineTest.ChannelCompatibilityCheck.mH125.root')
    cccPlot()
