#!/usr/bin/env python
import ROOT as rt,sys,math,os
import re


if __name__ == '__main__':

    for jet_type in ['CA15','AK8']:
        for region in ['muonCR','pt_scalesmear']:

            tfile_out = rt.TFile.Open('hist_1DZbb_%s_%s_interpolations_merge.root'%(region,jet_type),'recreate')
    
            tfile_new = rt.TFile.Open('hist_1DZbb_%s_%s_interpolations.root'%(region,jet_type),'read')
            for key in tfile_new.GetListOfKeys():
                if re.match('DMSbb',key.GetName()):
                    h = tfile_new.Get(key.GetName())
                    tfile_out.cd()
                    h.Write()
            tfile_old = rt.TFile.Open('hist_1DZbb_%s_%s_check.root'%(region,jet_type),'read')
            for key in tfile_old.GetListOfKeys():
                if not re.match('DMSbb',key.GetName()):
                    h = tfile_old.Get(key.GetName())
                    tfile_out.cd()
                    h.Write()

    
