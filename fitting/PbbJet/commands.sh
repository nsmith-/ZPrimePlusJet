
step=$1

if [[ $step == 1 ]]; then
  python submitJob_Hbb_create.py -o output-miniaod-pfmet140-hptckkw-hqq125ptShape/p10_data --is2017 --lumi 3.67 --sfData 10 -n 100  # for 10% data templates
  python submitJob_Hbb_create.py -o output-miniaod-pfmet140-hptckkw-hqq125ptShape/muonCR   --is2017 --lumi 36.7 -m -n 100 
  python submitJob_Hbb_create.py -o output-miniaod-pfmet140-hptckkw-hqq125ptShape/looserWZ --is2017 --lumi 3.67 --skip-qcd --skip-data --dbtagcut 0.9 -n 100
fi

if [[ $step == 2 ]]; then
  python submitJob_Hbb_create.py -o output-miniaod-pfmet140-hptckkw-hqq125ptShape/p10_data --hadd --clean -n 100
  python submitJob_Hbb_create.py -o output-miniaod-pfmet140-hptckkw-hqq125ptShape/muonCR   --hadd --clean -m -n 100
  python submitJob_Hbb_create.py -o output-miniaod-pfmet140-hptckkw-hqq125ptShape/looserWZ --hadd --clean --skip-qcd --skip-data --dbtagcut 0.9 -n 100
fi

if [[ $step == 3 ]]; then
  python buildRhalphabetHbb.py -i output-miniaod-pfmet140-hptckkw-hqq125ptShape/p10_data/hist_1DZbb_pt_scalesmear.root \
    --ifile-loose output-miniaod-pfmet140-hptckkw-hqq125ptShape/looserWZ/hist_1DZbb_pt_scalesmear_looserWZ.root \
    -o output-miniaod-pfmet140-hqq125ptShape/ \
    --remove-unmatched --prefit --addHptShape --blind |tee build.log
  
  python makeCardsHbb.py -i output-miniaod-pfmet140-hptckkw-hqq125ptShape/p10_data/hist_1DZbb_pt_scalesmear.root \
    --ifile-loose output-miniaod-pfmet140-hptckkw-hqq125ptShape/looserWZ/hist_1DZbb_pt_scalesmear_looserWZ.root \
    -o output-miniaod-pfmet140-hqq125ptShape/ \
    --remove-unmatched --no-mcstat-shape

  python writeMuonCRDatacard.py -i output-miniaod-pfmet140-hptckkw-hqq125ptShape/muonCR/hist_1DZbb_muonCR.root -o output-miniaod-pfmet140-hqq125ptShape/
fi

if [[ $step == 4 ]]; then
  pushd output-miniaod-pfmet140-hqq125ptShape/
  combineCards.py cat1=card_rhalphabet_cat1.txt cat2=card_rhalphabet_cat2.txt  cat3=card_rhalphabet_cat3.txt cat4=card_rhalphabet_cat4.txt  cat5=card_rhalphabet_cat5.txt cat6=card_rhalphabet_cat6.txt muonCR=datacard_muonCR.txt > card_rhalphabet_muonCR.txt
  text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel -m 125  --PO verbose --PO 'map=.*/*hqq125:r[1,0,20]' --PO 'map=.*/zqq:r_z[1,0,20]' card_rhalphabet_muonCR.txt -o card_rhalphabet_muonCR_floatZ.root
  combine -M FitDiagnostics card_rhalphabet_muonCR_floatZ.root --setParameterRanges r=-5,5:r_z=-2,2 --robustFit 1 --setRobustFitAlgo Minuit2,Migrad --saveNormalizations --plot --saveShapes --saveWithUncertainties --saveWorkspace
  # python rhalphabin.py 
  popd
fi
