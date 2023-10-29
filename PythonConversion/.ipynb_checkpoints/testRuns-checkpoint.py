import importlib
# importlib.import_module("testInstance")
import testInstance
c_orig = testInstance.c_orig 
importlib.import_module("functionGbound")
from functionGbound import gx_bound
y, gx, SP, T, pred, label, path = gx_bound(c_orig, c_orig, edge)