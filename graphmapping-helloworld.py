import networkx as nx
import pulp
import matplotlib.pyplot as plt

# Define G
# G = 5 nodes 8 links
G = nx.DiGraph()

for i in range(5):
    G.add_node(i, a=10)

for i in range(4):
    G.add_edge(i,i+1, a=10)
    G.add_edge(i+1,i, a=10)

# Define GS
# GS = 3 nodes 2 link
    
GS = nx.DiGraph()

GS.add_node(0, r=2)
GS.add_node(1, r=2)
GS.add_node(2, r=2)

GS.add_edge(0,1,r=5)
GS.add_edge(1,2,r=5)

# input
#G
#GS

#G, K{GS}

# ILP
problem = pulp.LpProblem(name="graph-maaping", sense=pulp.LpMaximize)

xNode = pulp.LpVariable.dicts(
    name="xNode",
    indices=(GS.nodes, G.nodes),
    cat=pulp.LpBinary
)

xEdge = pulp.LpVariable.dicts(
    name="xEdge",
    indices=(GS.edges, G.edges),
    cat=pulp.LpBinary
)

pi = pulp.LpVariable(
    name="pi",
    cat=pulp.LpBinary
)

aNode = nx.get_node_attributes(G, "a")
aEdge = nx.get_edge_attributes(G, "a")

rNode = nx.get_node_attributes(GS, "r")
rEdge = nx.get_edge_attributes(GS, "r")

# C1

for i in G.nodes:
    problem += (
        pulp.lpSum(
            xNode[v][i] * rNode[v]
            for v in GS.nodes
        ) <= aNode[i],
        f"C1_{i}"
    )

for v in GS.nodes:
    problem += (
        pulp.lpSum(
            xNode[v][i]
            for i in G.nodes
        ) == pi,
        f"C4_{v}"
    )

problem += (
    pulp.lpSum(
        xNode[v][i]
        for v in GS.nodes
        for i in G.nodes
    )
)
print(problem)