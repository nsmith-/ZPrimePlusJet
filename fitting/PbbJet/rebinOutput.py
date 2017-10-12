import ROOT as rt
from optparse import OptionParser
from array import array


def rebin1D(hist, x):
    hist.Rebin(len(x)-1,hist.GetName()+'_rebin',x)
    hist_rebin = rt.gDirectory.Get(hist.GetName()+'_rebin')
    hist_rebin.SetDirectory(0)
    return hist_rebin

def rebin2D(hist, x, y):
    hist_rebin = rt.TH2F(hist.GetName()+'_rebin',hist.GetTitle(),len(x)-1,x,len(y)-1,y)
    for i in range(1,hist_rebin.GetNbinsX()+1):
        for j in range(1,hist_rebin.GetNbinsY()+1):
            hist_rebin.SetBinContent(i,j,hist.GetBinContent(hist.FindBin(x[i-1],y[j-1])))
            hist_rebin.SetBinError(i,j,hist.GetBinError(hist.FindBin(x[i-1],y[j-1])))
    return hist_rebin

if __name__ == '__main__':
    parser = OptionParser()

    (options, args) = parser.parse_args()

    msd_binBoundaries = range(68,607,7)
    pt_binBoundaries = [450, 500, 550, 600, 675, 800, 1000]
    x = array('d',msd_binBoundaries)
    y = array('d',pt_binBoundaries)
    for arg in args:
        tfile_rebin = rt.TFile.Open(arg.replace('.root','_rebin.root'),'RECREATE')
        tfile = rt.TFile.Open(arg,'READ')
        for key in tfile.GetListOfKeys():
            hist = tfile.Get(key.GetName())            
            if isinstance(hist, rt.TH2):
                hist_rebin = rebin2D(hist,x,y)
            else:
                hist_rebin = rebin1D(hist,x)
            tfile_rebin.cd()
            hist_rebin.Write(hist.GetName())
            

        
