from optparse import OptionParser
import ROOT as rt
import CMS_lumi, tdrstyle
import subprocess # to execute shell command
rt.gROOT.SetBatch(True)
import glob
import math

# CMS style
CMS_lumi.cmsText = "CMS"
CMS_lumi.extraText = "Preliminary"
CMS_lumi.cmsTextSize = 0.65
CMS_lumi.outOfFrame = True
tdrstyle.setTDRStyle()

massSwitch = 160

from runCombine import massIterable

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


xsections = rt.TGraph(8)
xsections.SetPoint(0,  50, 0.8 * 1.574e-02)
xsections.SetPoint(1, 100, 0.8 * 1.526e-02)
xsections.SetPoint(2, 125, 0.8 * 1.486e-02)
xsections.SetPoint(3, 200, 0.8 * 1.359e-02)
xsections.SetPoint(4, 300, 0.8 * 1.251e-02)
xsections.SetPoint(5, 350, 0.8 * 1.275e-02)
xsections.SetPoint(6, 400, 0.8 * 1.144e-02)
xsections.SetPoint(7, 500, 0.8 * 7.274e-03)

theory_xsec = rt.TGraph(8)
theory_xsec.SetPoint(0,  50, 1.574e-02)
theory_xsec.SetPoint(1, 100, 1.526e-02)
theory_xsec.SetPoint(2, 125, 1.486e-02)
theory_xsec.SetPoint(3, 200, 1.359e-02)
theory_xsec.SetPoint(4, 300, 1.251e-02)
theory_xsec.SetPoint(5, 350, 1.275e-02)
theory_xsec.SetPoint(6, 400, 1.144e-02)
theory_xsec.SetPoint(7, 500, 7.274e-03)

br = rt.TGraph(8)
br.SetPoint(0,  50, 0.904965)
br.SetPoint(1, 100, 0.888511)
br.SetPoint(2, 125, 0.874462)
br.SetPoint(3, 200, 0.810039)
br.SetPoint(4, 300, 0.657186)
br.SetPoint(5, 350, 0.143152)
br.SetPoint(6, 400, 0.0045991)
br.SetPoint(7, 500, 0.00154471)

theory_xsec_Zp = rt.TGraph(6)
theory_xsec_Zp.SetPoint(0,  50, 2.2*83.7) #sigma(HT>400) = 2.2 * sigma(HT>500)
theory_xsec_Zp.SetPoint(1, 100, 2.2*46.3)
theory_xsec_Zp.SetPoint(2, 150, 2.2*31.32)
theory_xsec_Zp.SetPoint(3, 200, 2.2*23.17)
theory_xsec_Zp.SetPoint(4, 250, 2.2*18.5)
theory_xsec_Zp.SetPoint(5, 300, 2.2*16.03)

br_Zp = rt.TGraph(6)
br_Zp.SetPoint(0,  50, 0.2)
br_Zp.SetPoint(1, 100, 0.2)
br_Zp.SetPoint(2, 150, 0.2)
br_Zp.SetPoint(3, 200, 0.2)
br_Zp.SetPoint(4, 250, 0.2)
br_Zp.SetPoint(5, 300, 0.2)

tenpercentwidth = {'50': 52.3443,
            '100': 51.0427,
            '125': 50.5416,
            '200': 48.5446,
            '300': 43.6933,
            '350': 20.3893,
            '400': 3.65424,
            '500': 2.11755
            }
    
