import pulp as pl
import networkx as nx
import matplotlib.pyplot as plt
import random
from common import *
import os

    


def ConvertToILP(PHY : nx.DiGraph,
                 K : list,
                 ) -> pl.LpProblem:
    # Create a pulp linear model
    lp_problem = pl.LpProblem(name="SE_Fixed problem",
                              sense=pl.LpMaximize)

    # x_s_k_i_v
    xNode = pl.LpVariable.dicts(name="xNode",
                                indices= [(s,k,i,v) for i in PHY.nodes 
                                          for s in range(len(K))
                                          for k in range(len(K[s])) 
                                          for v in K[s][k].nodes],
                                cat=pl.LpBinary)

    #x_s_k_ij_vw
    xEdge = pl.LpVariable.dicts(name="xEdge",
                                indices=[(s,k,(i,j),(v,w)) 
                                         for s in range(len(K)) 
                                         for k in range(len(K[s])) 
                                         for (i,j) in PHY.edges 
                                         for (v,w) in K[s][k].edges],
                                cat=pl.LpBinary)

    #phi_s_k
    phi = pl.LpVariable.dicts(name="phi",
                            indices=[(s,k) 
                                     for s in range(len(K)) 
                                     for k in range(len(K[s]))],
                            cat=pl.LpBinary)

    #pi_s
    pi = pl.LpVariable.dicts(name="pi",
                            indices=[s for s in range(len(K))],
                            cat=pl.LpBinary)
    
    #z_s_k
    z = pl.LpVariable.dicts(name="z",
                            indices=[(s,k) 
                                     for s in range(len(K)) 
                                     for k in range(len(K[s]))],
                            cat=pl.LpBinary)

    # Constraints
    # C1 : Node resources
    for i in PHY.nodes:
        lp_problem += pl.lpSum(
                    xNode[(s,k,i,v)]*K[s][k].nodes[v]['r'] 
                            for s in range(len(K))
                            for k in range(len(K[s]))
                            for v in K[s][k].nodes
                            ) <= PHY.nodes[i]['a'],f"C1_{i}"
        
    # C2 : Edge resources
    for (i,j) in PHY.edges:
        lp_problem += pl.lpSum(xEdge[(s,k,(i,j),(v,w))]*K[s][k].edges[(v,w)]["r"]
                                    for s in range(len(K))
                                    for k in range(len(K[s]))
                                    for (v,w) in K[s][k].edges
                                    ) <= PHY.edges[(i,j)]['a'],f"C2_{(i,j)}"
        
    # C3 : Map once
    for i in PHY.nodes:
        for s in range(len(K)):
            for k in range(len(K[s])):
                lp_problem += pl.lpSum(xNode[(s,k,i,v)] 
                                for v in K[s][k].nodes) <= z[(s,k)],f"C3_{s}_{k}_{i}"

    # C4 : Map all
    for s in range(len(K)):
        for k in range(len(K[s])):
            for v in K[s][k].nodes:
                lp_problem += pl.lpSum(xNode[(s,k,i,v)] 
                                    for i in PHY.nodes) == z[(s,k)],f"C4_{s}_{k}_{v}"

    # C5 : Service conservative
    for i in PHY.nodes:
        for s in range(len(K)):
            for k in range(len(K[s])):
                for (v,w) in K[s][k].edges:
                    lp_problem += pl.lpSum(xEdge[(s,k,(i,j),(v,w))] - xEdge[(s,k,(j,i),(v,w))] 
                                        for j in PHY.nodes if (i,j) in PHY.edges) - (xNode[(s,k,i,v)] - xNode[(s,k,i,w)]) <= M*(1-phi[(s,k)]),f"C5_1_{s}_{k}_{i}_{(v,w)}"                        
                    lp_problem += pl.lpSum(xEdge[(s,k,(i,j),(v,w))] - xEdge[(s,k,(j,i),(v,w))] 
                                        for j in PHY.nodes if (i,j) in PHY.edges) - (xNode[(s,k,i,v)] - xNode[(s,k,i,w)]) >= -M*(1-phi[(s,k)]),f"C5_2_{s}_{k}_{i}_{(v,w)}" 

    # C6 : Only one configuration
    for s in range(len(K)):
        lp_problem += pl.lpSum(phi[(s,k)] for k in range(len(K[s]))) == pi[s],f"C6_{s}"

    # C7 : Change variables conditions
    for s in range(len(K)):
        for k in range(len(K[s])):
            lp_problem += z[(s,k)] <= pi[s],f"C7_1_{k}_{s}"
            lp_problem += z[(s,k)] <= phi[(s,k)],f"C7_2_{k}_{s}"
            lp_problem += z[(s,k)] >= pi[s] + phi[(s,k)] - 1,f"C7_3_{k}_{s}"


    # Objective
    lp_problem += pl.lpSum(pi[s] for s in range(len(K))) - (1-gamma)*(pl.lpSum(xEdge[(s,k,(i,j),(v,w))] 
                                                                               for s in range(len(K)) 
                                                                               for k in range(len(K[s]))
                                                                               for (i,j) in PHY.edges
                                                                               for (v,w) in K[s][k].edges))


    return lp_problem
    

