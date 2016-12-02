# instructions for running Z'(qq) + jet fit

_N.B. We are running combine in CMSSW\_7\_4\_7_

1. Create histograms (can take a while):
`python Zqq_create.py`
2. Build workspaces, let's stay blind for now
`python buildRhalphabet.py -b --pseudo`
3. Validate the input histograms and workspaces
`python validateInputs.py -b`
4. Make cards
`python makeCards.py`
`cd cards`
`combineCards.py card_rhalphabet_cat1.txt card_rhalphabet_cat2.txt card_rhalphabet_cat3.txt card_rhalphabet_cat4.txt card_rhalphabet_cat5.txt > ../cards_all.txt`
5. Run MLFit and limits, for one mass
`cd ..`
`combine -M MaxLikelihoodFit cards_all.txt --saveWithUncertainties --saveShapes -v 2 --rMin -50 --rMax 50`
`combine -M Asymptotic cards_all.txt --rMin -50 --rMax 50`
6. Validate the outputs
`python validateMLFit.py -b --fit prefit`
`python validateMLFit.py -b --fit fit_b`

# automizing
To run many limits:
`bash dumbFastLimits.sh`
To plot limits:
`python fullLims_1cat.py -b`

