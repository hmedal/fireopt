import argparse
import networkx as nx
import optmodel as opt
import json
import time
from time import strftime

def readGraph(graphFile):
    return nx.read_gml(graphFile)

if __name__ == "__main__":
    f = open("../../Experiments/%s-%s-%s Experiments.txt" % (time.strftime("%Y"),time.strftime("%m"),time.strftime("%d")), "a+")
    f.write("Started " + time.strftime("%c") + "\n")
    f.write("Landscape|Landowners|Budget|Expected Damage|Total Run Time|Second Stage Time|Create Model Time|Optimize Time|Allocation|Levels|Allocation Method|Total Budget Used|Remaining Budget|Maximum Amount Offered|Level Amounts|Area of Each Landowner|Time Completed\n")
    parser = argparse.ArgumentParser(description='Read filenames.')
    parser.add_argument('-g', '--graph', help='the graph file', default = "../../data/Santa Fe/SantaFe.gml")
    parser.add_argument('-p', '--params', help='the parameters file', default = "../../params/paramsFile.json")
    parser.add_argument('-c', '--coords', help='node coordinates', default = "../../params/nodeCoordinates.json")
    args = parser.parse_args()
    paramsFile = args.params
    nodeCoords = args.coords
    graph = readGraph(args.graph)
    paramsDict = json.loads(open(paramsFile).read())
    nodeCoordinates = json.loads(open(nodeCoords).read())
    for u in (0, 1, 2):
        paramsDict["method"] = u
        for n in (3, 4, 5, 6, 8, 9, 10):
            paramsDict["numLandowners"] = n
            budget = 20000
            while budget <= 100000:
                paramsDict["budget"] = budget
                for levels in (2, 5, 10, 15, 20):
                    paramsDict["numFinancialAsstLevels"] = levels
                    for r in range(5):
                        optModel = opt.OptimizationModel(graph, paramsDict, nodeCoordinates)              
                        optModel.writeResults(f)
                        f.flush()
                budget = budget + 20000
    f.write("Ended " + time.strftime("%c"))
    f.close()