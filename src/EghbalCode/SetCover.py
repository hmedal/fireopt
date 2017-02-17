import time
import networkx as nx

start_time = time.time()

from Data_SantaFe import *
from gurobipy import *

#' ====== Setting time as a weight into the network for the SP ============'

Budget = 1
' Budget = number of ignition points'

# Setting probability Duration

ProbDuration = [1]
Duration = [12*60]

'''
Duration = [12*60, 18*60, 24*60, 30*60, 36*60, 42*60, 48*60]
if Budget == 1:
        # 1 ignition
        ProbDuration = [0.45, 0.27, 0.18, 0.05, 0.03, 0.01, 0.01]

if Budget == 2:
        # 2 ignition
        ProbDuration = [0.09, 0.13, 0.22, 0.34, 0.16, 0.05, 0.01]

if Budget == 3:
        # 3 ignition
        ProbDuration = [0.01, 0.04, 0.14, 0.28, 0.36, 0.13, 0.04]

if Budget == 4:
        # 4 ignition
        ProbDuration = [0.0, 0.0, 0.01, 0.09, 0.21, 0.34, 0.36]

if Budget == 5:
        # 5 ignition
        ProbDuration = [0.0, 0.0, 0.0, 0.03, 0.12, 0.21, 0.67]
        '''

MaxDuration = max(Duration) + 100

t = [[MaxDuration for i in range(N_Nodes)] for i in range(N_Nodes)]

for r in range(N_Nodes):

        for q in Neighbor[r]:

            distance_q_r = DGG[q][r]['weight']
            t[q][r] = distance_q_r/ROS[q][r]
            'Distance between neighbor nodes is set'
            'to the weight of the graph, so we can use weight instead'

'#  Rebuilding the graph with time attribute'

Landscape = DGG.copy()

for link in DGG.edges():
    Landscape.add_edge(link[0],link[1], Time_Distance = t[link[0]][link[1]])


#' ============  Calculating the Shortest Path from all to all ============'

SPLength = nx.all_pairs_dijkstra_path_length(Landscape, weight = 'Time_Distance')
'all the shortest path from any cell to any other cell'

#SP = nx.all_pairs_dijkstra_path(Landscape, weight = 'Time_Distance')

reach_r_from_j_within_d = []
'is r reachable from j whithin d'
for d in range(len(Duration)):
    reach_r_from_j_within_d.append([])
    for r in range(N_Nodes):
        reach_r_from_j_within_d[d].append([])
        for j in range(N_Nodes):
            if SPLength[j][r] <= Duration[d]:
                reach_r_from_j_within_d[d][r].append(1)
            else:
                reach_r_from_j_within_d[d][r].append(0)


#' ===================  Building the optimization model ====================='

y = []
z = []

m = Model('Pyro_Terrorism_SetCover_ILP')

Links = DGG.edges()

for d in range(len(Duration)):

    y.append([])

    for r in range(N_Nodes):

            y[d].append(m.addVar( vtype = GRB.BINARY,name = 'y[%d]' %(r)))

for j in range(N_Nodes):

                z.append(m.addVar( vtype = GRB.BINARY,name = 'z[%d]' %j))

m.update()

# ======================    Constraints    ==================================

for d in range(len(Duration)):

    for r in range(N_Nodes):
        'Burn constraints'
        m.addConstr(y[d][r] <= quicksum(
                                        reach_r_from_j_within_d[d][r][j]*z[j]
                                                                            for j in range(N_Nodes)))
m.addConstr(quicksum(z[j] for j in range(N_Nodes)) <= Budget)
'Budget const'

m.update()

# ======================    Set Objective    ==================================

Obj = LinExpr()

for r in SetOfHighFireIntensity:
    for d in range(len(Duration)):
        Obj = Obj + ProbDuration[d]*ValueAtRisk[r]*y[d][r]

m.setObjective(Obj,GRB.MAXIMIZE)

m.update()

# =============================================================================

m.optimize()

end_time = time.time()

print
print 'Solve time = ', end_time - start_time
print
print
print ' ========= Optimal Ignition Points =========='
print
for i in range(N_Nodes):
    if z[i].x > 0:
        print '   ',i,' ',
print
print '=================================================='
print 'y:'
print
#for i in range(N_Nodes):
    #if y[0][i].x > 0:
        #print '   ',i