# PLOT upper limits
def plotUpperLimits(options,args):
    # see CMS plot guidelines: https://ghm.web.cern.ch/ghm/plots/
    all_masses = massIterable(options.masses)
    masses = []
    jet_type = {}
    cut = {}
    if len(options.box.split('_')) > 1:
        for mass in all_masses:
            if mass < massSwitch:
                jet_type[str(mass)] = options.box.split('_')[0]
                cut[str(mass)] = options.cuts.split('_')[0]
            else:
                jet_type[str(mass)] = options.box.split('_')[1]
                cut[str(mass)] = options.cuts.split('_')[1]
    else:
        for mass in all_masses:
            jet_type[str(mass)] = options.box
            cut[str(mass)] = options.cuts

    file_names = {}
    limits = {}
    print cut
    print jet_type
    for mass in all_masses:
        file_name = options.idir + "/%s/%s/DMSbb%s/higgsCombineDMSbb_%s_lumi-%.1f_%s.Asymptotic.mH120.root"%(jet_type[str(mass)],cut[str(mass)],str(mass),str(mass),options.lumi,jet_type[str(mass)])
        print file_name
        if glob.glob(file_name):
            print "Opened File ", file_name
            file_names[str(mass)] = file_name
            limits[str(mass)] = getLimits(file_name)
            print len( limits[str(mass)])
            if len( limits[str(mass)])>=5:
                masses.append(mass)
            
            
    N = len(masses)
    print " No of mass points : ", N
    yellow = rt.TGraph(2*N)    # yellow band
    green = rt.TGraph(2*N)     # green band
    median = rt.TGraph(N)      # median line
    obs = rt.TGraph(N)       # observed

    up2s = [ ]
    i = -1
    for mass in masses:
        i += 1
        limit = limits[str(mass)]
        up2s.append(limit[4])
        if options.xsec or options.gq or options.gqZp:
            fac = xsections.Eval(mass,0,'S')
            theory = theory_xsec.Eval(mass,0,'S') * br.Eval(mass,0,'S')
            if options.gqZp:
                theory = theory_xsec_Zp.Eval(mass,0,'S') * br_Zp.Eval(mass,0,'S')
        else:
            fac = 1
        if options.gq or options.gqZp:
            yellow.SetPoint(    i,    mass, math.sqrt(limit[4]*fac/theory)) # + 2 sigma 
            green.SetPoint(     i,    mass, math.sqrt(limit[3]*fac/theory)) # + 1 sigma
            median.SetPoint(    i,    mass, math.sqrt(limit[2]*fac/theory)) # median
            green.SetPoint(  2*N-1-i, mass, math.sqrt(limit[1]*fac/theory)) # - 1 sigma
            yellow.SetPoint( 2*N-1-i, mass, math.sqrt(limit[0]*fac/theory)) # - 2 sigma
            if len(limit)>5:
                obs.SetPoint(       i,    mass, math.sqrt(limit[5]*fac/theory)) # observed
        else:
            yellow.SetPoint(    i,    mass, limit[4] * fac ) # + 2 sigma
            green.SetPoint(     i,    mass, limit[3] * fac ) # + 1 sigma
            median.SetPoint(    i,    mass, limit[2] * fac ) # median
            green.SetPoint(  2*N-1-i, mass, limit[1] * fac ) # - 1 sigma
            yellow.SetPoint( 2*N-1-i, mass, limit[0] * fac ) # - 2 sigma
            if len(limit)>5:
                obs.SetPoint(       i,    mass, limit[5] * fac) # observed
        print mass,  limit[2]*fac
            

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
    #c.SetGrid()
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
    if options.gq:
        h_limit.GetYaxis().SetTitle("g_{q#Phi}")
    elif options.gqZp:
        h_limit.GetYaxis().SetTitle("g'_{q}")
        h_limit.GetYaxis().SetMoreLogLabels()
        h_limit.GetYaxis().SetNoExponent()
        h_limit.GetXaxis().SetMoreLogLabels()
        h_limit.GetXaxis().SetNoExponent()
    elif options.xsec:
        h_limit.GetYaxis().SetTitle("#sigma #times B [pb]")
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
    if len(limit)>5 and options.observed:
        obs.Draw('PLsame')

    theory_xsec.SetMarkerStyle(20)
    theory_xsec.SetLineColor(rt.kBlue+2)
    theory_xsec.SetLineWidth(2)
    #theory_xsec.SetLineStyle(2)
    if options.xsec:
        theory_xsec.Draw('Csame')

    CMS_lumi.lumi_13TeV = "%.1f fb^{-1}"%options.lumi
    CMS_lumi.CMS_lumi(c,4,11)

    #rt.gPad.SetTicks(1,1)
    #frame.Draw('sameaxis')

    if options.gq or options.gqZp:
        x1 = 0.67
    else:
        x1 = 0.6
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
    if len(limit)>5 and options.observed:
        legend.AddEntry(obs, "Observed",'lp')
    #legend.AddEntry(median, "Asymptotic CL_{s} expected",'L')
    legend.AddEntry(green, "Expected #pm 1 s.d.",'lf')
    legend.AddEntry(yellow,"Expected #pm 2 s.d.",'lf')
    if options.xsec:
        legend.AddEntry(theory_xsec,"gg#Phi, g_{q\Phi}=1, H_{T}>400 GeV",'l')
    legend.Draw()

    if len(options.box.split('_')) > 1:

        if options.xsec:
            dxleg = 30
            dyleg = 1
            yleg1 = 0.1
            yleg2 = 5
            
        elif options.gq:
            dxleg = 30
            dyleg = 1
            yleg1 = 2
            yleg2 = 10
            
        elif options.gqZp:
            dxleg = 40
            dyleg = 0.05
            yleg1 = 0.08
            yleg2 = 0.45
                        

        line1 = rt.TLine(massSwitch,yleg1,massSwitch,yleg2)
        line1.SetLineStyle(2)
        line1.SetLineWidth(2)
        line1.SetLineColor(rt.kGray+1)
        line1.Draw()
        lab = rt.TLatex()
        lab.SetTextSize(0.035)
        lab.SetTextFont(42)
        lab.SetTextColor(rt.kGray+1)
        lab.SetTextAlign(23)
        lab.DrawLatex(massSwitch-dxleg,yleg2-dyleg,"#leftarrow #splitline{anti-k_{T}}{R=0.8}")
        lab.DrawLatex(massSwitch+dxleg,yleg2-dyleg,"#splitline{CA}{R=1.5} #rightarrow")
        lab.Draw()

    print " "
    if options.gq: 
        c.SaveAs(options.odir+"/Limit_" + options.box + "_" + options.cuts + "_gq.pdf") 
        c.SaveAs(options.odir+"/Limit_" + options.box + "_" + options.cuts + "_gq.C") 
    elif options.gqZp: 
        c.SetLogx()
        c.SetLogy()
        c.SaveAs(options.odir+"/Limit_" + options.box + "_" + options.cuts + "_gqZp.pdf") 
        c.SaveAs(options.odir+"/Limit_" + options.box + "_" + options.cuts + "_gqZp.C") 
    elif options.xsec: 
        c.SetLogy()
        c.SaveAs(options.odir+"/Limit_" + options.box + "_" + options.cuts + "_xsec.pdf") 
        c.SaveAs(options.odir+"/Limit_" + options.box + "_" + options.cuts + "_xsec.C") 
    else: 
        c.SaveAs(options.odir+"/Limit_" + options.box + "_" + options.cuts + ".pdf")
        c.SaveAs(options.odir+"/Limit_" + options.box + "_" + options.cuts + ".C")
    c.Close()

