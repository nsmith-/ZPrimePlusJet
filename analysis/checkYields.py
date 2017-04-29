import ROOT as rt
import math
import sys
if __name__ == '__main__':
	# get histogram for transform
        f_h2ddt = rt.TFile.Open("$ZPRIMEPLUSJET_BASE/analysis/ZqqJet/h3_n2ddt_26eff_36binrho11pt_Spring16.root",
                                  "read")  # GridOutput_v13_WP026.root # smooth version of the ddt ; exp is 4.45 vs 4.32 (3% worse)
        trans_h2ddt = f_h2ddt.Get("h2ddt")
        trans_h2ddt.SetDirectory(0)
        f_h2ddt.Close()

	#tfile = rt.TFile.Open('root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier/JetHTRun2016C_23Sep2016_v1_v2.root')
	tfile = rt.TFile.Open(sys.argv[1])
	otree = tfile.Get('otree')
	otree.SetBranchStatus('*',0)
	otree.SetBranchStatus('triggerBits',1)
	otree.SetBranchStatus('passJson',1)
	otree.SetBranchStatus('AK8Puppijet0_N2sdb1',1)
	otree.SetBranchStatus('AK8Puppijet0_pt',1)
	otree.SetBranchStatus('AK8Puppijet0_msd',1)
	otree.SetBranchStatus('puppet',1)
	otree.SetBranchStatus('AK8Puppijet0_isTightVJet',1)
	otree.SetBranchStatus('AK8Puppijet0_doublecsv',1)
	otree.SetBranchStatus('neleLoose',1)
	otree.SetBranchStatus('nmuLoose',1)
	otree.SetBranchStatus('ntau',1)
	

	nEvents = [0,0,0,0,0,0,0,0,0]
	print otree.GetEntries()
	for i, event in enumerate(otree):
		if i%10000==0: print i
		if i>=100000: break
		nEvents[0]+=1		
		if (event.triggerBits&2) and event.passJson: 
			nEvents[1]+=1
			jpt_8 = event.AK8Puppijet0_pt
			if jpt_8 > 450:
				nEvents[2]+=1
				if event.AK8Puppijet0_msd > 40:
					nEvents[3]+=1
					if event.neleLoose ==0 and event.nmuLoose == 0 and event.ntau == 0:
						nEvents[4]+=1
						if event.AK8Puppijet0_isTightVJet:
							nEvents[5]+=1
							if event.puppet< 180:
								nEvents[6]+=1
								rh_8 = math.log(event.AK8Puppijet0_msd * event.AK8Puppijet0_msd / event.AK8Puppijet0_pt / event.AK8Puppijet0_pt)  # tocheck here
								# N2DDT transformation
								cur_rho_index = trans_h2ddt.GetXaxis().FindBin(rh_8)
								cur_pt_index = trans_h2ddt.GetYaxis().FindBin(jpt_8)
								if rh_8 > trans_h2ddt.GetXaxis().GetBinUpEdge(trans_h2ddt.GetXaxis().GetNbins()): cur_rho_index = trans_h2ddt.GetXaxis().GetNbins()
								if rh_8 < trans_h2ddt.GetXaxis().GetBinLowEdge(1): cur_rho_index = 1
								if jpt_8 > trans_h2ddt.GetYaxis().GetBinUpEdge(trans_h2ddt.GetYaxis().GetNbins()): cur_pt_index = trans_h2ddt.GetYaxis().GetNbins()
								if jpt_8 < trans_h2ddt.GetYaxis().GetBinLowEdge(1): cur_pt_index = 1
								jtN2b1sdddt_8 = event.AK8Puppijet0_N2sdb1 - trans_h2ddt.GetBinContent(cur_rho_index, cur_pt_index)
								if jtN2b1sdddt_8 < 0:
									nEvents[7]+=1
									if event.AK8Puppijet0_doublecsv > 0.9:
										nEvents[8]+=1

	print nEvents
	print [1.*n/nEvents[0] for n in nEvents]
		
		
