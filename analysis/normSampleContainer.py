import ROOT
from ROOT import TFile
from sampleContainer import *
import glob

class normSampleContainer:
    def __init__(self, sampleName, subSamples, sf=1, DBTAGCUTMIN=-99., lumi=1, isData=False, fillCA15=False, cutFormula='1',
                 minBranches=False, iSplit = 0, maxSplit = 1, triggerNames={}, treeName='otree', 
                 doublebName='AK8Puppijet0_doublecsv', doublebCut = 0.9, puOpt='2016'):

        self.sampleName            = sampleName
        self.subSampleContainers    = {}
        self.subSamples             = subSamples
        self._sf                    = sf
        self._lumi                  = lumi
        self._triggerNames          = triggerNames 
        self.DBTAGCUTMIN = DBTAGCUTMIN
        self.DBTAGCUT = doublebCut
        self.doublebName = doublebName
        self.xsectionFile    = os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/xSections.dat")

        # subSamples = {subsampleName: [paths]}
        for subSampleName,paths in self.subSamples.iteritems():
            xSection = self.getXsection(subSampleName,self.xsectionFile, isData)   # in pb
            tfiles = {}
            tfiles[subSampleName] = paths 
            print "normSampleContainer:: subSample = %s , Nfiles = %s , basePath = %s"%(subSampleName, len(tfiles[subSampleName]), paths[0].replace(paths[0].split("/")[-1],""))
            #print datetime.datetime.now()
            Nentries,h_puMC,checksum           = self.getNentriesAndPu(tfiles[subSampleName])
	    if isData: h_puMC = puOpt
            print "PUhistogram type= ",type(h_puMC)
            #print datetime.datetime.now()
            lumiWeight         =  (xSection*1000*lumi) / Nentries
            print "normSampleContainer:: [sample %s, subsample %s] lumi = %s fb-1, xSection = %.3f pb, nEvent = %s, weight = %.5f, Nfiles=%s,(chkSum=%s)" % (sampleName, subSampleName, lumi, xSection, Nentries, lumiWeight,len(tfiles[subSampleName]),checksum)
            self.subSampleContainers[subSampleName] = sampleContainer(subSampleName, tfiles[subSampleName], sf, DBTAGCUTMIN, lumiWeight, isData, fillCA15, cutFormula, minBranches, iSplit ,maxSplit,triggerNames,treeName,doublebName,doublebCut,h_puMC)

    #Get the number of events from the NEvents histogram
    def getNentriesAndPu(self,oTreeFiles):
        n = 0
        f1 = TFile.Open(oTreeFiles[0])
        h_puMC = f1.Get("Pu").Clone()
        n     += f1.Get("NEvents").GetBinContent(1)
        h_puMC.SetDirectory(0)
        checksum = 1
        f1.Close()
        for otf in oTreeFiles[1:]:
            f  = TFile.Open(otf)
            n += f.Get("NEvents").GetBinContent(1)
            checksum +=1
            h_puMC.Add(f.Get("Pu"))
            f.Close()
        return n,h_puMC,checksum

    def getXsection(self,fDataSet,xSectionFile, isData):
	if isData: return 1.0
        thisXsection = 1.0
        FoundXsection = False
        print "NormSampleContainer:: using xsection files from : ",xSectionFile
        with open(xSectionFile) as xSections:
            for line in xSections:
                if line[0]=="\n" or line[0]=="#": continue
                line       = line.strip().split()
                DataSetRef = line[0]
                xSection   = line[1]
                if fDataSet == DataSetRef:
                    thisXsection = eval(xSection)
                    FoundXsection = True
                    break
        if not FoundXsection:
            print "NormSampleContainer:: Cannot find xsection for %s",fDataSet
            sys.exit()
        return thisXsection

    ## Add all plots from subSamples,  Returns plots in { sampleName_plotName : sc.attr }
    def addPlots(self,plots):
        allplots = {}
        for plot in plots:
            firstName     = self.subSampleContainers.keys()[0]
            sc            = self.subSampleContainers[firstName]
            allplots[plot] = getattr(sc, plot).Clone(plot.replace("h_","h_%s_"%self.sampleName))      #Clone the histograms from first sample
        for plot in plots:
            for subSample in self.subSampleContainers.keys()[1:] :   #Add the rest of the histos
                sc             = self.subSampleContainers[subSample]
                allplots[plot].Add(getattr(sc,plot))
        return allplots

