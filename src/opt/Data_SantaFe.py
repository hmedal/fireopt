import math

N_Nodes_width = 25
N_Nodes_height = 25
N_Nodes = N_Nodes_width * N_Nodes_height

vertical_destance_between_two_cells = 30*4
'in meters, 30 meteres and four combined cell out of 100 cells to make 25 cells'
horizontal_destance_between_two_cells = 30*4

orthogonal_destance_between_two_cells = 169.7

position = {}

shift = 2

B = 5
'Budget'

Distance = 30*4
'Distance from center of cell i to center of cell j'

ProbIgnition = [0.1 for i in range(N_Nodes)]

ProbDuration = [1]
Duration = [24*60]

ValueAtRisk = []
with open('../../data/Cell Value.dat', 'r') as g:
    Value_Data = g.readlines()

    for vline in Value_Data:
        vrow = vline.split()        

        for i in range(len(vrow)):
            if float(vrow[i]) > 1 :
                ValueAtRisk.append(float(vrow[i]))
            elif float(vrow[i]) == 1 :
                ValueAtRisk.append(float(vrow[i]))
            
    
ValueAtRisk = [1 for i in range(N_Nodes)]

SetOfHighFireIntensity = [i for i in range(N_Nodes)]

SetOfPotentialIgnitionPoints = [i for i in range(N_Nodes)]

Delay = max(Duration)+10
'Delay in Minute occured for spread of fire when harvested'

import networkx as nx

' =============================================================================='
# Build a grid network
' =============================================================================='

DGG = nx.DiGraph()
DGG.add_node(N_Nodes-1)

e = 0

e = 0

for j in range(N_Nodes_height):

    for i in range(N_Nodes_width):
        e = j*(N_Nodes_width)

        position[e+i] = (i*shift,j*shift)

for j in range(N_Nodes_height):
    for i in range(N_Nodes_width-1):
        e = j*(N_Nodes_width)
        DGG.add_edge(e+i,e+i+1, weight = horizontal_destance_between_two_cells)
        DGG.add_edge(e+i+1,e+i, weight = horizontal_destance_between_two_cells)

for i in range(N_Nodes_width):
    for j in range(N_Nodes_height-1):
        DGG.add_edge(i+j*N_Nodes_width,i+(j+1)*N_Nodes_width, weight = vertical_destance_between_two_cells)
        DGG.add_edge(i+(j+1)*N_Nodes_width,i+j*N_Nodes_width, weight = vertical_destance_between_two_cells)

for h in range(N_Nodes_height-1):
    for w in range(N_Nodes_width):

        e = h*N_Nodes_width + w

        if (w < N_Nodes_width-1):
            DGG.add_edge(e , e+N_Nodes_width+1, weight = orthogonal_destance_between_two_cells)
            DGG.add_edge(e+N_Nodes_width+1 , e, weight = orthogonal_destance_between_two_cells)

        if (w > 0):
            DGG.add_edge(e , e+N_Nodes_width-1, weight = orthogonal_destance_between_two_cells)
            DGG.add_edge(e+N_Nodes_width-1 , e, weight = orthogonal_destance_between_two_cells)


' =============================================================================='


# Finding neighbors of each cell and the Distance between them
Neighbor = []
for i in range(N_Nodes):
    Neighbor.append(DGG.neighbors(i))



'=============================================================================='
# Finding ROS  or the Rate of Spread
'=============================================================================='
'From the Wei paper here are the ROS :'
'assuming that wind direction is from south west to north east, 45` and the network is situated such that'
'(0,0) is south west and (n,n) is north east, and teta be the angle between wind direction and direction fire'
'spreading from cell r to q then we have (teta, ROS) = (0, 0.6), (45,0.464 ), (90, 0.3), (135, 0.222), (180, 0.2) and '
'it is the same for (-teta, ROS) to cover the clockwise'

# ===================================================
# ===================================================

ROS = [ [0 for i in range(N_Nodes)] for i in range(N_Nodes)]

'===== Reading Data, teta, b and c========'

Cell_Direction_Fire = []

with open('../../data/Direction Data Santa Fe.dat', 'r') as f:
    Direction_Data = f.readlines()
    
    for line in Direction_Data:
        row = line.split()        

        for i in range(len(row)):            
            Cell_Direction_Fire.append(float(row[i]))

bEllipse = []
with open('../../data/b Data Santa Fe.dat', 'r') as ff:
    bData = ff.readlines()
    
    for line in bData:
        row = line.split()        

        for i in range(len(row)):            
            bEllipse.append(float(row[i]))

cEllipse = []
with open('../../data/c Data Santa Fe.dat', 'r') as fff:
    cData = fff.readlines()
    
    for line in cData:
        row = line.split()        

        for i in range(len(row)):            
            cEllipse.append(float(row[i]))  
        


for a in range(N_Nodes):
    for b in Neighbor[a]:
        Fire_Direction = Cell_Direction_Fire[a]

        bEllipse_length = bEllipse[a]
        

               
        if b == a + 1:

            Angle_with_Neighbor_cell = 0

        if b == a - 1:

            Angle_with_Neighbor_cell = 180

        if b == a + 7:

            Angle_with_Neighbor_cell = 90

        if b == a - 7:

            Angle_with_Neighbor_cell = 270

        if b == a + 8:

            Angle_with_Neighbor_cell = 45

        if b == a - 8:

            Angle_with_Neighbor_cell = 225

        if b == a + 6:

            Angle_with_Neighbor_cell = 135

        if b == a - 6:

            Angle_with_Neighbor_cell = 315


        Teta = abs(Fire_Direction - Angle_with_Neighbor_cell)

        if Teta > 180:
            Teta = 360 - Teta

        if Teta < 90:
            ROS[a][b] = (bEllipse[a]**2 - cEllipse[a]**2)/(bEllipse[a] - (cEllipse[a]*math.cos((math.pi)/180*Teta)))

        if Teta >= 90:
            ROS[a][b] = (bEllipse[a]**2 - cEllipse[a]**2)/(bEllipse[a] + (cEllipse[a]*math.cos((180 - Teta)*(math.pi/180))))
            





        


