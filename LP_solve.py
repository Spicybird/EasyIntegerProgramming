from scipy.optimize import linprog
import numpy as np

# c = [1, 1, 1]
# A = [[-5, 0, 0], [0, -2, 0], [0, 0, -2]]
# b = [-25, -20, -18]

# c = [1, 1]
# A = [[-1, 0], [0, -1]]
# b = [-3, -4]

c = [1, 1, 1]
A = [[-1, 0, -1], [0, -1, -1]]
b = [-3, -4]
# bounds = [[0, None], [0, None], [0, None], [0, None], [0, None], [0, None]]
# original problem: min c*x, s.t. A*x <= b, x >=0
res = linprog(c, A_ub=A, b_ub=b,  A_eq=None, b_eq=None, bounds=None, method='simplex')
print('-'*100)
print('original problem result:')
print(res.fun) #最优值 (目标函数最小值)
print(res.x ) #最优解

# dual problem: min b.T *y , s.t. -A.T *y <= - c.T
dual_A = -1 * np.array(A).T
c_dual = np.array(b)
b_dual = np.array(c)
res_dual = linprog(c_dual, A_ub=dual_A, b_ub=b_dual,  A_eq=None, b_eq=None, bounds=None, method='simplex')
print('-'*100)
print('dual problem result:')
print(res_dual.fun) #最优值 (目标函数最小值)
print(res_dual.x) #最优解