# Instructions to do everything

Need to install fork of CombineHarverster for Impacts: https://github.com/jmduarte/CombineHarvester/

# convert to binary
```
text2workspace.py -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel  --PO verbose --PO 'map=.*/*hqq125:r[1,0,20]' --PO 'map=.*/zqq:r_z[1,0,20]' card_rhalphabet_muonCR.txt -m 125 -o card_rhalphabet_muonCR_floatZ.root
```

# standard fit for r (fixed r_z = 1)
```
combine -M MultiDimFit -d card_rhalphabet_muonCR_floatZ.root -P r --floatOtherPOIs=0  --robustFit 1
```

# standard fit for r_z (fixed r = 1)
```
combine -M MultiDimFit -d card_rhalphabet_muonCR_floatZ.root -P r_z --floatOtherPOIs=0  --robustFit 1
```

# fit for r and r_z (both floating)
```
combine -M MultiDimFit -d card_rhalphabet_muonCR_floatZ.root --minimizerTolerance 0.001 --minimizerStrategy 2 --setPhysicsModelParameterRanges r=0,5:r_z=0,2
```

# 2d likelihood scan (data):
```
combine -M MultiDimFit --minimizerTolerance 0.001 --minimizerStrategy 2  --setPhysicsModelParameterRanges r=-4,8:r_z=0,3 --algo grid --points 441 -d card_rhalphabet_muonCR_floatZ.root -n 2D_data --saveWorkspace 
combine -M MultiDimFit --minimizerTolerance 0.001 --minimizerStrategy 2  --setPhysicsModelParameterRanges r=-4,8:r_z=0,3 --algo grid --points 441 -d higgsCombineErr.MultiDimFit.mH120.root -n 2D_data --saveWorkspace --freezeNuisances all --snapshotName MultiDimFit
```

# 2d likelihood scan (asimov):
```
combine -M MultiDimFit --minimizerTolerance 0.001 --minimizerStrategy 2  --setPhysicsModelParameterRanges r=-4,8:r_z=0,3 --algo grid --points 441 -d card_rhalphabet_muonCR_floatZ.root -n 2D_asimov -t -1 --toysFreq --setPhysicsModelParameters r=1,r_z=1 --saveWorkspace 
```

# 2d likelihood scan (data) wider range:
```
combine -M MultiDimFit --minimizerTolerance 0.001 --minimizerStrategy 2  --setPhysicsModelParameterRanges r=-6,12:r_z=0,3 --algo grid --points 441 -d card_rhalphabet_muonCR_floatZ.root -n 2D_data --saveWorkspace 
```

# 2d likelihood scan (asimov) wider range:
```
combine -M MultiDimFit --minimizerTolerance 0.001 --minimizerStrategy 2  --setPhysicsModelParameterRanges r=-6,12:r_z=0,3 --algo grid --points 441 -d card_rhalphabet_muonCR_floatZ.root -n 2D_asimov -t -1 --toysFreq --setPhysicsModelParameters r=1,r_z=1 --saveWorkspace 
```

# 1d likelihood scan for r_z (profiling r):
```
python ../plotDeltaLL.py -d card_rhalphabet_muonCR_floatZ.root --rMin 0 --rMax 2 --data --lumi 35.9 -n 100 -r 1 -o ./ -P r_z --floatOtherPOIs 
```

# 1d likelihood scan for r (profiling r_z):
```
python ../plotDeltaLL.py -d card_rhalphabet_muonCR_floatZ.root --rMin -4 --rMax 10 --data --lumi 35.9 -n 100 -r 1 -o ./ -P r --floatOtherPOIs
```

# 1d likelihood scan for r_z (fixed r = 1):
```
python ../plotDeltaLL.py -d card_rhalphabet_muonCR_floatZ.root --rMin 0 --rMax 2 --data --lumi 35.9 -n 100 -r 1 -o ./ -P r_z 
```

# 1d likelihood scan for r (fixed r_z = 1):
```
python ../plotDeltaLL.py -d card_rhalphabet_muonCR_floatZ.root --rMin -4 --rMax 10 --data --lumi 35.9 -n 100 -r 1 -o ./ -P r
```

