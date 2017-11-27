import os
import sys
from ROOT import *
from DAZSLE.ZPrimePlusJet.RootIterator import RootIterator

def reset(w, fr, exclude=None):
    for p in RootIterator(fr.floatParsFinal()):
        if exclude is not None and exclude in p.GetName(): continue
        if w.var(p.GetName()):
            print 'setting %s = %e +/- %e from %s' % (p.GetName(), p.getVal(), p.getError(), fr.GetName())
            w.var(p.GetName()).setVal(p.getVal())
            w.var(p.GetName()).setError(p.getError())
    return True

def prefit(base_path, rhalphabase_path, fix_pars={}, fix_pars_rhalphabet={}, signal_names=[], background_names=["wqq", "zqq", "qcd", "tqq", "hqq125","tthqq125","vbfhqq125","whqq125","zhqq125"]):
    # Save copy of original workspaces
    os.system("cp {} {}.original".format(base_path, base_path))
    os.system("cp {} {}.original".format(rhalphabase_path, rhalphabase_path))

    print "\n\n*** PREFIT ***"
    fbase = TFile.Open(base_path, 'update')
    fbase.ls()
    fralphabase = TFile.Open(rhalphabase_path, 'update')
    fralphabase.ls()
    categories = ['pass_cat1', 'pass_cat2', 'pass_cat3', 'pass_cat4', 'pass_cat5', 'pass_cat6',
                  'fail_cat1', 'fail_cat2', 'fail_cat3', 'fail_cat4', 'fail_cat5', 'fail_cat6']

    wbase = {}
    wralphabase = {}
    for cat in categories:
        wbase[cat] = fbase.Get('w_%s' % cat)
        wralphabase[cat] = fralphabase.Get('w_%s' % cat)
        for parname, parval in fix_pars.iteritems():
            if wbase[cat].var(parname):
                wbase[cat].var(parname).setVal(parval)
                wbase[cat].var(parname).setConstant(True)
            else:
                print "[rhalphabet_builder::prefit] WARNING : parameter {} doesn't exist, ignoring".format(parname)

        for parname, parval in fix_pars_rhalphabet.iteritems():
            if wralphabase[cat].var(parname):
                wralphabase[cat].var(parname).setVal(parval)
                wralphabase[cat].var(parname).setConstant(True)
            else:
                print "[rhalphabet_builder::prefit] WARNING : parameter {} doesn't exist in workspace {}, ignoring".format(parname, 'w_%s' % cat)

    w = RooWorkspace('w')
    w.factory('mu[1.,0.,20.]')
    x = wbase[categories[0]].var('x')
    rooCat = RooCategory('cat', 'cat')

    mu = w.var('mu')
    epdf_b = {}
    epdf_s = {}
    datahist = {}
    histpdf = {}
    histpdfnorm = {}
    data = {}
    signorm = {}
    for cat in categories:
        rooCat.defineType(cat)

    for cat in categories:
        norms_b = RooArgList()
        norms_s = RooArgList()
        norms_b.add(wralphabase[cat].function('qcd_%s_norm' % cat))
        norms_s.add(wralphabase[cat].function('qcd_%s_norm' % cat))
        pdfs_b = RooArgList()
        pdfs_s = RooArgList()
        pdfs_b.add(wralphabase[cat].pdf('qcd_%s' % cat))
        pdfs_s.add(wralphabase[cat].pdf('qcd_%s' % cat))

        if not wbase[cat]:
            print "ERROR : wbase[{}] doesn't exist! Printing file...".format(cat)
            fbase.ls()
        data[cat] = wbase[cat].data('data_obs_%s' % cat)
        for proc in (background_names + signal_names):
            if proc == 'qcd': 
                continue

            datahist['%s_%s' % (proc, cat)] = wbase[cat].data('%s_%s' % (proc, cat))
            if not datahist['%s_%s' % (proc, cat)]:
                print "ERROR : Couldn't load data {}_{} from workspace {} in file {}".format(proc, cat, "w_"+cat, fbase.GetPath())
                sys.exit(1)
            histpdf['%s_%s' % (proc, cat)] = RooHistPdf('histpdf_%s_%s' % (proc, cat),
                                                          'histpdf_%s_%s' % (proc, cat),
                                                          RooArgSet(wbase[cat].var('x')),
                                                          datahist['%s_%s' % (proc, cat)])
            getattr(w, 'import')(datahist['%s_%s' % (proc, cat)], RooFit.RecycleConflictNodes())
            getattr(w, 'import')(histpdf['%s_%s' % (proc, cat)], RooFit.RecycleConflictNodes())
            if proc in signal_names:
                # signal
                signorm['%s_%s' % (proc, cat)] = RooRealVar('signorm_%s_%s' % (proc, cat),
                                                              'signorm_%s_%s' % (proc, cat),
                                                              datahist['%s_%s' % (proc, cat)].sumEntries(),
                                                              0, 10. * datahist['%s_%s' % (proc, cat)].sumEntries())
                signorm['%s_%s' % (proc, cat)].setConstant(True)
                getattr(w, 'import')(signorm['%s_%s' % (proc, cat)], RooFit.RecycleConflictNodes())
                histpdfnorm['%s_%s' % (proc, cat)] = RooFormulaVar('histpdfnorm_%s_%s' % (proc, cat),
                                                                     '@0*@1', RooArgList(mu, signorm[
                        '%s_%s' % (proc, cat)]))
                pdfs_s.add(histpdf['%s_%s' % (proc, cat)])
                norms_s.add(histpdfnorm['%s_%s' % (proc, cat)])
            else:
                # background
                histpdfnorm['%s_%s' % (proc, cat)] = RooRealVar('histpdfnorm_%s_%s' % (proc, cat),
                                                                  'histpdfnorm_%s_%s' % (proc, cat),
                                                                  datahist['%s_%s' % (proc, cat)].sumEntries(),
                                                                  0, 10. * datahist[
                                                                      '%s_%s' % (proc, cat)].sumEntries())
                histpdfnorm['%s_%s' % (proc, cat)].setConstant(True)
                getattr(w, 'import')(histpdfnorm['%s_%s' % (proc, cat)], RooFit.RecycleConflictNodes())
                pdfs_b.add(histpdf['%s_%s' % (proc, cat)])
                pdfs_s.add(histpdf['%s_%s' % (proc, cat)])
                norms_b.add(histpdfnorm['%s_%s' % (proc, cat)])
                norms_s.add(histpdfnorm['%s_%s' % (proc, cat)])

        epdf_b[cat] = RooAddPdf('epdf_b_' + cat, 'epdf_b_' + cat, pdfs_b, norms_b)
        epdf_s[cat] = RooAddPdf('epdf_s_' + cat, 'epdf_s_' + cat, pdfs_s, norms_s)

        getattr(w, 'import')(epdf_b[cat], RooFit.RecycleConflictNodes())
        getattr(w, 'import')(epdf_s[cat], RooFit.RecycleConflictNodes())

    ## arguments = ["data_obs","data_obs",RooArgList(x),rooCat]

    ## m = std.map('string, RooDataHist*')()
    ## for cat in categories:
    ##    m.insert(std.pair('string, RooDataHist*')(cat, data[cat]))
    ## arguments.append(m)

    ## combData = getattr(r,'RooDataHist')(*arguments)

    cat = categories[0]
    args = data[cat].get(0)

    combiner = CombDataSetFactory(args, rooCat)

    for cat in categories:
        combiner.addSetBin(cat, data[cat])
    combData = combiner.done('data_obs', 'data_obs')

    simPdf_b = RooSimultaneous('simPdf_b', 'simPdf_b', rooCat)
    simPdf_s = RooSimultaneous('simPdf_s', 'simPdf_s', rooCat)
    for cat in categories:
        simPdf_b.addPdf(epdf_b[cat], cat)
        simPdf_s.addPdf(epdf_s[cat], cat)

    mu.setVal(1.)

    getattr(w, 'import')(simPdf_b, RooFit.RecycleConflictNodes())
    getattr(w, 'import')(simPdf_s, RooFit.RecycleConflictNodes())
    getattr(w, 'import')(combData, RooFit.RecycleConflictNodes())

    simPdf_b = w.pdf('simPdf_b')
    simPdf_s = w.pdf('simPdf_s')
    combData = w.data('data_obs')
    x = w.var('x')
    rooCat = w.cat('cat')
    mu = w.var('mu')
    CMS_set = RooArgSet()
    CMS_set.add(rooCat)
    CMS_set.add(x)

    opt = RooLinkedList()
    opt.Add(RooFit.CloneData(False))
    allParams = simPdf_b.getParameters(combData)
    RooStats.RemoveConstantParameters(allParams)
    opt.Add(RooFit.Constrain(allParams))

    mu.setVal(0.)
    mu.setConstant(True)

    nll = simPdf_s.createNLL(combData)
    m2 = RooMinimizer(nll)
    m2.setStrategy(2)
    m2.setMaxFunctionCalls(100000)
    m2.setMaxIterations(100000)
    m2.setPrintLevel(-1)
    m2.setPrintEvalErrors(-1)
    m2.setEps(1e-5)
    m2.optimizeConst(2)

    migrad_status = m2.minimize('Minuit2', 'migrad')
    improve_status = m2.minimize('Minuit2', 'improve')
    hesse_status = m2.minimize('Minuit2', 'hesse')
    fr = m2.save()

    icat = 0
    for cat in categories:
        for parname, parval in fix_pars.iteritems():
            if wbase[cat].var(parname):
                wbase[cat].var(parname).setConstant(False)
        for parname, parval in fix_pars_rhalphabet.iteritems():
            if wralphabase[cat].var(parname):
                wralphabase[cat].var(parname).setConstant(False)
        reset(wralphabase[cat], fr)
        if icat == 0:
            getattr(wralphabase[cat], 'import')(fr)
            wralphabase[cat].writeToFile(rhalphabase_path, True)
        else:
            wralphabase[cat].writeToFile(rhalphabase_path, False)
        icat += 1

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Prefit a workspace")
    parser.add_argument("--base_path", type=str, help="Path to base.root")
    parser.add_argument("--rhalphabase_path", type=str, help="Path to rhalphabase.root")
    parser.add_argument("--fix_pars", type=str, help="Parameters in base.root to fix (syntax parname:parvalue,...)")
    parser.add_argument("--fix_pars_rhalphabet", type=str, help="Parameters in rhalphabase.root to fix")
    parser.add_argument("--signals", type=str, help="Signal names")
    args = parser.parse_args()

    fix_pars = {}
    if args.fix_pars:
        for nameval in [x.split(":") for x in args.fix_pars.split(",")]:
            fix_pars[nameval[0]] = float(nameval[1])
    fix_pars_rhalphabet = {}
    if args.fix_pars_rhalphabet:
        for nameval in [x.split(":") for x in args.fix_pars_rhalphabet.split(",")]:
            print nameval
            fix_pars_rhalphabet[nameval[0]] = float(nameval[1])

    prefit(args.base_path, args.rhalphabase_path, fix_pars=fix_pars, fix_pars_rhalphabet=fix_pars_rhalphabet, signal_names=args.signals.split(","))
