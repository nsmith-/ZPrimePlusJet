# Example usage:
# python signalInterpolationsPhibb.py --input_file hist_1DZbb_pt_scalesmear_CA15_check.root --output_file hist_1DZbb_pt_scalesmear_CA15_interpolations.root --jet_type CA15 --interpolate --output_range 100,425,25

import os
import sys
from math import sqrt, floor
from ROOT import *
from histogram_interpolator import HistogramInterpolator
#from DAZSLE.ZPrimePlusJet.histogram_interpolator import HistogramInterpolator 
#import DAZSLE.PhiBBPlusJet.analysis_configuration as config
#import DAZSLE.ZPrimePlusJet.xbb_config as config
#gInterpreter.Declare("#include \"MyTools/RootUtils/interface/SeabornInterface.h\"")
#gSystem.Load(os.path.expandvars("$CMSSW_BASE/lib/$SCRAM_ARCH/libMyToolsRootUtils.so"))
gROOT.SetBatch(True)
gStyle.SetOptStat(0)
gStyle.SetOptTitle(0)
#seaborn = Root.SeabornInterface()
#seaborn.Initialize()

def make_validation_plots(interpolated_histogram, simulated_histogram, save_tag, adjacent_histograms=None, x_range=None):
	# 2D ratio plot
	ratio_histogram = interpolated_histogram.Clone()
	ratio_histogram.Divide(simulated_histogram)
	c_ratio = TCanvas("c_intp_validation_ratio_{}".format(save_tag), save_tag, 700, 500)
	c_ratio.SetRightMargin(0.2)
	ratio_histogram.Draw("colz")
	c_ratio.SaveAs(os.path.expandvars("$HOME/DAZSLE/data/Validation/figures/{}.pdf".format(c_ratio.GetName())))
	c_ratio.SaveAs(os.path.expandvars("$HOME/DAZSLE/data/Validation/figures/{}.eps".format(c_ratio.GetName())))
	c_ratio.SaveAs(os.path.expandvars("$HOME/DAZSLE/data/Validation/figures/{}.C".format(c_ratio.GetName())))

	# 2D pull plot
	pull_histogram = interpolated_histogram.Clone()
	for xbin in xrange(1, pull_histogram.GetNbinsX() + 1):
		for ybin in xrange(1, pull_histogram.GetNbinsY() + 1):
			num = interpolated_histogram.GetBinContent(xbin, ybin)
			num_err = interpolated_histogram.GetBinError(xbin, ybin)
			den = simulated_histogram.GetBinContent(xbin, ybin)
			den_err = simulated_histogram.GetBinError(xbin, ybin)
			total_err = sqrt(num_err**2 + den_err**2)
			if total_err > 0:
				pull = (num - den) / total_err
			else:
				pull = 0.
			pull_histogram.SetBinContent(xbin, ybin, pull)
			pull_histogram.SetBinError(xbin, ybin, 0)

	c_pull = TCanvas("c_intp_validation_pull_{}".format(save_tag), save_tag, 700, 500)
	c_pull.SetRightMargin(0.2)
	pull_histogram.Draw("colz")
	c_pull.SaveAs(os.path.expandvars("$HOME/DAZSLE/data/Validation/figures/{}.pdf".format(c_pull.GetName())))
	c_pull.SaveAs(os.path.expandvars("$HOME/DAZSLE/data/Validation/figures/{}.eps".format(c_pull.GetName())))
	c_pull.SaveAs(os.path.expandvars("$HOME/DAZSLE/data/Validation/figures/{}.C".format(c_pull.GetName())))

	# 1D plots
	for ptbin in xrange(0, interpolated_histogram.GetNbinsY() + 1):
		if ptbin == 0:
			interpolated_histogram_1D = interpolated_histogram.ProjectionX("{}_int_ptbinAll".format(interpolated_histogram.GetName()))
			simulated_histogram_1D = simulated_histogram.ProjectionX("{}_sim_ptbinAll".format(simulated_histogram.GetName()))
		else:
			interpolated_histogram_1D = interpolated_histogram.ProjectionX("{}_int_ptbin{}".format(interpolated_histogram.GetName(), ptbin), ptbin, ptbin)
			simulated_histogram_1D = simulated_histogram.ProjectionX("{}_sim_ptbin{}".format(simulated_histogram.GetName(), ptbin), ptbin, ptbin)
		ratio_histogram_1D = interpolated_histogram_1D.Clone()
		ratio_histogram_1D.Divide(simulated_histogram_1D)
		if ptbin == 0:
			c_comparison = TCanvas("c_intp_validation_{}_ptbinAll".format(save_tag), save_tag, 800, 1000)
		else:
			c_comparison = TCanvas("c_intp_validation_{}_ptbin{}".format(save_tag, ptbin), save_tag, 800, 1000)
		l_comparison = TLegend(0.6, 0.6, 0.88, 0.8)
		l_comparison.SetFillColor(0)
		l_comparison.SetBorderSize(0)
		top = TPad("top", "top", 0., 0.5, 1., 1.)
		top.SetBottomMargin(0.02)
		top.Draw()
		top.cd()

		ymax = -1
		if interpolated_histogram_1D.GetMaximum() > ymax:
			ymax = interpolated_histogram_1D.GetMaximum()
		if simulated_histogram_1D.GetMaximum() > ymax:
			ymax = simulated_histogram_1D.GetMaximum()
		if adjacent_histograms:
			for adj_mass, adj_hist in adjacent_histograms.iteritems():
				if adj_hist.GetMaximum() > ymax:
					ymax = adj_hist.GetMaximum()
		ymax = ymax * 1.3

		interpolated_histogram_1D.SetMarkerStyle(24)
		interpolated_histogram_1D.SetMarkerColor(kRed+2)
		interpolated_histogram_1D.SetLineColor(kRed+2)
		interpolated_histogram_1D.SetLineWidth(2)
		interpolated_histogram_1D.GetXaxis().SetTitleSize(0)
		interpolated_histogram_1D.GetXaxis().SetLabelSize(0)
		interpolated_histogram_1D.SetMaximum(ymax)
		if x_range:
			interpolated_histogram_1D.GetXaxis().SetRangeUser(x_range[0], x_range[1])
		interpolated_histogram_1D.Draw()
		simulated_histogram_1D.SetMarkerStyle(20)
		simulated_histogram_1D.SetMarkerColor(kMagenta+2)
		simulated_histogram_1D.SetLineColor(kMagenta+2)
		simulated_histogram_1D.SetLineWidth(2)
		simulated_histogram_1D.Draw("same")
		l_comparison.AddEntry(simulated_histogram_1D, "Simulated", "lp")
		l_comparison.AddEntry(interpolated_histogram_1D, "Interpolated", "lp")

		if adjacent_histograms:
			adj_hist_proj = {}
			for adj_mass in sorted(adjacent_histograms.keys()):
				if ptbin == 0:
					adj_hist_proj[adj_mass] = adjacent_histograms[adj_mass].ProjectionX("{}_ptbinAll".format(adjacent_histograms[adj_mass].GetName()))
				else:
					adj_hist_proj[adj_mass] = adjacent_histograms[adj_mass].ProjectionX("{}_ptbin{}".format(adjacent_histograms[adj_mass].GetName(), ptbin), ptbin, ptbin)
				adj_hist_proj[adj_mass].SetMarkerStyle(20)
				adj_hist_proj[adj_mass].SetMarkerSize(0)
				adj_hist_proj[adj_mass].SetLineStyle(3)
				adj_hist_proj[adj_mass].SetLineColor(kMagenta-9)
				adj_hist_proj[adj_mass].SetLineWidth(2)
				adj_hist_proj[adj_mass].Draw("hist same")
				l_comparison.AddEntry(adj_hist_proj[adj_mass], "Sim, m={} GeV".format(adj_mass), "l")
		l_comparison.Draw()

		c_comparison.cd()
		bottom = TPad("bottom", "bottom", 0., 0., 1., 0.5)
		bottom.SetTopMargin(0.02)
		bottom.SetBottomMargin(0.2)
		bottom.Draw()
		bottom.cd()
		if x_range:
			ratio_histogram_1D.GetXaxis().SetRangeUser(x_range[0], x_range[1])
		ratio_histogram_1D.Draw()

		c_comparison.cd()
		c_comparison.SaveAs(os.path.expandvars("$HOME/DAZSLE/data/Validation/figures/{}.pdf".format(c_comparison.GetName())))

