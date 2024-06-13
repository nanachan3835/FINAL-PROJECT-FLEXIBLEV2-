import networkx as nx 
import pulp as plp 
import matplotlib.pyplot as plt

# define G , G = 5 node 8 links

G = nx.DiGraph()

# add node to G
for i in range(5):
    G.add_node(i, a=10) # add node with attribute a = 10

# add links to G 
for i in range(4):
    G.add_edge(i, i+1, a=10) # add link with attribute a = 10
    G.add_edge(i+1, i, a=10) # add link with attribute a = 10

# define GS , GS = 3 node 2 links (a list of GS , 4GS)
GS_DICT =nx.DiGraph()
GS_DICT.add_node(0, r=2)
GS_DICT.add_node(1, r=2)
GS_DICT.add_node(2, r=2)
GS_DICT.add_edge(0,1,r=5)
GS_DICT.add_edge(1,2,r=5)

def GraphMappingToILP(PHY:nx.DiGraph, SLICE_SET:list[list[nx.DiGraph]]) -> pulp.lpProblem:
    slice = SLICE_SET[0]
    pass

#print(GS_DICT[1].nodes)
#print(GS_DICT[1].edges)      
#print(GS_DICT[1].nodes[0]['r'])
#for test with multiple GS
#for i in range(len(GS_DICT)): 
#    change GS_DICT[0]= GS_DICT[i]
#JUST TESTING , IF WORKING THEN PACKAGING IT INTO A FUNCTION


# choose GS[0] as the input

aNode = nx.get_node_attributes(G, "a")
aEdge = nx.get_edge_attributes(G, "a")

rNode = nx.get_node_attributes(GS_DICT, "r")
rEdge = nx.get_edge_attributes(GS_DICT, "r")

print(G.edges)
print( G.get_edge_data(0,1r ))


xNode = plp.LpVariable.dicts(
    name="xNode",
    indices=((G.nodes,GS_DICT.nodes)),
    cat=plp.LpBinary
)

xEdge = plp.LpVariable.dicts(
    name="xEdge",
    indices=((G.edges,GS_DICT.edges)),
    cat=plp.LpBinary
)



# problem for G and GS[0]

problem = plp.LpProblem(name="graph-mapping", sense=plp.LpMaximize)
# define variable of nodes
xNode = plp.LpVariable.dicts(
    name="xNode",
    indices=(GS_DICT.nodes, G.nodes),
    cat=plp.LpBinary
)
# define variable of edges
xEdge = plp.LpVariable.dicts(
    name="xEdge",
    indices=(GS_DICT.edges, G.edges),
    cat=plp.LpBinary
)
# define variable of pi (0==no mapping,1==mapping)
pi = plp.LpVariable(
    name="pi",
    cat=plp.LpBinary
)


# C1
for i in G.nodes:
    problem += (
        plp.lpSum(
            xNode[(j,i)]*rNode[j]
            for j in GS_DICT.nodes
            ) <= aNode[i],
        f"C1_{i}"
    )

# C2

for i in G.edges:
    problem += (
        plp.lpSum(
            xEdge[j][i] * rEdge[j]
            for j in GS_DICT.edges
            ) <= aEdge[i],
        f"C2_{i}"
    )

# C3
for i in G.nodes:
    problem += (
        plp.lpSum(
            xNode[j][i] for j in GS_DICT.nodes
            for j in GS_DICT.nodes
            ) <= pi,
        f"C3_{i}"
    )
# C4
for v in GS_DICT[0].nodes:
    problem += (
        plp.lpSum(
            xNode[v][i]
            for i in G.nodes
        ) == pi,
        f"C4_{v}"
    )
#C5
for vw in GS_DICT.edges:
    for i in G.nodes:
        problem += (
            (
                plp.lpSum(xEdge[vw].get((i,j)) for j in G.nodes) 
                - plp.lpSum(xEdge[vw].get((j,i)) for j in G.nodes)
            ) == xNode[vw[0]][i] - xNode[vw[1]][i],
            f"C5_{i}_{vw}"
        )



print("###################")
print(xEdge[(0,1)].get(1,0))




problem += (
    plp.lpSum(
        xNode[v][i]
        for v in GS_DICT[0].nodes
        for i in G.nodes
    )
)

print(problem)

# function to make graph
def makegraph(n,r_Nodes:list,r_Edges:list):
    G= nx.DiGraph()
    for i in range(n):
        G.add_node(i, a=r_Nodes[i]) # add node with attribute a = 10
    for i in range(n-1):
        G.add_edge(i, i+1, a=r_Edges[i]) # add link with attribute a = 10
        G.add_edge(i+1, i, a=r_Edges[i]) # add link with attribute a = 10
    return G
GS_list={"G1":makegraph(3,[2,2,2],[5,5]),"G2":makegraph(3,[2,2,2],[5,5])}
print(GS_list[G1].nodes)



