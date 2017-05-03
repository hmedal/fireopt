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
import time
from Data_SantaFe import *

class OptimizationModel():
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
        self.LandOwnerNodeList = self.LandOwnerNodeList()
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
        
        #Create variables
        for n in range(self.nScenario):
            for k in range(self.numberOfFinancialAsstValues):
                for j in range(self.ownerNums+1):
                    w[j, k, n] = m.addVar(vtype=GRB.CONTINUOUS, name="w_"+str(j)+"_"+str(k)+"_"+str(n))   
        
        for k in range(self.numberOfFinancialAsstValues):
            for j in range(self.ownerNums):
                self.y[j, k] = m.addVar(vtype=GRB.BINARY, name="y_"+str(j)+"_"+str(k))
        
        m.update()
        
        #6b
        for n in range(self.nScenario):
            m.addConstr(quicksum(w[0,k,n] for k in range(self.numberOfFinancialAsstValues)) == self.SecondStgValues[n], name = "6b_n"+str(n))
        
        #6c
        for r in range(2, self.ownerNums+1):
            for n in range(self.nScenario):
                m.addConstr(quicksum(quicksum(self.ProbDict[n, r-1, l, k]*w[r-1,k,n] for l in (0,1))
                                        for k in self.numberOfFinancialAsstValues) == quicksum(w[r, k, n] for k in self.numberOfFinancialAsstValues), name = "6c_r"+str(r)+"_n"+str(n))
                
        #6d
        #m.addContr(w[r, k, n] <= self.y[r, k]*self.SecondStgValues[n] for r in range(1, len(self.ownerNums)) for k in range(self.numberOfFinancialAsstValues) for n in range(self.nScenario))
        
        for k in range(self.numberOfFinancialAsstValues):
            for r in range(self.ownerNums):
                for n in range(self.nScenario):
                    m.addConstr(w[r, k, n] <= self.y[r, k]*self.SecondStgValues[n-1], name = "6c_r"+str(r)+"_k"+str(k)+"_n"+str(n))
        
        #6e
        m.addConstr(quicksum(quicksum(self.C_k[k]*self.y[j, k] for k in self.numberOfFinancialAsstValues)for j in self.ownerNums) <= self.Budget_param, name = "6e")
        
        #6f
        for j in range(self.ownerNums):
            m.addConstr(quicksum(self.y[j, k] for k in range(self.numberOfFinancialAsstValues)) == 1, name = "6f_r"+str(j))
                                              
        #6a -- Objective
        m.setObjective(quicksum(quicksum(w[len(self.ownerNums) - 1, k, n] for k in range(self.numberOfFinancialAsstValues)) for n in range(self.nScenario)), GRB.MINIMIZE)        

        m.update()
        
        m.optimize()
        
        return m

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
    def LandOwnerNodeList(self):
        Graph= nx.read_gml('SantaFe.gml')
        Landowners_node_lst = {}
        for i in range(len(self.ownerNums)):
            Landowners_node_lst[i] = [] 
        
        for node in Graph.nodes(data=True):
        #print "node", node[0]
            for i in range(len(self.ownerNums)): 
                if int(node[1]['owner']) == i+1: ##checking the owner of a node in data.gml is the owner in the list
                    Landowners_node_lst[i].append(node[0]) 
    
    def spread(self, ignition_points, Land):

        SumBurnt = 0
        Burnt_WUI = 0
    
        for nod in Land.nodes():
            min_arrival_time = Duration[0] + 0.00001
            for igpoint in ignition_points:
    
    
                if SPLength[igpoint][nod] < min_arrival_time:
                    min_arrival_time = SPLength[igpoint][nod]
                    #Land.node[nod]['fire'] = igpoints.index(igpoint)+1
                    Land.node[nod]['is_it_burned'] = 1
    
            Land.node[nod]['fire_arrival_time'] = min_arrival_time
    
    
        for nod in Land.nodes():
            if Land.node[nod]['fire_arrival_time'] <= fire_duration:
                Land.node[nod]['is_it_burned'] = 1
    
                SumBurnt += ValueAtRisk[nod]
    
                if Land.node[nod]['fire'] == 1:
                    Land.node[nod]['color'] = 'r'   ###what's the use of different color-illustration
    
                if Land.node[nod]['fire'] == 2:
                    Land.node[nod]['color'] = 'y'
    
                if Land.node[nod]['fire'] == 3:
                    Land.node[nod]['color'] = 'orange'
    
                if Land.node[nod]['fire'] == 4:
                    Land.node[nod]['color'] = 'pink'
    
                if Land.node[nod]['fire'] == 5:
                    Land.node[nod]['color'] = 'white'
    
                if Land.node[nod]['WUI'] == 1:
                    Burnt_WUI += 1
    
        for i in range(0,len(igpoints)):
            Land.node[igpoints[i]]['color'] = 'b'
    
        return (SumBurnt, Burnt_WUI)
    
    def Generate_Random_igpoint(self, Num_igpoints): #randomly generate upto 5 ignition point

        correctOrder = False
    
        while(not correctOrder):
    
            nodes = random.sample(range(0, N_Nodes-1), Num_igpoints)
    
            if Num_igpoints == 2:
    
                nod1 = nodes[0]
                nod2 = nodes[1]
    
    
                if (nod1 < nod2):
                    correctOrder = True
    
            if Num_igpoints == 3:
    
                nod1 = nodes[0]
                nod2 = nodes[1]
                nod3 = nodes[2]
    
                if (nod1 < nod2 < nod3):
                    correctOrder = True
    
            if Num_igpoints == 4:
    
                nod1 = nodes[0]
                nod2 = nodes[1]
                nod3 = nodes[2]
                nod4 = nodes[3]
    
                if (nod1 < nod2 < nod3 < nod4):
                    correctOrder = True
    
            if Num_igpoints == 5:
    
                nod1 = nodes[0]
                nod2 = nodes[1]
                nod3 = nodes[2]
                nod4 = nodes[3]
                nod5 = nodes[4]
    
                if (nod1 < nod2 < nod3 < nod4 < nod5):
                    correctOrder = True
    
        return(nodes)
    
    def SDCalculate(self, Burnt,Number_scenario_counted,which):

        SumBurnt = sum([i[which] for i in Burnt])
        AverageBurnt = float(SumBurnt)/Number_scenario_counted
    
        SumSquare_deviation_of_mean = sum([(i[which] - AverageBurnt)**2 for i in Burnt])
    
        sdBurnt = (float(SumSquare_deviation_of_mean)/Number_scenario_counted)**0.5
    
        return(AverageBurnt, sdBurnt)
    
    
    def CalcAllSecondStageValues(self):
        secondStageValues = {}
        #secondStageValues[s] = self.CalcSecondStageValue()
        for s in range(self.nScenario):
            Land = DGG.copy() ####DGG the data graph
            Duration = [24*60]
            fire_duration = Duration[0] ##data
            for nod in Land.nodes():
                Land.node[nod]['color'] = 'g'
                Land.node[nod]['fire_arrival_time'] = fire_duration + 100 ## Add 100 to make it very large initially
                Land.node[nod]['fire'] = 0
                Land.node[nod]['is_it_burned'] = 0
                if ValueAtRisk[nod] > 1:
                    Land.node[nod]['WUI'] = 1
                    Sum_WUI += 1
                else:
                    Land.node[nod]['WUI'] = 0
            
            fire_duration = Duration[0]
            MaxDuration = max(Duration) + 100 ## Duration comes from where...why add 100?? 
    
            t = [[MaxDuration for i in range(N_Nodes)] for i in range(N_Nodes)]  ## where from N_nodes comes-the data
    
            for r in range(N_Nodes):
    
                for q in Neighbor[r]:  ##where the neighbors of the nodes are defined
        
                    distance_q_r = DGG[q][r]['weight']
                    t[q][r] = distance_q_r/ROS[q][r] 
                    
                    'Distance between neighbor nodes is set'
                    'to the weight of the graph, so we can use weight instead'
    
            ###modify the time distance for the treated cells
            for Lowner in range(len(self.Decision_states[s])):
                if self.Decision_states[s][Lowner]==1:
                    for r in range(N_Nodes):
                        for q in Neighbor[r]:
                            if r or q in self.LandOwnerNodeList[Lowner]:
                                t[q][r]= 100000*60
            
            '#  Rebuilding the graph with time attribute'
            Landscape = DGG.copy() ##got the landscape with time as the distance
            
            for link in DGG.edges():
                Landscape.add_edge(link[0],link[1], Time_Distance = t[link[0]][link[1]])
            
            SPLength = nx.all_pairs_dijkstra_path_length(Landscape, weight = 'Time_Distance')
            Number_Sub_scenario_counted = 0
            SDBurnt = 100
            
            Num_igpoints = 5
            Max_Num__sub_Scenario = 5000
            
            nodes = [] 
            
            Burnt = []
            #SumBurnt = 0
            Total_Burnt= 0
            AveBurnt = 0
            
            while (Number_Sub_scenario_counted < Max_Num__sub_Scenario):
                nodes.append(self.Generate_Random_igpoint(Num_igpoints))
                igpoints = nodes[Number_Sub_scenario_counted][:Num_igpoints]
                Number_Sub_scenario_counted += 1
                Burnt.append(self.spread(igpoints, Land))
                (AveBurnt, SDBurnt) = self.SDCalculate(Burnt,Number_Sub_scenario_counted,0)
            Total_Burnt = sum([i[0] for i in Burnt])
            (AveWUIBurnt,STDWUIBurnt) = self.SDCalculate(Burnt,Number_Sub_scenario_counted,1)
            secondStageValues[s] = Total_Burnt    
              
        # fill in here
        return secondStageValues

    #def CalcSecondStageValue(self):
        # this will need to wait
        #return SecondStageValue 

    def writeResults(self, file):
        
        if m.status == GRB.Status.OPTIMAL:
            self.write("%s.sol" % file)
