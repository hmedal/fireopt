'''
Created on Dec 13, 2016
@author: hm568, tb2038, mcm600
'''

from gurobipy import *
import networkx as nx
import numpy as np
import pandas as pd
from sklearn import linear_model


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
        self.landowners[0] = self.createLandownersList(graph)
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
        
        #part of 6a -- create w variables
        for n in range(self.nScenario):
            for k in range(self.numberOfFinancialAsstValues): #I'm not sure how the "paramDF" file will be structured--this is temporary
                for j in self.ownerNums:
                    w[j, k, n] = self.addVar(vtype=GRB.INTEGER, name="w_"+str(j)+"_"+str(k)+"_"+str(n))   
        
        #Constraint 6f
        for k in range(self.numberOfFinancialAsstValues):
            for j in self.ownerNums:
                self.y[j, k] = self.addVar(vtype=GRB.BINARY, name="y_"+str(j)+"_"+str(k))
        
        self.update()
        
        #6b
        for r in range(2, len(self.ownerNums)):
            for n in range(self.nScenario):
                self.addConstr(quicksum(quicksum(self.ProbDict[n, r-1, l, k]*w[r-1,k,n] for l in (0,1))
                                        for k in self.numberOfFinancialAsstValues) == quicksum(w[r, k, n] for k in self.numberOfFinancialAsstValues))
                
        #6c
        #Not sure if this is the proper formatting for this constraint
        #Is this the proper use of self.SecondStgValues?
        self.addContr(w[r, k, n] <= self.y[r, k]*self.SecondStgValues[n] for r in range(1, len(self.owerNums)) for k in range(self.numberOfFinancialAsstValues) for n in range(self.nScenario))
        
        #Constraint 6d
        #the sum of the financial assistance offered to all landowners is less than or equal to the agency's budget
        #Where does C come from?
        self.addConstr(quicksum(c[k]*self.y[j, k] for j in self.ownerNums for k in self.numberOfFinancialAsstValues) <= self.Budget_param, name="budget_constraint")
        
        #Constraint 6e
        for j in self.ownerNums:
            self.addConstr(quicksum([self.y[j, k] for k in range(self.numberOfFinancialAsstValues)]) == 1)
                        
        self.update()
                                              
        #set objective
        lastLandowerIndex = len(self.ownerNums) - 1
        
        self.setObjective(quicksum(quicksum(w[lastLandownerIndex, k, n] for k in range(self.numberOfFinancialAsstValues)) for n in range(self.nScenario)), GRB.MINIMIZE)        

        self.update()

        # create the model
        
    '''
    ProbDecisionState method:
        The input is a data frame that contains the financial assistance offered to the landowner's and the corresponding decision
        Calculate the probabilities of a landowner's decision state for a given amount of financial assistance
        The output is the probability of a landowner to accept a cost-share plan for a given amount of financial assistance
    '''
    def ProbDecisionState(self, paramDF):
        Data_file = "LogRegression.csv"
        Data_df = pd.read_csv(Data_file, delimiter=',', usecols=[2, 3])
        
        nOwner = len(Data_df)
        nDecision_state = 2
        nLevel = 5
        
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
            for i in range(nOwner):
               for j in range(nDecision_state):
                    ProbDict[s, i, j, train_Feature[i,0]] = ProbDecisionState[i, j, train_Feature[i,0]]
                    
        
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
