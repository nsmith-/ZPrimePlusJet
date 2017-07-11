#!/usr/bin/env python
import ROOT as r,sys,math,os
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array
import re
#r.gSystem.Load("~/Dropbox/RazorAnalyzer/python/lib/libRazorRun2.so")
r.gSystem.Load(os.getenv('CMSSW_BASE')+'/lib/'+os.getenv('SCRAM_ARCH')+'/libHiggsAnalysisCombinedLimit.so')
#r.gInterpreter.GenerateDictionary("std::pair<std::string, RooDataHist*>", "map;string;RooDataHist.h")
#r.gInterpreter.GenerateDictionary("std::map<std::string, RooDataHist*>", "map;string;RooDataHist.h")


# including other directories
import tools as tools
#from RootIterator import RootIterator
from hist import *

BB_SF = 0.91
BB_SF_ERR = 0.03
V_SF = 0.993
V_SF_ERR = 0.043

##############################################################################
##############################################################################
#### B E G I N N I N G   O F   C L A S S
##############################################################################
##############################################################################

class RhalphabetBuilder(): 
    def __init__(self, pass_hists, fail_hists, input_file, out_dir, nr=2, np=1, mass_nbins=23, mass_lo=40, mass_hi=201, blind_lo=110, blind_hi=131, rho_lo=-6, rho_hi= -2.1, blind=False, mass_fit=False, freeze_poly=False, remove_unmatched=False, input_file_loose=None):
        self._pass_hists = pass_hists
        self._fail_hists = fail_hists
        self._mass_fit = mass_fit
        self._freeze = freeze_poly
        self._inputfile = input_file
        self._inputfile_loose = input_file_loose

        self._output_path = "{}/base.root".format(out_dir)
        self._rhalphabet_output_path = "{}/rhalphabase.root".format(out_dir)

        self._outfile_validation = r.TFile.Open("{}/validation.root".format(out_dir), "RECREATE");

        self._mass_nbins = mass_nbins
        self._mass_lo    = mass_lo
        self._mass_hi    = mass_hi
        self._blind = blind
        self._mass_blind_lo = blind_lo
        self._mass_blind_hi = blind_hi
        self._rho_lo = rho_lo
        self._rho_hi = rho_hi
        # self._mass_nbins = pass_hists[0].GetXaxis().GetNbins()
        # self._mass_lo    = pass_hists[0].GetXaxis().GetBinLowEdge( 1 )
        # self._mass_hi    = pass_hists[0].GetXaxis().GetBinUpEdge( self._mass_nbins )

        self._remove_unmatched  = remove_unmatched
        print "number of mass bins and lo/hi: ", self._mass_nbins, self._mass_lo, self._mass_hi;

        #polynomial order for fit
        self._poly_degree_rho = nr #1 = linear ; 2 is quadratic
        self._poly_degree_pt = np #1 = linear ; 2 is quadratic

        self._nptbins = pass_hists["data_obs"].GetYaxis().GetNbins()
        self._pt_lo = pass_hists["data_obs"].GetYaxis().GetBinLowEdge( 1 )
        self._pt_hi = pass_hists["data_obs"].GetYaxis().GetBinUpEdge( self._nptbins )

        # define RooRealVars
        self._lMSD    = r.RooRealVar("x","x",self._mass_lo,self._mass_hi)
        self._lMSD.setRange('Low',self._mass_lo,self._mass_blind_lo)
        self._lMSD.setRange('Blind',self._mass_blind_lo,self._mass_blind_hi)
        self._lMSD.setRange('High',self._mass_blind_hi,self._mass_hi)
        #self._lMSD.setBins(self._mass_nbins)       
        self._lPt     = r.RooRealVar("pt","pt",self._pt_lo,self._pt_hi)
        self._lPt.setBins(self._nptbins)
        self._lRho    = r.RooFormulaVar("rho","log(x*x/pt/pt)",r.RooArgList(self._lMSD,self._lPt))

        self._lEff    = r.RooRealVar("veff"      ,"veff"      ,0.5 ,0.,1.0)

        self._lEffQCD = r.RooRealVar("qcdeff"    ,"qcdeff"   ,0.01,0.,10.)
        qcd_pass_integral = 0
        qcd_fail_integral = 0
        for i in range(1,fail_hists["qcd"].GetNbinsX()+1):
            for j in range(1,fail_hists["qcd"].GetNbinsY()+1):
                if fail_hists["qcd"].GetXaxis().GetBinCenter(i) > self._mass_lo and fail_hists["qcd"].GetXaxis().GetBinCenter(i) < self._mass_hi:
                    qcd_fail_integral += fail_hists["qcd"].GetBinContent(i,j)
                    qcd_pass_integral += pass_hists["qcd"].GetBinContent(i,j)
        if qcd_fail_integral>0:
            qcdeff = qcd_pass_integral / qcd_fail_integral
            self._lEffQCD.setVal(qcdeff)
        print "qcdeff = %f"%qcdeff
        self._lDM     = r.RooRealVar("dm","dm", 0.,-10,10)
        self._lShift  = r.RooFormulaVar("shift",self._lMSD.GetName()+"-dm",r.RooArgList(self._lMSD,self._lDM)) 

        self._all_vars = []
        self._all_shapes = []
        self._all_data = []
        self._all_pars = []

        self._background_names = ["wqq", "zqq", "qcd", "tqq"]
        self._signal_names = []
        # for Pbb
        #for mass in [50,75,125,100,150,250,300]:
        #    self._signal_names.append("Pbb_" + str(mass))
        # for Hbb
        for mass in [125]:
            for sig in ["hqq", "zhqq", "whqq", "vbfhqq", "tthqq"]:
                self._signal_names.append(sig + str(mass))

    def run(self):
        self.LoopOverPtBins()

    def prefit(self):

        fbase = r.TFile.Open(self._output_path,'update')
        fralphabase = r.TFile.Open(self._rhalphabet_output_path,'update')

        categories = ['pass_cat1','pass_cat2','pass_cat3','pass_cat4','pass_cat5','pass_cat6',
                      'fail_cat1','fail_cat2','fail_cat3','fail_cat4','fail_cat5','fail_cat6']

        bkgs = self._background_names
        sigs = self._signal_names

        wbase = {}
        wralphabase = {}
        for cat in categories:
            wbase[cat] = fbase.Get('w_%s'%cat)
            wralphabase[cat] = fralphabase.Get('w_%s'%cat)

        w = r.RooWorkspace('w')
        w.factory('mu[1.,0.,20.]')
        x = wbase[categories[0]].var('x')
        rooCat = r.RooCategory('cat','cat')

        mu = w.var('mu')
        epdf_b = {} 
        epdf_s = {}
        datahist = {}
        histpdf = {}
        histpdfnorm = {}
        data = {}
        signorm = {}
        for cat in categories:
            rooCat.defineType(cat)

        for cat in categories:        
            norms_b = r.RooArgList()
            norms_s = r.RooArgList()
            norms_b.add(wralphabase[cat].function('qcd_%s_norm'%cat))
            norms_s.add(wralphabase[cat].function('qcd_%s_norm'%cat))
            pdfs_b = r.RooArgList()
            pdfs_s = r.RooArgList()
            pdfs_b.add(wralphabase[cat].pdf('qcd_%s'%cat))
            pdfs_s.add(wralphabase[cat].pdf('qcd_%s'%cat))

            data[cat] = wbase[cat].data('data_obs_%s'%cat)
            for proc in (bkgs+sigs):
                if proc=='qcd': continue

                datahist['%s_%s'%(proc,cat)] = wbase[cat].data('%s_%s'%(proc,cat))
                histpdf['%s_%s'%(proc,cat)] = r.RooHistPdf('histpdf_%s_%s'%(proc,cat),
                                                            'histpdf_%s_%s'%(proc,cat),
                                                            r.RooArgSet(wbase[cat].var('x')),
                                                            datahist['%s_%s'%(proc,cat)])
                getattr(w,'import')(datahist['%s_%s'%(proc,cat)],r.RooFit.RecycleConflictNodes())
                getattr(w,'import')(histpdf['%s_%s'%(proc,cat)],r.RooFit.RecycleConflictNodes())
                if 'hqq125' in proc:
                    # signal
                    signorm['%s_%s'%(proc,cat)] = r.RooRealVar('signorm_%s_%s'%(proc,cat),
                                                                'signorm_%s_%s'%(proc,cat),
                                                                datahist['%s_%s'%(proc,cat)].sumEntries(),
                                                                0,10.*datahist['%s_%s'%(proc,cat)].sumEntries())
                    signorm['%s_%s'%(proc,cat)].setConstant(True)                
                    getattr(w,'import')(signorm['%s_%s'%(proc,cat)],r.RooFit.RecycleConflictNodes())
                    histpdfnorm['%s_%s'%(proc,cat)] = r.RooFormulaVar('histpdfnorm_%s_%s'%(proc,cat),
                                                                       '@0*@1',r.RooArgList(mu,signorm['%s_%s'%(proc,cat)]))
                    pdfs_s.add(histpdf['%s_%s'%(proc,cat)])
                    norms_s.add(histpdfnorm['%s_%s'%(proc,cat)])
                else:
                    # background
                    histpdfnorm['%s_%s'%(proc,cat)] = r.RooRealVar('histpdfnorm_%s_%s'%(proc,cat),
                                                                    'histpdfnorm_%s_%s'%(proc,cat),
                                                                    datahist['%s_%s'%(proc,cat)].sumEntries(),
                                                                    0,10.*datahist['%s_%s'%(proc,cat)].sumEntries())
                    histpdfnorm['%s_%s'%(proc,cat)].setConstant(True)
                    getattr(w,'import')(histpdfnorm['%s_%s'%(proc,cat)],r.RooFit.RecycleConflictNodes())
                    pdfs_b.add(histpdf['%s_%s'%(proc,cat)])
                    pdfs_s.add(histpdf['%s_%s'%(proc,cat)])
                    norms_b.add(histpdfnorm['%s_%s'%(proc,cat)])
                    norms_s.add(histpdfnorm['%s_%s'%(proc,cat)])


            epdf_b[cat] = r.RooAddPdf('epdf_b_'+cat,'epdf_b_'+cat,pdfs_b,norms_b)
            epdf_s[cat] = r.RooAddPdf('epdf_s_'+cat,'epdf_s_'+cat,pdfs_s,norms_s)

            getattr(w,'import')(epdf_b[cat],r.RooFit.RecycleConflictNodes())
            getattr(w,'import')(epdf_s[cat],r.RooFit.RecycleConflictNodes())

        ## arguments = ["data_obs","data_obs",r.RooArgList(x),rooCat]

        ## m = r.std.map('string, RooDataHist*')()
        ## for cat in categories:
        ##    m.insert(r.std.pair('string, RooDataHist*')(cat, data[cat]))
        ## arguments.append(m)
        
        ## combData = getattr(r,'RooDataHist')(*arguments)
        
        cat = categories[0]
        args = data[cat].get(0)
            
        combiner = r.CombDataSetFactory(args, rooCat)
            
        for cat in categories:
            combiner.addSetBin(cat, data[cat])
        combData = combiner.done('data_obs','data_obs')

        simPdf_b = r.RooSimultaneous('simPdf_b','simPdf_b',rooCat)
        simPdf_s = r.RooSimultaneous('simPdf_s','simPdf_s',rooCat)
        for cat in categories:
            simPdf_b.addPdf(epdf_b[cat],cat)    
            simPdf_s.addPdf(epdf_s[cat],cat)

        mu.setVal(1.)    

        getattr(w,'import')(simPdf_b,r.RooFit.RecycleConflictNodes())
        getattr(w,'import')(simPdf_s,r.RooFit.RecycleConflictNodes())
        getattr(w,'import')(combData,r.RooFit.RecycleConflictNodes())

        w.Print('v')
        simPdf_b = w.pdf('simPdf_b')
        simPdf_s = w.pdf('simPdf_s')
        combData = w.data('data_obs')
        x = w.var('x')
        rooCat = w.cat('cat')
        mu = w.var('mu')
        CMS_set = r.RooArgSet()
        CMS_set.add(rooCat)
        CMS_set.add(x)

        opt = r.RooLinkedList()
        opt.Add(r.RooFit.CloneData(False))
        allParams = simPdf_b.getParameters(combData)
        r.RooStats.RemoveConstantParameters(allParams)            
        opt.Add(r.RooFit.Constrain(allParams))

        mu.setVal(1)
        mu.setConstant(True)

        nll = simPdf_s.createNLL(combData)
        m2 = r.RooMinimizer(nll)
        m2.setStrategy(2)
        m2.setMaxFunctionCalls(100000)
        m2.setMaxIterations(100000)
        m2.setPrintLevel(-1)
        m2.setPrintEvalErrors(-1)
        m2.setEps(1e-5)
        m2.optimizeConst(2)

        migrad_status = m2.minimize('Minuit2','migrad')
        improve_status = m2.minimize('Minuit2','improve')
        hesse_status = m2.minimize('Minuit2','hesse')
        fr = m2.save()
        fr.Print('v')

        icat = 0
        for cat in categories:
            reset(wralphabase[cat],fr)
            if icat==0:
                getattr(wralphabase[cat],'import')(fr)
                wralphabase[cat].writeToFile(self._rhalphabet_output_path,True)
            else:
                wralphabase[cat].writeToFile(self._rhalphabet_output_path,False)
            icat += 1

    def loadfit(self,fitToLoad):

        fralphabase_load = r.TFile.Open(fitToLoad,'read')
        fr = fralphabase_load.Get('w_pass_cat1').obj('nll_simPdf_s_data_obs')
        
        fbase = r.TFile.Open(self._output_path,'update')
        fralphabase = r.TFile.Open(self._rhalphabet_output_path,'update')

        categories = ['pass_cat1','pass_cat2','pass_cat3','pass_cat4','pass_cat5','pass_cat6',
                      'fail_cat1','fail_cat2','fail_cat3','fail_cat4','fail_cat5','fail_cat6']

        bkgs = self._background_names
        sigs = self._signal_names

        wbase = {}
        wralphabase = {}
        for cat in categories:
            wbase[cat] = fbase.Get('w_%s'%cat)
            wralphabase[cat] = fralphabase.Get('w_%s'%cat)

        icat = 0
        for cat in categories:
            reset(wralphabase[cat],fr,exclude='qcd_fail_cat')
            if icat==0:
                wralphabase[cat].writeToFile(self._rhalphabet_output_path,True)
            else:
                wralphabase[cat].writeToFile(self._rhalphabet_output_path,False)
            icat += 1
        
    def LoopOverPtBins(self):

        print "number of pt bins = ", self._nptbins;
        for pt_bin in range(1,self._nptbins+1):
        # for pt_bin in range(1,2):
            print "------- pT bin number ",pt_bin      

            # 1d histograms in each pT bin (in the order... data, w, z, qcd, top, signals)
            pass_hists_ptbin = {}
            fail_hists_ptbin = {}
            for name, hist in self._pass_hists.iteritems():
                pass_hists_ptbin[name] = tools.proj("cat",str(pt_bin),hist,self._mass_nbins,self._mass_lo,self._mass_hi)
            for name, hist in self._fail_hists.iteritems():
                fail_hists_ptbin[name] = tools.proj("cat",str(pt_bin),hist,self._mass_nbins,self._mass_lo,self._mass_hi)

            # make RooDataset, RooPdfs, and histograms
            # GetWorkspaceInputs returns: RooDataHist (data), then RooHistPdf of each electroweak
            (data_pass_rdh, data_fail_rdh, pass_rhps, fail_rhps) = self.GetWorkspaceInputs(pass_hists_ptbin, fail_hists_ptbin,"cat"+str(pt_bin))
            #Get approximate pt bin value
            this_pt = self._pass_hists["data_obs"].GetYaxis().GetBinLowEdge(pt_bin)+self._pass_hists["data_obs"].GetYaxis().GetBinWidth(pt_bin)*0.3;
            print "------- this bin pT value ",this_pt
            
            #Make the rhalphabet fit for this pt bin
            (rhalphabet_hist_pass, rhalphabet_hist_fail) = self.MakeRhalphabet(["data_obs", "wqq", "zqq", "tqq"], fail_hists_ptbin, this_pt, "cat"+str(pt_bin))

            # Get signals
            (signal_rdhs_pass, signal_rdhs_fail) = self.GetSignalInputs(pass_hists_ptbin, fail_hists_ptbin, "cat"+str(pt_bin))
            pass_rhps.update(signal_rdhs_pass)
            fail_rhps.update(signal_rdhs_fail)

            # #Write to file
            print "pass_rhps = "
            print pass_rhps
            self.MakeWorkspace(self._output_path, [data_pass_rdh] + pass_rhps.values(), "pass_cat"+str(pt_bin), True, True, this_pt)
            self.MakeWorkspace(self._output_path, [data_fail_rdh] + fail_rhps.values(), "fail_cat"+str(pt_bin), True, True, this_pt)

        
        for pt_bin in range(1,self._nptbins+1):
            for mass_bin in range(1,self._mass_nbins+1):
                print "qcd_fail_cat%i_Bin%i flatParam" % (pt_bin, mass_bin)

    # iHs = dict of fail histograms
    def MakeRhalphabet(self, samples, fail_histograms, pt, category):
        print "---- [MakeRhalphabet]"   

        rhalph_bkgd_name ="qcd";
        lUnity = r.RooConstVar("unity","unity",1.)
        lZero  = r.RooConstVar("lZero","lZero",0.)

        #Fix the pt (top) and the qcd eff
        self._lPt.setVal(pt)
        self._lEffQCD.setConstant(False)

        polynomial_variables = []
        self.buildPolynomialArray(polynomial_variables,self._poly_degree_pt,self._poly_degree_rho,"p","r",-30,30)
        print "polynomial_variables=",
        print polynomial_variables

        #Now build the function
        pass_bins = r.RooArgList()
        fail_bins = r.RooArgList()

        for mass_bin in range(1,self._mass_nbins+1):
            self._lMSD.setVal(fail_histograms["data_obs"].GetXaxis().GetBinCenter(mass_bin))
            if self._mass_fit :
                print ("Pt/mass poly")
                roopolyarray = self.buildRooPolyArray(self._lPt.getVal(),self._lMSD.getVal(),lUnity,lZero,polynomial_variables)
            else :
                print ("Pt/Rho poly")
                roopolyarray = self.buildRooPolyRhoArray(self._lPt.getVal(),self._lRho.getVal(),lUnity,lZero,polynomial_variables)
            print "RooPolyArray:"
            roopolyarray.Print()
            fail_bin_content = 0
            for sample in samples:
                if sample == "data_obs":
                    print sample, fail_histograms[sample].GetName(), "add data"
                    print "\t+={}".format(fail_histograms[sample].GetBinContent(mass_bin))
                    fail_bin_content += fail_histograms[sample].GetBinContent(mass_bin) # add data
                else:                    
                    print sample, fail_histograms[sample].GetName(), "subtract W/Z/ttbar"
                    print "\t-={}".format(fail_histograms[sample].GetBinContent(mass_bin))
                    fail_bin_content -= fail_histograms[sample].GetBinContent(mass_bin) # subtract W/Z/ttbar from data
            if fail_bin_content < 0: fail_bin_content = 0.

            print rhalph_bkgd_name+"_fail_"+category+"_Bin"+str(mass_bin), fail_bin_content

            #50 sigma range + 10 events
            fail_bin_unc = math.sqrt(fail_bin_content)*50.+10.
            #Define the failing category
            fail_bin_var = r.RooRealVar(rhalph_bkgd_name+"_fail_"+category+"_Bin"+str(mass_bin),rhalph_bkgd_name+"_fail_"+category+"_Bin"+str(mass_bin),fail_bin_content,0.,max(fail_bin_content+fail_bin_unc,0.))

            print "[david debug] fail_bin_var:"
            fail_bin_var.Print()

            #Now define the passing cateogry based on the failing (make sure it can't go negative)
            lArg = r.RooArgList(fail_bin_var,roopolyarray,self._lEffQCD)
            pass_bin_var = r.RooFormulaVar(rhalph_bkgd_name+"_pass_"+category+"_Bin"+str(mass_bin),rhalph_bkgd_name+"_pass_"+category+"_Bin"+str(mass_bin),"@0*max(@1,0)*@2",lArg)
            print "Pass=fail*poly*eff RooFormulaVar:"
            print pass_bin_var.Print()

            # print pass_bin_var.GetName()

            #If the number of events in the failing is small remove the bin from being free in the fit
            if fail_bin_content < 4:
                print "too small number of events", fail_bin_content, "Bin", str(mass_bin)
                fail_bin_var.setConstant(True)
                pass_bin_var = r.RooRealVar(rhalph_bkgd_name+"_pass_"+category+"_Bin"+str(mass_bin),rhalph_bkgd_name+"_pass_"+category+"_Bin"+str(mass_bin),0,0,0)
                pass_bin_var.setConstant(True)

            #Add bins to the array
            pass_bins.add(pass_bin_var)
            fail_bins.add(fail_bin_var)
            self._all_vars.extend([pass_bin_var,fail_bin_var])
            self._all_pars.extend([pass_bin_var,fail_bin_var])
            # print  fail_bin_var.GetName(),"flatParam",lPass#,lPass+"/("+lFail+")*@0"

        #print "Printing pass_bins:"
        #for i in xrange(pass_bins.getSize()):
        #    pass_bins[i].Print()
        pass_rparh  = r.RooParametricHist(rhalph_bkgd_name+"_pass_"+category,rhalph_bkgd_name+"_pass_"+category,self._lMSD,pass_bins,fail_histograms["data_obs"])
        fail_rparh  = r.RooParametricHist(rhalph_bkgd_name+"_fail_"+category,rhalph_bkgd_name+"_fail_"+category,self._lMSD,fail_bins,fail_histograms["data_obs"])
        print "Print pass and fail RooParametricHists"
        pass_rparh.Print()
        fail_rparh.Print()
        pass_norm = r.RooAddition(rhalph_bkgd_name+"_pass_"+category+"_norm",rhalph_bkgd_name+"_pass_"+category+"_norm",pass_bins)
        fail_norm = r.RooAddition(rhalph_bkgd_name+"_fail_"+category+"_norm",rhalph_bkgd_name+"_fail_"+category+"_norm",fail_bins)
        print "Printing NPass and NFail variables:"
        pass_norm.Print()
        fail_norm.Print()        
        self._all_shapes.extend([pass_rparh,fail_rparh,pass_norm,fail_norm])

        #Now write the wrokspace with the rooparamhist
        pass_workspace = r.RooWorkspace("w_pass_"+str(category))
        fail_workspace = r.RooWorkspace("w_fail_"+str(category))
        getattr(pass_workspace,'import')(pass_rparh,r.RooFit.RecycleConflictNodes())
        getattr(pass_workspace,'import')(pass_norm,r.RooFit.RecycleConflictNodes())
        getattr(fail_workspace,'import')(fail_rparh,r.RooFit.RecycleConflictNodes())
        getattr(fail_workspace,'import')(fail_norm,r.RooFit.RecycleConflictNodes())
        print "Printing rhalphabet workspace:"
        pass_workspace.Print()
        if category.find("1") > -1:
            pass_workspace.writeToFile(self._rhalphabet_output_path)
        else:
            pass_workspace.writeToFile(self._rhalphabet_output_path,False)
        fail_workspace.writeToFile(self._rhalphabet_output_path,False)
        return [pass_rparh,fail_rparh]

    def buildRooPolyArray(self,iPt,iMass,iQCD,iZero,iVars):

        # print "---- [buildRooPolyArray]"  
        # print len(iVars);

        lPt  = r.RooConstVar("Var_Pt_" +str(iPt)+"_"+str(iMass), "Var_Pt_" +str(iPt)+"_"+str(iMass),(iPt))
        lMass = r.RooConstVar("Var_Mass_"+str(iPt)+"_"+str(iMass), "Var_Mass_"+str(iPt)+"_"+str(iMass),(iMass))
        lMassArray = r.RooArgList()
        lNCount=0
        for pRVar in range(0,self._poly_degree_rho+1):
            lTmpArray = r.RooArgList()
            for pVar in range(0,self._poly_degree_pt+1):
                if lNCount == 0:
                    lTmpArray.add(iQCD) # for the very first constant (e.g. p0r0), just set that to 1
                else:
                    lTmpArray.add(iVars[lNCount])
                lNCount=lNCount+1
            pLabel="Var_Pol_Bin_"+str(round(iPt,2))+"_"+str(round(iMass,3))+"_"+str(pRVar)
            pPol = r.RooPolyVar(pLabel,pLabel,lPt,lTmpArray)
            lMassArray.add(pPol)
            self._all_vars.append(pPol)

        lLabel="Var_MassPol_Bin_"+str(round(iPt,2))+"_"+str(round(iMass,3))
        lMassPol = r.RooPolyVar(lLabel,lLabel,lMass,lMassArray)
        self._all_vars.extend([lPt,lMass,lMassPol])
        return lMassPol

    def buildRooPolyRhoArray(self,iPt,iRho,iQCD,iZero,iVars):

        # print "---- [buildRooPolyArray]"      

        lPt  = r.RooConstVar("Var_Pt_" +str(iPt)+"_"+str(iRho), "Var_Pt_" +str(iPt)+"_"+str(iRho),(iPt))
        lRho = r.RooConstVar("Var_Rho_"+str(iPt)+"_"+str(iRho), "Var_Rho_"+str(iPt)+"_"+str(iRho),(iRho))
        lRhoArray = r.RooArgList()
        lNCount=0
        for pRVar in range(0,self._poly_degree_rho+1):
            lTmpArray = r.RooArgList()
            for pVar in range(0,self._poly_degree_pt+1):
                if lNCount == 0: 
                    lTmpArray.add(iQCD); # for the very first constant (e.g. p0r0), just set that to 1
                else: 
                    print "lNCount = " + str(lNCount)
                    lTmpArray.add(iVars[lNCount])
                lNCount=lNCount+1
            pLabel="Var_Pol_Bin_"+str(round(iPt,2))+"_"+str(round(iRho,3))+"_"+str(pRVar)
            pPol = r.RooPolyVar(pLabel,pLabel,lPt,lTmpArray)
            print "pPol:"
            print pPol.Print()
            lRhoArray.add(pPol);
            self._all_vars.append(pPol)

        lLabel="Var_RhoPol_Bin_"+str(round(iPt,2))+"_"+str(round(iRho,3))
        lRhoPol = r.RooPolyVar(lLabel,lLabel,lRho,lRhoArray)
        self._all_vars.extend([lPt,lRho,lRhoPol])
        return lRhoPol


    def buildPolynomialArray(self, iVars,iNVar0,iNVar1,iLabel0,iLabel1,iXMin0,iXMax0):

        print "---- [buildPolynomialArray]"
        ## form of polynomial
        ## (p0r0 + p1r0 * pT + p2r0 * pT^2 + ...) + 
        ## (p0r1 + p1r1 * pT + p2r1 * pT^2 + ...) * rho + 
        ## (p0r2 + p1r2 * pT + p2r2 * pT^2 + ...) * rho^2 + ...
        '''
        r0p0    =    0, pXMin,pXMax
        r1p0    =   -3.7215e-03 +/-  1.71e-08
        r2p0    =    2.4063e-06 +/-  2.76e-11
            r0p1    =   -2.1088e-01 +/-  2.72e-06I  
            r1p1    =    3.6847e-05 +/-  4.66e-09
            r2p1    =   -3.8415e-07 +/-  7.23e-12
            r0p2    =   -8.5276e-02 +/-  6.90e-07
            r1p2    =    2.2058e-04 +/-  1.10e-09
            r2p2    =   -2.2425e-07 +/-  1.64e-12
        '''
        value = [ 0.,
            -3.7215e-03,
            2.4063e-06,
            -2.1088e-01, 
            3.6847e-05, 
            -3.8415e-07, 
            -8.5276e-02, 
            2.2058e-04,
            -2.2425e-07]
        error = [iXMax0,
            1.71e-08,
            2.76e-11,
            2.72e-06,
            4.66e-09,
            7.23e-12,
            6.90e-07,
            1.10e-09,
            1.64e-12]
        
        for i0 in range(iNVar0+1):
            for i1 in range(iNVar1+1):
                pVar = iLabel1+str(i1)+iLabel0+str(i0);     
                if self._freeze :
                
                    start = value [i0*3+i1]
                    pXMin = value [i0*3+i1]-error[i0*3+i1]
                    pXMax = value [i0*3+i1]+error[i0*3+i1]
                    
                else: 
                    start = 0.0
                    pXMin = iXMin0
                    pXMax = iXMax0
                
                pRooVar = r.RooRealVar(pVar,pVar,0.0,pXMin,pXMax)
                #print("========  here i0 %s i1 %s"%(i0,i1))
                print pVar
                #print(" is : %s  +/- %s"%(value[i0*3+i1],error[i0*3+i1]))
                iVars.append(pRooVar)
                self._all_vars.append(pRooVar)

    def GetWorkspaceInputs(self, pass_histograms, fail_histograms,iBin):

        roocategories = r.RooCategory("sample","sample") 
        roocategories.defineType("pass",1) 
        roocategories.defineType("fail",0) 
        data_rdh_pass = r.RooDataHist("data_obs_pass_"+iBin,"data_obs_pass_"+iBin,r.RooArgList(self._lMSD),pass_histograms["data_obs"])
        data_rdh_fail = r.RooDataHist("data_obs_fail_"+iBin,"data_obs_fail_"+iBin,r.RooArgList(self._lMSD), fail_histograms["data_obs"])
        data_rdh_comb  = r.RooDataHist("comb_data_obs","comb_data_obs",r.RooArgList(self._lMSD),r.RooFit.Index(roocategories),r.RooFit.Import("pass",data_rdh_pass),r.RooFit.Import("fail",data_rdh_fail)) 

        roofit_shapes = {}
        for sample in ["wqq", "zqq", "qcd", "tqq"]:
            roofit_shapes[sample] = self.GetRoofitHistObjects(pass_histograms[sample], fail_histograms[sample], sample, iBin)

        total_pdf_pass = r.RooAddPdf("tot_pass"+iBin,"tot_pass"+iBin,r.RooArgList(roofit_shapes["qcd"]["pass_epdf"]))
        total_pdf_fail = r.RooAddPdf("tot_fail"+iBin,"tot_fail"+iBin,r.RooArgList(roofit_shapes["qcd"]["fail_epdf"]))
        ewk_pdf_pass = r.RooAddPdf("ewk_pass"+iBin,"ewk_pass"+iBin,r.RooArgList(roofit_shapes["wqq"]["pass_epdf"],roofit_shapes["zqq"]["pass_epdf"], roofit_shapes["tqq"]["pass_epdf"]))
        ewk_pdf_fail = r.RooAddPdf("ewk_fail"+iBin,"ewk_fail"+iBin,r.RooArgList(roofit_shapes["wqq"]["fail_epdf"],roofit_shapes["zqq"]["fail_epdf"], roofit_shapes["tqq"]["fail_epdf"]))

        total_simulpdf  = r.RooSimultaneous("tot","tot",roocategories) 
        total_simulpdf.addPdf(total_pdf_pass,"pass") 
        total_simulpdf.addPdf(total_pdf_fail,"fail")     
        self._all_data.extend([data_rdh_pass,data_rdh_fail])
        self._all_shapes.extend([total_pdf_pass,total_pdf_fail,ewk_pdf_pass,ewk_pdf_fail])

        ## find out which to make global
        ## RooDataHist (data), then RooHistPdf of each electroweak
        # Previous return values 2 and 3 (RooAbsPdf (qcd,ewk)) removed by David on 19/1/2017, because they don't seem to be used. 
        return [
            data_rdh_pass, 
            data_rdh_fail, 
            #{"qcd":total_pdf_pass, "ewk":ewk_pdf_pass},
            #{"qcd":total_pdf_fail, "ewk":ewk_pdf_fail},
            {"wqq":roofit_shapes["wqq"]["pass_rdh"], "zqq":roofit_shapes["zqq"]["pass_rdh"], "tqq":roofit_shapes["tqq"]["pass_rdh"]}, 
            {"wqq":roofit_shapes["wqq"]["fail_rdh"], "zqq":roofit_shapes["zqq"]["fail_rdh"], "tqq":roofit_shapes["tqq"]["fail_rdh"]}, 
        ]

    # Get (RooHistPdf, RooExtendPdf, RooDataHist) for a pair of pass/fail histograms
    # - The RooExtendPdfs are coupled via their normalizations, N*eff or N*(1-eff). 
    def GetRoofitHistObjects(self, hist_pass, hist_fail, label="w", category="_cat0"):
        # normalization
        total_norm   = r.RooRealVar(label+"norm"+category, label+"norm"+category, (hist_pass.Integral()+hist_fail.Integral()), 0., 5.*(hist_pass.Integral()+hist_fail.Integral()))
        pass_norm  = r.RooFormulaVar(label+"fpass"+category, label+"norm"+category+"*(veff)", r.RooArgList(total_norm,self._lEff))
        fail_norm  = r.RooFormulaVar(label+"fqail"+category, label+"norm"+category+"*(1-veff)", r.RooArgList(total_norm,self._lEff))

        # shapes
        pass_rdh  = r.RooDataHist(label+"_pass_"+category, label+"_pass_"+category, r.RooArgList(self._lMSD),hist_pass)
        fail_rdh  = r.RooDataHist(label+"_fail_"+category, label+"_fail_"+category, r.RooArgList(self._lMSD),hist_fail) 
        pass_rhp      = r.RooHistPdf (label+"passh"+category, label+"passh"+category, r.RooArgList(self._lShift), r.RooArgList(self._lMSD), pass_rdh, 0)
        fail_rhp      = r.RooHistPdf (label+"failh"+category, label+"failh"+category, r.RooArgList(self._lShift), r.RooArgList(self._lMSD), fail_rdh, 0)

        # extended likelihood from normalization and shape above
        pass_epdf     = r.RooExtendPdf(label+"_passe_" +category, label+"pe" +category, pass_rhp, pass_norm)
        fail_epdf     = r.RooExtendPdf(label+"_faile_" +category, label+"fe" +category, fail_rhp, fail_norm)

        #lHist   = [pass_pdf,fail_rhp,pass_epdf,fail_epdf,pass_rdh,fail_rdh]
        return_dict = {
            "pass_rdh":pass_rdh, 
            "fail_rdh":fail_rdh,
            "pass_pdf":pass_rhp,
            "fail_pdf":fail_rhp, 
            "pass_epdf":pass_epdf,
            "fail_epdf":fail_epdf
        }
        self._all_vars.extend([total_norm, pass_norm, fail_norm])
        self._all_shapes.extend(return_dict.values())
        return return_dict

    def GetSignalInputs(self,iHP,iHF,iBin):
        # get signals
        lPSigs  = {}
        lFSigs  = {}
        for signal_name in self._signal_names:
            roofit_shapes = self.GetRoofitHistObjects(iHP[signal_name], iHF[signal_name],signal_name,iBin)
            lPSigs[signal_name] = roofit_shapes["pass_rdh"]
            lFSigs[signal_name] = roofit_shapes["fail_rdh"]
        return (lPSigs,lFSigs)


    #def MakeWorkspace(self,iOutput,iDatas,iFuncs,iVars,iCat="cat0",iShift=True):
    def MakeWorkspace(self, output_path, import_objects, category="cat0", do_shift=True, do_syst=True, pt_val=500.):
        print "Making workspace " + "w_" + str(category)
        workspace = r.RooWorkspace("w_"+str(category))

        # get the pT bin
        iPt = category[-1:]

        for import_object in import_objects:
            import_object.Print()
            process = import_object.GetName().split('_')[0]
            cat = import_object.GetName().split('_')[1]
            print 'Anter Object : ', import_object.GetName(), 'Process : ', process, 'Cat : ',cat
            mass = 0
            systematics = ['JES', 'JER', 'trigger', 'mcstat','Pu']
            if do_syst and ('tqq' in process or 'wqq' in process or 'zqq' in process or 'hqq' in process):
                # get systematic histograms
                hout = []
                histDict = {}
                for syst in systematics:
                    if syst == 'mcstat':
                        matchingString = ''
                        if self._remove_unmatched and ('wqq' in process or 'zqq' in process):
                            matchingString = '_matched'
                        if self._inputfile_loose is not None and ('wqq' in process or 'zqq' in process) and 'pass' in cat:                            
                            tmph = self._inputfile_loose.Get(process + '_' + cat + matchingString).Clone(process + '_' + cat)
                            tmph_up = self._inputfile_loose.Get(process + '_' + cat + matchingString).Clone(
                                process + '_' + cat + '_' + syst + 'Up')
                            tmph_down = self._inputfile_loose.Get(process + '_' + cat + matchingString).Clone(
                                process + '_' + cat + '_' + syst + 'Down')
                            tmph.Scale(GetSF(process, cat, self._inputfile, self._inputfile_loose, self._remove_unmatched, iPt))
                            tmph_up.Scale(GetSF(process, cat, self._inputfile, self._inputfile_loose, self._remove_unmatched, iPt))
                            tmph_down.Scale(GetSF(process, cat, self._inputfile, self._inputfile_loose, self._remove_unmatched, iPt))
                        else:                            
                            tmph = self._inputfile.Get(process + '_' + cat + matchingString).Clone(process + '_' + cat)
                            tmph_up = self._inputfile.Get(process + '_' + cat + matchingString).Clone(
                                process + '_' + cat + '_' + syst + 'Up')
                            tmph_down = self._inputfile.Get(process + '_' + cat + matchingString).Clone(
                                process + '_' + cat + '_' + syst + 'Down')
                            tmph.Scale(GetSF(process, cat, self._inputfile))
                            tmph_up.Scale(GetSF(process, cat, self._inputfile))
                            tmph_down.Scale(GetSF(process, cat, self._inputfile))
                        tmph_mass = tools.proj('cat', str(iPt), tmph, self._mass_nbins, self._mass_lo, self._mass_hi)
                        tmph_mass_up = tools.proj('cat', str(iPt), tmph_up, self._mass_nbins, self._mass_lo, self._mass_hi)
                        tmph_mass_down = tools.proj('cat', str(iPt), tmph_down, self._mass_nbins, self._mass_lo,
                                              self._mass_hi)
                        print 'Mass : ', tmph_mass, 'Up : ',tmph_mass_up, 'Down : ',tmph_mass_down

                        for i in range(1, tmph_mass_up.GetNbinsX() + 1):
                            mcstatup = tmph_mass_up.GetBinContent(i) + tmph_mass_up.GetBinError(i)
                            mcstatdown = max(0., tmph_mass_down.GetBinContent(i) - tmph_mass_down.GetBinError(i))
                            tmph_mass_up.SetBinContent(i, mcstatup)
                            tmph_mass_down.SetBinContent(i, mcstatdown)
                        tmph_mass.SetName(import_object.GetName())
                        tmph_mass_up.SetName(import_object.GetName() + '_' + import_object.GetName().replace('_', '') + syst + 'Up')
                        tmph_mass_down.SetName(import_object.GetName() + '_' + import_object.GetName().replace('_', '') + syst + 'Down')
                        histDict[import_object.GetName()] = tmph_mass
                        histDict[import_object.GetName() + '_' + import_object.GetName().replace('_', '') + syst + 'Up'] = tmph_mass_up
                        histDict[
                            import_object.GetName() + '_' + import_object.GetName().replace('_', '') + syst + 'Down'] = tmph_mass_down
                        if 'tqq' in process:
                            hout.append(tmph_mass)
                            # hout.append(tmph_mass_up)
                            # hout.append(tmph_mass_down)
                    else:
                        tmph_up = self._inputfile.Get(process + '_' + cat + '_' + syst + 'Up').Clone()
                        tmph_down = self._inputfile.Get(process + '_' + cat + '_' + syst + 'Down').Clone()
                        tmph_up.Scale(GetSF(process, cat, self._inputfile))
                        tmph_down.Scale(GetSF(process, cat, self._inputfile))
                        tmph_mass_up = tools.proj('cat', str(iPt), tmph_up, self._mass_nbins, self._mass_lo, self._mass_hi)
                        tmph_mass_down = tools.proj('cat', str(iPt), tmph_down, self._mass_nbins, self._mass_lo,
                                              self._mass_hi)
                        tmph_mass_up.SetName(import_object.GetName() + '_' + syst + 'Up')
                        tmph_mass_down.SetName(import_object.GetName() + '_' + syst + 'Down')
                        hout.append(tmph_mass_up)
                        hout.append(tmph_mass_down)
                uncorrelate(histDict, 'mcstat')
                for key, myhist in histDict.iteritems():
                    if 'mcstat' in key:
                        print key
                        hout.append(myhist)
                # blind if necessary and output to workspace
                for h in hout:
                    for i in range(1, h.GetNbinsX() + 1):
                        massVal = h.GetXaxis().GetBinCenter(i)
                        rhoVal = r.TMath.Log(massVal * massVal / pt_val / pt_val)
                        if self._blind and massVal > self._mass_blind_lo and massVal < self._mass_blind_hi:
                            print "blinding signal region for %s, mass bin [%i,%i] " % (
                            h.GetName(), h.GetXaxis().GetBinLowEdge(i), h.GetXaxis().GetBinUpEdge(i))
                            h.SetBinContent(i, 0.)
                            h.SetBinError(i, 0.)
                        if rhoVal < self._rho_lo or rhoVal > self._rho_hi:
                            print "removing rho = %.2f for %s, pt_val = %.2f, mass bin [%i,%i]" % (
                            rhoVal, h.GetName(), pt_val, h.GetXaxis().GetBinLowEdge(i), h.GetXaxis().GetBinUpEdge(i))
                            h.SetBinContent(i, 0.)
                            h.SetBinError(i, 0.)
                    tmprdh = r.RooDataHist(h.GetName(), h.GetName(), r.RooArgList(self._lMSD), h)
                    getattr(workspace, 'import')(tmprdh, r.RooFit.RecycleConflictNodes())
                    # validation
                    self._outfile_validation.cd()
                    h.Write()

            if do_shift and ('wqq' in process or 'zqq' in process or 'hqq' in process):
                if process == 'wqq':
                    mass = 80.
                elif process == 'zqq':
                    mass = 91.
                elif 'hqq' in process :
                    mass = float(process[-3:])  # hqq125 -> 125
                elif 'Pbb' in process:
                    mass = float(process.split('_')[-1])  # Pbb_75 -> 75

                # get the matched and unmatched hist
                
                if self._inputfile_loose is not None and ('wqq' in process or 'zqq' in process) and 'pass' in cat:                     
                    tmph_matched = self._inputfile_loose.Get(process + '_' + cat + '_matched').Clone()
                    tmph_unmatched = self._inputfile_loose.Get(process + '_' + cat + '_unmatched').Clone()
                    tmph_matched.Scale(GetSF(process, cat, self._inputfile, self._inputfile_loose, self._remove_unmatched, iPt))
                    tmph_unmatched.Scale(GetSF(process, cat, self._inputfile, self._inputfile_loose, False)) # doesn't matter if removing unmatched so just remove that option
                else:
                    tmph_matched = self._inputfile.Get(process + '_' + cat + '_matched').Clone()
                    tmph_unmatched = self._inputfile.Get(process + '_' + cat + '_unmatched').Clone()
                    tmph_matched.Scale(GetSF(process, cat, self._inputfile))
                    tmph_unmatched.Scale(GetSF(process, cat, self._inputfile))
                tmph_mass_matched = tools.proj('cat', str(iPt), tmph_matched, self._mass_nbins, self._mass_lo, self._mass_hi)
                tmph_mass_unmatched = tools.proj('cat', str(iPt), tmph_unmatched, self._mass_nbins, self._mass_lo,
                                           self._mass_hi)

                # smear/shift the matched
                hist_container = hist([mass], [tmph_mass_matched])
                # mass_shift = 0.99
                # mass_shift_unc = 0.03*2. #(2 sigma shift)
                # res_shift = 1.094
                # res_shift_unc = 0.123*2. #(2 sigma shift)
                m_data = 82.657
                m_data_err = 0.313
                m_mc = 82.548
                m_mc_err = 0.191
                s_data = 8.701
                s_data_err = 0.433
                s_mc = 8.027
                s_mc_err = 0.607
                mass_shift = m_data / m_mc
                mass_shift_unc = math.sqrt((m_data_err / m_data) * (m_data_err / m_data) + (m_mc_err / m_mc) * (
                m_mc_err / m_mc)) * 10.  # (10 sigma shift)
                res_shift = s_data / s_mc
                res_shift_unc = math.sqrt((s_data_err / s_data) * (s_data_err / s_data) + (s_mc_err / s_mc) * (
                s_mc_err / s_mc)) * 2.  # (2 sigma shift)
                # get new central value
                shift_val = mass - mass * mass_shift
                tmp_shifted_h = hist_container.shift(tmph_mass_matched, shift_val)
                # get new central value and new smeared value
                smear_val = res_shift - 1
                tmp_smeared_h = hist_container.smear(tmp_shifted_h[0], smear_val)
                hmatched_new_central = tmp_smeared_h[0]
                if smear_val <= 0: hmatched_new_central = tmp_smeared_h[1]
                    
                if re.match('zqq',tmph_mass_matched.GetName()):
                    print tmph_mass_matched.GetName()
                    print mass_shift
                    print mass_shift_unc
                    print shift_val
                    print "before shift", tmph_mass_matched.Integral()
                    print "after shift", tmp_shifted_h[0].Integral()
                
                    print res_shift
                    print res_shift_unc                
                    print smear_val                    
                    print "before smear", tmph_mass_matched.Integral()
                    print "after smear", hmatched_new_central.Integral()
                    #sys.exit()
                    
                # get shift up/down
                shift_unc = mass * mass_shift * mass_shift_unc
                hmatchedsys_shift = hist_container.shift(hmatched_new_central, mass * mass_shift_unc)
                # get res up/down
                hmatchedsys_smear = hist_container.smear(hmatched_new_central, res_shift_unc)

                if not (self._remove_unmatched and ('wqq' in process or 'zqq' in process)):
                    # add back the unmatched
                    hmatched_new_central.Add(tmph_mass_unmatched)
                    hmatchedsys_shift[0].Add(tmph_mass_unmatched)
                    hmatchedsys_shift[1].Add(tmph_mass_unmatched)
                    hmatchedsys_smear[0].Add(tmph_mass_unmatched)
                    hmatchedsys_smear[1].Add(tmph_mass_unmatched)
                hmatched_new_central.SetName(import_object.GetName())
                hmatchedsys_shift[0].SetName(import_object.GetName() + "_scaleUp")
                hmatchedsys_shift[1].SetName(import_object.GetName() + "_scaleDown")
                hmatchedsys_smear[0].SetName(import_object.GetName() + "_smearUp")
                hmatchedsys_smear[1].SetName(import_object.GetName() + "_smearDown")

                hout = [hmatched_new_central, hmatchedsys_shift[0], hmatchedsys_shift[1], hmatchedsys_smear[0],
                        hmatchedsys_smear[1]]
                # blind if necessary and output to workspace
                for h in hout:
                    for i in range(1, h.GetNbinsX() + 1):
                        massVal = h.GetXaxis().GetBinCenter(i)
                        rhoVal = r.TMath.Log(massVal * massVal / pt_val / pt_val)
                        if self._blind and massVal > self._mass_blind_lo and massVal < self._mass_blind_hi:
                            print "blinding signal region for %s, mass bin [%i,%i] " % (
                            h.GetName(), h.GetXaxis().GetBinLowEdge(i), h.GetXaxis().GetBinUpEdge(i))
                            h.SetBinContent(i, 0.)
                        if rhoVal < self._rho_lo or rhoVal > self._rho_hi:
                            print "removing rho = %.2f for %s, pt_val = %.2f, mass bin [%i,%i]" % (
                            rhoVal, h.GetName(), pt_val, h.GetXaxis().GetBinLowEdge(i), h.GetXaxis().GetBinUpEdge(i))
                            h.SetBinContent(i, 0.)
                    tmprdh = r.RooDataHist(h.GetName(), h.GetName(), r.RooArgList(self._lMSD), h)
                    getattr(workspace, 'import')(tmprdh, r.RooFit.RecycleConflictNodes())
                    if h.GetName().find("scale") > -1:
                        pName = h.GetName().replace("scale", "scalept")
                        tmprdh = r.RooDataHist(pName, pName, r.RooArgList(self._lMSD), h)
                        getattr(workspace, 'import')(tmprdh, r.RooFit.RecycleConflictNodes())
                        #pName = h.GetName().replace("scale", "shiftMH")
                        #tmprdh = r.RooDataHist(pName, pName, r.RooArgList(self._lMSD), h)
                        #getattr(workspace, 'import')(tmprdh, r.RooFit.RecycleConflictNodes())
                    # validation
                    self._outfile_validation.cd()
                    h.Write()
            else:
                print "Importing {}".format(import_object.GetName())
                getattr(workspace,'import')(import_object, r.RooFit.RecycleConflictNodes())

        if category.find("pass_cat1") == -1:
            workspace.writeToFile(output_path,False)
        else:
            workspace.writeToFile(output_path) 
        workspace.Print()
        # workspace.writeToFile(output_path)   

