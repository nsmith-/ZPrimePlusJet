#!/bin/bash

date

MAINDIR=`pwd`
ls

#If tarballing release
#export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
#export COIN_FULL_INDIRECT_RENDERING=1
#echo $VO_CMS_SW_DIR
#source $VO_CMS_SW_DIR/cmsset_default.sh
#export SCRAM_ARCH=slc6_amd64_gcc493
#tar xzf CMSSW_8_0_26_patch1.tar.gz
#cd CMSSW_8_0_26_patch1/src
#scram b ProjectRename
#eval `scramv1 runtime -sh`
#cd -

#CMSSW from scratch (only need for root)
export CWD=${PWD}
export PATH=${PATH}:/cvmfs/cms.cern.ch/common
export CMS_PATH=/cvmfs/cms.cern.ch
export SCRAM_ARCH=slc6_amd64_gcc491
scramv1 project CMSSW CMSSW_7_4_7
cd CMSSW_7_4_7/src
eval `scramv1 runtime -sh` # cmsenv
git clone -b phibb-fineddt https://github.com/DAZSLE/ZPrimePlusJet.git
cd ZPrimePlusJet
source setup.sh
cd ${CWD}


echo "var print: " 
for var in "$@"
do
    echo $var
done 
echo "$0"
echo "$1"
echo "$2"

python ${CMSSW_BASE}/src/ZPrimePlusJet/fitting/PbbJet/Hbb_create_Phibb.py --lumi 35.9 -o ./ -c --skip-mc --i-split $1 --max-split $2

echo "Inside $MAINDIR:"
ls
echo "DELETING..."
rm -rf CMSSW_7_4_7
#rm CMSSW_8_0_26_patch2.tar.gz
ls

date