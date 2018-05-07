import ROOT as rt
import array
import os

if __name__ == '__main__':
    if not os.path.isfile('h2d.root'):
        
        idir_data = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpchbb/zprimebits-v12.05/'
        samples = {
            'QCD': [#idir_data + '/QCD_HT100to200_13TeV_1000pb_weighted.root',
                    #idir_data + '/QCD_HT200to300_13TeV_1000pb_weighted.root',
                    idir_data + '/QCD_HT300to500_13TeV_all_1000pb_weighted.root',
                    idir_data + '/QCD_HT500to700_13TeV_1000pb_weighted.root',
                    idir_data + '/QCD_HT700to1000_13TeV_1000pb_weighted.root',
                    idir_data + '/QCD_HT1000to1500_13TeV_1000pb_weighted.root',
                    idir_data + '/QCD_HT1500to2000_13TeV_all_1000pb_weighted.root',
                    idir_data + '/QCD_HT2000toInf_13TeV_all_1000pb_weighted.root']
            }
        tchain = rt.TChain('otree')

        for sample in samples['QCD']:
            tchain.Add(sample)

        out = rt.TFile.Open('h2d.root','recreate')    
        h2d_ak8_mass = rt.TH2D('h2d_ak8_mass','h2d_ak8_mass',70,0,500,6,400,1000)
        h2d_ak8_rho = rt.TH2D('h2d_ak8_rho','h2d_ak8_rho',70,-7,0,6,400,1000)
        h2d_ca15_mass = rt.TH2D('h2d_ca15_mass','h2d_ca15_mass',70,0,500,6,400,1000)
        h2d_ca15_rho = rt.TH2D('h2d_ca15_rho','h2d_ca15_rho',70,-7,0,6,400,1000)
        
        tchain.Project('h2d_ak8_mass','AK8Puppijet0_pt:AK8Puppijet0_msd','scale1fb')
        tchain.Project('h2d_ak8_rho','AK8Puppijet0_pt:log(AK8Puppijet0_msd*AK8Puppijet0_msd/AK8Puppijet0_pt/AK8Puppijet0_pt)','scale1fb')
        tchain.Project('h2d_ca15_mass','CA15Puppijet0_pt:CA15Puppijet0_msd','scale1fb')
        tchain.Project('h2d_ca15_rho','CA15Puppijet0_pt:log(CA15Puppijet0_msd*CA15Puppijet0_msd/CA15Puppijet0_pt/CA15Puppijet0_pt)','scale1fb')


        h2d_ak8_mass.Write()
        h2d_ak8_rho.Write()
        h2d_ca15_mass.Write()
        h2d_ca15_rho.Write()
    else:
        out = rt.TFile.Open('h2d.root','read')
        h2d = out.Get('h2d_ak8_mass')
        
        
        rt.gStyle.SetOptStat(0)
        rt.gStyle.SetOptTitle(0)
        c = rt.TCanvas('c','c',500,400)
        c.SetLeftMargin(0.12)
        for h2d in [out.Get('h2d_ak8_mass'), out.Get('h2d_ak8_rho'), 
                    out.Get('h2d_ca15_mass'), out.Get('h2d_ca15_rho')]:
            h1d_list = []
            color_list = [rt.kBlack, rt.kRed, rt.kBlue, rt.kMagenta, rt.kCyan, rt.kOrange]
            for j in range(1,h2d.GetYaxis().GetNbins()+1):
                h1d = h2d.ProjectionX('_px%i'%j,j,j)
                h1d.Scale(1./h1d.Integral())
                h1d_list.append(h1d)
            
            j = 0
            h1d_list[0].Draw("hist")
            h1d_list[0].SetLineColor(rt.kBlack)
            if 'ak8' in h2d.GetName():
                if 'rho' in h2d.GetName():
                    h1d_list[0].GetXaxis().SetTitle('AK8 #rho=log(m_{SD}^{2}/p_{T}^{2})')
                    h1d_list[0].GetXaxis().SetRangeUser(-6,-1)
                else:
                    h1d_list[0].GetXaxis().SetTitle('AK8 m_{SD}^{PUPPI} (GeV)')
                    h1d_list[0].GetXaxis().SetRangeUser(40,300)
            elif 'ca15' in h2d.GetName():
                if 'rho' in h2d.GetName():
                    h1d_list[0].GetXaxis().SetTitle('CA15 #rho=log(m_{SD}^{2}/p_{T}^{2})')
                    h1d_list[0].GetXaxis().SetRangeUser(-5,0)
                else:
                    h1d_list[0].GetXaxis().SetTitle('CA15 m_{SD}^{PUPPI} (GeV)')                
                    h1d_list[0].GetXaxis().SetRangeUser(40,500)
            h1d_list[0].GetYaxis().SetTitle('Probability (A. U.)')
            h1d_list[0].GetYaxis().SetTitleOffset(1.5)
            h1d_list[0].GetXaxis().SetTitleOffset(1.2)
            h1d_list[0].SetMaximum(1.5*h1d_list[0].GetMaximum())
            h1d_list[0].SetMinimum(0.)
            tleg = rt.TLegend(0.6,0.6,0.89,0.89)
            tleg.SetLineWidth(0)
            tleg.SetLineColor(0)
            tleg.SetFillStyle(0)
            tleg.AddEntry(h1d_list[0],'p_{T} = %i-%i GeV'%(h2d.GetYaxis().GetBinLowEdge(1), h2d.GetYaxis().GetBinUpEdge(1)), 'l')

            for h1d, color in zip(h1d_list[1:],color_list[1:]):
                j+=1
                h1d.SetLineColor(color)
                h1d.SetMarkerColor(color)
                h1d.Draw("histsame")
                tleg.AddEntry(h1d,'p_{T} = %i-%i GeV'%(h2d.GetYaxis().GetBinLowEdge(j+1), h2d.GetYaxis().GetBinUpEdge(j+1)), 'l')
                
            tleg.Draw()
            tag1 = rt.TLatex(0.15,0.85,"CMS")
            tag1.SetNDC()
            tag1.SetTextSize(0.05)
            tag1.SetTextFont(62)
            tag1.Draw()
            tag2 = rt.TLatex(0.25,0.85,"Simulation")
            tag2.SetNDC()
            tag2.SetTextSize(0.05)
            tag2.SetTextFont(52)
            tag2.Draw()
            tag3 = rt.TLatex(0.15,0.80,"SM QCD Multijet")
            tag3.SetNDC()
            tag3.SetTextSize(0.04)
            tag3.SetTextFont(42)
            tag3.Draw()
    


            c.SaveAs(h2d.GetName().replace('h2d','h1d')+'.pdf')
            c.SaveAs(h2d.GetName().replace('h2d','h1d')+'.C')
    
    
