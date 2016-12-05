import json
from optparse import OptionParser
import ROOT as rt
import sys
from array import *
import os
from itertools import *
from operator import *
import pickle

def walk(top, topdown=True):
    """
    os.path.walk like function for TDirectories.
    Return 4-tuple: (dirpath, dirnames, filenames, top)
        dirpath = 'file_name.root:/some/path' # may end in a '/'?
        dirnames = ['list', 'of' 'TDirectory', 'keys']
        filenames = ['list', 'of' 'object', 'keys']
        top = this level's TDirectory
    """
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    assert isinstance(top, rt.TDirectory)
    names = [k.GetName() for k in top.GetListOfKeys()]
    dirpath = top.GetPath()
    dirnames = []
    filenames = []
    ## filter names for directories
    for k in names:
        d = top.Get(k)
        if isinstance(d, rt.TDirectory):
            dirnames.append(k)
        else:
            filenames.append(k)
    ## sort
    dirnames.sort()
    filenames.sort()
    ## yield
    if topdown:
        yield dirpath, dirnames, filenames, top
    for dn in dirnames:
        d = top.Get(dn)
        for x in walk(d, topdown):
            yield x
    if not topdown:
        yield dirpath, dirnames, filenames, top

    
def convertTree2Dict(runLumiDict,tree,lumiBranch,runBranch):    
    tree.SetBranchStatus("*",0)
    tree.SetBranchStatus(runBranch,1)
    tree.SetBranchStatus(lumiBranch,1)

    runNum = array('i',[0])
    lumiSec = array('i',[0])
    tree.SetBranchAddress(runBranch,runNum)
    tree.SetBranchAddress(lumiBranch,lumiSec)
    
    if not (hasattr(tree,lumiBranch) and hasattr(tree,runBranch)):
        print "tree does not contain run and lumi branches, returning empty json"
        return runLumiDict
    
    # loop over tree to get run, lumi "flat" dictionary
    nent = tree.GetEntries()
    print "total entries: %i"%nent
    for entry in xrange(nent):
        tree.GetEntry(entry)
        if entry%10000==0:
            print "processing entry %i"%entry
        if '%s'%(runNum[0]) in runLumiDict.keys():
            currentLumi = runLumiDict['%s'%(runNum[0])]
            if int(lumiSec[0]) in currentLumi:
                pass
            else:                
                currentLumi.append(int(lumiSec[0]))
                runLumiDict.update({'%s'%(runNum[0]):currentLumi})
        else:
            runLumiDict['%s'%(runNum[0])] = [int(lumiSec[0])]
        
    return runLumiDict

def fixDict(runLumiDict):
    # fix run, lumi list by grouping consecutive lumis
    for run in runLumiDict.keys():
        lumiGroups = []
        for k, g in groupby(enumerate(runLumiDict[run]), lambda (i,x):i-x):
            consecutiveLumis = map(itemgetter(1), g)
            lumiGroups.append([consecutiveLumis[0],consecutiveLumis[-1]])
        runLumiDict.update({run:lumiGroups})
        
    return runLumiDict
    
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-o','--output',dest="output",type="string",default="test.json",
                  help="Name of the json file to write to")
    parser.add_option('-l','--lumi-branch',dest="lumiBranch",type="string",default="lumi",
                  help="Name of lumi branch in tree")
    parser.add_option('-r','--run-branch',dest="runBranch",type="string",default="run",
                  help="Name of run branch in tree")
    
    (options,args) = parser.parse_args()


    rootFiles = []
    for f in args:
        if f.lower().endswith('.root'):
            rootFile = rt.TFile.Open(f)
            rootFiles.append(rootFile)

    trees = []
    # crawl root file to look for trees
    for rootFile in rootFiles:
        for dirpath, dirnames, filenames, tdirectory in walk(rootFile):
            for filename in set(filenames):
                obj = tdirectory.Get(filename)
                if isinstance(obj, rt.TTree) and obj!=None:
                    print "found tree %s in directory %s in file %s"%(obj.GetName(),tdirectory.GetName(),rootFile.GetName())
                    trees.append(obj)

    # loop over trees found
    runLumiDict = {}
    for tree in trees:
        runLumiDict = convertTree2Dict(runLumiDict,tree,options.lumiBranch,options.runBranch)
    runLumiDict = fixDict(runLumiDict)
    output = open(options.output,'w')
    json.dump(runLumiDict,output,sort_keys=True)
    output.close()
    print '\njson dumped to file %s:'%options.output
    os.system('cat %s'%options.output)
    print '\n'
            
    
