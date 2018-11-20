# Repository for Z' + jet and ggH(bb) + jet

## First time set-up:
```
cmsrel CMSSW_8_1_0    #CMSSW version used for combine/combineHavester
cd src/
git clone git@github.com:DAZSLE/ZPrimePlusJet.git
cd ZPrimePlusJet/
```
## Do this everytime:
```
cmsenv
source setup.sh
```
# Instructions for running GGH plotting code on FNAL LPC

MC stack plots:
~~~~
$ python analysis/controlPlotsGGH.py --lumi 30 -i /eos/uscms/store/user/lpchbb/ggHsample_V11/sklim-v0-28Oct/ -o plots_2016_10_31/
~~~~

Signal comparison plots:
~~~~
$python analysis/comparisonSignals.py --lumi 30. -i /eos/uscms/store/user/lpchbb/ggHsample_V11/sklim-v0-28Oct/ -o plots_2016_10_31/
~~~~