# 1d likelihood scan for r_z (profiling r) on asimov:
```
python ../plotDeltaLL.py -d card_rhalphabet_muonCR_floatZ.root --rMin 0 --rMax 2 --lumi 35.9 -n 100 -r 1 -o ./ -P r_z --floatOtherPOIs 
```

# 1d likelihood scan for r_z (fixed r = 1) on asimov:
```
python ../plotDeltaLL.py -d card_rhalphabet_muonCR_floatZ.root --rMin 0 --rMax 2 --lumi 35.9 -n 100 -r 1 -o ./ -P r_z 
```

# 1d likelihood scan for r (profiling r_z) on asimov:
```
python ../plotDeltaLL.py -d card_rhalphabet_muonCR_floatZ.root --rMin -4 --rMax 10 --lumi 35.9 -n 100 -r 1 -o ./ -P r --floatOtherPOIs
```

# 1d likelihood scan for r (fixed r_z = 1) on asimov:
```
python ../plotDeltaLL.py -d card_rhalphabet_muonCR_floatZ.root --rMin -4 --rMax 10  --lumi 35.9 -n 100 -r 1 -o ./ -P r
```

# observed and expected for r_z
```
combine -M ProfileLikelihood --signif card_rhalphabet_muonCR_floatZ.root --redefineSignalPOIs r_z --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --minimizerTolerance 0.001
combine -M ProfileLikelihood --signif card_rhalphabet_muonCR_floatZ.root --redefineSignalPOIs r_z -t -1 --toysFreq --expectSignal 1 --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --minimizerTolerance 0.001
```

# observed and expected for r
```
combine -M ProfileLikelihood --signif card_rhalphabet_muonCR_floatZ.root --redefineSignalPOIs r --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --minimizerTolerance 0.001
combine -M ProfileLikelihood --signif card_rhalphabet_muonCR_floatZ.root --redefineSignalPOIs r -t -1  --toysFreq --expectSignal 1 --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --minimizerTolerance 0.001
```

# observed and expected for r_z (fix r)
 ```
combine -M ProfileLikelihood --signif card_rhalphabet_muonCR_floatZ.root --redefineSignalPOIs r_z --freezeNuisances r
combine -M ProfileLikelihood --signif card_rhalphabet_muonCR_floatZ.root --redefineSignalPOIs r_z -t -1 --toysFreq --expectSignal 1 --freezeNuisances r
```

# observed and expected for r (fix r_z)
```
combine -M ProfileLikelihood --signif card_rhalphabet_muonCR_floatZ.root --redefineSignalPOIs r --freezeNuisances r_z
combine -M ProfileLikelihood --signif card_rhalphabet_muonCR_floatZ.root --redefineSignalPOIs r -t -1 --toysFreq --expectSignal 1 --freezeNuisances r_z
```

# get 2D error (data)
```
combine -M MultiDimFit -d card_rhalphabet_muonCR_floatZ.root --minimizerTolerance 0.001 --minimizerStrategy 2 --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --algo singles --robustFit 1  --minimizerAlgoForMinos Minuit2,Migrad --saveWorkspace -n Err 
```

# get stat-only error
```
combine -M MultiDimFit -d card_rhalphabet_muonCR_floatZ.root --minimizerTolerance 0.001 --minimizerStrategy 2 --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --robustFit 1  --minimizerAlgoForMinos Minuit2,Migrad --saveWorkspace -n Err
combine -M MultiDimFit -d higgsCombineErr.MultiDimFit.mH120.root --minimizerTolerance 0.001 --minimizerStrategy 2 --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --algo singles --robustFit 1  --minimizerAlgoForMinos Minuit2,Migrad --saveWorkspace -n noSysErr --freezeNuisances all --snapshotName MultiDimFit
```

# get 1D errors (data)
```
combine -M MultiDimFit -d card_rhalphabet_muonCR_floatZ.root --minimizerTolerance 0.001 --minimizerStrategy 2 --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --algo singles  -P r --freezeNuisances r_z --robustFit 1
combine -M MultiDimFit -d card_rhalphabet_muonCR_floatZ.root --minimizerTolerance 0.001 --minimizerStrategy 2 --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --algo singles  -P r_z --freezeNuisances r --robustFit 1
```

