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
process      zqq100	wqq        zqq	  tqq   qcd       zqq100	  wqq        zqq	tqq   qcd  
process      0		1	   2   	     3   4      0	  1	     2		3 4
rate         -1		-1         -1  	-1     1         -1	  -1	-1     -1		1
--------------------------------
lumi    lnN   1.05      1.05	1.05	- -	    1.05	  1.05	     1.05	- -
#scale   shape 0.2	0.2     0.2     -  -         0.2		  0.2        0.2	- -
#smear   shape -		1.0 	1.0     -   -        -		  1.0	     1.0	- -
veff    lnN   0.8	0.8 	0.8     -   -        1.012	  1.012	     1.012	- -
znorm   lnN   -		1.2 	1.2     -   -        -		  1.2	     1.2	- -
-------------------------------
qcdeff  flatParam
p1      flatParam
r0      flatParam
r1      flatParam
pr11     flatParam
pr12     flatParam