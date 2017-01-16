'''
Created on Dec 13, 2016

@author: hm568, tb2038

'''

class OptimizationModel(object):
    '''
    classdocs
    '''


    def __init__(self, graph, paramsDict):
        '''
        Constructor
        '''
    
    def createModel(self):
        pass
        # create the model
    def ProbDecisionState(self, paramsDict):
        '''
        The input is the data of financial assistance offereed to the landowner's and the corresponding decision
        Calculate the probabilities of a landowner's decision state for a given amount of financial assistance
        The output is the probability of a landowner to accept a cost-share plan for a given amount of financial assistance
        '''
        return ProbDict
    
    def CalcSecondStageValue(self):
        '''
         Calculate the second stage objective value
        The output is the second stage objective value for each scenario 
         
        ''' 
        return SecondStageValue 
    
    def SolveFirststageModel(self, createModel, paramsDict, ProbDecisionState, CalcSecondStageValue):
        
        '''
        As input takes the first stage model, total budget of the decision maker, probabilities of the decision state, and second stage Value
        for each scenario.
        solve the 1st stage model and 
        returns the optimal solution (level of financial assistance offered) and the optimal solution (expected total acreage burned)
        '''
        return ObjVal, optSol
