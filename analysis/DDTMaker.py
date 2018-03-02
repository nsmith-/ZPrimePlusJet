import ROOT
from ROOT import *
import sys
import math
from array import array
import functools
from multiprocessing import Pool
import scipy
import os

input_folder = "/afs/cern.ch/user/c/cmantill/DAZSLE/DDT"
output_folder = "/afs/cern.ch/user/c/cmantill/DAZSLE/DDT/tmp"

rho_bins = [180, -7., -1.5]
pt_bins = [100, 200., 1200.]
z_bins = {
    "N2":[750, 0., 0.75],
    }
points_per_job = 10

fRhoRange=(7-1.5);
fPtRange =(1000-500);

fcorrGEN = ROOT.TF1("corrGEN","[0]+[1]*pow(x*[2],-[3])",200,3500);
fcorrRECO_cen = ROOT.TF1("corrRECO_cen","[0]+[1]*x+[2]*pow(x,2)+[3]*pow(x,3)+[4]*pow(x,4)+[5]*pow(x,5)",200,3500);
fcorrRECO_for = ROOT.TF1("corrRECO_for","[0]+[1]*x+[2]*pow(x,2)+[3]*pow(x,3)+[4]*pow(x,4)+[5]*pow(x,5)",200,3500);

def setupCorr():
    fcorrGEN.SetParameter(0,1.00626)
    fcorrGEN.SetParameter(1, -1.06161)
    fcorrGEN.SetParameter(2,0.0799900)
    fcorrGEN.SetParameter(3,1.20454)
    fcorrRECO_cen.SetParameter(0,1.09302)
    fcorrRECO_cen.SetParameter(1,-0.000150068)
    fcorrRECO_cen.SetParameter(2,3.44866e-07)
    fcorrRECO_cen.SetParameter(3,-2.68100e-10)
    fcorrRECO_cen.SetParameter(4,8.67440e-14)
    fcorrRECO_cen.SetParameter(5,-1.00114e-17)
    fcorrRECO_for.SetParameter(0,1.27212)
    fcorrRECO_for.SetParameter(1,-0.000571640)
    fcorrRECO_for.SetParameter(2,8.37289e-07)
    fcorrRECO_for.SetParameter(3,-5.20433e-10)
    fcorrRECO_for.SetParameter(4,1.45375e-13)
    fcorrRECO_for.SetParameter(5,-1.50389e-17)

def correct(iEta,iPt,iMass):
    genCorr  = 1.
    recoCorr = 1.
    genCorr =  fcorrGEN.Eval( iPt )
    if( abs(iEta)  < 1.3 ): recoCorr = fcorrRECO_cen.Eval( iPt )
    else: recoCorr = fcorrRECO_for.Eval( iPt )
    return iMass*recoCorr*genCorr

def compute_ddt(name, point, nPtBins, nRhoBins, H):
    DDT = TH2F(name, "", nRhoBins, -7.0, -2.0, nPtBins, 200, 800)
    DDT.SetStats(0)
    nXb = H.GetXaxis().GetNbins()
    nYb = H.GetYaxis().GetNbins()
    for x in range(nXb):
        for y in range(nYb):
            proj = H.ProjectionZ("H3"+str(x)+str(y),x+1,x+1,y+1,y+1)
            p = array('d', [point])
            q = array('d', [0.0]*len(p))
            proj.GetQuantiles(len(p), q, p)
            DDT.SetBinContent( x+1, y+1, q[0] );
    return DDT

class dataObj:
	def __init__(self,r,p,n,w):
		self.rho = r
		self.pt = p
		self.z = n
		self.weight = w
	def GetSortNearestCrit(self, o):
		Drho = math.fabs(self.rho - o.rho)/fRhoRange
		Dpt = math.fabs(self.pt - o.pt)/fPtRange
		return (Drho*Drho) + (Dpt*Dpt)
	def GetSortNearestGlobal(self, pt, rho):
		Drho = math.fabs(self.rho - rho)/fRhoRange
		Dpt = math.fabs(self.pt - pt)/fPtRange
		return (Drho*Drho) + (Dpt*Dpt)
def SortByNearest(p1): # Compare to global (recently set) parameter
	return p1.GetSortNearestGlobal(gpt, grho)
def SortByZ(p1):
	return p1.z