# MAIN
def main(options,args):
    plotUpperLimits(options,args)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--model',dest="model", default="DMSbb",type="string", help="signal model name")
    parser.add_option('--masses',dest='masses', default='50,100,125,200,300,350,400,500',type='string',help='masses of resonance')
    parser.add_option('-b','--box',dest="box", default="AK8",type="string", help="box name")
    parser.add_option("--lumi", dest="lumi", default=35.9, type="float", help="luminosity", metavar="lumi")
    parser.add_option('-c', '--cuts', dest='cuts', default='p9', type='string', help='double b-tag cut value')
    parser.add_option('-x','--xsec', dest='xsec', action='store_true',default=False, help='cross_section',metavar='xsec')
    parser.add_option('--observed', dest='observed', action='store_true',default=False, help='show observed',metavar='observed')
    parser.add_option('-g','--gq', dest='gq', action='store_true',default=False, help='gq',metavar='gq')
    parser.add_option('--gqZp', dest='gqZp', action='store_true',default=False, help='gqZp',metavar='gqZp')
    parser.add_option('-i', '--idir', dest='idir', default='./', help='input directory',metavar='idir')
    parser.add_option('-o', '--odir', dest='odir', default='./', help='input directory',metavar='odir')
    parser.add_option('--massMin',dest="massMin", default=50.,type="float", help="minimum mass")
    parser.add_option('--massMax',dest="massMax", default=500.,type="float", help="maximum mass")
    parser.add_option('--xsecMin',dest="xsecMin", default=1e-3,type="float", help="minimum xsec")
    parser.add_option('--xsecMax',dest="xsecMax", default=1e4,type="float", help="maximum xsec")

    (options,args) = parser.parse_args()   
    main(options,args) 
