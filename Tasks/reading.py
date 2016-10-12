import networkx as nx
G=nx.Graph()
filename='C:\\Users\\mcm600\\workspace\\testing\\SanBernadinotest.gml'
#filename='C:\\Users\\mcm600\\git\\fireopt\\data\\SanBernardino.gml'
isnode=0

def process(line):
    global isnode
    if line=='  node [':
        isnode=1
        return
    if isnode==1:
        elements=line.strip().split(' ')
        G.add_node(int(elements[1]),id=elements[1])
        print(elements)
        isnode=0
#        print(elements[1]) 
#    print(line)

with open(filename) as f:
    for line in f:
        process(line.splitlines()[0])

print(G.nodes(data=True))