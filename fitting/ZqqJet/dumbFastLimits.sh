#!/bin/bash

echo "hello!"

#masses=(50 75 100 125 150 200 250)
masses=(50)

for i in "${masses[@]}"
do 
	echo $i 
	rm -f cards2x2_all_zqq$i*
	sed "s|zqq100|zqq$i|g" < cards2x2_all.txt > cards2x2_all_zqq$i.txt
	combine -M MaxLikelihoodFit cards2x2_all_zqq$i.txt --saveWithUncertainties --saveShapes -v 2 --rMin -5 --rMax 5 -n _asym_zqq$i
	python diffNuisances.py mlfit_asym_zqq$i.root -g nuisances_zqq$i.root 
	mv nuisances.pdf nuisances_zqq$i.pdf
	combine -M Asymptotic cards_all_zqq$i.txt --rMin -50 --rMax 50 -m $i -n _asym_zqq$i
	mv higgs* results
	mv mlfit* results
	python validateMLFit.py -b --fit prefit --mass $i --idir results
	python validateMLFit.py -b --fit fit_b --mass $i --idir results
done
