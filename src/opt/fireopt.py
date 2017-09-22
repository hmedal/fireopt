import argparse
import networkx as nx
import optmodel as opt
import json
import timeit

#start = timeit.default_timer()

def readGraph(graphFile):
    return nx.read_gml(graphFile)

n = 3

while n < 8:
    if __name__ == "__main__":
        parser = argparse.ArgumentParser(description='Read filenames.')
        parser.add_argument('-g', '--graph', help='the graph file', default = "../../data/SantaFe with %s landowners.gml" % n)
        parser.add_argument('-p', '--params', help='the parameters file', default = "../../params/paramsFile.json")
        args = parser.parse_args()
        paramsFile = args.params
        graph = readGraph(args.graph)
        paramsDict = json.loads(open(paramsFile).read())
        budget = 40000
        while budget <= 100000:
            for levels in (5, 10):
                start = timeit.default_timer()
                paramsDict["budget"] = budget
                paramsDict["numFinancialAsstLevels"] = levels
#           optModel = opt.OptimizationModel(graph, paramsDict, None, None)
                optModel = opt.OptimizationModel(graph, paramsDict)
#           optModel.optimize()
#           print "We've made it this far!"
#                optModel.writeResults('modified Santa Fe results 14')
#           print "The file has been created."
                stop = timeit.default_timer()
                optModel.writeResults('uniform experiments.txt', start, stop)
                print "Total run time: %s" % (stop - start)
            budget = budget + 20000
    n = n + 1
    
#stop = timeit.default_timer()

#print "Total run time: %s" % (stop - start)