from SE_FullFlex import ConvertToILP
from createGraph import CreateSlicesSet, CreatePHYGraph
import pulp as pl
import gurobipy as grb
import networkx as nx
import matplotlib.pyplot as plt
import time
import os
import pickle

def SolveSE_FullFelx(numslices : int,
                     config_list : list) -> tuple:
    
    numconf = len(config_list)
    # Create a physical network
    PHY = CreatePHYGraph()

    # Create a set of slices and configuration
    K = CreateSlicesSet(numslices=numslices,
                        numconf=numconf,
                        config_list=config_list)
    

    # Write an ILP from these graph
    GraphMapping = ConvertToILP(PHY=PHY,
                                K=K)
    # Call SOLVER
    SOLVER = pl.GUROBI(gapRel=5/100)

    GraphMapping.solve(solver=SOLVER)

    solution = dict()
    for var in GraphMapping.variables():
        solution[var.name] = var.varValue
    #accept_slices = round(-pl.value(GraphMapping.objective),0)

    #runtime = GraphMapping.solutionTime

    #a = GraphMapping.variablesDict()
    #rate = list()
    #for k in range(len(config_list)):
    #    rate.append(0)
    
    #for s in range(len(K)):    
    #    if GraphMapping.variablesDict()[f"pi_{s}"].varValue > 0.0:
    #        for k in range(len(K[s])):
    #            rate[k] += (GraphMapping.variablesDict()[f"phi_{s}_{k}"].varValue)/numslices
    #return (accept_slices, runtime, rate)

    with open(r"./solution.txt",'wb') as pk:
        # Pickling variablesDict
        pickle.dump(solution, pk)




SolveSE_FullFelx(numslices=5,
                 config_list=['C1'])
    

    
    
