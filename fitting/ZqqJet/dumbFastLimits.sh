#!/bin/bash

echo "hello!"

#masses=(50 75 100 125 150 200)
masses=(200)
#masses=(300)

for i in "${masses[@]}"
do 
	echo $i 
	sed "s|zqq100|zqq$i|g" < cards_all.txt > cards_all_zqq$i.txt
	combine -M MaxLikelihoodFit cards_all_zqq$i.txt --saveWithUncertainties --saveShapes -v 2 --rMin -5 --rMax 5 -n _asym_zqq$i
	# python diffNuisances.py mlfit_asym_zqq$i.root -g nuisances_zqq$i.root 
	# mv nuisances.pdf nuisances_zqq$i.pdf
	#combine -M Asymptotic cards_all_zqq$i.txt --rMin -50 --rMax 50 -m $i -n _asym_zqq$i
	# python validateMLFit.py -b --fit prefit --mass $i --idir results_Data5percent_2d27invfb_MassTo250
	# python validateMLFit.py -b --fit fit_b --mass $i --idir results_Data5percent_2d27invfb_MassTo250
done

# sed 's|zqq100|zqq50|g' < cards_all.txt > cards_all_zqq50.txt
# sed 's|zqq100|zqq75|g' < cards_all.txt > cards_all_zqq75.txt
# sed 's|zqq100|zqq100|g' < cards_all.txt > cards_all_zqq100.txt
# sed 's|zqq100|zqq125|g' < cards_all.txt > cards_all_zqq125.txt
# sed 's|zqq100|zqq150|g' < cards_all.txt > cards_all_zqq150.txt
# sed 's|zqq100|zqq200|g' < cards_all.txt > cards_all_zqq200.txt

# combine -M MaxLikelihoodFit cards_all_zqq100.txt --saveWithUncertainties --saveShapes -v 2 --rMin -50 --rMax 50 -n _asym_zqq100
# combine -M Asymptotic cards_all_zqq100.txt --rMin -50 --rMax 50 -m 100 -n _asym_zqq100

# combine -M MaxLikelihoodFit cards_all_zqq100.txt --saveWithUncertainties --saveShapes -v 2 --rMin -50 --rMax 50 -n _asym_zqq100
# combine -M Asymptotic cards_all_zqq100.txt --rMin -50 --rMax 50 -m 100 -n _asym_zqq100

# combine -M MaxLikelihoodFit cards_all_zqq100.txt --saveWithUncertainties --saveShapes -v 2 --rMin -50 --rMax 50 -n _asym_zqq100
# combine -M Asymptotic cards_all_zqq100.txt --rMin -50 --rMax 50 -m 100 -n _asym_zqq100

# combine -M MaxLikelihoodFit cards_all_zqq100.txt --saveWithUncertainties --saveShapes -v 2 --rMin -50 --rMax 50 -n _asym_zqq100
# combine -M Asymptotic cards_all_zqq100.txt --rMin -50 --rMax 50 -m 100 -n _asym_zqq100

# combine -M MaxLikelihoodFit cards_all_zqq100.txt --saveWithUncertainties --saveShapes -v 2 --rMin -50 --rMax 50 -n _asym_zqq100
# combine -M Asymptotic cards_all_zqq100.txt --rMin -50 --rMax 50 -m 100 -n _asym_zqq100