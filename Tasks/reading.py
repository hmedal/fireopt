import networkx as nx
G=nx.Graph()
filename='C:\\Users\\mcm600\\workspace\\testing\\SanBernadinotest.gml'

def process(line):
    print(line)

with open(filename) as f:
    for line in f:
        process(line.splitlines()[0])