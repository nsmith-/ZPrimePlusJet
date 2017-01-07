Combination of datacard.tpl
imax 2 number of bins
jmax * number of processes minus 1
kmax * number of nuisance parameters
----------------------------------------------------------------------------------------------------------------------------------
shapes * pass_muonCR hist_1DZbb_muonCR.root $PROCESS_pass $PROCESS_pass_$SYSTEMATIC
shapes * fail_muonCR hist_1DZbb_muonCR.root $PROCESS_fail $PROCESS_fail_$SYSTEMATIC
----------------------------------------------------------------------------------------------------------------------------------
bin fail_muonCR pass_muonCR
observation -1.0 -1.0 
----------------------------------------------------------------------------------------------------------------------------------
bin fail_muonCR fail_muonCR fail_muonCR fail_muonCR fail_muonCR fail_muonCR fail_muonCR fail_muonCR fail_muonCR fail_muonCR pass_muonCR pass_muonCR pass_muonCR pass_muonCR pass_muonCR pass_muonCR
process tthqq125 whqq125 zhqq125 vbfhqq125 zqq wqq qcd tqq vvqq stqq tthqq125 hqq125 zqq qcd tqq stqq
process -4 -3 -1 0 1 2 3 4 5 6 -4 -2 1 3 4 5
rate -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1
----------------------------------------------------------------------------------------------------------------------------------
lumi lnN 1.0001 - - - - - - - - - - - - - - - -
tqqpassnorm rateParam pass_muonCR tqq (@0*@1/0.084) tqqnorm,tqqeff
tqqfailnorm rateParam fail_muonCR tqq (@0*(1.0-@1)/(1.0-0.084)) tqqnorm,tqqeff
tqqnorm extArg 1.0 [0.0,10.0]
tqqeff extArg 0.084 [0.0,1.0]
