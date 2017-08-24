import argparse
import networkx as nx
import optmodel as opt
import json
import timeit

start = timeit.default_timer()

def readGraph(graphFile):
    return nx.read_gml(graphFile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read filenames.')
    parser.add_argument('-g', '--graph', help='the graph file', default = "../../data/SantaFe with 3 landowners.gml")
    parser.add_argument('-p', '--params', help='the parameters file', default = "../../params/paramsFile.json")
    args = parser.parse_args()
    paramsFile = args.params
    graph = readGraph(args.graph)
    paramsDict = json.loads(open(paramsFile).read())
#    optModel = opt.OptimizationModel(graph, paramsDict, None, None)
    optModel = opt.OptimizationModel(graph, paramsDict)
#    optModel.optimize()
    print "We've made it this far!"
    optModel.writeResults('modified Santa Fe results 4')
    print "The file has been created."

stop = timeit.default_timer()

print "Total run time: %s" % (stop - start)