import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Read filenames.')
    parser.add_argument('-g', '--graph', help='the graph file', default = "../../data/SanteFe.gml")
    parser.add_argument('-p', '--graph', help='the parameters file', default = "../../params/params.json")
    args = parser.parse_args()
    graphFile = args.graph
    # read in data from file
    # read in parameters from file
    # create optimization model
    # solve optimization model
    # write results to file