mkdir Results_Phibb && mkdir Results_Phibb/AK8 && mkdir Results_Phibb/CA15 && mkdir Outputs
######  AK8
for d in 7 75 8 85 9 95
do
     echo 'DBTAGCUT : '$d
     mkdir Results_Phibb/AK8/p$d
     python makeCardsPhibb.py -i Safe_Input_Rootfiles/hist_1DZbb_pt_scalesmear_AK8_check.root --dbtagcut $d -o Results_Phibb/AK8/p$d --remove-unmatched --no-mcstat-shape > Outputs/make_ak8_p$d.txt
     python buildRhalphabetPhibb.py -i Safe_Input_Rootfiles/hist_1DZbb_pt_scalesmear_AK8_check.root --dbtagcut $d -o Results_Phibb/AK8/p$d --remove-unmatched  --prefit --pseudo --use-qcd > Outputs/build_ak8_p$d.txt
     cd Results_Phibb/AK8/p$d
     ls
     for i in 50 100 125 200 300 350 400 500  
     do
     	echo $i
             cd DMSbb$i
             cp ../base.root .
             cp ../rhalphabase.root .
             ls *.root
             combineCards.py card_rhalphabet_cat1.txt card_rhalphabet_cat2.txt card_rhalphabet_cat3.txt card_rhalphabet_cat4.txt  card_rhalphabet_cat5.txt card_rhalphabet_cat6.txt   >  card_rhalphabet.txt
             combine -M Asymptotic -v 2 -t -1 card_rhalphabet.txt --freezeNuisances tqqnormSF,tqqeffSF > output.txt
             combine -M MaxLikelihoodFit card_rhalphabet.txt --robustFit 1 --minimizerAlgoForMinos Minuit2,Migrad  --saveNormalizations --plot --saveShapes --saveWithUncertainties --saveWorkspace --freezeNuisances tqqnormSF,tqqeffSF
             ls -ltrh
             cd ../
     done
done
echo "Done for AK8"
cd /uscms_data/d3/askaur/AN/New/CMSSW_7_4_7/src/DAZSLE/ZPrimePlusJet/fitting/PbbJet
pwd

##### CA15
for d in 7 75 8 85 9 95
do
     echo 'DBTAGCUT : '$d
     mkdir Results_Phibb/CA15/p$d
     python makeCardsPhibb.py -i Safe_Input_Rootfiles/hist_1DZbb_pt_scalesmear_CA15_check.root --dbtagcut $d --lrho -4.7 --hrho -1.0 -o Results_Phibb/CA15/p$d --remove-unmatched --no-mcstat-shape > Outputs/make_ca15_p$d.txt
     python buildRhalphabetPhibb.py -i Safe_Input_Rootfiles/hist_1DZbb_pt_scalesmear_CA15_check.root --dbtagcut $d --lrho -4.7 --hrho -1.0 -o Results_Phibb/CA15/p$d --remove-unmatched  --prefit --pseudo --use-qcd > Outputs/build_ca15_p$d.txt
     cd Results_Phibb/CA15/p$d
     ls
     for i in 50 100 125 200 300 350 400 500  
     do
     	echo $i
             cd DMSbb$i
             cp ../base.root .
             cp ../rhalphabase.root .
             ls *.root
             combineCards.py card_rhalphabet_cat1.txt card_rhalphabet_cat2.txt card_rhalphabet_cat3.txt card_rhalphabet_cat4.txt  card_rhalphabet_cat5.txt card_rhalphabet_cat6.txt   >  card_rhalphabet.txt
             combine -M Asymptotic -v 2 -t -1 card_rhalphabet.txt --freezeNuisances tqqnormSF,tqqeffSF > output.txt
             combine -M MaxLikelihoodFit card_rhalphabet.txt --robustFit 1 --minimizerAlgoForMinos Minuit2,Migrad  --saveNormalizations --plot --saveShapes --saveWithUncertainties --saveWorkspace --freezeNuisances tqqnormSF,tqqeffSF
             ls -ltrh
             cd ../
     done
done
echo "Done for CA15"
cd /uscms_data/d3/askaur/AN/New/CMSSW_7_4_7/src/DAZSLE/ZPrimePlusJet/fitting/PbbJet
pwd
