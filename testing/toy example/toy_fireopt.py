import argparse
import networkx as nx
import toy_optmodel as opt
import json

def readGraph(graphFile):
    return nx.read_gml(graphFile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read filenames.')
    parser.add_argument('-g', '--graph', help='the graph file', default = "toyLandscape.gml")
    parser.add_argument('-p', '--params', help='the parameters file', default = "toyParams.json")
    args = parser.parse_args()
   # paramsFile = args.params
    graph = readGraph(args.graph)
    #paramsDict = json.loads(open(paramsFile).read())
    with open("toyParams.json") as data_file:
        paramsDict = json.load(data_file)
    optModel = opt.OptimizationModel(graph, paramsDict)
    #optModel.optimize()
    #optModel.writeResults('results.txt')