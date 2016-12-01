cp base.root cards/
cp ralphabase.root cards/
for i in 50 75 100 150 250 300 400 500
do
	echo $i
	combineCards.py cards/card_rhalphabet_Pbb_cat1_$i.txt cards/card_rhalphabet_Pbb_cat2_$i.txt cards/card_rhalphabet_Pbb_cat3_$i.txt cards/card_rhalphabet_Pbb_cat4_$i.txt cards/card_rhalphabet_Pbb_cat5_$i.txt> combined_$i.txt 
#combineCards.py cards/card_rhalphabet_cat1.txt cards/card_rhalphabet_cat2.txt cards/card_rhalphabet_cat3.txt  > combined.txt 
#	combine -M MaxLikelihoodFit --rMin=-50 --rMax=50 --saveNormalizations --plot --saveShapes --saveWithUncertainties  -v 2 combined_$i.txt
	combine -M Asymptotic -t -1 combined_$i.txt
done
