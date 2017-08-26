#AK8 w/o Data
nohup python analysis/controlPlotsPhibb.py --lumi 35.9 -o plots_AK8_NoData > output_ak8_NoData.txt & 
#AK8 with Data
nohup python analysis/controlPlotsPhibb.py --lumi 35.9 --isData -o plots_AK8_Data > output_ak8_Data.txt & 
#AK8 with Data and muonCR
nohup python analysis/controlPlotsPhibb.py --lumi 35.9 --isData --muonCR -o plots_AK8_Data_MuonCR > output_ak8_Data_MuonCR.txt & 
#CA15 w/o Data
nohup python analysis/controlPlotsPhibb.py --lumi 35.9 --fillCA15 -o plots_CA15_NoData > output_ca15_NoData.txt & 
#CA15 with Data
nohup python analysis/controlPlotsPhibb.py --lumi 35.9 --isData --fillCA15 -o plots_CA15_Data > output_ca15_Data.txt & 
#CA15 with Data and muonCR
nohup python analysis/controlPlotsPhibb.py --lumi 35.9 --isData --muonCR --fillCA15 -o plots_CA15_Data_MuonCR > output_ca15_Data_MuonCR.txt & 

