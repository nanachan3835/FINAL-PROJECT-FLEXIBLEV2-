import networkx as nx
from pulp import *

def Convert_to_ILP( SFClist: list[list[nx.DiGraph]], G: nx.DiGraph) -> LpProblem:


    # define pi variable
    pi = LpVariable.dicts(
        name="pi",
        indices=(s for s in range(len(SFClist))),
        cat="Binary",
    )

    # define node variable
    # xNode[s][k][v][i]
    # xEdge[s][k][vw][ij]
    # pi[s]
    # phi[s][k]
    xNode = {}
    for s_index, s in enumerate(SFClist):
        xNode[s_index] = {}
        for k, config in enumerate(s):
            xNode[s_index][k] = {}
            for i in G.nodes:
                xNode[s_index][k][i] = {}
                for v in config:
                    xNode[s_index][k][i][v] = LpVariable(f"xNode_{s_index}_{k}_{i}_{v}", cat="Binary")

    # define phi variable
    phi = {}

    for s_index, s in enumerate(SFClist):
        phi[s_index] = {}
        for k, config in enumerate(s):
            phi[s_index][k] = LpVariable(name=f"phi_{s_index}_{k}", cat="Binary")
    # print(phi)

    xEdge = {}

    for s_index, s in enumerate(SFClist):
        xEdge[s_index] = {}
        for k, subgraph in enumerate(s):
            xEdge[s_index][k] = {}
            for vw in subgraph.edges:
                xEdge[s_index][k][vw] = {}
                for ij in G.edges:
                    xEdge[s_index][k][vw][ij] = LpVariable(name=f"xEdge_{s_index}_{k}_{vw}_{ij}", cat="Binary")
    # print(xEdge)
    # print(xEdge[0][0][(2,3)][(2,3)])
    # xEdge = LpVariable.dicts(name    = "xEdge", 
    #                             indices  =[(s_index, k, (i, j), (v, w)) 
    #                                 for s_index, s in enumerate(SFClist)
    #                                 for k, subgraph in enumerate(s)
    #                                 for v, w in subgraph.edges 
    #                                 for i, j in G.edges],
    #                             cat = "Binary"
    #                             )



    z = {}

    for s_index, s in enumerate(SFClist):
        z[s_index] = {}
        for k, subgraph in enumerate(s):
            z[s_index][k] = LpVariable(name=f"z_{s_index}_{k}", cat="Binary")


    __problem = LpProblem(name="FIXED", sense=LpMinimize)

    # Attributes of the physical network
    aNode = nx.get_node_attributes(G, "weight")
    aEdge = nx.get_edge_attributes(G, "weight")


    for s_index, s in enumerate(SFClist):
        for k, config in enumerate(s):
            rNode = nx.get_node_attributes(config, "weight")
            rEdge = nx.get_edge_attributes(config, "weight")

            #C1:
            for i in G.nodes:
                
                __problem += (
                    lpSum(
                        xNode[s_index] [k] [i] [v] * rNode[v]
                        for v in config.nodes
                    ) <= aNode[i] * phi[s_index][k],
                    f'C1_{s_index}_{k}_{i}'
                )

            
            #C2:
            for (i,j) in G.edges:
                __problem += (
                    lpSum(
                        xEdge[s_index][k][vw][ij] * rEdge[(v,w)]
                            for  v,w in config.edges
                    )
                    <= aEdge[(i,j)] * phi[s_index][k],
                    f'C2_{s_index}_{k}_{i}_{j}'
                )
            #C3:
            for i in G.nodes:
                __problem+=(
                    lpSum(
                        xNode[s_index][k][v][i]
                        for v in config.nodes
                    )
                    <= z[s_index][k]
                )
            
            #C4:[3, 2]
            for v in config.nodes:
                __problem +=(
                    lpSum(
                        xNode[s_index][k][v][i]
                        for v in config.nodes                   
                    )
                    == z[s_index][k]
                    
                )
            #C5:
            M = 100
            for (v,w) in config.edges:
                for (i,j) in G.edges:
                    __problem +=(
                        lpSum(
                            (xEdge[(s_index, k, (i, j), (v, w))] - xEdge[(s_index, k, (j, i), (v, w))]) 
                            - (xNode[(s_index, k, i, v)] - xNode[(s_index, k, i, w)])

                        )
                        <= M * (1 - phi[(s_index, k)]) 
                    )
                    __problem +=(
                        lpSum(
                            (xEdge[(s_index, k, (i, j), (v, w))] - xEdge[(s_index, k, (j, i), (v, w))]) 
                            - (xNode[(s_index, k, i, v)] - xNode[(s_index, k, i, w)])

                        )
                        >= -1 * M * (1 - phi[(s_index, k)])                        
                    )
            
    #C6:
    for s_index in range(len(SFClist)):
        # print(s_index)
        __problem +=(
            lpSum(
                phi[(s_index, k)] for k in range(len(SFClist[s_index]))
            )
            == pi[s_index]
        )
    #C7:
    for s_index in range(len(SFClist)): 
        for k in range(len(SFClist[s_index])):
            __problem += (
                z[(s_index, k)] <= pi[s_index]
            )
            __problem += (
                z[(s_index, k)] <= phi[(s_index, k)]
            )
            __problem += (
                z[(s_index, k)] >= pi[s_index] + phi[(s_index, k)] - 1
            )

    GAMMA = 0.99999
    __problem += - GAMMA * lpSum(pi.values()) \
        + (1 - GAMMA) * lpSum(
            xEdge[(s_index, k, (i, j), (v, w))]
                for s_index, s in enumerate(SFClist) 
                for k, subgraph in enumerate(s)
                for v, w in subgraph.edges
                for i, j in G.edges 
        )
   

    
    return __problem 