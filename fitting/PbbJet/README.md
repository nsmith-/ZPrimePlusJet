Instructions to run create cards and run limits, etc.

Create templates:
```
# create all templates, with passing region double b-tag > 0.9
export SKLIMDIR=/eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier
python Hbb_create.py -i root://cmseos.fnal.gov/$SKLIMDIR -o output-miniaod-pfmet140-hptckkw-hqq125ptShape --lumi 35.9

# create templates for muon CR
python Hbb_create.py -i root://cmseos.fnal.gov/$SKLIMDIR -o output-miniaod-pfmet140-hptckkw-hqq125ptShape --lumi 35.9 -m

# create looser templates, with passing region double b-tag > 0.8 
# (have to change hard-coded value DBTAGCUT = 0.8 in sampleContainer.py)
python Hbb_create.py -i root://cmseos.fnal.gov/$SKLIMDIR -o output-miniaod-pfmet140-hptckkw-hqq125ptShape-looser --lumi 35.9 --skip-qcd --skip-data
cp output-miniaod-pfmet140-hptckkw-hqq125ptShape-looser/hist_1DZbb_pt_scalesmear.root output-miniaod-pfmet140-hptckkw-hqq125ptShape/hist_1DZbb_pt_scalesmear_looserWZ.root
```

Make workspaces and datacards:
```
# make workspaces (with MC only)
python buildRhalphabetHbb.py -i output-miniaod-pfmet140-hptckkw-hqq125ptShape/hist_1DZbb_pt_scalesmear.root --ifile-loose output-miniaod-pfmet140-hptckkw-hqq125ptShape/hist_1DZbb_pt_scalesmear_looserWZ.root -o output-miniaod-pfmet140-hqq125ptShape/ --remove-unmatched --prefit --addHptShape --pseudo

# make workspaces (with blinded data % 10: scale MC down by factor of 10)
python buildRhalphabetHbb.py -i output-miniaod-pfmet140-hptckkw-hqq125ptShape/hist_1DZbb_pt_scalesmear.root --ifile-loose output-miniaod-pfmet140-hptckkw-hqq125ptShape/hist_1DZbb_pt_scalesmear_looserWZ.root -o output-miniaod-pfmet140-hqq125ptShape/ --remove-unmatched --prefit --addHptShape --scale 10 --blind

# make workspaces (with full data)
python buildRhalphabetHbb.py -i output-miniaod-pfmet140-hptckkw-hqq125ptShape/hist_1DZbb_pt_scalesmear.root --ifile-loose output-miniaod-pfmet140-hptckkw-hqq125ptShape/hist_1DZbb_pt_scalesmear_looserWZ.root -o output-miniaod-pfmet140-hqq125ptShape/ --remove-unmatched --prefit --addHptShape

# make datacards
python makeCardsHbb.py -i output-miniaod-pfmet140-hqq125ptShape/hist_1DZbb_pt_scalesmear.root --ifile-loose output-miniaod-pfmet140-hqq125ptShape/hist_1DZbb_pt_scalesmear_looserWZ.root -o output-miniaod-pfmet140-hqq125ptShape/ --remove-unmatched --no-mcstat-shape

# make muonCR datacards
python writeMuonCRDatacard.py -i output-miniaod-pfmet140-hqq125ptShape/  -o output-miniaod-pfmet140-hqq125ptShape/
cd output-miniaod-pfmet140-hqq125ptShape/
```

Run combine commands (for individual fits, limits, etc.):
```
# combine cards
combineCards.py cat1=card_rhalphabet_cat1.txt cat2=card_rhalphabet_cat2.txt  cat3=card_rhalphabet_cat3.txt cat4=card_rhalphabet_cat4.txt  cat5=card_rhalphabet_cat5.txt cat6=card_rhalphabet_cat6.txt muonCR=datacard_muonCR.txt > card_rhalphabet_muonCR.txt

# convert to binary file
text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel -m 125  --PO verbose --PO 'map=.*/*hqq125:r[1,0,20]' --PO 'map=.*/zqq:r_z[1,0,20]' card_rhalphabet_muonCR.txt -o card_rhalphabet_muonCR_floatZ.root
```

Make post-fit plots:
```
combine -M MaxLikelihoodFit card_rhalphabet_muonCR_floatZ.root --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --robustFit 1 --minimizerAlgoForMinos Minuit2,Migrad --saveNormalizations --plot --saveShapes --saveWithUncertainties --saveWorkspace
mkdir mlfit/
cd ..
python validateMLFit.py -i output-miniaod-pfmet140-hptckkw-hqq125ptShape/ -o output-miniaod-pfmet140-hptckkw-hqq125ptShape/ --fit fit_s
```

Run F-tests:
```
# run f-test for (2, 1) vs (2, 2) with MC:
python runFtest.py -i output-miniaod-pfmet140-hptckkw-hqq125ptShape/hist_1DZbb_pt_scalesmear.root --ifile-loose output-miniaod-pfmet140-hptckkw-hqq125ptShape/hist_1DZbb_pt_scalesmear_looserWZ.root -t 10 --nr1 2 --np1 1 --nr2 2 --np2 2 -n 153 --lumi 35.9 -r 0 -o output-miniaod-pfmet140-hptckkw-hqq125ptShape/ftest/ --pseudo

# run f-test for (2, 1) vs (2, 2) with blinded data % 10:
python runFtest.py -i output-miniaod-pfmet140-hptckkw-hqq125ptShape/hist_1DZbb_pt_scalesmear.root --ifile-loose output-miniaod-pfmet140-hptckkw-hqq125ptShape/hist_1DZbb_pt_scalesmear_looserWZ.root -t 10 --nr1 2 --np1 1 --nr2 2 --np2 2 -n 153 --lumi 35.9 -r 0 -o output-miniaod-pfmet140-hptckkw-hqq125ptShape/ftest/ --scale 10 --blind
```

Follow other combine instructions:
https://github.com/DAZSLE/ZPrimePlusJet/blob/Hbb_Diff-pT/fitting/PbbJet/README.md
