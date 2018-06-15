import ROOT as rt
from rhalphabet_builder_Phibb import BB_SF,BB_SF_ERR,V_SF,V_SF_ERR,GetSF
import array
import re
rt.gROOT.SetBatch()
jet_type = 'CA15'
sigName = 'DMSbb'
muonCR = False

#sigs = [sigName+str(m) for m in range(50,505,5)]
sigs = [sigName+str(m) for m in [50, 100, 125, 200, 300, 350, 400, 500]]
cut = 'p9'
numberOfMassBins = 80
numberOfPtBins = 6
if muonCR:
    numberOfPtBins = 1
if muonCR:
    tfile = rt.TFile.Open('templates_psbb_interp/hist_1DZbb_muonCR_' + jet_type + '_interpolations_merge_rebin.root')
elif jet_type=='AK8' and not muonCR:
    tfile = rt.TFile.Open('templates_psbb_interp/hist_1DZbb_pt_scalesmear_' + jet_type + '_interpolations_merge.root')
elif jet_type=='CA15' and not muonCR:
    tfile = rt.TFile.Open('templates_psbb_interp/hist_1DZbb_pt_scalesmear_' + jet_type + '_interpolations_merge_rebin.root')

histoDict, histoDictLoose = {}, {}
for proc in sigs:
    for box in ['pass','fail']:
        print 'getting histogram for process: %s_%s'%(proc,box)
        histoDict['%s_%s'%(proc,box)] = tfile.Get('%s_%s_%s'%(proc,cut,box))
        histoDictLoose['%s_%s'%(proc,box)] = tfile.Get('%s_%s_%s'%(proc,'p8',box))
        matchString = '_matched'
        histoDict['%s_%s%s'%(proc,box,matchString)] = tfile.Get('%s_%s_%s%s'%(proc,cut,box,matchString))
        histoDictLoose['%s_%s%s'%(proc,box,matchString)] = tfile.Get('%s_%s_%s%s'%(proc,'p8',box,matchString))
        for syst in ['JER','JES','Pu']:
            print 'getting histogram for process: %s_%s_%s_%sUp'%(proc,cut,box,syst)
            histoDict['%s_%s_%sUp'%(proc,box,syst)] = tfile.Get('%s_%s_%s_%sUp'%(proc,cut,box,syst))
            print 'getting histogram for process: %s_%s_%s_%sDown'%(proc,cut,box,syst)
            histoDict['%s_%s_%sDown'%(proc,box,syst)] = tfile.Get('%s_%s_%s_%sDown'%(proc,cut,box,syst))
rates = {}
mcstatErrs = {}
jesErrs = {}
jerErrs = {}
puErrs = {}
jesGraph = {}
jerGraph = {} 
mcstatGraph = {}
puGraph = {}
for box in ['pass','fail']:
    for i in range(1,numberOfPtBins+1):
        jesGraph[box, i] = rt.TGraph(len(sigs))
        jerGraph[box, i] = rt.TGraph(len(sigs))
        puGraph[box, i] = rt.TGraph(len(sigs))
        mcstatGraph[box, i] = rt.TGraph(len(sigs))
        jesGraph[box, i].SetName('jes_%s_%s_%s_cat%i'%(jet_type,sigName,box,i))
        jerGraph[box, i].SetName('jer_%s_%s_%s_cat%i'%(jet_type,sigName,box,i))
        puGraph[box, i].SetName('pu_%s_%s_%s_cat%i'%(jet_type,sigName,box,i))
        mcstatGraph[box, i].SetName('mcstat_%s_%s_%s_cat%i'%(jet_type,sigName,box,i))
