Combination of datacard.tpl
imax 2 number of bins
jmax * number of processes minus 1
kmax * number of nuisance parameters
----------------------------------------------------------------------------------------------------------------------------------
shapes * fail_CATX base.root w_fail_CATX:$PROCESS_fail_CATX w_fail_CATX:$PROCESS_fail_CATX_$SYSTEMATIC
shapes qcd fail_CATX ralphabase.root w_fail_CATX:$PROCESS_fail_CATX
shapes * pass_CATX base.root w_pass_CATX:$PROCESS_pass_CATX w_pass_CATX:$PROCESS_pass_CATX_$SYSTEMATIC
shapes qcd pass_CATX ralphabase.root w_pass_CATX:$PROCESS_pass_CATX
----------------------------------------------------------------------------------------------------------------------------------
bin pass_CATX fail_CATX
observation -1.0 -1.0 
----------------------------------------------------------------------------------------------------------------------------------
bin pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX
process zqq wqq tthqq125 whqq125 hqq125 zhqq125 vbfhqq125 qcd tqq  zqq wqq tthqq125 whqq125 hqq125 zhqq125 vbfhqq125 qcd tqq
process -1 0 1 2 3 4 5 6 7   -1 0 1 2 3 4 5 6 7 
rate -1 -1 -1 -1 -1 -1 -1 1.0 -1 -1 -1 -1 -1 -1 -1 -1 1.0 -1 
----------------------------------------------------------------------------------------------------------------------------------
lumi lnN 1.05 1.05 1.05 1.05 1.05 1.05 1.05 - 1.05 1.05 1.05 1.05 1.05 1.05 1.05 1.05 - 1.05
veff lnN 1.2 1.2 1.2 1.2 1.2 1.2 1.2 - - 1.2 1.2 1.2 1.2 1.2 1.2 1.2 - -
bbeff lnN 1.01 - 1.01 1.01 1.01 1.01 1.01 - - 1.01 - 1.01 1.01 1.01 1.01 1.01 - -
znormQ lnN 1.1 1.1  - - -  - - - - 1.1 1.1 - - -  - - - - 
znormEW lnN 1.15 1.15  - - -  - - - - 1.15 1.15 - - -  - - - -
jes lnN 1.02 1.02 1.02 1.02 1.02 1.02 1.02 - 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 - 1.02
jer lnN 1.02 1.02 1.02 1.02 1.02 1.02 1.02 - 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 - 1.02
trigger lnN 1.02 1.02 1.02 1.02 1.02 1.02 1.02 - 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 - 1.02
muveto lnN 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005
eleveto lnN 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005
scale shape 1.0 1.0 - - - - - - 1.0 1.0 - - - - - -
smear shape  1.0 1.0 - - - - - - 1.0 1.0 - - - - - -
#tqqnormSF lnN - - - - - - - - 1.06 - - - - - - - - 1.06
#tqqeffSF lnN - - - - - - - - 1.29 - - - - - - - - 0.9935
tqqpassCATXnorm rateParam pass_CATX tqq (@0*@1) tqqnormSF,tqqeffSF
tqqfailCATXnorm rateParam fail_CATX tqq (@0*(1.0-@1*0.0845)/(1.0-0.0845)) tqqnormSF,tqqeffSF
tqqnormSF extArg 1.0 [0.0,10.0]
tqqeffSF extArg 1.0 [0.0,10.0]
r1p0 flatParam
r2p0 flatParam
r0p1 flatParam
r1p1 flatParam
r2p1 flatParam
r0p2 flatParam
r1p2 flatParam
r2p2 flatParam
r3p2 flatParam
r3p1 flatParam
r3p0 flatParam
r0p3 flatParam
r1p3 flatParam
r2p3 flatParam
r3p3 flatParam
qcdeff flatParam
