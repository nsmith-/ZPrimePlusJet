# instructions for running Z'(qq) + jet fit

_N.B. We are running combine in CMSSW\_7\_4\_7_

1. Create histograms (can take a while):
`python Zqq_create.py`
2. Build workspaces
`python buildRhalphabet.py -b`
3. Validate the input histograms and workspaces
`python validateInputs.py -b`
4. Make cards
`python makeCards.py`
`combineCards.py card_rhalphabet_34_cat1.txt card_rhalphabet_34_cat2.txt card_rhalphabet_34_cat3.txt card_rhalphabet_34_cat4.txt card_rhalphabet_34_cat5.txt  > card_rhalphabet_34_pt.txt or whatever the last line is`
5. Run MLFit and limits, for one mass
`cd ..`
`combine -M MaxLikelihoodFit cards_all.txt --saveWithUncertainties --saveShapes -v 2 --rMin -50 --rMax 50`
`combine -M Asymptotic cards_all.txt --rMin -50 --rMax 50`
6. Validate output
`python massplot.py or plotPt.py`
7. Plot final mass (paper 17-001)
`python massplotPaper.py`

# automizing
To run many limits:
`use limit.py`
To plot limits:
`python fullLims_1cat.py -b`