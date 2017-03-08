'''
Created on Dec 13, 2016
@author: hm568, tb2038, mcm600
'''

from gurobipy import Model, quicksum, GRB
import networkx as nx
import numpy as np
import pandas as pd
from sklearn import linear_model
import random

class OptimizationModel(Model):
    '''
    classdocs
    '''
    
    '''
    Constructor
    '''
    def __init__(self, graph, paramDF):
        self.nScenario = paramDF['numScenarios']
        self.C_k = paramDF['Cost']
        self.Budget_param = paramDF['budget']
        self.Decision_states = self.CreateScenarioDecisionStates()
        self.Prob = self.ProbDecisionState(paramDF)
        self.numberOfFinancialAsstValues = paramDF['numFinancialAssLevel']
        self.SecondStgValues = self.CalcAllSecondStageValues()
        self.setParams(graph, paramDF)
        self.landowners[0], self.ownerNums= self.createLandownersList(graph)
        self.createModel()
        
    def setParams(self, graph, paramDF):
        self.graph = graph
        self.paramDF = paramDF
        
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
        
        m = Model("Optimization Model")
        
        #part of 6a -- create w variables
        for n in range(self.nScenario):
            for k in range(self.numberOfFinancialAsstValues): #I'm not sure how the "paramDF" file will be structured--this is temporary
                for j in self.ownerNums:
                    w[j, k, n] = m.addVar(vtype=GRB.INTEGER, name="w_"+str(j)+"_"+str(k)+"_"+str(n))   
        
        #Constraint 6f
        for k in range(self.numberOfFinancialAsstValues):
            for j in self.ownerNums:
                self.y[j, k] = m.addVar(vtype=GRB.BINARY, name="y_"+str(j)+"_"+str(k))
        
        m.update()
        
        #6b
        for r in range(2, len(self.ownerNums)):
            for n in range(self.nScenario):
                m.addConstr(quicksum(quicksum(self.ProbDict[n, r-1, l, k]*w[r-1,k,n] for l in (0,1))
                                        for k in self.numberOfFinancialAsstValues) == quicksum(w[r, k, n] for k in self.numberOfFinancialAsstValues))
                
        #6c
        #Not sure if this is the proper formatting for this constraint
        #Is this the proper use of self.SecondStgValues?
        m.addContr(w[r, k, n] <= self.y[r, k]*self.SecondStgValues[n] for r in range(1, len(self.owerNums)) for k in range(self.numberOfFinancialAsstValues) for n in range(self.nScenario))
        
        #Constraint 6d
        #the sum of the financial assistance offered to all landowners is less than or equal to the agency's budget
        #Where does C come from?
        m.addConstr(quicksum(quicksum(self.C_k[k]*self.y[j, k] for k in self.numberOfFinancialAsstValues)for j in self.ownerNums) <= self.Budget_param, name="budget_constraint")
        
        #Constraint 6e
        for j in self.ownerNums:
            m.addConstr(quicksum(self.y[j, k] for k in range(self.numberOfFinancialAsstValues)) == 1)
                        
        m.update()
                                              
        #set objective
        lastLandownerIndex = len(self.ownerNums) - 1
        
        m.setObjective(quicksum(quicksum(w[lastLandownerIndex, k, n] for k in range(self.numberOfFinancialAsstValues)) for n in range(self.nScenario)), GRB.MINIMIZE)        

        m.update()

        # create the model
        
    '''
    ProbDecisionState method:
        The input is a data frame that contains the financial assistance offered to the landowner's and the corresponding decision
        Calculate the probabilities of a landowner's decision state for a given amount of financial assistance
        The output is the probability of a landowner to accept a cost-share plan for a given amount of financial assistance
    '''
    def CreateScenarioDecisionStates(self):
        States = np.array([0, 1.0])
        Decision_states = {}
        for s in range(self.nScenario):
            Decision_states[s] = np.random.choice(States, len(self.ownerNums))
        
        return Decision_states
        
    def ProbDecisionState(self, paramDF):
        Data_file = "LogRegression.csv"
        Data_df = pd.read_csv(Data_file, delimiter=',', usecols=[2, 3])
        
        nOwner = len(Data_df)
        nDecision_state = 2
        #nLevel = 5
        
        train_Feature = Data_df['Level'].as_matrix().reshape(-1, 1)  # we only take the first two features.
        train_Target = Data_df['Decision'].as_matrix()
        
        h = .02  # step size in the mesh
        
        logreg = linear_model.LogisticRegression(C=1e5)
        
        # we create an instance of Neighbours Classifier and fit the data.
        logreg.fit(train_Feature, train_Target)
        
        #np.set_printoptions(threshold=1000000)
        
        State_prob = logreg.predict_proba(train_Feature)
        print State_prob
        
        # Put the result into a dictionary
        ProbDecisionState = {}
        for i in range(nOwner):
            for j in range(nDecision_state):
                ProbDecisionState[i, j, train_Feature[i,0]] = State_prob[i][j]
        
        ProbDict = {}
        for s in range(self.nScenario):
            for i in range(len(self.ownerNums)):
                for j in range(nDecision_state):
                    ProbDict[s, i, j, train_Feature[i,0]] = ProbDecisionState[i, j, train_Feature[i,0]]
        
        for s in range(self.nScenario):
            for i in range(len(self.ownerNums)):
                for k in range(self.numberOfFinancialAsstValues):
                    l= 0
                    if self.Decision_states[s][i]==0:
                        l=1
                    ProbDict[s, i, l, k]= 0
        
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

    def writeResults(self, file):
        
        if m.status == GRB.Status.OPTIMAL:
            self.write("%s.sol" % file)
