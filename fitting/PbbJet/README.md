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

Running limits:
```bash
# AK8
python runCombine.py -i hist_1DZbb_pt_scalesmear_AK8_check.root -o cards_2017_07_08/  -c p7 --lrho -6.0 --hrho -2.1 --model DMSbb --mass 50,100,125,200,300,350,400,500
python runCombine.py -i hist_1DZbb_pt_scalesmear_AK8_check.root -o cards_2017_07_08/  -c p75 --lrho -6.0 --hrho -2.1 --model DMSbb --mass 50,100,125,200,300,350,400,500
python runCombine.py -i hist_1DZbb_pt_scalesmear_AK8_check.root -o cards_2017_07_08/  -c p8 --lrho -6.0 --hrho -2.1 --model DMSbb --mass 50,100,125,200,300,350,400,500
python runCombine.py -i hist_1DZbb_pt_scalesmear_AK8_check.root -o cards_2017_07_08/  -c p85 --lrho -6.0 --hrho -2.1 --model DMSbb --mass 50,100,125,200,300,350,400,500
python runCombine.py -i hist_1DZbb_pt_scalesmear_AK8_check.root -o cards_2017_07_08/  -c p9 --lrho -6.0 --hrho -2.1 --model DMSbb --mass 50,100,125,200,300,350,400,500
# CA15
python runCombine.py -i hist_1DZbb_pt_scalesmear_CA15_check.root  -o cards_2017_07_08/  -c p7 --lrho -4.7 --hrho -1.0 --model DMSbb --mass 50,100,125,200,300,350,400,500 -b CA15
python runCombine.py -i hist_1DZbb_pt_scalesmear_CA15_check.root  -o cards_2017_07_08/  -c p75 --lrho -4.7 --hrho -1.0 --model DMSbb --mass 50,100,125,200,300,350,400,500 -b CA15
python runCombine.py -i hist_1DZbb_pt_scalesmear_CA15_check.root  -o cards_2017_07_08/  -c p8 --lrho -4.7 --hrho -1.0 --model DMSbb --mass 50,100,125,200,300,350,400,500 -b CA15
python runCombine.py -i hist_1DZbb_pt_scalesmear_CA15_check.root  -o cards_2017_07_08/  -c p85 --lrho -4.7 --hrho -1.0 --model DMSbb --mass 50,100,125,200,300,350,400,500 -b CA15
python runCombine.py -i hist_1DZbb_pt_scalesmear_CA15_check.root  -o cards_2017_07_08/  -c p9 --lrho -4.7 --hrho -1.0 --model DMSbb --mass 50,100,125,200,300,350,400,500 -b CA15
```

Plotting limits:
```bash
# AK8
python plotLimits.py --xsec -c p7 -b AK8 -i cards_2017_07_08/ --xsecMin 1e-3 --xsecMax 1e3
python plotLimits.py --xsec -c p75 -b AK8 -i cards_2017_07_08/ --xsecMin 1e-3 --xsecMax 1e3
python plotLimits.py --xsec -c p8 -b AK8 -i cards_2017_07_08/ --xsecMin 1e-3 --xsecMax 1e3
python plotLimits.py --xsec -c p85 -b AK8 -i cards_2017_07_08/ --xsecMin 1e-3 --xsecMax 1e3
python plotLimits.py --xsec -c p9 -b AK8 -i cards_2017_07_08/ --xsecMin 1e-3 --xsecMax 1e3
# CA15
python plotLimits.py --xsec -c p7 -b CA15 -i cards_2017_07_08/ --xsecMin 1e-3 --xsecMax 1e3
python plotLimits.py --xsec -c p75 -b CA15 -i cards_2017_07_08/ --xsecMin 1e-3 --xsecMax 1e3
python plotLimits.py --xsec -c p8 -b CA15 -i cards_2017_07_08/ --xsecMin 1e-3 --xsecMax 1e3
python plotLimits.py --xsec -c p85 -b CA15 -i cards_2017_07_08/ --xsecMin 1e-3 --xsecMax 1e3
python plotLimits.py --xsec -c p9 -b CA15 -i cards_2017_07_08/ --xsecMin 1e-3 --xsecMax 1e3
```
