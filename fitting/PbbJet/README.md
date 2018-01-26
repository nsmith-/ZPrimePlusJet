Create histogram templates for all double-b tagging cut points (0.7,0.75,0.8,0.85,0.9):
```bash
# AK8 1D (m) muon control region templates
python Hbb_create_Phibb.py --lumi 35.9 -o ./ -m 2>&1 | tee log_AK8_muon.txt
# CA15 1D (m) muon control region templates
python Hbb_create_Phibb.py --lumi 35.9 -o ./ -c -m 2>&1 | tee log_CA15_muon.txt
# AK8 2D (m, pt) failing/passing region templates
python Hbb_create_Phibb.py --lumi 35.9 -o ./ --skip-data 2>&1 | tee log_AK8_qcd.txt 
# CA15 2D (m, pt) failing/passing region templates 
python Hbb_create_Phibb.py --lumi 35.9 -o ./ -c --skip-data 2>&1 | tee log_CA15_qcd.txt 
```

Interpolating signal shapes and merging with data and MC shapes:
```bash
cd ../../analysis/
# AK8
python signalInterpolationsPhibb.py --input_file ../fitting/PbbJet/hist_1DZbb_pt_scalesmear_AK8_check.root --output_file hist_1DZbb_pt_scalesmear_AK8_interpolations.root --jet_type AK8 --interpolate --output_range 50,505,5
python signalInterpolationsPhibb.py --input_file ../fitting/PbbJet/hist_1DZbb_muonCR_AK8_check.root --output_file hist_1DZbb_muonCR_AK8_interpolations.root --jet_type AK8 --interpolate_muCR --output_range 50,505,5
# CA15
python signalInterpolationsPhibb.py --input_file ../fitting/PbbJet/hist_1DZbb_pt_scalesmear_CA15_check.root --output_file ../fitting/PbbJet/hist_1DZbb_pt_scalesmear_CA15_interpolations.root --jet_type CA15 --interpolate --output_range 50,505,5
cd fitting/PbbJet
python signalInterpolationsPhibb.py --input_file ../fitting/PbbJet/hist_1DZbb_muonCR_CA15_check.root --output_file ../fitting/PbbJet/hist_1DZbb_muonCR_CA15_interpolations.root --jet_type CA15 --interpolate_muCR --output_range 50,505,5
cd ../fitting/PbbJet/
python mergePhibb.py
```

Running (expected) limits:
```bash
# AK8
python runCombine.py -i hist_1DZbb_pt_scalesmear_AK8_interpolations_merge.root  -o cards_AK8_p9_r2p1_interp/ -c p9 --lrho -6.0 --hrho -2.1 --model DMSbb --masses '50,55,60,65,70,75,80,85,90,95,100,125,150,175,200,225,250,275,300,325,350,375,400,425,450,475,500' -b AK8 --nr 2 --np 1 
# CA15
python runCombine.py -i hist_1DZbb_pt_scalesmear_CA15_interpolations_merge.root  -o cards_CA15_p9_r3p1_interp/ -c p9 --lrho -4.7 --hrho -1.0 --model DMSbb --masses '50,55,60,65,70,75,80,85,90,95,100,125,150,175,200,225,250,275,300,325,350,375,400,425,450,475,500' -b CA15 --nr 5 --np 1 
```

Plotting (expected) limits:
```bash
# AK8
python plotLimits.py --gq -c p9 -b CA15 -i cards_AK8_p9_r2p1_interp/ --xsecMin 0 --xsecMax 15 -o cards_AK8_p9_r3p1_interp/ --masses '50,55,60,65,70,75,80,85,90,95,100,125,150,175,200,225,250,275,300,325,350,375,400,425,450,475,500'
# CA15
python plotLimits.py --gq -c p9 -b CA15 -i cards_CA15_p9_r3p1_interp/ --xsecMin 0 --xsecMax 15 -o cards_CA15_p9_r3p1_interp/ --masses '50,55,60,65,70,75,80,85,90,95,100,125,150,175,200,225,250,275,300,325,350,375,400,425,450,475,500'
```

Running F-tests AK8 and CA15 (2, 1) vs (3, 1) polynomial on 10% of data (lower order is model 1):
```bash
python runFtest.py -i hist_1DZbb_pt_scalesmear_AK8_check.root -t 100 --scale 10 --nr1 2 --np1 1 --nr2 3 --np2 1 -n 150 --lumi 3.59 -r 0 -o ftest_2017_08_23 -b AK8 -c p9 --lrho -6.0 --hrho -2.1 --mass 125
python runFtest.py -i hist_1DZbb_pt_scalesmear_CA15_check.root -t 100 --scale 10 --nr1 2 --np1 1 --nr2 3 --np2 1 -n 273 --lumi 3.59 -r 0 -o ftest_2017_08_23 -b CA15 -c p75 --lrho -4.7 --hrho -1.0 --mass 300 
```

Running F-test for AK8 and CA15 (2, 1) vs (3, 1) polynomial on MC (lower order is model 1):
```bash
python runFtest.py -i hist_1DZbb_pt_scalesmear_AK8_check.root -t 100 --scale 1 --nr1 2 --np1 1 --nr2 3 --np2 1 -n 150 --lumi 35.9 -r 0 -o ftest_2017_08_23 -b AK8 -c p9 --lrho -6.0 --hrho -2.1 --mass 125 --pseudo
python runFtest.py -i hist_1DZbb_pt_scalesmear_CA15_check.root -t 100 --scale 1 --nr1 2 --np1 1 --nr2 3 --np2 1 -n 273 --lumi 35.9 -r 0 -o ftest_2017_08_23 -b CA15 -c p75 --lrho -4.7 --hrho -1.0 --mass 300 --pseudo
```
