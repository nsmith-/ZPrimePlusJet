from optparse import OptionParser
import ROOT as rt
import CMS_lumi, tdrstyle
import subprocess # to execute shell command
rt.gROOT.SetBatch(True)
import glob

# CMS style
CMS_lumi.cmsText = "CMS"
CMS_lumi.extraText = "Preliminary"
CMS_lumi.cmsTextSize = 0.65
CMS_lumi.outOfFrame = True
tdrstyle.setTDRStyle()


# GET limits from root file
def getLimits(file_name):
    
    tfile = rt.TFile.Open(file_name,'read')
    try:
        if tfile.InheritsFrom("TFile") is False:
            print 'tfile.InheritsFrom("TFile") is False'
            return []
    except:
        print 'EXCEPTION'
        return []
        
    tree = tfile.Get("limit")
    
    try:
        if tree.InheritsFrom("TTree") is False: 
            print 'limit.InheritsFrom("TTree") is False'
            tfile.cd()
            tfile.Close()
            return []
    except:
        print 'EXCEPTION'
        tfile.cd()
        tfile.Close()
        return []

    limits = []
    for quantile in tree:
        limits.append(tree.limit)

    return limits


def massIterable(massList):
    if len(massList.split(','))==1:
        massIterableList = [massList]
    else:
        massIterableList = list(eval(massList))
    return massIterableList

xsections = {'50': 1.574e-02*0.8,
            '100': 1.526e-02*0.8,
            '125': 1.486e-02*0.8,
            '200': 1.359e-02*0.8,
            '300': 1.251e-02*0.8,
            '350': 1.275e-02*0.8,
            '400': 1.144e-02*0.8,
            '500': 7.274e-03*0.8
            }

