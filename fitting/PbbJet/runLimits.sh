cp base.root cards/
cp ralphabase.root cards/
combineCards.py cards/card_rhalphabet_cat1.txt cards/card_rhalphabet_cat2.txt cards/card_rhalphabet_cat3.txt cards/card_rhalphabet_cat4.txt  cards/card_rhalphabet_cat5.txt > combined.txt 
#combineCards.py cards/card_rhalphabet_cat1.txt cards/card_rhalphabet_cat2.txt cards/card_rhalphabet_cat3.txt  > combined.txt 
combine -M MaxLikelihoodFit --rMin=-50 --rMax=50 --saveNormalizations --plot --saveShapes --saveWithUncertainties  -v 4 combined.txt
combine -M Asymptotic -v 2 combined.txt --minimizerTolerance 0.001 --minimizerStrategy 2 -S 0
