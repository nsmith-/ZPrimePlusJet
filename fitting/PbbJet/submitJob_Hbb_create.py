import glob
import sys, commands, os, fnmatch
from optparse import OptionParser,OptionGroup

def exec_me(command, dryRun=False):
    print command
    if not dryRun:
        os.system(command)

def write_condor(exe='runjob.sh', arguments = [], files = [],dryRun=True):
    job_name = exe.replace('.sh','.jdl')
    out = 'universe = vanilla\n'
    out += 'Executable = %s\n'%exe
    out += 'Should_Transfer_Files = YES\n'
    out += 'WhenToTransferOutput = ON_EXIT_OR_EVICT\n'
    out += 'Transfer_Input_Files = %s,%s\n'%(exe,','.join(files))
    out += 'Output = %s.stdout\n'%job_name
    out += 'Error  = %s.stderr\n'%job_name
    out += 'Log    = %s.log\n'   %job_name
    #out += 'notify_user = jduarte1@FNAL.GOV\n'
    #out += 'x509userproxy = /tmp/x509up_u42518\n'
    out += 'Arguments = %s\n'%(' '.join(arguments))
    out += 'Queue 1\n'
    with open(job_name, 'w') as f:
        f.write(out)
    if not dryRun:
        os.system("condor_submit %s"%job_name)

def write_bash(temp = 'runjob.sh', command = '' ,gitClone=""):
    out = '#!/bin/bash\n'
    out += 'date\n'
    out += 'MAINDIR=`pwd`\n'
    out += 'ls\n'
    out += '#CMSSW from scratch (only need for root)\n'
    out += 'export CWD=${PWD}\n'
    out += 'export PATH=${PATH}:/cvmfs/cms.cern.ch/common\n'
    out += 'export CMS_PATH=/cvmfs/cms.cern.ch\n'
    out += 'export SCRAM_ARCH=slc6_amd64_gcc530\n'
    out += 'scramv1 project CMSSW CMSSW_8_1_0\n'
    out += 'cd CMSSW_8_1_0/src\n'
    out += 'eval `scramv1 runtime -sh` # cmsenv\n'
    out += gitClone + '\n'
    out += 'cd ZPrimePlusJet\n'
    out += 'echo "Execute with git status/log:"\n'
    out += 'git status -uno \n'
    out += 'git log -n 1 \n'
    out += 'source setup.sh\n'
    out += 'cd ${CWD}\n'
    out += command + '\n'
    out += 'echo "Inside $MAINDIR:"\n'
    out += 'ls\n'
    out += 'echo "DELETING..."\n'
    out += 'rm -rf CMSSW_8_1_0\n'
    out += 'rm -rf *.pdf *.C\n'
    out += 'ls\n'
    out += 'date\n'
    with open(temp, 'w') as f:
        f.write(out)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('--hadd', dest='hadd', action='store_true',default = False, help='hadd roots from subjobs', metavar='hadd')
    parser.add_option('--clean', dest='clean', action='store_true',default = False, help='clean submission files', metavar='clean')
    parser.add_option('-o', '--odir', dest='odir', default='./', help='directory to write histograms/job output', metavar='odir')

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

    maxJobs = 500

    outpath= options.odir
    #gitClone = "git clone -b Hbb git://github.com/DAZSLE/ZPrimePlusJet.git"
    gitClone = "git clone -b Hbb_test git://github.com/kakwok/ZPrimePlusJet.git"

    #Small files used by the exe
    files = ['']
    #ouput to ${MAINDIR}/ so that condor transfer the output to submission dir
    command      = 'python ${CMSSW_BASE}/src/ZPrimePlusJet/fitting/PbbJet/Hbb_create.py -o ${MAINDIR}/ --i-split $1 --max-split $2'
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
    
        for iJob in range(0,maxJobs):
            #if not iJob==0: continue
            arguments = [ str(iJob), str(maxJobs)]
            exe       = "runjob_%s.sh"%iJob
            write_bash(exe, command,gitClone)
            write_condor(exe, arguments, files,dryRun)
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
                #remove all but _0 file
                for i in range(1,10):
                    exec_me("rm %s/runjob_%s*"%(outpath,i),dryRun)
        else:
            print "%s/%s jobs done, not hadd-ing"%(nOutput,maxJobs)
