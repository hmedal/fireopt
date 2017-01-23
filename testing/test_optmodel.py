import unittest
import src.opt.optmodel as opt
import networkx as nx
import json
import pandas as pd

class TestOptModel(unittest.TestCase):

    def setUp(self):
        graphFile = "../data/SanteFe.gml"
        self.graph = nx.read_gml(graphFile)
        paramsFile = "../params/paramsFile.json"
        self.paramsDict = json.loads(open(paramsFile).read())

    def test_createModel(self):
        pass

    def test_ProbDecisionState(self):
        d = {'amountOffered': pd.Series([1., 2., 3.], index=['a', 'b', 'c', 'd']), 'decision': pd.Series([1., 0., 0., 1.], index=['a', 'b', 'c', 'd'])}
        df = pd.DataFrame(d)

    def test_CalcSecondStageValue(self):
        pass

    def test_SolveFirststageModel(self):
        pass