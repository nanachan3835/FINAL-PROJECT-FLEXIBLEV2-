from SE_FullFlex import *
import networkx as nx
import pulp as plp
import matplotlib.pyplot as plt
from common import *
from create_graph import *




PHY = CreatePHYGraph()
SLICE_SET = CreateSlicesSet()
problem = ConvertToILP(PHY, SLICE_SET)
#print(problem)
print(problem.variables())







