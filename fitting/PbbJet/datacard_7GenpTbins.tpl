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
bin pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX pass_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX fail_CATX
process tthqq125_GenpT1 whqq125_GenpT1 hqq125_GenpT1 zhqq125_GenpT1 vbfhqq125_GenpT1 tthqq125_GenpT2 whqq125_GenpT2 hqq125_GenpT2 zhqq125_GenpT2 vbfhqq125_GenpT2 tthqq125_GenpT3 whqq125_GenpT3 hqq125_GenpT3 zhqq125_GenpT3 vbfhqq125_GenpT3 tthqq125_GenpT4 whqq125_GenpT4 hqq125_GenpT4 zhqq125_GenpT4 vbfhqq125_GenpT4 tthqq125_GenpT5 whqq125_GenpT5 hqq125_GenpT5 zhqq125_GenpT5 vbfhqq125_GenpT5 tthqq125_GenpT6 whqq125_GenpT6 hqq125_GenpT6 zhqq125_GenpT6 vbfhqq125_GenpT6 tthqq125_GenpT7 whqq125_GenpT7 hqq125_GenpT7 zhqq125_GenpT7 vbfhqq125_GenpT7 zqq wqq qcd tqq tthqq125_GenpT1 whqq125_GenpT1 hqq125_GenpT1 zhqq125_GenpT1 vbfhqq125_GenpT1 tthqq125_GenpT2 whqq125_GenpT2 hqq125_GenpT2 zhqq125_GenpT2 vbfhqq125_GenpT2 tthqq125_GenpT3 whqq125_GenpT3 hqq125_GenpT3 zhqq125_GenpT3 vbfhqq125_GenpT3 tthqq125_GenpT4 whqq125_GenpT4 hqq125_GenpT4 zhqq125_GenpT4 vbfhqq125_GenpT4 tthqq125_GenpT5 whqq125_GenpT5 hqq125_GenpT5 zhqq125_GenpT5 vbfhqq125_GenpT5 tthqq125_GenpT6 whqq125_GenpT6 hqq125_GenpT6 zhqq125_GenpT6 vbfhqq125_GenpT6 tthqq125_GenpT7 whqq125_GenpT7 hqq125_GenpT7 zhqq125_GenpT7 vbfhqq125_GenpT7 zqq wqq qcd tqq 
process -34 -33 -32 -31 -30 -29 -28 -27 -26 -25 -24 -23 -22 -21 -20 -19 -18 -17 -16 -15 -14 -13 -12 -11 -10 -9 -8 -7 -6 -5 -4 -3 -2 -1 0 1 2 3 4 -34 -33 -32 -31 -30 -29 -28 -27 -26 -25 -24 -23 -22 -21 -20 -19 -18 -17 -16 -15 -14 -13 -12 -11 -10 -9 -8 -7 -6 -5 -4 -3 -2 -1 0 1 2 3 4 
rate -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 1.0 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 1.0 -1 
----------------------------------------------------------------------------------------------------------------------------------
#lumi_13TeV lnN 1.025 1.025 1.025 1.025 1.025 1.025 1.025 - 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 - 1.025
lumi lnN 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 - - 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 1.025 - -
hqq125pt lnN - - 1.30 - - - - 1.30 - - - - 1.30 - - - - 1.30 - - - - 1.30 - - - - 1.30 - - - - 1.30 - - - - - - - - 1.30 - - - - 1.30 - - - - 1.30 - - - - 1.30 - - - - 1.30 - - - - 1.30 - - - - 1.30 - - - - - -
hqq125ptShape shape - - 1 - - - - 1 - - - - 1 - - - - 1 - - - - 1 - - - - 1 - - - - 1 - - - - - - - - 1 - - - - 1 - - - - 1 - - - - 1 - - - - 1 - - - - 1 - - - - 1 - - - - - -
#CMS_eff_v lnN 1.2 1.2 1.2 1.2 1.2 1.2 1.2 - - 1.2 1.2 1.2 1.2 1.2 1.2 1.2 - -
#CMS_eff_bb lnN 1.1 1.1 1.1 1.1 1.1 - - - - 1.1 1.1 1.1 1.1 1.1 - - - -
veff lnN 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 - - 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 1.2 - -
bbeff lnN 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 - - - - 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 1.1 - - - -
znormQ lnN - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 1.1 1.1 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 1.1 1.1 - -
#znormQ lnN - - - - - 1.1 - - - - - - - - 1.1 - - -
#wnormQ lnN - - - - - - 1.1 - - - - - - - - 1.1 - -
znormEW lnN - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 1.15 1.15 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 1.15 1.15 - -
wznormEW lnN - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 1.05 - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 1.05 - -
#CMS_scale_j lnN 1 1 1 1 1 1 1 - 1 1 1 1 1 1 1 1 - 1
#CMS_res_j lnN 1 1 1 1 1 1 1 - 1 1 1 1 1 1 1 1 - 1
JER lnN 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 - 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 - 1
JES lnN 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 - 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 - 1
Pu lnN 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 - 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 - 1
#trigger shape 1 1 1 1 1 1 1 - 1 1 1 1 1 1 1 1 - 1
trigger lnN 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 - 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 1.02 - 1.02
muveto lnN 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005
eleveto lnN 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 1.005 - 1.005
scale shape 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - - 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - -
#scalept shape 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - - 0.1 0.1 0.1 0.1 0.1 0.1 0.1 - -
smear shape 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 - - 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 0.5 - -
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
#hbb rateParam 	    * tthqq125 $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/sm_br_yr4.root:br
#hbb rateParam 	    * whqq125 $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/sm_br_yr4.root:br
#hbb rateParam 	    * hqq125 $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/sm_br_yr4.root:br
#hbb rateParam 	    * zhqq125 $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/sm_br_yr4.root:br
#hbb rateParam 	    * vbfhqq125 $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/sm_br_yr4.root:br
#ttH_13TeV rateParam * tthqq125 $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/sm_yr4_13TeV.root:xs_13TeV 
#WH_13TeV rateParam * whqq125 $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/sm_yr4_13TeV.root:xs_13TeV 
#ggH_13TeV rateParam * hqq125 $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/sm_yr4_13TeV.root:xs_13TeV 
#ZH_13TeV rateParam * zhqq125 $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/sm_yr4_13TeV.root:xs_13TeV 
#vbfH_13TeV rateParam * vbfhqq125 $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit/data/lhc-hxswg/sm/sm_yr4_13TeV.root:xs_13TeV 
