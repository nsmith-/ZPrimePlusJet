#!/usr/bin/env python
# -----------------------------------------------------------------------------
#  File:        train.py
#  Description: Example of Random Grid Search to find the results of an
#               ensemble cuts. 
#  Created:     10-Jan-2015 Harrison B. Prosper and Sezen Sekmen
# -----------------------------------------------------------------------------
import os, sys, re
from rgsutil import *
from string import *
from ROOT import *
# -----------------------------------------------------------------------------
def main():
    print "="*80
    print "\t=== Example 0 - One-Sided Cuts ==="
    print "="*80

    # ---------------------------------------------------------------------
    # Load the RGS shared library and check that the various input files
    # exist.
    # ---------------------------------------------------------------------
    if gSystem.Load("libRGS") < 0:
        error("unable to load libRGS")

    # Name of file containing cut definitions
    # Format of file:
    #   variable-name  cut-type (>, <, <>, |>, |<, ==)
    varfilename = "rgs.cuts"
    if not os.path.exists(varfilename):
        error("unable to open variables file %s" % varfilename)

    # Name of signal file
    #sigfilename = "/eos/uscms/store/user/lpchbb/zprimebits-v11.05/sklim-Nov7/GluGluHToBB_M125_13TeV_powheg_pythia8_1000pb_weighted.root"
    sigfilename = "GluGluHToBB_M125_13TeV_powheg_pythia8_1000pb_weighted.root"
    if not os.path.exists(sigfilename):
        error("unable to open signal file %s" % sigfilename)

    # Name of background file        
    #bkgfilename = "/eos/uscms/store/user/lpchbb/zprimebits-v11.05/sklim-Nov7/TTbar_madgraphMLM_1000pb_weighted.root"
    bkgfilename = "TTbar_madgraphMLM_1000pb_weighted.root"
    if not os.path.exists(bkgfilename):
        error("unable to open background file %s" % bkgfilename)

    # ---------------------------------------------------------------------
    #  Create RGS object
    #  
    #   The file (cutdatafilename) of cut-points is usually a signal file,
    #   which ideally differs from the signal file on which the RGS
    #   algorithm is run.
    # ---------------------------------------------------------------------
    cutdatafilename = sigfilename
    start      = 0           # start row 
    maxcuts    = 1000        # maximum number of cut-points to consider
    treename   = "otree"  # name of Root tree 
    weightname = "scale1fb"    # name of event weight variable
    
    rgs = RGS(cutdatafilename, start, maxcuts, treename, weightname)

    # ---------------------------------------------------------------------
    #  Add signal and background data to RGS object.
    #  Weight each event using the value in the field weightname, if
    #  present.
    #  NB: We asssume all files are of the same format.
    # ---------------------------------------------------------------------
    start    = 0 #  start row
    numrows  =-1 #  scan all the data from the files
    # The last (optional) argument is a string, which, if given, will be
    # appended to the "count" and "fraction" variables. The "count" variable
    # contains the number of events that pass per cut-point, while "fraction"
    # is count / total, where total is the total number of events per file.
    # If no string is given, the default is to append an integer to the
    # "count" and "fraction" variables, starting at 0, in the order in which
    # the files are added to the RGS object.
    rgs.add(bkgfilename, start, numrows, "_b")
    rgs.add(sigfilename, start, numrows, "_s")

    # ---------------------------------------------------------------------	
    #  Run RGS and write out results
    # ---------------------------------------------------------------------	    
    rgs.run(varfilename)

    # Write to a root file
    rgsfilename = "%s_train2d.root" % nameonly(varfilename)
    rgs.save(rgsfilename)

    # Write to a text file
    rgsfilename = "%s_train2d.txt" % nameonly(varfilename)
    rgs.save(rgsfilename)    
# -----------------------------------------------------------------------------
try:
    main()
except KeyboardInterrupt:
    print "\tciao!\n"



