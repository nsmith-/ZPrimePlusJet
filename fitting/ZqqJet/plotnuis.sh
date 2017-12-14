#!/bin/bash

for x in `seq 50 5 300`;  do
    cd ZQQ_${x}
    cp ../diffNuisances.py .
    python diffNuisances.py lim_34mlfit.root -g test.root
    cp nuisances.pdf ../nuis/nuis_${x}.pdf
    cd ..
done
    