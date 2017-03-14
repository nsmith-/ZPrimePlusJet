sklim_directory = "root://cmsxrootd-site.fnal.gov//store/user/lpchbb/zprimebits-v12.03/cvernier/"
scalar_sklim_directory = "root://cmsxrootd-site.fnal.gov/store/user/lpchbb/zprimebits-v12.02/norm/"
sklims = {                                                                                                                                                                                
    'hqq125'   : [sklim_directory+'/GluGluHToBB_M125_13TeV_powheg_pythia8_all_1000pb_weighted.root'],                                                                              
    # sklim_directory+'/GluGluHToBB_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root'],                                                                                               
    #'VBFHbb'  : [sklim_directory+'/VBFHToBB_M125_13TeV_amcatnlo_pythia8_1000pb_weighted.root'],                                                                                  
    'vbfhqq125': [sklim_directory+'/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_all_1000pb_weighted.root'],                                                                   
    'zhqq125'  : [sklim_directory+'/ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',                                                                               
                    sklim_directory+'/ggZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_1000pb_weighted.root',                                                                                             
                    sklim_directory+'/ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_ext_1000pb_weighted.root',                                                                                           
                    sklim_directory+'/ggZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],                                                                                              
    'whqq125'  : [sklim_directory+'/WminusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root',                                                                          
                    sklim_directory+'/WplusH_HToBB_WToQQ_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],                                                                             
    'tthqq125' :  [sklim_directory+'/ttHTobb_M125_13TeV_powheg_pythia8_1000pb_weighted.root'],#ttHTobb_M125_TuneCUETP8M2_ttHtranche3_13TeV_powheg_pythia8_1000pb_weighted.root'],
    'vvqq'     : [sklim_directory+'/WWTo4Q_13TeV_powheg_1000pb_weighted.root',                                                                                                       
                    sklim_directory+'/ZZ_13TeV_pythia8_1000pb_weighted.root',                                                                                                       
                    sklim_directory+'/WZ_13TeV_pythia8_1000pb_weighted.root'],                                                                                                      
    'zqq'      : [sklim_directory+'/DYJetsToQQ_HT180_13TeV_1000pb_weighted.root'],                                                                                                    
    #ZJetsToQQ_HT600toInf_13TeV_madgraph_1000pb_weighted.root'],#DYJetsToQQ_HT180_13TeV_1000pb_weighted.root '],                                                              
    'stqq'     :  [sklim_directory+'/ST_t_channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',                                            
                    sklim_directory+'/ST_t_channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV_powhegV2_madspin_1000pb_weighted.root',                                           
                    sklim_directory+'/ST_tW_antitop_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root',                                                
                    sklim_directory+'/ST_tW_top_5f_inclusiveDecays_13TeV_powheg_pythia8_TuneCUETP8M2T4_1000pb_weighted.root'],                                                   
    #'W'       :  [sklim_directory+'/WJetsToQQ_HT_600ToInf_13TeV_1000pb_weighted.root'],                                                                                               
    'wqq'      :  [sklim_directory+'/WJetsToQQ_HT180_13TeV_1000pb_weighted.root'],                                                                                                    
    'wlnu'     :[sklim_directory+'WJetsToLNu_HT_100To200_13TeV_1000pb_weighted.root',                                                                                                
                    sklim_directory+'/WJetsToLNu_HT_200To400_13TeV_1000pb_weighted.root',                                                                                                
                    sklim_directory+'/WJetsToLNu_HT_400To600_13TeV_1000pb_weighted.root',                                                                                                
                    sklim_directory+'/WJetsToLNu_HT_600To800_13TeV_1000pb_weighted.root',                                                                                                
                    sklim_directory+'/WJetsToLNu_HT_800To1200_13TeV_1000pb_weighted.root',                                                                                               
                    sklim_directory+'/WJetsToLNu_HT_1200To2500_13TeV_1000pb_weighted.root'],                                                                                              
    #'TTbar'   :  [sklim_directory+'/TTJets_13TeV_1000pb_weighted.root'], #MadGraph is the old default                                                                             
    'tqq'      :  [sklim_directory+'/TT_powheg_1000pb_weighted.root'], #Powheg is the new default                                                                                     
    'qcd'      : [sklim_directory+'/QCD_HT100to200_13TeV_1000pb_weighted.root',                                                                                                       
                    sklim_directory+'/QCD_HT200to300_13TeV_all_1000pb_weighted.root',                                                                                                   
                    sklim_directory+'/QCD_HT300to500_13TeV_all_1000pb_weighted.root',                                                                                                   
                    sklim_directory+'/QCD_HT500to700_13TeV_ext_1000pb_weighted.root',                                                                                                   
                    sklim_directory+'/QCD_HT700to1000_13TeV_ext_1000pb_weighted.root',                                                                                                  
                    sklim_directory+'/QCD_HT1000to1500_13TeV_all_1000pb_weighted.root',                                                                                                 
                    sklim_directory+'/QCD_HT1500to2000_13TeV_all_1000pb_weighted.root',                                                                                                 
                    sklim_directory+'/QCD_HT2000toInf_13TeV_1000pb_weighted.root'],                                                                                                     
    'Phibb50'  : [sklim_directory+'/Spin0_ggPhi12j_g1_50_Scalar_13TeV_madgraph_1000pb_weighted.root'],                                                                            
    'Phibb75'  : [sklim_directory+'/Spin0_ggPhi12j_g1_75_Scalar_13TeV_madgraph_1000pb_weighted.root'],                                                                            
    'Phibb150' : [sklim_directory+'/Spin0_ggPhi12j_g1_150_Scalar_13TeV_madgraph_1000pb_weighted.root'],                                                                          
    'Phibb250' : [sklim_directory+'/Spin0_ggPhi12j_g1_250_Scalar_13TeV_madgraph_1000pb_weighted.root'],                                                                          
    'data_jetht' : [sklim_directory+'JetHTRun2016B_23Sep2016_v1.root',                                                                                                             
                    sklim_directory+'JetHTRun2016B_23Sep2016_v3_0.root',                                                                                                               
                    sklim_directory+'JetHTRun2016B_23Sep2016_v3_1.root',                                                                                                               
                    sklim_directory+'JetHTRun2016B_23Sep2016_v3_2.root',                                                                                                               
                    sklim_directory+'JetHTRun2016B_23Sep2016_v3_3.root',                                                                                                               
                    sklim_directory+'JetHTRun2016B_23Sep2016_v3_4.root',                                                                                                               
                    sklim_directory+'JetHTRun2016B_23Sep2016_v3_5.root',                                                                                                               
                    sklim_directory+'JetHTRun2016B_23Sep2016_v3_6.root',                                                                                                               
                    sklim_directory+'JetHTRun2016B_23Sep2016_v3_7.root',                                                                                                               
                    sklim_directory+'JetHTRun2016B_23Sep2016_v3_8.root',                                                                                                               
                    sklim_directory+'JetHTRun2016B_23Sep2016_v3_9.root',                                                                                                               
                    sklim_directory+'JetHTRun2016B_23Sep2016_v3_10.root',                                                                                                              
                    sklim_directory+'JetHTRun2016B_23Sep2016_v3_11.root',                                                                                                              
                    sklim_directory+'JetHTRun2016B_23Sep2016_v3_12.root',                                                                                                              
                    sklim_directory+'JetHTRun2016B_23Sep2016_v3_13.root',                                                                                                              
                    sklim_directory+'JetHTRun2016B_23Sep2016_v3_14.root',                                                                                                              
                    sklim_directory+'JetHTRun2016C_23Sep2016_v1_v2.root',                                                                                                              
                    sklim_directory+'JetHTRun2016D_23Sep2016_v1_0.root',                                                                                                               
                    sklim_directory+'JetHTRun2016D_23Sep2016_v1_1.root',                                                                                                               
                    sklim_directory+'JetHTRun2016D_23Sep2016_v1_2.root',                                                                                                               
                    sklim_directory+'JetHTRun2016D_23Sep2016_v1_3.root',                                                                                                               
                    sklim_directory+'JetHTRun2016D_23Sep2016_v1_4.root',                                                                                                               
                    sklim_directory+'JetHTRun2016D_23Sep2016_v1_5.root',                                                                                                               
                    sklim_directory+'JetHTRun2016D_23Sep2016_v1_6.root',                                                                                                               
                    sklim_directory+'JetHTRun2016D_23Sep2016_v1_7.root',                                                                                                               
                    sklim_directory+'JetHTRun2016E_23Sep2016_v1_0.root',                                                                                                               
                    sklim_directory+'JetHTRun2016E_23Sep2016_v1_1.root',                                                                                                               
                    sklim_directory+'JetHTRun2016E_23Sep2016_v1_2.root',                                                                                                               
                    sklim_directory+'JetHTRun2016E_23Sep2016_v1_3.root',                                                                                                               
                    sklim_directory+'JetHTRun2016E_23Sep2016_v1_4.root',                                                                                                               
                    sklim_directory+'JetHTRun2016E_23Sep2016_v1_5.root',                                                                                                               
                    sklim_directory+'JetHTRun2016E_23Sep2016_v1_6.root',                                                                                                               
                    sklim_directory+'JetHTRun2016E_23Sep2016_v1_7.root',                                                                                                               
                    sklim_directory+'JetHTRun2016F_23Sep2016_v1.root',                                                                                                                 
                    sklim_directory+'JetHTRun2016G_23Sep2016_v1_v2.root',                                                                                                              
                    sklim_directory+'JetHTRun2016H_PromptReco_v2.root',                                                                                                                
                    sklim_directory+'JetHTRun2016H_PromptReco_v3.root'],                                                                                                             
    'data_singlemu': [sklim_directory+'/SingleMuonRun2016B_23Sep2016_v1.root',                                                                                                    
                       sklim_directory+'/SingleMuonRun2016B_23Sep2016_v3.root',                                                                                                           
                       sklim_directory+'/SingleMuonRun2016C_23Sep2016_v1.root',                                                                                                           
                       sklim_directory+'/SingleMuonRun2016D_23Sep2016_v1.root',                                                                                                           
                       sklim_directory+'/SingleMuonRun2016E_23Sep2016_v1.root',                                                                                                           
                       sklim_directory+'/SingleMuonRun2016F_23Sep2016_v1.root',                                                                                                           
                       sklim_directory+'/SingleMuonRun2016G_23Sep2016_v1.root',                                                                                                           
                       sklim_directory+'/SingleMuonRun2016H_PromptReco_v2.root',                                                                                                          
                       sklim_directory+'/SingleMuonRun2016H_PromptReco_v3.root'],
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_1000_PseudoScalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_1000_Scalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_100_Scalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_125_PseudoScalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_125_Scalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_150_PseudoScalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_150_Scalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_200_PseudoScalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_200_Scalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_250_PseudoScalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_250_Scalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_25_PseudoScalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_25_Scalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_300_PseudoScalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_300_Scalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_350_PseudoScalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_350_Scalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_400_Scalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_500_PseudoScalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_500_Scalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_50_PseudoScalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_50_Scalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_5_PseudoScalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_5_Scalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_600_PseudoScalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_600_Scalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_75_PseudoScalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_75_Scalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_800_PseudoScalar_13TeV_madgraph_1000pb_weighted.root
/eos/uscms/store/user/lpchbb/zprimebits-v12.02/norm/Spin0_ggPhi12j_g1_800_Scalar_13TeV_madgraph_1000pb_weighted.root

}