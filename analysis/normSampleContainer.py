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
            xSection = self.getXsection(subSampleName,self.xsectionFile)   # in pb
            tfiles = {}
            # Allow "*" format
            expandedPath = paths
            for p in paths:
                if "*" in p:
                    expandedPath.extend(glob.glob(p))
                    expandedPath.remove(p)
            tfiles[subSampleName] = expandedPath 
            print "normSampleContainer:: subSample = %s , Nfiles = %s , basePath = %s"%(subSampleName, len(tfiles[subSampleName]), paths[0].replace(paths[0].split("/")[-1],""))
            #print datetime.datetime.now()
            Nentries           = self.getNentries(tfiles[subSampleName])
            #print datetime.datetime.now()
            lumiWeight         =  (xSection*1000*lumi) / Nentries
            print "normSampleContainer:: [sample %s, subsample %s] lumi = %s , xSection = %.3f, nEvent = %s, weight = %.3f" % (sampleName, subSampleName, lumi, xSection, Nentries, lumiWeight)
            self.subSampleContainers[subSampleName] = sampleContainer(subSampleName, tfiles[subSampleName], sf, DBTAGCUTMIN, lumiWeight, isData, fillCA15, cutFormula, minBranches, iSplit ,maxSplit,triggerNames,treeName,doublebName,doublebCut,puOpt)

    #Get the number of events from the NEvents histogram
    def getNentries(self,oTreeFiles):
        n = 0
        for otf in oTreeFiles:
            f  = TFile(otf)
            n += f.Get("NEvents").GetBinContent(1)
            f.Close()
        return n

    def getXsection(self,fDataSet,xSectionFile):
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
            allplots[plot] = getattr(sc, plot).Clone(self.sampleName+"_"+plot)      #Clone the histograms from first sample
        for plot in plots:
            for subSample in self.subSampleContainers.keys()[1:] :   #Add the rest of the histos
                sc             = self.subSampleContainers[subSample]
                allplots[plot].Add(getattr(sc,plot))
        return allplots

