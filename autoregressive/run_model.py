import pandas as pd
import numpy as np
from typing import Any, NamedTuple
import rpy2.robjects as ro
import rpy2.robjects.packages as rpackages
from rpy2.robjects.vectors import StrVector
from autoregressive.util import convert_from_r, convert_df_dates_from_r, convert_to_r, install






def train_model(df_train):
    r_train = convert_to_r(df_train)

    sVARfit = ro.globalenv['sVARfit']
    fit = sVARfit(r_train)

    return convert_from_r(fit)
    

def forecast(results, pred_df, nsteps = 1):
    B = results['coef']

    df_results = pd.DataFrame(columns = pd.MultiIndex.from_product([pred_df.columns, ['Actual','Forecast']]))
    for c in pred_df.columns:
        df_results[(c,'Actual')] = pred_df[c].reset_index(drop = True)

    lagged = df_results.loc[:,(slice(None), 'Actual')].iloc[-4:-1,:]
    lagged.columns = lagged.columns.droplevel(1)


    nsites = len(lagged.columns)
    nlags_needed = len(B)
    nlags_provided = len(lagged)

    if nlags_needed > nlags_provided:
        print(f'{nlags_needed} lagged periods are needed. "lagged" has {nlags_provided}')
        return

    # Concatenate coefficients B
    C = np.concatenate([B[x] for x in sorted(B)], 1)

    results = lagged

    for s in range(nsteps):
        lagged_upd = results.iloc[::-1].iloc[0:nlags_needed]

        # Reverse and flatten dataframe with lagged values
        np_lagged = lagged_upd.to_numpy().flatten(order='C')

        # Matrix multiplication
        f = pd.DataFrame(np.matmul(C, np_lagged).reshape(1,nsites), columns = pred_df.columns)

        results = pd.concat([results,f]).reset_index(drop = True)

    results = results.iloc[nlags_needed:].reset_index(drop = True)

    return results


if __name__ == '__main__':
    install()

    df = pd.read_csv('autoregressive/debug/data/AEMO1213.csv')
    df = df[['Date', 'Time', 'CATHROCK', 'MTMILLAR']]
    data = df.iloc[:,[2, 3]]

    K = len(data.columns)
    # Choose training data
    # First 45 days
    train = range(0, 12*24*45)
    print(train)
    # Choose test data
    # Next 30 days
    test = range(train[-1]+1, train[-1]+2+12*24*45)
    print(test)

    df_train = data.iloc[train,:]
    df_test = data.iloc[test,:]

    
    results = train_model(df_train)






