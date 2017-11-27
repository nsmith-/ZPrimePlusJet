#! /usr/bin/env python
import sys
import math
import array
from ROOT import RooRealVar, RooDataHist, RooHistPdf, RooArgList, RooArgSet, RooIntegralMorph, RooFormulaVar

class HistogramInterpolator:
	'''
		Class for interpolating signal histograms between mass points
		hist_dict = {interpolation key:TH1, ...}
	'''
	def __init__(self , hist_dict):
		self._hists = hist_dict
		self._input_values = sorted(hist_dict.keys())
		self._x = RooRealVar("x", "x", 
								self._hists[self._input_values[0]].GetXaxis().GetXmin(), 
								self._hists[self._input_values[0]].GetXaxis().GetXmax())
		self._x.setBins(self._hists[self._input_values[0]].GetNbinsX())

		# Convert TH1s to RooHistPdfs
		self._datahists = {}
		self._histpdfs = {}
		for input_value, histogram in self._hists.iteritems():
			self._datahists[input_value] = RooDataHist(histogram.GetName() + "d0", histogram.GetName() + "d0", 
																			RooArgList(self._x), histogram)
			self._histpdfs[input_value] = RooHistPdf(histogram.GetName() + "dh0", histogram.GetName() + "dh0", 
																			RooArgSet(self._x), self._datahists[input_value])

	def make_interpolation(self, int_val):
		print "[HistogramInterpolator::make_interpolation] INFO : Making interpolation for mass {}".format(int_val)
		# Find neighboring input values
		left_index = -1
		left_val = -1.
		right_val = -1.
		for index in xrange(len(self._input_values) - 1):
			if self._input_values[index] < int_val < self._input_values[index + 1]:
				left_index = index
				left_val = self._input_values[index]
				right_val = self._input_values[index + 1]
				break
		if left_index == -1:
			print "[HistogramInterpolator::make_interpolation] ERROR : Interpolation value {} is outside range of input values ({})".format(int_val, self._input_values)
			sys.exit(1)

		# Ensure left and right histograms have entries (RooIntegralMorph crashes otherwise)
		if self._hists[left_val].GetEntries() < 10 or self._hists[right_val].GetEntries() < 10:
			print "[HistogramInterpolator::make_interpolation] WARNING : Left and/or right histogram has low number of entries (left={}, right={}). Setting output to zero.".format(self._hists[left_val].GetEntries(), self._hists[right_val].GetEntries())
			int_hist = self._hists[left_val].Clone()
			int_hist.SetName("interpolated_hist_{}".format(int_val))
			int_hist.Reset()
			return int_hist

		# Do morphing using RooIntegralMorph
		alpha = 1. - float(int_val - left_val) / (right_val - left_val)
		print "[HistogramInterpolator::make_interpolation] INFO : Adjacent masses = {}, {}, alpha = {}".format(left_val, right_val, alpha)
		alpha_var = RooRealVar("alpha", "alpha", 0, 1)
		alpha_var.setVal(alpha)
		morpher = RooIntegralMorph("morpher", "morpher", self._histpdfs[left_val], self._histpdfs[right_val], self._x, alpha_var)
		alpha_var.setVal(alpha)
		int_hist = morpher.createHistogram("interpolated_hist_{}".format(int_val), self._x)

		# Normalize using linear interpolation of histogram integrals
		left_norm = self._hists[left_val].Integral()
		right_norm = self._hists[right_val].Integral()
		int_norm = left_norm + (right_norm - left_norm)*(1. - alpha)
		int_hist.Scale(int_norm)

		return int_hist

	def get_adjacent_histograms(self, int_val):
		'''
			Get the adjacent histograms for a given interpolation value that would be used to generate the interpolation
		'''
		# Find neighboring input values
		left_index = -1
		left_val = -1.
		right_val = -1.
		for index in xrange(len(self._input_values) - 1):
			if self._input_values[index] < int_val < self._input_values[index + 1]:
				left_index = index
				left_val = self._input_values[index]
				right_val = self._input_values[index + 1]
				break
		if left_index == -1:
			print "[HistogramInterpolator::get_adjacent_histograms] ERROR : Interpolation value {} is outside range of input values ({})".format(int_val, self._input_values)
			sys.exit(1)
		return {left_val:self._hists[left_val], right_val:self._hists[right_val]}