def do_ddt_smoothing(rho_pt_points, jet_type, var="N2", drho_cut=None, wp=0.05):
        setupCorr();
	lObjs = []
	for iSample in ["QCD"]:
                if 'phil' in jet_type:
                    lFile = TFile("root://eoscms//eos/cms/store/user/pharris/prod/%s_HT_v2.root"%iSample) 
                    lTree = lFile.Get("otree")
                else:
                    lFile = TFile.Open("/afs/cern.ch/user/c/cmantill/work/public/Bacon/CMSSW_7_4_7/src/inputs/ZPrimePlusJet/sklimming/skim%s/QCD.root"%jet_type)
                    lTree = lFile.Get("otree2")
		for i0 in xrange(lTree.GetEntriesFast()):
                    if(i0 % 100000 == 0): print float(i0)/float(lTree.GetEntriesFast())
                    lTree.GetEntry(i0)
                    if 'phil' in jet_type:
                        lPt = getattr(lTree,"lPt")
                        lEta = getattr(lTree,"lEta")
                        lMass = getattr(lTree,"lMass")
                        lW0 = getattr(lTree,"lW0")
                        lW1 = getattr(lTree,"lW1")
                        lN2 = getattr(lTree,"lN2")
                    else:
                        lPt = getattr(lTree,"%sPuppijet0_pt"%jet_type)
                        lEta = getattr(lTree,"%sPuppijet0_eta"%jet_type)
                        lMass = getattr(lTree,"%sPuppijet0_msd"%jet_type)
                        lN2 = getattr(lTree,"%sPuppijet0_N2sdb1"%jet_type)
                        lW0 = getattr(lTree,"puWeight")
                        lW1 = getattr(lTree,"scale1fb")
                    if(lPt  < 180): continue;
                    lMass = correct(lEta,lPt,lMass);
                    if(lMass < 30): continue;
                    pRho = 2.*math.log(lMass/lPt);
                    lSkip = 0
                    for rho_pt_point in rho_pt_points:
                        if (abs(pRho - rho_pt_point[0]) > fRhoRange/rho_bins[0]): 
                            lSkip = 1;
                    if lSkip == 1: continue
                    lWeight =  lW0*lW1;
                    lObjs.append(dataObj(pRho, lPt, lN2, lWeight))

	lObjs.sort(key=SortByZ)

        smoothed_ddt_results = []
        for rho_pt_point in rho_pt_points:
            smoothed_ddt_results.append(do_ddt_point(rho_pt_point[0], rho_pt_point[1], lObjs, drho_cut=drho_cut, wp=wp))

	return smoothed_ddt_results	

def do_ddt_point(iRho, iPt, iObjs, drho_cut=None, wp=0.05):
	# First loop: calculate sum of weights. 
	pTotWeight = 0.
        fRho = iRho; fPt = iPt;
	for p in iObjs:
            pDRho1 = abs(p.rho - fRho)/fRhoRange
            pDPt1 = abs(p.pt - fPt)/fPtRange
            pWeight = 1. / (0.001 + math.sqrt((pDRho1)**2 + (pDPt1)**2))
            if drho_cut:
                pWeight *= (pDRho < drho_cut)
            point_weight = p.weight * pWeight
            pTotWeight += point_weight
                
	# Second loop: determine index of points on either side of pTotWeight*wp - points already sorted by N2
	sum_weight = 0.
	last_weight = -1.
	last_point_index = -1
	for i, p in enumerate(iObjs):
            pWeight = 1. / (0.001 + math.sqrt((pDRho1)**2 + (pDPt1)**2))
            if drho_cut:
                pWeight *= (drho < drho_cut)
            point_weight = p.weight * pWeight
            sum_weight += point_weight
            print 'i ',i,' pt ',fPt,' rho ',fRho,' n2 ',p.z,' weight/tot ',sum_weight / pTotWeight
            if sum_weight / pTotWeight < wp:
                continue
            z = p.z
            last_point_index = i
            last_weight = point_weight
            break
	if last_point_index < 0:
            print "ERROR : Didn't find z value corresponding to WP {}".format(wp)
            sys.exit(1)

	pDelta = (sum_weight - wp * pTotWeight) / last_weight
	this_z = iObjs[last_point_index].z * pDelta + iObjs[last_point_index-1].z * (1. - pDelta)
	return [fRho, fPt, this_z]

