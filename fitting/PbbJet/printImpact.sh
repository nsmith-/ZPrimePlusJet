text2workspace.py card_rhalphabet_muonCR.txt -m 125
combineTool.py -M Impacts -d card_rhalphabet_muonCR.root -m 125 --doInitialFit --robustFit 1
combineTool.py -M Impacts -d card_rhalphabet_muonCR.root -m 125 --doFits --robustFit 1 --parallel 4
combineTool.py -M Impacts -d card_rhalphabet_muonCR.root -m 125 -o impacts.json
plotImpacts.py -i impacts.json -o impacts

# javier commands:
text2workspace.py -m 125 card_rhalphabet_muonCR.txt
combineTool.py -M Impacts -d card_rhalphabet_muonCR.root -m 125  -t -1 --toysFreq --expectSignal 1 --robustFit 1 --doInitialFit --rMin -5 --rMax 5 --exclude 'rgx{mcstat}'
combineTool.py -M Impacts -d card_rhalphabet_muonCR.root -m 125  -t -1 --toysFreq --expectSignal 1 --robustFit 1 --doFits --rMin -5 --rMax 5 --exclude 'rgx{mcstat}'
combineTool.py -M Impacts -d card_rhalphabet_muonCR.root -m 125  -t -1 --toysFreq --expectSignal 1 -o impacts_asimov.json --rMin -5 --rMax 5 --exclude 'rgx{mcstat}'
plotImpacts.py -i impacts_asimov.json -o impacts_asimov

text2workspace.py -m 125 card_rhalphabet_muonCR.txt
combineTool.py -M Impacts -d card_rhalphabet_muonCR.root -m 125 --robustFit 1 --doInitialFit --rMin -5 --rMax 5 --exclude 'rgx{mcstat}'
combineTool.py -M Impacts -d card_rhalphabet_muonCR.root -m 125 --robustFit 1 --doFits --rMin -5 --rMax 5 --exclude 'rgx{mcstat}'
combineTool.py -M Impacts -d card_rhalphabet_muonCR.root -m 125 -o impacts_data.json --rMin -5 --rMax 5 --exclude 'rgx{mcstat}'
plotImpacts.py -i impacts_data.json -o impacts_data
