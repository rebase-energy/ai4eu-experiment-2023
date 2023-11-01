import numpy as np
from itertools import chain
from sklearn.model_selection import KFold
from blend.model.segmentationtools import segmentations

def create_groups(min_value, max_value, step_size, n_regimes):
    
    eval_points = list(np.arange(min_value,max_value+step_size,step_size))
    
    groups = list(segmentations(eval_points,n_regimes))
    
    return groups


def create_unique_groups(groups):

    unique_groups = [[list(x)] for x in set(tuple(x) for x in chain.from_iterable(groups))]
    
    return unique_groups  

    
def create_groups_range(groups, step_size):
    groups_range = [None] * len(groups)
    for i in range(len(groups)):
    
        groups_range[i] = [None] * len(groups[i])
    
        for j, g in enumerate(groups[i]):
        
            rangemin = g[0]
            rangemax = g[-1]+step_size
        
            groups_range[i][j] = tuple([rangemin, rangemax])
            
    return groups_range


def create_kfold(kf_splits, kf_shuffle, kf_seed):

    if (kf_shuffle == True)&(kf_seed == None):
        random_state = np.random.randint(0,10000)
    else:
        random_state = kf_seed
    
    kFold=KFold(n_splits=kf_splits,shuffle=kf_shuffle,random_state=random_state)
    
    return kFold