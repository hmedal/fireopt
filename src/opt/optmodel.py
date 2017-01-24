'''
Created on Dec 13, 2016

@author: hm568, tb2038

'''

class OptimizationModel(object):
    '''
    classdocs
    '''
    
    '''
    Constructor
    '''
    def __init__(self, graph, paramDF, Budget_param):
        Fire_model = self.createModel()
        Prob = self.ProbDecisionState(paramDF)
        SecondStgValue = self.CalcSecondStageValue()
        self.Solve(Fire_model, Budget_param, Prob, SecondStgValue)
        
    
    def createModel(self):
        pass
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
    
    def CalcSecondStageValue(self):
        
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