# PLOT upper limits
def plotUpperLimits(options,args):
    # see CMS plot guidelines: https://ghm.web.cern.ch/ghm/plots/
    all_masses = [50, 100, 125, 200, 300, 350, 400, 500]
    masses = []
    jet_type = options.box
    cut = options.cuts.split(',')[0]
    file_names = {}
    limits = {}
    for mass in all_masses:
        file_name = options.idir + "/%s/%s/DMSbb%s/higgsCombineDMSbb_%s_lumi-%.1f_%s.Asymptotic.mH120.root"%(jet_type,cut,str(mass),str(mass),options.lumi,jet_type)
        print file_name
        if glob.glob(file_name):
            print "Opened File ", file_name
            file_names[str(mass)] = file_name
            limits[str(mass)] = getLimits(file_name)
            print len( limits[str(mass)])
            if len( limits[str(mass)])>0:
                masses.append(mass)
            
            
    N = len(masses)
    print " No of mass points : ", N
    yellow = rt.TGraph(2*N)    # yellow band
    green = rt.TGraph(2*N)     # green band
    median = rt.TGraph(N)      # median line
    obs = rt.TGraph(N)       # observed
    if options.xsec:
        theory_xsec = rt.TGraph(N)       # theory cross section

    up2s = [ ]
    i = -1
    for mass in masses:
        i += 1
        limit = limits[str(mass)]
        up2s.append(limit[4])
        if options.xsec:
            fac = xsections[str(mass)]
        else:
            fac = 1
        yellow.SetPoint(    i,    mass, limit[4] * fac ) # + 2 sigma
        green.SetPoint(     i,    mass, limit[3] * fac ) # + 1 sigma
        median.SetPoint(    i,    mass, limit[2] * fac ) # median
        green.SetPoint(  2*N-1-i, mass, limit[1] * fac ) # - 1 sigma
        yellow.SetPoint( 2*N-1-i, mass, limit[0] * fac ) # - 2 sigma
        obs.SetPoint(       i,    mass, limit[5] * fac) # observed
        if options.xsec:
            theory_xsec.SetPoint(       i,    mass, xsections[str(mass)]) # theory x-section

    W = 800
    H  = 600
    T = 0.08*H
    B = 0.12*H
    L = 0.12*W#*scaleleftmargin
    R = 0.04*W#*scalerightmargin
    c = rt.TCanvas("c","c",100,100,W,H)
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
    #frame.GetYaxis().SetTitle("95% upper limit on #sigma #times BR / (#sigma #times BR)_{SM}")
    #frame.GetXaxis().SetTitle("background systematic uncertainty [%]")
    if options.xsec: 
        frame.SetMinimum(0.001)
        frame.SetMaximum(100)
    else:
        frame.SetMinimum(0)
        frame.SetMaximum(max(up2s)*1.05)
    
    h_limit = rt.TMultiGraph()
    h_limit.Add(yellow)
    h_limit.Add(green)
    h_limit.Add(median)
    #h_limit.Add(obs)
    #h_limit.Add(theory_xsec)

    h_limit.Draw('a3')
    h_limit.GetXaxis().SetLimits(options.massMin,options.massMax)
    h_limit.SetMinimum(options.xsecMin)
    h_limit.SetMaximum(options.xsecMax)
    h_limit.GetXaxis().SetTitle('Resonance mass [GeV]')
    h_limit.GetYaxis().SetTitle("#sigma [pb]")
    h_limit.GetYaxis().SetTitleOffset(0.9)
    #h_limit.Draw('F')
    
    yellow.SetFillColor(rt.kOrange)
    yellow.SetLineColor(rt.kBlack)
    yellow.SetFillStyle(1001)
    yellow.SetLineWidth(2)
    yellow.SetLineStyle(2)
    yellow.Draw('Fsame')
    
    green.SetFillColor(rt.kGreen+1)
    green.SetLineColor(rt.kBlack)
    green.SetLineWidth(2)
    green.SetLineStyle(2)
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
        theory_xsec.SetLineColor(rt.kBlue+2)
        theory_xsec.SetLineWidth(2)
        theory_xsec.Draw('Lsame')

    CMS_lumi.lumi_13TeV = "%.1f fb^{-1}"%options.lumi
    CMS_lumi.CMS_lumi(c,4,11)

    #rt.gPad.SetTicks(1,1)
    #frame.Draw('sameaxis')

    x1 = 0.65
    x2 = x1 + 0.24
    if options.xsec: 
        y1 = 0.72
    else: 
        y1 = 0.62
    y2 = y1 + 0.18
    legend = rt.TLegend(x1,y1,x2,y2)
    legend.SetFillStyle(0)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.041)
    legend.SetTextFont(42)
    legend.AddEntry(obs, "Observed",'lp')
    #legend.AddEntry(median, "Asymptotic CL_{s} expected",'L')
    legend.AddEntry(green, "Expeted #pm 1 s.d.",'lf')
    legend.AddEntry(yellow,"Expected #pm 2 s.d.",'lf')
    if options.xsec:
        legend.AddEntry(theory_xsec,"#Phi(b#bar{b})",'l')
    legend.Draw()

    print " "
    if options.xsec: 
        c.SetLogy()
        c.SaveAs("Limit_" + jet_type + "_" + cut+ "_xsec.pdf") 
        c.SaveAs("Limit_" + jet_type + "_" + cut+ "_xsec.C") 
    else: 
        c.SaveAs("Limit_" + jet_type + "_" + cut+ ".pdf")
        c.SaveAs("Limit_" + jet_type + "_" + cut+ ".C")
    c.Close()

# MAIN
def main(options,args):
    plotUpperLimits(options,args)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--model',dest="model", default="DMSbb",type="string", help="signal model name")
    parser.add_option('--mass',dest="mass", default='750',type="string", help="mass of resonance")
    parser.add_option('-b','--box',dest="box", default="AK8",type="string", help="box name")
    parser.add_option("--lumi", dest="lumi", default=35.9, type="float", help="luminosity", metavar="lumi")
    parser.add_option('-c', '--cuts', dest='cuts', default='p9', type='string', help='double b-tag cut value')
    parser.add_option('-x','--xsec', dest='xsec', action='store_true',default=False, help='cross_section',metavar='xsec')
    parser.add_option('-i', '--idir', dest='idir', default='./', help='input directory',metavar='idir')
    parser.add_option('--massMin',dest="massMin", default=50.,type="float", help="minimum mass")
    parser.add_option('--massMax',dest="massMax", default=500.,type="float", help="maximum mass")
    parser.add_option('--xsecMin',dest="xsecMin", default=1e-3,type="float", help="minimum xsec")
    parser.add_option('--xsecMax',dest="xsecMax", default=1e4,type="float", help="maximum xsec")

    (options,args) = parser.parse_args()   
    main(options,args) 
