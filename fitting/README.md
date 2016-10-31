python HSR_create.py

python fit_fullralph.py --xMin 50 --xMax 350 --nBins 60 --input hists_1D.root

cd Cards/ggH

cp ../../base.root .

cp ../../ralphabase.root ralpha.root

mkdir plots #if it doesn't exist

combine -M MaxLikelihoodFit card_hist_ralpha_cat1.txt --saveWithUncertainties --saveShapes -v 2 --rMin -50 --rMax 50  --plots --out plots

python plot.py --cats 1 --mass 125 --passfail

