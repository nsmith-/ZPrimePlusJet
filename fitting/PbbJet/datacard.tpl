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
bin pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX
process tthqq125 whqq125 hqq125 zhqq125 vbfhqq125 zqq wqq qcd tqq tthqq125 whqq125 hqq125 zhqq125 vbfhqq125 zqq wqq qcd tqq 
process -4 -3 -2 -1 0 1 2 3 4 -4 -3 -2 -1 0 1 2 3 4 
rate -1 -1 -1 -1 -1 -1 -1 1.0 -1 -1 -1 -1 -1 -1 -1 -1 1.0 -1 
----------------------------------------------------------------------------------------------------------------------------------
#lumi_13TeV lnN 1.026 1.026 1.026 1.026 1.026 1.026 1.026 - 1.026 1.026 1.026 1.026 1.026 1.026 1.026 1.026 - 1.026
lumi lnN 1.026 1.026 1.026 1.026 1.026 1.026 1.026 - 1.026 1.026 1.026 1.026 1.026 1.026 1.026 1.026 - 1.026
#CMS_eff_v lnN 1.2 1.2 1.2 1.2 1.2 1.2 1.2 - - 1.2 1.2 1.2 1.2 1.2 1.2 1.2 - -
#CMS_eff_bb lnN 1.1 1.1 1.1 1.1 1.1 - - - - 1.1 1.1 1.1 1.1 1.1 - - - -
veff lnN 1.2 1.2 1.2 1.2 1.2 1.2 1.2 - - 1.2 1.2 1.2 1.2 1.2 1.2 1.2 - -
bbeff lnN 1.1 1.1 1.1 1.1 1.1 - - - - 1.1 1.1 1.1 1.1 1.1 - - - -
znormQ lnN - - - - - 1.1 1.1 - - - - - - - 1.1 1.1 - -
#znormQ lnN - - - - - 1.1 - - - - - - - - 1.1 - - -
#wnormQ lnN - - - - - - 1.1 - - - - - - - - 1.1 - -
znormEWCATX lnN - - - - - 1.15 1.15 - - - - - - - 1.15 1.15 - -
#znormEWCATX lnN - - - - - 1.15 - - - - - - - - 1.15 - - -
#wnormEWCATX lnN - - - - - - 1.15 - - - - - - - - 1.15 - -
wznormEWCATX lnN - - - - - - 1.05 - - - - - - - - 1.05 - -
#CMS_scale_j lnN 1 1 1 1 1 1 1 - 1 1 1 1 1 1 1 1 - 1
#CMS_res_j lnN 1 1 1 1 1 1 1 - 1 1 1 1 1 1 1 1 - 1
JER lnN 1 1 1 1 1 1 1 - 1 1 1 1 1 1 1 1 - 1
JES lnN 1 1 1 1 1 1 1 - 1 1 1 1 1 1 1 1 - 1
trigger shape 1 1 1 1 1 1 1 - 1 1 1 1 1 1 1 1 - 1
muveto lnN 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005
eleveto lnN 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005
scale shape 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - - 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - -
#scalept shape 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - - 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - -
smear shape 0.5 0.5 0.5 0.5 0.5 0.5 0.5 - - 0.5 0.5 0.5 0.5 0.5 0.5 0.5 - -
tqqpassCATXnorm rateParam pass_CATX tqq (@0*@1) tqqnormSF,tqqeffSF
tqqfailCATXnorm rateParam fail_CATX tqq (@0*(1.0-@1*TQQEFF)/(1.0-TQQEFF)) tqqnormSF,tqqeffSF
#tqqfailCATXnorm rateParam fail_CATX tqq (@0*(1.0-@1*5.523909e-02)/(1.0-5.523909e-02)) tqqnormSF,tqqeffSF
tqqnormSF extArg 1.0 [0.0,10.0]
tqqeffSF extArg 1.0 [0.0,10.0]
r1p0 flatParam
r2p0 flatParam
r0p1 flatParam
r1p1 flatParam
r2p1 flatParam
qcdeff flatParam
