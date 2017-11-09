import argparse
import networkx as nx
import optmodel as opt
import json
import time

def readGraph(graphFile):
    return nx.read_gml(graphFile)

if __name__ == "__main__":
    f = open("../../Experiments/Experiments 11-9-2017.txt", "a+")
    f.write("Started " + time.strftime("%c") + "\n")
    f.write("Landscape|Landowners|Budget|Expected Damage|Total Run Time|Second Stage Time|Create Model Time|Optimize Time|Allocation|Levels|Allocation Method|Total Budget Used|Remaining Budget|Maximum Amount Offered|Level Amounts|Area of Each Landowner|Time Completed\n")
    landFiles = ["SantaFe","SanBernardino","Umpqua"]
    parser = argparse.ArgumentParser(description='Read filenames.')
    parser.add_argument('-p', '--params', help='the parameters file', default = "../../params/paramsFile.json")
    for landscape in landFiles:
        parser.add_argument('-g', '--graph', help='the graph file', default = "../../data/%s.gml" % landscape)
        args = parser.parse_args()
        paramsFile = args.params
        graph = readGraph(args.graph)
        paramsDict = json.loads(open(paramsFile).read())
        paramsDict["landscape"] = landscape
        for u in (0, 1, 2):
            paramsDict["method"] = u
            for n in (3, 4, 5, 6):
                paramsDict["numLandowners"] = n
                budget = 20000
                while budget <= 100000:
                    paramsDict["budget"] = budget
                    for levels in (2, 5, 10, 15, 20):
                        paramsDict["numFinancialAsstLevels"] = levels
                        for r in range(5):
                            optModel = opt.OptimizationModel(graph, paramsDict)              
                            optModel.writeResults(f)
                            f.flush()
                    budget = budget + 20000
    f.write("Ended " + time.strftime("%c"))
    f.close()