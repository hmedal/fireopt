import unittest
import src.opt.fireopt as fireopt

class TestFireOpt(unittest.TestCase):

    def test_readGraph(self):
        graphFile = "../data/SanteFe.gml"
        graph = fireopt.readGraph(graphFile)
        self.assertGreater(len(graph.nodes()), 0)