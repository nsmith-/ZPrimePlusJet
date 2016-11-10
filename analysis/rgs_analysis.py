#!/usr/bin/env python
# ---------------------------------------------------------------------
#  File:        analysis.py
#  Description: Analyze the results of RGS and find the best cuts.
#               Definitions:
#                 1. A cut is a threshold on a single variable.
#                    e.g., x > xcut
#                 2. A cut-point is the AND of a sequence of cuts. This
#                    can be visualized as a point in the space of cuts.
#                 3. A box cut is a two-sided threshold.
#                    e.g., (x > xlow) and (x < xhigh)
#                 4. A ladder cut is the OR of cut-pooints.
# ---------------------------------------------------------------------
#  Created:     10-Jan-2015 Harrison B. Prosper and Sezen Sekmen
# ---------------------------------------------------------------------
import os, sys, re
from string import *
from rgsutil import *
from time import sleep
from ROOT import *
# ---------------------------------------------------------------------

yvar = 'nAK4PuppijetsTdR08'
xvar = 'pfmet'
lumi = 1.0
def plotData():

    msize = 0.15 # marker size

    varDict = {'nAK4PuppijetsdR08': ['AK4 n_{jet}, #Delta R>0.8', 12, 0, 12],
               'nAK4Puppijets': ['AK4 n_{jet}', 12, 0, 12],
               'nAK4PuppijetsLdR08': ['AK4 n_{L b-tag}, #Delta R>0.8',6, 0, 6],
               'nAK4PuppijetsMdR08':  ['AK4 n_{M b-tag}, #Delta R>0.8', 6, 0, 6],
               'nAK4PuppijetsTdR08':  ['AK4 n_{T b-tag}, #Delta R>0.8', 6, 0, 6],    
               'nAK4PuppijetsbtagL':  ['AK4 n_{L b-tag}', 6, 0, 6],                 
               'nAK4PuppijetsbtagM':  ['AK4 n_{M b-tag}', 6, 0, 6],                     
               'nAK4PuppijetsbtagT':  ['AK4 n_{T b-tag}', 6, 0, 6],                     
               'AK8CHSjet0_doublecsv':  ['AK8 double b-tag', 50, -1, 1],          
               'AK8Puppijet0_tau32':  ['AK8 #tau_{32}', 50, 0, 1.5],        
               'AK8Puppijet0_tau21':  ['AK8 #tau_{21}', 50, 0, 1.5],   
               'pfmet':  ['PF E_{T}^{miss}', 50, 0, 1000],
        }


    xlabel = varDict[xvar][0]
    xbins =   varDict[xvar][1]
    xmin  =  varDict[xvar][2]
    xmax  = varDict[xvar][3]

    ylabel = varDict[yvar][0]
    ybins =    varDict[yvar][1]
    ymin  =  varDict[yvar][2]
    ymax  =  varDict[yvar][3]
    
    cmass = TCanvas("fig_%s_%s"%(xvar,yvar), "t#bar{t}+jets/ggH(b#bar{b})",
                    10, 10, 500, 500)
    cmass.SetTopMargin(0.1)
    cmass.SetLeftMargin(0.15)
    
    # -- background
    hb = mkhist2("hb",
                 xlabel,
                 ylabel,
                 xbins, xmin, xmax,
                 ybins, ymin, ymax,
                 color=kBlue-10)
    hb.SetFillColor(kBlue-10)
    hb.SetLineColor(kBlue-10)
    hb.Sumw2()
    hb.SetMarkerSize(msize)
    hb.GetYaxis().SetTitleOffset(1.20)
    
    bntuple = Ntuple('TTbar_madgraphMLM_1000pb_weighted.root', 'otree')
    btotal  = 0.0
    total   = 0
    for ii, event in enumerate(bntuple):
        btotal += event.scale1fb
        total  += 1
        hb.Fill(getattr(event,xvar), getattr(event,yvar), event.scale1fb)
        if total % 100 == 0:
            cmass.cd()
            hb.Draw('box')
            cmass.Update()
    
    # -- signal
    hs = mkhist2("hs",
                 xlabel,
                 ylabel,
                 xbins, xmin, xmax,
                 ybins, ymin, ymax,
                 color=kRed+1)
    hs.SetFillColor(kRed+1)
    hs.SetLineColor(kRed+1)
    hs.SetFillStyle(3001)
    hs.Sumw2()
    hs.SetMarkerSize(msize)
    hs.GetYaxis().SetTitleOffset(1.20)
    
    sntuple = Ntuple('GluGluHToBB_M125_13TeV_powheg_pythia8_1000pb_weighted.root', 'otree')
    stotal  = 0.0
    total   = 0
    for event in sntuple:
        stotal += event.scale1fb
        total  += 1
        hs.Fill(getattr(event,xvar), getattr(event,yvar), event.scale1fb)
        if total % 100 == 0:
            cmass.cd()
            hs.Draw('box')
            cmass.Update()

    cmass.cd()
    hs.Scale(10.) #multiply signal x10
    hb.Draw('boxl')
    hs.Draw('boxl same')    
    cmass.Update()
    return (cmass, hs, hb)
