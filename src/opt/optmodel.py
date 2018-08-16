'''
Created on Dec 13, 2016
@author: hm568, tb2038, mcm600
'''

#from gurobipy import Model, quicksum, GRB
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
import timeit
from __builtin__ import str
from networkx.algorithms.distance_measures import radius, center

class OptimizationModel():
    '''
    classdocs
    '''

    '''
    Constructor
    '''
    def __init__(self, graph, paramDF, nodeCoords):
        self.setParams(graph, paramDF, nodeCoords)
        
        self.graph, self.nodeList, self.AreaBelongsToLandowners = self.reassignLandowners(graph)
       
        print "ownerNums", range(self.numLandowners)
        print "number of scenarios: ", self.nScenario
        exit()
        self.Decision_states = self.CreateScenarioDecisionStates()
        self.Prob, self.C_k, self.maxOffered = self.ProbDecisionState(self.paramDF)
        self.DecisionProb = self.filterProbDict()
        
        start = timeit.default_timer()
        
        startScndStg = timeit.default_timer()
        self.SecondStgValues = self.CalcAllSecondStageValues()
        stopScndStg = timeit.default_timer()
        self.timeScndStg = stopScndStg - startScndStg
        
        startCreateModel = timeit.default_timer()
        self.m, self.timeOptimize = self.createModel()
        stopCreateModel = timeit.default_timer()
        self.timeCreateModel = stopCreateModel - startCreateModel
        
        stop = timeit.default_timer()
        self.time = stop - start

    def setParams(self, graph, paramDF, nodeCoords):
        self.paramDF = paramDF
        self.nodeCoordinates = nodeCoords
        self.Budget_param = paramDF['budget']
        self.numberOfFinancialAsstValues = paramDF['numFinancialAsstLevels']
        self.numLandowners = paramDF['numLandowners']
        self.method = paramDF['method']
        self.sizeBlocks = paramDF['sizeBlocks']
        self.timeLimit = paramDF['timeLimit']
        self.landscape = paramDF['landscape']
        self.Cell_area = 3.4595
        self.nScenario = (2)**(self.numLandowners)
          
    def reassignLandowners(self, graph):
        for node in graph.nodes():
            graph.node[node]["coordinates"] = self.nodeCoordinates[str(node)]
            
        '''
        if self.numLandowners == 3:
            centers = [129, 145, 487]
        if self.numLandowners == 4:
            centers = [130, 143, 455, 468]
        if self.numLandowners == 5:
            centers = [78, 96, 312, 528, 546]
        if self.numLandowners == 6:
            centers = [129, 137, 145, 479, 487, 495]
        if self.numLandowners == 7:
            centers = [77, 97, 162, 312, 487, 527, 547]
        if self.numLandowners == 8:
            centers = [153, 159, 165, 171, 453, 459, 465, 471]
        if self.numLandowners == 9:
            centers = [84, 90, 101, 123, 312, 501, 523, 534, 540]
        if self.numLandowners == 10:
            centers = [127, 132, 137, 142, 147, 477, 482, 487, 492, 497]
        '''
        
        centerNode = center(graph)[0]
        graphRadius = radius(graph)
        xCenter = graph.node[centerNode]["coordinates"]["x"]
        yCenter = graph.node[centerNode]["coordinates"]["y"]
        
        landCenters = []
        landArea = 2*math.pi/self.numLandowners
        for piece in range(self.numLandowners):
            angle = landArea*piece
            landAreaX = math.floor(xCenter + graphRadius*math.cos(angle))
            landAreaY = math.floor(yCenter + graphRadius*math.sin(angle))
            nodeNum = landAreaX*25 + landAreaY
            landCenters.append(nodeNum)

        owner = 0
        for landCenter in landCenters:
            graph.node[landCenter]["owner"] = owner
            owner = owner + 1

        for node in graph.nodes():
            distList = []
            for landCenter in landCenters:
                distance = ((graph.node[landCenter]["coordinates"]["x"] - graph.node[node]["coordinates"]["x"])**2 + (graph.node[landCenter]["coordinates"]["y"] - graph.node[node]["coordinates"]["y"])**2)**0.5
                distList.append(distance)
            graph.node[node]["owner"] = distList.index(min(distList))

        '''    
        for node in graph.nodes():
            distList = []
            for center in centers:
                distance = nx.shortest_path_length(graph, source=node, target=center)
                distList.append(distance)
            graph.node[node]["owner"] = distList.index(min(distList))
        '''

        nodeList = {}
        for owner in range(self.numLandowners):
            nodeList[owner] = []
            for node in graph.nodes():
                if graph.node[node]["owner"] == owner:
                    nodeList[owner].append(node)
        
        AreaBelongsToLandowners = []
        for owner in nodeList:
            AreaBelongsToLandowners.append(self.Cell_area*len(nodeList[owner]))
        
        return graph, nodeList, AreaBelongsToLandowners              

    def createLandownersList(self, graph):
        #iterate through nodes in graph and return a list of all the unique landowners
        landowners = {}
        ownerNames = []
        ownerNums = []
        nOwners = 0
        for nodeNum,nodeAttr in list(graph.nodes(data=True)):
            if nodeAttr['owner'] not in ownerNames:
                ownerNames.append(nodeAttr['owner'])

        ownerNameNum = zip(ownerNames, range(len(ownerNames)))

        for name, number in ownerNameNum:
            landowners[name] = int(number)
            ownerNums.append(number)
            nOwners = nOwners+1

        return landowners, ownerNums, nOwners

    def filterProbDict(self):
        DecisionProb = {}

        for n in range(self.nScenario):
            for k in range(self.numberOfFinancialAsstValues):
                for j in range(self.numLandowners):
                    for l in (0,1):
                        if (n,j,l,k) in self.Prob:
                            if self.Prob[n,j,l,k] > -99:
                                DecisionProb[n,j,k] = self.Prob[n,j,l,k]

        return DecisionProb

    def createModel(self):
        w = {}
        self.y = {}
        self.x = {}

        m = Model("Optimization Model")

        m.Params.timeLimit = self.timeLimit

        #Create variables
        for n in range(self.nScenario):
            for k in range(self.numberOfFinancialAsstValues):
                for j in range(self.numLandowners):
                    w[j, k, n] = m.addVar(vtype=GRB.CONTINUOUS, name="w_j"+str(j)+"_k"+str(k)+"_n"+str(n))

        for k in range(self.numberOfFinancialAsstValues):
            for j in range(self.numLandowners):
                self.y[j, k] = m.addVar(vtype=GRB.BINARY, name="y_j"+str(j)+"_k"+str(k))
                
        if self.method == 2:
            for k in range(1, self.numberOfFinancialAsstValues):
                self.x[k] = m.addVar(vtype=GRB.BINARY, name="x_k%s" % k)

        m.update()

        #6a updated
        for n in range(self.nScenario):
            m.addConstr(quicksum(w[0,k,n] for k in range(self.numberOfFinancialAsstValues)) ==
                        self.SecondStgValues[n]*quicksum(self.DecisionProb[n,0,k]*self.y[0, k]
                        for k in range(self.numberOfFinancialAsstValues)), name = "6a_n"+str(n))

        #6b updated
        for r in range(1,self.numLandowners):
            for n in range(self.nScenario):
                m.addConstr(quicksum(w[r-1,k,n] for k in range(self.numberOfFinancialAsstValues)) ==
                            quicksum(w[r,k,n]*(1/max(self.DecisionProb[n,r,k],0.00001))
                            for k in range(self.numberOfFinancialAsstValues)),
                            name = "6b_j"+str(r)+"_n"+str(n))

        #6c updated
        for k in range(self.numberOfFinancialAsstValues):
            for r in range(self.numLandowners):
                for n in range(self.nScenario):
                    m.addConstr(w[r, k, n] <= self.y[r, k]*self.SecondStgValues[n],
                                name = "6c_j"+str(r)+"_k"+str(k)+"_n"+str(n))

        #6e
        m.addConstr(quicksum(quicksum(self.C_k[k]*self.y[j, k] for k in range(self.numberOfFinancialAsstValues))*self.AreaBelongsToLandowners[j]
                            for j in range(self.numLandowners)) <= self.Budget_param, name = "6e")

        #6f
        for j in range(self.numLandowners):
            m.addConstr(quicksum(self.y[j, k] for k in range(self.numberOfFinancialAsstValues)) == 1,
                        name = "6f_j"+str(j))
            
        #6g -- Uniform
        if self.method == 1:
            for j in range(self.numLandowners-1):
                for k in range(self.numberOfFinancialAsstValues):
                    m.addConstr(self.y[j, k] == self.y[j+1, k], name = "uniform constraint")

        #6h -- Hybrid
        if self.method == 2:
            for j in range(self.numLandowners):
                for k in range(1, self.numberOfFinancialAsstValues):
                    m.addConstr(self.y[j, k] <= self.x[k])
            m.addConstr(quicksum(self.x[k] for k in range(1, self.numberOfFinancialAsstValues)) <= 1,
                        name = "hybrid constraint")

        #6a -- Objective
        m.setObjective(quicksum(quicksum(w[self.numLandowners-1, k, n] for k in range(self.numberOfFinancialAsstValues))
                                for n in range(self.nScenario)), GRB.MINIMIZE)

        m.update()

        start = timeit.default_timer()
        
        m.optimize()
        
        stop = timeit.default_timer()
        
        time = stop - start

        return m, time

    '''
    ProbDecisionState method:
        The input is a data frame that contains the financial assistance offered to the landowner's and the corresponding decision
        Calculate the probabilities of a landowner's decision state for a given amount of financial assistance
        The output is the probability of a landowner to accept a cost-share plan for a given amount of financial assistance
    '''
    def CreateScenarioDecisionStates(self):
        l = [bin(x)[2:].rjust(self.numLandowners, '0') for x in range(2**self.numLandowners)]
        #States = np.array([0, 1.0])
        Decision_states = {}
        for s in range(self.nScenario):
            Decision_states[s] = [int(l[s][j]) for j in range(self.numLandowners)]

        return Decision_states

    '''

    def CreateLogRegDataFile(self):  ##newly added method

        Financial_level_data = "../../data/AsstanceLevel_probability.csv"
        Financial_level_df = pd.read_csv(Financial_level_data, delimiter=',', usecols=[0, 1, 2])
        nRow_LogRegression = len(Financial_level_df) * self.numberOfRowforEachlevel
        columns = ['OwnerIdx', 'Amount', 'Decision']
        LogRegression_df = pd.DataFrame(index=range(0, nRow_LogRegression), columns=columns)

        for row in range(len(Financial_level_df)):
            for i in range(self.numberOfRowforEachlevel):
                LogRegression_df['OwnerIdx'][row * self.numberOfRowforEachlevel + i] = row * self.numberOfRowforEachlevel + i
                LogRegression_df['Amount'][row * self.numberOfRowforEachlevel + i] = random.uniform(
                    Financial_level_df['Amount_LL'][row],
                    Financial_level_df['Amount_UL'][row])
                # LogRegression_df['Level'][k * numberOfRowforEachlevel + i] = k
                LogRegression_df['Decision'][row * self.numberOfRowforEachlevel + i] = np.random.choice(np.arange(0, 2),
                                                                                                   p=[1 -
                                                                                                      Financial_level_df[
                                                                                                          'Probability'][
                                                                                                          row],
                                                                                                      Financial_level_df[
                                                                                                          'Probability'][
                                                                                                          row]])

        return LogRegression_df

    '''

    def ProbDecisionState(self, paramDF):

        Data_file = "../../data/Synthetic Data.csv"

        Data_df = pd.read_csv(Data_file, delimiter=',', usecols=[1, 2, 3])
        print "Data_df", Data_df
        nOwner = self.numLandowners
        nDecision_state = 2

        train_Feature = Data_df['Amount'].as_matrix().reshape(-1, 1)  # we only take the first two features.
        train_Target = Data_df['Decision'].as_matrix()


        h = .02  # step size in the mesh

        logreg = linear_model.LogisticRegression(C=1e5)

        # we create an instance of Neighbours Classifier and fit the data.
        logreg.fit(train_Feature, train_Target.astype(str))

        #np.set_printoptions(threshold=1000000)
        minimum_amount_offered = Data_df['Amount'].min()
        maximum_amount_offered = Data_df['Amount'].max()

        print "minimum_amount_offered", minimum_amount_offered
        print "maximum_amount_offered", maximum_amount_offered

        Amount_increment = (maximum_amount_offered - minimum_amount_offered) / (self.numberOfFinancialAsstValues - 1)

        DiscretizedFinancialAmountValues = []  ##Contains the financial amount (money) values that defines the upper and lower bounds of the financial assistance levels.
        DiscretizedFinancialAmountValues.append(minimum_amount_offered)
        for i in range(self.numberOfFinancialAsstValues - 1):
            DiscretizedFinancialAmountValues.append(DiscretizedFinancialAmountValues[
                                                        -1] + Amount_increment)  ##Add the amount increment to the last element added to the list to construct the bound of the financial assistance levels.
        '''
        CostOfFinancialAssistanceLevels = []  ##Contains the costs regarding the financial assistance values. They are the midpoints of the upper and lower bounds of the corresponding financial assistance values.
        CostOfFinancialAssistanceLevels.append(
            DiscretizedFinancialAmountValues[0])  # the first element is inserted manually
        for j in range(1, len(DiscretizedFinancialAmountValues)):
            CostOfFinancialAssistanceLevels.append(
                (DiscretizedFinancialAmountValues[j - 1] + DiscretizedFinancialAmountValues[j]) / 2.0)
        '''

        InputArrayForProbEstimation = np.array(DiscretizedFinancialAmountValues)
        print "InputArrayForProbEstimation", InputArrayForProbEstimation

        Estimated_prob = logreg.predict_proba(InputArrayForProbEstimation.reshape(-1, 1))
        #print Estimated_prob

        # Put the result into a dictionary
        ProbDict = {}

        for s in range(self.nScenario):
            for i in range(self.numLandowners):
                for j in range(nDecision_state):
                    for k in range(self.numberOfFinancialAsstValues):
                        ProbDict[s, i, j, k] = Estimated_prob[k, j]

        for s in range(self.nScenario):
            for i in range(self.numLandowners):
                for k in range(self.numberOfFinancialAsstValues):
                    l= 0
                    if self.Decision_states[s][i]==0:
                        l=1
                    ProbDict[s, i, l, k]= -99

        return ProbDict, DiscretizedFinancialAmountValues, maximum_amount_offered


    '''
    CalcSecondStageValue method:
         Calculate the second stage objective value
        The output is the second stage objective value for each scenario

    '''

    def spread(self, ignition_points, Land, SPLength, fire_duration):

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

        for i in range(0,len(ignition_points)):
            Land.node[ignition_points[i]]['color'] = 'b'

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

        '''
        #Undo the fixing of the set of wildfire sub scenarios
        scenario_nodelist = {}
        fname = str(self.nScenario) + 'scenario_nodelist.txt'
        if os.path.isfile(fname):
            f = open(fname, 'rb')  # Pickle file is newly created
            scenario_nodelist = pickle.load(f)  # dump data to f
            f.close()

        #secondStageValues[s] = self.CalcSecondStageValue()
        nodes = []  # list of nodes

        node_gen = 0
        '''
      
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

            #fire_duration = Duration[0]
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
                            if q in self.nodeList[Lowner]:
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

            nodes = []  #comment out this here when fixing the wildfire sub-scenarios fixed in all scenarios and replications

            Burnt = []
            #SumBurnt = 0
            Total_Burnt= 0
            AveBurnt = 0

            while (Number_Sub_scenario_counted < Max_Num__sub_Scenario):

                '''Undo the fixing of the set of wildfire sub scenarios
                if os.path.isfile(fname):
                    nodes = scenario_nodelist[s]
                else:
                    if node_gen == 0:
                        nodes.append(self.Generate_Random_igpoint(Num_igpoints))
                igpoints = nodes[Number_Sub_scenario_counted][:Num_igpoints]
                '''
                nodes.append(self.Generate_Random_igpoint(Num_igpoints))
                igpoints = nodes[Number_Sub_scenario_counted][:Num_igpoints]
                Number_Sub_scenario_counted += 1
                Burnt.append(self.spread(igpoints, Land, SPLength, fire_duration))
                (AveBurnt, SDBurnt) = self.SDCalculate(Burnt,Number_Sub_scenario_counted,0)
            Total_Burnt = sum([i[0] for i in Burnt])
            (AveWUIBurnt,STDWUIBurnt) = self.SDCalculate(Burnt,Number_Sub_scenario_counted,1)
            secondStageValues[s] = AveBurnt
            #scenario_nodelist[s] = nodes
            #node_gen = node_gen + 1
            print "Scenario %s" % (s)
        # fill in here
        '''Undo the fixing of the set of wildfire sub scenarios
        if os.path.isfile(fname) == False:
            f = open(fname, 'wb')  # Pickle file is newly created
            pickle.dump(scenario_nodelist, f)  # dump data to f
            f.close()
        '''
        return secondStageValues

    #def CalcSecondStageValue(self):
        # this will need to wait
        #return SecondStageValue 

    def writeResults(self, file):
        #f = open(file, "a+")
        if self.m.status == GRB.Status.OPTIMAL:
            print ('\nOBJECTIVE VALUE: %g' % self.m.objVal)
            for v in self.m.getVars():
                print('%s %g' % (v.varName, v.x))
            for n in range(self.nScenario):
                for r in range(self.numLandowners):        
                    for k in range(self.numberOfFinancialAsstValues):
                        print "[%s,%s,%s] = %s" % (n,r,k,self.DecisionProb[n,r,k])
            allocations = []
            print self.Budget_param, self.m.objVal
            print "offer allocation:"
            for j in range(self.numLandowners):
                for k in range(self.numberOfFinancialAsstValues):
                    if self.m.getVarByName("y_j%s_k%s" % (j,k)).x > 0.5:
                        allocations.append(k)
                        print "%s: %s" % (j,k)
            print "financial assistance levels:"
            for k in range(self.numberOfFinancialAsstValues):
                print self.C_k[k]
            print "area of each landowners:"
            for j in range(self.numLandowners):
                print self.AreaBelongsToLandowners[j]
            TotalBudgetUsed = 0
            for j in range(self.numLandowners):
                TotalBudgetUsed = TotalBudgetUsed + self.C_k[allocations[j]]*self.AreaBelongsToLandowners[j]
            RemainingBudget = self.Budget_param - TotalBudgetUsed
            if self.method == 0:
                allocMethod = "Risk-based"
            if self.method == 1:
                allocMethod = "Uniform"
            if self.method == 2:
                allocMethod = "Hybrid"
            #Landowners, Budget, Expected Damage, Total Run Time, Second Stage Time, Create Model Time, Optimize Time, Allocation, Levels, Total Budget Used, Remaining Budget, Maximum Amount Offered, Level Amounts, Area of Each Landowner
            file.write("%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n" % (self.landscape, self.numLandowners, self.Budget_param, self.m.objVal, self.time, self.timeScndStg, self.timeCreateModel, self.timeOptimize, allocations, self.numberOfFinancialAsstValues, allocMethod, TotalBudgetUsed, RemainingBudget, self.maxOffered, self.C_k, self.AreaBelongsToLandowners, time.strftime("%c")))
            print "The file has been updated."
        
        if self.m.status == GRB.Status.TIME_LIMIT:
            if self.method == 0:
                allocMethod = "Risk-based"
            if self.method == 1:
                allocMethod = "Uniform"
            if self.method == 2:
                allocMethod = "Hybrid"
            #Landowners, Budget, Expected Damage, Total Run Time, Second Stage Time, Create Model Time, Optimize Time, Allocation, Levels, Total Budget Used, Remaining Budget, Maximum Amount Offered, Level Amounts, Area of Each Landowner
            file.write("\n\nExperiment exceeded time limit.\nLandscape|Landowners|Budget|Current ObjVal|Obj Bound|MIP Gap|Total Run Time|Second Stage Time|Optimize Time|Allocation Levels|Allocation Method|Maximum Amount Offered|Level Amounts|Area of Each Landowner|Time Completed\n")
            file.write("%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s\n\n\n" % (self.landscape, self.numLandowners, self.Budget_param, self.m.objVal, self.m.ObjBoundC, self.m.MIPGap, self.time, self.timeScndStg, self.timeLimit, self.numberOfFinancialAsstValues, allocMethod, self.maxOffered, self.C_k, self.AreaBelongsToLandowners, time.strftime("%c")))
            print "The file has been updated."