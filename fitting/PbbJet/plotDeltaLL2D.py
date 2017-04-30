

import ROOT as rt
from tools import *
from array import array

def exec_me(command,dryRun=True):
    print command
    if not dryRun: os.system(command)
##-------------------------------------------------------------------------------------

def bestFit(t, x, y):
    nfind = t.Draw(y+":"+x, "deltaNLL == 0")
    if (nfind == 0):
        gr0 = rt.TGraph(1)
        gr0.SetPoint(0,-999,-999)
        gr0.SetMarkerStyle(34)
        gr0.SetMarkerSize(1.5)
        return gr0
    else:
        gr0 = rt.gROOT.FindObject("Graph").Clone()
        gr0.SetMarkerStyle(34)
        gr0.SetMarkerSize(1.5)
        if (gr0.GetN() > 1):
            gr0.Set(1)
        return gr0
def frameTH2D(hin, threshold):
    frameValue = 1000
    xw = hin.GetXaxis().GetBinWidth(1)
    yw = hin.GetYaxis().GetBinWidth(1)
    nx = hin.GetNbinsX()
    ny = hin.GetNbinsY()
    x0 = hin.GetXaxis().GetXmin()
    x1 = hin.GetXaxis().GetXmax()
    y0 = hin.GetYaxis().GetXmin()
    y1 = hin.GetYaxis().GetXmax()
    xbins = array('d',[frameValue]*999)
    ybins = array('d',[frameValue]*999)
    eps = 0.001
    xbins[0] = x0 - eps*xw - xw
    xbins[1] = x0 + eps*xw - xw;
    for ix in range(2, nx+1):
        xbins[ix] = x0 + (ix-1)*xw
    xbins[nx+1] = x1 - eps*xw + 0.5*xw
    xbins[nx+2] = x1 + eps*xw + xw
    ybins[0] = y0 - eps*yw - yw
    ybins[1] = y0 + eps*yw - yw
    for iy in range(2, ny+1):
        ybins[iy] = y0 + (iy-1)*yw
    ybins[ny+1] = y1 - eps*yw + yw
    ybins[ny+2] = y1 + eps*yw + yw

    framed = rt.TH2D("%s framed"%hin.GetName(),"%s framed"%hin.GetTitle(),nx + 2, xbins,ny + 2, ybins)

    for ix in range(1, nx+1):
        for iy in range(1, ny+1):
            framed.SetBinContent(1+ix, 1+iy, hin.GetBinContent(ix,iy))

    nx = framed.GetNbinsX();
    ny = framed.GetNbinsY();
    for ix in range(1, nx+1):
        framed.SetBinContent(ix,  1, frameValue)
        framed.SetBinContent(ix, ny, frameValue)
    for iy in range(2, ny):
        framed.SetBinContent( 1, iy, frameValue)
        framed.SetBinContent(nx, iy, frameValue)

    return framed

