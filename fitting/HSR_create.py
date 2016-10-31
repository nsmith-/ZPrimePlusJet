import os
import math
from array import array
import optparse
import ROOT
from ROOT import *
import scipy, copy

def quick2dplot(File, tree, plot, var, var2, Cut, Weight): # Same as above, but 2D plotter
        temp = plot.Clone("temp")
        chain = ROOT.TChain(tree)
        chain.Add(File)
        chain.Draw(var2+":"+var+">>"+"temp", "("+Weight+")*("+Cut+")", "goff")
        plot.GetYaxis().SetTitleOffset(1.45)
        plot.Add(temp)


mass=[125]#800,900,1000,1200,1400,1600,1800,2000,2500, 3000, 4500]
VAR = "AK8Puppijet0_msd"


outfile=ROOT.TFile("base_1D.root", "recreate");


lumi =12891.
SF_tau21 =1


sklimpath="/eos/uscms/store/user/lpchbb/ggHsample_V11/sklim-v0-28Oct/"


data_file = TFile(sklimpath+"QCD.root")
data_tree= data_file.Get("otree")

#triggerpassbb==1
presel = "AK8Puppijet0_pt>500"
#triggerpassbb==1&&jet2pmass>105&jet2pmass<135&jet2tau21<0.6&jet2bbtag>0.6&vtype==-1&jet2pt>200&json==1&jet1pt>200&etadiff<1.3&jet1tau21<0.6&dijetmass_corr>800&jet2ID==1&jet1ID==1"
tag = presel + "&(AK8CHSjet0_doublecsv>0.9)"
antitag = presel + "&AK8CHSjet0_doublecsv<0.9"

#quick2dplot(File, tree, plot, var, var2, Cut, Weight:


data_obs_pass= TH2F("data_obs_pass","data_obs_pass",60,50,350,1, 500, 3000)
data_obs_fail= TH2F("data_obs_fail","data_obs_fail",60,50,350,1, 500, 3000)
quick2dplot(sklimpath+"QCD.root", "otree", data_obs_pass, "AK8Puppijet0_msd","AK8Puppijet0_pt",tag,"1")
quick2dplot(sklimpath+"QCD.root", "otree", data_obs_fail, "AK8Puppijet0_msd","AK8Puppijet0_pt",antitag,"1")

qcd_pass= TH2F("qcd_pass","qcd_pass",60,50,350,1, 500, 3000)
qcd_fail= TH2F("qcd_fail","qcd_fail",60,50,350,1, 500, 3000)

quick2dplot(sklimpath+"QCD.root","otree",qcd_pass, "AK8Puppijet0_msd","AK8Puppijet0_pt",tag,"scale1fb*12.89")
quick2dplot(sklimpath+"QCD.root","otree",qcd_fail, "AK8Puppijet0_msd","AK8Puppijet0_pt",antitag,"scale1fb*12.89")

tqq_pass= TH2F("tqq_pass","tqq_pass",60,50,350,1, 500, 3000)
tqq_fail= TH2F("tqq_fail","tqq_fail",60,50,350,1, 500, 3000)

quick2dplot(sklimpath+"TTbar_madgraphMLM.root","otree",tqq_pass, "AK8Puppijet0_msd","AK8Puppijet0_pt",tag,"scale1fb*12.89")
quick2dplot(sklimpath+"TTbar_madgraphMLM.root","otree",tqq_fail, "AK8Puppijet0_msd","AK8Puppijet0_pt",antitag,"scale1fb*12.89")

wqq_pass= TH2F("wqq_pass","wqq_pass",60,50,350,1, 500, 3000)
wqq_fail= TH2F("wqq_fail","wqq_fail",60,50,350,1, 500, 3000)

quick2dplot(sklimpath+"W.root","otree",wqq_pass, "AK8Puppijet0_msd","AK8Puppijet0_pt",tag,"scale1fb*12.89")
quick2dplot(sklimpath+"W.root","otree",wqq_fail, "AK8Puppijet0_msd","AK8Puppijet0_pt",antitag,"scale1fb*12.89")

zqq_pass= TH2F("zqq_pass","zqq_pass",60,50,350,1, 500, 3000)
zqq_fail= TH2F("zqq_fail","zqq_fail",60,50,350,1, 500, 3000)

quick2dplot(sklimpath+"DY.root","otree",zqq_pass, "AK8Puppijet0_msd","AK8Puppijet0_pt",tag,"scale1fb*12.89")
quick2dplot(sklimpath+"DY.root","otree",zqq_fail, "AK8Puppijet0_msd","AK8Puppijet0_pt",antitag,"scale1fb*12.89")

for m in mass:
	path=sklimpath 
        signal_file= TFile(path+"GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8_ext.root")#_%s_VH_alph.root"%(m))
        tree = signal_file.Get("otree") 
	Signal_mX_pass = TH2F("hqq_%s_pass"%(m), "", 60,50,350,1, 500, 3000)
	Signal_mX_fail = TH2F("hqq_%s_fail"%(m), "", 60,50,350,1, 500, 3000)
	quick2dplot(path+"GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8_ext.root","otree",Signal_mX_pass, "AK8Puppijet0_msd","AK8Puppijet0_pt",tag,"scale1fb*12.89")
	quick2dplot(path+"GluGluHToBB_M125_13TeV_amcatnloFXFX_pythia8_ext.root","otree",Signal_mX_fail, "AK8Puppijet0_msd","AK8Puppijet0_pt",antitag,"scale1fb*12.89")
	#Signal_mX_pass.Scale(SF_tau21*lumi*0.01)
	#Signal_mX_fail.Scale(SF_tau21*lumi*0.01)
	outfile.cd()
	Signal_mX_pass.Write()
	Signal_mX_fail.Write()
	


outfile.cd()
qcd_pass.Write()
qcd_fail.Write()
data_obs_pass.Write()
data_obs_fail.Write()
wqq_pass.Write()
wqq_fail.Write()
zqq_pass.Write()
zqq_fail.Write()
tqq_pass.Write()
tqq_fail.Write()
outfile.Write()
outfile.Close()