# get 2D error (asimov)
```
combine -M MultiDimFit -d card_rhalphabet_muonCR_floatZ.root --minimizerTolerance 0.001 --minimizerStrategy 2 --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --algo singles   -t -1 --toysFreq --setPhysicsModelParameters r=1,r_z=1 --robustFit 1 --minimizerAlgoForMinos Minuit2,Migrad 
```

# get 1D errors (asimov)
```
combine -M MultiDimFit -d card_rhalphabet_muonCR_floatZ.root --minimizerTolerance 0.001 --minimizerStrategy 2 --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --algo singles  -P r --freezeNuisances r_z --robustFit 1 -t -1 --toysFreq --setPhysicsModelParameters r=1,r_z=1
combine -M MultiDimFit -d card_rhalphabet_muonCR_floatZ.root --minimizerTolerance 0.001 --minimizerStrategy 2 --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --algo singles  -P r_z --freezeNuisances r --robustFit 1 -t -1 --toysFreq --setPhysicsModelParameters r=1,r_z=1
```

# channel compatibility for r (float r_z):
```
combine -M ChannelCompatibilityCheck card_rhalphabet_muonCR_floatZ.root --redefineSignalPOIs r -m 125 -g cat1 -g cat2 -g cat3 -g cat4 -g cat5 -g cat6 -g muonCR --saveFitResult --setPhysicsModelParameterRanges r=-20,20:r_z=-10,10 --robustFit 1 
```
# channel compatibility for r_z (float r):
```
combine -M ChannelCompatibilityCheck card_rhalphabet_muonCR_floatZ.root --redefineSignalPOIs r_z -m 125 -g cat1 -g cat2 -g cat3 -g cat4 -g cat5 -g cat6 -g muonCR --saveFitResult --setPhysicsModelParameterRanges r=-5,5:r_z=-10,10 --robustFit 1 
```
# channel compatibility for r (fix r_z=1):
```
combine -M ChannelCompatibilityCheck card_rhalphabet_muonCR_floatZ.root --redefineSignalPOIs r -m 125 -g cat1 -g cat2 -g cat3 -g cat4 -g cat5 -g cat6 -g muonCR --saveFitResult --setPhysicsModelParameterRanges r=-20,20:r_z=-10,10 --robustFit 1 --freezeNuisances r_z
```
# channel compatibility for r_z (fix r=1):
```
combine -M ChannelCompatibilityCheck card_rhalphabet_muonCR_floatZ.root --redefineSignalPOIs r_z -m 125 -g cat1 -g cat2 -g cat3 -g cat4 -g cat5 -g cat6 -g muonCR --saveFitResult --setPhysicsModelParameterRanges r=-5,5:r_z=-10,10 --robustFit 1 --freezeNuisances r
```

# limit for r_z (float r_z)
```
combine -M Asymptotic -d card_rhalphabet_muonCR_floatZ.root --minimizerTolerance 0.001 --minimizerStrategy 2 --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2  --saveWorkspace -n hLimit --redefineSignalPOIs r 
```

# limit for r (float r_z)
```
combine -M Asymptotic -d card_rhalphabet_muonCR_floatZ.root --minimizerTolerance 0.001 --minimizerStrategy 2 --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2  --saveWorkspace -n zLimit
```

# impacts (asimov)
```
combineTool.py -M Impacts -d card_rhalphabet_muonCR_floatZ.root -m 125  -t -1 --toysFreq --expectSignal 1 --robustFit 1 --doInitialFit --rMin -5 --rMax 5 --exclude 'rgx{mcstat}'
combineTool.py -M Impacts -d card_rhalphabet_muonCR_floatZ.root -m 125  -t -1 --toysFreq --expectSignal 1 --robustFit 1 --doFits --rMin -5 --rMax 5 --exclude 'rgx{mcstat}'
combineTool.py -M Impacts -d card_rhalphabet_muonCR_floatZ.root -m 125  -t -1 --toysFreq --expectSignal 1 -o impacts_asimov.json --rMin -5 --rMax 5 --exclude 'rgx{mcstat}'
plotImpacts.py -i impacts_asimov.json -o impacts_asimov
```

