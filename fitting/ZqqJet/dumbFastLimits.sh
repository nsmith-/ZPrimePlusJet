#!/bin/bash

echo "hello!"

#masses=(50 75 100 125 150 200)
masses=(100 150)

for i in "${masses[@]}"
do 
	echo $i 
	sed "s|zqq100|zqq$i|g" < cards_all.txt > cards_all_zqq$i.txt
	combine -M MaxLikelihoodFit cards_all_zqq$i.txt --saveWithUncertainties --saveShapes -v 2 --rMin -50 --rMax 50 -n _asym_zqq$i
	combine -M Asymptotic cards_all_zqq$i.txt --rMin -50 --rMax 50 -m $i -n _asym_zqq$i
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