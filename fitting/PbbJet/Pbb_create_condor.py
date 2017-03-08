import os
import math
from array import array
from ROOT import *
import sys
sys.path.append(os.path.expandvars("$CMSSW_BASE/src/DAZSLE/ZPrimePlusJet/analysisa"))
sys.path.append(os.path.expandvars("$CMSSW_BASE/src/DAZSLE/ZPrimePlusJet/analysis/PbbJet"))
from sklims import sklims

if __name__ == "__main__":
	from argparse import ArgumentParser
	parser = ArgumentParser(description="Run sampleContainer jobs on condor")
	parser.add_argument("--samples", default="all", help="Comma-separated list of samples to run")
	parser.add_argument("--no_retar", action="store_true", help="Don't re-tar")
	args = parser.parse_args()

	if not args.no_retar:
		os.system("csub_tar --cmssw")

	if args.samples == "all":
		samples = ["hqq125", "tthqq125", "vbfhqq125", "whqq125", "zhqq125", "qcd", "tqq", "stqq", "wqq", "wlnu", "zqq", "vvqq", "data_jetht", "data_singlemu"]
	elif args.samples == "signal":
		samples = ["hqq125", "tthqq125", "vbfhqq125", "whqq125", "zhqq125"]
	elif args.samples == "background":
		samples = ["qcd", "tqq", "stqq", "wqq", "wlnu", "zqq", "vvqq"]
	elif args.samples == "data":
		samples = ["data_jetht", "data_singlemu"]
	else:
		samples = args.samples.split(",")

	for sample in samples:
		submission_directory = "/uscms_data/d3/dryu/DAZSLE/data/Histograms/condor/" + sample
		os.system("mkdir -pv " + submission_directory)
		start_dir = os.getcwd()
		os.chdir(submission_directory)

		subjob = 0
		for input_file in sklims[sample]:
			run_script = open(submission_directory + "/run_{}.sh".format(subjob), "w")
			files_to_transfer = []
			input_files_on_node = []
			if "root://" in input_file:
				input_files_on_node.append(input_file)
			else:
				input_files_on_node.append(os.path.basename(input_file))
				files_to_transfer.append(input_file)

			run_command = "python $CMSSW_BASE/src/DAZSLE/ZPrimePlusJet/fitting/PbbJet/Pbb_create2.py --input_files {} --sample {} --output_file {}".format(",".join(input_files_on_node), sample, sample + ".root." + str(subjob))
			run_command += " --lumi 35.8 "
			run_command += " --sf 1"
			if "data" in sample:
				run_command += " --isData "
				if "jetht" in sample:
					run_command += " --cutFormula \"((triggerBits&2)&&passJson)\""
				elif "singlemu" in sample:
					run_command += " --cutFormula \"((triggerBits&4)&&passJson)\""
			run_script.write("#!/bin/bash\n")
			run_script.write("export ZPRIMEPLUSJET_BASE=$CMSSW_BASE/src/DAZSLE/ZPrimePlusJet/\n")
			run_script.write(run_command + "\n")
			run_script.close()

			submit_command = "csub " + submission_directory + "/run_{}.sh --cmssw --no_retar".format(subjob)
			if len(files_to_transfer):
				submit_command += " -F " + ",".join(file_to_transfer)
			os.system(submit_command)
			subjob += 1

		os.chdir(start_dir)
