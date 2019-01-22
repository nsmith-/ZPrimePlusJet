Combination of datacard.tpl
imax 2 number of bins
jmax 5 number of processes minus 1
kmax 23 number of nuisance parameters
----------------------------------------------------------------------------------------------------------------------------------
shapes *              ch1_fail_CATX  base.root w_fail_CATX:$PROCESS_fail_CATX w_fail_CATX:$PROCESS_fail_CATX_$SYSTEMATIC
shapes qcd            ch1_fail_CATX  rhalphabase.root w_fail_CATX:$PROCESS_fail_CATX
shapes *              ch1_pass_CATX  base.root w_pass_CATX:$PROCESS_pass_CATX w_pass_CATX:$PROCESS_pass_CATX_$SYSTEMATIC
shapes qcd            ch1_pass_CATX  rhalphabase.root w_pass_CATX:$PROCESS_pass_CATX
----------------------------------------------------------------------------------------------------------------------------------
bin          ch1_pass_CATX  ch1_fail_CATX
observation  -1             -1           
----------------------------------------------------------------------------------------------------------------------------------
bin                                ch1_pass_CATX  ch1_pass_CATX  ch1_pass_CATX  ch1_pass_CATX  ch1_pass_CATX  ch1_pass_CATX  ch1_fail_CATX  ch1_fail_CATX  ch1_fail_CATX  ch1_fail_CATX  ch1_fail_CATX  ch1_fail_CATX
process                            hcc125         hqq125         zqq            wqq            qcd            tqq            hcc125         hqq125         zqq            wqq            qcd            tqq          
process                            0              1              2              3              4              5              0              1              2              3              4              5            
rate                               -1             -1             -1             -1             1              -1             -1             -1             -1             -1             1              -1           
-------------------------------------------------------------------------------------                                                       
bbeff                   lnN        1.1            1.1            -              -              -              -              1.1            1.1            -              -              -              -            
eleveto                 lnN        1.005          1.005          1.005          1.005          -              1.005          1.005          1.005          1.005          1.005          -              1.005        
hqq125pt                lnN        -              1.3            -              -              -              -              -              1.3            -              -              -              -            
hqq125ptShape           shape      -              1.0            -              -              -              -              -              1.0            -              -              -              -            
lumi                    lnN        1.025          1.025          1.025          1.025          -              -              1.025          1.025          1.025          1.025          -              -            
muveto                  lnN        1.005          1.005          1.005          1.005          -              1.005          1.005          1.005          1.005          1.005          -              1.005        
scale                   shape      0.1            0.1            0.1            0.1            -              -              0.1            0.1            0.1            0.1            -              -            
smear                   shape      0.5            0.5            0.5            0.5            -              -              0.5            0.5            0.5            0.5            -              -            
trigger                 lnN        1.02           1.02           1.02           1.02           -              1.02           1.02           1.02           1.02           1.02           -              1.02         
veff                    lnN        1.2            1.2            1.2            1.2            -              -              1.2            1.2            1.2            1.2            -              -            
wznormEW                lnN        -              -              -              1.05           -              -              -              -              -              1.05           -              -            
znormEW                 lnN        -              -              1.15           1.15           -              -              -              -              1.15           1.15           -              -            
znormQ                  lnN        -              -              1.1            1.1            -              -              -              -              1.1            1.1            -              -            
tqqfailCATXnorm  rateParam ch1_fail_CATX tqq (@0*(1.0-@1*TQQEFF)/(1.0-TQQEFF)) tqqnormSF,tqqeffSF  
tqqpassCATXnorm  rateParam ch1_pass_CATX tqq (@0*@1) tqqnormSF,tqqeffSF  
tqqnormSF extArg 1.0 [0.0,10.0]
tqqeffSF extArg 1.0 [0.0,10.0]