# ---------------------------------------------------------------------
def main():
    print "="*80
    print "\t=== Example 1 - Obtain Best One-Sided Cuts ==="
    print "="*80

    resultsfilename = "rgs_train2d.root"
    treename = "RGS"
    print "\n\topen RGS file: %s"  % resultsfilename
    ntuple = Ntuple(resultsfilename, treename)
    
    variables = ntuple.variables()
    for name, count in variables:
        print "\t\t%-30s\t%5d" % (name, count)        
    print "\tnumber of cut-points: ", ntuple.size()

    # -------------------------------------------------------------
    # Plot results of RGS, that is, the fraction of events that
    # pass a given cut-point.
    #  1. Loop over cut points and compute a significance measure
    #     for each cut-point.
    #  2. Find cut-point with highest significance.
    # -------------------------------------------------------------
    # Set up a standard Root graphics style (see histutil.py in the
    # python directory).
    setStyle()

    cmass, hs, hb = plotData()

    
    # Create a 2-D histogram for ROC plot
    msize = 0.30  # marker size for points in ROC plot
    
    xbins =   50  # number of bins in x (background)
    xmin  =  0.0  # lower bound of x
    xmax  =  1.0  # upper bound of y

    ybins =   50
    ymin  =  0.0
    ymax  =  1.0

    color = kBlue+1
    hist  = mkhist2("hroc",
                    "#epsilon_{B}",
                    "#epsilon_{S}",
                    xbins, xmin, xmax,
                    ybins, ymin, ymax,
                    color=color)
    hist.SetMinimum(0)
    hist.SetMarkerSize(msize)


    # loop over all cut-points, compute a significance measure Z
    # for each cut-point, and find the cut-point with the highest
    # significance and the associated cuts.
    print "\tfilling ROC plot..."	
    bestZ = -1      # best Z value
    bestSoverB = -1 # best S/B value
    bestSoverSqrtB = -1 # best S/sqrt(B) value
    bestRow = -1    # row with best cut-point
    bestFraction_s = -1 # best S fraction
    bestFraction_b = -1 # best B fraction

    for row, cuts in enumerate(ntuple):
        fb = cuts.fraction_b  #  background fraction
        fs = cuts.fraction_s  #  signal fraction
        b  = cuts.count_b     #  background count
        s  = cuts.count_s     #  signal count
                
        #  Plot fs vs fb
        hist.Fill(fb, fs)
        	
        # Compute measure of significance
        #   Z  = sign(LR) * sqrt(2*|LR|)
        # where LR = log(Poisson(s+b|s+b)/Poisson(s+b|b))
        Z = 0.0
        if b > 1:
            Z = 2*((s+b)*log((s+b)/b)-s)
            absZ = abs(Z)
            if absZ != 0:
                Z = Z*sqrt(absZ)/absZ                    
        if Z > bestZ:
            bestZ = Z
            bestrow = row
            bestFraction_s = fs
            bestFraction_b = fb
            if b>0:
                bestSoverB = float(s)/float(b)
                bestSoverSqrtB = float(s)/sqrt(b)

    # -------------------------------------------------------------            
    # Write out best cut
    # -------------------------------------------------------------
    ntuple.read(bestrow)
    print "\nBest cuts"
    bestcuts = {}
    for name, count in variables:    
        if name[0:5] in ['count', 'fract', 'cutpo']: continue
        var = ntuple(name)
        bestcuts[name] = var
        print "\t%s" % name
        print "\t\t%10.2f" % var
    print
    
    print "Yields and relative efficiencies"
    for name, count in variables:        
        if not (name[0:5] in ['count', 'fract']): continue
        var = ntuple(name)
        print "\t%-30s %10.3f" % (name, var)
        if name[0:5] == "fract":
            print
    
    # -------------------------------------------------------------
    # Save plots
    # -------------------------------------------------------------
    print "\t== plot ROC ==="	
    croc = TCanvas("fig_%s_%s_%s_ROC" % (nameonly(resultsfilename),xvar,yvar),
                   "ROC", 520, 10, 500, 500)
    croc.SetTopMargin(0.1)
    croc.SetLeftMargin(0.15)
    croc.cd()
    hist.Draw()
    croc.Update()



    print "\t=== plot one-sided cuts ==="
    
    xbins= hs.GetNbinsX()
    xmin = hs.GetXaxis().GetBinLowEdge(1)
    xmax = hs.GetXaxis().GetBinUpEdge(xbins)

    ybins= hs.GetNbinsY()
    ymin = hs.GetYaxis().GetBinLowEdge(1)
    ymax = hs.GetYaxis().GetBinUpEdge(ybins)

    
    xcut = array('d')
    ycut = array('d')

    lessThanList = ['nAK4PuppijetsdR08','nAK4PuppijetsTdR08','nAK4PuppijetsMdR08','nAK4PuppijetsLdR08','AK8Puppijet0_tau21','pfmet','nAK4PuppijetsbtagT','nAK4Puppijets','nAK4PuppijetsbtagM','nAK4PuppijetsbtagL']
    greaterThanList = ['AK8Puppijet0_tau32','AK8CHSjet0_doublecsv']
    if xvar in lessThanList and yvar in lessThanList:
        xcut.append(bestcuts[xvar])
        xcut.append(bestcuts[xvar])
        xcut.append(xmin)

        ycut.append(ymin)
        ycut.append(bestcuts[yvar])
        ycut.append(bestcuts[yvar])
    elif xvar in lessThanList and yvar in greaterThanList:
        xcut.append(bestcuts[xvar])
        xcut.append(bestcuts[xvar])
        xcut.append(xmin)

        ycut.append(ymax)
        ycut.append(bestcuts[yvar])
        ycut.append(bestcuts[yvar])        
    elif xvar in greaterThanList and yvar in greaterThanList:
        xcut.append(bestcuts[xvar])
        xcut.append(bestcuts[xvar])
        xcut.append(xmax)

        ycut.append(ymax)
        ycut.append(bestcuts[yvar])
        ycut.append(bestcuts[yvar])        
    elif xvar in greaterThanList and yvar in lessThanList:
        xcut.append(bestcuts[xvar])
        xcut.append(bestcuts[xvar])
        xcut.append(xmax)

        ycut.append(ymin)
        ycut.append(bestcuts[yvar])
        ycut.append(bestcuts[yvar])
        
    hcut = TGraph(3, xcut, ycut)

    cmass.cd()
    hcut.Draw('same')

    
    leg = TLegend(0.6,0.75,0.85,0.9)
    leg.SetFillStyle(0)
    leg.SetBorderSize(0)
    leg.SetTextSize(0.035)
    leg.SetTextFont(42)
    leg.AddEntry(hb.GetName(),'t#bar{t}+jets','f')
    leg.AddEntry(hs.GetName(),'ggH(b#bar{b}) #times 10','f')
    leg.Draw()

    tag4 = TLatex(0.22,0.85,"#epsilon_{B}* = %.2f, #epsilon_{S}* = %.2f"%(bestFraction_b,bestFraction_s))
    tag5 = TLatex(0.22,0.80,"S/#sqrt{B} = %.2f"%(bestSoverSqrtB))
    tag4.SetTextSize(0.035); tag5.SetTextSize(0.035)
    tag4.SetNDC(); tag5.SetNDC()
    tag4.SetTextFont(42); tag5.SetTextFont(42)

    
    tag1 = TLatex(0.67,0.92,"%.0f fb^{-1} (13 TeV)"%lumi)
    tag1.SetNDC(); tag1.SetTextFont(42)
    tag1.SetTextSize(0.04)
    tag2 = TLatex(0.1,0.92,"CMS")
    tag2.SetNDC(); tag2.SetTextFont(62)
    tag3 = TLatex(0.2,0.92,"Simulation Preliminary")
    tag3.SetNDC(); tag3.SetTextFont(52)
    tag2.SetTextSize(0.05); tag3.SetTextSize(0.04); 
    
    for c in [cmass, croc]:
        c.cd()
        tag1.Draw(); tag2.Draw(); tag3.Draw(); tag4.Draw(); tag5.Draw()
        
    croc.SaveAs(".pdf")    
    croc.SaveAs(".C")    
    cmass.SaveAs('.pdf')
    cmass.SaveAs('.C')
    
    #sleep(5)
# ---------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "bye!"


