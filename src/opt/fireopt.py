import argparse
import networkx as nx
import optmodel as opt
import json
import timeit

#start = timeit.default_timer()

def readGraph(graphFile):
    return nx.read_gml(graphFile)


for n in (3, 4, 5, 6):
    if __name__ == "__main__":
        parser = argparse.ArgumentParser(description='Read filenames.')
        parser.add_argument('-g', '--graph', help='the graph file', default = "../../data/SantaFe.gml")
        parser.add_argument('-p', '--params', help='the parameters file', default = "../../params/paramsFile.json")
        args = parser.parse_args()
        paramsFile = args.params
        graph = readGraph(args.graph)
        paramsDict = json.loads(open(paramsFile).read())
        budget = 20000
        while budget <= 100000:
            for levels in (2, 5, 10, 15):
                start = timeit.default_timer()
                paramsDict["budget"] = budget
                paramsDict["numFinancialAsstLevels"] = levels
                paramsDict["numLandowners"] = n
#           optModel = opt.OptimizationModel(graph, paramsDict, None, None)
                optModel = opt.OptimizationModel(graph, paramsDict)
#           optModel.optimize()
#           print "We've made it this far!"
#                optModel.writeResults('modified Santa Fe results 14')
#           print "The file has been created."
                stop = timeit.default_timer()
                optModel.writeResults('new experiment.txt', start, stop)
                print "Total run time: %s" % (stop - start)
            budget = budget + 20000
    
#stop = timeit.default_timer()

#print "Total run time: %s" % (stop - start)