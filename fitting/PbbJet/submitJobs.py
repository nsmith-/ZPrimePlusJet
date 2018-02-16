import sys, commands, os, fnmatch
from optparse import OptionParser

def exec_me(command, dryRun=False):
    print command
    if not dryRun:
        os.system(command)

def write_condor(temp='job_condor', arguments = [], files = []):
    out = 'universe = vanilla\n'
    out += 'Executable = runjob.sh\n'
    out += 'Should_Transfer_Files = YES\n'
    out += 'WhenToTransferOutput = ON_EXIT_OR_EVICT\n'
    out += 'Transfer_Input_Files = runjob.sh %s\n'%(' '.join(files))
    out += 'Output = job_$(Cluster)_$(Process).stdout\n'
    out += 'Error = job_$(Cluster)_$(Process).stderr\n'
    out += 'Log = job_$(Cluster)_$(Process).log\n'
    out += 'notify_user = jduarte1@FNAL.GOV\n'
    out += 'x509userproxy = /tmp/x509up_u42518\n'
    out += 'Arguments = %s\n'%(' '.join(arguments))
    out += 'Queue 1\n'
    with open(temp, 'w') as f:
        f.write(out)    

def write_bash(temp = 'runjob.sh', command = ''):
    out = '#!/bin/bash\n'
    out += 'date\n'
    out += 'MAINDIR=`pwd`\n'
    out += 'ls\n'
    out += '#CMSSW from scratch (only need for root)\n'
    out += 'export CWD=${PWD}\n'
    out += 'export PATH=${PATH}:/cvmfs/cms.cern.ch/common\n'
    out += 'export CMS_PATH=/cvmfs/cms.cern.ch\n'
    out += 'export SCRAM_ARCH=slc6_amd64_gcc491\n'
    out += 'scramv1 project CMSSW CMSSW_7_4_7\n'
    out += 'cd CMSSW_7_4_7/src\n'
    out += 'eval `scramv1 runtime -sh` # cmsenv\n'
    out += 'git clone -b 74x-root6 https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit HiggsAnalysis/CombinedLimit\n'
    out += 'scramv1 build -j 4\n'
    out += 'git clone -b phibb-fineddt https://github.com/DAZSLE/ZPrimePlusJet.git\n'
    out += 'cd ZPrimePlusJet\n'
    out += 'source setup.sh\n'
    out += 'cd ${CWD}\n'
    out += command + '\n'
    out += 'echo "Inside $MAINDIR:"\n'
    out += 'ls\n'
    #out += 'echo "DELETING..."\n'
    #out += 'rm -rf CMSSW_7_4_7\n'
    out += 'ls\n'
    out += 'date\n'
    with open(temp, 'w') as f:
        f.write(out)

if __name__ == '__main__':
    maxSplit = 100
    dryRun = False
    #command = 'python ${CMSSW_BASE}/src/ZPrimePlusJet/fitting/PbbJet/Hbb_create_Phibb.py --lumi 35.9 -o ./ -c --skip-mc --i-split $1 --max-split $2'
    files = ['cards_AK8_CA15_remove_unmatched/CA15/p9/DMSbb490/base.root', 'cards_AK8_CA15_remove_unmatched/CA15/p9/DMSbb490/rhalphabase.root', 'cards_AK8_CA15_remove_unmatched/CA15/p9/DMSbb490/datacard_muonCR.root', 'cards_AK8_CA15_remove_unmatched/CA15/p9/DMSbb490/card_rhalphabet_muonCR.txt']
    command = 'python ${CMSSW_BASE}/src/ZPrimePlusJet/fitting/PbbJet/limit.py -M Bias -d card_rhalphabet_muonCR.txt --datacard-alt card_rhalphabet_muonCR.txt -m 490 -o ./ -r 7 -t 10 --rMin -50 --rMax 50 --seed $1'

    for iSplit in range(0,maxSplit):
        arguments = [str(iSplit), str(maxSplit)]

        write_condor('job_condor', arguments, files)
        write_bash('runjob.sh', command)
    
        #exec_me('cat job_condor',dryRun)
        #exec_me('cat runjob.sh',dryRun)
        #exec_me('condor_submit job_condor' ,dryRun)
