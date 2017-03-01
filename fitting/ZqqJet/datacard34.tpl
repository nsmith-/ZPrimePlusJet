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
scale   shape 0.2	0.2     0.2     -  -         0.2	0.2        0.2	- -
smear   shape 1.0		1.0 	1.0     -   -        1.0		  1.0	     1.0	- -
veff    lnN   0.95	0.95 	0.95    -   -        1.003	  1.003	     1.003	- -
znormQ  lnN   1.05	1.05 	1.05     -   -        1.05    1.05	     1.05	- -
znormE  lnN   -		1.05 	1.05     -   -        -		  1.05	     1.05	- -
jecs    lnN  1.02   1.02    1.02   1.02  -   1.02   1.02    1.02   1.02  - 
trigger lnN  1.02   1.02    1.02   1.02  -   1.02   1.02    1.02   1.02  - 
muveto  lnN  1.005  1.005   1.005  1.005 -   1.005  1.005   1.005  1.005 - 
eveto   lnN  1.005  1.005   1.005  1.005 -   1.005  1.005   1.005  1.005 -  
ttnormSF lnN  -      -       -      1.05   -   -      -       -      1.05   - 
tteffSF  lnN  -      -       -      1.1   -   -      -       -      1.1   - 
-------------------------------
qcdeff  flatParam
p0r0  flatParam
p1r0  flatParam
p2r0  flatParam
p3r0  flatParam
p0r1  flatParam
p1r1  flatParam
p2r1  flatParam
p3r1  flatParam
p0r2  flatParam
p1r2  flatParam
p2r2  flatParam
p3r2  flatParam
p0r3  flatParam
p1r3  flatParam
p2r3  flatParam
p3r3  flatParam
p0r4  flatParam
p1r4  flatParam
p2r4  flatParam
p3r4  flatParam