def do_ddt_simple(jet_type, var="N2", wp=0.05):
        setupCorr();
	H3 = TH3F("H3", ";Jet #rho;Jet p_{T} (GeV)", rho_bins[0], rho_bins[1], rho_bins[2], pt_bins[0], pt_bins[1], pt_bins[2], z_bins[var][0], z_bins[var][1], z_bins[var][2])
	H31 = TH3F("H31", ";Jet #rho;Jet p_{T} (GeV)", rho_bins[0], rho_bins[1], rho_bins[2], pt_bins[0], pt_bins[1], pt_bins[2], z_bins[var][0], z_bins[var][1], z_bins[var][2])
	H32 = TH3F("H32", ";Jet #rho;Jet p_{T} (GeV)", rho_bins[0], rho_bins[1], rho_bins[2], pt_bins[0], pt_bins[1], pt_bins[2], z_bins[var][0], z_bins[var][1], z_bins[var][2])
	H33 = TH3F("H33", ";Jet #rho;Jet p_{T} (GeV)", rho_bins[0], rho_bins[1], rho_bins[2], pt_bins[0], pt_bins[1], pt_bins[2], z_bins[var][0], z_bins[var][1], z_bins[var][2])
	H3.SetStats(0)
	H31.SetStats(0)
	H32.SetStats(0)
	H33.SetStats(0)

	for iSample in ["QCD"]:
                if 'phil' in jet_type:
                    lFile = TFile("root://eoscms//eos/cms/store/user/pharris/prod/%s_HT_v2.root"%iSample)
                    lTree = lFile.Get("otree")
                else:
                    lFile = TFile.Open("/afs/cern.ch/user/c/cmantill/work/public/Bacon/CMSSW_7_4_7/src/inputs/ZPrimePlusJet/sklimming/skim%s/QCD.root"%jet_type)
                    lTree = lFile.Get("otree2")
		for i0 in xrange(lTree.GetEntriesFast()):
                        #if(i0 % 100000 == 0): print float(i0)/float(lTree.GetEntriesFast())
                        lTree.GetEntry(i0)
                        if 'phil' in jet_type:
                            lPt = getattr(lTree,"lPt")
                            lEta = getattr(lTree,"lEta")
                            lMass = getattr(lTree,"lMass")
                            lW0 = getattr(lTree,"lW0")
                            lW1 = getattr(lTree,"lW1")
                            lN2 = getattr(lTree,"lN2")
                        else:
                            lPt = getattr(lTree,"%sPuppijet0_pt"%jet_type)
                            lEta = getattr(lTree,"%sPuppijet0_eta"%jet_type)
                            lMass = getattr(lTree,"%sPuppijet0_msd"%jet_type)
                            lN2 = getattr(lTree,"%sPuppijet0_N2sdb1"%jet_type)
                            lW0 = getattr(lTree,"puWeight")
                            lW1 = getattr(lTree,"scale1fb")
                        if(lPt  < 180): continue;
                        lMass = correct(lEta,lPt,lMass);
                        if(lMass < 30): continue;
                        pRho = 2.*math.log(lMass/lPt);
                        lWeight =  lW0*lW1;
			H3.Fill(pRho, lPt, lN2, lWeight)
			if i0 % 3 == 0:
				H31.Fill(pRho, lPt, lN2, lWeight)
			if i0 % 3 == 1:
				H32.Fill(pRho, lPt, lN2, lWeight)
			if i0 % 3 == 2:
				H33.Fill(pRho, lPt, lN2, lWeight)
	ddt = compute_ddt("N2DDT", wp, pt_bins[0], rho_bins[0], H3)
	ddt1 = compute_ddt("N2DDT1", wp, pt_bins[0], rho_bins[0], H31)
	ddt2 = compute_ddt("N2DDT2", wp, pt_bins[0], rho_bins[0], H32)
	ddt3 = compute_ddt("N2DDT3", wp, pt_bins[0], rho_bins[0], H33)

        output_file = TFile("ddt_output.root", "RECREATE")
        ddt.Write()
        ddt1.Write()
        ddt2.Write()
        ddt3.Write()

	return ddt, ddt1, ddt2, ddt3

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser()
	parser.add_argument("--jet_type", type=str, default = "AK8",help="AK8 or CA15")
	parser.add_argument("--run", action="store_true",  default=False,help="Run locally")
	parser.add_argument("--crun", action="store_true", default=False,help="Run on HTCondor")
	parser.add_argument("--ncpu", type=int, default=4, help="Multiprocessing ncpus")
	parser.add_argument("--drho_cut", type=float, help="Add drho cut for smoothing")
	parser.add_argument("--smoothing_subjob", type=int, help="For batch, run a specific subjob")
	parser.add_argument("--var", type=str, default="N2", help="N2, dcsv, or dsub")
	parser.add_argument("--grid", action="store_true", default=False,help="Flag for running on batch")
        parser.add_argument("--merge",  action="store_true", default=False,help="Merge jobs")
        parser.add_argument("--imerge", type=int, help="smoothing number")
        parser.add_argument("--knn", action="store_true", default=False,help="knn from phil")
        parser.add_argument("--wp", type=float, default=0.05, help="N2 working point")
	args = parser.parse_args()

        rho_pt_points = []
        rho_points = []
        for rho_bin in xrange(rho_bins[0] + 1):
            rho = rho_bins[1] + rho_bin * (rho_bins[2] - rho_bins[1]) / rho_bins[0]
            rho_points.append((rho))
            for pt_bin in xrange(pt_bins[0] + 1):
                pt = pt_bins[1] + pt_bin * (pt_bins[2] - pt_bins[1]) / pt_bins[0]
                rho_pt_points.append((rho, pt))
        njobs = int(math.ceil(1. * len(rho_pt_points) / points_per_job))
        njobsknn = int(math.ceil(1. * len(rho_points)))
                  
        fWP = args.wp

	if args.grid:
            print 'NJOBS: %i'%njobs
            input_folder = "./"
            output_folder = "./"

	if args.run:
            print "running simple"
            ddt, ddt1, ddt2, ddt3 = do_ddt_simple(args.jet_type, args.var, fWP)
            
        if args.var == "N2":
            wp = fWP
        else:
            print "ERROR : No WP established for var {}, jet type {}".format(args.var, args.jet_type)
            
        if args.smoothing_subjob > -1:
            print 'job ',args.smoothing_subjob
            if args.knn:
                j = args.smoothing_subjob
                if 'AK8' in args.jet_type:
                    gROOT.LoadMacro("knnQuantile.C+")
                    if j < len(rho_points):
                        print 'iRho %f'%rho_points[j]
                        #knnQuantile(abs(rho_points[j]),"/afs/cern.ch/user/c/cmantill/work/public/Bacon/CMSSW_7_4_7/src/inputs/ZPrimePlusJet/sklimming/skimAK8/QCD.root","otree2")
                        knnQuantile(abs(rho_points[j]),float(wp),"/afs/cern.ch/user/c/cmantill/work/public/Bacon/CMSSW_7_4_7/src/inputs/ZPrimePlusJet/sklimming/skimAK82017/QCD.root","otree2")
                elif 'CA15' in args.jet_type:
                    gROOT.LoadMacro("knnQuantile.C+")
                    if j < len(rho_points):
                        print 'iRho %f'%rho_points[j]
                        knnQuantile(abs(rho_points[j]),float(wp),"/afs/cern.ch/user/c/cmantill/work/public/Bacon/CMSSW_7_4_7/src/inputs/ZPrimePlusJet/sklimming/skimCA15/QCD.root","otree2","CA15")
                else:
                    gROOT.LoadMacro("knnQuantile.C+")
                    if j < len(rho_points):
                        print 'iRho %f'%rho_points[j]
                        knnQuantile(abs(rho_points[j]))
            else:
                rho_pt_points_subjob = []
                for i in xrange(points_per_job):
                    j = args.smoothing_subjob*points_per_job + i
                    if j >= len(rho_pt_points): continue
                    rho_pt_points_subjob.append(rho_pt_points[j])
                print 'rho pt subjobs'
                print rho_pt_points_subjob
                print len(rho_pt_points_subjob)
                ddt_smooth_results = do_ddt_smoothing(rho_pt_points_subjob, args.jet_type, var=args.var, drho_cut=None)

        if args.smoothing_subjob > -1 and not args.knn:
            lOFile = TFile("N2DDT_%i.root"%args.smoothing_subjob, "RECREATE")
            lX = []; lY = []; lZ = [];
            for ddt in ddt_smooth_results:
                lX.append(ddt[0])
                lY.append(ddt[1])
                lZ.append(ddt[2])
            lGraph2D = TGraph2D(len(lX),array('d',lX),array('d',lY),array('d',lZ))
            lGraph2D.SetTitle("DDT_rho_pt_%i"%args.smoothing_subjob)
            lGraph2D.SetName ("DDT_rho_pt_%i"%args.smoothing_subjob)
            lGraph2D.Write();

        if args.crun:
            import random
            rand=int(random.random()*10000)
            submission_dir = "/afs/cern.ch/user/c/cmantill/DAZSLE/DDT/smoothing_%s/"%(str(rand)+args.jet_type)
            cwd = os.getcwd()
            alldir = cwd
            os.system("mkdir -pv %s"%submission_dir)
            os.chdir(submission_dir)

            if args.knn:
                for ijob in xrange(njobsknn):
                    dirs=os.getcwd().split("/")
                    job_script_path = "%s/run_csubjob_%s.sh"%(submission_dir,str(ijob))
                    job_script = open(job_script_path, 'w')
                    job_script.write("#!/bin/bash\n")
                    job_script.write('rm N2DDT*.root \n')
                    job_script.write('cd  /afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/tmp/CMSSW_7_4_7/src  \n')
                    job_script.write('eval `scramv1 runtime -sh`\n')
                    job_script.write('cd - \n')
                    job_script.write('cp /afs/cern.ch/user/c/cmantill/work/public/Bacon/CMSSW_7_4_7/src/2017/ZPrimePlusJet/analysis/knnQuantile*.C . \n')
                    command = "python %s/DDTMaker.py --grid --smoothing_subjob %s --jet_type %s --var %s --knn"%(cwd,str(ijob),str(args.jet_type), str(args.var))
                    job_script.write(command + "\n")
                    job_script.write('mv N2DDT*.root %s/ \n'%(submission_dir))
                    job_script.close()
                    os.system('chmod +x %s' % os.path.abspath(job_script.name))
                    os.system('bsub -q 8nh -o out.%%J %s' % (os.path.abspath(job_script.name)))
            else:
                rho_pt_strings = []
                for ijob in xrange(njobs):
                    job_rho_pt_strings = []
                    for ipoint in xrange(points_per_job):
                        i = ijob * points_per_job + ipoint
                        if i > len(rho_pt_points)-1: continue
                        job_rho_pt_strings.append(str(rho_pt_points[i][0]) + ":" + str(rho_pt_points[i][1]))
                        job_rho_pt_string = ",".join(job_rho_pt_strings)
                        rho_pt_strings.append(job_rho_pt_string)

                    dirs=os.getcwd().split("/")
                    job_script_path = "%s/run_csubjob_%s.sh"%(submission_dir,str(ijob))
                    job_script = open(job_script_path, 'w')
                    job_script.write("#!/bin/bash\n")
                    job_script.write('cd  /afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/tmp/CMSSW_7_4_7/src  \n')
                    job_script.write('eval `scramv1 runtime -sh`\n')
                    job_script.write('cd - \n')
                    command = "python %s/DDTMaker.py --grid --smoothing_subjob %s --jet_type %s --var %s"%(cwd,str(ijob),str(args.jet_type), str(args.var))
                    job_script.write(command + "\n")
                    job_script.write('mv N2DDT_%i.root %s/N2DDT_%i.root \n'%(ijob,submission_dir,ijob))
                    job_script.close()
                    os.system('chmod +x %s' % os.path.abspath(job_script.name))
                    os.system('bsub -q 8nh -o out.%%J %s' % (os.path.abspath(job_script.name)))

        if args.merge:
            lX = []; lY = []; lZ = [];
            fGraphs = [];
            submission_dir = "/afs/cern.ch/user/c/cmantill/DAZSLE/DDT/smoothing_%s/"%str(args.imerge)
            for ijob in xrange(njobs):
                lFile = TFile("%s/N2DDT_%i.root"%(submission_dir,ijob))
                for pGraph in lFile.GetListOfKeys():
                    pXs = pGraph.ReadObj().GetX()
                    pYs = pGraph.ReadObj().GetY()
                    pG = pGraph.ReadObj()
                    pG.Fit("pol5","Q","R",300,1200)
                    pF = pG.GetFunction("pol5")
                    pY = []
                    pZ = []
                    for i0 in range(pGraph.ReadObj().GetN()):
                        lX.append(float(pX)*-1.)
                        lY.append(pXs[i0])
                        lZ.append(pF.Eval(pXs[i0]))
                        pY.append(pXs[i0])
                        pZ.append(pF.Eval(pXs[i0]))
                    pGraph = r.TGraph(len(pY),array('d',pY),array('d',pZ))
                    fGraphs.append(pGraph)

            lOFile = r.TFile("Output.root","RECREATE")
            lGraph2D = r.TGraph2D(len(lX),array('d',lX),array('d',lY),array('d',lZ))
            lGraph2D.SetTitle("DDT_rho_pt")
            lGraph2D.SetName ("DDT_rho_pt")
            lGraph2D.Write()

            lN=180
            lH2D = r.TH2F("Rho2D","Rho2D",lN,-7,-1.5,lN,200,1200)
            lH2D.GetXaxis().SetTitle("#rho")
            lH2D.GetYaxis().SetTitle("p_{T} (GeV)")
            for i0 in range(lN+1):
                for i1 in range(lN+1):
                    print "Interpol:",i0,i1
                    lX = lH2D.GetXaxis().GetBinCenter(i0)
                    lY = lH2D.GetYaxis().GetBinCenter(i1)
                    if lY > 1180:
                        lY=1180
                    lH2D.SetBinContent(i0,i1,fGraphs[val(lX,fX)].Eval(lY))

            lH2D.Write()
            lH2D.Draw("colz")
            
