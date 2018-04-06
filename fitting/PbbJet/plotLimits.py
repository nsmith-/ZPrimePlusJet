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

sample_xsec = {} # cross section used to normalize sample (in combine)
theory_xsec = {} # real theory cross section to compare (no BR)
br = {} # branching ratio to bb
legend_entry = {}
legend_entry['DMSbb'] = 'gg#Phi, g_{q\Phi}=1, H_{T}>400 GeV'
legend_entry['DMPSbb'] = 'ggA, g_{qA}=1, H_{T}>400 GeV'
legend_entry['Zpqq'] = "Z', g_{q}=1, H_{T}>500 GeV"

sample_xsec['DMSbb'] = rt.TGraph(8)
sample_xsec['DMSbb'].SetPoint(0,  50, 0.8 * 1.574e-02 * 100.)
sample_xsec['DMSbb'].SetPoint(1, 100, 0.8 * 1.526e-02 * 100.)
sample_xsec['DMSbb'].SetPoint(2, 125, 0.8 * 1.486e-02 * 100.)
sample_xsec['DMSbb'].SetPoint(3, 200, 0.8 * 1.359e-02 * 100.)
sample_xsec['DMSbb'].SetPoint(4, 300, 0.8 * 1.251e-02 * 100.)
sample_xsec['DMSbb'].SetPoint(5, 350, 0.8 * 1.275e-02 * 100.)
sample_xsec['DMSbb'].SetPoint(6, 400, 0.8 * 1.144e-02 * 100.)
sample_xsec['DMSbb'].SetPoint(7, 500, 0.8 * 7.274e-03 * 100.)

theory_xsec['DMSbb'] = rt.TGraph(8)
theory_xsec['DMSbb'].SetPoint(0,  50, 1.574e-02)
theory_xsec['DMSbb'].SetPoint(1, 100, 1.526e-02)
theory_xsec['DMSbb'].SetPoint(2, 125, 1.486e-02)
theory_xsec['DMSbb'].SetPoint(3, 200, 1.359e-02)
theory_xsec['DMSbb'].SetPoint(4, 300, 1.251e-02)
theory_xsec['DMSbb'].SetPoint(5, 350, 1.275e-02)
theory_xsec['DMSbb'].SetPoint(6, 400, 1.144e-02)
theory_xsec['DMSbb'].SetPoint(7, 500, 7.274e-03)

br_list = [[50, 0.85644], [55, 0.856044], [60, 0.855345], [65, 0.854398], [70, 
  0.853242], [75, 0.851899], [80, 0.850389], [85, 0.848721], [90, 
  0.846903], [95, 0.844943], [100, 0.842843], [105, 0.840606], [110, 
  0.838234], [115, 0.835729], [120, 0.833091], [125, 0.830321], [130, 
  0.827417], [135, 0.82438], [140, 0.821209], [145, 0.817903], [150, 
  0.81446], [155, 0.81088], [160, 0.80716], [165, 0.8033], [170, 
  0.799296], [175, 0.795148], [180, 0.790852], [185, 0.786407], [190, 
  0.781809], [195, 0.777055], [200, 0.772143], [205, 0.767069], [210, 
  0.761829], [215, 0.75642], [220, 0.750836], [225, 0.745074], [230, 
  0.739128], [235, 0.732993], [240, 0.726662], [245, 0.72013], [250, 
  0.713388], [255, 0.706428], [260, 0.699242], [265, 0.69182], [270, 
  0.684149], [275, 0.676218], [280, 0.668011], [285, 0.659512], [290, 
  0.650702], [295, 0.641556], [300, 0.632049], [305, 0.622146], [310, 
  0.611807], [315, 0.60098], [320, 0.589596], [325, 0.577565], [330, 
  0.564752], [335, 0.550952], [340, 0.53579], [345, 0.518319], [350, 
  0.141923], [355, 0.049768], [360, 0.0271303], [365, 
  0.0178448], [370, 0.0130041], [375, 0.0101058], [380, 
  0.0082066], [385, 0.0068805], [390, 0.00590992], [395, 
  0.00517327], [400, 0.00459782], [405, 0.0041376], [410, 
  0.00376232], [415, 0.00345123], [420, 0.00318974], [425, 
  0.00296725], [430, 0.00277595], [435, 0.00260994], [440, 
  0.00246468], [445, 0.00233664], [450, 0.00222305], [455, 
  0.00212167], [460, 0.00203071], [465, 0.00194868], [470, 
  0.00187439], [475, 0.00180682], [480, 0.00174514], [485, 
  0.00168863], [490, 0.0016367], [495, 0.00158882], [500, 0.00154457]]

br['DMSbb'] = rt.TGraph(len(br_list))
for i, br_m_val in enumerate(br_list):
    br['DMSbb'].SetPoint(i,  br_m_val[0], br_m_val[1])

sample_xsec['DMPSbb'] = rt.TGraph(8)
sample_xsec['DMPSbb'].SetPoint(0,  50, 0.8 * 3.587e-02 * 100.)
sample_xsec['DMPSbb'].SetPoint(1, 100, 0.8 * 3.379e-02 * 100.)
sample_xsec['DMPSbb'].SetPoint(2, 125, 0.8 * 3.374e-02 * 100.)
sample_xsec['DMPSbb'].SetPoint(3, 200, 0.8 * 3.306e-02  * 100.)
sample_xsec['DMPSbb'].SetPoint(4, 300, 0.8 * 3.770e-02 * 100.)
sample_xsec['DMPSbb'].SetPoint(5, 350, 0.8 * 4.262e-02  * 100.)
sample_xsec['DMPSbb'].SetPoint(6, 400, 0.8 * 2.499e-02 * 100.)
sample_xsec['DMPSbb'].SetPoint(7, 500, 0.8 * 1.264e-02 * 100.)