def contourFromTH2(h2in, threshold, minPoints=20):
    
    contours = array('d',[threshold])
    hframed = frameTH2D(h2in, 2.3)
    hframed.SetContour(1,contours)
    hframed.Draw("CONT Z LIST")
    rt.gPad.Update()


    conts = rt.gROOT.GetListOfSpecials().FindObject("contours")
    contour0 = conts.At(0)
    curv = contour0.First()
    finalcurv = rt.TGraph(1)
    try:
        curv.SetLineWidth(3)
        curv.SetLineColor(rt.kBlack)
        curv.Draw("lsame")
        finalcurv = curv.Clone()
        maxN = curv.GetN()
    except AttributeError:
        print "ERROR: no curve drawn for box=%s, clsType=%s -- no limit "%(box, clsType)

    for i in xrange(1, contour0.GetSize()):
        curv = contour0.After(curv)
        curv.SetLineWidth(3)
        curv.SetLineColor(rt.kBlack)
        curv.Draw("lsame")
        if curv.GetN()>maxN:
            maxN = curv.GetN()
            finalcurv = curv.Clone()

    return finalcurv

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--data', action='store_true', dest='isData', default=False, help='is data')
    (options, args) = parser.parse_args()
     
    import tdrstyle
    tdrstyle.setTDRStyle()
    rt.gStyle.SetPadTopMargin(0.10)
    rt.gStyle.SetPadLeftMargin(0.16)
    rt.gStyle.SetPadRightMargin(0.18)
    rt.gStyle.SetPalette(1)
    rt.gStyle.SetPaintTextFormat("1.1f")
    rt.gStyle.SetOptFit(0000)
    rt.gROOT.SetBatch()
    rt.gStyle.SetOptTitle(0)
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetPalette(rt.kBlackBody)
    rt.gStyle.SetNumberContours(999)

    #exec_me('combine -M MultiDimFit --minimizerTolerance 0.001 --minimizerStrategy 2  --setPhysicsModelParameterRanges r=0,5:r_z=0,2 --algo grid --points 100 -d card_rhalphabet_muonCR_floatZ.root -n 2D --saveWorkspace',True)
    c = rt.TCanvas('c','c',500,400)
    
    if options.isData:
        dataTag = 'data'
    else:
        dataTag = 'asimov'
    
    tfile = rt.TFile.Open('higgsCombine2D_%s.MultiDimFit.mH120.root'%(dataTag))
    limit = tfile.Get('limit')
    fit = bestFit(limit, 'r', 'r_z')
    limit.Draw("r_z:r>>htemp(20,-4,8,20,0,3)","2*deltaNLL*(quantileExpected>-1)","colz")
    #contours = array('d',[2.3,5.99])
    htemp = rt.gPad.GetPrimitive('htemp')
    htemp.GetXaxis().SetTitle('#mu')
    htemp.GetYaxis().SetTitle('#mu_{Z}')
    htemp.GetZaxis().SetTitle('-2 #Delta log L(%s)'%dataTag)
    htemp.SetMinimum(0.)
    htemp.SetMaximum(16.)
    #htemp.DrawCopy("colz")
    #htemp.SetContour(2,contours)
    #htemp.Draw("cont3 same")
    htemp.SetLineColor(rt.kRed)
    
    cl68 = contourFromTH2(htemp, 2.3)
    cl95 = contourFromTH2(htemp, 5.99)
    cl68.SetLineColor(rt.kBlack)
    cl68.SetLineWidth(2)
    cl68.SetLineStyle(1)
    cl95.SetLineColor(rt.kBlack)
    cl95.SetLineWidth(2)
    cl95.SetLineStyle(2)
    
    htemp.DrawCopy("colz")
    cl68.Draw("L SAME")
    cl95.Draw("L SAME")
    fit.Draw("P SAME")

    smx = 1.
    smy = 1.
    m = rt.TMarker()
    m.SetMarkerSize(1.8)
    m.SetMarkerColor(rt.kBlack)
    m.SetMarkerStyle(29)
    m.DrawMarker(smx,smy)

    lumi = 35.9
    tag1 = rt.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.04)
    tag2 = rt.TLatex(0.17,0.92,"CMS")
    tag2.SetNDC(); tag2.SetTextFont(62)
    tag3 = rt.TLatex(0.27,0.92,"Preliminary")
    tag3.SetNDC(); tag3.SetTextFont(52)
    tag2.SetTextSize(0.05); tag3.SetTextSize(0.04); tag1.Draw(); tag2.Draw(); tag3.Draw()

    leg = rt.TLegend(0.6,0.7,0.85,0.87)
    leg.SetTextFont(42)
    leg.SetFillColor(rt.kWhite)
    leg.SetLineColor(rt.kWhite)
    leg.SetFillStyle(0)
    leg.SetLineWidth(0)
    leg.AddEntry(fit, "Best fit", "p")
    leg.AddEntry(m, "SM expected", "p")
    leg.AddEntry(cl68, "68% CL", "l")
    leg.AddEntry(cl95, "95% CL", "l")
    leg.Draw("same")

    
    
    c.Print('deltaLL2D_%s.pdf'%dataTag)
    c.Print('deltaLL2D_%s.C'%dataTag)

    
    htemp.Draw("axis")
    cl68.Draw("L SAME")
    cl95.Draw("L SAME")
    fit.Draw("P SAME")

    
    smx = 1.
    smy = 1.
    m = rt.TMarker()
    m.SetMarkerSize(1.8)
    m.SetMarkerColor(rt.kBlack)
    m.SetMarkerStyle(29)
    m.DrawMarker(smx,smy)
    
    lumi = 35.9
    tag1 = rt.TLatex(0.67,0.92,"%.1f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.04)
    tag2 = rt.TLatex(0.17,0.92,"CMS")
    tag2.SetNDC(); tag2.SetTextFont(62)
    tag3 = rt.TLatex(0.27,0.92,"Preliminary")
    tag3.SetNDC(); tag3.SetTextFont(52)
    tag2.SetTextSize(0.05); tag3.SetTextSize(0.04); tag1.Draw(); tag2.Draw(); tag3.Draw()

    leg = rt.TLegend(0.6,0.7,0.85,0.85)
    leg.SetTextFont(42)
    leg.SetFillColor(rt.kWhite)
    leg.SetLineColor(rt.kWhite)
    leg.SetFillStyle(0)
    leg.SetLineWidth(0)
    leg.AddEntry(fit, "Best fit", "p")
    leg.AddEntry(m, "SM expected", "p")
    leg.AddEntry(cl68, "68% CL", "l")
    leg.AddEntry(cl95, "95% CL", "l")
    leg.Draw("same")

    
    c.Print('deltaLL2D_noHist_%s.pdf'%dataTag)
    c.Print('deltaLL2D_noHist_%s.C'%dataTag)

