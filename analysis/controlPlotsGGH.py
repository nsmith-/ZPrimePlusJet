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
from plotHelpers import *
from sampleContainer import *
#
def makePlots(plot,hs,hb,hd,hall,legname,color,style,isData,odir,lumi,ofile,canvases):
    if isData:
        c = makeCanvasComparisonStackWData(hd,hs,hb,legname,color,style,plot.replace('h_','stack_'),odir,lumi,ofile)
        canvases.append(c)	
    else:
        c = makeCanvasComparisonStack(hs,hb,legname,color,style,'ggHbb',plot.replace('h_','stack_'),odir,lumi,False,ofile)
        c1 = makeCanvasComparison(hall,legname,color,style,plot.replace('h_','signalcomparison_'),odir,lumi,ofile,True)
        canvases.append(c)	
        canvases.append(c1)
##############################################################################
def main(options,args,outputExists):
    #idir = "/eos/uscms/store/user/lpchbb/ggHsample_V11/sklim-v0-28Oct/"
    #odir = "plots_2016_10_31/"
    idir = options.idir
    odir = options.odir
    lumi = options.lumi
    isData = options.isData
    muonCR = options.muonCR

    
    legname = {'ggHbb': 'ggH(b#bar{b})',
               'Hbb': 'H(b#bar{b})',
               'VBFHbb':'VBF H(b#bar{b})',
               'VHbb': 'VH(b#bar{b})',
	       'ttHbb': 't#bar{t}H(b#bar{b})',
               'Diboson': 'VV(4q)',
               'SingleTop': 'single-t',
               'DY': 'Z+jets',
               'W': 'W+jets',
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
       
    tfiles = {'Hbb':   [idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			idir+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_1000pb_weighted.root',
			idir+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			idir+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			idir+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',  
			idir+'/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			idir+'/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
			idir+'/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root'],	
	      'ggHbb': [idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],
                        # idir+'/GluGluHToBB_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root'],
              'VBFHbb': [idir+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_1000pb_weighted.root'],
              'VHbb': [idir+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
              	       idir+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
                       idir+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
		       idir+'/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',
		       idir+'/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root'],
              'ttHbb':  [idir+'/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],#ttHTobb_M125_TuneCUETP8M2_ttHtranche3_13TeV_powheg_pythia8_1000pb_weighted.root'],
              'Diboson': [idir+'/WWTo4Q_13TeV_powheg_1000pb_weighted.root',
                          idir+'/ZZTo4Q_13TeV_amcatnloFXFX_madspin_pythia8_1000pb_weighted.root',
                          idir+'/WZ_13TeV_pythia8_1000pb_weighted.root'],
              'DY': [idir+'/DYJetsToQQ_HT180_13TeV_1000pb_weighted.root'],
              'SingleTop':  [idir+'/ST_t_channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
                             idir+'/ST_t_channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',
                             idir+'/ST_tW_antitop_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root',
                             idir+'/ST_tW_top_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root'],
              'W':  [idir+'/WJetsToQQ_HT180_13TeV_1000pb_weighted.root',
                     idir+'WJetsToLNu_HT_100To200_13TeV_1000pb_weighted.root',
                     idir+'/WJetsToLNu_HT_200To400_13TeV_1000pb_weighted.root',
                     idir+'/WJetsToLNu_HT_400To600_13TeV_1000pb_weighted.root',
                     idir+'/WJetsToLNu_HT_600To800_13TeV_1000pb_weighted.root',
                     idir+'/WJetsToLNu_HT_800To1200_13TeV_1000pb_weighted.root',
                    idir+'/WJetsToLNu_HT_1200To2500_13TeV_1000pb_weighted.root'],
              'TTbar':  [idir+'/TT_powheg_1000pb_weighted.root'], #Powheg is the new default
              'QCD': [idir+'/QCD_HT100to200_13TeV_1000pb_weighted.root',
                      idir+'/QCD_HT200to300_13TeV_ext_1000pb_weighted.root',
                      idir+'/QCD_HT300to500_13TeV_ext_1000pb_weighted.root',
                      idir+'/QCD_HT500to700_13TeV_ext_1000pb_weighted.root',
                      idir+'/QCD_HT700to1000_13TeV_1000pb_weighted.root',
                      idir+'/QCD_HT1000to1500_13TeV_ext_1000pb_weighted.root',
                      idir+'/QCD_HT1500to2000_13TeV_1000pb_weighted.root',
                      idir+'/QCD_HT2000toInf_13TeV_ext_1000pb_weighted.root',],
              'Phibb50': [idir+'/Spin0_ggPhi12j_g1_50_Scalar_13TeV_madgraph_1000pb_weighted.root'],
              'Phibb75': [idir+'/Spin0_ggPhi12j_g1_75_Scalar_13TeV_madgraph_1000pb_weighted.root'],
              'Phibb150': [idir+'/Spin0_ggPhi12j_g1_150_Scalar_13TeV_madgraph_1000pb_weighted.root'],
              'Phibb250': [idir+'/Spin0_ggPhi12j_g1_250_Scalar_13TeV_madgraph_1000pb_weighted.root'],
              'data': [
			   idir+'/JetHTRun2016G_23Sep2016_v1.root',
                           idir+'/JetHTRun2016H_PromptReco_v3.root',
                           idir+'/JetHTRun2016G_23Sep2016_v1_v2.root',
                           idir+'/JetHTRun2016B_23Sep2016_v1.root',
                           idir+'/JetHTRun2016H_PromptReco_v1.root',
                           idir+'/JetHTRun2016C_23Sep2016_v1.root']

              'muon': [ 
		       idir+'/SingleMuonRun2016H_PromptReco_v1.root',
                       idir+'/SingleMuonRun2016H_PromptReco_v3.root',
                       idir+'/SingleMuonRun2016B_23Sep2016_v1.root',
                       idir+'/SingleMuonRun2016F_23Sep2016_v1.root',
                       idir+'/SingleMuonRun2016E_23Sep2016_v1.root',
                       idir+'/SingleMuonRun2016D_23Sep2016_v1.root',
                       idir+'/SingleMuonRun2016H_PromptReco_v2.root',
                       idir+'/SingleMuonRun2016G_23Sep2016_v1.root',
                       idir+'/SingleMuonRun2016C_23Sep2016_v1.root',
                       idir+'/SingleMuonRun2016B_23Sep2016_v3.root']


            }

    color = {'ggHbb': ROOT.kAzure+1,
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
             'DY':  ROOT.kRed+1,
             'W':  ROOT.kGreen+2,
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
		     'Phibb50': 2,
             'Phibb75': 3,
		     'Phibb150': 4,
		     'Phibb250': 5,
             'VBFHbb': 3,
		     'VHbb': 4,
		     'ttHbb': 5,
             'Diboson': 1,
             'SingleTop': 1,
             'DY': 1,
             'W': 1,
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
        


    canvases = []
    if isData and muonCR:
        plots = ['h_msd_ak8_muCR1','h_msd_ak8_muCR2','h_msd_ak8_muCR3','h_msd_ak8_muCR4_pass','h_msd_ak8_muCR4_fail','h_msd_ak8_muCR5','h_msd_ak8_muCR6',
                 'h_msd_ak8_muCR4','h_pt_mu_muCR4','h_eta_mu_muCR4','h_pt_ak8_muCR4','h_eta_ak8_muCR4','h_dbtag_ak8_muCR4','h_t21ddt_ak8_muCR4','h_msd_ak8_topR6_N2_pass']                 
    elif isData:
        plots = ['h_pt_ak8','h_msd_ak8','h_dbtag_ak8','h_n_ak4','h_n_ak4_dR0p8','h_t21_ak8','h_t32_ak8','h_n2b1sdddt_ak8','h_t21ddt_ak8','h_met','h_npv','h_eta_ak8','h_ht']
    else:	
    	plots = ['h_pt_ak8','h_pt_ak8_sub1','h_pt_ak8_sub2','h_msd_ak8','h_msd_ak8_inc','h_dbtag_ak8','h_dbtag_ak8_sub1','h_dbtag_ak8_sub2',
                 'h_pt_bbleading','h_bb_bbleading','h_msd_bbleading',
                 'h_n_ak4','h_n_ak4_dR0p8','h_pt_ak8_dbtagCut','h_msd_ak8_dbtagCut',
                 'h_t21_ak8','h_t32_ak8','h_msd_ak8_t21ddtCut','h_msd_ak8_t21ddtCut_inc','h_msd_ak8_N2Cut','h_n_ak4_fwd',
                 'h_n_ak4L','h_n_ak4M','h_n_ak4T','h_n_ak4L100','h_n_ak4M100','h_n_ak4T100','h_n_ak4L150','h_n_ak4M150','h_n_ak4T150',
                 'h_n_ak4_dR0p8','h_isolationCA15','h_n2b1sdddt_ak8','h_t21ddt_ak8','h_msd_ak8_topR1','h_msd_ak8_topR2_pass',
                 'h_msd_ak8_topR3_pass','h_msd_ak8_topR4_pass','h_met','h_t32_ak8_t21ddtCut','h_msd_ak8_topR5_pass','h_msd_ak8_topR7_pass',
                 'h_msd_ak8_muCR1','h_msd_ak8_muCR2','h_msd_ak8_muCR3','h_msd_ak8_muCR4_pass','h_msd_ak8_muCR4_fail','h_msd_ak8_muCR5','h_msd_ak8_muCR6',
                 'h_msd_ak8_topR6_pass','h_msd_ak8_topR6_fail',
		 #'h_msd_ak8_topR6_pass_0p4','h_msd_ak8_topR6_fail_0p4',
		 #'h_msd_ak8_topR6_pass_0p45','h_msd_ak8_topR6_fail_0p45',
		 #'h_msd_ak8_topR6_pass_0p5','h_msd_ak8_topR6_fail_0p5',
		 #'h_msd_ak8_topR6_pass_0p6','h_msd_ak8_topR6_fail_0p6',
		 #'h_msd_ak8_topR6_pass_0p65','h_msd_ak8_topR6_fail_0p65',
	     #    'h_msd_ak8_topR6_pass_0p7','h_msd_ak8_topR6_fail_0p7',
		 #'h_msd_ak8_topR6_pass_0p75','h_msd_ak8_topR6_fail_0p75',
                 'h_msd_ak8_bbleading_topR6_pass','h_msd_ak8_bbleading_topR6_fail']
            
    if not outputExists: 
        print "Signals... "
        sigSamples = {}
        sigSamples['ggHbb']  = sampleContainer('ggHbb',tfiles['ggHbb']  , 1, lumi) 
        sigSamples['VBFHbb'] = sampleContainer('VBFHbb',tfiles['VBFHbb'], 1, lumi ) 
        sigSamples['VHbb'] = sampleContainer('VHbb',tfiles['VHbb'], 1, lumi ) 	
        sigSamples['ttHbb'] = sampleContainer('ttHbb',tfiles['ttHbb'], 1, lumi )    
        #sigSamples['Phibb50']  = sampleContainer('Phibb50',tfiles['Phibb50']  , 1, 0.2480*lumi) 
        #sigSamples['Phibb75'] = sampleContainer('Phibb75',tfiles['Phibb75'], 1, 0.2080*lumi ) 
        #sigSamples['Phibb150'] = sampleContainer('Phibb150',tfiles['Phibb150'], 1, 0.2764*lumi ) 	
        #sigSamples['Phibb250'] = sampleContainer('Phibb250',tfiles['Phibb250'], 1, 0.6699*lumi ) 	
        print "Backgrounds..."
        bkgSamples = {}    
        bkgSamples['QCD'] = sampleContainer('QCD',tfiles['QCD'], 1, lumi)
        if isData and muonCR:
            bkgSamples['TTbar1Mu']  = sampleContainer('TTbar1Mu',tfiles['TTbar'], 1, lumi, False, False, 'genMuFromW==1&&genEleFromW+genTauFromW==0')
            bkgSamples['TTbar1Ele']  = sampleContainer('TTbar1Ele',tfiles['TTbar'], 1, lumi, False, False, 'genEleFromW==1&&genMuFromW+genTauFromW==0')
            bkgSamples['TTbar1Tau']  = sampleContainer('TTbar1Tau',tfiles['TTbar'], 1, lumi, False, False, 'genTauFromW==1&&genEleFromW+genMuFromW==0')
            bkgSamples['TTbar0Lep']  = sampleContainer('TTbar0Lep',tfiles['TTbar'], 1, lumi, False, False, 'genMuFromW+genEleFromW+genTauFromW==0')
            bkgSamples['TTbar2Lep']  = sampleContainer('TTbar2Lep',tfiles['TTbar'], 1, lumi, False, False, 'genMuFromW+genEleFromW+genTauFromW==2')
        else:        
            bkgSamples['TTbar']  = sampleContainer('TTbar',tfiles['TTbar'], 1, lumi)
        bkgSamples['SingleTop'] = sampleContainer('SingleTop',tfiles['SingleTop'], 1, lumi)
        bkgSamples['Diboson'] = sampleContainer('Diboson',tfiles['Diboson'], 1, lumi)
        bkgSamples['W']  = sampleContainer('W',tfiles['W'], 1, lumi)
        bkgSamples['DY']  = sampleContainer('DY',tfiles['DY'], 1, lumi)
        #bkgSamples['Hbb'] = sampleContainer('Hbb',tfiles['Hbb'], 1, lumi ) 	

        if isData:
            print "Data..."
        if isData and muonCR:
            dataSample = sampleContainer('muon',tfiles['muon'], 1, lumi, isData, False, '((triggerBits&4)&&passJson)')
        elif isData:
            dataSample = sampleContainer('data',tfiles['data'], 1, lumi, isData, False, '((triggerBits&2)&&passJson)')
        
        ofile = ROOT.TFile.Open(odir+'/Plots_1000pb_weighted.root ','recreate')

        hall_byproc = {}
        for process, s in sigSamples.iteritems():
            hall_byproc[process] = {}
        for process, s in bkgSamples.iteritems():
            hall_byproc[process] = {}
        if isData:
            if muonCR:
                hall_byproc['muon'] = {}
            else:
                hall_byproc['data'] = {}

        for plot in plots:
            hs = {}
            hb = {}
            hall={}
            hd = None
            for process, s in sigSamples.iteritems():
                hs[process] = getattr(s,plot)
                hall[process] = getattr(s,plot)
                hall_byproc[process][plot] = getattr(s,plot)
            for process, s in bkgSamples.iteritems():
                hb[process] = getattr(s,plot)
                hall[process] = getattr(s,plot)
                hall_byproc[process][plot] = getattr(s,plot)
            if isData:
                hd = getattr(dataSample,plot)          
                if muonCR:      
                    hall_byproc['muon'][plot] = getattr(dataSample,plot)
                else:
                    hall_byproc['data'][plot] = getattr(dataSample,plot)
    
            makePlots(plot,hs,hb,hd,hall,legname,color,style,isData,odir,lumi,ofile,canvases)
            
        ofile.cd()
        for proc, hDict in hall_byproc.iteritems():
            for plot, h in hDict.iteritems():
                h.Write()
        ofile.Close()
    
    else:        
        sigSamples = ['ggHbb','VBFHbb','VHbb','ttHbb']        
        bkgSamples = ['QCD','SingleTop','Diboson','W','DY']                      
        if isData and muonCR:
            bkgSamples.extend(['TTbar1Mu','TTbar1Ele','TTbar1Tau','TTbar0Lep','TTbar2Lep'])
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
            if isData and muonCR:
                hd = ofile.Get(plot.replace('h_','h_muon_'))
            elif isData:
                hd = ofile.Get(plot.replace('h_','h_data_'))
                
            makePlots(plot,hs,hb,hd,hall,legname,color,style,isData,odir,lumi,ofile,canvases)
        


##----##----##----##----##----##----##
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", default = 30,type=float,help="luminosity", metavar="lumi")
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
    parser.add_option('-s','--isData', action='store_true', dest='isData', default =False,help='signal comparison', metavar='isData')
    parser.add_option('-m','--muonCR', action='store_true', dest='muonCR', default =False,help='for muon CR', metavar='muonCR')

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
        
    main(options,args,outputExists)
##----##----##----##----##----##----##




