Combination of datacard_novbf.tpl
imax 2 number of bins
jmax * number of processes minus 1
kmax * number of nuisance parameters
----------------------------------------------------------------------------------------------------------------------------------
shapes *              fail_CATX  base.root w_fail_CATX:$PROCESS_fail_CATX w_fail_CATX:$PROCESS_fail_CATX_$SYSTEMATIC
shapes qcd            fail_CATX  ralphabase.root w_fail_CATX:$PROCESS_fail_CATX
shapes *              pass_CATX  base.root w_pass_CATX:$PROCESS_pass_CATX w_pass_CATX:$PROCESS_pass_CATX_$SYSTEMATIC
shapes qcd            pass_CATX  ralphabase.root w_pass_CATX:$PROCESS_pass_CATX
----------------------------------------------------------------------------------------------------------------------------------
bin          pass_CATX  fail_CATX
observation  -1.0           -1.0         
----------------------------------------------------------------------------------------------------------------------------------
bin                             pass_CATX  pass_CATX  pass_CATX  pass_CATX  pass_CATX  pass_CATX  pass_CATX  pass_CATX  pass_CATX  fail_CATX  fail_CATX  fail_CATX  fail_CATX  fail_CATX  fail_CATX  fail_CATX  fail_CATX  fail_CATX
process                         wmhqq125       wphqq125       hqq125         tthqq125       zhqq125        zqq            wqq            qcd            tqq            wmhqq125       wphqq125       hqq125         tthqq125       zhqq125        zqq            wqq            qcd            tqq          
process                         -4             -3             -2             -1             0              1              2              3              4              -4             -3             -2             -1             0              1              2              3              4            
rate                            -1             -1             -1             -1             -1             -1             -1             1.0000         -1             -1             -1             -1             -1             -1             -1             -1             1.0000         -1           
----------------------------------------------------------------------------------------------------------------------------------
lumi                    lnN     1.05           1.05           1.05           1.05           1.05           1.05           1.05           -              -              1.05           1.05           1.05           1.05           1.05           1.05           1.05           -              -            
veff_unc                lnN     0.8            0.8            0.8            0.8            0.8            0.8            0.8            -              -              1.012          1.012          1.012          1.012          1.012          1.012          1.012          -              -            
znorm                   lnN     -              -              -              -              -              1.2            -              -              -              -              -              -              -              -              1.2            -              -              -            
#scale   shape 0.2	0.2     0.2     -  -         0.2      		       0.2        0.2		   - -
#smear   shape -		1.0 	1.0     -   -        -		       		    1.0		        1.0	- -
r1p0  flatParam
r2p0  flatParam
r0p1  flatParam
r1p1  flatParam
r2p1  flatParam
r2p2  flatParam
r0p2  flatParam
qcdeff        flatParam
