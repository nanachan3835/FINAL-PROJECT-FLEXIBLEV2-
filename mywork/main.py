from solver_test_2 import *
import networkx as nx
import pulp as plp
import matplotlib.pyplot as plt
from create_graph import *
from validate import *
#from pulp import Lpvariable
#import Solvers as sol 
#from sol import *
#from ILP import scip



PHY = CreatePHYGraph()
SLICE_SET = CreateSlicesSet()
problem = GraphMappingToILP(PHY, SLICE_SET)
saveProblem(problem)
#LoadProblem("./solution.pkl")
solution=validate(PHY,SLICE_SET,"./solution.pkl")
print(solution)

