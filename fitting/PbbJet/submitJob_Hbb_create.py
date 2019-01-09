import glob
import sys, commands, os, fnmatch
from optparse import OptionParser,OptionGroup

def exec_me(command, dryRun=False):
    print command
    if not dryRun:
        os.system(command)

def write_condor(njobs, exe='runjob', files = [], dryRun=True):
    fname = '%s.jdl' % exe
    out = """universe = vanilla
Executable = {exe}.sh
Should_Transfer_Files = YES
WhenToTransferOutput = ON_EXIT_OR_EVICT
Transfer_Input_Files = {exe}.sh,{files}
Output = {exe}.$(Process).stdout
Error  = {exe}.$(Process).stderr
Log    = {exe}.$(Process).log
Arguments = $(Process) {njobs}
Queue {njobs}
    """.format(exe=exe, files=','.join(files), njobs=njobs)
    with open(fname, 'w') as f:
        f.write(out)
    if not dryRun:
        os.system("condor_submit %s" % fname)

def write_bash(exe='runjob', command='', gitClone=""):
    fname = '%s.sh' % exe
    out = """#!/bin/bash
date
MAINDIR=`pwd`
ls
#CMSSW from scratch (only need for root)
export CWD=${{PWD}}
export PATH=${{PATH}}:/cvmfs/cms.cern.ch/common
export CMS_PATH=/cvmfs/cms.cern.ch
export SCRAM_ARCH=slc6_amd64_gcc530
scramv1 project CMSSW CMSSW_8_1_0
cd CMSSW_8_1_0/src
eval `scramv1 runtime -sh` # cmsenv
{gitClone}
cd ZPrimePlusJet
echo "Execute with git status/log:"
git status -uno 
git log -n 1 
source setup.sh
cd ${{CWD}}
{command}
echo "Inside $MAINDIR:"
ls
echo "DELETING..."
rm -rf CMSSW_8_1_0
rm -rf *.pdf *.C
ls
date
""".format(command=command, gitClone=gitClone)
    with open(fname, 'w') as f:
        f.write(out)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--hadd', dest='hadd', action='store_true',default = False, help='hadd roots from subjobs', metavar='hadd')
    parser.add_option('--clean', dest='clean', action='store_true',default = False, help='clean submission files', metavar='clean')
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write histograms/job output', metavar='odir')
    parser.add_option('-n', '--njobs', dest='njobs', default=500, type="int", help='Number of jobs to split into', metavar='njobs')

    script_group  = OptionGroup(parser, "script options")
    script_group.add_option("--bb", action='store_true', dest="bb", default=False, help="sort by double b-tag")
    script_group.add_option('-m', '--muonCR', action='store_true', dest='muonCR', default=False, help='for muon CR',
                    metavar='muonCR')
    script_group.add_option('--dbtagmin', dest='dbtagmin', default=-99., type="float",
                      help='left bound to btag selection(fail region lower bound)', metavar='dbtagmin')
    script_group.add_option('--dbtagcut', dest='dbtagcut', default=0.9, type="float",
                      help='btag selection for cut value(pass region lower bound)', metavar='dbtagcut')
    script_group.add_option('--skip-qcd', action='store_true', dest='skipQCD', default=False, help='skip QCD', metavar='skip-qcd')
    script_group.add_option('--skip-data', action='store_true', dest='skipData', default=False, help='skip Data', metavar='skip-data')
    script_group.add_option("--lumi", dest="lumi", default=41.3, type="float", help="luminosity", metavar="lumi")
    script_group.add_option("--is2017"  , dest="is2017", action='store_true', default=False, help="use 2017 files", metavar="is2017")
    script_group.add_option("--sfData" , dest="sfData", default=1, type="int", help="process 1/sf of data", metavar="sfData")
    script_group.add_option("--region" , dest="region", default='topR6_N2',choices=['topR6_N2','QGquark','QGgluon'], help="region for pass/fail doubleB tag", metavar="region")
    parser.add_option_group(script_group)

    (options, args) = parser.parse_args()
    hadd  = options.hadd
    dryRun= False 

    maxJobs = options.njobs

    outpath= options.odir
    #gitClone = "git clone -b Hbb git://github.com/DAZSLE/ZPrimePlusJet.git"
    #gitClone = "git clone -b Hbb_test git://github.com/kakwok/ZPrimePlusJet.git"
    gitClone = "git clone -b Hbb git://github.com/andrzejnovak/ZPrimePlusJet.git"

    #Small files used by the exe
    files = []
    #ouput to ${MAINDIR}/ so that condor transfer the output to submission dir
    command      = 'python ${CMSSW_BASE}/src/ZPrimePlusJet/fitting/PbbJet/Hxx_create.py -o ${MAINDIR}/ --i-split $1 --max-split $2'
    #Add script options to job command
    for opts in script_group.option_list:
        if not getattr(options, opts.dest)==opts.default:
            print "Using non default option %s = %s "%(opts.dest, getattr(options, opts.dest))
            if opts.action == 'store_true':
                command  += " --%s "%(opts.metavar)
            else:
                command  += " --%s %s "%(opts.dest,getattr(options, opts.dest))

    if not hadd: 
        print "command to run: ", command

    fileName = 'hist_1DZbb_pt_scalesmear.root'
    if options.skipQCD:
        fileName = 'hist_1DZbb_pt_scalesmear_looserWZ.root'
    if options.bb:
        fileName = 'hist_1DZbb_sortByBB.root'
    elif options.muonCR:
        fileName = 'hist_1DZbb_muonCR.root'
    subFileName = fileName.replace(".root","_*.root")
    

    if not options.hadd:
        if not os.path.exists(outpath):
            exec_me("mkdir -p %s"%(outpath), False)
        os.chdir(outpath)
        print "submitting jobs from : ",os.getcwd()
    
        exe = "runjob"
        write_bash(exe, command, gitClone)
        write_condor(maxJobs, exe, files, dryRun)
    else:
        print "Trying to hadd subjob files from %s/%s"%(outpath,subFileName)
        nOutput = len(glob.glob("%s/%s"%(outpath,subFileName)))
        if nOutput==maxJobs:
            print "Found %s subjob output files"%nOutput
            exec_me("hadd -f %s/%s %s/%s"%(outpath,fileName,outpath,subFileName),dryRun)
            print "DONE hadd. Removing subjob files.."
            exec_me("rm %s/%s"%(outpath,subFileName),dryRun)
            if options.clean:
                print "Cleaning submission files..." 
                exec_me("rm %s/runjob.*.stdout" % (outpath,), dryRun)
                exec_me("rm %s/runjob.*.stderr" % (outpath,), dryRun)
                exec_me("rm %s/runjob.*.log" % (outpath,), dryRun)
        else:
            print "%s/%s jobs done, not hadd-ing"%(nOutput,maxJobs)
