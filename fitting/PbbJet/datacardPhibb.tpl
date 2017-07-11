Combination of datacard.tpl
imax 2 number of bins
jmax * number of processes minus 1
kmax * number of nuisance parameters
----------------------------------------------------------------------------------------------------------------------------------
shapes * fail_CATX base.root w_fail_CATX:$PROCESS_fail_CATX w_fail_CATX:$PROCESS_fail_CATX_$SYSTEMATIC
shapes qcd fail_CATX rhalphabase.root w_fail_CATX:$PROCESS_fail_CATX
shapes * pass_CATX base.root w_pass_CATX:$PROCESS_pass_CATX w_pass_CATX:$PROCESS_pass_CATX_$SYSTEMATIC
shapes qcd pass_CATX rhalphabase.root w_pass_CATX:$PROCESS_pass_CATX
----------------------------------------------------------------------------------------------------------------------------------
bin pass_CATX fail_CATX
observation -1.0 -1.0 
----------------------------------------------------------------------------------------------------------------------------------
bin pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX
process SIGNALNAMESIGNALMASS zqq wqq qcd tqq hqq125 tthqq125 vbfhqq125 whqq125 zhqq125 SIGNALNAMESIGNALMASS zqq wqq qcd tqq hqq125 tthqq125 vbfhqq125 whqq125 zhqq125
process 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9
rate -1 -1 -1 1.0 -1 -1 -1 -1 -1 -1 -1 -1 -1 1.0 -1 -1 -1 -1 -1 -1 
----------------------------------------------------------------------------------------------------------------------------------
lumi lnN 1.025 1.025 1.025 - - 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 - - 1.025 1.025 1.025 1.025 1.025
veff lnN 1.2 1.2 1.2 - - 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 - - 1.2 1.2 1.2 1.2 1.2 
bbeff lnN 1.1 - - - - 1.1 1.1 1.1 1.1 1.1 1.1 - - - - 1.1 1.1 1.1 1.1 1.1 
hqq125pt lnN - - - - - 1.3 - - - - - - - - - 1.3 - - - - 
znormQ lnN - 1.1 1.1 - - - - - - - - 1.1 1.1 - - - - - - - 
znormEW lnN - 1.15 1.15 - - - - - - - - 1.15 1.15 - - - - - - -
wznormEW lnN - - 1.05 - - - - - - - - - 1.05 - - - - - - -
JER lnN 1 1 1 - 1 1 1 1 1 1 1 1 1 - 1 1 1 1 1 1 
JES lnN 1 1 1 - 1 1 1 1 1 1 1 1 1 - 1 1 1 1 1 1 
Pu lnN 1 1 1 - 1 1 1 1 1 1 1 1 1 - 1 1 1 1 1 1 
trigger lnN 1.02 1.02 1.02 - 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 - 1.02 1.02 1.02 1.02 1.02 1.02 1.02
muveto lnN 1.005 1.005 1.005 - 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005 1.005 1.005 1.005 1.005 1.005 1.005
eleveto lnN 1.005 1.005 1.005 - 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005 1.005 1.005 1.005 1.005 1.005 1.005
scale shape 0.1 0.1 0.1 - - 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - - 0.1 0.1 0.1 0.1 0.1
#scalept shape 0.1 0.1 0.1 - - 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - - 0.1 0.1 0.1 0.1 0.1
smear shape 0.5 0.5 0.5 - - 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 - - 0.5 0.5 0.5 0.5 0.5
tqqpassCATXnorm rateParam pass_CATX tqq (@0*@1) tqqnormSF,tqqeffSF
tqqfailCATXnorm rateParam fail_CATX tqq (@0*(1.0-@1*TQQEFF)/(1.0-TQQEFF)) tqqnormSF,tqqeffSF
tqqnormSF extArg 1.0 [0.0,10.0]
tqqeffSF extArg 1.0 [0.0,10.0]
r1p0 flatParam
r2p0 flatParam
r0p1 flatParam
r1p1 flatParam
r2p1 flatParam
qcdeff flatParam