re_sbb = re.compile("Sbb(?P<mass>\d+)")
for i_sig, proc in enumerate(sigs):
    re_match = re_sbb.search(proc)
    mass = int(re_match.group("mass"))
    for box in ['pass','fail']:
        for i in range(1,numberOfPtBins+1):
            if muonCR:
                histo = histoDict['%s_%s'%(proc,box)]
                error = array.array('d',[0.0])
                rate = histoDict['%s_%s'%(proc,box)].IntegralAndError(1,histo.GetNbinsX(),error)
            else:
                matchString = '_matched'
                if 'pass' in box:
                    histo = histoDictLoose['%s_%s%s'%(proc,box,matchString)]
                else:
                    histo = histoDict['%s_%s%s'%(proc,box,matchString)]
                error = array.array('d',[0.0])
                rate = histo.IntegralAndError(1,histo.GetNbinsX(),i,i,error)
            if rate>0:
                mcstatErrs['%s_%s'%(proc,box),i,1] = 1.0+(error[0]/rate)
            else:
                mcstatErrs['%s_%s'%(proc,box),i,1] = 1.0

            if not muonCR:
                rate = histoDict['%s_%s'%(proc,box)].Integral(1, numberOfMassBins, i, i)        
            if rate>0:
                if muonCR:
                    rateJESUp = histoDict['%s_%s_JESUp'%(proc,box)].Integral()
                    rateJESDown = histoDict['%s_%s_JESDown'%(proc,box)].Integral()
                    rateJERUp = histoDict['%s_%s_JERUp'%(proc,box)].Integral()
                    rateJERDown = histoDict['%s_%s_JERDown'%(proc,box)].Integral()
                    ratePuUp = histoDict['%s_%s_PuUp'%(proc,box)].Integral()
                    ratePuDown = histoDict['%s_%s_PuDown'%(proc,box)].Integral()
                else:
                    rateJESUp = histoDict['%s_%s_JESUp'%(proc,box)].Integral(1, numberOfMassBins, i, i)
                    rateJESDown = histoDict['%s_%s_JESDown'%(proc,box)].Integral(1, numberOfMassBins, i, i)
                    rateJERUp = histoDict['%s_%s_JERUp'%(proc,box)].Integral(1, numberOfMassBins, i, i)
                    rateJERDown = histoDict['%s_%s_JERDown'%(proc,box)].Integral(1, numberOfMassBins, i, i)
                    ratePuUp = histoDict['%s_%s_PuUp'%(proc,box)].Integral(1, numberOfMassBins, i, i)
                    ratePuDown = histoDict['%s_%s_PuDown'%(proc,box)].Integral(1, numberOfMassBins, i, i)
                jesErrs['%s_%s'%(proc,box)] =  1.0+(abs(rateJESUp-rate)+abs(rateJESDown-rate))/(2.*rate)   
                jerErrs['%s_%s'%(proc,box)] =  1.0+(abs(rateJERUp-rate)+abs(rateJERDown-rate))/(2.*rate) 
                puErrs['%s_%s'%(proc,box)] =  1.0+(abs(ratePuUp-rate)+abs(ratePuDown-rate))/(2.*rate)
            else:
                jesErrs['%s_%s'%(proc,box)] =  1.0
                jerErrs['%s_%s'%(proc,box)] =  1.0
                puErrs['%s_%s'%(proc,box)] =  1.0
            print proc, 'cat %i'%i, 'JES', jesErrs['%s_%s'%(proc,box)], 'JER' ,jerErrs['%s_%s'%(proc,box)], 'PU', puErrs['%s_%s'%(proc,box)], 'mcstat', mcstatErrs['%s_%s'%(proc,box),i,1]
            jesGraph[box, i].SetPoint(i_sig, mass,  jesErrs['%s_%s'%(proc,box)])
            jerGraph[box, i].SetPoint(i_sig, mass,  jerErrs['%s_%s'%(proc,box)])
            puGraph[box, i].SetPoint(i_sig, mass,  puErrs['%s_%s'%(proc,box)])
            mcstatGraph[box, i].SetPoint(i_sig, mass,  mcstatErrs['%s_%s'%(proc,box),i,1])

hist = rt.TH1D('hist','hist',100,50, 500)
hist.SetMinimum(1)
if muonCR: 
    hist.SetMaximum(2)
else:
    hist.SetMaximum(1.1)
    

rt.gStyle.SetOptStat(0)
#rt.gStyle.SetOptTitle(0)
c = rt.TCanvas('c','c',500,400)
if muonCR:
    muonString = '_muonCR'
else:
    muonString = ''
tfile_out = rt.TFile.Open('lnN_%s_%s%s.root'%(jet_type,sigName,muonString),'recreate')
for box in ['pass','fail']:
    for i in range(1,numberOfPtBins+1):
        hist.SetTitle('%s %s %s cat%i%s'%(jet_type, sigName, box, i,muonString))
        hist.Draw()
        jerGraph[box,i].Draw("csame")
        jesGraph[box,i].Draw("csame")
        jesGraph[box,i].SetLineColor(rt.kBlue)
        jesGraph[box,i].SetLineStyle(2)
        puGraph[box,i].Draw("csame")
        puGraph[box,i].SetLineColor(rt.kRed)
        puGraph[box,i].SetLineStyle(3)
        mcstatGraph[box,i].Draw("csame")
        mcstatGraph[box,i].SetLineColor(rt.kGreen)
        mcstatGraph[box,i].SetLineStyle(4)
        legend = rt.TLegend(0.5, 0.7, 0.9, 0.9)
        legend.SetFillStyle(0)
        legend.SetBorderSize(0)
        legend.SetTextSize(0.038)
        legend.SetTextFont(42)
        legend.AddEntry(jerGraph[box,i],'JER','l')
        legend.AddEntry(jesGraph[box,i],'JES','l')
        legend.AddEntry(puGraph[box,i],'PU', 'l')
        legend.AddEntry(mcstatGraph[box,i],'mcstat', 'l')
        legend.Draw('same')
        c.Print('lnN_%s_%s_%s_cat%i%s.pdf'%(jet_type,sigName,box,i,muonString))
        tfile_out.cd()
        jerGraph[box,i].Write()
        jesGraph[box,i].Write()
        puGraph[box,i].Write()
        mcstatGraph[box,i].Write()
                   