# impacts (data)
```
combineTool.py -M Impacts -d card_rhalphabet_muonCR_floatZ.root -m 125 --minimizerTolerance 0.001 --minimizerStrategy 2 --robustFit 1 --minimizerAlgoForMinos Minuit2,Migrad --doInitialFit --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --exclude 'rgx{mcstat}’
combineTool.py -M Impacts -d card_rhalphabet_muonCR_floatZ.root -m 125 --minimizerTolerance 0.001 --minimizerStrategy 2 --robustFit 1 --minimizerAlgoForMinos Minuit2,Migrad --doFits --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --exclude 'rgx{mcstat}'

combineTool.py -M Impacts -d card_rhalphabet_muonCR_floatZ.root -m 125 -o impacts_data.json --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --exclude 'rgx{mcstat}'
plotImpacts.py -i impacts_data.json -o impacts_data

combineTool.py -M Impacts -d card_rhalphabet_muonCR_floatZ.root --redefineSignalPOIs r  -m 125 -o impacts_data_r.json --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --exclude 'rgx{mcstat}'
plotImpacts.py -i impacts_data_r.json -o impacts_data_r

combineTool.py -M Impacts -d card_rhalphabet_muonCR_floatZ.root --redefineSignalPOIs r  -m 125 -o impacts_data_r_nothy.json --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --exclude 'rgx{mcstat},hqq125pt'
plotImpacts.py -i impacts_data_r_nothy.json -o impacts_data_r_nothy
```

# get ML fit plots
```
combine -M MaxLikelihoodFit card_rhalphabet_muonCR_floatZ.root --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --robustFit 1 --minimizerAlgoForMinos Minuit2,Migrad  --saveNormalizations --plot --saveShapes --saveWithUncertainties --saveWorkspace
mkdir mlfit/
cd ..
python validateMLFit.py -i output-miniaod-pfmet140-hptckkw-hqq125ptShape/ -o output-miniaod-pfmet140-hptckkw-hqq125ptShape/ --fit fit_s
```

# get all impacts
```
combineTool.py -M Impacts -d card_rhalphabet_muonCR_floatZ.root -m 125 --minimizerTolerance 0.001 --minimizerStrategy 2 --robustFit 1 --minimizerAlgoForMinos Minuit2,Migrad --doInitialFit --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 --all
combineTool.py -M Impacts -d card_rhalphabet_muonCR_floatZ.root -m 125 --minimizerTolerance 0.001 --minimizerStrategy 2 --robustFit 1 --minimizerAlgoForMinos Minuit2,Migrad --doFits --setPhysicsModelParameterRanges r=-5,5:r_z=-2,2 —all
```

# run on grid for likelihood scan
```
source /cvmfs/cms.cern.ch/crab3/crab.sh
combineTool.py -M MultiDimFit --minimizerTolerance 0.001 --minimizerStrategy 2  --setPhysicsModelParameterRanges r=-4,8:r_z=0,3 --algo grid --points 10000 --split-points 100 -d card_rhalphabet_muonCR_floatZ.root -n 2D_data --saveWorkspace  --custom-crab /uscms_data/d3/jduarte1/CMSSW_7_4_7/src/CombineHarvester/CombineTools/scripts/custom_crab.py --job-mode crab3 --crab-area 2D_data
combineTool.py -M MultiDimFit --minimizerTolerance 0.001 --minimizerStrategy 2  --setPhysicsModelParameterRanges r=-4,8:r_z=0,3 --algo grid --points 10000 --split-points 100 -d card_rhalphabet_muonCR_floatZ.root -n 2D_asimov -t -1 --toysFreq --setPhysicsModelParameters r=1,r_z=1 --saveWorkspace --custom-crab /uscms_data/d3/jduarte1/CMSSW_7_4_7/src/CombineHarvester/CombineTools/scripts/custom_crab.py --job-mode crab3 --crab-area 2D_asimov
```
