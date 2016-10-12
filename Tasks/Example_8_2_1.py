# add 6 nodes

import networkx as nx

G=nx.Graph()

G.add_nodes_from([1,6])
G.node[1]['name']='Plant 1'
G.node[6]['name']='City 1'

G.add_edge(1,2,weight=4)
G.add_edge(1,3,weight=3)
G.add_edge(2,4,weight=3)
G.add_edge(2,5,weight=2)
G.add_edge(3,5,weight=3)
G.add_edge(4,6,weight=2)
G.add_edge(5,6,weight=2)

print(G.edges(data=True))