import argparse
import networkx as nx
import optmodel as opt
import json

def readGraph(graphFile):
    return nx.read_gml(graphFile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read filenames.')
    parser.add_argument('-g', '--graph', help='the graph file', default = "../../data/SantaFe.gml")
    parser.add_argument('-p', '--params', help='the parameters file', default = "../../params/paramsFile.json")
    args = parser.parse_args()
    paramsFile = args.params
    graph = readGraph(args.graph)
    paramsDict = json.loads(open(paramsFile).read())
    for u in (0, 1):
        paramsDict["uniform"] = u
        for n in (3, 4, 5, 6):
            paramsDict["numLandowners"] = n
            budget = 20000
            while budget <= 100000:
                paramsDict["budget"] = budget
                for levels in (2, 5, 10, 15, 20):
                    paramsDict["numFinancialAsstLevels"] = levels
                    for r in range(5):
                        optModel = opt.OptimizationModel(graph, paramsDict)              
                        optModel.writeResults('../../Experiments/Experiments 10-27-2017.txt')
                budget = budget + 20000