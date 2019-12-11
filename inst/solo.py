#!/usr/bin/env python
def solo(X, gene_names, doublet_depth=2.0, gpu=False, out_dir ='solo_out', doublet_ratio=2.0, seed=None, known_doublets=None, doublet_type='multinomial', expected_number_of_doublets=None, plot=False, normal_logging=False, n_hidden = 128, n_latent = 16, cl_hidden= 64, cl_layers = 1, dropout_rate = 0.1, learning_rate=0.001, valid_pct=0.1):
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    import json
    import os
    import shutil
    import anndata
    import numpy as np
    from anndata import AnnData
    from sklearn.metrics import roc_auc_score, roc_curve
    from scipy.sparse import issparse
    from collections import defaultdict
    import scvi
    from scvi.dataset import AnnDatasetFromAnnData, LoomDataset, GeneExpressionDataset
    from scvi.models import Classifier, VAE
    from scvi.inference import UnsupervisedTrainer, ClassifierTrainer
    import torch
    from solo.utils import create_average_doublet, create_summed_doublet, create_multinomial_doublet, make_gene_expression_dataset
    if not normal_logging:
      scvi._settings.set_verbosity(10)
    if gpu and not torch.cuda.is_available():
      gpu = torch.cuda.is_available()
      print('Cuda is not available, switching to cpu running!')
    # if not os.path.isdir(out_dir):
    #     os.mkdir(out_dir)
    # data_ext = os.path.splitext(data_file)[-1]
    # if data_ext == '.loom':
    #     scvi_data = LoomDataset(data_file)
    # elif data_ext == '.h5ad':
    #     scvi_data = AnnDatasetFromAnnData(anndata.read(data_file))
    # else:
    #     msg = f'{data_ext} is not a recognized format.\n'
    #     msg += 'must be one of {h5ad, loom}'
    #     raise TypeError(msg)
    # if issparse(scvi_data.X):
    #     scvi_data.X = scvi_data.X.todense()
    scvi_data = make_gene_expression_dataset(X, gene_names)
    num_cells, num_genes = scvi_data.X.shape
    if known_doublets is not None:
      print('Removing known doublets for in silico doublet generation')
      print('Make sure known doublets are in the same order as your data')
      known_doublets = np.loadtxt(known_doublets, dtype=str) == 'True'
      assert len(known_doublets) == scvi_data.X.shape[0]
      known_doublet_data = make_gene_expression_dataset(
          scvi_data.X[known_doublets],
          scvi_data.gene_names)
      known_doublet_data.labels = np.ones(known_doublet_data.X.shape[0])
      singlet_scvi_data = make_gene_expression_dataset(
          scvi_data.X[~known_doublets],
          scvi_data.gene_names)
      singlet_num_cells, _ = singlet_scvi_data.X.shape
    else:
      known_doublet_data = None
      singlet_num_cells = num_cells
      known_doublets = np.zeros(num_cells, dtype=bool)
      singlet_scvi_data = scvi_data
    singlet_scvi_data.labels = np.zeros(singlet_scvi_data.X.shape[0])
    scvi_data.labels = known_doublets.astype(int)
    params = {
    "n_hidden": n_hidden,
    "n_latent": n_latent,
    "cl_hidden": cl_hidden,
    "cl_layers": cl_layers,
    "dropout_rate": dropout_rate,
    "learning_rate": learning_rate,
    "valid_pct": valid_pct
    }
    # set VAE params
    vae_params = {}
    for par in ['n_hidden', 'n_latent', 'n_layers', 'dropout_rate', 'ignore_batch']:
      if par in params:
          vae_params[par] = params[par]
    vae_params['n_batch'] = 0 if params.get(
        'ignore_batch', False) else scvi_data.n_batches
    # training parameters
    valid_pct = params.get('valid_pct', 0.1)
    learning_rate = params.get('learning_rate', 1e-3)
    stopping_params = {'patience': params.get('patience', 10), 'threshold': 0}
    ##################################################
    # VAE
    vae = VAE(n_input=singlet_scvi_data.nb_genes, n_labels=2,
              reconstruction_loss='nb',
              log_variational=True, **vae_params)
    if seed:
        if gpu:
            device = torch.device('cuda')
            vae.load_state_dict(torch.load(os.path.join(seed, 'vae.pt')))
            vae.to(device)
        else:
            map_loc = 'cpu'
            vae.load_state_dict(torch.load(os.path.join(seed, 'vae.pt'),
                                           map_location=map_loc))
        # copy latent representation
        latent_file = os.path.join(seed, 'latent.npy')
        if os.path.isfile(latent_file):
            shutil.copy(latent_file, os.path.join(out_dir, 'latent.npy'))
    else:
        stopping_params['early_stopping_metric'] = 'reconstruction_error'
        stopping_params['save_best_state_metric'] = 'reconstruction_error'
        # initialize unsupervised trainer
        utrainer = \
            UnsupervisedTrainer(vae, singlet_scvi_data,
                                train_size=(1. - valid_pct),
                                frequency=2,
                                metrics_to_monitor=['reconstruction_error'],
                                use_cuda=gpu,
                                early_stopping_kwargs=stopping_params)
        utrainer.history['reconstruction_error_test_set'].append(0)
        # initial epoch
        utrainer.train(n_epochs=2000, lr=learning_rate)
        # drop learning rate and continue
        utrainer.early_stopping.wait = 0
        utrainer.train(n_epochs=500, lr=0.5 * learning_rate)
        # save VAE
        torch.save(vae.state_dict(), os.path.join(out_dir, 'vae.pt'))
        # save latent representation
        full_posterior = utrainer.create_posterior(
            utrainer.model,
            singlet_scvi_data,
            indices=np.arange(len(singlet_scvi_data)))
        latent, _, _ = full_posterior.sequential().get_latent()
        np.save(os.path.join(out_dir, 'latent.npy'),
                latent.astype('float32'))
    ##################################################
    # simulate doublets
    non_zero_indexes = np.where(singlet_scvi_data.X > 0)
    cells = non_zero_indexes[0]
    genes = non_zero_indexes[1]
    cells_ids = defaultdict(list)
    for cell_id, gene in zip(cells, genes):
        cells_ids[cell_id].append(gene)
    # choose doublets function type
    if doublet_type == 'average':
        doublet_function = create_average_doublet
    elif doublet_type == 'sum':
        doublet_function = create_summed_doublet
    else:
        doublet_function = create_multinomial_doublet
    cell_depths = singlet_scvi_data.X.sum(axis=1)
    num_doublets = int(doublet_ratio * singlet_num_cells)
    if known_doublet_data is not None:
        num_doublets -= known_doublet_data.X.shape[0]
        # make sure we are making a non negative amount of doublets
        assert num_doublets >= 0
    in_silico_doublets = np.zeros((num_doublets, num_genes), dtype='float32')
    # for desired # doublets
    for di in range(num_doublets):
        # sample two cells
        i, j = np.random.choice(singlet_num_cells, size=2)
        # generate doublets
        in_silico_doublets[di, :] = \
            doublet_function(singlet_scvi_data.X, i, j,
                             doublet_depth=doublet_depth,
                             cell_depths=cell_depths, cells_ids=cells_ids)
    # merge datasets
    # we can maybe up sample the known doublets
    # concatentate
    classifier_data = GeneExpressionDataset()
    classifier_data.populate_from_data(
        X=np.vstack([scvi_data.X,
                     in_silico_doublets]),
        labels=np.hstack([np.ravel(scvi_data.labels),
                          np.ones(in_silico_doublets.shape[0])]),
        remap_attributes=False)
    assert(len(np.unique(classifier_data.labels.flatten())) == 2)
    ##################################################
    # classifier
    # model
    classifier = Classifier(n_input=(vae.n_latent + 1),
                            n_hidden=params['cl_hidden'],
                            n_layers=params['cl_layers'], n_labels=2,
                            dropout_rate=params['dropout_rate'])
    # trainer
    stopping_params['early_stopping_metric'] = 'accuracy'
    stopping_params['save_best_state_metric'] = 'accuracy'
    strainer = ClassifierTrainer(classifier, classifier_data,
                                 train_size=(1. - valid_pct),
                                 frequency=2, metrics_to_monitor=['accuracy'],
                                 use_cuda=gpu,
                                 sampling_model=vae, sampling_zl=True,
                                 early_stopping_kwargs=stopping_params)
    # initial
    strainer.train(n_epochs=1000, lr=learning_rate)
    # drop learning rate and continue
    strainer.early_stopping.wait = 0
    strainer.train(n_epochs=300, lr=0.1 * learning_rate)
    torch.save(classifier.state_dict(), os.path.join(out_dir, 'classifier.pt'))
    ##################################################
    # post-processing
    # use logits for predictions for better results
    logits_classifier = Classifier(n_input=(vae.n_latent + 1),
                                   n_hidden=params['cl_hidden'],
                                   n_layers=params['cl_layers'], n_labels=2,
                                   dropout_rate=params['dropout_rate'],
                                   logits=True)
    logits_classifier.load_state_dict(classifier.state_dict())
    # using logits leads to better performance in for ranking
    logits_strainer = ClassifierTrainer(logits_classifier, classifier_data,
                                        train_size=(1. - valid_pct),
                                        frequency=2,
                                        metrics_to_monitor=['accuracy'],
                                        use_cuda=gpu,
                                        sampling_model=vae, sampling_zl=True,
                                        early_stopping_kwargs=stopping_params)
    # models evaluation mode
    vae.eval()
    classifier.eval()
    logits_classifier.eval()
    print('Train accuracy: %.4f' % strainer.train_set.accuracy())
    print('Test accuracy:  %.4f' % strainer.test_set.accuracy())
    # compute predictions manually
    # output logits
    train_y, train_score = strainer.train_set.compute_predictions(soft=True)
    test_y, test_score = strainer.test_set.compute_predictions(soft=True)
    # train_y == true label
    # train_score[:, 0] == singlet score; train_score[:, 1] == doublet score
    train_score = train_score[:, 1]
    train_y = train_y.astype('bool')
    test_score = test_score[:, 1]
    test_y = test_y.astype('bool')
    train_auroc = roc_auc_score(train_y, train_score)
    test_auroc = roc_auc_score(test_y, test_score)
    print('Train AUROC: %.4f' % train_auroc)
    print('Test AUROC:  %.4f' % test_auroc)
    train_fpr, train_tpr, train_t = roc_curve(train_y, train_score)
    test_fpr, test_tpr, test_t = roc_curve(test_y, test_score)
    train_t = np.minimum(train_t, 1 + 1e-9)
    test_t = np.minimum(test_t, 1 + 1e-9)
    train_acc = np.zeros(len(train_t))
    for i in range(len(train_t)):
        train_acc[i] = np.mean(train_y == (train_score > train_t[i]))
    test_acc = np.zeros(len(test_t))
    for i in range(len(test_t)):
        test_acc[i] = np.mean(test_y == (test_score > test_t[i]))
    # write predictions
    # softmax predictions
    order_y, order_score = strainer.compute_predictions(soft=True)
    _, order_pred = strainer.compute_predictions()
    doublet_score = order_score[:, 1]
    np.save(os.path.join(out_dir, 'softmax_scores.npy'), doublet_score[:num_cells])
    np.save(os.path.join(out_dir, 'softmax_scores_sim.npy'), doublet_score[num_cells:])
    # logit predictions
    logit_y, logit_score = logits_strainer.compute_predictions(soft=True)
    logit_doublet_score = logit_score[:, 1]
    np.save(os.path.join(out_dir, 'logit_scores.npy'), logit_doublet_score[:num_cells])
    np.save(os.path.join(out_dir, 'logit_scores_sim.npy'), logit_doublet_score[num_cells:])
    if expected_number_of_doublets is not None:
        solo_scores = doublet_score[:num_cells]
        k = len(solo_scores) - expected_number_of_doublets
        if expected_number_of_doublets / len(solo_scores) > .5:
          print('Make sure you actually expect more than half your cells to be doublets. If not change your -e parameter value')
        assert k > 0
        idx = np.argpartition(solo_scores, k)
        threshold = np.max(solo_scores[idx[:k]])
        is_solo_doublet = doublet_score > threshold
    else:
        is_solo_doublet = order_pred[:num_cells]
    is_doublet = known_doublets
    new_doublets_idx = np.where(~(is_doublet) & is_solo_doublet[:num_cells])[0]
    is_doublet[new_doublets_idx] = True
    np.save(os.path.join(out_dir, 'is_doublet.npy'), is_doublet[:num_cells])
    np.save(os.path.join(out_dir, 'is_doublet_sim.npy'), is_doublet[num_cells:])
    np.save(os.path.join(out_dir, 'preds.npy'), order_pred[:num_cells])
    np.save(os.path.join(out_dir, 'preds_sim.npy'), order_pred[num_cells:])
    if plot:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns
        # plot ROC
        plt.figure()
        plt.plot(train_fpr, train_tpr, label='Train')
        plt.plot(test_fpr, test_tpr, label='Test')
        plt.gca().set_xlabel('False positive rate')
        plt.gca().set_ylabel('True positive rate')
        plt.legend()
        plt.savefig(os.path.join(out_dir, 'roc.pdf'))
        plt.close()
        # plot accuracy
        plt.figure()
        plt.plot(train_t, train_acc, label='Train')
        plt.plot(test_t, test_acc, label='Test')
        plt.axvline(0.5, color='black', linestyle='--')
        plt.gca().set_xlabel('Threshold')
        plt.gca().set_ylabel('Accuracy')
        plt.legend()
        plt.savefig(os.path.join(out_dir, 'accuracy.pdf'))
        plt.close()
        # plot distributions
        plt.figure()
        sns.distplot(test_score[test_y], label='Simulated')
        sns.distplot(test_score[~test_y], label='Observed')
        plt.legend()
        plt.savefig(os.path.join(out_dir, 'train_v_test_dist.pdf'))
        plt.close()
        plt.figure()
        sns.distplot(doublet_score[:num_cells], label='Simulated')
        plt.legend()
        plt.savefig(os.path.join(out_dir, 'real_cells_dist.pdf'))
        plt.close()
###############################################################################
# __main__
###############################################################################
# if __name__ == '__main__':
#     main()
