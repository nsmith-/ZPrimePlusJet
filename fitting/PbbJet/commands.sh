
step=$1

wdir=output-Hcc1
# --dbtagcut also the value read for CvL
# 0 local test
if [[ $step == 0 ]]; then
  mkdir -p $wdir/test
  python Hxx_create.py -b -o $wdir/test --is2017 --lumi 2.8 --sfData 10 --max-split 10000 --dbtagcut 0.83 -m --region 'Hcc1'
fi

if [[ $step == 1 ]]; then
  python submitJob_Hbb_create.py -o $wdir/p10_data --is2017 --lumi 41.1 --sfData 10 -n 100  --dbtagcut 0.83  --region 'Hcc1' # for 10% data templates
  python submitJob_Hbb_create.py -o $wdir/muonCR   --is2017 --lumi 41.1 -m -n 100   --dbtagcut 0.83 --region 'Hcc1'
  python submitJob_Hbb_create.py -o $wdir/looserWZ --is2017 --lumi 41.1 --skip-qcd --skip-data -n 100 --dbtagcut 0.83 --region 'Hcc1'
fi

if [[ $step == 2 ]]; then
  python submitJob_Hbb_create.py -o $wdir/p10_data --hadd --clean -n 100  --dbtagcut 0.83 --region 'Hcc1'
  python submitJob_Hbb_create.py -o $wdir/muonCR   --hadd --clean -m -n 100 --dbtagcut 0.83 --region 'Hcc1'
  python submitJob_Hbb_create.py -o $wdir/looserWZ --hadd --clean --skip-qcd --skip-data -n 100 --dbtagcut 0.83 --region 'Hcc1'
fi

if [[ $step == 3 ]]; then
  python buildRhalphabetHbb.py -i $wdir/p10_data/hist_1DZbb_pt_scalesmear.root \
    \ #--ifile-loose $wdir/looserWZ/hist_1DZbb_pt_scalesmear_looserWZ.root \
    -o $wdir/  \
    --remove-unmatched --addHptShape  \
    --prefit --pseudo --scale 10.0 |tee build.log
    # --prefit --blind --is2017 --scale 10.0 |tee build.log
  
  python makeCardsHbb.py -i $wdir/p10_data/hist_1DZbb_pt_scalesmear.root \
    \ #--ifile-loose $wdir/looserWZ/hist_1DZbb_pt_scalesmear_looserWZ.root \
    -o $wdir/ --remove-unmatched --no-mcstat-shape 

   python writeMuonCRDatacard.py -i $wdir/muonCR/hist_1DZbb_muonCR.root -o $wdir/
fi

if [[ $step == 4 ]]; then
  pushd $wdir/
  combineCards.py cat1=card_rhalphabet_cat1.txt cat2=card_rhalphabet_cat2.txt  cat3=card_rhalphabet_cat3.txt cat4=card_rhalphabet_cat4.txt  cat5=card_rhalphabet_cat5.txt cat6=card_rhalphabet_cat6.txt muonCR=datacard_muonCR.txt > card_rhalphabet_muonCR.txt

  text2workspace.py card_rhalphabet_muonCR.txt -o card_rhalphabet_all_floatZ.root -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel -m 125  --PO verbose --PO 'map=.*/hcc125:r[1,0,20]' --PO 'map=.*/zcc:r_z[1,0,20]' 
  combine -M FitDiagnostics card_rhalphabet_all_floatZ.root --setParameterRanges r=-5,5:r_z=-2,2 --robustFit 1 --setRobustFitAlgo Minuit2,Migrad --saveWorkspace \
    --setParameters r=1,r_z=1 -t -1 --toysFreq # --saveNormalizations --plot --saveShapes --saveWithUncertainties
  
  text2workspace.py card_rhalphabet_all.txt -o card_rhalphabet_all_floatZ.root -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel -m 125  --PO verbose --PO 'map=.*/hcc125:r[1,0,20]' --PO 'map=.*/zcc:r_z[1,0,20]' 

  combine -M Significance --signif card_rhalphabet_all_floatZ.root  --redefineSignalPOIs r_z --setParameterRanges r=-10,10:r_z=-2,2 --setParameters r=1,r_z=1 \
    -t -1 --toysFreq --freezeParameters r # scale # tqqnormSF,tqqeffSF

  combine -M Asymptotic card_rhalphabet_all_floatZ.root --redefineSignalPOIs r --setParameterRanges r=-10,10:r_z=-2,2 --setParameters r=0,r_z=1 \
    -t -1 --toysFreq  --freezeParameters r_z #,tqqnormSF,tqqeffSF 

  # python rhalphabin.py 

  #mkdir mlfit
  popd
fi

if [[ $step == 5 ]]; then
  python validateMLFit.py -i $wdir/ -o $wdir/ --fit fit_s --lumi 41.1 --tag 'DDCvL' --cut 0.83
fi
