1. Run local test with small number of events
```
mkdir test_folder
python controlPlotsGGH.py --lumi 36.7 -o test_folder/  --max-split 100000
```
2. Submit jobs to condor
`--dryRun` option will write the condor files only without submitting.
 - Make sure to edit the `gitClone` path to the correct repository.
 - 
```
python submitJob_controlPlot.py -o controlplots/ --lumi 36.7 
```
3. Hadd subjob files and plot 
Use the same command from submission the same options. Add the `--hadd --clean` part will hadd the subjob histograms and clean the submission files(leaving 1 set for de-buggin reference)
```
python submitJob_controlPlot.py -o controlplots/ --lumi 36.7 --hadd --clean
```
