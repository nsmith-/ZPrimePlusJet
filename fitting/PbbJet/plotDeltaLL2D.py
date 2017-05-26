import ROOT as rt
from tools import *
from array import array
from scipy.interpolate import Rbf, interp1d
import itertools
import numpy as np

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


def interpolate2D(hist,epsilon=1,smooth=0):
    x = array('d',[])
    y = array('d',[])
    z = array('d',[])
    
    binWidthX = float(hist.GetXaxis().GetBinWidth(1))
    binWidthY = float(hist.GetYaxis().GetBinWidth(1))
    
    for i in range(1, hist.GetNbinsX()+1):
        for j in range(1, hist.GetNbinsY()+1):
            if hist.GetBinContent(i,j)>0.:
                x.append(hist.GetXaxis().GetBinCenter(i))
                y.append(hist.GetYaxis().GetBinCenter(j))
                z.append(hist.GetBinContent(i,j))

    mgMin = hist.GetXaxis().GetBinCenter(1)
    mgMax = hist.GetXaxis().GetBinCenter(hist.GetNbinsX())#+hist.GetXaxis().GetBinWidth(hist.GetNbinsX())
    mchiMin = hist.GetYaxis().GetBinCenter(1)
    mchiMax = hist.GetYaxis().GetBinCenter(hist.GetNbinsY())#+hist.GetYaxis().GetBinWidth(hist.GetNbinsY())
    
    myX = np.linspace(mgMin, mgMax,int((mgMax-mgMin)/binWidthX+1))
    myY = np.linspace(mchiMin, mchiMax, int((mchiMax-mchiMin)/binWidthY+1))
    myXI, myYI = np.meshgrid(myX,myY)

    rbf = Rbf(x, y, z, function='multiquadric', epsilon=epsilon,smooth=smooth)
    myZI = rbf(myXI, myYI)
    
    for i in range(1, hist.GetNbinsX()+1):
        for j in range(1, hist.GetNbinsY()+1):
            if hist.GetBinContent(i,j)<=0.:
                hist.SetBinContent(i,j,myZI[j-1][i-1])
    return hist

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
    #rt.gStyle.SetPalette(rt.kBlackBody)
    #rt.gStyle.SetPalette(rt.kBird)
    #rt.gStyle.SetPalette(rt.kCherry)
    stops = [ 0.0, 1.0]
    red =   [ 1.0, 0.3]
    green = [ 1.0, 0.3]
    blue =  [ 1.0, 1.0]

    s = array('d', stops)
    r = array('d', red)
    g = array('d', green)
    b = array('d', blue)

    npoints = len(s)
    rt.TColor.CreateGradientColorTable(npoints, s, r, g, b, 999)

    rt.gStyle.SetNumberContours(999)

    #exec_me('combine -M MultiDimFit --minimizerTolerance 0.001 --minimizerStrategy 2  --setPhysicsModelParameterRanges r=0,5:r_z=0,2 --algo grid --points 100 -d card_rhalphabet_muonCR_floatZ.root -n 2D --saveWorkspace',True)
    c = rt.TCanvas('c','c',500,400)
    
    if options.isData:
        #dataTag = 'data_nosys'
        dataTag = 'data'
    else:
        #dataTag = 'asimov_nosys'
        dataTag = 'asimov'
    
    tfile = rt.TFile.Open('higgsCombine2D_%s.MultiDimFit.mH120.root'%(dataTag))
    limit = tfile.Get('limit')
    fit = bestFit(limit, 'r', 'r_z')
    limit.Draw("r_z:r>>htemp(21,-4,8,21,0,3)","2*deltaNLL*(quantileExpected>-1)*(deltaNLL>0)*(deltaNLL<100)","colz")
    #limit.Draw("r_z:r>>htemp(21,-6,12,21,0,3)","2*deltaNLL*(quantileExpected>-1)*(deltaNLL>0)*(deltaNLL<100)","colz")
    #contours = array('d',[2.3,5.99])
    htemp = rt.gPad.GetPrimitive('htemp')
    if options.isData:
        htemp.SetBinContent(htemp.FindBin(1.5,0.5),0)
    htemp = interpolate2D(htemp)
    htemp.GetXaxis().SetTitle('#mu_{H}')
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
    cl997 = contourFromTH2(htemp, 11.83)
    cl68.SetLineColor(rt.kBlack)
    cl68.SetLineWidth(2)
    cl68.SetLineStyle(1)
    cl95.SetLineColor(rt.kBlack)
    cl95.SetLineWidth(2)
    cl95.SetLineStyle(2)
    cl997.SetLineColor(rt.kBlack)
    cl997.SetLineWidth(2)
    cl997.SetLineStyle(3)
    
    htemp.DrawCopy("colz")
    cl68.Draw("L SAME")
    cl95.Draw("L SAME")
    #cl997.Draw("L SAME")
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


    leg = rt.TLegend(0.55,0.7,0.8,0.87)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    leg.SetFillColor(rt.kWhite)
    leg.SetLineColor(rt.kWhite)
    leg.SetLineStyle(0)
    leg.SetFillStyle(0)
    leg.SetLineWidth(0)
    leg.AddEntry(fit, "Best fit", "p")
    leg.AddEntry(m, "SM expected", "p")
    leg.AddEntry(cl68, "68% CL", "l")
    leg.AddEntry(cl95, "95% CL", "l")
    leg.Draw("same")


    
    
    c.Print('deltaLL2D_%s.pdf'%dataTag.lower())
    c.Print('deltaLL2D_%s.C'%dataTag.lower())

    
    htemp.Draw("axis")
    cl68.Draw("L SAME")
    cl95.Draw("L SAME")
    #cl997.Draw("L SAME")
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

    leg = rt.TLegend(0.55,0.7,0.8,0.87)
    leg.SetBorderSize(0)
    leg.SetTextFont(42)
    leg.SetFillColor(rt.kWhite)
    leg.SetLineColor(rt.kWhite)
    leg.SetLineStyle(0)
    leg.SetFillStyle(0)
    leg.SetLineWidth(0)
    leg.AddEntry(fit, "Best fit", "p")
    leg.AddEntry(m, "SM expected", "p")
    leg.AddEntry(cl68, "68% CL", "l")
    leg.AddEntry(cl95, "95% CL", "l")
    leg.Draw("same")

    
    c.Print('deltaLL2D_noHist_%s.pdf'%dataTag)
    c.Print('deltaLL2D_noHist_%s.C'%dataTag)

