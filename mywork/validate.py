from solver_test_2 import *
import networkx as nx
import pulp as plp
import matplotlib.pyplot as plt
from create_graph import *


def takeValue(PHY,K,solution_file):
    with gzip.open(solution_file,'rb') as pf:
        solution_data = pickle.load(pf)
  
    # x_s_k_i_v
    xNode = dict()
    for s in range(len(K)):
        xNode[s]=dict()
        for k in range(len(K[s])):
            xNode[s][k]=dict()
            for i in PHY.nodes:
                xNode[s][k][i] = dict()
                for v in K[s][k].nodes:
                    xNode[s][k][i][v] = solution_data[f"xNode_{s}_{k}_({i},_{v})"]

    #x_s_k_ij_vw
    xEdge = dict()
    for s in range(len(K)):
        xEdge[s]=dict()
        for k in range(len(K[s])):
            xEdge[s][k]=dict()
            for (i,j) in PHY.edges:
                xEdge[s][k][(i,j)] = dict()
                for (v,w) in K[s][k].edges:
                    xEdge[s][k][(i,j)][(v,w)] = solution_data[f"xEdge_{s}_{k}_(({i},_{j}),_({v},_{w}))"]

    #phi_s_k
    phi = dict()
    for s in range(len(K)): 
        phi[s] = dict()
        for k in range(len(K[s])):
            phi[s][k]=solution_data[f"phi_({s},_{k})"]

    #pi_s
    pi = dict()
    for s in range(len(K)):
        pi[s] = solution_data[f"pi_{s}"]
    
    #z_s_k
    z = dict()
    for s in range(len(K)): 
        z[s] = dict()
        for k in range(len(K[s])):
            z[s][k]=solution_data[f"z_({s},_{k})"]

    return xNode, xEdge, pi, phi, z




def validate(PHY:nx.DiGraph,SLICE_SET:list[list[nx.DiGraph]],solution_file:str)->str:
    NODE_LIST, EDGE_LIST, pi, phi, z = takeValue(PHY,SLICE_SET,solution_file)
    solution_data = LoadProblem(solution_file)
    #rang buoc 1
    for v in PHY.nodes:
                    if not(
                                sum(
                                            get_solution_value(solution_data,NODE_LIST[s][k][v][i]) * SLICE_SET[s][k].nodes[i]["cpu"]
                                            for s in range(len(SLICE_SET))
                                            for k in range(len(SLICE_SET[s])) 
                                            for i in SLICE_SET[s][k].nodes
                                 ) <= PHY.nodes[v]["cpu"]
                                and 

                                sum(
                                            get_solution_value(solution_data,NODE_LIST[s][k][v][i]) * SLICE_SET[s][k].nodes[i]["ram"]
                                            for s in range(len(SLICE_SET))
                                            for k in range(len(SLICE_SET[s])) 
                                            for i in SLICE_SET[s][k].nodes
                                 ) <= PHY.nodes[v]["ram"]
                                ):
                        A="CONSTRAINT 1 :FALSE"
                        return A
                  
    # rang buoc 2
    for (i,j) in PHY.edges:
                if not (
                            sum(
                                        get_solution_value(solution_data,EDGE_LIST[s][k][(i,j)][(v,w)]) * SLICE_SET[s][k].edges[(v,w)]["banwith"]
                                        for s in range(len(SLICE_SET))
                                        for k in range(len(SLICE_SET[s]))
                                        for (v,w) in SLICE_SET[s][k].edges
                                    ) <= PHY.edges[(i,j)]["banwith"]
                            ):
                    A="CONSTRAINT 2 :FALSE"
                    return A
               
    # rang buoc 3
    for s in range(len(SLICE_SET)):
        for k in range(len(SLICE_SET[s])):
            for i in PHY.nodes:
                if not(
                            sum(
                                get_solution_value(solution_data,NODE_LIST[s][k][i][v])  
                                for v in SLICE_SET[s][k].nodes
                            ) <= get_solution_value(solution_data,z[s][k])
                            ):
                    A="CONSTRAINT 3 :FALSE"
                    return A
    # rang buoc 4
    for s in range(len(SLICE_SET)):
        for k in range(len(SLICE_SET[s])):
            for v in SLICE_SET[s][k].nodes:
                if not(
                                sum(
                                        get_solution_value(solution_data,NODE_LIST[s][k][i][v]) 
                                        for i in PHY.nodes
                                ) == get_solution_value(solution_data,z[s][k])
                ):
                    A="CONSTRAINT 4 :FALSE"
                    return A
    # rang buoc 5
    for s in range(len(SLICE_SET)):
        for k in range(len(SLICE_SET[s])):
            for i in PHY.nodes:
                for (v,w) in SLICE_SET[s][k].edges:
                    for j in PHY.nodes:
                        if (i,j) in PHY.edges:
                            if not(
                                    (
                                        get_solution_value(solution_data,EDGE_LIST[s][k][(i,j)][(v,w)]) - get_solution_value(solution_data,EDGE_LIST[s][k][(j,i)][(v,w)])
                                        - (get_solution_value(solution_data,NODE_LIST[s][k][i][v]) - get_solution_value(solution_data,NODE_LIST[s][k][i][w]))
                                    ) <= 100*(1-get_solution_value(solution_data,phi[s][k])) 
                                    
                                and
                                    (
                                        (get_solution_value(solution_data,EDGE_LIST[s][k][(i,j)][(v,w)])-get_solution_value(solution_data,EDGE_LIST[s][k][(j,i)][(v,w)]))
                                        - (get_solution_value(solution_data,NODE_LIST[s][k][i][v]) - get_solution_value(solution_data,NODE_LIST[s][k][i][w]))
                                    ) >= -100*(1-get_solution_value(solution_data,phi[s][k]))
                                
                            ):
                                A="CONSTRAINT 5 :FALSE"
                                return A        

    # rang buoc 6
    for s in range(len(SLICE_SET)):
            if not(
                    sum(get_solution_value(solution_data,phi[s][k]) 
                                 for k in range(len(SLICE_SET[s])) 
                                 for s in range(len(SLICE_SET))
                                 ) == get_solution_value(solution_data,pi[s])
            ):
                A="CONSTRAINT 6 :FALSE"
                return A
    # rang buoc 7
    for s in range(len(SLICE_SET)):
        for k in range(len(SLICE_SET[s])):
            if not(
                get_solution_value(solution_data,z[s][k]) <= get_solution_value(solution_data,pi[s])  and
                get_solution_value(solution_data,z[s][k])  <= get_solution_value(solution_data,phi[s][k])  and
                get_solution_value(solution_data,z[s][k])  >= get_solution_value(solution_data,pi[s]) + get_solution_value(solution_data,phi[s][k]) - 1
            ):
                A="CONSTRAINT 7 :FALSE"
                return A
    return "SOLUTION ACCEPTED"
