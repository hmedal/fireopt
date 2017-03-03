from gurobipy import Model, quicksum, GRB
import networkx as nx
import numpy as np
import pandas as pd
from sklearn import linear_model


class OptimizationModel(Model):

    def __init__(self, name):
        Model.__init__(self, name)
        print str(self)
        self.testVar = 4
        self.createVars()
        self.update()
        self.createObjectiveFunction()
        self.createConstraints()


    def createVars(self):
        a = self.addVar(vtype=GRB.INTEGER, name="a")
        self.b = self.addVar(vtype=GRB.INTEGER, name="b")
        self.c = self.addVar(vtype=GRB.INTEGER, name="c")
        self.d = self.addVar(vtype=GRB.INTEGER, name="d")

    def createConstraints(self):
        # Add constraint: 400a + 200b + 150c + 500d >= 500
        self.addConstr(400 * self.a + 200 * self.b + 150 * self.c + 500 * self.d >= 500, "c0")

        # Add constraint: 3a + 2b >= 6
        self.addConstr(3 * self.a + 2 * self.b >= 6, "c1")

        # Add constraint: 2a + 2b + 4c + 4d >=10
        self.addConstr(2 * self.a + 2 * self.b + 4 * self.c + 4 * self.d >= 10, "c2")

        # Add constraint: 2a + 4b + c + 5d >= 8
        self.addConstr(2 * self.a + 4 * self.b + self.c + 5 * self.d >= 8, "c3")

    def createObjectiveFunction(self):
        self.setObjective(50 * self.a + 20 * self.b + 30 * self.c + 80 * self.d, GRB.MINIMIZE)

class MyClass1():

    def __init__(self, name):
        self.name = name

class MyClass2(MyClass1):

    def __init__(self, name, secondName):
        MyClass1.__init__(self, name)
        print "myClass2 name", self
        self.secondName = secondName

if __name__ == "__main__":
    #myModel = OptimizationModel("mip1")
    #myModel.optimize()
    myObjectTwo = MyClass2("jim", "bob")
    print myObjectTwo.name, myObjectTwo.secondName
    print myObjectTwo
    myModel = OptimizationModel("mip1")
    # myModel.optimize()

