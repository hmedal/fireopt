
import argparse
import json
import timeit
from gurobipy import Model, quicksum, GRB
import networkx as nx
import numpy as np
import pandas as pd
from sklearn import linear_model
import random
import time
from Data_SantaFe import *
import pickle
import os.path
import array


class OptimizationModel():
    '''
    classdocs
    '''

    '''
    Constructor
    '''

    def __init__(self, graph, paramDF, NumFinancialAssistanceValues):
        self.Budget_param = paramDF['budget']
        self.numberOfFinancialAsstValues = NumFinancialAssistanceValues
        self.numLandowners = paramDF['numLandowners']
        self.graph = self.reassignLandowners(graph)
        self.landowners, self.ownerNums, self.nOwners = self.createLandownersList()
        print "ownerNums", self.ownerNums
        self.nScenario = (2) ** (self.nOwners)
        self.Cell_area = 3.4595
        print "number of scenarios: ", self.nScenario
        #        self.setParams(graph, paramDF)
        self.LandOwnerNodeList, self.AreaBelongsToLandowners = self.LandOwnerNodeList()
        print "LandOwnerNodeList", self.LandOwnerNodeList
        self.Decision_states = self.CreateScenarioDecisionStates()
        self.Prob, self.C_k, self.maxOffered = self.ProbDecisionState()
        self.SecondStgValues = self.CalcAllSecondStageValues()
        self.DecisionProb = self.filterProbDict()
        self.m = self.createModel()

    '''
    def setParams(self, graph, paramDF):
        self.graph = graph
        self.paramDF = paramDF
    '''
    def reassignLandowners(self, graph):
        reassigned = []

        acreNodes = np.arange(nx.number_of_nodes(graph))

        reassigned = np.array_split(acreNodes, self.numLandowners)

        for owner in range(len(reassigned)):
            for acres in reassigned[owner]:
                graph.node[acres]['owner'] = owner + 1

        return graph

    def createLandownersList(self):

        landowners = {}
        ownerNames = []
        ownerNums = []
        nOwners = 0
        for nodeNum, nodeAttr in list(self.graph.nodes(data=True)):
            if nodeAttr['owner'] not in ownerNames:
                ownerNames.append(nodeAttr['owner'])

        ownerNameNum = zip(ownerNames, range(len(ownerNames)))

        for name, number in ownerNameNum:
            landowners[name] = int(number)
            ownerNums.append(number)
            nOwners = nOwners + 1

        return landowners, ownerNums, nOwners

    def filterProbDict(self):
        DecisionProb = {}
        #        print self.Prob
        for n in range(self.nScenario):
            for k in range(self.numberOfFinancialAsstValues):
                for j in range(self.nOwners):
                    for l in (0, 1):
                        if (n, j, l, k) in self.Prob:
                            #                            print "[%s,%s,%s,%s]" % (n,j,l,k)
                            if self.Prob[n, j, l, k] > -99:
                                #                                print "This worked."
                                DecisionProb[n, j, k] = self.Prob[n, j, l, k]
                                #        print DecisionProb
        return DecisionProb

    def lDecState(self, n, r):
        l = 0

        if self.Prob[n, r, l, 0] == -99:
            l = 1

        return l

    '''
    def kLevel(self, r, n):

        kLevel = []

        for k in self.numberOfFinancialAsstValues:
            if self.Prob(n, r, lDecState(r,n),k) > 0.00001:
                kLevel.append(k)

        return kLevel
    '''

    def createModel(self):
        w = {}
        self.y = {}

        m = Model("Optimization Model")

        # Create variables
        for n in range(self.nScenario):
            for k in range(self.numberOfFinancialAsstValues):
                for j in range(self.nOwners):
                    w[j, k, n] = m.addVar(vtype=GRB.CONTINUOUS, name="w_j" + str(j) + "_k" + str(k) + "_n" + str(n))

        for k in range(self.numberOfFinancialAsstValues):
            for j in range(self.nOwners):
                self.y[j, k] = m.addVar(vtype=GRB.BINARY, name="y_j" + str(j) + "_k" + str(k))

        m.update()

        #        for n in (n,j,k) in self.DecisionProb:
        #            m.addConstr(quicksum(w[0,k,n] for k in (n,j,k) in self.DecisionProb) ==
        #                        self.SecondStgValues[n]*quicksum(self.DecisionProb[n,0,k]*self.y[0, k]
        #                        for k in (n,j,k) in self.DecisionProb), name = "6a_n"+str(n))

        # 6a updated
        for n in range(self.nScenario):
            m.addConstr(quicksum(w[0, k, n] for k in range(self.numberOfFinancialAsstValues)) ==
                        self.SecondStgValues[n] * quicksum(self.DecisionProb[n, 0, k] * self.y[0, k]
                                                           for k in range(self.numberOfFinancialAsstValues)),
                        name="6a_n" + str(n))

        # 6b updated
        for r in range(1, self.nOwners):
            for n in range(self.nScenario):
                # sum1 = 0
                # sum2 = 0
                # for k in range(self.numberOfFinancialAsstValues):
                #    if self.DecisionProb[n,r-1,k] > 0.00001:
                #        sum1 += w[r-1,k,n]
                #    if self.DecisionProb[n,r,k] > 0.00001:
                #        sum2 += w[r,k,n]*(1/self.DecisionProb[n,r,k])
                m.addConstr(quicksum(w[r - 1, k, n] for k in range(self.numberOfFinancialAsstValues)) ==
                            quicksum(w[r, k, n] * (1 / max(self.DecisionProb[n, r, k], 0.00001))
                                     for k in range(self.numberOfFinancialAsstValues)),
                            name="6b_j" + str(r) + "_n" + str(n))
                # m.addConstr(sum1 == sum2, name="6b_j" + str(r) + "_n" + str(n))

        # 6c updated
        for k in range(self.numberOfFinancialAsstValues):
            for r in range(self.nOwners):
                for n in range(self.nScenario):
                    m.addConstr(w[r, k, n] <= self.y[r, k] * self.SecondStgValues[n],
                                name="6c_j" + str(r) + "_k" + str(k) + "_n" + str(n))

        # 6e
        m.addConstr(quicksum(quicksum(self.C_k[k] * self.y[j, k] for k in range(self.numberOfFinancialAsstValues)) *
                             self.AreaBelongsToLandowners[j]
                             for j in range(self.nOwners)) <= self.Budget_param, name="6e")

        # 6f
        for j in range(self.nOwners):
            m.addConstr(quicksum(self.y[j, k] for k in range(self.numberOfFinancialAsstValues)) == 1,
                        name="6f_j" + str(j))

        # 6g -- Uniform
        for j in range(self.nOwners - 1):
            for k in range(self.numberOfFinancialAsstValues):
                m.addConstr(self.y[j, k] == self.y[j + 1, k], name="uniform constraint")
                #                m.addConstr(self.y[j, 0] == 0, name = "greater than 0")

        # 6a -- Objective
        m.setObjective(quicksum(quicksum(w[self.nOwners - 1, k, n] for k in range(self.numberOfFinancialAsstValues))
                                for n in range(self.nScenario)), GRB.MINIMIZE)

        m.update()

        m.optimize()

        return m

    

    def CreateScenarioDecisionStates(self):
        l = [bin(x)[2:].rjust(len(self.ownerNums), '0') for x in range(2 ** len(self.ownerNums))]
        print "l", l
        # States = np.array([0, 1.0])
        Decision_states = {}
        for s in range(self.nScenario):
            Decision_states[s] = [int(l[s][j]) for j in range(len(self.ownerNums))]

        return Decision_states


    def ProbDecisionState(self):

        #Data_file = "../../data/Synthetic Data.csv"
        Data_file = "Synthetic Data.csv"
        Data_df = pd.read_csv(Data_file, delimiter=',', usecols=[1, 2, 3])
        print "Data_df", Data_df
        nOwner = (len(self.ownerNums))
        nDecision_state = 2

        train_Feature = Data_df['Amount'].as_matrix().reshape(-1, 1)  
        train_Target = Data_df['Decision'].as_matrix()

        h = .02  # step size in the mesh

        logreg = linear_model.LogisticRegression(C=1e5)

        
        logreg.fit(train_Feature, train_Target.astype(str))

        
        minimum_amount_offered = Data_df['Amount'].min()
        maximum_amount_offered = Data_df['Amount'].max()

        print "minimum_amount_offered", minimum_amount_offered
        print "maximum_amount_offered", maximum_amount_offered

        Amount_increment = (maximum_amount_offered - minimum_amount_offered) / (self.numberOfFinancialAsstValues - 1)

        DiscretizedFinancialAmountValues = [] 
        DiscretizedFinancialAmountValues.append(minimum_amount_offered)
        for i in range(self.numberOfFinancialAsstValues - 1):
            DiscretizedFinancialAmountValues.append(DiscretizedFinancialAmountValues[
                                                        -1] + Amount_increment)  
        

        InputArrayForProbEstimation = np.array(DiscretizedFinancialAmountValues)
        print "InputArrayForProbEstimation", InputArrayForProbEstimation

        Estimated_prob = logreg.predict_proba(InputArrayForProbEstimation.reshape(-1, 1))
        

       
        ProbDict = {}

        for s in range(self.nScenario):
            for i in range(len(self.ownerNums)):
                for j in range(nDecision_state):
                    for k in range(self.numberOfFinancialAsstValues):
                        ProbDict[s, i, j, k] = Estimated_prob[k, j]

        for s in range(self.nScenario):
            for i in range(len(self.ownerNums)):
                for k in range(self.numberOfFinancialAsstValues):
                    l = 0
                    if self.Decision_states[s][i] == 0:
                        l = 1
                    ProbDict[s, i, l, k] = -99

        return ProbDict, DiscretizedFinancialAmountValues, maximum_amount_offered

   

    def LandOwnerNodeList(self):
        
        Landowners_node_lst = {}
        for i in range(len(self.ownerNums)):
            Landowners_node_lst[i] = []

        for node in self.graph.nodes(data=True):
            # print "node", node[0]
            for i in range(len(self.ownerNums)):
                if int(node[1]['owner']) == i + 1:  
                    Landowners_node_lst[i].append(node[0])

        AreaOfLandowners = [] 
        for i in range(len(self.ownerNums)):
            total_land_area = self.Cell_area * len(Landowners_node_lst[i])
            AreaOfLandowners.append(total_land_area)

        print "AreaOfLandowners", AreaOfLandowners
        return Landowners_node_lst, AreaOfLandowners

    def spread(self, ignition_points, Land, SPLength, fire_duration):

        SumBurnt = 0
        Burnt_WUI = 0

        for nod in Land.nodes():
            min_arrival_time = Duration[0] + 0.00001
            for igpoint in ignition_points:

                if SPLength[igpoint][nod] < min_arrival_time:
                    min_arrival_time = SPLength[igpoint][nod]
                    # Land.node[nod]['fire'] = igpoints.index(igpoint)+1
                    Land.node[nod]['is_it_burned'] = 1

            Land.node[nod]['fire_arrival_time'] = min_arrival_time

        for nod in Land.nodes():
            if Land.node[nod]['fire_arrival_time'] <= fire_duration:
                Land.node[nod]['is_it_burned'] = 1

                SumBurnt += ValueAtRisk[nod]

                if Land.node[nod]['fire'] == 1:
                    Land.node[nod]['color'] = 'r'  

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

        for i in range(0, len(ignition_points)):
            Land.node[ignition_points[i]]['color'] = 'b'

        return (SumBurnt, Burnt_WUI)

    def Generate_Random_igpoint(self, Num_igpoints):  

        correctOrder = False

        while (not correctOrder):

            nodes = random.sample(range(0, N_Nodes - 1), Num_igpoints)

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

        return (nodes)

    def SDCalculate(self, Burnt, Number_scenario_counted, which):

        SumBurnt = sum([i[which] for i in Burnt])
        AverageBurnt = float(SumBurnt) / Number_scenario_counted

        SumSquare_deviation_of_mean = sum([(i[which] - AverageBurnt) ** 2 for i in Burnt])

        sdBurnt = (float(SumSquare_deviation_of_mean) / Number_scenario_counted) ** 0.5

        return (AverageBurnt, sdBurnt)

    def CalcAllSecondStageValues(self):
        secondStageValues = {}

        scenario_nodelist = {}
        fname = str(self.nScenario) + 'scenario_nodelist.txt'
        if os.path.isfile(fname):
            f = open(fname, 'rb')  # Pickle file is newly created
            scenario_nodelist = pickle.load(f)  # dump data to f
            f.close()

        
        nodes = []  

        node_gen = 0


        for s in range(self.nScenario):
            Land = DGG.copy()  
            Duration = [24 * 60]
            fire_duration = Duration[0]  
            for nod in Land.nodes():
                Land.node[nod]['color'] = 'g'
                Land.node[nod]['fire_arrival_time'] = fire_duration + 100  
                Land.node[nod]['fire'] = 0
                Land.node[nod]['is_it_burned'] = 0
                if ValueAtRisk[nod] > 1:
                    Land.node[nod]['WUI'] = 1
                    Sum_WUI += 1
                else:
                    Land.node[nod]['WUI'] = 0

            # fire_duration = Duration[0]
            MaxDuration = max(Duration) + 100 

            t = [[MaxDuration for i in range(N_Nodes)] for i in range(N_Nodes)]  

            for r in range(N_Nodes):

                for q in Neighbor[r]: 

                    distance_q_r = DGG[q][r]['weight']
                    t[q][r] = distance_q_r / ROS[q][r]

             
            for Lowner in range(len(self.Decision_states[s])):
                if self.Decision_states[s][Lowner] == 1:
                    for r in range(N_Nodes):
                        for q in Neighbor[r]:
                            if q in self.LandOwnerNodeList[Lowner]:
                                t[q][r] = 100000 * 60

            
            Landscape = DGG.copy()  
            for link in DGG.edges():
                Landscape.add_edge(link[0], link[1], Time_Distance=t[link[0]][link[1]])

            SPLength = nx.all_pairs_dijkstra_path_length(Landscape, weight='Time_Distance')
            Number_Sub_scenario_counted = 0
            SDBurnt = 100

            Num_igpoints = 5
            Max_Num__sub_Scenario = 5000

        

            Burnt = []
            # SumBurnt = 0
            Total_Burnt = 0
            AveBurnt = 0

            while (Number_Sub_scenario_counted < Max_Num__sub_Scenario):
               
                if os.path.isfile(fname):
                    nodes = scenario_nodelist[s]
                    print "File exists.................................."
                else:
                    if node_gen == 0:  
                        nodes.append(self.Generate_Random_igpoint(Num_igpoints))
                igpoints = nodes[Number_Sub_scenario_counted][:Num_igpoints]
                
                Number_Sub_scenario_counted += 1
                Burnt.append(self.spread(igpoints, Land, SPLength, fire_duration))
                (AveBurnt, SDBurnt) = self.SDCalculate(Burnt, Number_Sub_scenario_counted, 0)
            Total_Burnt = sum([i[0] for i in Burnt])
            (AveWUIBurnt, STDWUIBurnt) = self.SDCalculate(Burnt, Number_Sub_scenario_counted, 1)
            secondStageValues[s] = AveBurnt
            scenario_nodelist[s] = nodes
            node_gen = node_gen + 1
            print "Scenario %s" % (s)
        
        
        if os.path.isfile(fname) == False:
            f = open(fname, 'wb')  
            pickle.dump(scenario_nodelist, f)  
            f.close()

        return secondStageValues


    def writeResults(self):
        
        if self.m.status == GRB.Status.OPTIMAL:
            print ('\nOBJECTIVE VALUE: %g' % self.m.objVal)
            for v in self.m.getVars():
                print('%s %g' % (v.varName, v.x))
            for n in range(self.nScenario):
                for r in range(self.nOwners):
                    for k in range(self.numberOfFinancialAsstValues):
                        print "[%s,%s,%s] = %s" % (n, r, k, self.DecisionProb[n, r, k])
            allocations = []
            print self.Budget_param, self.m.objVal
            print "offer allocation:"
            for j in range(self.nOwners):
                for k in range(self.numberOfFinancialAsstValues):
                    if self.m.getVarByName("y_j%s_k%s" % (j, k)).x == 1:
                        allocations.append(k)
                        print "%s: %s" % (j, k)
            
            for k in range(self.numberOfFinancialAsstValues):
                print self.C_k[k]
            print "area of each landowners:"
            for j in range(self.nOwners):
                print self.AreaBelongsToLandowners[j]

            TotalBudgetUsed = 0
            for j in range(self.nOwners):
                TotalBudgetUsed = TotalBudgetUsed + self.C_k[allocations[j]] * self.AreaBelongsToLandowners[j]
            RemainingBudget = self.Budget_param - TotalBudgetUsed

            #f.write("%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n" % (
            #self.nOwners, self.Budget_param, self.m.objVal, allocations, self.numberOfFinancialAsstValues,
            #TotalBudgetUsed, RemainingBudget, self.maxOffered, self.C_k, self.AreaBelongsToLandowners))
            print "The file has been updated."

        return self.m.objVal, TotalBudgetUsed


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Read filenames.')
    parser.add_argument('-g', '--graph', help='the graph file', default = "SantaFe.gml")
    #parser.add_argument('-g', '--graph', help='the graph file', default="SantaFe with 3 landowners.gml")
    #parser.add_argument('-p', '--params', help='the parameters file', default = "../../params/paramsFile.json")
    parser.add_argument('-p', '--params', help='the parameters file', default="params/paramsFile.json")
    args = parser.parse_args()
    paramsFile = args.params
    graph = nx.read_gml(args.graph)
    paramsDict = json.loads(open(paramsFile).read())
    ofile = open("Relative error.txt", "a")
    for n in (3, 4, 5, 6):
        paramsDict["numLandowners"] = n
        budget = 20000
        while budget <= 100000:
            paramsDict["budget"] = budget
            for levels in (2, 5, 10, 15):
                optModel_level_2 = OptimizationModel(graph, paramsDict, 2)
                Expected_damage_level_2, TotalBudgetUsed_level_2 = optModel_level_2.writeResults()
                optModel = OptimizationModel(graph, paramsDict, levels)
                Expected_damage, TotalBudgetUsed = optModel.writeResults()
                Relative_error = (Expected_damage_level_2 - Expected_damage)/Expected_damage
                print "Relative error_from level_2 to level_"+ str(levels)+":", Relative_error
                ofile.write("\nLandscape file name: %s" % args.graph)
                ofile.write("\nNumber of landowner: %s" % n)
                ofile.write("\nBudget: %s" % budget)
                ofile.write("\nNumber of financial allocation levels: %s" % levels)
                ofile.write("\nExpected damage with levels 2: %s" % Expected_damage_level_2)
                ofile.write("\nExpected damage with levels"+str(levels)+": %s" % Expected_damage)
                ofile.write("\nRelative error_from level_2 to level_"+ str(levels)+ ": %s" % Relative_error)
                ofile.write("\nEnd of results for this combination-----------------------------------------------------------------------------")
            budget = budget + 20000