def generate_config_slice():

    # Create a list of configuration
    GS = list()

    # Create 4 configuration of a slice
    k1 = nx.DiGraph()
    k1.add_node(0,r=random.randint(20,25))
    k1.add_node(1,r=random.randint(20,25))
    k1.add_node(2,r=random.randint(20,25))

    k1.add_edge(0,1,r=random.randint(20,25))
    k1.add_edge(1,2,r=random.randint(20,25))
    
    GS.append(k1)

    k2 = nx.DiGraph()
    k2.add_node(0,r=random.randint(15,20))
    k2.add_node(1,r=random.randint(15,20))
    k2.add_node(2,r=random.randint(15,20))
    k2.add_node(3,r=random.randint(15,20))

    k2.add_edge(0,1,r=random.randint(15,20))
    k2.add_edge(1,2,r=random.randint(15,20))
    k2.add_edge(2,3,r=random.randint(15,20))

    GS.append(k2)

    k3 = nx.DiGraph()
    k3.add_node(0,r=random.randint(10,15))
    k3.add_node(1,r=random.randint(10,15))
    k3.add_node(2,r=random.randint(10,15))
    k3.add_node(3,r=random.randint(10,15))

    k3.add_edge(0,1,r=random.randint(10,15))
    k3.add_edge(1,2,r=random.randint(10,15))
    k3.add_edge(1,3,r=random.randint(10,15))
    
    GS.append(k3)

    k4 = nx.DiGraph()
    k4.add_node(0,r=random.randint(5,10))
    k4.add_node(1,r=random.randint(5,10))
    k4.add_node(2,r=random.randint(5,10))
    k4.add_node(3,r=random.randint(5,10))

    k4.add_edge(0,1,r=random.randint(5,10))
    k4.add_edge(1,2,r=random.randint(5,10))
    k4.add_edge(2,3,r=random.randint(5,10))
    k4.add_edge(3,0,r=random.randint(5,10))

    GS.append(k4)

    return GS


def CreatePHYGraph():
    PHY = nx.DiGraph()

    # Create a physical network PHY
    for i in range(20):
        PHY.add_node(i,a=random.randint(10,30))

    for i in range(20):
            r = 30
            PHY.add_edge(i,i+1,a=r)
            PHY.add_edge(i+1,i,a=r)
    for i in range (10):
           r = 30
           e = random.randint(5,10)
           m = random.randint(1,5)
           PHY.add_edge(e,20-i,a=r)
           PHY.add_edge(20-i,e,a=r)
           PHY.add_edge(m,20-i,a=r)
           PHY.add_edge(20-i,m,a=r)



    return PHY

def CreateSlicesSet():
    # Create a list of slices
    K = list()
    for i in range(20):
        # Create a list of configuration for each slice
        K.append(generate_config_slice())

    return K



PHY = CreatePHYGraph()
SLICE_SET = CreateSlicesSet()
problem = ConvertToILP(PHY, SLICE_SET)
print(problem)