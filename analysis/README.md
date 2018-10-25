1. Run local test with small number of events
```
mkdir test_folder
python controlPlotsGGH.py --lumi 36.7 -o test_folder/  --max-split 100000
```
2. Submit jobs to condor
```
python submitJob_controlPlot.py -o controlplots/ --lumi 36.7 
```
3. Hadd subjob files and plot 
```
python submitJob_controlPlot.py -o controlplots/ --lumi 36.7 --hadd --clean
```
