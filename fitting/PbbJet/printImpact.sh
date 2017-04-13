text2workspace.py card_rhalphabet_muonCR.txt -m 125
combineTool.py -M Impacts -d card_rhalphabet_muonCR.root -m 125 --doInitialFit --robustFit 1
combineTool.py -M Impacts -d card_rhalphabet_muonCR.root -m 125 --doFits --robustFit 1 --parallel 4
combineTool.py -M Impacts -d card_rhalphabet_muonCR.root -m 125 -o impacts.json
plotImpacts.py -i impacts.json -o impacts

