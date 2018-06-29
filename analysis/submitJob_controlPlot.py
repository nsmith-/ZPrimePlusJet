import glob
import sys, commands, os, fnmatch
from optparse import OptionParser

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
    maxJobs = 1000
    dryRun = True

    outpath= 'controlPlotsGGH_jobs'
    gitClone = "git clone -b Hbb git://github.com/DAZSLE/ZPrimePlusJet.git"
    #gitClone = "git clone -b Hbb_test git://github.com/kakwok/ZPrimePlusJet.git"

    if not os.path.exists(outpath):
        exec_me("mkdir -p %s"%(outpath), False)
    os.chdir(outpath)
    print "submitting jobs from : ",os.getcwd()

    #Small files used by the exe
    files = ['']
    
    #ouput to ${MAINDIR}/ so that condor transfer the output to submission dir
    command = 'python ${CMSSW_BASE}/src/ZPrimePlusJet/analysis/controlPlotsGGH.py --lumi 36.7 -o ${MAINDIR}/ --i-split $1 --max-split $2'
    for iJob in range(0,maxJobs):
        #if not iJob==0: continue
        arguments = [ str(iJob), str(maxJobs)]
        exe       = "runjob_%s.sh"%iJob
        write_bash(exe, command,gitClone)
        write_condor(exe, arguments, files,dryRun)
