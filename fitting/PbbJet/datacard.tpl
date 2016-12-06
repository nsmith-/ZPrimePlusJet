Combination of datacard.tpl
imax 2 number of bins
jmax 9 number of processes minus 1
kmax 3 number of nuisance parameters
----------------------------------------------------------------------------------------------------------------------------------
shapes *              ch1_fail_CATX  base.root w_fail_CATX:$PROCESS_fail_CATX w_fail_CATX:$PROCESS_fail_CATX_$SYSTEMATIC
shapes qcd            ch1_fail_CATX  ralphabase.root w_fail_CATX:$PROCESS_fail_CATX
shapes *              ch1_pass_CATX  base.root w_pass_CATX:$PROCESS_pass_CATX w_pass_CATX:$PROCESS_pass_CATX_$SYSTEMATIC
shapes qcd            ch1_pass_CATX  ralphabase.root w_pass_CATX:$PROCESS_pass_CATX
----------------------------------------------------------------------------------------------------------------------------------
bin          ch1_pass_CATX  ch1_fail_CATX
observation  -1.0           -1.0         
----------------------------------------------------------------------------------------------------------------------------------
bin                             ch1_pass_CATX  ch1_pass_CATX  ch1_pass_CATX  ch1_pass_CATX  ch1_pass_CATX  ch1_pass_CATX  ch1_pass_CATX  ch1_pass_CATX  ch1_pass_CATX  ch1_pass_CATX  ch1_fail_CATX  ch1_fail_CATX  ch1_fail_CATX  ch1_fail_CATX  ch1_fail_CATX  ch1_fail_CATX  ch1_fail_CATX  ch1_fail_CATX  ch1_fail_CATX  ch1_fail_CATX
process                         wmhqq125       wphqq125       hqq125         tthqq125       zhqq125        vbfhqq125      zqq            wqq            qcd            tqq            wmhqq125       wphqq125       hqq125         tthqq125       zhqq125        vbfhqq125      zqq            wqq            qcd            tqq          
process                         -5             -4             -3             -2             -1             0              1              2              3              4              -5             -4             -3             -2             -1             0              1              2              3              4            
rate                            -1             -1             -1             -1             -1             -1             -1             -1             1.0000         -1             -1             -1             -1             -1             -1             -1             -1             -1             1.0000         -1           
----------------------------------------------------------------------------------------------------------------------------------
lumi                    lnN     1.05           1.05           1.05           1.05           1.05           1.05           1.05           1.05           -              -              1.05           1.05           1.05           1.05           1.05           1.05           1.05           1.05           -              -            
veff_unc                lnN     0.8            0.8            0.8            0.8            0.8            0.8            0.8            0.8            -              -              1.012          1.012          1.012          1.012          1.012          1.012          1.012          1.012          -              -            
znorm                   lnN     -              -              -              -              -              -              1.2            -              -              -              -              -              -              -              -              -              1.2            -              -              -            
#scale   shape 0.2	0.2     0.2     -  -         0.2      		       0.2        0.2		   - -
#smear   shape -		1.0 	1.0     -   -        -		       		    1.0		        1.0	- -
p0r0          flatParam
p0r1          flatParam
p1r1          flatParam
p1r0          flatParam
p2r0          flatParam
p2r1          flatParam
qcdeff        flatParam
