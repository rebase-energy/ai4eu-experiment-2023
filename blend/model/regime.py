import numpy as np
import pandas as pd
from itertools import chain
from blend.model.auxiliary import create_groups, create_unique_groups, create_groups_range, create_kfold
from blend.model.ols import weighting_least_squares_concrete


def get_regimes(df_X, df_Y, n_regimes=range(1,7), step_size=1, n_best=None, kf_splits=2, kf_shuffle=True, kf_seed=None):

    min_value = 0 
    max_value = 23 

    if not isinstance(n_regimes, list): n_regimes = [n_regimes]

    if kf_splits >=2:
        kFold = create_kfold(kf_splits, kf_shuffle, kf_seed)

    iterables = [list(range(kf_splits)), ['weights', 'n_train', 'n_test', 'mae_train', 'mae_test']]
    train_results = pd.DataFrame(columns=pd.MultiIndex.from_product(iterables, names=['kfold', 'param']))

    for n_rgm in n_regimes:

        print('Solving weighting model for ', n_rgm, 'regimes')

        groups = create_groups(min_value, max_value, step_size, n_rgm)
        unique_groups = create_unique_groups(groups)

        # groups_range = create_groups_range(groups, step_size)
        unique_groups_range = create_groups_range(unique_groups, step_size)
        unique_groups_range = list(chain.from_iterable(unique_groups_range))


        idx1 = train_results.index
        idx2 = pd.Index(unique_groups_range, tupleize_cols=False)
        train_results = train_results.reindex(index = idx1.union(idx2))

        # Calculate weights and training scores for all unique regimes
        for gindx in unique_groups_range:

            rangemin = gindx[0]
            rangemax = gindx[1]

            idx = df_X.index[(df_X.index.hour >= rangemin)&(df_X.index.hour < rangemax)]


            if kf_splits >= 2:
                kfoldsplit = kFold.split(idx)
            else:
                kfoldsplit = [(np.array(range(len(idx))),np.array(range(len(idx))))]

            for kf, kfindx in enumerate(kfoldsplit):

                if train_results.loc[train_results.index == gindx,(kf,'weights')].isnull()[0]:

                    train_index = kfindx[0]
                    test_index = kfindx[1]

                    # Slice for regime and kfold
                    df_X_train = df_X.loc[idx[train_index],:]
                    df_Y_train = df_Y.loc[idx[train_index]]
                    df_X_test = df_X.loc[idx[test_index],:]
                    df_Y_test = df_Y.loc[idx[test_index]]

                    # Solve
                    weights, optvalue = weighting_least_squares_concrete(np.array(df_X_train),np.array(df_Y_train))

                    # Calculate errors
                    error_train = np.mean(np.abs(np.sum(np.array(df_X_train)*weights, axis=1)-np.array(df_Y_train)))
                    error_test = np.mean(np.abs(np.sum(np.array(df_X_test)*weights, axis=1)-np.array(df_Y_test)))

                    train_results.loc[train_results.index == gindx,(kf,'weights')] = [tuple(weights)]
                    train_results.loc[train_results.index == gindx,(kf,'n_train')] = df_Y_train.shape[0]
                    train_results.loc[train_results.index == gindx,(kf,'n_test')] = df_Y_test.shape[0]
                    train_results.loc[train_results.index == gindx,(kf,'mae_train')] = error_train 
                    train_results.loc[train_results.index == gindx,(kf,'mae_test')] = error_test

    train_score = pd.DataFrame(index = train_results.index)
    for gindx in train_score.index:   

        trainerrors = train_results.loc[[gindx],(slice(None),['mae_train'])]
        trainlengths = train_results.loc[[gindx],(slice(None),['n_train'])] 
        testerrors = train_results.loc[[gindx],(slice(None),['mae_test'])] 
        testlengths = train_results.loc[[gindx],(slice(None),['n_test'])]

        length_train = np.sum(np.array(trainlengths))
        error_train = np.sum(np.array(trainerrors)*np.array(trainlengths))/length_train
        length_test = np.sum(np.array(testlengths))
        error_test = np.sum(np.array(testerrors)*np.array(testlengths))/length_test

        train_score.loc[[gindx],'mae_train'] = error_train
        train_score.loc[[gindx],'mae_test'] = error_test
        train_score.loc[[gindx],'n_test'] = length_test


    scores = []
    for n_rgm in n_regimes:

        print('Calculating scores for ', n_rgm, 'regimes')

        groups = create_groups(min_value, max_value, step_size, n_rgm)
        groups_range = create_groups_range(groups, step_size)

        groups_range_all = list(chain(*groups_range))


        tsc = train_score.loc[groups_range_all,['mae_test','n_test']]
        
        # Assign group number
        gindex = (tsc.index.str[0] == 0).cumsum()

        # Calculate MAE scores in test set
        scores_df = pd.DataFrame(index = pd.MultiIndex.from_tuples(groups_range), columns=['score'])
        scores_df.loc[:,'score'] = (tsc['mae_test'].multiply(tsc['n_test'], axis=0).groupby(gindex).sum()/tsc.groupby(gindex)['n_test'].sum()).values

        scores.append(scores_df.reset_index())


    scores = pd.concat(scores)

    cnames = sorted(scores.columns.drop('score'), key=lambda x: float(x[6:]))
    cnames.append('score')
    scores = scores[cnames]
    scores.sort_values(by=['score'], ascending = True, inplace = True)

    if n_best == None:
        result = scores
    else:
        result = scores.iloc[:n_best,:]
    result = result.set_index(result.columns.drop('score').to_list())

    return result


def get_regime_weights(df_X, df_Y, regimes):

    if not isinstance(regimes[0], tuple): regimes = [regimes]

    train_results = pd.DataFrame(columns=['weights', 'n_train','mae_train'])
    idx = pd.Index(regimes, tupleize_cols=False).dropna().to_list()
    train_results = train_results.reindex(index = idx)

    for gindx in idx:

        rangemin = gindx[0]
        rangemax = gindx[1]

        idx = df_X.index[(df_X.index.hour >= rangemin)&(df_X.index.hour < rangemax)]

        # Slice for regime
        df_X_train = df_X.loc[idx,:]
        df_Y_train = df_Y.loc[idx]

        # Solve
        weights, optvalue = weighting_least_squares_concrete(np.array(df_X_train),np.array(df_Y_train))

        # Calculate error
        error_train = np.mean(np.abs(np.sum(np.array(df_X_train)*weights, axis=1)-np.array(df_Y_train)))

        train_results.loc[train_results.index == gindx,'weights'] = [tuple(weights)]
        train_results.loc[train_results.index == gindx,'n_train'] = df_Y_train.shape[0]
        train_results.loc[train_results.index == gindx,'mae_train'] = error_train 

    return train_results


def get_weighted_average(df_X, train_results):

    df_X_mean = pd.DataFrame(index = df_X.index, columns=['Weighted Mean'])

    for i in range(len(train_results)):

        rangemin = train_results.index[i][0]
        rangemax =  train_results.index[i][1]

        idx = df_X.index[(df_X.index.hour >= rangemin)&(df_X.index.hour < rangemax)]

        df_X_mean.loc[idx,'Weighted Mean'] = np.sum(np.array(df_X.loc[idx,:])*train_results.iloc[0].loc['weights'], axis=1)

    return df_X_mean
