from ortools.linear_solver import pywraplp
import numpy as np


def main():

    # need = [30, 40, 60, 300, 120, 15, 200, 130]
    # width = [12, 6, 8, 9, 15, 17, 3, 5]
    # M = len(need)
    # K = sum(need)
    # W = 50
    need = [3, 4]
    width = [12, 6]
    M = len(need)
    K = sum(need)
    W = 20


    # 初始化求解器
    solver = pywraplp.Solver.CreateSolver('CBC')
    #
    y = np.array([solver.IntVar(0, 1, f'y_{j}')for j in range(K)])
    x = np.array([solver.IntVar(0, 1, f'x_{i}{j}')
                 for i in range(M)
                 for j in range(K)]).reshape(M, K)



    # 定义约束
    for i in range(M):
        solver.Add(sum(x[i, j] for j in range(K)) >= need[i])

    for j in range(K):
        solver.Add(sum(x[i, j] * width[i] for i in range(M)) <= W*y[j])

    # 目标函数
    solver.Minimize(sum(y))

    # 求解
    status = solver.Solve()

    # 打印结果
    if status == solver.OPTIMAL:
        solution_value = solver.Objective().Value()
        print('solution_value: ', solution_value)
        x_solution_value = np.array([x[i, j].solution_value()
                                    for i in range(M)
                                    for j in range(K)]).reshape(M, K)
        print('x_solution_value: \n', x_solution_value)

        y_solution_value = np.array([y[j].solution_value()
                                    for j in range(K)])
        print('y_solution_value: \n', y_solution_value)

    else:  # No optimal solution was found.
        if status == solver.FEASIBLE:
            print('A potentially suboptimal solution was found.')
        else:
            print('The solver could not solve the problem.')


if __name__ == '__main__':
    main()