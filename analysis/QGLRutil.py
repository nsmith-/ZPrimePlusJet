import math,ROOT

def deltaPhi(phi1, phi2):
  PHI = abs(phi1-phi2)
  if PHI<=math.pi:
      return PHI
  else:
      return 2*math.pi-PHI

def deltaR(eta1, phi1, eta2, phi2):
  deta = eta1-eta2
  dphi = deltaPhi(phi1,phi2)
  return math.sqrt(deta*deta + dphi*dphi)

def SortByCSV(vect):
    vect.sort(key=lambda x: x.csv, reverse=False)

def FindHighestDeta_qq(QuarkJets):
    nQuarkJets = len(QuarkJets)
    if nQuarkJets>1:
        jetPairs =[]                # List of jet indexes
        deltaEtaQQ = []
        for i in range(0,nQuarkJets):
            for j in range(0,nQuarkJets):
                if not (i==j) and j>i:
                    jetPairs.append((i,j))
        for iPair in jetPairs:
            i  = iPair[0]   #first jet
            j  = iPair[1]   #2nd jet 
            deltaEtaQQ.append( abs(QuarkJets[i].Eta()-QuarkJets[j].Eta()))
        print deltaEtaQQ
        print "max deltaEtaQQ = ", max(deltaEtaQQ), jetPairs[deltaEtaQQ.index(max(deltaEtaQQ))]
        return  max(deltaEtaQQ), jetPairs[deltaEtaQQ.index(max(deltaEtaQQ))]
    else:
        return  -1,(0,0) 

def CalcMqq(QuarkJets, pair):
    if len(QuarkJets)>=2:
        return (QuarkJets[pair[0]]+QuarkJets[pair[1]]).M()
    else:
        return -1
def CalcQGLR(QuarkJets,pair):
    if len(QuarkJets)>=2:
        qgid_0 = QuarkJets[pair[0]].qgid
        qgid_1 = QuarkJets[pair[1]].qgid
        QGLR = -1
        if (qgid_0*qgid_1 + (1-qgid_0)*(1-qgid_1)) != 0:
            QGLR = qgid_0 * qgid_1 / ( (qgid_0*qgid_1 + (1-qgid_0)*(1-qgid_1)) )
        return QGLR
    else:
        return -1

##----##----##----##----##----##----##
if __name__ == '__main__':
    #f = ROOT.TFile("/eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.07-puWeight/norm/VBFHToBB_M_125_13TeV_powheg_pythia8_weightfix_1000pb_weighted.root")
    f = ROOT.TFile("/eos/uscms/store/user/lpchbb/zprimebits-v12.04/cvernier/TT_powheg_1000pb_weighted_v1204.root")
    t = f.Get("otree")
    for i,evt in enumerate(t):
        if i>20: break
        print "new Event"
        QuarkJets = []
        for i in range(0,4):
            ak4pT   = getattr(t,"AK4Puppijet"+str(i)+"_pt")
            ak4eta  = getattr(t,"AK4Puppijet"+str(i)+"_eta")
            ak4phi  = getattr(t,"AK4Puppijet"+str(i)+"_phi")
            ak4mass = getattr(t,"AK4Puppijet"+str(i)+"_mass")
            dR_ak8  = deltaR( ak4eta,ak4phi, t.AK8Puppijet0_eta, t.AK8Puppijet0_phi)
            print ak4pT, dR_ak8
            if ak4pT> 30.0 and dR_ak8>0.3:
                jet = ROOT.TLorentzVector()
                jet.SetPtEtaPhiM(ak4pT,ak4eta,ak4phi,ak4mass)
                jet.qgid = getattr(t,"AK4Puppijet"+str(i)+"_qgid")
                jet.csv = getattr(t,"AK4Puppijet"+str(i)+"_csv")
                QuarkJets.append(jet)
                print jet.Eta()
        print "N un-matched jet = ", len(QuarkJets)
        maxdEtaQQ, pair = FindHighestDeta_qq(QuarkJets)
        print "highest dEta pair = ",pair, "mass = %.3f, QGLR = %.3f"%(CalcMqq(QuarkJets,pair),CalcQGLR(QuarkJets,pair))
