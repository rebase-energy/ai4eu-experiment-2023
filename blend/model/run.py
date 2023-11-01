import pandas as pd
import numpy as np
from blend.model.ols import weighting_least_squares_concrete, linearcombination_concrete
from blend.model.regime import get_regimes, get_regime_weights, get_weighted_average

def calc_weights(df_X, df_Y, indx_train, indx_test, target_col):
    # Calculate weights
    weights, optvalue = weighting_least_squares_concrete(np.array(df_X.loc[indx_train,[(target_col,'Provider A'),(target_col,'Provider B')]]), np.array(df_Y.loc[indx_train]))

    # Calculate linear combination
    weights_lc, intercept_lc, optvalue_lc = linearcombination_concrete(np.array(df_X.loc[indx_train,[(target_col,'Provider A'),(target_col,'Provider B')]]), np.array(df_Y.loc[indx_train]))

    # Calculate weighted mean
    df_X.loc[:,(target_col,'Weighted Mean')] = np.sum(np.array(df_X.loc[:,[(target_col,'Provider A'),(target_col,'Provider B')]])*weights, axis=1)
    df_X.loc[:,(target_col,'Linear Combination')] = np.sum(np.array(df_X.loc[:,[(target_col,'Provider A'),(target_col,'Provider B')]])*weights_lc, axis=1)+intercept_lc





def calc_regime(df_train_X, df_train_Y, nr_regimes):
    nr_regimes = [i for i in range(1, nr_regimes+1)]
    r = get_regimes(df_train_X, df_train_Y, n_regimes=nr_regimes, kf_splits=1)

    weights = get_regime_weights(df_train_X, df_train_Y, r.index[0])

    return weights