import ROOT as rt
from RootIterator import RootIterator

from optparse import OptionParser


poiMap = {'r_w':"#mu_{W}",
          'r_z':"#mu_{Z}",
          'r_wz':"#mu_{WZ}"}
        
def getCatDict(poi):
    catDict = {}
    catDict['muonCR',poi] = '#splitline{Combined}{   #scale[0.8]{'+poiMap[poi]+' = %.2f_{#minus%.2f}^{+%.2f}}}'
    catDict['cat1',poi] = '#splitline{[450, 500] GeV}{    #scale[0.8]{'+poiMap[poi]+' = %.2f_{#minus%.2f}^{+%.2f}}}'
    catDict['cat2',poi] = '#splitline{[500, 550] GeV}{    #scale[0.8]{'+poiMap[poi]+' = %.2f_{#minus%.2f}^{+%.2f}}}'
    catDict['cat3',poi] = '#splitline{[550, 600] GeV}{    #scale[0.8]{'+poiMap[poi]+' = %.2f_{#minus%.2f}^{+%.2f}}}'
    catDict['cat4',poi] = '#splitline{[600, 675] GeV}{    #scale[0.8]{'+poiMap[poi]+' = %.2f_{#minus%.2f}^{+%.2f}}}'
    catDict['cat5',poi] = '#splitline{[675, 800] GeV}{    #scale[0.8]{'+poiMap[poi]+' = %.2f_{#minus%.2f}^{+%.2f}}}'
    catDict['cat6',poi] = '#splitline{[800, 1000] GeV}{     #scale[0.8]{'+poiMap[poi]+' = %.2f_{#minus%.2f}^{+%.2f}}}'
    return catDict

def cccPlot(f = rt.gFile, poi = "r", rMin =-10, rMax=15, filename="ccc_r.pdf"):
    c1 = rt.TCanvas("c1")
    c1.SetLeftMargin(0.4)
    c1.SetBottomMargin(0.12)
    c1.SetGridx(1)
    if (f == 0):
        print "No input file open"
        sys.exit()
    fit_nominal   = f.Get("fit_nominal")
    fit_alternate = f.Get("fit_alternate")
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

    frame = rt.TH2F("frame",";%s;"%poiMap[poi],1,rMin,rMax,nChann,0,nChann)

    iChann = 0
    points = rt.TGraphAsymmErrors(nChann)
    catDict = getCatDict(poi)
    
    for a in sorted(RootIterator(fit_alternate.floatParsFinal())):
        if (rt.TString(a.GetName()).Index(prefix) == 0):
            ri = a
            channel = a.GetName()
            channel = channel.replace(prefix,"")            
            if channel=='muonCR':
                # put at some dummy value
                points.SetPoint(iChann,       100, iChann+0.5)
                points.SetPointError(iChann, -1, 1, 0, 0)
            else:
                points.SetPoint(iChann,       ri.getVal(), iChann+0.5)
                points.SetPointError(iChann, -ri.getAsymErrorLo(), ri.getAsymErrorHi(), 0, 0)
            iChann+=1
            if channel=='muonCR':
                frame.GetYaxis().SetBinLabel(iChann, (catDict[channel,options.poi]%(rFit.getVal(),-rFit.getAsymErrorLo(), rFit.getAsymErrorHi())).replace('-','#minus'))
            else:
                frame.GetYaxis().SetBinLabel(iChann, (catDict[channel,options.poi]%(ri.getVal(),-ri.getAsymErrorLo(), ri.getAsymErrorHi())).replace('-','#minus'))
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
    l.DrawLatex(0.41,0.8,"Preliminary")
    tag1 = rt.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%(options.lumi))
    tag1.SetNDC()
    tag1.SetTextFont(42)
    tag1.SetTextSize(0.045)
    tag1.Draw()
    
    c1.RedrawAxis()
    c1.Print(filename)
    c1.Print(filename.replace('.pdf','.C'))

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option('--rMin',dest='rMin', default=-10 ,type='float',help='minimum of r (signal strength) in profile likelihood plot')
    parser.add_option('--rMax',dest='rMax', default=15,type='float',help='maximum of r (signal strength) in profile likelihood plot')  
    parser.add_option('--lumi',dest='lumi', default=35.9,type='float',help='lumi')

    parser.add_option('-P','--poi'   ,action='store',type='string',dest='poi'   ,default='r', help='poi name')  

    
    (options, args) = parser.parse_args()
    rt.gROOT.SetBatch()
    for arg in args:
        if '.root' in arg:
            f = rt.TFile.Open(arg,'r')
            cccPlot(f, options.poi, options.rMin, options.rMax, "ccc_"+options.poi+".pdf")
            f.Close()