# Note: this requires David's ROOT-seaborn interface to get the color helix.
# - git clone ssh://git@github.com/DryRun/RootUtils MyTools/RootUtils
# - scram b
# - Uncomment the includes in the header of this file
def make_summary_plot(sim_hists, int_hists, save_tag):
	c = TCanvas("c_intp_summary_{}".format(save_tag), "c_intp_summary_{}".format(save_tag), 800, 600)
	l = TLegend(0.6, 0.2, 0.88, 0.8)
	l.SetFillColor(0)
	l.SetBorderSize(0)

	xmin = 0.
	xmax = 500.
	ymin = 0.
	ymax = max([h.GetMaximum() for h in sim_hists.values() + int_hists.values()]) * 1.3
	frame = TH1D("frame", "frame", 100, 0., 500.)
	frame.SetMinimum(ymin)
	frame.SetMaximum(ymax)
	frame.GetXaxis().SetTitle("m_{SD}^{PUPPI} [GeV]")

	for sim_mass in sorted(sim_hists.keys()):
		color = seaborn.GetColorRoot("cubehelixlarge", int(floor(30 * sim_mass / 500.)), 30)
		sim_hists[sim_mass].SetLineColor(color)
		sim_hists[sim_mass].SetLineStyle(1)
		sim_hists[sim_mass].SetLineWidth(2)
		sim_hists[sim_mass].SetMarkerStyle(20)
		sim_hists[sim_mass].SetMarkerSize(0)
		sim_hists[sim_mass].SetMarkerColor(color)
		sim_hists[sim_mass].Draw("hist same")
		#sim_hists[sim_mass].Draw("same")
		l.AddEntry(sim_hists[sim_mass], "m_{{X}}={} GeV".format(sim_mass), "l")

	for int_mass in sorted(int_hists.keys()):
		color = seaborn.GetColorRoot("cubehelixlarge", int(floor(30 * int_mass / 500.)), 30)
		int_hists[int_mass].SetLineColor(color)
		int_hists[int_mass].SetLineStyle(2)
		int_hists[int_mass].SetLineWidth(2)
		int_hists[int_mass].SetMarkerStyle(20)
		int_hists[int_mass].SetMarkerSize(0)
		int_hists[int_mass].SetMarkerColor(color)
		int_hists[int_mass].Draw("hist same")
		#int_hists[int_mass].Draw("same")
		l.AddEntry(int_hists[int_mass], "m_{{X}}={} GeV".format(int_mass), "l")

	l.Draw()
	c.SaveAs(os.path.expandvars("$HOME/DAZSLE/data/Validation/figures/{}.pdf".format(c.GetName())))

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description='Perform signal interpolations on pT vs. mSD histograms.')
	parser.add_argument("--input_file", type=str, help="Input file with e.g. DMSbb125_pass histograms")
	parser.add_argument("--output_file", type=str, help="Output filename")
	parser.add_argument('--jet_type', type=str, help="AK8 or CA15")
	parser.add_argument('--interpolate', action='store_true', help="Perform signal interpolations")
	parser.add_argument('--interpolate_muCR', action='store_true', help="Perform signal interpolations")
	parser.add_argument('--validate', type=int, help="Validate interpolation at specified mass value (must be a simulated point with adjacent simulated points)")
	parser.add_argument('--plots', action='store_true', help="Validate interpolation at specified mass value (must be a simulated point with adjacent simulated points)")
	parser.add_argument('--input_masses', type=str, default="50,100,125,200,300,350,400,500", help="List of input masses (comma-separated)")
	output_group = parser.add_mutually_exclusive_group() 
	output_group.add_argument('--output_masses', type=str, help="List of output masses (comma-separated)")
	output_group.add_argument('--output_range', type=str, help="Range of output masses (e.g. 100,425,25 for 100-400 GeV in 25 GeV steps)")
	args = parser.parse_args()

	# Create list of input and output masses
	input_masses = [int(x) for x in args.input_masses.split(",")]
	if args.output_masses:
		output_masses = []
		for x in args.output_masses.split(","):
			if int(x) not in input_masses:
				output_masses.append(int(x))
	elif args.output_range:
		output_args = [int(x) for x in args.output_range.split(",")]
		output_masses = []
		print output_args
		for x in xrange(output_args[0], output_args[1], output_args[2]):
			if x not in input_masses:
				output_masses.append(x)
	else:
		print "[signal_interpolations] ERROR : Must specify output_masses or output_range"
		sys.exit(1)

	# Example histogram name: DMSbb100_p9_fail_JERDown;1	

	models = ["DMSbb"]

	if args.interpolate:
		# Input and output files (uses David's configuration. Replace if you are not David.)
		#input_file = TFile(config.get_histogram_file(args.region, args.jet_type), "READ")
		#output_file = TFile(config.get_interpolation_file(args.region, args.jet_type), "RECREATE")
		input_file = TFile(args.input_file, "READ")
		output_file = TFile(args.output_file, "RECREATE")

		# Top-level loop
		for region in ["pass", "fail"]:
			for model in models:
				for wp in ["p7", "p75", "p8", "p85", "p9"]:
					for syst in ["", "_JESUp", "_JERUp", "_PuUp", "_triggerUp", "_JESDown", "_JERDown", "_PuDown", "_triggerDown","_matched","_unmatched"]:
						input_histograms = {}
						output_histograms_1D = {}
						model_histogram = None
						for ptbin in xrange(1, 7):
							input_histograms[ptbin] = {}
							output_histograms_1D[ptbin] = {}
							for mass in input_masses:
								if not model_histogram:
									model_histogram = input_file.Get("{}{}_{}_{}{}".format(model, mass, wp, region, syst))
									if not model_histogram:
										print "[signal_interpolations] ERROR : Couldn't find histogram {} in file {}".format("{}{}_{}{}".format(model, mass, region, syst), input_file.GetPath())
									model_histogram.SetName("model")
									model_histogram.SetDirectory(0)
									model_histogram.Reset()
									if model_histogram.GetNbinsY() != 6:
										print "ERROR : The model histogram appears to have !=6 y bins, which this code assumes."
										sys.exit(1)
								input_histograms[ptbin][mass] = input_file.Get("{}{}_{}_{}{}".format(model, mass, wp, region, syst)).ProjectionX("{}{}_{}_ptbin{}".format(model, mass, region, ptbin), ptbin, ptbin)
								input_histograms[ptbin][mass].SetDirectory(0)
							print input_histograms[ptbin]
							interpolator = HistogramInterpolator(input_histograms[ptbin])
							for mass in output_masses:
								output_histograms_1D[ptbin][mass] = interpolator.make_interpolation(mass)
								output_histograms_1D[ptbin][mass].SetName("{}{}_{}_{}{}_ptbin{}".format(model, mass, wp, region, syst, ptbin))
								#output_file.cd()
								#output_histograms_1D[ptbin][mass].Write()

						# Put 1D histograms back together into 2D
						output_histograms = {}
						for mass in output_masses:
							output_histograms[mass] = model_histogram.Clone()
							output_histograms[mass].SetName("{}{}_{}_{}{}".format(model, mass, wp, region, syst))
							for msdbin in xrange(1, model_histogram.GetNbinsX() + 1):
								for ptbin in xrange(1, model_histogram.GetNbinsY() + 1):
									output_histograms[mass].SetBinContent(msdbin, ptbin, output_histograms_1D[ptbin][mass].GetBinContent(msdbin))
									output_histograms[mass].SetBinError(msdbin, ptbin, output_histograms_1D[ptbin][mass].GetBinContent(msdbin))
							output_file.cd()
							print "[debug] Writing {}".format(output_histograms[mass].GetName())
							output_histograms[mass].Write()

						# Save a copy of the input histograms to the output file
						output_file.cd()
						for mass in input_masses:
							input_file.Get("{}{}_{}_{}{}".format(model, mass, wp, region, syst)).Write()
		input_file.Close()
		output_file.Close()

	if args.interpolate_muCR:
		input_file = TFile(args.input_file, "READ")
		output_file = TFile(args.output_file, "RECREATE")
		# Top-level loop
		for region in ["pass", "fail"]:
			for model in models:
				for wp in ["p7", "p75", "p8", "p85", "p9"]:
					for syst in ['','_JERUp','_JERDown','_JESUp','_JESDown','_mutriggerUp','_mutriggerDown','_muidUp','_muidDown','_muisoUp','_muisoDown','_PuUp','_PuDown']:
						input_histograms = {}
						output_histograms = {}
						for mass in input_masses:
							if model == "ZPrime" and mass > 300:
								continue
							print "[debug] Trying to get " + "{}{}_{}_{}{}".format(model, mass, wp, region, syst) + " from file " + input_file.GetPath()
							input_histograms[mass] = input_file.Get("{}{}_{}_{}{}".format(model, mass, wp, region, syst)).Clone()
							if not input_histograms[mass]:
								print "ERROR : Couldn't find histogram {}{}_{}{} in file {}".format(model, mass, region, syst, input_file.GetPath())
								sys.exit(1)
							input_histograms[mass].SetDirectory(0)
							# Save a copy of the input to the output file
							output_file.cd()
							input_histograms[mass].Write()
						print input_histograms
						interpolator = HistogramInterpolator(input_histograms)
						for mass in output_masses:
							if model == "ZPrime" and mass > 300:
								continue
							output_histograms[mass] = interpolator.make_interpolation(mass)
							output_histograms[mass].SetName("{}{}_{}_{}{}".format(model, mass, wp, region, syst))
							output_file.cd()
							output_histograms[mass].Write()
		print "Saved interpolations to {}".format(output_file.GetPath())
		input_file.Close()
		output_file.Close()

	if args.validate:
		validation_mass = args.validate
		if not validation_mass in input_masses:
			print "ERROR : The validation mass must be in the list of input masses."
			sys.exit(1)
		input_file = TFile(args.input_file, "READ")

		# Find the neighboring simulated masses
		left_mass = -1
		right_mass = -1
		input_masses_minus_validation = [x for x in input_masses if x != validation_mass]
		for i in xrange(len(input_masses_minus_validation) - 1):
			if input_masses_minus_validation[i] < validation_mass and validation_mass < input_masses_minus_validation[i+1]:
				left_mass = input_masses_minus_validation[i]
				right_mass = input_masses_minus_validation[i+1]
				break
		if left_mass == -1:
			print "ERROR : Couldn't find adjacent simulated masses."
			print "Validation mass = {}".format(validation_mass)
			print "Input masses = ",
			print input_masses_minus_validation
			sys.exit(1)

		# Top-level loop
		for region in ["pass", "fail"]:
			for model in models:
				input_histograms = {}
				output_histograms_1D = {}
				model_histogram = None
				for ptbin in xrange(1, 7):
					input_histograms[ptbin] = {}
					for mass in [left_mass, right_mass]:
						if not model_histogram:
							model_histogram = input_file.Get("{}{}_{}".format(model, mass, region))
							model_histogram.SetName("model")
							model_histogram.SetDirectory(0)
							model_histogram.Reset()
							if model_histogram.GetNbinsY() != 6:
								print "ERROR : The model histogram appears to have !=6 y bins, which this code assumes."
								sys.exit(1)
						input_histograms[ptbin][mass] = input_file.Get("{}{}_{}".format(model, mass, region)).ProjectionX("{}{}_{}_ptbin{}".format(model, mass, region, ptbin), ptbin, ptbin)
						print "[debug] Name = {}".format(input_histograms[ptbin][mass].GetName())
					interpolator = HistogramInterpolator(input_histograms[ptbin])
					output_histograms_1D[ptbin] = interpolator.make_interpolation(validation_mass)
					output_histograms_1D[ptbin].SetName("{}{}_{}_ptbin{}".format(model, validation_mass, region, ptbin))

				# Put 1D histograms back together into 2D
				interpolated_histogram = model_histogram.Clone()
				interpolated_histogram.SetName("{}{}_{}_interpolated".format(model, validation_mass, region))
				for msdbin in xrange(1, model_histogram.GetNbinsX() + 1):
					for ptbin in xrange(1, model_histogram.GetNbinsY() + 1):
						interpolated_histogram.SetBinContent(msdbin, ptbin, output_histograms_1D[ptbin].GetBinContent(msdbin))
						interpolated_histogram.SetBinError(msdbin, ptbin, output_histograms_1D[ptbin].GetBinError(msdbin))

				# Get simulated histograms
				simulated_histogram = input_file.Get("{}{}_{}".format(model, validation_mass, region))
				adjacent_histograms = {}
				for adj_mass in [left_mass, right_mass]:
					adjacent_histograms[adj_mass] = input_file.Get("{}{}_{}".format(model, adj_mass, region))

				save_tag = "{}_{}_{}_{}".format(args.jet_type, region, model, validation_mass)
				make_validation_plots(interpolated_histogram, simulated_histogram, save_tag, adjacent_histograms=adjacent_histograms, x_range=[left_mass-75.,right_mass+75.])

	if args.plots:
		sim_file = TFile(args.input_file, "READ")
		int_file = TFile(args.output_file, "READ")
		for region in ["pass", "fail"]:
			for model in models:
				for ptbin in xrange(0, 7):
					sim_hists = {}
					int_hists = {}
					for sim_mass in input_masses:
						if ptbin == 0:
							sim_hists[sim_mass] = sim_file.Get("{}{}_{}".format(model, sim_mass, region)).ProjectionX("{}{}_{}_ptbinAll".format(model, sim_mass, region))
						else:
							sim_hists[sim_mass] = sim_file.Get("{}{}_{}".format(model, sim_mass, region)).ProjectionX("{}{}_{}_ptbin{}".format(model, sim_mass, region, ptbin), ptbin, ptbin)
						sim_hists[sim_mass].SetDirectory(0)
					for int_mass in output_masses:
						if ptbin == 0:
							int_hists[int_mass] = int_file.Get("{}{}_{}".format(model, int_mass, region)).ProjectionX("{}{}_{}_ptbinAll".format(model, sim_mass, region))
						else:
							int_hists[int_mass] = int_file.Get("{}{}_{}".format(model, int_mass, region)).ProjectionX("{}{}_{}_ptbin{}".format(model, sim_mass, region, ptbin), ptbin, ptbin)
						int_hists[int_mass].SetDirectory(0)
					if ptbin == 0:
						save_tag = "{}_{}_{}_ptbinAll".format(region, model, args.jet_type)
					else:
						save_tag = "{}_{}_{}_ptbin{}".format(region, model, args.jet_type, ptbin)
					make_summary_plot(sim_hists, int_hists, save_tag)


