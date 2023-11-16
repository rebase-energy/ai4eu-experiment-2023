import pandas as pd
import numpy as np
from typing import Any, NamedTuple
import rpy2.robjects as ro
import rpy2.robjects.packages as rpackages
from rpy2.robjects.vectors import StrVector
from rpy2.robjects import pandas2ri
from rpy2.robjects import conversion, default_converter
from rpy2.robjects.conversion import localconverter
import os



def convert_df_dates_from_r(df: pd.DataFrame, date_cols: 'list[str]' = None) -> pd.DataFrame:
   """ convert given date columns into pandas datetime with UTC timezone

   Args:
       df (pd.DataFrame): The pandas dataframe
       date_cols (list[str], optional): _description_. Defaults to None.

   Returns:
       pd.DataFrame: The dataframe with the converted
   """
   result = df.copy()
   if date_cols is not None:
       for col in (set(date_cols) & set(result.columns)):
           result[col] = pd.to_datetime(
               result[col], unit='D', origin='1970-1-1').dt.tz_localize('UTC')
           

def convert_to_r(item: Any) -> Any:
   """ converts python object into rpy2 format

   Args:
       item (Any): native python object

   Returns:
       Any: rpy2 object
   """
   if item is None:
       return ro.r("NULL")
   elif isinstance(item, pd.DataFrame):
       with localconverter(ro.default_converter + pandas2ri.converter):
           result = ro.conversion.py2rpy(item)
       return result
   elif isinstance(item, np.ndarray):
       return ro.FloatVector(item)
   elif isinstance(item, (list, tuple, set, pd.Index)):
       if len(item) == 0:
           return None
       if isinstance(item[0], float):
           return ro.FloatVector(item)
       if isinstance(item[0], int):
           return ro.IntVector(item)
       return ro.StrVector(item)
   elif isinstance(item, (pd.Series, NamedTuple)):
       return convert_to_r(dict(item))
   elif isinstance(item, dict):
       temp = {k: convert_to_r(v) for k, v in item.items()
               if v is not None}
       temp = {k: v for k, v in temp.items() if v is not None}
       return ro.ListVector(temp)
   else:
       return item
   


def convert_from_r(item: Any, date_cols: 'list[str]' = None, name: str = '', reserve_plots:bool = True) -> Any:
   """convert rpy object into python native object

   Args:
       item (Any): rpy2 object to convert
       date_cols (list[str], optional): define the date column in R dataframe , in order to convert them into pandas datetime. Defaults to None.
       name (str, optional): name of the object to convert, (not required for external use). Defaults to ''.
       reserve_plots (bool, optional): if True preserve rpy2 ListVector as rpy2 ListVector if name contains plot, in order to be able to output ggplot plots. Defaults to True.

   Returns:
       Any: the converted item
   """
   result = item
   remove_list: bool = True
   if item == ro.vectors.NULL:
       return None
   elif 'plot' in name and isinstance(item, ro.vectors.ListVector) and reserve_plots:
       return item
   elif isinstance(item, (ro.environments.Environment,
                          ro.Formula)):
       return None
   elif isinstance(item, ro.vectors.DataFrame):
       with localconverter(ro.default_converter + pandas2ri.converter):
           result = ro.conversion.rpy2py(item)
       result = convert_df_dates_from_r(result, date_cols)
       remove_list = False
   elif isinstance(item, (ro.vectors.StrVector,
                          ro.vectors.FloatVector,
                          ro.vectors.BoolVector,
                          ro.vectors.FloatMatrix,
                          ro.vectors.IntVector)):
       result = np.array(item)
       #result = tuple(item)
   elif isinstance(item, ro.vectors.ListVector):
       result = {}
       remove_list = False
       if len(item) > 0:
           if item.names != ro.vectors.NULL:
               result = dict(zip(item.names, list(item)))
               for k, v in result.items():
                   result[k] = convert_from_r(v, date_cols, name=k)
           else:
               result = dict(zip(range(len(item)), list(item)))
               for k, v in result.items():
                   result[k] = convert_from_r(v, date_cols, name=str(k))

   if '__len__' in result.__dir__() and len(result) == 1 and remove_list:
       result = result[0]
   return result



def install():
    utils = rpackages.importr("utils")

    packnames = ('ff', 'MASS')
    # Selectively install what needs to be install.
    names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
    if len(names_to_install) > 0:
        utils.install_packages(StrVector(names_to_install))

    rpackages.importr("ff")
    rpackages.importr("MASS")

    ro.r('source("autoregressive/R/sVAR-opt.R")')

