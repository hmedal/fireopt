#  Linear Programming - Section 3.4, Example 6 (page 70)
#
#  minimize
#      50a +  20b +  30c +  80d
#  subject to
#     400a + 200b + 150c + 500d >= 500
#       3a +   2b               >= 6
#       2a +   2b +   4c +   4d >=10
#       2a +   4b +    c +   5d >= 8

#  a, b, c, d integers

from gurobipy import *

try:

    # Create a new model
    m = Model("mip1")

    # Create variables
    a = m.addVar(vtype=GRB.INTEGER, name="a")
    b = m.addVar(vtype=GRB.INTEGER, name="b")
    c = m.addVar(vtype=GRB.INTEGER, name="c")
    d = m.addVar(vtype=GRB.INTEGER, name="d")

    # Integrate new variables
    m.update()

    # Set objective
    m.setObjective(50 * a + 20 * b + 30 * c + 80 * d, GRB.MINIMIZE)

    # Add constraint: 400a + 200b + 150c + 500d >= 500
    m.addConstr(400 * a + 200 * b + 150 * c + 500 * d >= 500, "c0")

    # Add constraint: 3a + 2b >= 6
    m.addConstr(3 * a + 2 * b >= 6, "c1")
    
    # Add constraint: 2a + 2b + 4c + 4d >=10
    m.addConstr(2 * a + 2 * b + 4 * c + 4 * d >= 10, "c2")
    
    # Add constraint: 2a + 4b + c + 5d >= 8
    m.addConstr(2 * a + 4 * b + c + 5 * d >= 8, "c3")

    m.optimize()

    for v in m.getVars():
        print('%s %g' % (v.varName, v.x))

    print('Obj: %g' % m.objVal)

except GurobiError:
    print('Encountered a Gurobi error')

except AttributeError:
    print('Encountered an attribute error')