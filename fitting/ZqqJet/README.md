# instructions for running Z'(qq) + jet fit

_N.B. We are running combine in CMSSW\_7\_4\_7_

1. Create histograms (can take a while):
`python Zqq_create.py`
2. Build workspaces, let's stay blind for now
`python buildRhalphabet.py -b --pseudo`
3. Validate the input histograms and workspaces
`python validateInputs.py -b`
4. Run MLFit
`combine -M MaxLikelihoodFit tmpCard.txt --saveWithUncertainties --saveShapes -v 2 --rMin -50 --rMax 50`
5. Validate the outputs
`python validateMLFit.py -b`

