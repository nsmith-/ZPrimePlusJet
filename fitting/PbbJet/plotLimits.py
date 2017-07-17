from optparse import OptionParser
import ROOT
from ROOT import TFile, TTree, TCanvas, TGraph, TMultiGraph, TGraphErrors, TLegend
import CMS_lumi, tdrstyle
import subprocess # to execute shell command
ROOT.gROOT.SetBatch(ROOT.kTRUE)

# CMS style
CMS_lumi.cmsText = "CMS"
CMS_lumi.extraText = "Preliminary"
CMS_lumi.cmsTextSize = 0.65
CMS_lumi.outOfFrame = True
tdrstyle.setTDRStyle()

def massIterable(massList):
    if len(massList.split(','))==1:
        massIterableList = [massList]
    else:
        massIterableList = list(eval(massList))
    return massIterableList


# GET limits from root file
def getLimits(file_name):

    file = TFile(file_name)
    tree = file.Get("limit")

    limits = [ ]
    for quantile in tree:
        limits.append(tree.limit)
        #print ">>>   %.2f" % limits[-1]

    return limits[:6]


# PLOT upper limits
def plotUpperLimits():
    # see CMS plot guidelines: https://ghm.web.cern.ch/ghm/plots/
    masses = [50, 100, 125, 200, 300, 350, 400, 500]
    xsection = [1.574e-02, 1.526e-02, 1.486e-02, 1.359e-02, 1.251e-02, 1.275e-02, 1.144e-02, 7.274e-03]
    N = len(masses)
    print " No of mass points : ", N
    yellow = TGraph(2*N)    # yellow band
    green = TGraph(2*N)     # green band
    median = TGraph(N)      # median line
    obs = TGraph(N)       # observed
    if options.xsec: theory_xsec = TGraph(N)       # theory cross section
    jet_type = 'AK8'
    if options.fillCA15:
        jet_type = 'CA15'
    cut = options.cuts.split(',')[0]   

    up2s = [ ]
    for i in range(N):
        file_name = options.ifile+ "/%s/%s/DMSbb%s/higgsCombineTest.Asymptotic.mH120.root"%(jet_type,cut,str(masses[i]))
        print "Opened File ", file_name
        limit = getLimits(file_name)
        up2s.append(limit[4])
        if options.xsec: fac = xsection[i]
        else: fac = 1
        yellow.SetPoint(    i,    masses[i], limit[4] * fac ) # + 2 sigma
        green.SetPoint(     i,    masses[i], limit[3] * fac ) # + 1 sigma
        median.SetPoint(    i,    masses[i], limit[2] * fac ) # median
        green.SetPoint(  2*N-1-i, masses[i], limit[1] * fac ) # - 1 sigma
        yellow.SetPoint( 2*N-1-i, masses[i], limit[0] * fac ) # - 2 sigma
        obs.SetPoint(       i,    masses[i], limit[5] * fac) # observed
        if options.xsec : theory_xsec.SetPoint(       i,    masses[i], xsection[i]) # theory x-section

    W = 800
    H  = 600
    T = 0.08*H
    B = 0.12*H
    L = 0.12*W#*scaleleftmargin
    R = 0.04*W#*scalerightmargin
    c = TCanvas("c","c",100,100,W,H)
    c.SetFillColor(0)
    c.SetBorderMode(0)
    c.SetFrameFillStyle(0)
    c.SetFrameBorderMode(0)
    c.SetLeftMargin( L/W )
    c.SetRightMargin( R/W )
    c.SetTopMargin( T/H )
    c.SetBottomMargin( B/H )
    c.SetTickx(0)
    c.SetTicky(0)
    c.SetGrid()
    c.cd()
    frame = c.DrawFrame(1.4,0.001, 4.1, 10)
    frame.GetYaxis().CenterTitle()
    frame.GetYaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetTitleSize(0.05)
    frame.GetXaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetLabelSize(0.04)
    frame.GetYaxis().SetTitleOffset(0.9)
    frame.GetXaxis().SetNdivisions(508)
    frame.GetYaxis().CenterTitle(True)
    #frame.GetYaxis().SetTitle("95% upper limit on #sigma / #sigma_{SM}")
#    frame.GetYaxis().SetTitle("95% upper limit on #sigma #times BR / (#sigma #times BR)_{SM}")
    #frame.GetXaxis().SetTitle("background systematic uncertainty [%]")
    if options.xsec: 
        frame.SetMinimum(0.001)
        frame.SetMaximum(100)
    else:
        frame.SetMinimum(0)
        frame.SetMaximum(max(up2s)*1.05)
    frame.GetXaxis().SetLimits(min(masses),max(masses))

    yellow.SetFillColor(ROOT.kOrange)
    yellow.SetLineColor(ROOT.kOrange)
    yellow.SetFillStyle(1001)
    yellow.Draw('F')
    
    green.SetFillColor(ROOT.kGreen+1)
    green.SetLineColor(ROOT.kGreen+1)
    green.SetFillStyle(1001)
    green.Draw('Fsame')

    median.SetLineColor(1)
    median.SetLineWidth(2)
    median.SetLineStyle(2)
    median.Draw('Lsame')
    
    obs.SetMarkerStyle(20)
    obs.SetLineWidth(2)
    obs.Draw('PLsame')

    if options.xsec:
        theory_xsec.SetMarkerStyle(20)
        theory_xsec.SetLineWidth(2)
        theory_xsec.Draw('Lsame')

    CMS_lumi.CMS_lumi(c,13,11)
    ROOT.gPad.SetTicks(1,1)
    frame.Draw('sameaxis')

    x1 = 0.22
    x2 = x1 + 0.24
    if options.xsec: y1 = 0.68
    else: y1 = 0.58
    y2 = y1 + 0.16
    legend = TLegend(x1,y1,x2,y2)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.041)
    legend.SetTextFont(42)
    legend.AddEntry(obs, "Observed",'lp')
    legend.AddEntry(median, "Asymptotic CL_{s} expected",'L')
    legend.AddEntry(green, "#pm 1 std. deviation",'f')
    #legend.AddEntry(green, "Asymptotic CL_{s} #pm 1 std. deviation",'f')
    legend.AddEntry(yellow,"#pm 2 std. deviation",'f')
    if options.xsec: legend.AddEntry(theory_xsec,"Theory x-sec",'l')
    #legend.AddEntry(yellow, "Asymptotic CL_{s} #pm 2 std. deviation",'f')
    legend.Draw()

    print " "
    if options.xsec: c.SetLogy()
    if options.xsec: c.SaveAs("Limit_" + jet_type + "_" + cut+ "_xsec.png") 
    else: c.SaveAs("Limit_" + jet_type + "_" + cut+ ".png")
    #c.SaveAs("Limit_" + jet_type + "_" + cut+ ".C")    
    c.Close()

# MAIN
def main(options,args):

    plotUpperLimits()



if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("--lumi", dest="lumi", default=35.9, type="float", help="luminosity", metavar="lumi")
    parser.add_option('-c', '--cuts', dest='cuts', default='p9', type='string', help='double b-tag cut value')
    parser.add_option('-x','--xsec', dest='xsec', action='store_true',default=False, help='cross_section',metavar='xsec')
    parser.add_option('--fillCA15', action='store_true', dest='fillCA15', default =False,help='for CA15', metavar='fillCA15')
    parser.add_option('-i', '--ifile', dest='ifile', default='hist_1DZbb.root', help='file with histogram inputs',metavar='ifile')

    (options,args) = parser.parse_args()   
    main(options,args) 
