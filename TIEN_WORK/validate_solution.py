import pulp as pl
import networkx as nx
import copy
import pickle
from createGraph import CreatePHYGraph,CreateSlicesSet
#def ValidateSolution(prob: SliceMappingProblem) -> SliceMappingProblem:
#    PHY = prob.PHY
#    SFC_SET = prob.SFC_SET
#    solution = prob.solution
#    result = validatesolution(PHY, SFC_SET, solution)
#    prob.solution_status = result
#    return prob

def validatesolution(PHY, K, solution_file) -> int:
    
    xNode, xEdge, pi, phi, z = takeValue(PHY,K,solution_file)
    # Constraints
    # C1 : Node resources
    if not all (sum(
                    xNode[s][k][i][v]*K[s][k].nodes[v]['cap']['cpu'] 
                            for s in range(len(K))
                            for k in range(len(K[s]))
                            for v in K[s][k].nodes
                            ) <= PHY.nodes[i]['cap']['cpu'] for i in PHY.nodes):
        return -1
        
    if not all (sum(
                    xNode[s][k][i][v]*K[s][k].nodes[v]['cap']['storage'] 
                            for s in range(len(K))
                            for k in range(len(K[s]))
                            for v in K[s][k].nodes
                            ) <= PHY.nodes[i]['cap']['storage'] for i in PHY.nodes):
        return -1
        
    if not all (sum(
                    xNode[s][k][i][v]*K[s][k].nodes[v]['cap']['memory'] 
                            for s in range(len(K))
                            for k in range(len(K[s]))
                            for v in K[s][k].nodes
                            ) <= PHY.nodes[i]['cap']['memory'] for i in PHY.nodes):
        return -1
        
    # C2 : Edge resources
    if not all (sum(xEdge[s][k][ij][vw]*K[s][k].edges[vw]["cap"]['bandwidth']
                                    for s in range(len(K))
                                    for k in range(len(K[s]))
                                    for vw in K[s][k].edges
                                    ) <= PHY.edges[ij]['cap']['bandwidth'] for ij in PHY.edges):
        return -2
       
    # C3 : Map once
    if not all(sum(xNode[s][k][i][v] for v in K[s][k].nodes) <= z[s][k] for i in PHY.nodes
                                                                            for s in range(len(K))
                                                                            for k in range(len(K[s]))):
        return -3 

    # C4 : Map all
    if not all(sum(xNode[s][k][i][v] for i in PHY.nodes) == z[s][k] for s in range(len(K))
                                                                    for k in range(len(K[s]))
                                                                    for v in K[s][k].nodes):
        return -4

    # C5 : Service conservative
    M = 1000
    if not all(sum(xEdge[s][k][(i,j)][(v,w)] - xEdge[s][k][(j,i)][(v,w)]
        for j in PHY.nodes if (i,j) in PHY.edges) - (xNode[s][k][i][v] - xNode[s][k][i][w]) <= M*(1-phi[s][k]) for i in PHY.nodes
                                                                                                            for s in range(len(K))
                                                                                                            for k in range(len(K[s]))
                                                                                                            for (v,w) in K[s][k].edges):
        return -5                    
        
    if not all(sum(xEdge[s][k][(i,j)][(v,w)] - xEdge[s][k][(j,i)][(v,w)]
        for j in PHY.nodes if (i,j) in PHY.edges) - (xNode[s][k][i][v] - xNode[s][k][i][v]) >= -M*(1-phi[s][k]) for i in PHY.nodes
                                                                                                            for s in range(len(K))
                                                                                                            for k in range(len(K[s]))
                                                                                                            for (v,w) in K[s][k].edges):
        return -5

    # C6 : Only one configuration
    if not all (sum(phi[s][k] for k in range(len(K[s]))) == pi[s] for s in range(len(K))):
        return -6

    # C7 : Change variables conditions
    if not all (z[s][k] <= pi[s] for s in range(len(K)) for k in range(len(K[s]))) :
        return -7
    if not all (z[s][k] <= phi[s][k] for s in range(len(K)) for k in range(len(K[s]))) :
        return -7
    if not all (z[s][k] >= pi[s] + phi[s][k] - 1 for s in range(len(K)) for k in range(len(K[s]))) :
        return -7
    
    return 1

def takeValue(PHY,K,solution_file):
    with open(solution_file,'rb') as pf:
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
                    xNode[s][k][i][v] = solution_data[f"xNode_{s}_{k}_{i}_{v}"]

    #x_s_k_ij_vw
    xEdge = dict()
    for s in range(len(K)):
        xEdge[s]=dict()
        for k in range(len(K[s])):
            xEdge[s][k]=dict()
            for (i,j) in PHY.edges:
                xEdge[s][k][(i,j)] = dict()
                for (v,w) in K[s][k].edges:
                    xEdge[s][k][(i,j)][(v,w)] = solution_data[f"xEdge_{s}_{k}_({i},_{j})_({v},_{w})"]

    #phi_s_k
    phi = dict()
    for s in range(len(K)): 
        phi[s] = dict()
        for k in range(len(K[s])):
            phi[s][k]=solution_data[f"phi_{s}_{k}"]

    #pi_s
    pi = dict()
    for s in range(len(K)):
        pi[s] = solution_data[f"pi_{s}"]
    
    #z_s_k
    z = dict()
    for s in range(len(K)): 
        z[s] = dict()
        for k in range(len(K[s])):
            z[s][k]=solution_data[f"z_{s}_{k}"]

    return xNode, xEdge, pi, phi, z


print(validatesolution(PHY=CreatePHYGraph(),
                 K=CreateSlicesSet(5,1,['C1']),
                 solution_file="./solution.txt"))
