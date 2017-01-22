#author: mcm600

import networkx as nx
from gurobipy import *
from comtypes.typeinfo import VARDESC

G = nx.Graph()
    
m = Model("maxflow")
    
arcs = {
    ('so', '1'):   2,
    ('so', '2'):   3,
    ('1',  '2'):   3,
    ('1',  '3'):   4,
    ('3',  'si'):  1,
    ('2',  'si'):  2}
   
for i,j in arcs:
    G.add_edge(i,j,capacity=arcs[(i,j)],flow=m.addVar(ub=arcs[i,j], name='flow_%s_%s' % (i, j)))

m.update()

m.setObjective(G['so']['1']['flow'] + G['so']['2']['flow'], GRB.MAXIMIZE)
    
for i,j in arcs:
    m.addConstr(G[i][j]['flow'] <= G[i][j]['capacity'], 'cap_%s_%s' % (i,j))
    m.addConstr(G[i][j]['flow'] >= 0, 'non-neg')
 
#Flow conservation constraints  
m.addConstr(G['so']['1']['flow'] == G['1']['2']['flow'] + G['1']['3']['flow'], 'node_flow_%s' % ('1'))
m.addConstr(G['2']['si']['flow'] == G['so']['2']['flow'] + G['1']['2']['flow'], 'node_flow_%s' % ('2'))
m.addConstr(G['3']['si']['flow'] == G['1']['3']['flow'], 'node_flow_%s' % ('3'))
m.addConstr(G['so']['1']['flow'] + G['so']['2']['flow'] == G['3']['si']['flow'] + G['2']['si']['flow'], 'node_flow_%s' % ('si'))

m.update()
m.optimize()
    
#Print solution
if m.status == GRB.Status.OPTIMAL:
    print ('\nMAXIMUM SOURCE FLOW: %g' % m.objVal)
    for i,j in arcs:
        if G[i][j]['flow'].x > 0:
            print '\nOptimal flows for ' + i + ' -> ' + j + ': ' + str(G[i][j]['flow'].x)