##############################################################################
##############################################################################
#### E N D   O F   C L A S S
##############################################################################
##############################################################################

##-------------------------------------------------------------------------------------
def LoadHistograms(f, pseudo, blind, useQCD, scale, r_signal, mass_range, blind_range, rho_range, fLoose=None):
    pass_hists = {}
    fail_hists = {}
    f.ls()

    # backgrounds
    pass_hists_bkg = {}
    fail_hists_bkg = {}
    background_names = ["wqq", "zqq", "qcd", "tqq"]
    for i, bkg in enumerate(background_names):
        if bkg=='qcd':
            qcd_fail = f.Get('qcd_fail')
            qcd_fail.Scale(1. / scale)
            qcd_fail.SetBinContent(13, 4, (
            qcd_fail.GetBinContent(12, 4) + qcd_fail.GetBinContent(14, 4)) / 2.)  # REMOVE HIGH WEIGHT EVENT BIN
            qcd_fail.SetBinError(13, 4, (
            qcd_fail.GetBinError(12, 4) + qcd_fail.GetBinError(14, 4)) / 2.)  # REMOVE HIGH WEIGHT EVENT BIN
            if useQCD:
                qcd_pass = f.Get('qcd_pass').Clone()
                qcd_pass.Scale(1. / scale)
            else:
                qcd_pass_real = f.Get('qcd_pass').Clone('qcd_pass_real')
                qcd_pass_real.Scale(1. / scale)
                qcd_pass = qcd_fail.Clone('qcd_pass')
                qcd_pass_real_integral = 0
                qcd_fail_integral = 0
                for i in range(1, qcd_pass_real.GetNbinsX() + 1):
                    for j in range(1, qcd_pass_real.GetNbinsY() + 1):
                        if qcd_pass_real.GetXaxis().GetBinCenter(i) > mass_range[0] and qcd_pass_real.GetXaxis().GetBinCenter(
                                i) < mass_range[1]:
                            qcd_pass_real_integral += qcd_pass_real.GetBinContent(i, j)
                            qcd_fail_integral += qcd_fail.GetBinContent(i, j)
                qcd_pass.Scale(qcd_pass_real_integral / qcd_fail_integral)  # qcd_pass = qcd_fail * eff(pass)/eff(fail)
            pass_hists_bkg["qcd"] = qcd_pass
            fail_hists_bkg["qcd"] = qcd_fail
            print 'qcd pass integral', qcd_pass.Integral()
            print 'qcd fail integral', qcd_fail.Integral()
        elif (fLoose is not None) and (bkg=='wqq' or bkg=='zqq'):
            hpass_tmp = fLoose.Get(bkg + '_pass').Clone()
            hfail_tmp = f.Get(bkg + '_fail').Clone()
            hpass_tmp.Scale(1. / scale)
            hfail_tmp.Scale(1. / scale)
            hpass_tmp.Scale(GetSF(bkg, 'pass', f, fLoose))
            hfail_tmp.Scale(GetSF(bkg, 'fail', f))
            pass_hists_bkg[bkg] = hpass_tmp
            fail_hists_bkg[bkg] = hfail_tmp            
        else:
            hpass_tmp = f.Get(bkg + '_pass').Clone()
            hfail_tmp = f.Get(bkg + '_fail').Clone()
            hpass_tmp.Scale(1. / scale)
            hfail_tmp.Scale(1. / scale)
            hpass_tmp.Scale(GetSF(bkg, 'pass', f))
            hfail_tmp.Scale(GetSF(bkg, 'fail', f))
            pass_hists_bkg[bkg] = hpass_tmp
            fail_hists_bkg[bkg] = hfail_tmp

    # signals
    pass_hists_sig = {}
    fail_hists_sig = {}
    # for Pbb
    #masses = [50, 75, 125, 100, 150, 250, 300]
    #sigs = ['Pbb_']
    #signal_names = []
    # for Hbb
    masses = [125]  # 50,75,125,100,150,200,250,300]
    sigs = ["hqq", "zhqq", "whqq", "vbfhqq", "tthqq"]
    signal_names = []

    for mass in masses:
        for sig in sigs:
            passhist = f.Get(sig + str(mass) + "_pass").Clone()
            failhist = f.Get(sig + str(mass) + "_fail").Clone()
            for hist in [passhist, failhist]:
                for i in range(0, hist.GetNbinsX() + 2):
                    for j in range(0, hist.GetNbinsY() + 2):
                        if hist.GetBinContent(i, j) <= 0:
                            hist.SetBinContent(i, j, 0)
            failhist.Scale(1. / scale)
            passhist.Scale(1. / scale)
            failhist.Scale(GetSF(sig + str(mass), 'fail', f))
            passhist.Scale(GetSF(sig + str(mass), 'pass', f))
            pass_hists_sig[sig + str(mass)] = passhist
            fail_hists_sig[sig + str(mass)] = failhist
            signal_names.append(sig + str(mass))

    if pseudo:        
        for i, bkg in enumerate(background_names):
            if i==0:
                pass_hists["data_obs"] = pass_hists_bkg[bkg].Clone('data_obs_pass')
                fail_hists["data_obs"] = fail_hists_bkg[bkg].Clone('data_obs_fail')
            else:                
                pass_hists["data_obs"].Add(pass_hists_bkg[bkg])
                fail_hists["data_obs"].Add(fail_hists_bkg[bkg])

        for i, signal in enumerate(signal_names):
            pass_hists["data_obs"].Add(pass_hists_sig[signal],r_signal)
            fail_hists["data_obs"].Add(fail_hists_sig[signal],r_signal)
    else:
        pass_hists["data_obs"] = f.Get('data_obs_pass')
        fail_hists["data_obs"] = f.Get('data_obs_fail')


    pass_hists.update(pass_hists_bkg)
    pass_hists.update(pass_hists_sig)
    fail_hists.update(fail_hists_bkg)
    fail_hists.update(fail_hists_sig)
    
    for histogram in (pass_hists.values() + fail_hists.values()):
        for i in range(1,histogram.GetNbinsX()+1):
            for j in range(1,histogram.GetNbinsY()+1):
                massVal = histogram.GetXaxis().GetBinCenter(i)
                ptVal = histogram.GetYaxis().GetBinLowEdge(j) + histogram.GetYaxis().GetBinWidth(j) * 0.3
                rhoVal = r.TMath.Log(massVal * massVal / ptVal / ptVal)
                if blind and histogram.GetXaxis().GetBinCenter(i) > blind_range[0] and histogram.GetXaxis().GetBinCenter(i) < blind_range[1]:
                    print "blinding signal region for %s, mass bin [%i,%i] "%(histogram.GetName(),histogram.GetXaxis().GetBinLowEdge(i),histogram.GetXaxis().GetBinUpEdge(i))
                    histogram.SetBinContent(i,j,0.)
                if rhoVal < rho_range[0] or rhoVal > rho_range[1]:
                    print "removing rho = %.2f for %s, pt bin [%i, %i], mass bin [%i,%i]" % (
                    rhoVal, histogram.GetName(), histogram.GetYaxis().GetBinLowEdge(j), histogram.GetYaxis().GetBinUpEdge(j),
                    histogram.GetXaxis().GetBinLowEdge(i), histogram.GetXaxis().GetBinUpEdge(i))
                    histogram.SetBinContent(i, j, 0.)
        histogram.SetDirectory(0)  

    # print "lengths = ", len(pass_hists), len(fail_hists)
    # print pass_hists;
    # print fail_hists;
    return (pass_hists,fail_hists)