theory_xsec['DMPSbb'] = rt.TGraph(8)
theory_xsec['DMPSbb'].SetPoint(0,  50, 3.587e-02)
theory_xsec['DMPSbb'].SetPoint(1, 100, 3.379e-02)
theory_xsec['DMPSbb'].SetPoint(2, 125, 3.374e-02)
theory_xsec['DMPSbb'].SetPoint(3, 200, 3.306e-02)
theory_xsec['DMPSbb'].SetPoint(4, 300, 3.770e-02)
theory_xsec['DMPSbb'].SetPoint(5, 350, 4.262e-02)
theory_xsec['DMPSbb'].SetPoint(6, 400, 2.499e-02)
theory_xsec['DMPSbb'].SetPoint(7, 500, 1.264e-02)

br_list = [[50, 0.852511], [55, 0.850153], [60, 0.847484], [65, 0.844523], [70, 
  0.841283], [75, 0.837772], [80, 0.833996], [85, 0.82996], [90, 
  0.825665], [95, 0.821115], [100, 0.816311], [105, 0.811255], [110, 
  0.805947], [115, 0.80039], [120, 0.794582], [125, 0.788526], [130, 
  0.782221], [135, 0.775668], [140, 0.768867], [145, 0.761818], [150, 
  0.754521], [155, 0.746976], [160, 0.739184], [165, 0.731143], [170, 
  0.722854], [175, 0.714316], [180, 0.705528], [185, 0.69649], [190, 
  0.687201], [195, 0.677659], [200, 0.667863], [205, 0.657812], [210, 
  0.647503], [215, 0.636934], [220, 0.626103], [225, 0.615006], [230, 
  0.603639], [235, 0.591998], [240, 0.580078], [245, 0.567872], [250, 
  0.555373], [255, 0.542574], [260, 0.529463], [265, 0.516029], [270, 
  0.502256], [275, 0.488129], [280, 0.473626], [285, 0.458721], [290, 
  0.443382], [295, 0.42757], [300, 0.411232], [305, 0.394302], [310, 
  0.376692], [315, 0.358277], [320, 0.338882], [325, 0.318235], [330, 
  0.295893], [335, 0.271021], [340, 0.241659], [345, 0.199353], [350, 
  0.00397345], [355, 0.00261999], [360, 0.00211189], [365, 
  0.00182771], [370, 0.00164097], [375, 0.00150681], [380, 
  0.00140477], [385, 0.00132401], [390, 0.0012582], [395, 
  0.00120335], [400, 0.00115681], [405, 0.00111675], [410, 
  0.00108185], [415, 0.00105113], [420, 0.00102385], [425, 
  0.000999458], [430, 0.000977495], [435, 0.000957607], [440, 
  0.000939506], [445, 0.000922955], [450, 0.00090776], [455, 
  0.000893757], [460, 0.000880809], [465, 0.0008688], [470, 
  0.000857629], [475, 0.000847211], [480, 0.000837473], [485, 
  0.000828348], [490, 0.000819782], [495, 0.000811723], [500, 
  0.000804129]]

br['DMPSbb'] = rt.TGraph(len(br_list))
for i, br_m_val in enumerate(br_list):
    br['DMPSbb'].SetPoint(i,  br_m_val[0], br_m_val[1])

theory_xsec['Zpqq'] = rt.TGraph(6)
theory_xsec['Zpqq'].SetPoint(0,  50, 2.2*83.7) #sigma(HT>400) = 2.2 * sigma(HT>500)
theory_xsec['Zpqq'].SetPoint(1, 100, 2.2*46.3)
theory_xsec['Zpqq'].SetPoint(2, 150, 2.2*31.32)
theory_xsec['Zpqq'].SetPoint(3, 200, 2.2*23.17)
theory_xsec['Zpqq'].SetPoint(4, 250, 2.2*18.5)
theory_xsec['Zpqq'].SetPoint(5, 300, 2.2*16.03)

br['Zpqq'] = rt.TGraph(6)
br['Zpqq'].SetPoint(0,  50, 0.2)
br['Zpqq'].SetPoint(1, 100, 0.2)
br['Zpqq'].SetPoint(2, 150, 0.2)
br['Zpqq'].SetPoint(3, 200, 0.2)
br['Zpqq'].SetPoint(4, 250, 0.2)
br['Zpqq'].SetPoint(5, 300, 0.2)

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
        file_name = options.idir + "/%s/%s/%s%s/higgsCombine%s_%s_lumi-%.1f_%s.Asymptotic.mH120.root"%(jet_type[str(mass)],cut[str(mass)],options.model,str(mass),options.model,str(mass),options.lumi,jet_type[str(mass)])
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
            fac = sample_xsec[options.model].Eval(mass,0,'S')
            if options.gqZp: 
                theory = theory_xsec['Zpqq'].Eval(mass,0,'S') * br['Zpqq'].Eval(mass,0,'S')
            else: 
                theory = theory_xsec[options.model].Eval(mass,0,'S') * br[options.model].Eval(mass,0,'S')
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

    theory_xsec[options.model].SetMarkerStyle(20)
    theory_xsec[options.model].SetLineColor(rt.kBlue+2)
    theory_xsec[options.model].SetLineWidth(2)
    #theory_xsec[options.model].SetLineStyle(2)
    if options.xsec:
        theory_xsec[options.model].Draw('Csame')

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
        legend.AddEntry(theory_xsec[options.model],legend_entry[options.model],'l')
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
        else:
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
