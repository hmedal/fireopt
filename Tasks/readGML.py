import networkx as nx

G=nx.DiGraph()

#filename='C:\\Users\\mcm600\\git\\fireopt\\data\\SanBernardino.gml'
filename='..\\data\\SanBernardino.gml'

isnode=0
nodename=-1
isedge=0
edgesource=-1
edgetarget=-1

def process(line):
    global isnode
    global nodename
    global isedge,edgesource,edgetarget
    if line.strip()=='node [':
        isnode=1
        return
    if line.strip()==']':
        isnode=0
        nodename=-1
        isedge=0
        edgesource=-1
        edgetarget=-1
        return
    if isnode==1:
        elements=line.strip().split(' ')
        G.add_node(int(elements[1]),id=int(elements[1]))
        nodename=int(elements[1])
        isnode=2
        return
    if isnode==2:
        elements=line.strip().split(' ')
        G.node[nodename][elements[0]]=elements[1].strip('\"')
        return
    if line.strip()=='edge [':
        isedge=1
        return
    if isedge==1:
        elements=line.strip().split(' ')
        edgesource=int(elements[1])
        isedge=2
        return
    if isedge==2:
        elements=line.strip().split(' ')
        edgetarget=int(elements[1])
        isedge=3
        return
    if isedge==3:
        elements=line.strip().split(' ')
        G.add_edge(edgesource,edgetarget,weight=float(elements[1]))
        return

with open(filename) as f:
    for line in f:
        process(line.splitlines()[0])

print(nx.shortest_path(G,1,120))
#print(G.nodes(data=True))
#print(G.edges(data=True))