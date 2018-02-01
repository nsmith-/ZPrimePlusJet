import sys, commands, os, fnmatch
from optparse import OptionParser

def exec_me(command, dryRun=False):
    print command
    if not dryRun:
        os.system(command)
        
if __name__ == '__main__':
    maxSplit = 1000
    dryRun = False
    for iSplit in range(0,maxSplit):
        exec_me('sed -e s/ISPLIT/%s/g -e s/MAXSPLIT/%s/g job_condor > job_condor_real'%(iSplit,maxSplit),dryRun)
        exec_me('cat job_condor_real',dryRun)
        exec_me('condor_submit job_condor_real' ,dryRun)
