import pulp as plp 
import matplotlib.pyplot as plt
import math
import networkx as nx
#from common import *

def GraphMappingToILP(PHY:nx.DiGraph, SLICE_SET:list[list[nx.DiGraph]]) -> plp.LpProblem:
    # tao problem 
    problem = plp.LpProblem(name="GraphMapping", 
                            sense=plp.LpMaximize)
    # tao bien xNode cho tat ca cac slide trong SLICE_SET
    NODE_LIST=list()                    
    # tao bien xNode
    for s in range(len(SLICE_SET)):
        node_k = list()
        for k in range(len(SLICE_SET[s])):
                xNode = plp.LpVariable.dicts(name=f"xNode_{s}_{k}",
                                 indices = [(i,v) 
                                             for v in PHY.nodes
                                             for i in SLICE_SET[s][k].nodes],
                                 cat=plp.LpBinary)
                node_k.append(xNode)
        NODE_LIST.append(node_k)
                
    #tao bien xEdge cho tat ca cac slide trong SLICE_SET
    EDGE_LIST=list()
    # tao bien xEdge
    for s in range(len(SLICE_SET)):
        edge_k = list()
        for k in range(len(SLICE_SET[s])):
                xEdge = plp.LpVariable.dicts(name=f"xEdge_{s}_{k}",
                                 indices = [((i,j),(v,w)) 
                                             for (i,j) in PHY.edges
                                             for (v,w) in SLICE_SET[s][k].edges],
                                 cat=plp.LpBinary)
                edge_k.append(xEdge)
        EDGE_LIST.append(edge_k)
    # tao bien phi
    phi = plp.LpVariable.dicts(name="phi",
                               indices = [(s,k) 
                                           for s in range(len(SLICE_SET))
                                           for k in range(len(SLICE_SET[s]))],
                               cat=plp.LpBinary)
    # tao bien pi
    pi = plp.LpVariable.dicts(name="pi",
                              indices = [s 
                                         for s in range(len(SLICE_SET))],
                              cat=plp.LpBinary)
    # tao bien z    
    z = plp.LpVariable.dicts(name="z",
                             indices = [(s,k) 
                                         for s in range(len(SLICE_SET))
                                         for k in range(len(SLICE_SET[s]))],
                             cat=plp.LpBinary)
    #PHY_add = 
   


    # tao cac rang buoc
    # rang buoc 1
    for i in PHY.nodes:
                    problem += (
                                plp.lpSum(
                                            NODE_LIST[s][k][(v,i)] * SLICE_SET[s][k].nodes[v]["r"][0]
                                            for s in range(len(SLICE_SET))
                                            for k in range(len(SLICE_SET[s])) 
                                            for v in SLICE_SET[s][k].nodes
                                 ) <= PHY.nodes[i]["a"][0], f"C1_{i}"
                                )
                    problem += (
                                plp.lpSum(
                                            NODE_LIST[s][k][(v,i)] * SLICE_SET[s][k].nodes[v]["r"][1]
                                            for s in range(len(SLICE_SET))
                                            for k in range(len(SLICE_SET[s])) 
                                            for v in SLICE_SET[s][k].nodes
                                 ) <= PHY.nodes[i]["a"][1], f"C1_{i}"
                                )
                    problem += (
                                plp.lpSum(
                                            NODE_LIST[s][k][(v,i)] * SLICE_SET[s][k].nodes[v]["r"][2]
                                            for s in range(len(SLICE_SET))
                                            for k in range(len(SLICE_SET[s])) 
                                            for v in SLICE_SET[s][k].nodes
                                 ) <= PHY.nodes[i]["a"][2], f"C1_{i}"
                                )
            #) <= nx.get_node_attributes(PHY.nodes[i],"a"), f"C1_{i}"
    # rang buoc 2
    for (i,j) in PHY.edges:
                problem += (
                            plp.lpSum(
                                        EDGE_LIST[s][k][((i,j),(v,w))] * SLICE_SET[s][k].edges[(v,w)]["r"][0]
                                        for s in range(len(SLICE_SET))
                                        for k in range(len(SLICE_SET[s]))
                                        for (v,w) in SLICE_SET[s][k].edges
                                    ) <= PHY.edges[(i,j)]["a"][0], f"C2_{(i,j)}"
                            )
                problem += (
                                plp.lpSum(
                                            NODE_LIST[s][k][(v,i)] * SLICE_SET[s][k].nodes[v]["r"][1]
                                            for s in range(len(SLICE_SET))
                                            for k in range(len(SLICE_SET[s])) 
                                            for v in SLICE_SET[s][k].nodes
                                 ) <= PHY.nodes[i]["a"][1], f"C1_{i}"
                                )
                problem += (
                                plp.lpSum(
                                            NODE_LIST[s][k][(v,i)] * SLICE_SET[s][k].nodes[v]["r"][1]
                                            for s in range(len(SLICE_SET))
                                            for k in range(len(SLICE_SET[s])) 
                                            for v in SLICE_SET[s][k].nodes
                                 ) <= PHY.nodes[i]["a"][1], f"C1_{i}"
                                )
            #) <= nx.get_edge_attributes(PHY.edge[i,j],"a"), f"C2_{(i,j)}"
    # rang buoc 3
    for s in range(len(SLICE_SET)):
        for k in range(len(SLICE_SET[s])):
            for i in PHY.nodes:
                problem += (
                            plp.lpSum(
                                NODE_LIST[s][k][(v,i)]  
                                for v in SLICE_SET[s][k].nodes
                            ) <= z[(s,k)], f"C3_{s}_{k}_{i}"
                            ) 
    # rang buoc 4
    for s in range(len(SLICE_SET)):
        for k in range(len(SLICE_SET[s])):
            for v in SLICE_SET[s][k].nodes:
                problem += (
                                plp.lpSum(
                                        NODE_LIST[s][k][(v,i)] 
                                        for i in PHY.nodes
                                ) == z[(s,k)], f"C4_{s}_{k}_{v}"
                )
    # rang buoc 5
    for s in range(len(SLICE_SET)):
        for k in range(len(SLICE_SET[s])):
            for i in PHY.nodes:
                for (v,w) in SLICE_SET[s][k].edges:
                    problem += (
                                plp.lpSum(
                                        EDGE_LIST[s][k][((i,j),(v,w))]-EDGE_LIST[s][k][((j,i),(v,w))]
                                        for j in PHY.nodes if (i,j) in PHY.edges) 
                                        - (NODE_LIST[s][k][(v,i)] - NODE_LIST[s][k][(w,i)]
                                ) <= 100*(1-phi[(s,k)]), f"C5_1_{s}_{k}_{i}_{(v,w)}"
                            ) 
                    problem += (
                                plp.lpSum(
                                         EDGE_LIST[s][k][((i,j),(v,w))]-EDGE_LIST[s][k][((j,i),(v,w))]
                                for j in PHY.nodes if (i,j) in PHY.edges) 
                                - (NODE_LIST[s][k][(v,i)] - NODE_LIST[s][k][(w,i)]
                                ) >= -100*(1-phi[(s,k)]), f"C5_2_{s}_{k}_{i}_{(v,w)}"
                            )            

    # rang buoc 6
    for s in range(len(SLICE_SET)):
            problem += plp.lpSum(phi[(s,k)] 
                                 for k in range(len(SLICE_SET[s])) 
                                 for s in range(len(SLICE_SET))
                                 ) == pi[s],f"C6_{s}"
    # rang buoc 7
    for s in range(len(SLICE_SET)):
        for k in range(len(SLICE_SET[s])):
            problem += z[(s,k)] <= pi[s], f"C7_1_{s}_{k}"
            problem += z[(s,k)] <= phi[(s,k)], f"C7_2_{s}_{k}"
            problem += z[(s,k)] >= pi[s] + phi[(s,k)] - 1, f"C7_3_{s}_{k}"
    #OBJECTIVE FUNCTION
    problem += plp.lpSum(pi[s] for s in range(len(SLICE_SET))) - (1-0.999)*(plp.lpSum(xEdge[((i,j),(v,w))] 
                                                                               for s in range(len(SLICE_SET)) 
                                                                               for k in range(len(SLICE_SET[s]))
                                                                               for (i,j) in PHY.edges
                                                                               for (v,w) in SLICE_SET[s][k].edges))
    return problem