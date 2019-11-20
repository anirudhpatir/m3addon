def doubletdetection_py(X, boost_rate, n_components, n_top_var_genes, use_phenograph, n_iters, verbose, standard_scaling, \
                        p_thresh, voter_thresh):
  import doubletdetection
  if use_phenograph:
    phenograph_parameters = {"prune":True}
  clf = doubletdetection.BoostClassifier(boost_rate=boost_rate, n_components=int(n_components), n_top_var_genes=int(n_top_var_genes), use_phenograph=use_phenograph, \
                        phenograph_parameters=phenograph_parameters, n_iters=int(n_iters), verbose=verbose, standard_scaling=standard_scaling)
  # raw_counts is a cells by genes count matrix
  labels = clf.fit(X).predict(float(p_thresh), float(voter_thresh))
  return(labels)
