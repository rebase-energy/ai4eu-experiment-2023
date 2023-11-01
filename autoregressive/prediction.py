import pandas as pd
import json
import simplejson
import pickle
from datetime import datetime
import numpy as np
import rpy2.robjects as ro
import rpy2.robjects.packages as rpackages
import os
from util import convert_to_r
from rpy2.robjects.vectors import StrVector


rootpath = "/Users/henrikkalvegren/Github/ai4eu-experiment-2023/autoregressive/"


def load():
    utils = rpackages.importr("utils")
    packnames = ('ff', 'MASS')
    # Selectively install what needs to be install.
    names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
    if len(names_to_install) > 0:
        utils.install_packages(StrVector(names_to_install))

    rpackages.importr("ff")
    rpackages.importr("MASS")


def fit(df_train):
    ro.r['source'](os.path.join(rootpath, 'R', 'sVAR-opt.R'))
    sVARfit = ro.globalenv['sVARfit']

    r_train = convert_to_r(df_train)
    fit = sVARfit(r_train)

def forecast(B, lagged, nsteps = 1):

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
        f = pd.DataFrame(np.matmul(C, np_lagged).reshape(1,nsites), columns = df_test.columns)

        results = pd.concat([results,f]).reset_index(drop = True)

    results = results.iloc[nlags_needed:].reset_index(drop = True)

    return results

def evaluate(train_set, valid_set, params):
    # df_train_X = train_set.drop(columns=['target'])
    # df_train_y = train_set['target']
    # lgb_trainset = lgb.Dataset(df_train_X, label=df_train_y)

    # df_test_X = valid_set.drop(columns=['target'])
    # df_test_y = valid_set['target']
    # lgb_testset = lgb.Dataset(df_test_X, label=df_test_y)

    # valid_sets = [lgb_testset]
    # valid_names = ['test']

    # evals_result = {}
    # gbm = lgb.train(
    #     params, 
    #     lgb_trainset,
    #     valid_sets=valid_sets,
    #     valid_names=valid_names,
    #     evals_result=evals_result
    # )

    evals_result = {}
    
    return evals_result


def get_prediction(train_set, val_x, params):
    df = pd.DataFrame()
    return df




def to_multiindex(df):
    df.index = pd.MultiIndex.from_arrays(
            [pd.to_datetime(df['ref_datetime'].values),
            pd.to_datetime(df['valid_datetime'].values)],
            names=['ref_datetime', 'valid_datetime'])
    # Drop now duplicated index columns
    df = df.drop(columns=['ref_datetime', 'valid_datetime'])
    return df

def to_df(json_data):
    data = simplejson.loads(json_data)
    df = pd.DataFrame(data)
    return to_multiindex(df)



def get_params(file_name='params.json'):
    with open(file_name, 'r') as f:
        return json.load(f)


def store_result(result):
    with open('out/result.pickle', 'wb') as f:
        pickle.dump({
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'result': result
        }, f)