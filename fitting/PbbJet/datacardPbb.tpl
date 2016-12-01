imax 2
jmax *
kmax *
---------------
shapes *    * base.root   w_$CHANNEL:$PROCESS_$CHANNEL            w_$CHANNEL:$PROCESS_$CHANNEL_$SYSTEMATIC
shapes qcd  * ralphabase.root w_$CHANNEL:$PROCESS_$CHANNEL 
---------------
bin          pass_CATX fail_CATX
observation -1         -1
------------------------------
bin          pass_CATX	pass_CATX  pass_CATX pass_CATX pass_CATX fail_CATX  fail_CATX  fail_CATX	fail_CATX   fail_CATX   
process      pqq_CATY	wqq        zqq	  tqq   qcd       pqq_CATY	  wqq        zqq	tqq   qcd  
process      0		1	   2   	     3   4      0	  1	     2		3 4
rate         -1		-1         -1  	-1     1         -1	  -1	-1     -1		1
--------------------------------
lumi    lnN   1.05      1.05	1.05	- -	    1.05	  1.05	     1.05	- -
#scale   shape 0.2	0.2     0.2     -  -         0.2		  0.2        0.2	- -
#smear   shape -		1.0 	1.0     -   -        -		  1.0	     1.0	- -
veff_unc    lnN   0.8	0.8	0.8     -   -        1.012	  1.012	     1.012	- -
znorm   lnN   -		1.2 	1.2     -   -        -		  1.2	     1.2	- -
-------------------------------
qcdeff  flatParam
p0r0  flatParam
p1r0  flatParam
p2r0  flatParam
p0r1  flatParam
p1r1  flatParam
p2r1  flatParam
