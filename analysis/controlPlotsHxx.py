import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array
import glob
import os,json
from plotHelpers import *
from sampleContainer import *
from normSampleContainer import *
DBTMIN=-99
#
def makePlots(plot,hs,hb,hd,hall,legname,color,style,isData,odir,lumi,ofile,canvases, blind=False):
    if isData:
        c = makeCanvasComparisonStackWData(hd,hs,hb,legname,color,style,plot.replace('h_','stack_'),odir,lumi,ofile, blind=blind)
        canvases.append(c)  
    else:
        c = makeCanvasComparisonStack(hs,hb,legname,color,style,'ggHbb',plot.replace('h_','stack_'),odir,lumi,False,ofile)
        c1 = makeCanvasComparison(hall,legname,color,style,plot.replace('h_','signalcomparison_'),odir,lumi,ofile,True)
        canvases.append(c1)

##############################################################################
def main(options,args,outputExists):
    odir = options.odir
    lumi = options.lumi
    isData = options.isData
    muonCR = options.muonCR
    is2017 = options.is2017
    
    legname = {
            'ggHbb': 'ggH(b#bar{b})',
            'ggHcc': 'ggH(c#bar{c})',
            'Hbb': 'H(b#bar{b})',
            'VBFHbb':'VBF H(b#bar{b})',
            'VHbb': 'VH(b#bar{b})',
            'ttHbb': 't#bar{t}H(b#bar{b})',
            'Diboson': 'VV(4q)',
            'SingleTop': 'single-t',
            'Z': 'Z(qq)+jets',
            'W': 'W(qq)+jets',
            'DYll': 'Z(ll)+jets',
            'Wlnu': 'W(l#nu)+jets',
            'TTbar': 't#bar{t}+jets',        
            'TTbar1Mu': 't#bar{t}+jets, 1#mu',  
            'TTbar1Ele': 't#bar{t}+jets, 1e',        
            'TTbar1Tau': 't#bar{t}+jets, 1#tau',        
            'TTbar0Lep': 't#bar{t}+jets, 0l',        
            'TTbar2Lep': 't#bar{t}+jets, 2l',        
            'QCD': 'QCD',
            'data': 'JetHT data',
            'muon': 'SingleMuon data',
            'Phibb50': '#Phi(b#bar{b}), 50 GeV',
            'Phibb75': '#Phi(b#bar{b}), 75 GeV',
            'Phibb150': '#Phi(b#bar{b}), 150 GeV',
            'Phibb250': '#Phi(b#bar{b}), 250 GeV'               
    }

    if isData and muonCR:
        legname['data'] = 'SingleMuon data'

    if options.is2017:
        samplefiles   = open(os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/samples_v15.01.json"),"r")
        tfiles  = json.load(samplefiles)['Hxx_2017']
    # Load older when missing
        backup_samplefiles   = open(os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/samplefiles.json"),"r")
        b_tfiles  = json.load(backup_samplefiles)['controlPlotsGGH_2017']
        for key in b_tfiles.keys():
            if key not in tfiles.keys():
                tfiles[key] = b_tfiles[key]
                print "Adding old/backup files:", key 
        puOpt  = "2017"
    else:
        tfiles = get2016files()
        puOpt  = "2016"       

    color = {'ggHbb': ROOT.kAzure+1,
             'ggHcc': ROOT.kRed+1,
             'Hbb': ROOT.kRed,
             'VHbb': ROOT.kTeal+1,
             'VBFHbb': ROOT.kBlue-10,
             'Phibb50': ROOT.kBlue-1,
             'Phibb75': ROOT.kAzure+1,
             'Phibb150': ROOT.kTeal+1,
             'Phibb250': ROOT.kMagenta+1,
             'ttHbb': ROOT.kBlue-1,
             'Diboson': ROOT.kOrange,
             'SingleTop': ROOT.kRed-2,
             'Z':  ROOT.kRed,
             'DYll':  ROOT.kRed-3,
             'W':  ROOT.kGreen+3,
             'Wlnu':  ROOT.kGreen+2,
             'TTbar':  ROOT.kGray,
             'TTbar1Mu':  ROOT.kViolet,
             'TTbar1Ele':  ROOT.kSpring,
             'TTbar1Tau':  ROOT.kOrange+2,
             'TTbar0Lep':  ROOT.kGray,
             'TTbar2Lep':  ROOT.kMagenta-9,
             'QCD': ROOT.kBlue+2,
             'data':ROOT.kBlack,
             'muon':ROOT.kBlack
            }

    style = {'Hbb': 1,
             'ggHbb': 2,             
             'ggHcc': 2,             
             'Phibb50': 2,
             'Phibb75': 3,
             'Phibb150': 4,
             'Phibb250': 5,
             'VBFHbb': 3,
             'VHbb': 4,
             'ttHbb': 5,
             'Diboson': 1,
             'SingleTop': 1,
             'Z': 1,
             'DYll': 1,
             'W': 1,
             'Wlnu': 1,
             'TTbar': 1,
             'TTbar1Mu': 1,
             'TTbar1Ele': 1,
             'TTbar1Tau': 1,
             'TTbar0Lep': 1,
             'TTbar2Lep': 1,
             'QCD': 1,
             'data': 1,
             'muon':1
            }

    # Defining plots
    canvases = []
    if options.isData and muonCR:
        plots = []
        testSample = sampleContainer('test',[], 1, DBTMIN,lumi)
        for attr in dir(testSample):
            try:
                if 'h_' in attr and getattr(testSample,attr).InheritsFrom('TH1') and not getattr(testSample,attr).InheritsFrom('TH2'):
                    plots.append(attr)
            except:
                pass
	blind_data = []
    elif isData:
        plots = ['h_pt_ak8','h_msd_ak8','h_dbtag_ak8','h_n_ak4','h_n_ak4_dR0p8','h_t21_ak8','h_t32_ak8','h_n2b1sdddt_ak8','h_t21ddt_ak8',
        'h_met','h_npv','h_eta_ak8','h_ht','h_dbtag_ak8_aftercut','h_n2b1sdddt_ak8_aftercut','h_rho_ak8', 
        'h_DDBvLtag_ak8', 'h_DDCvLtag_ak8', 'h_DDCvBtag_ak8', 
        'h_msd_ak8_Hcc1_incl', 'h_msd_ak8_Hcc1_pass', 'h_msd_ak8_Hcc1_fail',
        'h_Cuts'] 
        blind_data = ['h_msd_ak8_Hcc1_pass', 'h_msd_ak8_Hcc1_fail', 'h_msd_ak8_Hcc1_incl']
    else:
        plots = []
        testSample = sampleContainer('test',[], 1, DBTMIN,lumi)
        for attr in dir(testSample):
            try:
                if 'h_' in attr and getattr(testSample,attr).InheritsFrom('TH1') and not getattr(testSample,attr).InheritsFrom('TH2'):
                    plots.append(attr)
            except:
                pass
	blind_data = []
    print plots
    if not outputExists: # First step making files
        samples = ['ggHbb', 'ggHcc', 'ttHbb','QCD','SingleTop','Diboson','TTbar']                      
        pudir="root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.08-Pu/hadd/"
        print tfiles.keys()
        for s in samples:
            if type(tfiles[s])==type({}): continue
            for tfile in tfiles[s]:
                if not "root://" in tfile and not os.path.isfile(tfile):
                    print 'ControlplotGGH:: error: %s does not exist'%tfile                 
                    sys.exit()
        print "Signals... "
        sigSamples = {}
        # normSampleContainer(sampleName, subSamples, sf=1, DBTAGCUTMIN=-99., lumi=1, options.isData=False, fillCA15=False, cutFormula='1', minBranches=False, 
        #                        iSplit = 0, maxSplit = 1, triggerNames={}, treeName='otree', doublebName='AK8Puppijet0_doublecsv', doublebCut = 0.9, puOpt='2016')
        def_treeName = 'Events'
        def_DDB = 'AK8Puppijet0_deepdoubleb'
        dbtagcut = options.dbtagcut
        if  options.is2017:
            sigSamples['ggHbb'] = normSampleContainer('ggHbb', tfiles['ggHbb'], 1, DBTMIN, lumi, False, False, '1', False, 
                iSplit = options.iSplit, maxSplit = options.maxSplit, treeName=def_treeName, doublebName=def_DDB, doublebCut=dbtagcut, puOpt='default').addPlots(plots) 
            sigSamples['ggHcc'] = normSampleContainer('ggHcc',tfiles['ggHcc']  , 1, DBTMIN,lumi,False,False,'1',False, 
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, doublebCut=dbtagcut, puOpt='default').addPlots(plots) 
            sigSamples['ttHbb'] = normSampleContainer('ttHbb',tfiles['ttHbb']  , 1, DBTMIN,lumi,False,False,'1',False, 
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, doublebCut=dbtagcut, puOpt='default').addPlots(plots)
            sigSamples['WHbb'] = normSampleContainer('WHbb',tfiles['WHbb']  , 1, DBTMIN,lumi,False,False,'1',False, 
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, doublebCut=dbtagcut, puOpt='default').addPlots(plots)
            sigSamples['ZHbb'] = normSampleContainer('ZHbb',tfiles['ZHbb']  , 1, DBTMIN,lumi,False,False,'1',False,
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, doublebCut=dbtagcut, puOpt='default').addPlots(plots)
            sigSamples['VBFHbb'] = normSampleContainer('VBFHbb',tfiles['VBFHbb']  , 1, DBTMIN,lumi,False,False,'1',False, 
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, doublebCut=dbtagcut, puOpt='default').addPlots(plots)
        else:
            sigSamples['ggHbb']  = sampleContainer('ggHbb',tfiles['ggHbb']  , 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt) 
            sigSamples['VBFHbb'] = sampleContainer('VBFHbb',tfiles['VBFHbb'], 1, DBTMIN,lumi ,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt) 
            sigSamples['VHbb'] = sampleContainer('VHbb',tfiles['VHbb'], 1, DBTMIN,lumi ,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)    

        print "Backgrounds..."
        bkgSamples = {}    
        if options.is2017:
            bkgSamples['W']   = normSampleContainer('W',tfiles['W'], 1, DBTMIN,lumi,False,False,'1',False, 
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, doublebCut=dbtagcut,  puOpt="default").addPlots(plots)
            bkgSamples['Zcc']  = normSampleContainer('Zcc',tfiles['Z'], 1, DBTMIN,lumi,False,False,'1',False, selectFlav=2, 
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, doublebCut=dbtagcut, puOpt="default").addPlots(plots)
            bkgSamples['Zbb']  = normSampleContainer('Zbb',tfiles['Z'], 1, DBTMIN,lumi,False,False,'1',False, selectFlav=3, 
                iSplit = options.iSplit, maxSplit = options.maxSplit,treeName=def_treeName, doublebName=def_DDB, doublebCut=dbtagcut, puOpt="default").addPlots(plots)
            bkgSamples['QCD'] = normSampleContainer('QCD',tfiles['qcd'], 1, DBTMIN,lumi,False,False,'1',False, 
                iSplit = options.iSplit, maxSplit = options.maxSplit, treeName=def_treeName, doublebName=def_DDB, doublebCut=dbtagcut, puOpt="default").addPlots(plots)
            bkgSamples['TTbar']  = normSampleContainer('TTbar',tfiles['TTbar'], 1, DBTMIN,lumi,False,False,'1',False,
                iSplit = options.iSplit, maxSplit = options.maxSplit, treeName=def_treeName, doublebName=def_DDB, doublebCut=dbtagcut, puOpt="default").addPlots(plots)
            bkgSamples['SingleTop']  = normSampleContainer('SingleTop',tfiles['SingleTop'], 1, DBTMIN,lumi,False,False,'1',False,
                iSplit = options.iSplit, maxSplit = options.maxSplit, treeName=def_treeName, doublebName=def_DDB, doublebCut=dbtagcut, puOpt="default").addPlots(plots)
            bkgSamples['Diboson']  = normSampleContainer('Diboson',tfiles['Diboson'], 1, DBTMIN,lumi,False,False,'1',False,
                iSplit = options.iSplit, maxSplit = options.maxSplit, treeName=def_treeName, doublebName=def_DDB, doublebCut=dbtagcut, puOpt="default").addPlots(plots)

            if options.isData and muonCR:
            	bkgSamples['Wlnu']  = normSampleContainer('Wlnu',tfiles['Wlnu'], 1, DBTMIN,lumi,False,False,'1',False,
                iSplit = options.iSplit, maxSplit = options.maxSplit, treeName=def_treeName, doublebName=def_DDB, doublebCut=dbtagcut, puOpt="default").addPlots(plots)
                pass
                # no samples here

        else:
            bkgSamples['W']  = sampleContainer('W',tfiles['W'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
            bkgSamples['Z'] = sampleContainer('Z',tfiles['Z'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
            bkgSamples['QCD'] = sampleContainer('QCD',tfiles['QCD'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
            bkgSamples['TTbar']  = sampleContainer('TTbar',tfiles['TTbar'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
            bkgSamples['SingleTop']=sampleContainer('SingleTop',tfiles['SingleTop'],1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
            bkgSamples['Diboson'] = sampleContainer('Diboson',tfiles['Diboson'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
            if options.isData and muonCR:
                bkgSamples['Wlnu']  = sampleContainer('Wlnu',tfiles['Wlnu'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt='2016')
                bkgSamples['DYll']  = sampleContainer('DYll',tfiles['DYll'], 1, DBTMIN,lumi,False,False,'1',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt='2016')

        if options.isData: 
            print "Data..."
            triggerNames={"version":"zprimebit-15.01","branchName":"triggerBits",
                          "names":[
                               "HLT_AK8PFJet330_PFAK8BTagCSV_p17_v*",
                               "HLT_PFHT1050_v*",
                               "HLT_AK8PFJet400_TrimMass30_v*",
                               "HLT_AK8PFJet420_TrimMass30_v*",
                               "HLT_AK8PFHT800_TrimMass50_v*",
                               "HLT_PFJet500_v*",
                               "HLT_AK8PFJet500_v*"]
            }
        if options.is2017:
            if options.isData and muonCR:
                dataSample = normSampleContainer('muon', tfiles['muon'], 1, DBTMIN, lumi, True, False, '((triggerBits&1)&&passJson)', False,
                    iSplit = options.iSplit, maxSplit = options.maxSplit, treeName=def_treeName, doublebName=def_DDB, doublebCut=dbtagcut).addPlots(plots)
            elif options.isData:      
                dataSample = normSampleContainer('data', tfiles['data'], 1, DBTMIN,lumi, options.isData,False,"passJson",False,
                    iSplit = options.iSplit, maxSplit = options.maxSplit, triggerNames=triggerNames, treeName=def_treeName, doublebName=def_DDB, doublebCut=dbtagcut).addPlots(plots)
        else:
            if options.isData and muonCR:
                dataSample = normSampleContainer('muon', tfiles['muon'], 1, DBTMIN, lumi, True, False, '((triggerBits&4)&&passJson)', False,
                    iSplit = options.iSplit, maxSplit = options.maxSplit, triggerNames=triggerNames, treeName=def_treeName).addPlots(plots)
            elif options.isData:
                dataSample = sampleContainer('data',tfiles['data'], 1, DBTMIN,lumi, options.isData, False, '((triggerBits&2)&&passJson)',False, iSplit = options.iSplit, maxSplit = options.maxSplit,puOpt=options.puOpt)
        
        ofile = ROOT.TFile.Open(odir+'/Plots_1000pb_weighted_%s.root '%options.iSplit,'recreate')
        # Initialize dict (is this necessary?)
        hall_byproc = {}
        for process, s in sigSamples.iteritems():
            hall_byproc[process] = {}
        for process, s in bkgSamples.iteritems():
            hall_byproc[process] = {}
        if options.isData:
            if muonCR:
                hall_byproc['muon'] = {}
            else:
                hall_byproc['data'] = {}

        #normSamples =['QCD','Z','W', 'TTbar', 'Wlnu','ggHbb','ggHcc', 'ttHbb', 'Diboson', 'SingleTop']
        for Sample in bkgSamples.keys():
            #if Sample in normSamples:
            if type(bkgSamples[Sample]) == dict:
                hall_byproc[Sample] = bkgSamples[Sample]
                del bkgSamples[Sample]
        for Sample in sigSamples.keys():
            #if Sample in normSamples:
            if type(sigSamples[Sample]) == dict:
                hall_byproc[Sample] = sigSamples[Sample]
                del sigSamples[Sample]
        if options.isData:
            if not options.muonCR:
                hall_byproc['data'] = dataSample
            else: 
                hall_byproc['muon'] = dataSample

        for plot in plots:
            for process, s in sigSamples.iteritems():
                hall_byproc[process][plot] = getattr(s,plot)
            for process, s in bkgSamples.iteritems():
                hall_byproc[process][plot] = getattr(s,plot)
        print 'halled all'
        ofile.cd()
        for proc, hDict in hall_byproc.iteritems():
            for plot, h in hDict.iteritems():
                print proc, plot, h.Integral()
                h.Write()
        print 'filewrote'

            # for plot in plots:
            #     hs = {}
            #     hb = {}
            #     hall={}
            #     hd = None
            #     for process, s in sigSamples.iteritems():
            #         hs[process] = getattr(s,plot)
            #         hall[process] = getattr(s,plot)
            #     for process, s in bkgSamples.iteritems():
            #         hb[process] = getattr(s,plot)
            #         hall[process] = getattr(s,plot)
                #if isData:
                #    hd = getattr(dataSample,plot)
                #makePlots(plot,hs,hb,hd,hall,legname,color,style,isData,odir,lumi,ofile,canvases)
        
        ofile.Close()
    else:  
        print "Plotting part"
        #sigSamples = ['ggHbb', 'ggHcc', 'ttHbb', 'VBFHbb','VHbb','ttHbb']        
        sigSamples = ['ggHbb', 'ggHcc', 'ttHbb', 'VBFHbb','ttHbb']        
        bkgSamples = ['QCD','SingleTop','Diboson','W','Z']                      
        if options.isData and muonCR:
            bkgSamples.extend(['Wlnu'])#,'DYll'])
            bkgSamples.extend(['TTbar'])
        else:        
            bkgSamples.extend(['TTbar'])
            
        ofile = ROOT.TFile.Open(odir+'/Plots_1000pb_weighted.root','read')
        for plot in plots:
            hb = {}
            hs = {}
            hall = {}
            hd = None
            for process in bkgSamples:
                hb[process] = ofile.Get(plot.replace('h_','h_%s_'%process))
                hall[process] = ofile.Get(plot.replace('h_','h_%s_'%process))
            for process in sigSamples:
                hs[process] = ofile.Get(plot.replace('h_','h_%s_'%process))
                hall[process] = ofile.Get(plot.replace('h_','h_%s_'%process))
            if options.isData and muonCR:
                hd = ofile.Get(plot.replace('h_','h_muon_'))
            elif options.isData:
                hd = ofile.Get(plot.replace('h_','h_data_'))
            else: pass
            empty = False
            for process, s in dict(hall.items()).iteritems():
                if s == None: empty=True
            if empty:
                print "Plots for {} are empty".format(plot)
                continue
            if plot in blind_data: blind_this = True
            else: blind_this = False
            makePlots(plot,hs,hb,hd,hall,legname,color,style,options.isData,odir,lumi,ofile,canvases, blind_this)
	    #except:
		#    print "can't plot", plot
        


##----##----##----##----##----##----##
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", default = 35.9,type=float,help="luminosity", metavar="lumi")
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
    parser.add_option('-s','--isData', action='store_true', dest='isData', default =False,help='signal comparison', metavar='isData')
    parser.add_option('-m','--muonCR', action='store_true', dest='muonCR', default =False,help='for muon CR', metavar='muonCR')
    parser.add_option('--is2017', action='store_true', dest='is2017', default =True,help='for using 2017 files', metavar='is2017')
    parser.add_option("--max-split", dest="maxSplit", default=1, type="int", help="max number of jobs", metavar="maxSplit")
    parser.add_option("--i-split"  , dest="iSplit", default=0, type="int", help="job number", metavar="iSplit")
    parser.add_option("--puOpt"  , dest="puOpt", default="2017", help="select pu weight source", metavar="puOpt")
    parser.add_option('--dbtagcut', dest='dbtagcut', default=0.9, type="float",
                      help='btag selection for cut value(pass region lower bound)', metavar='dbtagcut')

    (options, args) = parser.parse_args()

     
    import tdrstyle
    tdrstyle.setTDRStyle()
    ROOT.gStyle.SetPadTopMargin(0.10)
    ROOT.gStyle.SetPadLeftMargin(0.16)
    ROOT.gStyle.SetPadRightMargin(0.10)
    #ROOT.gStyle.SetPalette(1)
    ROOT.gStyle.SetPaintTextFormat("1.1f")
    ROOT.gStyle.SetOptFit(0000)
    ROOT.gROOT.SetBatch()

    
    outputExists = False
    if glob.glob(options.odir+'/Plots_1000pb_weighted.root'):
        outputExists = True
    print "outputExists:", outputExists
        
    main(options,args,outputExists)
##----##----##----##----##----##----##




