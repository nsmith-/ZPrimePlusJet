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


    for arg in args:
        tfile_rebin = rt.TFile.Open(arg.replace('.root','_rebin.root'),'RECREATE')
        tfile = rt.TFile.Open(arg,'READ')
        if 'CA15' in arg:
            #msd_binBoundaries = range(47,299+7,7) # muon CR
            msd_binBoundaries = range(82,600+7,7) # SR
            pt_binBoundaries = [450, 500, 550, 600, 675, 800, 1000]
        elif 'AK8' in arg:
            msd_binBoundaries = range(40,201+7,7) # muon CR
            pt_binBoundaries = [450, 500, 550, 600, 675, 800, 1000]
        x = array('d',msd_binBoundaries)
        y = array('d',pt_binBoundaries)
        for key in tfile.GetListOfKeys():
            hist = tfile.Get(key.GetName())            
            if isinstance(hist, rt.TH2):
                #hist_rebin = rebin2D(hist,x,y)
                for i in range(1,hist.GetNbinsX()+1):
                    for j in range(1,hist.GetNbinsY()+1):
                        if hist.GetXaxis().GetBinCenter(i) < x[0] or hist.GetXaxis().GetBinCenter(i) > x[-1]:
                            hist.SetBinContent(i,j,0)
                            hist.SetBinError(i,j,0)
            else:
                #hist_rebin = rebin1D(hist,x)
                for i in range(1,hist.GetNbinsX()+1):
                    if hist.GetXaxis().GetBinCenter(i) < x[0] or hist.GetXaxis().GetBinCenter(i) > x[-1]:
                        hist.SetBinContent(i,0)
                        hist.SetBinError(i,0)
            tfile_rebin.cd()
            #hist_rebin.Write(hist.GetName())
            hist.Write(hist.GetName())
            

        
