#Same as fuctionCheckO1Flag but uses delta1 as percentage instead
import numpy as np
import importlib
import pandas as pd

importlib.import_module("functionGetCellInfo")
from functionGetCellInfo import getCellInfo
importlib.import_module("functionHbound")
from functionHbound import hx_bound

def calcHBoundAfterPartition(k, x_now, d, df_cell,edge,origin,destination):
    c_L, c_U, M, c, c_g, yK = getCellInfo(k, x_now, "c_g", d, df_cell)
    y_h, hx = hx_bound(c_L, c_U, d, x_now,edge,origin,destination)
    return y_h, hx