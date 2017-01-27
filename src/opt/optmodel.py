'''
Created on Dec 13, 2016

@author: hm568, tb2038

'''

import gurobipy as gurobi
import networkx as nx

class OptimizationModel(gurobi.Model):
    '''
    classdocs
    '''
    
    '''
    Constructor
    '''
    def __init__(self, graph, paramDF, Budget_param):
        self.Prob = self.ProbDecisionState(paramDF)
        self.SecondStgValue = self.CalcSecondStageValue()
        self.setParams(graph, paramDF, Budget_param)
        self.createModel()
        
    def setParams(self, graph, paramDF, Budget_param):
        self.graph = graph
        self.paramDF = paramDF
        self.Budget_param = Budget_param

    def createModel(self):
        for node in self.graph.nodes():
            pass
            #self.addVar()
        #self.addConstr()
        #self.setObjective()
        # create the model
        
    '''
    ProbDecisionState method:
        The input is a data frame that contains the financial assistance offered to the landowner's and the corresponding decision
        Calculate the probabilities of a landowner's decision state for a given amount of financial assistance
        The output is the probability of a landowner to accept a cost-share plan for a given amount of financial assistance
    '''
    def ProbDecisionState(self, paramDF):
        
        return ProbDict
    
    '''
    CalcSecondStageValue method:
         Calculate the second stage objective value
        The output is the second stage objective value for each scenario 
         
    ''' 

    def CalcAllSecondStageValues(self):
        secondStageValues = {}
        # fill in here
        return secondStageValues

    def CalcSecondStageValue(self):
        # this will need to wait
        return SecondStageValue 
    
    '''
    Solve method:
        As input takes the first stage model, total budget of the decision maker, probabilities of the decision state, and second stage Value
        for each scenario.
        solve the 1st stage model and 
        returns the optimal solution (level of financial assistance offered) and the optimal solution (expected total acreage burned)
    '''
    
    def Solve(self, createModel, Budget_param, ProbDecisionState, CalcSecondStageValue):
        
        
        return ObjVal, optSol
