import os, json

import os

sampledirs = open(os.path.expandvars("$ZPRIMEPLUSJET_BASE/analysis/ggH/sampledirs.json"),"r")
fdirs  = json.load(sampledirs)['Hbb_create_2017']
for key in fdirs.keys():
	tfiles[key] = {}
	for subd in fdirs[key]:
		subdfiles = [ "root://cmseos.fnal.gov/" + subd + f for f in os.listdir(subd)]
		tfiles[key][ subd.strip('/').split('/')[-1] ] = subdfiles

with open('ggH/samplefiles.json', 'w') as fp:
	json.dump(tfiles, fp, indent=4, separators=(',', ': '))                                                                                                                                     

