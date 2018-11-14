from squad_problem import *
import pandas as pd

# SETTINGS -------------------------------------------------------------------------------------------------------------

# Number of time windows. Setting this to a value x will create (x-1) substitution moments during the match.
n_windows = 10
# Duration of the match in minutes. Used to format the results to make them easier to use.
match_time = 90
# The total number of windows that a player should be in the field before being allowed to be subbed again. Can be used to
# avoid great skewness in substitutions (e.g. one player substituting often at beginning of match, other often at end).
# Setting this value too high can increase the complexity of the LP problem.
min_windows_between_sub = 2
# The total number of unique solutions to generate.
n_solutions = 10

# PREPARE DATA FOR LP PROBLEM ------------------------------------------------------------------------------------------

skillmatrix = pd.read_csv('data/skillmatrix.csv', sep=',',header=0, index_col = 0)
sk = SkillMatrix(skillmatrix)

windows = list(range(n_windows))

# LINEAR OPTIMIZATION --------------------------------------------------------------------------------------------------

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
            squad_solution.write_solution_to_txt_file('results/' + str(i) + '_result.txt')
            squad_solution.write_squad_dataframe_to_csv('results/' + str(i) + '_squad.csv')
            squad_solution.write_substitutions_dataframe_to_csv('results/' + str(i) + '_substitutions.csv')

        elif i==0:
            tfile = open('INFEASIBLE PROBLEM', 'w')
            tfile.close()