def GetSF(process, cat, f, fLoose=None, removeUnmatched=False, iPt=-1):    
    SF = 1
    print process, cat
    if 'hqq' in process or 'zqq' in process or 'Pbb' in process:
        if 'pass' in cat:
            SF *= BB_SF
            if 'zqq' in process:
                print BB_SF
        else:
            passInt = f.Get(process + '_pass').Integral()
            failInt = f.Get(process + '_fail').Integral()
            if failInt > 0:
                SF *= (1. + (1. - BB_SF) * passInt / failInt)
                if 'zqq' in process:
                    print (1. + (1. - BB_SF) * passInt / failInt)
    if 'wqq' in process or 'zqq' in process or 'hqq' in process or 'Pbb' in process:
        SF *= V_SF
        if 'zqq' in process:
            print V_SF
    matchingString = ''
    if removeUnmatched and ('wqq' in process or 'zqq' in process):
        matchingString = '_matched'
    if fLoose is not None and ('wqq' in process or 'zqq' in process) and 'pass' in cat:
        if iPt > -1:
            nbinsX = f.Get(process + '_pass' + matchingString).GetXaxis().GetNbins()
            passInt = f.Get(process + '_pass' + matchingString).Integral(1, nbinsX, int(iPt), int(iPt))
            passIntLoose = fLoose.Get(process + '_pass' + matchingString).Integral(1, nbinsX, int(iPt), int(iPt))
        else:
            passInt = f.Get(process + '_pass' + matchingString).Integral()
            passIntLoose = fLoose.Get(process + '_pass' + matchingString).Integral()
        SF *= passInt/passIntLoose
        if 'zqq' in process:
            print passInt/passIntLoose
    # remove cross section from MH=125 signal templates (template normalized to luminosity*efficiency*acceptance)
    ## if process=='hqq125':
    ##     SF *= 1./48.85*5.824E-01
    ## elif process=='zhqq':
    ##     SF *= 1./(8.839E-01*(1.-3.*0.0335962-0.201030)*5.824E-01+8.839E-01*5.824E-01*0.201030+1.227E-01*5.824E-01*0.201030+1.227E-01*5.824E-01*0.201030)
    ## elif process=='whqq':
    ##     SF *= 1./(5.328E-01*(1.-3.*0.108535)*5.824E-01+8.400E-01*(1.-3.*0.108535)*5.824E-01)
    ## elif process=='vbfhqq':
    ##     SF *= 1./(3.782*5.824E-01)
    ## elif process=='tthqq':
    ##     SF *= 1./(5.071E-01*5.824E-01)
    
    #if 'zqq' in process:
    #    print SF
    #    sys.exit()
    return SF

def reset(w,fr,exclude=None):
    for p in RootIterator(fr.floatParsFinal()):
        if exclude is not None and exclude in p.GetName(): continue
        if w.var(p.GetName()):
            print 'setting %s = %e +/- %e from %s'%(p.GetName(), p.getVal(), p.getError(),fr.GetName())
            w.var(p.GetName()).setVal(p.getVal())
            w.var(p.GetName()).setError(p.getError())
    return True
