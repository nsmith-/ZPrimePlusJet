{  
  //gSystem->Load("/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/CMSSW_7_4_12_patch1/src/MonoX/../../lib/slc6_amd64_gcc491/libHiggsAnalysisCombinedLimit.so");
  if(gSystem->Getenv("CMSSW_VERSION")) {
    cout << "===> rootfit" << endl;
    TString rfitpath("/cvmfs/cms.cern.ch/slc6_amd64_gcc481/lcg/roofit/5.34.18-cms4/include");
    TString path = gSystem->GetIncludePath();
    path += "-I. -I$ROOTSYS/src -I";
    path += rfitpath;
    gSystem->SetIncludePath(path.Data());
    TString str = gSystem->GetMakeSharedLib();
    if (str.Contains("-m32")==0 && str.Contains("-m64")==0) {
      str.ReplaceAll("g++", "g++ -m32");
      gSystem->SetMakeSharedLib(str);
    }      
  }
  gSystem->Load("/afs/cern.ch/user/p/pharris/pharris/public/bacon/prod/CMSSW_7_1_20/lib/slc6_amd64_gcc481/libHiggsAnalysisCombinedLimit.so");
  //gSystem->Load("RooParametricHist_cxx.so");

}
