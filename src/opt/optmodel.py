'''
Created on Dec 13, 2016
@author: hm568, tb2038, mcm600
'''

from gurobipy import *
import networkx as nx

class OptimizationModel(gurobi.Model):
    '''
    classdocs
    '''
    
    '''
    Constructor
    '''
    def __init__(self, graph, paramDF, Budget_param, nScenario):
        self.nScenario = nScenario
        self.Budget_param = Budget_param
        self.Prob = self.ProbDecisionState(paramDF)
        self.numberOfFinancialAsstValues = 5
        self.SecondStgValues = self.CalcAllSecondStageValues()
        self.setParams(graph, paramDF, Budget_param)
        self.landowners = self.createLandownersList(graph)
        self.createModel()
        
    def setParams(self, graph, paramDF, Budget_param):
        self.graph = graph
        self.paramDF = paramDF
        self.Budget_param = Budget_param

    def createLandownersList(self, graph):
        #iterate through nodes in graph and return a list of all the unique landowners
        landowners = {}
        ownerNames = []
        ownerNums = []
        
        for nodeNum,nodeAttr in list(graph.nodes(data=True)):
            if nodeAttr['owner'] not in ownerNames:
                ownerNames.append(nodeAttr['owner'])
        
        ownerNameNum = zip(ownerNames, range(len(ownerNames)))
        
        for name, number in ownerNameNum:
            landowners[name] = number.int()
            ownerNums.append(number)
        
        return landowners, ownerNums

    def createModel(self):
        w = {}
        self.y = {}
        
        #part of 6a
        for n in range(self.nScenario):
            for k in range(self.numberOfFinancialAsstValues): #I'm not sure how the "paramDF" file will be structured--this is temporary
                for j in self.ownerNums:
                    w[j][k][n] = self.addVar(vtype=GRB.INTEGER, name="w_"+str(j)+"_"+str(k)+"_"+str(n))   
        
        #6b
        for r in range(2, len(self.ownerNums):
            for n in range(self.nScenario):
                self.addConstr()
                
        #6c
        #
        
        
        #Constraint 6d
        #the sum of the financial assistance offered to all landowners is less than or equal to the agency's budget
        self.addConstr(quicksum(finAssist[j] for j in self.ownerNums) <= self.Budget_param, name="budget_constraint")
        
        #Constraint 6e
        for j in self.ownerNums:
            self.addConstr(quicksum([self.y[j][k] for k in range(self.numberOfFinancialAsstValues)]) == 1)
        
        #Constraint 6f
        for k in range(self.numberOfFinancialAsstValues): #temporary until we have "paramDF" file
            for j in self.ownerNums:
                self.y[j][k] = self.addVar(vtype=GRB.BINARY, name="y_"+str(j)+"_"+str(k))
                        
        #set objective
        lastLandowerIndex = len(self.ownerNums) - 1
        self.setObjective(quicksum([w[lastLandowerIndex][k][n] for k in range(self.numberOfFinancialAsstValues) for n in range(self.nScenario)]), GRB.MINIMIZE)

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
        
        for s in range(self.nScenario):
            secondStageValues[s] = self.CalcSecondStageValue()
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
    
    def Solve(self, createModel):
        
        
        return ObjVal, optSol
