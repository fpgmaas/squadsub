import pandas as pd
import numpy as np
from pulp import *
from itertools import product
from utils import *
from squad_problem import *

# SETTINGS --------------------------------------------------------------

skillmatrix = pd.read_csv('data/skillmatrix.csv', sep=',',header=0, index_col = 0)
sk = SkillMatrix(skillmatrix)

n_windows = 10
match_time = 90
min_windows_between_sub = 2 # To avoid great skewness in substitutions (e.g. one player substituting often at beginning of match, other often at end).
n_solutions = 10 # How many solutions to create
windows = list(range(n_windows))

# LINEAR OPTIMIZATION -------------------------------------------------
squad_problem = SquadProblem(sk, n_windows, match_time, min_windows_between_sub)
squad_solution = squad_problem.solve()

for i in range(n_solutions):

    # If problem already solved and optimal; add constraint.
    if squad_solution.get_lp_status()>0:
        squad_problem.update_squad_problem()

    # If problem is being solved for the first time, or it is optimal and we just added a constraint, slve and write to file.
    if squad_solution.get_lp_status()>=0:
        squad_problem.solve()

        if squad_solution.get_lp_status()>0:
            squad_solution.write_solution_to_file('results/result_' + str(i) + '.txt')

        elif i==0:
            tfile = open('INFEASIBLE PROBLEM', 'w')
            tfile.close()




