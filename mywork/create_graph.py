import networkx as nx
import random   



def generate_config_slice():
    r=random.randint(20,25)
    # Create a list of configuration
    GS = list()
    #đổi sang dùng dict để làm attribute 
    a={'cpu':random.randint(20,25),'ram':random.randint(20,25)}
    # Create 4 configuration of a slice
    k1 = nx.DiGraph()
    k1.add_node(0)
    k1.add_node(1)
    #k1.add_node(2)
    k1.nodes[0].update(a)
    k1.nodes[1].update(a)
    #k1.nodes[2].update(a)
    k1.add_edge(0,1,banwith=random.randint(20,25))
    #k1.add_edge(1,2,banwith=random.randint(20,25))
    GS.append(k1)
    #k2 create 
    k2 = nx.DiGraph()
    k2.add_node(0)
    k2.add_node(1)
    #k2.add_node(2)
    k2.nodes[0].update(a)
    k2.nodes[1].update(a)
    #k2.nodes[2].update(a)
    k2.add_edge(0,1,banwith=random.randint(15,20))
    #k2.add_edge(1,2,banwith=random.randint(15,20))
    GS.append(k2)
    #k3 create 
    # k3 = nx.DiGraph()
    # k3.add_node(0)
    # k3.add_node(1)
    # #k3.add_node(2)
    # k3.nodes[0].update(a)
    # k3.nodes[1].update(a)
    # #k3.nodes[2].update(a)
    # k3.add_edge(0,1,banwith=random.randint(15,20))
    # #k3.add_edge(1,2,banwith=random.randint(15,20))
    
    return GS


def CreatePHYGraph():
    PHY = nx.DiGraph()
    a={'cpu':random.randint(70,80),'ram':random.randint(70,80)}
    # Create a physical network PHY
    for i in range(6):
        PHY.add_node(i)
        PHY.nodes[i].update(a)

    for i in range(4):
            r = random.randint(40,60)
            PHY.add_edge(i,i+1,banwith=r)
            PHY.add_edge(i+1,i,banwith=r)
            # PHY.edges[(i,i+1)].update(a)
            # PHY.edges[(i+1,i)].update(a)
    # PHY.add_edge(3,6,banwith=random.randint(40,60))
    # PHY.add_edge(6,3,banwith=random.randint(40,60))
    # PHY.add_edge(4,8,banwith=random.randint(40,60))
    # PHY.add_edge(8,4,banwith=random.randint(40,60))
    # PHY.add_edge(2,5,banwith=random.randint(40,60))
    # PHY.add_edge(5,2,banwith=random.randint(40,60))
    # PHY.add_edge(1,9,banwith=random.randint(40,60))
    # PHY.add_edge(9,1,banwith=random.randint(40,60))
    #r = random.randint(10,30)
    # PHY.add_edge(1,5,a=r)
    # PHY.add_edge(5,1,a=r)
    # PHY.add_edge(1,3,a=r)
    # PHY.add_edge(3,1,a=r)



    return PHY

def CreateSlicesSet():
    # Create a list of slices
    K = list()
    for i in range(2):
        # Create a list of configuration for each slice
        K.append(generate_config_slice())

    return K