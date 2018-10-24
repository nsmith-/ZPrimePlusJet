import json,glob,os
import controlPlotsGGH 
import Hbb_create
from optparse import OptionParser

def expand(fpaths):
    expandedPaths = []
    for p in fpaths:
        if "*" in p:
            if "root://" in p:
                redirector = "root://cmseos.fnal.gov/"
                eosp = p.replace("root://cmseos.fnal.gov/","")  #glob does not work with redirector
                globpaths = glob.glob(eosp)
                for i,glob_p in enumerate(globpaths):
                    globpaths[i] = redirector+glob_p
                expandedPaths.extend(globpaths)
        else:
            expandedPaths.append(p)
    return expandedPaths 

def expandPath(fdict):
    rdict = {}
    for sample,subSample in fdict.iteritems():
        if type(subSample)==type([]):       # already filenames
            rdict[sample] = expand(subSample)
            if len(rdict[sample])==0:            print "ERROR: %s has no files"%(sample)
        elif type(subSample)==type({}):     # subSamples has list of files each, expand
            d={} 
            for subSname,subpaths in subSample.iteritems():
                expandedPath = expand(subpaths) 
                if len(expandedPath)==0:            print "ERROR: %s has no files"%(subSname)
                d[subSname] = expandedPath 
            rdict[sample] =  d
    return rdict

def main(options,args):
    if not options.printOnly:
        outf = open(os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/samplefiles.json"),"w")
        print "Writing to ", os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/samplefiles.json")
    finaljson = {}
    finaljson['controlPlotsGGH_2017'] = expandPath(controlPlotsGGH.get2017files()) 
    #finaljson['Hbb_create_2017']      = expandPath(Hbb_create.get2017files(False)) 
    if not options.printOnly:
        outf.write((json.dumps(finaljson,indent=4)))
    else:
        print (json.dumps(finaljson,indent=4,sort_keys=True))
    for key,tfiles in finaljson.iteritems():
        print "list of samples used by %s =  "%key, sorted(tfiles.keys())


if __name__ == '__main__':
    parser = OptionParser()
    #parser.add_option('-o','--odir', dest='odir', default = '',help='directory to write plots', metavar='odir')
    parser.add_option('-p','--printOnly', dest='printOnly',action='store_true', default=False,help='print json to screen only', metavar='printOnly')
    (options, args) = parser.parse_args()
    main(options,args)

