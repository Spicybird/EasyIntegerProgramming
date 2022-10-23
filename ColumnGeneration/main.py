import numpy as np
import gurobipy as gp
from gurobipy import GRB


class Master:
    def __init__(self, lengths, demands, W) -> None:
        self.M, self.lengths, self.demands, self.W = len(lengths), lengths, demands, W
        self.n_col, self.n_dim = 0, 0

    def create_model(self):
        self.x = []
        self.model = gp.Model("Master")
        self.__set_vars()
        self.__set_contrs()

    def solve(self, flag=0):
        self.model.Params.OutputFlag = flag
        self.model.optimize()

    def get_dual_vars(self):
        return [self.constrs[i].getAttr(GRB.Attr.Pi) for i in range(len(self.constrs))]

    def __set_contrs(self) -> None:
        self.constrs = self.model.addConstrs((self.x[i] * (self.W // self.lengths[i]) >= self.demands[i])
                                             for i in range(self.M))

    def __set_vars(self) -> None:
        for i in range(self.M):
            self.x.append(self.model.addVar(obj=1, lb=0, ub=GRB.INFINITY,
                                            vtype=GRB.CONTINUOUS, name='x' + str(i)))
        self.n_col = 1
        self.n_dim = self.M

    def update_contrs(self, column_coeff):
        self.column = gp.Column(column_coeff, self.model.getConstrs())
        self.model.addVar(vtype=GRB.CONTINUOUS, lb=0, obj=1,
                          name='x' + str(self.n_dim), column=self.column)
        self.n_dim += 1
        self.n_col += 1

    def print_status(self):
        print("master objective value: {}".format(self.model.ObjVal))

    def to_int(self):
        for x in self.model.getVars():
            x.setAttr("VType", GRB.INTEGER)

    def write(self):
        self.model.write("model.lp")


class SubProblem:
    def __init__(self, lengths, W) -> None:
        self.lengths, self.M, self.W = lengths, len(lengths), W

    def create_model(self):
        self.model = gp.Model("sub model")
        self.y = self.model.addVars(self.M, lb=0, ub=GRB.INFINITY, vtype=GRB.INTEGER, name='y')
        self.model.addConstr((gp.quicksum(self.lengths[i] * self.y[i] for i in range(self.M)) <= self.W))

    def set_objective(self, pi):
        self.model.setObjective(1 - gp.quicksum(pi[i] * self.y[i] for i in range(self.M)), sense=GRB.MINIMIZE)

    def solve(self, flag=0):
        self.model.Params.OutputFlag = flag
        self.model.optimize()

    def get_solution(self):
        return [self.model.getVars()[i].x for i in range(self.M)]

    def print_status(self):
        print("sub problem objective value: {}".format(self.model.ObjVal))

    def get_check_num(self):
        return self.model.ObjVal

    def get_reduced_cost2(self):
        return self.model.ObjVal

    def write(self):
        self.model.write("sub_model.lp")


W = 16  # width of large roll
lengths = [3, 5, 7]
demands = [25, 20, 18]
M = len(lengths)  # number of items
N = sum(demands)  # number of available rolls

# model = gp.Model("cutting stock")
# y = model.addVars(N, vtype=GRB.BINARY, name='y')
# x = model.addVars(N, M, vtype=GRB.INTEGER, name='x')
# model.addConstrs((gp.quicksum(x[i, j] for i in range(N)) >= demands[j]) for j in range(M))
# model.addConstrs((gp.quicksum(lengths[j] * x[i, j] for j in range(M)) <= W * y[i] for i in range(N)))
# model.setObjective(gp.quicksum(y[i] for i in range(N)))
# model.optimize()

# x_j: number of times patter j is used
# a_ij: number of times item i is cut in patter j

MAX_ITER_TIMES = 10

cutting_stock = Master(lengths, demands, W)
cutting_stock.create_model()
sub_prob = SubProblem(lengths, W)
sub_prob.create_model()

for k in range(MAX_ITER_TIMES):
    cutting_stock.solve()
    cutting_stock.print_status()
    pi = cutting_stock.get_dual_vars()
    print('_' * 100)
    print('k:', k)
    print('pi: ', pi)
    # cutting_stock.write()

    sub_prob.set_objective(pi)
    sub_prob.solve()
    sub_prob.print_status()
    y = sub_prob.get_solution()
    print('_' * 100)
    print('y: ', y)
    check_num = sub_prob.get_check_num()
    print('check num: ', check_num)
    # sub_prob.write()
    cutting_stock.update_contrs(column_coeff=y)
    if check_num >= 0:
        break

cutting_stock.to_int()
# cutting_stock.solve(flag=1)
cutting_stock.solve(flag=0)
cutting_stock.print_status()
